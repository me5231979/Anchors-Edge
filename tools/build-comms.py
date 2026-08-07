#!/usr/bin/env python3
"""Generate the Anchor's Edge comms package.

For every session: a ready-to-send email and a Teams post, grouped by
month, written from the course specs. Outputs:

    comms/index.html   styled, printable (linked from the dashboard's
                       admin view)
    comms/anchors-edge-comms-package.pdf   compiled via headless
                       Chromium when available

    python3 tools/build-comms.py [--pdf]
"""
import json, os, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://me5231979.github.io/Anchors-Edge/"

sys.path.insert(0, os.path.join(ROOT, "tools"))
from importlib import import_module
dash = import_module("build-dashboard".replace("-", "_")) if False else None

# month data mirrors the dashboard (kept small here to stay standalone)
MONTHS = [
    {"n": 1, "slug": "oct", "date": "October 2026", "goal": 1, "theme": "See the Talent Around You"},
    {"n": 2, "slug": "nov", "date": "November 2026", "goal": 1, "theme": "The Transfer Portal in Practice"},
    {"n": 3, "slug": "dec", "date": "December 2026", "goal": 2, "theme": "The Vanderbilt Manager Standard"},
    {"n": 4, "slug": "jan", "date": "January 2027", "goal": 3, "theme": "AI at Work: Start Where You Are"},
    {"n": 5, "slug": "feb", "date": "February 2027", "goal": 1, "theme": "Retain, Grow, Move"},
    {"n": 6, "slug": "mar", "date": "March 2027", "goal": 2, "theme": "Coaching as the Core Manager Behavior"},
    {"n": 7, "slug": "apr", "date": "April 2027", "goal": 3, "theme": "Spot AI-Exposed Work"},
    {"n": 8, "slug": "may", "date": "May 2027", "goal": 2, "theme": "Measured Leader Behavior"},
    {"n": 9, "slug": "jun", "date": "June 2027", "goal": 3, "theme": "From Insight to Action"},
]
GOAL_NAMES = {1: "Talent Marketplace & Transfer Portal",
              2: "Manager Effectiveness at Scale",
              3: "AI-Enabled Workforce Readiness"}
DAYS = [("monday", "Manager Monday"), ("tuesday", "Take-Off Tuesday"), ("thursday", "Thrive Thursday")]


def esc(t):
    return html.escape(t, quote=False)


def load(slug):
    return json.load(open(os.path.join(ROOT, "specs", slug + ".json")))


def email_for(spec, m, day_label):
    manager = spec["series"] == "Manager Monday"
    url = SITE + "courses/" + spec["slug"] + "/"
    aud = "Vanderbilt people managers" if manager else "all Vanderbilt staff"
    greeting = "Hi managers," if manager else "Hi everyone,"
    objectives = "".join("<li>%s</li>" % esc(o) for o in spec["objectives"])
    subject = "[Anchor's Edge] %s this week: %s" % (spec["series"], spec["title"])
    body = f"""<p>{greeting}</p>
<p>This month Anchor's Edge is on <b>{esc(m["theme"])}</b> (Goal {m["goal"]}: {esc(GOAL_NAMES[m["goal"]])}), and this week's {esc(spec["series"])} session is <b>{esc(spec["title"])}</b>: {esc(spec["tagline"].rstrip('.'))}.</p>
<p>In 45 live minutes you will:</p>
<ul>{objectives}</ul>
<p><b>When:</b> {esc(spec["series"])}, 45 minutes, virtual (calendar invite to follow)<br>
<b>Who:</b> {aud}<br>
<b>Join:</b> open the session on your own screen at <a href="{url}">{url.replace("https://", "")}</a> when the class starts. Everything you type stays on your screen.</p>
<p>Can't make it live? The self-paced edition covers the same ground with extra practice: <a href="{url}web/">{url.replace("https://", "")}web/</a></p>
<p>See you there,<br>The Futures Learning Hub team</p>"""
    return subject, body


def teams_for(spec, m):
    url = SITE + "courses/" + spec["slug"] + "/"
    who = "Managers" if spec["series"] == "Manager Monday" else "All staff"
    return (f"<b>{esc(spec['series'])} · {esc(spec['title'])}</b> · {who} · 45 min, live and hands-on. "
            f"{esc(spec['tagline'].rstrip('.'))}. This month's theme: {esc(m['theme'])} "
            f"(Goal {m['goal']}, {esc(GOAL_NAMES[m['goal']])}). "
            f"Bring the deck to your own screen: <a href=\"{url}\">{url.replace('https://', '')}</a> "
            f"(missed it? self-paced: <a href=\"{url}web/\">{url.replace('https://', '')}web/</a>)")


