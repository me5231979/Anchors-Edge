#!/usr/bin/env python3
"""Playwright QA pass over course pages.

    python3 tools/qa.py oct-monday [more-slugs...]   # specific courses
    python3 tools/qa.py --all                        # every course
    python3 tools/qa.py --dashboard                  # the dashboard page

Checks per course (classroom + web + facilitator editions):
  - console is clean (ignoring net/TUNNEL noise)
  - every slide either fits the viewport or would show the scroll hint
    (overflow > 56px is reported so copy can be trimmed)
  - trainer/builder/recap/capstone interactions round-trip
Requires a local server:  python3 -m http.server 8931
"""
import os, sys, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'http://localhost:8931'
EXEC = '/opt/pw-browsers/chromium'
# viewport matched to a typical projected/shared screen
VW, VH = 1600, 900


def find_chromium():
    for d in sorted(os.listdir('/opt/pw-browsers')):
        p = os.path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome')
        if os.path.exists(p):
            return p
    p = '/opt/pw-browsers/chromium'
    if os.path.exists(p):
        return p
    raise SystemExit('no chromium found')


def check_page(page, url, label, interactions=True, strict_fit=True, takeaway=True):
    errors = []
    console = []
    page.on('console', lambda m: console.append(m) if m.type in ('error', 'warning') else None)
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(600)

    # slide overflow
    slides = page.eval_on_selector_all('.slide', '''els => els.map(e => ({
        id: e.id, over: e.scrollHeight - e.clientHeight }))''')
    for s in slides:
        if strict_fit and s['over'] > 56 and s['id'] != 's-briefing':
            errors.append('%s: slide %s overflows by %dpx' % (label, s['id'], s['over']))

    if interactions:
        # trainer round-trip: click first option in each trainer, then next
        for t in page.query_selector_all('.trainer'):
            tid = t.get_attribute('id') or '?'
            opts = t.query_selector_all('.quiz__options .opt')
            if not opts:
                errors.append('%s: trainer %s has no options' % (label, tid))
                continue
            opts[0].click()
            fb = t.query_selector('.quiz__feedback')
            if not fb or not fb.inner_text().strip():
                errors.append('%s: trainer %s no feedback after click' % (label, tid))
        # builder: pick first opt in each slot, run
        for lab in page.query_selector_all('.lab'):
            lid = lab.get_attribute('id') or '?'
            slots = lab.query_selector_all('.slot')
            for slot in slots:
                o = slot.query_selector('.opt')
                if o:
                    o.click()
            run = lab.query_selector('.lab__runrow .btn')
            if run and not run.is_disabled():
                run.click()
                page.wait_for_timeout(300)
                out = lab.query_selector('.lab__outcome')
                if not out or out.get_attribute('hidden') is not None:
                    errors.append('%s: builder %s outcome missing' % (label, lid))
            elif slots:
                errors.append('%s: builder %s run stayed disabled' % (label, lid))
        # recap: answer all questions
        recap = page.query_selector('#recap')
        if recap:
            for _ in range(8):
                opt = page.query_selector('#recapOptions .opt:not([disabled])')
                if not opt:
                    break
                opt.click()
                page.wait_for_timeout(120)
                nxt = page.query_selector('#recapNext')
                if nxt and nxt.is_visible():
                    nxt.click()
                    page.wait_for_timeout(120)
            res = page.query_selector('#recapResult')
            if not res or res.get_attribute('hidden') is not None:
                errors.append('%s: recap did not reach the score screen' % label)
        # capstone: fill and build
        who = page.query_selector('#capWho')
        if who:
            who.fill('a senior coordinator; went quiet in September')
            for gid in ('#capPractice', '#capWhen'):
                g = page.query_selector(gid + ' .opt')
                if g:
                    g.click()
            b = page.query_selector('#capBuild')
            if b and not b.is_disabled():
                b.click()
                page.wait_for_timeout(200)
                out = page.query_selector('#capOut')
                if not out or out.get_attribute('hidden') is not None:
                    errors.append('%s: capstone card did not build' % label)
                # the sheet is the only thing that prints, so it has to catch this
                ps = page.query_selector('#psEntered')
                if not ps or ps.get_attribute('hidden') is not None:
                    errors.append('%s: takeaway sheet did not record the commitment' % label)
                elif 'senior coordinator' not in (ps.inner_text() or ''):
                    errors.append('%s: takeaway sheet missing the typed commitment' % label)
            else:
                errors.append('%s: capstone build stayed disabled' % label)

    # every course edition prints the takeaway sheet, and it carries the
    # resources; the dashboard is not a course and has neither
    if takeaway:
        if not page.query_selector('.printsheet'):
            errors.append('%s: no takeaway sheet' % label)
        if not page.query_selector('#printSheet'):
            errors.append('%s: no print button on the closing slide' % label)
        if len(page.query_selector_all('.printsheet a[href*="ecsr.fa.us2.oraclecloud.com"]')) < 2:
            errors.append('%s: takeaway sheet needs two Oracle Learning resources' % label)
        if len(page.query_selector_all('.ps__res--url a')) < 2:
            errors.append('%s: takeaway sheet needs two free outside resources' % label)

    for m in console:
        txt = m.text
        if 'net::' in txt or 'TUNNEL' in txt or 'favicon' in txt:
            continue
        if m.type == 'error':
            errors.append('%s: console error: %s' % (label, txt[:160]))
    return errors


def main():
    args = sys.argv[1:]
    do_dash = '--dashboard' in args
    args = [a for a in args if a != '--dashboard']
    if '--all' in args:
        slugs = sorted(d for d in os.listdir(os.path.join(ROOT, 'courses'))
                       if os.path.isfile(os.path.join(ROOT, 'courses', d, 'index.html')))
    else:
        slugs = args
    all_errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=find_chromium(),
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': VW, 'height': VH})
        if do_dash:
            all_errors += check_page(page, BASE + '/index.html', 'dashboard', interactions=False, takeaway=False)
        for slug in slugs:
            all_errors += check_page(page, BASE + '/courses/%s/' % slug, slug + ':class')
            if os.path.exists(os.path.join(ROOT, 'courses', slug, 'web', 'index.html')):
                all_errors += check_page(page, BASE + '/courses/%s/web/' % slug,
                                         slug + ':web', strict_fit=False)
            all_errors += check_page(page, BASE + '/courses/%s/facilitator/' % slug,
                                     slug + ':fac', interactions=False)
            print('checked', slug)
        browser.close()
    if all_errors:
        print('\n'.join(all_errors))
        sys.exit(1)
    print('QA clean: %d course(s)%s' % (len(slugs), ' + dashboard' if do_dash else ''))


if __name__ == '__main__':
    main()
