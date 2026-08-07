# Anchor's Edge

The weekly virtual learning series, the
Apply arm of CHART. One repo: the month-by-month dashboard at the root
plus 27 course sites under `courses/<slug>/`, published as one GitHub
Pages site at https://me5231979.github.io/Anchors-Edge/.

Slugs are `<mon>-<day>`: `oct-monday` ... `jun-thursday`. Manager Monday
is for managers; Take-Off Tuesday and Thrive Thursday are for all staff;
Wellness Wednesday is a nod line on the dashboard, never a course.

## Content lives in specs/

Never hand-edit `courses/**` or `index.html`; they are generated. Each
course is one JSON spec in `specs/<slug>.json` (rules and limits:
`tools/AUTHORING.md`). Every slide must fit one screen with zero
scrolling (virtual instructor-led delivery); the generator enforces copy
length limits and fails on any em or en dash.

## Pipeline

```
python3 tools/generate.py [slug ...]         # spec -> courses/<slug>/index.html + facilitator/notes.json
python3 tools/build-web.py [slug ...]        # -> web/index.html (self-paced; strips data-classroom)
python3 tools/build-facilitator.py [slug ...]# -> facilitator/index.html + guide.html (printable)
python3 -m http.server 8931 &                # needed by shoot + qa
python3 tools/shoot.py [slug ...]            # -> facilitator/img/<slide>.jpg for the guide
python3 tools/build-dashboard.py             # -> index.html (reads all specs)
python3 tools/qa.py --all --dashboard        # Playwright: fit, interactions, console
```

Regenerate web + facilitator + dashboard after ANY spec change; re-shoot
after any visual change.

## Shared engine

`assets/` at the root serves every course (fonts, VU lockups,
`css/styles.css` deck engine, `js/deck.js` config-driven interactions,
`js/qrcode.js`). Course pages reference it at `../../assets/`; the web
and facilitator builders rewrite depth automatically. Interaction data
is injected per course as `window.COURSE` by the generator; the three
interaction types are trainer (scenario rounds), builder (2-slot choice
lab), and check (concept card + one question).

## Fixed session shape (45 full / 30 core)

welcome(QR, classroom only) > mission (Chancellor's charge, trimmed) >
goal (this month's target with baseline/Q4 meter) > hero (objectives +
goal chip) > agenda > three teaching sections (one interaction each) >
manifesto > recap quiz (3 Q) > capstone commitment card > closing.
Timing per section is fixed in `tools/generate.py` (FULL_MIN/CORE_MIN)
and sums exactly to 45 and 30.

## Publishing

```
git push -u origin <branch>
git branch -f gh-pages main && git push -f origin gh-pages   # when publishing from main
```