def build():
    sections = ""
    for m in MONTHS:
        cards = ""
        for day, label in DAYS:
            slug = m["slug"] + "-" + day
            spec = load(slug)
            subject, body = email_for(spec, m, label)
            teams = teams_for(spec, m)
            cards += f"""
  <div class="sess">
    <h3>{esc(label)} · {esc(spec["title"])}</h3>
    <p class="mini">{esc(spec["tagline"])}</p>
    <p class="tagline">Email</p>
    <div class="msg"><p class="subj"><b>Subject:</b> {esc(subject)}</p>{body}</div>
    <p class="tagline teams">Teams post</p>
    <div class="msg">{teams}</div>
  </div>"""
        sections += f"""
  <section class="monthblock">
    <h2><span class="mnum">M{m["n"]}</span> {esc(m["date"])} · {esc(m["theme"])} <span class="goalpill">Goal {m["goal"]} · {esc(GOAL_NAMES[m["goal"]])}</span></h2>
    {cards}
  </section>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anchor's Edge · Comms Package</title>
<meta name="robots" content="noindex">
<style>
  @font-face {{ font-family: 'Libre Caslon Display'; font-weight: 400;
    src: url('../assets/fonts/libre-caslon-display-latin-400-normal.woff2') format('woff2'); }}
  @font-face {{ font-family: 'Inter'; font-weight: 400;
    src: url('../assets/fonts/inter-latin-400-normal.woff2') format('woff2'); }}
  @font-face {{ font-family: 'Inter'; font-weight: 600;
    src: url('../assets/fonts/inter-latin-600-normal.woff2') format('woff2'); }}
  @font-face {{ font-family: 'Antonio'; font-weight: 700;
    src: url('../assets/fonts/antonio-latin-700-normal.woff2') format('woff2'); }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: 'Inter', Arial, sans-serif; color: #1C1C1C; background: #fff;
    font-size: 13px; line-height: 1.55; }}
  .sheet {{ max-width: 860px; margin: 0 auto; padding: 28px 32px; }}
  header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
    border-bottom: 2px solid #CFAE70; padding-bottom: 14px; margin-bottom: 18px; }}
  header img {{ width: 150px; }}
  h1 {{ font-family: 'Libre Caslon Display', serif; font-weight: 400; font-size: 26px; margin: 0; }}
  h1 em {{ font-style: italic; color: #946E24; }}
  .eyebrow {{ font-family: 'Antonio', Impact, sans-serif; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; font-size: 10px; color: #946E24; margin: 0 0 6px; }}
  h2 {{ font-family: 'Libre Caslon Display', serif; font-weight: 400; font-size: 19px;
    margin: 26px 0 10px; padding-top: 14px; border-top: 1px solid #E4E4E4;
    display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
  .mnum {{ font-family: 'Antonio', Impact, sans-serif; color: #CFAE70; font-size: 17px; }}
  .goalpill {{ font-family: 'Antonio', Impact, sans-serif; text-transform: uppercase; letter-spacing: .07em;
    font-size: 10px; color: #1C1C1C; background: rgba(207,174,112,.28); border: 1px solid rgba(148,110,36,.35);
    border-radius: 4px; padding: 3px 7px; }}
  h3 {{ font-family: 'Libre Caslon Display', serif; font-weight: 400; font-size: 15.5px; margin: 16px 0 2px; }}
  .sess {{ border: 1px solid #E4E4E4; border-left: 3px solid #CFAE70; border-radius: 4px;
    padding: 10px 16px 14px; margin-bottom: 12px; break-inside: avoid; }}
  .tagline {{ font-family: 'Antonio', Impact, sans-serif; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; font-size: 10px; margin: 12px 0 4px; color: #1C1C1C;
    background: #CFAE70; display: inline-block; padding: 2px 7px; border-radius: 2px; }}
  .tagline.teams {{ background: #B3C9CD; }}
  .msg {{ border: 1px solid #E4E4E4; border-radius: 4px; padding: 10px 14px; background: #FAFAF8; }}
  .msg p {{ margin: 0 0 8px; }}
  .msg p:last-child {{ margin-bottom: 0; }}
  .msg ul {{ margin: 0 0 8px; padding-left: 20px; }}
  .subj {{ border-bottom: 1px dashed #E4E4E4; padding-bottom: 6px; }}
  .mini {{ color: #555; margin: 0 0 4px; }}
  a {{ color: #946E24; }}
  .printbtn {{ position: fixed; right: 18px; top: 18px; background: #CFAE70; border: 0; border-radius: 4px;
    padding: 9px 16px; font-family: Inter, Arial, sans-serif; font-weight: 600; font-size: 13px; cursor: pointer; }}
  @media print {{ .printbtn {{ display: none; }} .sheet {{ padding: 0; max-width: none; }} }}
</style>
</head>
<body>
<button class="printbtn" onclick="window.print()">Print / Save as PDF</button>
<div class="sheet">
  <header>
    <div>
      <p class="eyebrow">Vanderbilt · Futures Learning Hub · Anchor's Edge · admin</p>
      <h1>The comms <em>package</em>.</h1>
      <p class="mini" style="margin-top:6px">One ready-to-send email and one Teams post per session, grouped by month. Copy, swap anything in brackets, send. A compiled PDF of this page ships alongside it.</p>
    </div>
    <img src="../assets/img/vu-lockup-black.png" alt="Vanderbilt University">
  </header>
  {sections}
  <p class="mini" style="margin-top:16px;color:#777">Generated from the course specs by tools/build-comms.py. Regenerate after any title or tagline change.</p>
</div>
</body>
</html>
"""
    for ch in ("—", "–"):
        assert ch not in page, "comms page contains a long dash"
    os.makedirs(os.path.join(ROOT, "comms"), exist_ok=True)
    out = os.path.join(ROOT, "comms", "index.html")
    open(out, "w").write(page)
    print("wrote comms/index.html (27 sessions)")
    return out


def make_pdf(html_path):
    from playwright.sync_api import sync_playwright

    def find_chromium():
        for d in sorted(os.listdir('/opt/pw-browsers')):
            p = os.path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome')
            if os.path.exists(p):
                return p
        return '/opt/pw-browsers/chromium'

    pdf_path = os.path.join(ROOT, "comms", "anchors-edge-comms-package.pdf")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=find_chromium(), args=['--no-sandbox'])
        page = b.new_page()
        page.goto("file://" + html_path, wait_until="networkidle")
        page.pdf(path=pdf_path, format="Letter",
                 margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
                 print_background=True)
        b.close()
    print("wrote comms/anchors-edge-comms-package.pdf")


if __name__ == "__main__":
    out = build()
    if "--pdf" in sys.argv:
        make_pdf(out)
