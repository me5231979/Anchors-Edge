#!/usr/bin/env python3
"""Generate the Wellness Wednesday talking points.

One page per month for whoever posts or opens the Wellness Wednesday
moment: the wellness idea itself in a few lines, a one-line recap of
Monday and Tuesday, and a tease for Thursday and the in-person workshop
with where to sign up. Deliberately brief; it is a five-minute nod, not
a course.

    wellness/index.html                       styled, printable
    wellness/anchors-edge-wellness-talking-points.pdf

    python3 tools/build-wellness.py [--pdf]
"""
import json, os, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://me5231979.github.io/Anchors-Edge/"
SIGNUP = "[sign-up link]"   # replaced once the registration URL exists

# The wellness thread for each month: the idea, why it belongs beside this
# month's theme, and one thing a person can actually do the same day.
WELLNESS = [
    {"n": 1, "slug": "oct", "date": "October 2026", "theme": "See the Talent Around You",
     "title": "Speaking up about what you are good at",
     "points": [
        "Talking about your own strengths at work is uncomfortable for most people, and staying quiet about them is a quiet cost: the work you would be best at goes to whoever mentioned it first.",
        "Psychological safety is what makes that conversation possible. It is not comfort or agreement; it is the belief that naming a skill, a gap or a mistake will not be held against you.",
        "You do not need a program for it. You need one honest sentence in one conversation this week.",
     ],
     "do": "Say one true sentence about your own work out loud this week: something you are good at, or something you want help with."},
    {"n": 2, "slug": "nov", "date": "November 2026", "theme": "The Transfer Portal in Practice",
     "title": "Belonging travels with you",
     "points": [
        "An internal move is exciting and unsettling at once. People leave a team where they knew everyone's shorthand and arrive somewhere they have to earn it again.",
        "Belonging is rebuilt through small repeated contact, not a welcome lunch. Movers should expect a few awkward weeks and plan for them.",
        "The people who stay behind feel it too. A teammate leaving well is not a rejection of the team, and saying so out loud helps.",
     ],
     "do": "If someone near you is moving, ask what they want to keep from this team. If someone new arrived, invite them to one thing this week."},
    {"n": 3, "slug": "dec", "date": "December 2026", "theme": "The Vanderbilt Manager Standard",
     "title": "Pace is a leadership behavior",
     "points": [
        "Teams copy the pace they see. A leader who sends messages at midnight teaches the team that midnight is when work happens, whatever the policy says.",
        "Sustainable pace is not doing less. It is being deliberate about when work is visible, so recovery time is real rather than theoretical.",
        "This month is about observable behaviors. Pace is one of the most observable of all.",
     ],
     "do": "Pick one boundary you can make visible this week: a scheduled send, a real lunch, or a meeting that ends on time."},
    {"n": 4, "slug": "jan", "date": "January 2027", "theme": "AI at Work: Start Where You Are",
     "title": "Cognitive load, and when to put something down",
     "points": [
        "Every new tool costs attention before it saves any. That cost is real and temporary, and it is worth naming rather than pretending it away.",
        "The point of handing a chore to a tool is not to fill the time with more chores. It is to have more attention left for the work only you can do.",
        "Notice what you are actually spending recovered time on. If it is more low-value work, the tool did not help.",
     ],
     "do": "After you save time with any tool this week, name where that time went. If the answer is nothing good, choose differently next time."},
    {"n": 5, "slug": "feb", "date": "February 2027", "theme": "Retain, Grow, Move",
     "title": "Growth is a wellbeing question",
     "points": [
        "People rarely describe career stagnation as a wellbeing problem, but it behaves like one: low energy, less initiative, a slow pull away from work that used to matter.",
        "Growth does not have to mean promotion. A new skill, a different project, or a clearer path is often enough to change how the week feels.",
        "Asking for growth is not disloyalty. Managers hearing the ask is how people stay.",
     ],
     "do": "Name one thing you want to be better at a year from now, and tell one person who could help."},
    {"n": 6, "slug": "mar", "date": "March 2027", "theme": "Coaching as the Core Manager Behavior",
     "title": "Listening lowers the load on both sides",
     "points": [
        "Being genuinely listened to reduces the pressure of a problem even when nothing about the problem changes. That is why a good conversation can leave you lighter.",
        "It works in both directions. Listening without preparing your reply is less effortful than performing attention while planning what to say.",
        "Most of the skill is restraint: fewer interruptions, one honest question, a pause before answering.",
     ],
     "do": "In one conversation this week, ask a second question before you offer any advice."},
    {"n": 7, "slug": "apr", "date": "April 2027", "theme": "Spot AI-Exposed Work",
     "title": "Change fatigue is real, and it has a pace",
     "points": [
        "Change fatigue is not resistance. It is what happens when changes arrive faster than people can absorb them, and it shows up as flat energy rather than open objection.",
        "Adoption goes better in small, finished pieces. One change that lands beats three that are half-installed.",
        "Naming the fatigue out loud costs nothing and takes a surprising amount of pressure out of a team.",
     ],
     "do": "Ask your team, or yourself, which change is still only half-landed. Finish that one before starting another."},
    {"n": 8, "slug": "may", "date": "May 2027", "theme": "Measured Leader Behavior",
     "title": "Receiving feedback without emptying the tank",
     "points": [
        "Feedback lands hardest when it feels like a verdict on who you are rather than information about something you did.",
        "You do not have to accept or reject it in the room. Thank the person, sit with it, and decide later what to do with it.",
        "One adjustment is a complete response. Trying to fix everything at once is how people end up avoiding feedback altogether.",
     ],
     "do": "The next time you get feedback, say thank you and write it down. Choose your one adjustment tomorrow, not in the moment."},
    {"n": 9, "slug": "jun", "date": "June 2027", "theme": "From Insight to Action",
     "title": "Recovery before the next stretch",
     "points": [
        "Rest is not what happens when the work runs out. Planned recovery is what makes the next stretch of work possible.",
        "Closing a season properly means naming what actually got done, not just what is still open.",
        "The habits from this year survive a break. They do not survive being carried at full speed indefinitely.",
     ],
     "do": "Write down one thing you finished this year that you never marked as finished. Then take the break you have been deferring."},
]


