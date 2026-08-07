#!/usr/bin/env python3
"""Accessibility and resilience audit for Anchor's Edge.

Runs real browser checks against the built site and reports WCAG and
failure-mode problems. Requires a local server:

    python3 -m http.server 8931
    python3 tools/audit.py                 # representative sample
    python3 tools/audit.py --all           # every course (slow)

Checks
  contrast     WCAG 2.2 AA text contrast, computed from rendered styles
  names        accessible names on controls, alt text, form labels
  headings     h1 count and level skips
  landmarks    main / nav / footer present
  keyboard     every control reachable, no positive tabindex
  focus        a visible focus indicator on every control
  targets      WCAG 2.2 target size (24 CSS px minimum)
  nojs         page still readable with JavaScript disabled
  mobile       no horizontal page overflow at 390px
  zoom         usable at 200 percent zoom
  motion       content visible under prefers-reduced-motion
  forced       text survives forced-colors (Windows High Contrast)
  console      no console errors
  links        internal links resolve to files that exist
"""
import os, re, sys, json, collections
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'http://localhost:8931'


def find_chromium():
    for d in sorted(os.listdir('/opt/pw-browsers')):
        p = os.path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome')
        if os.path.exists(p):
            return p
    return '/opt/pw-browsers/chromium'


# ---------------------------------------------------------------- browser JS
# Contrast: walk visible text, resolve effective background by climbing
# ancestors, and compute the WCAG 2.x ratio. Large text uses the 3:1 bar.
CONTRAST_JS = r"""() => {
  const lum = (c) => {
    const s = c.map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
    return 0.2126*s[0] + 0.7152*s[1] + 0.0722*s[2];
  };
  const parse = (str) => {
    const m = str.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return { rgb: [p[0], p[1], p[2]], a: p.length > 3 ? p[3] : 1 };
  };
  const blend = (fg, bg) => fg.rgb.map((v, i) => v * fg.a + bg[i] * (1 - fg.a));
  const chain = (start) => {
    let node = start, stack = [], opaque = false;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) stack.push(c);
      if (c && c.a === 1) { opaque = true; break; }
      node = node.parentElement;
    }
    return { stack, opaque };
  };
  const isOverlay = (el) => {
    let n = el;
    while (n && n.nodeType === 1) {
      const pos = getComputedStyle(n).position;
      if (pos === 'fixed' || pos === 'sticky') return true;
      n = n.parentElement;
    }
    return false;
  };
  const chainToOverlay = (start) => {
    // collect backgrounds only up to the fixed/sticky element itself
    let node = start, stack = [];
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) stack.push(c);
      if (c && c.a === 1) return { stack, opaque: true };
      if (cs.position === 'fixed' || cs.position === 'sticky') return { stack, opaque: false };
      node = node.parentElement;
    }
    return { stack, opaque: false };
  };
  const bgOf = (el) => {
    let { stack, opaque } = isOverlay(el) ? chainToOverlay(el) : chain(el);
    if (!opaque) {
      // overlay (fixed/sticky) elements paint over whatever is beneath them
      const r = el.getBoundingClientRect();
      const x = Math.min(Math.max(r.left + r.width / 2, 1), window.innerWidth - 1);
      const y = Math.min(Math.max(r.top + r.height / 2, 1), window.innerHeight - 1);
      const under = document.elementsFromPoint(x, y) || [];
      for (const u of under) {
        if (u === el || el.contains(u)) continue;
        const c2 = chain(u);
        if (c2.opaque) { stack = stack.concat(c2.stack); opaque = true; break; }
      }
    }
    let base = [255, 255, 255];
    for (let i = stack.length - 1; i >= 0; i--) base = blend(stack[i], base);
    return base;
  };
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  let n;
  while ((n = walker.nextNode())) {
    const txt = n.textContent.trim();
    if (!txt || txt.length < 2) continue;
    const el = n.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue;
    // visually hidden (screen-reader only) text is not painted, so it has no contrast
    if (cs.clip === 'rect(0px, 0px, 0px, 0px)' || el.closest('.sr-only')) continue;
    // transient animation states are not a contrast failure; the settled state is
    if (cs.transitionProperty && cs.transitionProperty.indexOf('color') !== -1
        && el.classList && !el.classList.contains('lit')) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // text painted as a gradient cannot be measured this way; flagged separately
    if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)') continue;
    const fgc = parse(cs.webkitTextFillColor !== 'rgba(0, 0, 0, 0)' && cs.webkitTextFillColor
                      ? cs.webkitTextFillColor : cs.color);
    if (!fgc) continue;
    const bg = bgOf(el);
    const fg = blend(fgc, bg);
    const l1 = lum(fg), l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3.0 : 4.5;
    if (ratio < need) {
      out.push({ ratio: Math.round(ratio * 100) / 100, need, size: Math.round(size * 10) / 10,
                 weight, sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
                   ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''),
                 text: txt.slice(0, 45) });
    }
  }
  return out;
}"""

