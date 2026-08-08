#!/usr/bin/env python3
"""Generate a course site from its content spec.

    python3 tools/generate.py            # all specs
    python3 tools/generate.py oct-monday # one spec

Reads specs/<slug>.json, writes courses/<slug>/index.html and
courses/<slug>/facilitator/notes.json. The classroom page is the source
for the web and facilitator editions (tools/build-web.py and
tools/build-facilitator.py).

The spec is validated hard: copy length limits keep every slide on one
screen for the virtual classroom, and em or en dashes anywhere fail the
build.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resources

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://me5231979.github.io/Anchors-Edge/"

GOALS = {
    1: {"name": "the Talent Marketplace and the Transfer Portal",
        "short": "Talent Marketplace & Transfer Portal",
        "desc": "Launch the Talent Marketplace and the Transfer Portal: helping leaders see talent needs, retain top talent, strengthen succession, and connecting employees to internal opportunities across the university."},
    2: {"name": "Manager Effectiveness at Scale",
        "short": "Manager Effectiveness at Scale",
        "desc": "Implement a Vanderbilt manager standard that measures demonstrated leader behavior."},
    3: {"name": "AI-Enabled Workforce Readiness",
        "short": "AI-Enabled Workforce Readiness",
        "desc": "Equip managers to identify AI-exposed work, critical skills, and emerging talent needs on their teams, and translate those insights into practical workforce actions."},
}

SERIES_SUB = {
    "Manager Monday": "The manager lens",
    "Take-Off Tuesday": "Tools and tech, hands on",
    "Thrive Thursday": "The soft skill that carries it",
    "Navigator Workshop": "In person, hands on",
}

# fixed session timing, identical across courses (sums checked below)
FULL_MIN = {"s-welcome": 2, "s-mission": 2, "s-hero": 2,
            "s-one": 9, "s-two": 11, "s-three": 9, "s-belief": 1,
            "s-recap": 4, "s-plan": 4, "s-close": 1}
CORE_MIN = {"s-welcome": 1, "s-mission": 1, "s-hero": 1,
            "s-one": 6, "s-two": 8, "s-three": 6, "s-belief": 0,
            "s-recap": 3, "s-plan": 3, "s-close": 1}
assert sum(FULL_MIN.values()) == 45, sum(FULL_MIN.values())
assert sum(CORE_MIN.values()) == 30, sum(CORE_MIN.values())

# in-person navigator workshops run 90 full / 60 core
WS_FULL = {"s-welcome": 3, "s-mission": 4, "s-hero": 3,
           "s-one": 21, "s-two": 23, "s-three": 21, "s-belief": 2,
           "s-recap": 5, "s-plan": 6, "s-close": 2}
WS_CORE = {"s-welcome": 2, "s-mission": 2, "s-hero": 2,
           "s-one": 14, "s-two": 16, "s-three": 14, "s-belief": 1,
           "s-recap": 4, "s-plan": 3, "s-close": 2}
assert sum(WS_FULL.values()) == 90, sum(WS_FULL.values())
assert sum(WS_CORE.values()) == 60, sum(WS_CORE.values())


def timing(spec):
    if spec.get("format") == "workshop":
        return WS_FULL, WS_CORE, 90, 60
    return FULL_MIN, CORE_MIN, 45, 30

# ---------------------------------------------------------------- validation
LIMITS = {
    "heroLead": 170, "missionTie": 250, "goalLead": 230, "lead": 260,
    "manifesto": 90, "objective": 110, "agenda_d": 110, "trainer_q": 150,
    "trainer_why": 170, "opt_t": 100, "coach": 180, "card_text": 240,
    "recap_opt": 80, "recap_why": 170, "practice_move": 170, "group": 170,
    "context": 300, "discuss": 170, "deeper_title": 60, "deeper_body": 430,
    "deeper_step": 170,
}

def strip_tags(t):
    return re.sub(r"<[^>]+>", "", t or "")

def check_len(val, limit, path, errors):
    n = len(strip_tags(val))
    if n > limit:
        errors.append("%s: %d chars (limit %d): %r" % (path, n, limit, val[:60]))

def validate(spec, errors):
    def L(key, val, path):
        check_len(val, LIMITS[key], path, errors)
    for f in ("slug", "series", "month", "monthShort", "theme", "goal", "title",
              "titleHtml", "tagline", "description", "heroLead", "objectives",
              "skills", "missionTie", "manifesto",
              "sections", "recap", "capstone", "closing", "facilitator"):
        if f not in spec:
            errors.append("missing field: " + f)
    if errors:
        return
    L("heroLead", spec["heroLead"], "heroLead")
    L("missionTie", spec["missionTie"], "missionTie")
    if spec.get("goalLead"):
        L("goalLead", spec["goalLead"], "goalLead")
    L("manifesto", spec["manifesto"], "manifesto")
    if len(spec["objectives"]) != 3:
        errors.append("need exactly 3 objectives")
    for i, o in enumerate(spec["objectives"]):
        L("objective", o, "objectives[%d]" % i)
    if not (3 <= len(spec["skills"]) <= 4):
        errors.append("need 3 or 4 skills")
    for i, a in enumerate(spec.get("agenda", [])):
        L("agenda_d", a["d"], "agenda[%d].d" % i)
    if len(spec["sections"]) != 3:
        errors.append("need exactly 3 sections")
    types = [s["interaction"]["type"] for s in spec["sections"]]
    for t in types:
        if t not in ("trainer", "builder", "check"):
            errors.append("unknown interaction type " + t)
    for si, sec in enumerate(spec["sections"]):
        p = "sections[%d]" % si
        L("lead", sec["lead"], p + ".lead")
        if sec.get("group"):
            L("group", sec["group"], p + ".group")
        if sec.get("solo"):
            L("group", sec["solo"], p + ".solo")
        src = sec.get("source")
        if src:
            check_len(src.get("label", ""), 110, p + ".source.label", errors)
            if not (src.get("url", "").startswith("http")):
                errors.append(p + ".source needs a full url")
        d = sec.get("deeper")
        if not d:
            if spec.get("format") != "workshop":
                errors.append(p + ": missing deeper block (self-paced dive)")
        else:
            L("deeper_title", d["title"], p + ".deeper.title")
            L("deeper_body", d["body"], p + ".deeper.body")
            if not (2 <= len(d["steps"]) <= 3):
                errors.append(p + ".deeper needs 2 or 3 steps")
            for st in d["steps"]:
                L("deeper_step", st, p + ".deeper.steps")
        it = sec["interaction"]
        if it["type"] == "trainer":
            if not (3 <= len(it["items"]) <= 4):
                errors.append(p + ": trainer needs 3 or 4 items")
            if len(it["labels"]) != 3:
                errors.append(p + ": trainer needs 3 labels")
            for l in it["labels"]:
                check_len(l, 60, p + ".labels", errors)
            for qi, q in enumerate(it["items"]):
                L("trainer_q", q["q"], "%s.items[%d].q" % (p, qi))
                L("trainer_why", q["why"], "%s.items[%d].why" % (p, qi))
        elif it["type"] == "builder":
            if len(it["slots"]) != 2:
                errors.append(p + ": builder needs exactly 2 slots")
            for slt in it["slots"]:
                if len(slt["opts"]) != 3:
                    errors.append(p + ": each builder slot needs 3 opts")
                for o in slt["opts"]:
                    L("opt_t", o["t"], p + ".slot opt")
                    L("coach", o["coach"], p + ".slot coach")
        elif it["type"] == "check":
            L("card_text", it["card"]["text"], p + ".card.text")
            if not it.get("context") or not it.get("discuss"):
                errors.append(p + ": check needs context and discuss (live-class replacement for the quiz)")
            else:
                L("context", it["context"], p + ".context")
                L("discuss", it["discuss"], p + ".discuss")
            if len(it["opts"]) != 3:
                errors.append(p + ": check needs 3 opts")
            if sum(1 for o in it["opts"] if o.get("correct")) != 1:
                errors.append(p + ": check needs exactly 1 correct opt")
            for o in it["opts"]:
                check_len(o["t"], 90, p + ".check opt", errors)
                L("trainer_why", o["why"], p + ".check why")
    if len(spec["recap"]) != 3:
        errors.append("need exactly 3 recap questions")
    for qi, q in enumerate(spec["recap"]):
        if len(q["opts"]) != 4:
            errors.append("recap[%d] needs 4 opts" % qi)
        for o in q["opts"]:
            L("recap_opt", o, "recap[%d].opts" % qi)
        L("recap_why", q["why"], "recap[%d].why" % qi)
    # section ids are load-bearing: the runbook, skip link and nav all assume them
    ids = [sec.get("id") for sec in spec["sections"]]
    if ids != ["s-one", "s-two", "s-three"]:
        errors.append("section ids must be s-one, s-two, s-three (got %r)" % ids)
    # an out-of-range answer marks every choice wrong at runtime
    for si, sec in enumerate(spec["sections"]):
        it = sec["interaction"]
        if it["type"] == "trainer":
            n = len(it.get("labels", []))
            for qi, q in enumerate(it["items"]):
                a = q.get("answer")
                if not isinstance(a, int) or not (0 <= a < n):
                    errors.append("sections[%d].items[%d].answer out of range: %r" % (si, qi, a))
        if it["type"] == "builder":
            for slt in it["slots"]:
                if not slt.get("key"):
                    errors.append("sections[%d]: builder slot missing key" % si)
                for o in slt["opts"]:
                    if not isinstance(o.get("pts"), int) or not o.get("coach"):
                        errors.append("sections[%d]: builder opt needs pts and coach" % si)
    for qi, q in enumerate(spec["recap"]):
        c = q.get("correct")
        if not isinstance(c, int) or not (0 <= c < len(q["opts"])):
            errors.append("recap[%d].correct out of range: %r" % (qi, c))

    cap = spec["capstone"]
    for pr in cap.get("practices", []):
        if not (pr.get("id") and pr.get("chip") and pr.get("name") and pr.get("move")):
            errors.append("capstone practice needs id, chip, name and move")
    for w in cap.get("whens", []):
        if not (w.get("id") and w.get("chip") and w.get("out")):
            errors.append("capstone when needs id, chip and out")
    if len(cap["practices"]) != 3:
        errors.append("capstone needs exactly 3 practices")
    for pr in cap["practices"]:
        L("practice_move", pr["move"], "capstone.practice.move")
    if len(cap["whens"]) != 3:
        errors.append("capstone needs exactly 3 whens")
    fac = spec["facilitator"]
    for k in ("audience", "pulse", "s1", "s2", "s3", "capstoneSay", "closeSay"):
        if k not in fac:
            errors.append("facilitator missing " + k)


def check_dashes(text, slug):
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        if ch in text:
            i = text.index(ch)
            raise SystemExit("%s: %s at char %d: ...%s..." % (slug, name, i, text[max(0, i-40):i+40]))

# ---------------------------------------------------------------- html bits
def esc(t):
    """Escape for both text nodes and attribute values (quotes included)."""
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") \
                    .replace('"', "&quot;").replace("'", "&#39;")

def js_str(t):
    return json.dumps(t)

def skills_html(skills):
    out = []
    for s in skills:
        cls = "skillpill skillpill--core" if s.get("core") else "skillpill"
        out.append('<span class="%s">%s</span>' % (cls, esc(s["label"])))
    return "".join(out)

def trainer_html(sec):
    it = sec["interaction"]
    return '''
      <div class="quiz trainer" id="%(id)s-play" data-reveal style="margin-top:1.75rem">
        <p class="eyebrow" style="margin-bottom:.5rem">Play · %(playTitle)s</p>
        <p class="why" style="margin-top:0"><b>Why this matters:</b> %(intro)s</p>
        <p class="quiz__progress"></p>
        <p class="quiz__q" style="margin-top:.4rem"></p>
        <div class="quiz__options" role="group" aria-label="Choices"></div>
        <p class="quiz__feedback" aria-live="polite"></p>
        <div class="quiz__nav"><button class="btn btn--dark" style="visibility:hidden">Next</button></div>
        <div class="trainer__result" hidden aria-live="polite"></div>
      </div>''' % {"id": sec["id"], "playTitle": esc(it["playTitle"]), "intro": esc(it["intro"])}

def builder_html(sec):
    it = sec["interaction"]
    return '''
      <div class="lab" id="%(id)s-lab" data-reveal style="margin-top:1.75rem">
        <p class="eyebrow" style="margin-bottom:.5rem">Practice · %(playTitle)s</p>
        <p class="why" style="margin-top:0"><b>Why this matters:</b> %(intro)s</p>
        <div class="lab__slots"></div>
        <div class="lab__runrow">
          <button class="btn" disabled>%(runLabel)s</button>
          <span class="quiz__progress">Choose both steps</span>
        </div>
        <div class="lab__outcome" hidden aria-live="polite"></div>
      </div>''' % {"id": sec["id"], "playTitle": esc(it["playTitle"]),
                   "intro": esc(it["intro"]), "runLabel": esc(it.get("runLabel", "Run it"))}

def check_html(sec):
    """The concept card shows in both editions. The live class gets extra
    context and a facilitator-led discussion prompt in place of the quiz;
    the self-paced edition gets the knowledge check."""
    it = sec["interaction"]
    opts = "".join(
        '<button class="opt" data-correct="%d" data-why="%s"><span class="mark">%s</span><span>%s</span></button>'
        % (1 if o.get("correct") else 0, esc(o["why"]), chr(65 + i), esc(o["t"]))
        for i, o in enumerate(it["opts"]))
    return '''
      <div class="card" data-reveal style="margin-top:1.75rem;border-color:rgba(207,174,112,.5)">
        <span class="tag">%(cardTag)s</span>
        <p style="margin:.5rem 0 0" class="measure">%(cardText)s</p>
      </div>
      <div class="card" data-classroom data-reveal style="margin-top:1.25rem">
        <span class="tag">In the room</span>
        <p style="margin:.5rem 0 0" class="measure">%(context)s</p>
        <p style="margin:.75rem 0 0" class="why"><b>Talk it through:</b> %(discuss)s</p>
      </div>
      <div class="quiz" data-webonly hidden data-quiz data-reveal style="margin-top:1.5rem">
        <p class="quiz__q">%(q)s</p>
        <div class="quiz__options">%(opts)s</div>
        <p class="quiz__feedback" aria-live="polite"></p>
      </div>''' % {"cardTag": esc(it["card"]["tag"]), "cardText": esc(it["card"]["text"]),
                   "context": esc(it["context"]), "discuss": esc(it["discuss"]),
                   "q": esc(it["q"]), "opts": opts}

INTERACTION_HTML = {"trainer": trainer_html, "builder": builder_html, "check": check_html}


def section_html(sec, num):
    inter = INTERACTION_HTML[sec["interaction"]["type"]](sec)
    tones = ["on-light", "on-dark", "on-cream"]
    tone = tones[(num - 1) % 3]
    group = ""
    if sec.get("group"):
        group = ('\n      <p class="why" data-classroom data-reveal style="margin-top:1.25rem">'
                 '<b>Breakout · 3 min:</b> %s</p>' % esc(sec["group"]))
    solo = ""
    if sec.get("solo"):
        solo = ('\n      <p class="why" data-webonly hidden data-reveal style="margin-top:1.25rem">'
                '<b>On your own:</b> %s</p>' % esc(sec["solo"]))
    source = ""
    if sec.get("source"):
        src = sec["source"]
        source = ('\n      <p class="why srcline" data-reveal><b>Grounded in:</b> '
                  '<a href="%s" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">%s</a></p>'
                  % (esc(src["url"]), esc(src["label"])))
    deeper = ""
    if sec.get("deeper"):
        d = sec["deeper"]
        steps = "".join("<li>%s</li>" % esc(x) for x in d["steps"])
        deeper = ('''
      <details class="deeper" data-webonly hidden data-reveal>
        <summary><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg> Go deeper</summary>
        <div class="deeper__body">
          <div><h3>%s</h3><p>%s</p></div>
          <div class="deeper__ask"><h3><span class="mode">On your own</span></h3>
          <ol class="steps">%s</ol></div>
        </div>
      </details>''' % (esc(d["title"]), esc(d["body"]), steps))
    return '''
  <!-- ============ SECTION %(num)02d ============ -->
  <section class="slide %(tone)s" id="%(id)s" data-count data-title="%(dataTitle)s">
    <div class="wrap">
      <p class="eyebrow" data-reveal>Section %(num)02d · %(eyebrow)s</p>
      <h2 class="h2" data-reveal>%(headline)s</h2>
      <p class="lead" data-reveal>%(lead)s</p>%(inter)s%(source)s%(group)s%(solo)s%(deeper)s
    </div>
  </section>''' % {"num": num, "tone": tone, "id": sec["id"], "dataTitle": esc(sec["dataTitle"]),
                   "eyebrow": esc(sec["eyebrow"]), "headline": sec["headline"],
                   "lead": esc(sec["lead"]), "inter": inter, "group": group, "solo": solo,
                   "deeper": deeper, "source": source}


def printsheet_html(spec):
    """The one thing a learner should get from Ctrl+P: the takeaway, not the deck."""
    g = GOALS[spec["goal"]]
    objectives = "".join("<li>%s</li>" % esc(o) for o in spec["objectives"])
    rows = ""
    for i, sec in enumerate(spec["sections"], start=1):
        it = sec["interaction"]
        if it["type"] == "check":
            take = it["card"]["text"]
        elif it["type"] == "trainer":
            take = it["passMsg"]
        else:
            take = it["heads"]["strong"]
        src = ""
        if sec.get("source"):
            src = ('<p class="ps__src">Grounded in: <a href="%s">%s</a></p>'
                   % (esc(sec["source"]["url"]), esc(sec["source"]["label"])))
        rows += ('<div class="ps__sec"><h3>%d &middot; %s</h3><p>%s</p>%s</div>'
                 % (i, esc(strip_tags(sec["headline"])), esc(take), src))
    cap = spec["capstone"]
    moves = "".join("<li><b>%s.</b> %s</li>" % (esc(pr["name"]), esc(pr["move"]))
                    for pr in cap["practices"])
    deeper = ""
    for sec in spec["sections"]:
        d = sec.get("deeper")
        if d:
            steps = "".join("<li>%s</li>" % esc(x) for x in d["steps"])
            deeper += ('<div class="ps__sec"><h3>%s</h3><ol>%s</ol></div>'
                       % (esc(d["title"]), steps))
    deeper_block = ("<h2>Practise it on your own</h2>" + deeper) if deeper else ""

    # The recap questions, with the answer spelled out: a real content recap
    # for someone reading this a month later without the deck in front of them.
    quiz = ""
    for qi, q in enumerate(spec["recap"], start=1):
        quiz += ('<div class="ps__sec"><h3>%d &middot; %s</h3>'
                 '<p><b>Answer:</b> %s</p><p>%s</p></div>'
                 % (qi, esc(q["q"]), esc(q["opts"][q["correct"]]), esc(q["why"])))

    oracle, free = resources.for_slug(spec["slug"])
    res = ""
    if oracle:
        # The Oracle deep links run past 140 characters, so paper gets the
        # course title and the one instruction that actually works: search it.
        res += ('<div class="ps__sec"><h3>In Oracle Learning</h3><ul class="ps__res">%s</ul>'
                '<p class="ps__src">On paper, search these titles in Oracle Learning.</p></div>'
                % "".join('<li><a href="%s">%s</a></li>' % (esc(u), esc(l)) for l, u in oracle))
    if free:
        res += ('<div class="ps__sec"><h3>Free, outside Vanderbilt</h3><ul class="ps__res ps__res--url">%s</ul></div>'
                % "".join('<li><a href="%s">%s</a></li>' % (esc(u), esc(l)) for l, u in free))
    res_block = ("<h2>Where to go next</h2>" + res) if res else ""

    parts = [
        '\n  <section class="printsheet" aria-hidden="true">',
        '    <header class="ps__head">',
        '      <p class="ps__eyebrow">Anchor&#39;s Edge &middot; %s &middot; %s</p>' % (esc(spec["series"]), esc(spec["month"])),
        '      <h1>%s</h1>' % esc(spec["title"]),
        '      <p class="ps__tagline">%s</p>' % esc(spec["tagline"]),
        '      <p class="ps__goal">Goal %d &middot; %s</p>' % (spec["goal"], esc(g["short"])),
        '    </header>',
        '    <h2>What this session builds</h2>',
        '    <ol class="ps__obj">%s</ol>' % objectives,
        '    <h2>The rule to remember</h2>',
        '    <p class="ps__manifesto">%s</p>' % esc(spec["manifesto"]),
        '    <h2>What each part taught</h2>',
        '    %s' % rows,
        '    <h2>The recap, with the answers</h2>',
        '    %s' % quiz,
        '    <h2>Your commitment</h2>',
        '    <p>%s</p>' % esc(cap["lead"]),
        '    <ul class="ps__moves">%s</ul>' % moves,
        # Filled in by deck.js when the learner builds their card; the ruled
        # lines below are what prints if they did not, or printed in advance.
        '    <div class="ps__entered" id="psEntered" hidden></div>',
        '    <p class="ps__write" id="psWrite"><b>Mine:</b> ' + ('.' * 46) + ' &nbsp; <b>By when:</b> ' + ('.' * 14) + '</p>',
        '    %s' % deeper_block,
        '    %s' % res_block,
        '    <p class="ps__foot">%s</p>' % (SITE + "courses/" + spec["slug"] + "/"),
        '  </section>\n',
    ]
    return "\n".join(parts)


def course_config_js(spec):
    trainers, labs = [], []
    for sec in spec["sections"]:
        it = sec["interaction"]
        if it["type"] == "trainer":
            trainers.append({
                "rootId": sec["id"] + "-play", "title": it["playTitle"],
                "progressWord": it.get("progressWord", "Round"),
                "labels": it["labels"], "passAt": it["passAt"],
                "passMsg": it["passMsg"], "failMsg": it["failMsg"], "items": it["items"]})
        elif it["type"] == "builder":
            labs.append({
                "rootId": sec["id"] + "-lab", "outcomeTag": it["outcomeTag"],
                "slots": it["slots"], "heads": it["heads"], "reactions": it["reactions"]})
    cap = spec["capstone"]
    g = GOALS[spec["goal"]]
    config = {
        "trainers": trainers, "labs": labs, "recap": spec["recap"],
        "recapMsgs": spec.get("recapMsgs"),
        "capstone": {
            "whoRow": cap["whoRow"], "cardTitle": cap["cardTitle"],
            "copyTag": "%s · %s · Anchor's Edge" % (spec["title"], spec["month"]),
            "goalRow": "Goal %d, %s." % (spec["goal"], g["short"]),
            "evidenceRow": cap["evidenceRow"],
            "practices": cap["practices"], "whens": cap["whens"]},
    }
    # "</script>" inside any string would end the block early and kill every interaction
    return json.dumps(config, ensure_ascii=False, indent=1).replace("<", "\\u003c")


def build_course(spec):
    g = GOALS[spec["goal"]]
    slug = spec["slug"]
    course_url = SITE + "courses/" + slug + "/"
    sections_html = "".join(section_html(s, i + 1) for i, s in enumerate(spec["sections"]))
    nav_links = "".join('<a href="#%s">%s</a>' % (s["id"], esc(s["nav"])) for s in spec["sections"])
    objectives = "".join("<li>%s</li>" % esc(o) for o in spec["objectives"])
    agenda = ""
    cap = spec["capstone"]
    practice_chips = "".join(
        '<button class="opt" data-id="%s"><span>%s</span></button>' % (p["id"], esc(p["chip"]))
        for p in cap["practices"])
    when_chips = "".join(
        '<button class="opt" data-id="%s"><span>%s</span></button>' % (w["id"], esc(w["chip"]))
        for w in cap["whens"])
    footer_sections = "".join(
        '<li><a href="#%s">%s</a></li>' % (s["id"], esc(s["nav"])) for s in spec["sections"])
    closing = spec["closing"]

    values = {
        "title": esc(spec["title"]),
        "description": esc(spec["description"]),
        "slug": slug, "courseUrl": course_url,
        "series": esc(spec["series"]),
        "seriesSub": esc(SERIES_SUB[spec["series"]]),
        "month": esc(spec["month"]), "theme": esc(spec["theme"]),
        "goalNum": spec["goal"], "goalName": esc(g["name"]), "goalShort": esc(g["short"]),
        "goalShortHtml": (lambda w: esc(" ".join(w[:-1])) + " <em>" + esc(w[-1]) + "</em>")(g["short"].split()),
        "goalDesc": esc(g["desc"]),
        "goalLead": esc(spec.get("goalLead", "")),
        "titleHtml": spec["titleHtml"],
        "tagline": esc(spec["tagline"]),
        "heroLead": esc(spec["heroLead"]),
        "objectives": objectives, "skills": skills_html(spec["skills"]),
        "missionTie": esc(spec["missionTie"]),
        "agenda": agenda, "manifesto": esc(spec["manifesto"]),
        "sections": sections_html, "navLinks": nav_links,
        "capEyebrow": esc(cap["eyebrow"]), "capHeadline": cap["headline"],
        "capLead": esc(cap["lead"]),
        "whoLabel": esc(cap["whoLabel"]), "whoPlaceholder": esc(cap["whoPlaceholder"]),
        "practiceLabel": esc(cap["practiceLabel"]), "practiceChips": practice_chips,
        "whenChips": when_chips,
        "closeHeadline": closing["headline"], "closeLead": esc(closing["lead"]),
        "nextTag": esc(closing["nextTag"]), "nextTitle": esc(closing["nextTitle"]),
        "nextBody": esc(closing["nextBody"]), "brandline": esc(closing["brandline"]),
        "footerSections": footer_sections,
        "printsheet": printsheet_html(spec),
        "config": course_config_js(spec),
        "slideCount": "12",
    }
    _, _, f_tot, _ = timing(spec)
    ws = spec.get("format") == "workshop"
    values["fmtMinutes"] = str(f_tot)
    values["fmtModeLabel"] = "Minutes, in person" if ws else "Minutes, live"
    values["welcomeH1"] = ("Welcome. Scan the code to bring this workshop <em class=\"gold-text\">to your seat</em>." if ws else
                           "Welcome. Scan or click the chat link to bring this <em class=\"gold-text\">to your screen</em>.")

    html = COURSE_TEMPLATE
    for k, v in values.items():
        html = html.replace("[[%s]]" % k, str(v))
    leftover = re.findall(r"\[\[[a-zA-Z]+\]\]", html)
    if leftover:
        raise SystemExit("unfilled template tokens: %s" % sorted(set(leftover)))
    return html


# ---------------------------------------------------------------- notes.json
def std_notes(spec):
    """Standard runbook blocks for the fixed slides; course slides come
    from the spec's facilitator entries."""
    g = GOALS[spec["goal"]]
    fac = spec["facilitator"]
    series = spec["series"]
    F_MIN, C_MIN, F_TOT, C_TOT = timing(spec)
    ws = spec.get("format") == "workshop"

    def sec(id_, title, purpose, say, facilitate, extra=None):
        d = {"id": id_, "title": title, "minutes": F_MIN[id_],
             "coreMinutes": C_MIN[id_], "purpose": purpose, "say": say,
             "facilitate": facilitate}
        if extra:
            d.update(extra)
        return d

    out = [
        sec("s-welcome", "Welcome / QR",
            ("Get everyone into the deck on their own device and set the tone: %d minutes, in person, hands on." % F_TOT) if ws else
            "Get everyone into the deck on their own screen and set the tone: 45 minutes, live, hands on.",
            ("Welcome to the %s. Scan the code so this session runs on your device too. %d minutes, one focus: %s" % (series, F_TOT, spec["tagline"].rstrip(".") + ".")) if ws else
            "Welcome to %s. Scan the code or click the link in chat so this session runs on your screen too. Forty-five minutes, one focus: %s" % (series, spec["tagline"].rstrip(".") + "."),
            (["Slide projected as people arrive; phones up before you speak.",
              "State the norm once: type into your own device, nothing you enter is saved or sent."] if ws else
             ["Slide up as people join; link pasted in chat every few minutes.",
              "State the norm once: type into your own screen, nothing you enter is saved or sent."]),
            {"watchFor": "People lurking without the deck open. The interactions only land if the deck is on their screen.",
             "transition": "Before the topic, thirty seconds on why Vanderbilt is asking for this hour."}),
        sec("s-mission", "Why we're here",
            "Anchor the session in the Chancellor's charge and name the goal this month serves, inside one minute.",
            "One sentence from the Chancellor sits over everything we do: Vanderbilt will define the great university of the 21st Century and be it. %s This month serves Goal %d, %s." % (
                spec["missionTie"], spec["goal"], g["short"]),
            ["Read the mission line slowly, once; name the goal, once.",
             "No discussion here; the whole slide is under a minute."],
            {"transition": "Here is what you will be able to do in %d minutes." % F_TOT}),
        sec("s-hero", "Objectives",
            "Set the contract for the session in about a minute; this slide is also the roadmap.",
            "By the end of this session you will be able to: " + "; ".join(o.rstrip(".").lower() for o in spec["objectives"]) + ". We take them in order, and each one has something to practice.",
            ["Read the three objectives briskly; they double as the agenda.",
             "Point at the goal chip once, then move."],
            {"transition": "First objective."}),
    ]
    for key, id_ in (("s1", "s-one"), ("s2", "s-two"), ("s3", "s-three")):
        n = dict(fac[key])
        n["id"] = id_
        n["minutes"] = FULL_MIN[id_]
        n["coreMinutes"] = CORE_MIN[id_]
        out.append(n)
    out.append(sec("s-belief", "The core idea",
        "Land the one sentence the session exists to install.",
        "If you keep one sentence from today, this is it. Read it once, out loud: %s" % spec["manifesto"],
        ["Pause two beats after reading; the word animation carries it."],
        {"coreNote": "Core: pass through in stride; the sentence reads itself.",
         "transition": "The recap makes it stick."}))
    out.extend([
        sec("s-recap", "Recap quiz",
            "Score the learning while it is fresh; wrong answers are teaching moments, not failures.",
            "Three questions, on your own screen. Answer honestly; the explanations are where the learning sticks.",
            ["Give the room 90 seconds to run it individually.",
             "Ask for a show of results in chat: how many got 3 of 3?",
             "Read out the explanation for whichever question drew the most misses."],
            {"watchFor": "Rushing past the why lines. The explanations carry the teaching.",
             "transition": "Now point it at your real week."}),
        sec("s-plan", "Capstone commitment",
            "Convert the session into one named, dated action per person.",
            fac["capstoneSay"],
            ["Two quiet minutes; everyone builds their own card.",
             "Invite two or three volunteers to read their card aloud or paste it in chat.",
             "Remind: copy the card somewhere you will see it this week."],
            {"watchFor": "Vague entries. Nudge for a name-able situation and a real date.",
             "transition": "Last slide."}),
        sec("s-close", "Closing",
            "End with the next step and where this thread continues.",
            fac["closeSay"],
            ["Point at the next-step card; one sentence.",
             "Name the rest of the week's rhythm: the other sessions echo this month's theme."]),
    ])
    return out