def esc(t):
    return html.escape(t, quote=False)


def load(slug):
    p = os.path.join(ROOT, "specs", slug + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def month_block(w):
    mon, course_url = w["slug"], SITE + "courses/"
    mo, tu, th, ws = (load(mon + "-monday"), load(mon + "-tuesday"),
                      load(mon + "-thursday"), load(mon + "-workshop"))
    points = "".join("<li>%s</li>" % esc(p) for p in w["points"])

    def recap(spec, label, who):
        if not spec:
            return ""
        return ('<li><b>%s</b> (%s) covered <b>%s</b>: %s '
                '<a href="%s%s/">recap or catch up</a></li>'
                % (esc(label), esc(who), esc(spec["title"]),
                   esc(spec["tagline"].rstrip(".")), course_url, esc(spec["slug"])))

    ahead = ""
    if th:
        ahead += ('<li><b>Thursday</b> brings <b>%s</b>: %s <a href="%s%s/">details and sign-up</a></li>'
                  % (esc(th["title"]), esc(th["tagline"].rstrip(".")), course_url, esc(th["slug"])))
    if ws:
        ahead += ('<li><b>The in-person workshop</b> this month is <b>%s</b>, 90 minutes with a navigator, '
                  'hands on in the room. Watch your invite for the date. Sign up: %s</li>'
                  % (esc(ws["title"]), esc(SIGNUP)))

    return '''
  <section class="wk" id="m%(n)d">
    <div class="wk__head">
      <span class="wk__num">M%(n)d</span>
      <div>
        <p class="wk__date">%(date)s &middot; Wellness Wednesday</p>
        <h2>%(title)s</h2>
        <p class="wk__theme">This month's theme: %(theme)s</p>
      </div>
    </div>

    <p class="tagline">Say this</p>
    <ul class="wk__points">%(points)s</ul>

    <p class="wk__do"><b>One thing to try:</b> %(do)s</p>

    <p class="tagline back">Where we have been this week</p>
    <ul class="wk__list">%(recaps)s</ul>

    <p class="tagline fwd">What is coming</p>
    <ul class="wk__list">%(ahead)s</ul>
  </section>''' % {
        "n": w["n"], "date": esc(w["date"]), "title": esc(w["title"]),
        "theme": esc(w["theme"]), "points": points, "do": esc(w["do"]),
        "recaps": recap(mo, "Monday", "managers") + recap(tu, "Tuesday", "all staff"),
        "ahead": ahead}


def build():
    blocks = "".join(month_block(w) for w in WELLNESS)
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wellness Wednesday talking points | Anchor's Edge</title>
<link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
<style>
  @font-face { font-family: 'Libre Caslon Display'; font-weight: 400;
    src: url('../assets/fonts/libre-caslon-display-latin-400-normal.woff2') format('woff2'); }
  @font-face { font-family: 'Inter'; font-weight: 400;
    src: url('../assets/fonts/inter-latin-400-normal.woff2') format('woff2'); }
  @font-face { font-family: 'Inter'; font-weight: 600;
    src: url('../assets/fonts/inter-latin-600-normal.woff2') format('woff2'); }
  @font-face { font-family: 'Antonio'; font-weight: 700;
    src: url('../assets/fonts/antonio-latin-700-normal.woff2') format('woff2'); }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Inter', Arial, sans-serif; color: #1C1C1C; background: #fff;
    font-size: 13.5px; line-height: 1.55; }
  main { max-width: 820px; margin: 0 auto; padding: 28px 32px; }
  header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
    border-bottom: 2px solid #CFAE70; padding-bottom: 14px; margin-bottom: 6px; }
  header img { width: 150px; }
  h1 { font-family: 'Libre Caslon Display', serif; font-weight: 400; font-size: 27px; margin: 0; }
  h1 em { font-style: italic; color: #8A6520; }
  h2 { font-family: 'Libre Caslon Display', serif; font-weight: 400; font-size: 20px; margin: 2px 0 3px; }
  .eyebrow { font-family: 'Antonio', Impact, sans-serif; font-weight: 700; text-transform: uppercase;
    letter-spacing: .09em; font-size: 10px; color: #8A6520; margin: 0 0 6px; }
  .intro { color: #4F4F4F; margin: 10px 0 4px; }
  .wk { border: 1px solid #E4E4E4; border-left: 3px solid #CFAE70; border-radius: 4px;
    padding: 14px 18px 16px; margin-top: 14px; break-inside: avoid; page-break-inside: avoid;
    scroll-margin-top: 16px; }
  .wk__head { display: flex; gap: 14px; align-items: flex-start; border-bottom: 1px solid #EEE;
    padding-bottom: 8px; margin-bottom: 10px; }
  .wk__num { font-family: 'Antonio', Impact, sans-serif; font-size: 26px; color: #8A6520; line-height: 1; }
  .wk__date { font-family: 'Antonio', Impact, sans-serif; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; font-size: 10px; color: #8A6520; margin: 0; }
  .wk__theme { margin: 0; font-size: 12px; color: #555; }
  .tagline { font-family: 'Antonio', Impact, sans-serif; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; font-size: 10px; margin: 12px 0 5px; color: #1C1C1C;
    background: #CFAE70; display: inline-block; padding: 2px 8px; border-radius: 2px; }
  .tagline.back { background: #B3C9CD; }
  .tagline.fwd { background: #8BA18E; }
  ul { margin: 0; padding-left: 18px; }
  li { margin-bottom: 5px; }
  .wk__points li { margin-bottom: 7px; }
  .wk__do { border: 1px dashed #CFAE70; border-radius: 3px; background: rgba(207,174,112,.08);
    padding: 8px 12px; margin: 10px 0 0; }
  a { color: #8A6520; }
  .backlink { margin: 0; font-size: 12px; }
  .backlink a { display: inline-block; padding: 5px 2px; }
  .foot p { margin: 0; }
  .foot { margin-top: 18px; padding-top: 10px; border-top: 1px solid #E4E4E4;
    font-size: 11px; color: #666; }
  a:focus-visible, button:focus-visible { outline: 3px solid #8A6520; outline-offset: 2px; }
  .printbtn { position: fixed; right: 18px; bottom: 18px; z-index: 5; background: #CFAE70;
    color: #1C1C1C; border: 0; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,.22);
    padding: 9px 16px; font-family: Inter, Arial, sans-serif; font-weight: 600; font-size: 13px; cursor: pointer; }
  @media print { .printbtn, .backlink { display: none; } main { padding: 0; max-width: none; } body { font-size: 11.5px; } }
</style>
</head>
<body>
<button class="printbtn" onclick="window.print()">Print / Save as PDF</button>
<main>
  <header>
    <div>
      <p class="eyebrow">Vanderbilt &middot; Futures Learning Hub &middot; Anchor's Edge</p>
      <h1>Wellness Wednesday <em>talking points</em></h1>
    </div>
    <img src="../assets/img/vu-lockup-black.png" alt="Vanderbilt University">
  </header>
  <p class="intro">Wellness Wednesday is a five-minute nod, not a course. One page per month:
  the idea to share, one thing people can try that day, a quick recap of Monday and Tuesday,
  and what is coming Thursday and at the in-person workshop. Post it, read it at the top of a
  meeting, or paste it into a channel.</p>
  <p class="backlink"><a href="../index.html">Back to the Anchor's Edge dashboard</a></p>
%(blocks)s
  <footer class="foot"><p>Generated from the course specs by tools/build-wellness.py.
  Session links go to the live course pages; sign-up links are added once registration opens.</p></footer>
</main>
</body>
</html>
''' % {"blocks": blocks}

    for ch in ("—", "–"):
        if ch in page:
            raise SystemExit("wellness page contains a long dash")
    os.makedirs(os.path.join(ROOT, "wellness"), exist_ok=True)
    out = os.path.join(ROOT, "wellness", "index.html")
    open(out, "w").write(page)
    print("wrote wellness/index.html (%d months)" % len(WELLNESS))
    return out


def make_pdf(html_path):
    from playwright.sync_api import sync_playwright

    def find_chromium():
        for d in sorted(os.listdir('/opt/pw-browsers')):
            p = os.path.join('/opt/pw-browsers', d, 'chrome-linux', 'chrome')
            if os.path.exists(p):
                return p
        return '/opt/pw-browsers/chromium'

    pdf = os.path.join(ROOT, "wellness", "anchors-edge-wellness-talking-points.pdf")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=find_chromium(), args=['--no-sandbox'])
        page = b.new_page()
        page.goto("file://" + html_path, wait_until="networkidle")
        page.pdf(path=pdf, format="Letter", print_background=True,
                 margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
        b.close()
    print("wrote wellness/anchors-edge-wellness-talking-points.pdf")


if __name__ == "__main__":
    out = build()
    if "--pdf" in sys.argv:
        make_pdf(out)