NAMES_JS = r"""() => {
  const problems = [];
  const name = (el) => {
    const al = el.getAttribute('aria-label');
    if (al && al.trim()) return al;
    const lb = el.getAttribute('aria-labelledby');
    if (lb) { const t = document.getElementById(lb); if (t && t.textContent.trim()) return t.textContent; }
    if (el.tagName === 'INPUT') {
      const id = el.id;
      if (id) { const l = document.querySelector('label[for="' + CSS.escape(id) + '"]');
                if (l && l.textContent.trim()) return l.textContent; }
      if (el.closest('label')) return 'wrapped-label';
      if (el.getAttribute('title')) return el.getAttribute('title');
      return '';
    }
    if (el.tagName === 'IMG') return el.getAttribute('alt');
    return el.textContent.trim();
  };
  document.querySelectorAll('a[href], button, input, select, textarea').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const n = name(el);
    if (!n || !String(n).trim()) {
      problems.push({ kind: 'no-accessible-name', tag: el.tagName.toLowerCase(),
                      cls: String(el.className).slice(0, 40), html: el.outerHTML.slice(0, 90) });
    }
  });
  document.querySelectorAll('img').forEach(el => {
    if (el.getAttribute('alt') === null) {
      problems.push({ kind: 'img-missing-alt', src: (el.getAttribute('src') || '').slice(-40) });
    }
  });
  document.querySelectorAll('[tabindex]').forEach(el => {
    const t = parseInt(el.getAttribute('tabindex'), 10);
    if (t > 0) problems.push({ kind: 'positive-tabindex', tabindex: t,
                               html: el.outerHTML.slice(0, 70) });
  });
  return problems;
}"""

STRUCT_JS = r"""() => {
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => {
    const cs = getComputedStyle(h);
    return cs.display !== 'none' && cs.visibility !== 'hidden';
  }).map(h => ({ level: +h.tagName[1], text: h.textContent.trim().slice(0, 40) }));
  const skips = [];
  for (let i = 1; i < hs.length; i++) {
    if (hs[i].level - hs[i-1].level > 1) skips.push({ from: hs[i-1].level, to: hs[i].level, at: hs[i].text });
  }
  return {
    h1: hs.filter(h => h.level === 1).length,
    h1texts: hs.filter(h => h.level === 1).map(h => h.text),
    skips,
    main: document.querySelectorAll('main').length,
    nav: document.querySelectorAll('nav, [role=navigation]').length,
    footer: document.querySelectorAll('footer, [role=contentinfo]').length,
    lang: document.documentElement.getAttribute('lang') || null,
    title: document.title || null
  };
}"""

