#!/usr/bin/env python3
"""Generate the Anchor's Edge dashboard (index.html at the repo root).

Reads every course spec in specs/ for live titles and taglines, plus the
static month data below (from the 9-month plan). Sessions whose spec is
missing render as "In build" so the dashboard can ship at any stage.

    python3 tools/build-dashboard.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOALS = {
    1: {"short": "Workforce Intelligence & Transfer Portal",
        "desc": "By Q4, launch an AI-enabled system that helps leaders see talent needs, retain top talent, strengthen succession, and connect employees to internal opportunities across the university.",
        "baseline": "6% of BUs", "target": "85% of BUs", "pct": 85, "base": 6,
        "months": "Oct · Jan · Apr"},
    2: {"short": "Manager Effectiveness at Scale",
        "desc": "By Q4, implement a Vanderbilt manager standard that measures demonstrated leader behavior.",
        "baseline": "15%", "target": "80%", "pct": 80, "base": 15,
        "months": "Nov · Feb · May"},
    3: {"short": "AI-Enabled Workforce Readiness",
        "desc": "By Q4, equip managers to identify AI-exposed work, critical skills, and emerging talent needs on their teams, and translate those insights into practical workforce actions.",
        "baseline": "5%", "target": "25%", "pct": 25, "base": 5,
        "months": "Dec · Mar · Jun"},
}

MONTHS = [
    {"n": 1, "slug": "oct", "date": "October 2026", "goal": 1,
     "theme": "See the Talent Around You",
     "tagline": "Make talent, skill, and opportunity visible across the team.",
     "nod": "Psychological safety enables talent honesty.",
     "lil": "LinkedIn Learning: Talent Management, Don Phin",
     "lab": "Know-Your-Team talent-mapping lab (in person, navigator led)"},
    {"n": 2, "slug": "nov", "date": "November 2026", "goal": 2,
     "theme": "The Vanderbilt Manager Standard",
     "tagline": "Name the observable behaviors that define a Vanderbilt manager.",
     "nod": "Sustainable pace as a leader behavior.",
     "lil": "LinkedIn Learning: New Manager Foundations, Todd Dewett",
     "lab": "Manager Standard walk-through clinic (in person, navigator led)"},
    {"n": 3, "slug": "dec", "date": "December 2026", "goal": 3,
     "theme": "AI at Work: Start Where You Are",
     "tagline": "Demystify AI and lead one safe first use case.",
     "nod": "Cognitive load: when to lean on AI, and when to rest.",
     "lil": "LinkedIn Learning: Generative AI for Business Leaders, Kian Katanforoosh",
     "lab": "First-AI-Win sandbox session (in person, navigator led)"},
    {"n": 4, "slug": "jan", "date": "January 2027", "goal": 1,
     "theme": "Retain, Grow, Move",
     "tagline": "Succession and internal mobility, without the fear.",
     "nod": "Career wellness: growth as a wellbeing driver.",
     "lil": "LinkedIn Learning: Retaining Your Best Talent, Roberta Matuson",
     "lab": "Stay-interview practice lab (in person, navigator led)"},
    {"n": 5, "slug": "feb", "date": "February 2027", "goal": 2,
     "theme": "Coaching as the Core Manager Behavior",
     "tagline": "Coach the person, manage the task.",
     "nod": "Active listening lowers stress on both sides.",
     "lil": "LinkedIn Learning: Coaching Skills for Leaders and Managers, Sara Canaday",
     "lab": "GROW-model coaching practicum (in person, navigator led)"},
    {"n": 6, "slug": "mar", "date": "March 2027", "goal": 3,
     "theme": "Spot AI-Exposed Work",
     "tagline": "See what's changing on your team before it changes you.",
     "nod": "Change fatigue: pacing team-level AI adoption.",
     "lil": "LinkedIn Learning: AI for Leaders, Doug Rose",
     "lab": "Team AI-exposure mapping workshop (in person, navigator led)"},
    {"n": 7, "slug": "apr", "date": "April 2027", "goal": 1,
     "theme": "The Transfer Portal in Practice",
     "tagline": "Move people to opportunity without moving them out.",
     "nod": "Belonging travels: supporting movers and stayers.",
     "lil": "LinkedIn Learning: Building Your Team, Chris Croft",
     "lab": "Portal walkthrough and skill-profile clinic (in person, navigator led)"},
    {"n": 8, "slug": "may", "date": "May 2027", "goal": 2,
     "theme": "Measured Leader Behavior",
     "tagline": "The standard becomes visible, and measurable.",
     "nod": "Receiving feedback without depleting yourself.",
     "lil": "LinkedIn Learning: Giving and Receiving Feedback, Gemma Leigh Roberts",
     "lab": "Feedback role-play and development-plan build (in person, navigator led)"},
    {"n": 9, "slug": "jun", "date": "June 2027", "goal": 3,
     "theme": "From Insight to Action",
     "tagline": "Translate AI signals into reskill, redeploy, redesign, or hire.",
     "nod": "Closing the year: recovery before the next sprint.",
     "lil": "LinkedIn Learning: Leading Your Team Through Change, Gemma Leigh Roberts",
     "lab": "Workforce action-planning capstone lab (in person, navigator led)"},
]

DAYS = [
    ("monday", "Manager Monday", "For managers"),
    ("tuesday", "Take-Off Tuesday", "All staff"),
    ("wednesday", "Wellness Wednesday", "A light nod"),
    ("thursday", "Thrive Thursday", "All staff"),
]


def esc(t):
    return html.escape(t, quote=False)


def load_spec(slug):
    p = os.path.join(ROOT, "specs", slug + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def session_row(m, day, label, aud):
    if day == "wednesday":
        return f'''
        <div class="session session--nod">
          <span class="session__day">Wellness Wednesday<small>{esc(aud)} · no course</small></span>
          <div class="session__body"><p>{esc(m["nod"])} A concept card or five-minute opener, woven through the week.</p></div>
          <span></span>
        </div>'''
    slug = m["slug"] + "-" + day
    spec = load_spec(slug)
    if spec is None:
        return f'''
        <div class="session">
          <span class="session__day">{esc(label)}<small>{esc(aud)}</small></span>
          <div class="session__body"><h4>In build</h4><p>This session's course is on the way.</p></div>
          <span class="session__cta"><span class="btn btn--soon">Coming soon</span></span>
        </div>'''
    return f'''
        <div class="session">
          <span class="session__day">{esc(label)}<small>{esc(aud)}</small></span>
          <div class="session__body"><h4>{esc(spec["title"])}</h4><p>{esc(spec["tagline"])}</p></div>
          <span class="session__cta">
            <a class="btn btn--dark" href="courses/{slug}/">Launch</a>
            <a class="btn btn--ghost-dark" href="courses/{slug}/facilitator/">Facilitator</a>
            <a class="btn btn--ghost-dark" href="courses/{slug}/web/">Self-paced</a>
          </span>
        </div>'''


def month_card(m):
    g = GOALS[m["goal"]]
    rows = "".join(session_row(m, d, lbl, aud) for d, lbl, aud in DAYS)
    return f'''
      <article class="month" data-goal="{m["goal"]}" data-reveal id="m{m["n"]}">
        <div class="month__head">
          <span class="month__num">M{m["n"]}</span>
          <span class="month__date">{esc(m["date"])}</span>
          <span class="month__goal">Goal {m["goal"]} · {esc(g["short"])}</span>
        </div>
        <h3>{esc(m["theme"])}</h3>
        <p class="month__tagline">{esc(m["tagline"])}</p>
        <div class="sessions">{rows}
        </div>
        <div class="month__extras">
          <span><b>Course of the month:</b> {esc(m["lil"])}</span>
          <span><b>Navigator led:</b> {esc(m["lab"])}</span>
        </div>
      </article>'''


def goal_card(n):
    g = GOALS[n]
    return f'''
        <article class="goal" data-reveal>
          <span class="goal__num">Goal {n} of 3</span>
          <h3>{esc(g["short"])}</h3>
          <p>{esc(g["desc"])}</p>
          <div class="goal__meter">
            <div class="goal__scale" data-meter="{g["pct"]}"><span></span><i style="left:{g["base"]}%"></i></div>
            <div class="goal__labels"><span>Baseline · <b>{esc(g["baseline"])}</b></span><span>Q4 target · <b>{esc(g["target"])}</b></span></div>
          </div>
          <p class="goal__months">Months: {g["months"]}</p>
        </article>'''


built = sum(1 for m in MONTHS for d in ("monday", "tuesday", "thursday")
            if load_spec(m["slug"] + "-" + d))

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anchor's Edge | A Nine-Month Rhythm of Learning | Vanderbilt</title>
<meta name="description" content="Anchor's Edge is the ongoing Apply arm of CHART: a 45-minute weekly virtual learning series for Vanderbilt staff and managers, October 2026 to June 2027, aligned to three enterprise goals.">
<link rel="canonical" href="https://me5231979.github.io/Anchors-Edge/">
<meta property="og:type" content="website">
<meta property="og:title" content="Anchor's Edge | Vanderbilt">
<meta property="og:description" content="Nine months, three goals, one rhythm: the weekly virtual learning series that keeps learning close to the work.">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="assets/img/favicon-96.png">
<link rel="preload" href="assets/fonts/libre-caslon-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/dashboard.css?v=1">
</head>
<body>
<a class="skip-link" href="#months">Skip to the months</a>

<!-- ===================== NAV ===================== -->
<header class="nav" id="nav">
  <a class="nav__brand" href="#top" aria-label="Vanderbilt University, home">
    <img class="nav__lockup" src="assets/img/vu-lockup-white.png" alt="Vanderbilt University" width="250" height="65">
    <img class="nav__vicon" src="assets/img/vu-v-icon-nav.png" alt="Vanderbilt University" width="34" height="25">
  </a>
  <nav class="nav__links" aria-label="Sections">
    <a href="#goals">The Goals</a>
    <a href="#rhythm">The Rhythm</a>
    <a href="#months">The Months</a>
    <a href="#how">How It Works</a>
    <a class="btn" href="#m1">Start with October</a>
  </nav>
</header>

<main id="top">

  <!-- ============ HERO ============ -->
  <section class="hero">
    <div class="wrap">
      <img src="assets/img/vu-v-icon.png" alt="Vanderbilt V" class="hero__mark" data-reveal>
      <p class="eyebrow" data-reveal>Vanderbilt University · Futures Learning Hub · The Apply Arm of CHART</p>
      <h1 class="h-hero" data-reveal>Anchor's Edge. A nine-month <em class="gold-text">rhythm</em> of learning.</h1>
      <p class="lead" data-reveal>A 45-minute weekly virtual series that keeps learning close to the work, October 2026 to June 2027. Every month lands on one of three enterprise goals, and every day of the week echoes that month's theme.</p>
      <div class="hero__meta" data-reveal>
        <div><b>9</b> Months</div>
        <div><b>3</b> Enterprise goals</div>
        <div><b>27</b> Live sessions</div>
        <div><b>45</b> Minutes each</div>
      </div>
      <div class="hero__cta" data-reveal>
        <a class="btn" href="#months">Browse the months</a>
        <a class="btn btn--ghost" href="#goals">See the goals</a>
      </div>
    </div>
  </section>

  <!-- ============ GOALS ============ -->
  <section class="section on-cream" id="goals">
    <div class="wrap">
      <p class="eyebrow" data-reveal>What we're moving</p>
      <h2 class="h2" data-reveal>Three goals. Every session <em>targets one</em>.</h2>
      <p class="lead" data-reveal>Anchor's Edge is the connective tissue: a weekly touch that keeps every manager and staff member close to the goals, reinforced by a monthly LinkedIn Learning course and a navigator-led in-person session.</p>
      <div class="goals">{goal_card(1)}{goal_card(2)}{goal_card(3)}
      </div>
      <p class="goals__note" data-reveal><b>And Goal 4 stays on the wall:</b> meet or exceed the FY27 divisional budgetary target. Anchor's Edge serves it the quiet way, by keeping development in-house, weekly, and close to the work.</p>
    </div>
  </section>

  <!-- ============ THE RHYTHM ============ -->
  <section class="section on-dark" id="rhythm">
    <div class="wrap">
      <p class="eyebrow" data-reveal>The weekly rhythm</p>
      <h2 class="h2" data-reveal>Four days. One <em>theme</em>.</h2>
      <div class="grid3" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
        <div class="feature" data-reveal>
          <span class="feature__num">MON</span>
          <h3>Manager Monday</h3>
          <span class="rhythm-aud">For managers</span>
          <p>The month's theme through the manager lens: the behaviors, reads, and conversations that move the goal on a real team.</p>
        </div>
        <div class="feature" data-reveal>
          <span class="feature__num">TUE</span>
          <h3>Take-Off Tuesday</h3>
          <span class="rhythm-aud">All staff</span>
          <p>Tools and tech, hands on: the systems behind the theme, from Workforce Intelligence to the Transfer Portal to safe AI use.</p>
        </div>
        <div class="feature" data-reveal>
          <span class="feature__num">WED</span>
          <h3>Wellness Wednesday</h3>
          <span class="rhythm-aud">A light nod</span>
          <p>A concept card or five-minute opener, never a full course, so the wellness thread runs through every month without competing for attention.</p>
        </div>
        <div class="feature" data-reveal>
          <span class="feature__num">THU</span>
          <h3>Thrive Thursday</h3>
          <span class="rhythm-aud">All staff</span>
          <p>The soft skill that carries the theme: curiosity, clarity, adaptability, advocacy, empathy, and the rest of the year's toolkit.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ THE MONTHS ============ -->
  <section class="section on-cream" id="months">
    <div class="wrap">
      <p class="eyebrow" data-reveal>The catalog</p>
      <h2 class="h2" data-reveal>Nine months, month <em>by month</em>.</h2>
      <p class="lead" data-reveal>Every session is a live, interactive course site: the facilitator shares it on the call, learners work every exercise on their own screens, and the link from class is the reference they keep. Each ships with a scripted facilitator edition and a self-paced edition for catch-up.</p>
      <div class="filterbar" id="filterbar" data-reveal role="group" aria-label="Filter months by goal">
        <button class="filterchip" data-goal="all" aria-pressed="true">All months</button>
        <button class="filterchip" data-goal="1" aria-pressed="false">Goal 1 · Workforce Intelligence</button>
        <button class="filterchip" data-goal="2" aria-pressed="false">Goal 2 · Manager Effectiveness</button>
        <button class="filterchip" data-goal="3" aria-pressed="false">Goal 3 · AI Readiness</button>
      </div>
      <div class="months" id="catalog">{''.join(month_card(m) for m in MONTHS)}
      </div>
    </div>
  </section>

  <!-- ============ HOW IT WORKS ============ -->
  <section class="section on-dark" id="how">
    <div class="wrap">
      <p class="eyebrow" data-reveal>The model</p>
      <h2 class="h2" data-reveal>One link. Three editions.<br>Zero <em>slide decks</em>.</h2>
      <div class="grid3">
        <div class="feature" data-reveal>
          <span class="feature__num">01</span>
          <h3>Live and hands on</h3>
          <p>Each 45-minute session runs as a virtual class. The welcome slide carries the link and QR; learners open the course on their own screens and play every interaction themselves. Nobody just watches.</p>
        </div>
        <div class="feature" data-reveal>
          <span class="feature__num">02</span>
          <h3>Anyone can teach it</h3>
          <p>The facilitator edition scripts every slide: what to say, what to do, what to ask, the answers to expect, and the transition, plus prep checklists, contingencies, and a printable guide.</p>
        </div>
        <div class="feature" data-reveal>
          <span class="feature__num">03</span>
          <h3>The link is the takeaway</h3>
          <p>Missed the live session? The self-paced edition is the same course, solo. The same URL works on the call and at a desk six months later, and every capstone card copies to the clipboard.</p>
        </div>
      </div>
    </div>
  </section>

</main>

<!-- ============ FOOTER ============ -->
<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <img src="assets/img/vu-lockup-white.png" alt="Vanderbilt University" width="300" height="78" style="width:min(300px,80%);height:auto">
        <p class="brandline">Anchor the learning where the work happens.</p>
      </div>
      <div>
        <h4>The goals</h4>
        <ul>
          <li><a href="#goals">Goal 1 · Workforce Intelligence &amp; Transfer Portal</a></li>
          <li><a href="#goals">Goal 2 · Manager Effectiveness at Scale</a></li>
          <li><a href="#goals">Goal 3 · AI-Enabled Workforce Readiness</a></li>
        </ul>
      </div>
      <div>
        <h4>The program</h4>
        <ul>
          <li><a href="#rhythm">The weekly rhythm</a></li>
          <li><a href="#months">All nine months</a></li>
          <li><a href="#how">How it works</a></li>
          <li><a href="https://me5231979.github.io/Course_Library/" target="_blank" rel="noopener">The Staff Learning Collection</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__legal">
      <span>© <span id="year">2026</span> Vanderbilt University. Anchor's Edge · The Apply arm of CHART.</span>
      <span>Questions? <a href="mailto:chart@vanderbilt.edu">chart@vanderbilt.edu</a> · Futures Learning Hub</span>
    </div>
  </div>
</footer>

<script>
(function () {{
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, c) {{ return Array.prototype.slice.call((c || document).querySelectorAll(s)); }};
  var nav = document.getElementById('nav');
  window.addEventListener('scroll', function () {{
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }}, {{ passive: true }});
  var els = $$('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {{
    var obs = new IntersectionObserver(function (entries) {{
      entries.forEach(function (e) {{
        if (e.isIntersecting) {{ e.target.classList.add('in'); obs.unobserve(e.target); }}
      }});
    }}, {{ threshold: 0.12, rootMargin: '0px 0px -6% 0px' }});
    els.forEach(function (el) {{ obs.observe(el); }});
  }} else {{ els.forEach(function (el) {{ el.classList.add('in'); }}); }}
  $$('[data-meter]').forEach(function (m) {{
    var span = m.querySelector('span');
    var fire = function () {{ span.style.width = m.getAttribute('data-meter') + '%'; }};
    if ('IntersectionObserver' in window && !reduce) {{
      var mo = new IntersectionObserver(function (es) {{
        es.forEach(function (e) {{ if (e.isIntersecting) {{ setTimeout(fire, 300); mo.unobserve(e.target); }} }});
      }}, {{ threshold: 0.4 }});
      mo.observe(m);
    }} else fire();
  }});
  var chips = $$('#filterbar .filterchip');
  chips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      chips.forEach(function (c) {{ c.setAttribute('aria-pressed', String(c === chip)); }});
      var goal = chip.getAttribute('data-goal');
      $$('.month').forEach(function (mo) {{
        mo.hidden = goal !== 'all' && mo.getAttribute('data-goal') !== goal;
      }});
    }});
  }});
  document.getElementById('year').textContent = new Date().getFullYear();
}})();
</script>
</body>
</html>
'''

for ch, name in (("—", "em dash"), ("–", "en dash")):
    assert ch not in page, "dashboard contains an " + name

open(os.path.join(ROOT, "index.html"), "w").write(page)
print("wrote index.html (%d of 27 course sessions linked)" % built)