def build_notes(spec):
    g = GOALS[spec["goal"]]
    fac = spec["facilitator"]
    F_MIN, C_MIN, F_TOT, C_TOT = timing(spec)
    ws = spec.get("format") == "workshop"
    return {
        "meta": {
            "program": "%s · %s · Anchor's Edge · Vanderbilt" % (spec["title"], spec["series"]),
            "totalMinutes": F_TOT,
            "audience": fac["audience"],
            "roomSetup": ("In person, navigator led: projector plus presenter device, tables that pair easily, learners on their own devices via the welcome-slide QR. Nothing typed into the deck is saved or sent." if ws else
                          "Virtual, instructor led: camera on, deck link in chat, breakouts of 2 available. Learners follow on their own screens via the welcome-slide link or QR. Nothing typed into the deck is saved or sent."),
            "postSession": fac["pulse"],
            "paths": {
                "full": {"minutes": F_TOT,
                         "description": ("The full %d-minute in-person workshop: every exercise runs at tables, debriefs are voices in the room, and the capstone gets read-alouds. The per-section minutes sum to %d including transitions." % (F_TOT, F_TOT)) if ws else
                         "The full 45-minute virtual session: every interaction runs live, breakouts run in pairs, and the capstone gets read-alouds. The per-section minutes on each slide sum to 45 including transitions."},
                "core": {"minutes": C_TOT,
                         "description": ("The %d-minute path: agenda and core-idea slides pass in stride, table time shortens, debriefs shrink to one voice per table. Never cut the exercises or the capstone." % C_TOT) if ws else
                         "The 30-minute slot: agenda and core-idea slides pass in stride, breakouts become solo passes with chat share-outs, debriefs shrink to one voice. Never cut the section interactions or the capstone."},
            },
            "framework": "ATD facilitator-guide structure: per module SAY / DO / ASK (with anticipated responses) / DEBRIEF / TRANSITION, plus preparation checklists, materials, contingencies, and a tough-questions bank.",
            "goal": "Goal %d, %s." % (spec["goal"], g["short"]),
            "materials": [
                "Meeting platform with screen share and breakout rooms; deck link ready to paste in chat",
                "Facilitator machine with the facilitator edition open; notifications off",
                "Learners on their own devices with the learner link",
                "Chat open for share-outs; the capstone copy button pastes there cleanly",
            ],
            "prep": {
                "weekBefore": [
                    "Run the learner edition start to finish and do every interaction honestly; you will demo at least one live.",
                    "Read this month's theme page on the Anchor's Edge dashboard so the goal tie-in is fluent.",
                    "Send the invite with the learner link and one line on what to bring.",
                ],
                "dayBefore": [
                    "Test screen share with the facilitator edition; confirm the notes rail is readable.",
                    "Open the learner link on a second device; the QR must land there.",
                    "Run the section interactions once so you can drive them without reading.",
                ],
                "thirtyMinBefore": [
                    "Welcome slide up as people join; link pasted in chat.",
                    "Close every other tab; silence the machine.",
                    "Breakout rooms pre-configured in pairs.",
                ],
            },
            "contingencies": fac.get("contingencies", [
                {"if": "Screen share or the site fails mid-session",
                 "then": "Paste the learner link in chat and narrate from your own browser; every interaction runs on learner devices without the share."},
                {"if": "Breakout rooms are unavailable",
                 "then": "Run the breakout prompts as 60-second chat storms: everyone types their answer at once, you read the best three aloud."},
                {"if": "The room is silent on debriefs",
                 "then": "Switch to chat-first: ask for one-word answers in chat, then invite one person to expand on theirs."},
            ]),
            "toughQuestions": fac.get("toughQuestions", []),
            "templates": fac.get("templates", []),
        },
        "sections": std_notes(spec),
    }