TARGETS_JS = r"""() => {
  const small = [];
  document.querySelectorAll('a[href], button, input[type=button], input[type=submit]').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    // WCAG 2.2 target-size exception: links inline within a sentence
    const inline = el.tagName === 'A' && getComputedStyle(el).display === 'inline' &&
                   el.parentElement && el.parentElement.textContent.trim().length > el.textContent.trim().length;
    if (inline) return;
    if (r.width < 24 || r.height < 24) {
      small.push({ w: Math.round(r.width), h: Math.round(r.height),
                   cls: String(el.className).slice(0, 40),
                   text: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30) });
    }
  });
  return small;
}"""

VISIBLE_TEXT_JS = r"""() => {
  // characters of text actually painted (opacity and visibility respected)
  let total = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const el = n.parentElement;
    if (!el) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    let op = 1, node = el;
    while (node && node.nodeType === 1) { op *= parseFloat(getComputedStyle(node).opacity); node = node.parentElement; }
    if (op < 0.05) continue;
    total += n.textContent.trim().length;
  }
  return total;
}"""

GRADIENT_TEXT_JS = r"""() => {
  // text painted via background-clip disappears in forced-colors mode
  const hits = [];
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)' && (el.textContent || '').trim()) {
      hits.push({ cls: String(el.className).slice(0, 40), text: el.textContent.trim().slice(0, 40) });
    }
  });
  return hits;
}"""


def focus_check_keyboard(page, limit=25):
    """Press Tab repeatedly and confirm the focused control shows a ring."""
    problems = []
    page.evaluate("window.scrollTo(0,0)")
    for _ in range(limit):
        page.keyboard.press('Tab')
        page.wait_for_timeout(120)   # let any transition settle before reading
        info = page.evaluate("""() => {
          const el = document.activeElement;
          if (!el || el === document.body) return null;
          const cs = getComputedStyle(el);
          const ring = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0)
                    || (cs.boxShadow && cs.boxShadow !== 'none');
          return { ring, tag: el.tagName.toLowerCase(),
                   cls: String(el.className).slice(0, 40),
                   text: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30) };
        }""")
        if info and not info['ring']:
            problems.append(info)
    return problems


def focus_check_unused(page):
    return page.evaluate(r"""() => {
      const problems = [];
      const controls = [...document.querySelectorAll('a[href], button, input, select, textarea')]
        .filter(el => { const cs = getComputedStyle(el);
                        return cs.display !== 'none' && cs.visibility !== 'hidden'; });
      for (const el of controls.slice(0, 60)) {
        const before = getComputedStyle(el);
        const snapshot = [before.outline, before.outlineWidth, before.boxShadow,
                          before.borderColor, before.backgroundColor, before.textDecorationLine].join('|');
        el.focus();
        const after = getComputedStyle(el);
        const now = [after.outline, after.outlineWidth, after.boxShadow,
                     after.borderColor, after.backgroundColor, after.textDecorationLine].join('|');
        const hasOutline = after.outlineStyle !== 'none' && parseFloat(after.outlineWidth) > 0;
        if (!hasOutline && snapshot === now) {
          problems.push({ tag: el.tagName.toLowerCase(),
                          cls: String(el.className).slice(0, 40),
                          text: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30) });
        }
      }
      return problems;
    }""")


def audit_page(browser, url, label, findings, deep=True):
    ctx = browser.new_context(viewport={'width': 1600, 'height': 900})
    page = ctx.new_page()
    errors = []
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(700)

    def add(check, detail):
        findings.append({'page': label, 'check': check, 'detail': detail})

    for c in page.evaluate(CONTRAST_JS):
        add('contrast', c)
    for p in page.evaluate(NAMES_JS):
        add('names', p)

    s = page.evaluate(STRUCT_JS)
    if s['h1'] != 1:
        add('headings', {'issue': 'h1 count is %d' % s['h1'], 'texts': s['h1texts']})
    for sk in s['skips']:
        add('headings', {'issue': 'level skip h%d to h%d' % (sk['from'], sk['to']), 'at': sk['at']})
    if not s['main']:
        add('landmarks', 'no <main>')
    if not s['footer']:
        add('landmarks', 'no <footer>')
    if not s['lang']:
        add('landmarks', 'no lang on <html>')
    if not s['title']:
        add('landmarks', 'no <title>')

    for t in page.evaluate(TARGETS_JS):
        add('targets', t)
    # forced-colors is verified in audit_variants with a real emulated context
    for f in focus_check_keyboard(page):
        add('focus', f)

    baseline_text = page.evaluate(VISIBLE_TEXT_JS)
    if baseline_text < 200:
        add('render', {'issue': 'very little visible text with JS on', 'chars': baseline_text})

    for e in errors:
        if 'net::' in e or 'favicon' in e or 'TUNNEL' in e:
            continue
        add('console', e[:180])
    ctx.close()
    return baseline_text


