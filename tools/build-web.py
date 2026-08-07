#!/usr/bin/env python3
"""Generate the self-paced web edition for every course.

    python3 tools/build-web.py            # all courses
    python3 tools/build-web.py oct-monday # one course

Same course as the classroom edition minus the live-class elements: the
QR welcome slide is dropped, every element tagged data-classroom (the
breakout prompts) is removed, and every data-webonly element (the solo
variants) is unhidden.
"""
import json, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_workshop(slug):
    p = os.path.join(ROOT, 'specs', slug + '.json')
    if not os.path.exists(p):
        raise SystemExit('%s: no spec; run tools/generate.py --prune to clear orphans' % slug)
    return json.load(open(p)).get('format') == 'workshop'


def build(slug):
    if is_workshop(slug):
        print('skip courses/%s (workshop: no self-paced edition)' % slug)
        return
    src = os.path.join(ROOT, 'courses', slug, 'index.html')
    s = open(src).read()

    # ---- 1. drop the welcome/QR slide ----
    i = s.index('id="s-welcome"')
    start = s.rindex('<section', 0, i)
    cstart = s.rindex('<!--', 0, start)
    if s[cstart:start].count('\n') <= 2:
        start = cstart
    end = s.index('</section>', i) + len('</section>')
    s = s[:start] + s[end:]

    # ---- 2. classroom-only elements out, web-only elements in ----
    s = re.sub(r'\n?\s*<p class="why" data-classroom.*?</p>', '', s, flags=re.S)
    s = re.sub(r'\n?\s*<div class="card" data-classroom.*?</div>', '', s, flags=re.S)
    s = s.replace(' data-webonly hidden', ' data-webonly')

    # ---- 3. head + paths (one directory deeper) ----
    s = s.replace(" | Anchor's Edge | Vanderbilt</title>",
                  ": Self-Paced | Anchor's Edge | Vanderbilt</title>", 1)
    s = re.sub(r'(rel="canonical" href="[^"]+?)/?"', r'\1/web/"', s, count=1)
    s = s.replace('"../../assets/', '"../../../assets/')
    s = s.replace('href="../../index.html', 'href="../../../index.html')
    s = s.replace('<a class="btn btn--ghost" href="web/">Self-paced edition</a>',
                  '<a class="btn btn--ghost" href="../">Classroom edition</a>')  # no-op for workshops
    s = s.replace('<li><a href="web/">Self-paced version</a></li>',
                  '<li><a href="../">Classroom edition (for facilitators)</a></li>')

    # ---- 4. slide counter ----
    n = len(re.findall(r'<section class="slide', s))
    s = re.sub(r'(id="deckCount">1 / )\d+', lambda m: m.group(1) + str(n), s)

    assert 'data-classroom' not in s, slug + ': a classroom block survived'
    assert s.count('<div') == s.count('</div>'), slug + ': unbalanced divs after stripping classroom blocks'
    assert ': Self-Paced' in s, slug + ': title rewrite missed'
    assert '/web/"' in s, slug + ': canonical rewrite missed'
    assert '../../assets/' not in s.replace('../../../assets/', ''), slug + ': asset path rewrite missed'
    assert '"../../index.html' not in s, slug + ': dashboard link depth rewrite missed'
    assert 'id="s-welcome"' not in s, slug
    assert 'Breakout ·' not in s, slug + ': a live-class breakout prompt survived'
    out = os.path.join(ROOT, 'courses', slug, 'web', 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(s)
    print('wrote courses/%s/web/index.html (%d slides)' % (slug, n))


if __name__ == '__main__':
    slugs = sys.argv[1:]
    if not slugs:
        slugs = sorted(d for d in os.listdir(os.path.join(ROOT, 'courses'))
                       if os.path.isfile(os.path.join(ROOT, 'courses', d, 'index.html')))
    for slug in slugs:
        build(slug)
