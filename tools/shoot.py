#!/usr/bin/env python3
"""Screenshot every classroom slide into facilitator/img/<slide-id>.jpg
for the printable guide. Requires the local server:

    python3 -m http.server 8931
    python3 tools/shoot.py            # all courses
    python3 tools/shoot.py oct-monday # one course
"""
import os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'http://localhost:8931'


def find_chromium():
    for d in sorted(os.listdir('/opt/pw-browsers')):
        p = os.path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome')
        if os.path.exists(p):
            return p
    return '/opt/pw-browsers/chromium'


def shoot(page, slug):
    outdir = os.path.join(ROOT, 'courses', slug, 'facilitator', 'img')
    os.makedirs(outdir, exist_ok=True)
    page.goto(BASE + '/courses/%s/' % slug, wait_until='networkidle')
    page.wait_for_timeout(700)
    ids = page.eval_on_selector_all('.slide', 'els => els.map(e => e.id)')
    for sid in ids:
        page.evaluate("id => document.getElementById(id).scrollIntoView({inline:'start'})", sid)
        page.wait_for_timeout(650)
        page.screenshot(path=os.path.join(outdir, sid + '.jpg'),
                        type='jpeg', quality=52)
    print('shot %s (%d slides)' % (slug, len(ids)))


def main():
    slugs = sys.argv[1:]
    if not slugs:
        slugs = sorted(d for d in os.listdir(os.path.join(ROOT, 'courses'))
                       if os.path.isfile(os.path.join(ROOT, 'courses', d, 'index.html')))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=find_chromium(), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        for slug in slugs:
            shoot(page, slug)
        browser.close()


if __name__ == '__main__':
    main()