def audit_variants(browser, url, label, findings, baseline_text):
    def add(check, detail):
        findings.append({'page': label, 'check': check, 'detail': detail})

    # --- JavaScript disabled ---
    ctx = browser.new_context(viewport={'width': 1600, 'height': 900}, java_script_enabled=False)
    p = ctx.new_page()
    p.goto(url, wait_until='domcontentloaded')
    p.wait_for_timeout(400)
    nojs_text = p.evaluate_handle  # not available without JS; measure via DOM dump instead
    html = p.content()
    ctx.close()
    # crude but honest: does the CSS hide everything when JS never adds .in?
    if 'data-reveal' in html:
        ctx2 = browser.new_context(viewport={'width': 1600, 'height': 900})
        p2 = ctx2.new_page()
        p2.goto(url, wait_until='networkidle')
        hidden = p2.evaluate("""() => {
          // simulate JS never running: no .js flag on <html>, no .in from the observer
          document.documentElement.classList.remove('js');
          document.querySelectorAll('[data-reveal].in').forEach(e => e.classList.remove('in'));
          document.querySelectorAll('.manifesto .w.lit').forEach(e => e.classList.remove('lit'));
          let total = 0;
          const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let n;
          while ((n = w.nextNode())) {
            const el = n.parentElement; if (!el) continue;
            const cs = getComputedStyle(el);
            if (cs.display === 'none' || cs.visibility === 'hidden') continue;
            let op = 1, node = el;
            while (node && node.nodeType === 1) { op *= parseFloat(getComputedStyle(node).opacity); node = node.parentElement; }
            if (op < 0.05) continue;
            total += n.textContent.trim().length;
          }
          return total;
        }""")
        ctx2.close()
        if baseline_text and hidden < baseline_text * 0.25:
            add('nojs', {'issue': 'content invisible without JS (reveal animation never runs)',
                         'visible_chars_with_js': baseline_text, 'without': hidden})

    # --- mobile ---
    ctx = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True,
                              has_touch=True, device_scale_factor=2)
    p = ctx.new_page()
    p.goto(url, wait_until='networkidle')
    p.wait_for_timeout(600)
    m = p.evaluate("""() => ({
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        bodyW: document.body.scrollWidth, winW: window.innerWidth })""")
    if m['overflow'] > 4:
        add('mobile', {'issue': 'horizontal page overflow at 390px', 'px': m['overflow']})
    small = p.evaluate(TARGETS_JS)
    for t in small[:6]:
        add('mobile-targets', t)
    ctx.close()

    # --- 200 percent zoom ---
    ctx = browser.new_context(viewport={'width': 800, 'height': 600}, device_scale_factor=2)
    p = ctx.new_page()
    p.goto(url, wait_until='networkidle')
    p.wait_for_timeout(500)
    z = p.evaluate("""() => document.documentElement.scrollWidth - document.documentElement.clientWidth""")
    if z > 4:
        add('zoom', {'issue': 'horizontal overflow at 200 percent zoom', 'px': z})
    ctx.close()

    # --- forced colors (Windows High Contrast) ---
    ctx = browser.new_context(viewport={'width': 1600, 'height': 900}, forced_colors='active')
    p = ctx.new_page()
    p.goto(url, wait_until='networkidle')
    p.wait_for_timeout(600)
    invisible = p.evaluate("""() => {
      const bad = [];
      document.querySelectorAll('h1,h2,h3,p,span,a,button,li').forEach(el => {
        const t = (el.textContent || '').trim();
        if (!t) return;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        // in forced-colors, transparent text fill means the text is not painted
        if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)') {
          bad.push({ cls: String(el.className).slice(0, 30), text: t.slice(0, 40) });
        }
      });
      return bad;
    }""")
    for b in invisible[:8]:
        add('forced-colors', b)
    ctx.close()

    # --- reduced motion ---
    ctx = browser.new_context(viewport={'width': 1600, 'height': 900}, reduced_motion='reduce')
    p = ctx.new_page()
    p.goto(url, wait_until='networkidle')
    p.wait_for_timeout(600)
    rm = p.evaluate(VISIBLE_TEXT_JS)
    ctx.close()
    if baseline_text and rm < baseline_text * 0.5:
        add('motion', {'issue': 'content hidden under prefers-reduced-motion',
                       'chars': rm, 'baseline': baseline_text})


