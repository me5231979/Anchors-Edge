# Authoring a course spec for Anchor's Edge

Each course is one JSON file in `specs/<slug>.json`. The generator
(`tools/generate.py <slug>`) turns it into the full course site and
validates it hard. Your spec is done ONLY when `python3 tools/generate.py
<slug>` exits cleanly.

Study `specs/oct-monday.json` first; it is the exemplar. Match its
register, structure, and level of craft.

## The program

Anchor's Edge is the ongoing Apply arm of CHART, Vanderbilt's enterprise
program for safe, confident, productive AI use. It is a 45-minute weekly
VIRTUAL instructor-led series. Every month lands on one enterprise goal;
every session that week echoes the month's theme. Courses are read on
slides in an online dashboard during a live virtual class: copy must be
SHORT, one idea per slide, zero scrolling.

Never time-box the program in learner-facing copy: no "nine-month
program", no "nine months", no program date range, and no month names
outside a course's own month identity (the program grows to 12 months
next year). Say "the series" or "this month's theme". A course may name
its own month and the sessions of its own week.

The calendar: Oct: See the Talent Around You (G1) · Nov: The Transfer
Portal in Practice (G1) · Dec: The Vanderbilt Manager Standard (G2) ·
Jan: AI at Work: Start Where You Are (G3) · Feb: Retain, Grow, Move (G1)
· Mar: Coaching as the Core Manager Behavior (G2) · Apr: Spot AI-Exposed
Work (G3) · May: Measured Leader Behavior (G2) · Jun: From Insight to
Action (G3).

## Real systems and terminology (hard rule)

Name ONLY things Vanderbilt actually has or that the plan names:
the **Talent Marketplace** and the **Transfer Portal** (the two talent
systems; there is NO system called "Workforce Intelligence" and that
phrase must never appear), Oracle (1:1 templates, feedback tools, goals),
engagement/pulse surveys, CHART, LinkedIn Learning courses of the month,
and navigator-led in-person sessions. Never state goal percentages,
baselines, or targets anywhere; name the goal only.

## Two genuinely different experiences

The live class and the self-paced edition are built from one spec but
must feel different:
- **Live class**: more context, less knowledge-checking. In `check`
  sections the quiz is replaced on screen by an "In the room" context
  card (`interaction.context`) plus a facilitator-led discussion prompt
  (`interaction.discuss`). Facilitator notes for check sections run the
  discussion, never a quiz.
- **Self-paced**: keeps the knowledge checks AND goes deeper. Every
  section carries a `deeper` block (title, body, 2-3 solo activity
  steps) that renders only in the self-paced edition, diving further
  into the section's idea with a hands-on exercise.

## Audience rule

- **Manager Monday**: people managers. "Your team" framing is correct.
- **Take-Off Tuesday** and **Thrive Thursday**: ALL Vanderbilt staff.
  Never assume the learner manages anyone. Frame examples around a
  person's own work, career, and collaborations.

## Hard rules (the generator enforces most of them)

1. ZERO em dashes and ZERO en dashes anywhere in the file. Rewrite
   around them. The build fails on the first one found.
2. Character limits (stripped of tags): heroLead 260, lead 260,
   missionTie 250, goalLead 230, manifesto 90, objectives 110 each,
   agenda descriptions 110, trainer q 150, trainer why 170, builder
   option text 100, builder coach 180, check card text 240, check/trainer
   labels 60, recap options 80 each, recap why 170, practice move 170,
   group/solo prompts 170.
3. Exactly: 3 objectives, 3 agenda items, 3 sections, 3 recap questions
   (4 options each), 3 capstone practices, 3 capstone whens, 3 or 4
   skills.
4. Section ids are fixed: `s-one`, `s-two`, `s-three`.
5. Each section has ONE interaction. Across the three sections use all
   three types once each: `check`, `trainer`, `builder` (any order that
   fits the teaching).