# ---------------------------------------------------------------- template
COURSE_TEMPLATE = open(os.path.join(ROOT, "tools", "course-template.html")).read()


def run(slug):
    spec_path = os.path.join(ROOT, "specs", slug + ".json")
    spec = json.load(open(spec_path))
    errors = []
    if spec.get("slug") != slug:
        errors.append("slug %r does not match filename %r; the QR code would 404"
                      % (spec.get("slug"), slug))
    validate(spec, errors)
    if errors:
        raise SystemExit(slug + ":\n  " + "\n  ".join(errors))
    check_dashes(json.dumps(spec, ensure_ascii=False), slug)
    html = build_course(spec)
    check_dashes(html, slug)
    outdir = os.path.join(ROOT, "courses", slug)
    os.makedirs(os.path.join(outdir, "facilitator"), exist_ok=True)
    open(os.path.join(outdir, "index.html"), "w").write(html)
    notes = build_notes(spec)
    check_dashes(json.dumps(notes, ensure_ascii=False), slug)
    with open(os.path.join(outdir, "facilitator", "notes.json"), "w") as f:
        json.dump(notes, f, ensure_ascii=False, indent=1)
    print("built courses/%s (index.html + facilitator/notes.json)" % slug)


def prune():
    """Remove generated course folders whose spec no longer exists."""
    import shutil
    specs = {f[:-5] for f in os.listdir(os.path.join(ROOT, "specs")) if f.endswith(".json")}
    cdir = os.path.join(ROOT, "courses")
    if not os.path.isdir(cdir):
        return
    for d in sorted(os.listdir(cdir)):
        if d not in specs and os.path.isdir(os.path.join(cdir, d)):
            shutil.rmtree(os.path.join(cdir, d))
            print("pruned orphaned courses/%s (no spec)" % d)


if __name__ == "__main__":
    slugs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--prune" in sys.argv or not slugs:
        prune()
    if not slugs:
        slugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "specs"))
                       if f.endswith(".json"))
    for s in slugs:
        run(s)