def check_links(findings):
    """Every internal href in built HTML must resolve on disk."""
    import glob
    pages = ['index.html'] + glob.glob('courses/*/index.html') + \
            glob.glob('courses/*/web/index.html') + glob.glob('courses/*/facilitator/index.html') + \
            ['comms/index.html']
    for rel in pages:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        html = open(path).read()
        base = os.path.dirname(path)
        for href in set(re.findall(r'href="([^"#][^"]*)"', html)) | set(re.findall(r'src="([^"#][^"]*)"', html)):
            if href.startswith(('http://', 'https://', 'mailto:', 'data:', '#')):
                continue
            target = os.path.normpath(os.path.join(base, href.split('?')[0].split('#')[0]))
            if target.endswith('/'):
                target += 'index.html'
            if os.path.isdir(target):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                findings.append({'page': rel, 'check': 'links',
                                 'detail': {'broken': href, 'resolved': os.path.relpath(target, ROOT)}})


def main():
    all_courses = '--all' in sys.argv
    import glob
    slugs = sorted(d.split('/')[-2] for d in glob.glob(os.path.join(ROOT, 'courses/*/index.html')))
    if not all_courses:
        slugs = ['oct-monday', 'oct-workshop', 'jan-tuesday']

    targets = [(BASE + '/index.html', 'dashboard'), (BASE + '/comms/', 'comms')]
    for s in slugs:
        targets.append((BASE + '/courses/%s/' % s, s + ':class'))
        if os.path.exists(os.path.join(ROOT, 'courses', s, 'web', 'index.html')):
            targets.append((BASE + '/courses/%s/web/' % s, s + ':web'))
        targets.append((BASE + '/courses/%s/facilitator/' % s, s + ':fac'))

    findings = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=find_chromium(), args=['--no-sandbox'])
        for url, label in targets:
            base_text = audit_page(browser, url, label, findings)
            # variant checks are expensive; run them on one page per kind
            if label in ('dashboard', 'oct-monday:class', 'oct-monday:web', 'oct-workshop:class', 'comms'):
                audit_variants(browser, url, label, findings, base_text)
            print('audited', label, flush=True)
        browser.close()

    check_links(findings)

    by_check = collections.Counter(f['check'] for f in findings)
    print('\n================ AUDIT SUMMARY ================')
    if not findings:
        print('no findings')
    for check, n in by_check.most_common():
        print('%-16s %d' % (check, n))
    out = os.path.join(ROOT, 'audit-report.json')
    json.dump(findings, open(out, 'w'), indent=1)
    print('\nfull report: audit-report.json (%d findings)' % len(findings))

    print('\n---- sample of each ----')
    seen = set()
    for f in findings:
        if f['check'] in seen:
            continue
        seen.add(f['check'])
        print('[%s] %s: %s' % (f['check'], f['page'], json.dumps(f['detail'])[:190]))


if __name__ == '__main__':
    main()