6. Headlines (`titleHtml`, section `headline`, capstone `headline`,
   closing `headline`): serif with EXACTLY one italic phrase via
   `<em>...</em>` (in `titleHtml` use `<em class="gold-text">`). No
   other HTML in any field except those four headline fields.
7. Human, warm, direct copy. No negative parallelisms ("not X, but Y"),
   no rule-of-three stacks, no marketing filler. Read it aloud in your
   head. Contractions welcome.
8. AI months (Dec, Mar, Jun): the shared traffic light must never be
   contradicted: green = public or generic; yellow = internal, approved
   VU tools only; red = private information about people, never.
9. Privacy norm in anything touching people data: roles, never names.
10. JSON: plain ASCII quotes, no trailing commas, `·` (middle dot) is
    allowed and used in eyebrows.

## Field-by-field notes

- `slug`: `<mon>-<day>` e.g. `nov-monday`, `mar-thursday`.
- `series`: exact name: `Manager Monday`, `Take-Off Tuesday`,
  `Thrive Thursday`.
- `month` e.g. `November 2026`; `monthShort` e.g. `Nov`; `monthIndex` 1-9.
- `theme`: the month's theme from the plan.
- `goal`: 1, 2, or 3 (the generator adds names, metrics, meter).
- `title`: short display title (2-4 words), distinct across all 27.
- `tagline`: the session focus line from the plan, lightly polished.
- `missionTie`: one or two sentences connecting THIS session to the
  Chancellor's "define the great university of the 21st Century" charge.
  Mention one Area of Focus by name where natural.
- `goalLead`: one sentence on where this session fits the month's goal.
- `manifesto`: the one sentence of the session. Short, punchy, quotable.
- `sections[*].group`: a breakout prompt for the live class (pairs, 3
  min). `solo`: the same work for the self-paced reader. Both required.
- `capstone`: one typed field + practice chips + when chips. The
  generator adds the goal row and copy button automatically.
- `facilitator.s1/s2/s3`: full Say / facilitate(Do) / ask{q, expect,
  respond} / debrief / watchFor / transition / coreNote blocks, plus
  `title` and `purpose`. Say blocks are spoken word-for-word scripts,
  90 seconds max, natural voice.
- `facilitator.capstoneSay` / `closeSay`: spoken scripts for those two
  moments. In `closeSay`, name the other sessions coming that week
  (Tuesday/Thursday sessions of the same month; Monday names both, the
  others point forward only, and Thursday points to next week/month).
- `facilitator.audience`, `pulse`, `contingencies` (4, first two copied
  from the exemplar), `toughQuestions` (3), `templates` (2: pre-work
  invite + 7-day pulse).

## Interaction craft

- `trainer`: 3 scenario rounds, one shared 3-label answer set. The
  labels are the concept's categories. `passAt` 2. Scenarios concrete
  and Vanderbilt-plausible (roles like coordinator, analyst, advisor).
- `builder`: 2 slots x 3 options (weak 1pt / mid 2pts / strong 3pts),
  each with a coach line that teaches WHY. heads + reactions for
  strong/mid/weak tiers; reactions describe what happens days later.
- `check`: one gold-bordered concept card (the teachable rule) + one
  3-option question, exactly one correct, every why teaches. REQUIRED
  extra fields: `context` (limit 300; the richer framing the live room
  gets instead of the quiz) and `discuss` (limit 170; the facilitator's
  discussion prompt).

## The deeper block (required on every section)

`sections[*].deeper = {"title": ..., "body": ..., "steps": [...]}`.
Limits: title 60, body 430, steps 2-3 at 170 each. Self-paced only.
The body teaches one layer beneath the slide (the nuance, the edge case,
the worked example); the steps are a concrete solo activity that applies
it to the learner's real work. Do not repeat the slide copy.

## Verify before you finish

Run: `python3 tools/generate.py <slug>` for each spec you wrote.
Fix every reported error. Do not run build-web, build-facilitator, or
qa; the coordinator runs those.
