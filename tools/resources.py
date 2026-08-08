#!/usr/bin/env python3
"""Per-course resource lists for the printable takeaway sheet.

Two Oracle Learning courses (real deep links from the active catalog)
and two free outside resources per course. Free means free: TED talks,
open podcasts, and public reports, never anything behind a paywall.
Used by tools/generate.py; edit here, then rerun the generator.
"""

FREE = {
    "safety":   ('Amy Edmondson: Building a psychologically safe workplace (TEDxHGSE, 12 min)',
                'https://www.youtube.com/watch?v=LhoLuui9gX8'),
    "rework":   ('Google re:Work: Understand team effectiveness (free guide)',
                'https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness'),
    "convo":    ('Celeste Headlee: 10 ways to have a better conversation (TED, 12 min)',
                'https://www.ted.com/talks/celeste_headlee_10_ways_to_have_a_better_conversation'),
    "listen":   ('Julian Treasure: 5 ways to listen better (TED, 8 min)',
                'https://www.ted.com/talks/julian_treasure_5_ways_to_listen_better'),
    "adapt":    ('Natalie Fratto: 3 ways to measure your adaptability (TED, 6 min)',
                'https://www.ted.com/talks/natalie_fratto_3_ways_to_measure_your_adaptability_and_how_to_improve_it'),
    "mollick":  ('Ethan Mollick, One Useful Thing (free newsletter on AI at work)',
                'https://www.oneusefulthing.org/'),
    "eurich":   ('Tasha Eurich: Increase your self-awareness with one simple fix (TED, 17 min)',
                'https://www.ted.com/talks/tasha_eurich_increase_your_self_awareness_with_one_simple_fix'),
    "ideacast": ('HBR IdeaCast (free weekly management podcast)',
                'https://hbr.org/podcasts'),
    "worklife": ('WorkLife with Adam Grant (free TED podcast)',
                'https://www.ted.com/podcasts/worklife'),
    "wef":      ('World Economic Forum: Future of Jobs Report 2025 (free)',
                'https://www.weforum.org/publications/the-future-of-jobs-report-2025/'),
    "cfl":      ('Coaching for Leaders (free weekly podcast, Dave Stachowiak)',
                'https://coachingforleaders.com/podcast/'),
    "mt1on1":   ('Manager Tools: One-on-Ones (free podcast series)',
                'https://www.manager-tools.com/map-universe/one-ones'),
    "mtbasics": ('Manager Tools: the manager basics (free podcast series)',
                'https://www.manager-tools.com/manager-tools-basics'),
    "deloitte": ('Deloitte Global Human Capital Trends (free report)',
                'https://www.deloitte.com/us/en/insights/topics/talent/human-capital-trends.html'),
    "sinek":    ('Simon Sinek: Why good leaders make you feel safe (TED, 12 min)',
                'https://www.ted.com/talks/simon_sinek_why_good_leaders_make_you_feel_safe'),
    "shrmstay": ('SHRM: Stay interview questions (free tool)',
                'https://www.shrm.org/topics-tools/tools/forms/stay-interview-questions'),
    "giver":    ('Adam Grant: Are you a giver or a taker? (TED, 13 min)',
                'https://www.ted.com/talks/adam_grant_are_you_a_giver_or_a_taker'),
    "atdment":  ('ATD: Do your employees need coaching or mentoring? (free article)',
                'https://www.td.org/content/atd-blog/do-your-employees-need-coaching-or-mentoring'),
    "atdcoach": ('ATD Talent Development Framework: Coaching (free article)',
                'https://www.td.org/insights/the-atd-talent-development-framework-coaching'),
    "burkus":   ('David Burkus: How to hack networking (TEDx, 11 min)',
                'https://www.ted.com/talks/david_burkus_how_to_hack_networking'),
    "netpod":   ('WorkLife: Networking for people who hate networking (TED podcast)',
                'https://www.ted.com/talks/worklife_with_adam_grant_networking_for_people_who_hate_networking'),
    "dweck":    ('Carol Dweck: The power of believing that you can improve (TED, 10 min)',
                'https://www.ted.com/talks/carol_dweck_the_power_of_believing_that_you_can_improve'),
    "mmai":     ('MIT Sloan Management Review: Me, Myself, and AI (free podcast)',
                'https://sloanreview.mit.edu/audio-series/me-myself-and-ai/'),
    "sadun":    ('MIT SMR: Reskilling the workforce with AI, Raffaella Sadun (free audio)',
                'https://sloanreview.mit.edu/audio/reskilling-the-workforce-with-ai-harvard-business-schools-raffaella-sadun/'),
    "gilbert":  ('Dan Gilbert: Why we make bad decisions (TED, 34 min)',
                'https://www.ted.com/talks/dan_gilbert_why_we_make_bad_decisions'),
    "weakties": ('TED Ideas: Talk to the people you already know (free article)',
                'https://ideas.ted.com/how-to-find-your-next-job-talk-to-the-people-you-already-know/'),
}

# slug -> {"oracle": [{"label","url"}, ...], "free": [FREE keys]}
COURSE = {
    "apr-monday": {
        "oracle": [
            {"label": 'Skills for Leading the Future of Work',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857269013'},
            {"label": 'Building an Adaptability Mindset in the Age of AI',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002877629563'},
        ],
        "free": ['wef', 'sadun'],
    },
    "apr-thursday": {
        "oracle": [
            {"label": 'Critical Thinking',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857213040'},
            {"label": 'Spotting Misinformation Online',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856960858'},
        ],
        "free": ['gilbert', 'mollick'],
    },
    "apr-tuesday": {
        "oracle": [
            {"label": 'Business Process Improvement',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857668358'},
            {"label": 'Systems Thinking and Process Improvement',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002978567564'},
        ],
        "free": ['mollick', 'mmai'],
    },
    "apr-workshop": {
        "oracle": [
            {"label": 'Building a Data-Driven Skills-First Workforce Strategy',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857133092'},
            {"label": 'Human Resources: Strategic Workforce Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002967757630'},
        ],
        "free": ['wef', 'deloitte'],
    },
    "dec-monday": {
        "oracle": [
            {"label": 'Avoiding New Manager Mistakes',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856838381'},
            {"label": 'Oracle Cloud: Training for Vanderbilt Managers',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001205002309'},
        ],
        "free": ['mtbasics', 'sinek'],
    },
    "dec-thursday": {
        "oracle": [
            {"label": 'Communicating with Clarity as a Manager',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857301175'},
            {"label": 'Using Active Listening in Workplace Situations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001635276452'},
        ],
        "free": ['listen', 'convo'],
    },
    "dec-tuesday": {
        "oracle": [
            {"label": 'Goal Setting for Business Impact as a Manager',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856848229'},
            {"label": 'Oracle Cloud: Training for Vanderbilt Managers',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001205002309'},
        ],
        "free": ['mt1on1', 'ideacast'],
    },
    "dec-workshop": {
        "oracle": [
            {"label": 'Demonstrating Accountability as a Leader',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856848459'},
            {"label": 'Building Accountability into Your Culture',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856480391'},
        ],
        "free": ['mtbasics', 'safety'],
    },
    "feb-monday": {
        "oracle": [
            {"label": 'Succession Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857590895'},
            {"label": 'Developing Talent through Succession Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002804335701'},
        ],
        "free": ['shrmstay', 'deloitte'],
    },
    "feb-thursday": {
        "oracle": [
            {"label": 'Mentorship, Sponsorship, and Lifting Others as You Climb',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856559880'},
            {"label": 'Nano Tips for Effective Sponsorship as a Leader with India Gary-Martin',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002900901365'},
        ],
        "free": ['atdment', 'giver'],
    },
    "feb-tuesday": {
        "oracle": [
            {"label": 'Creating a Career Plan',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857219110'},
            {"label": 'Creating Your Internal Mobility Career Plan',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857307403'},
        ],
        "free": ['dweck', 'weakties'],
    },
    "feb-workshop": {
        "oracle": [
            {"label": 'Building Employee Engagement',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003102002595'},
            {"label": 'Storytelling for Recruiting and Employee Retention',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856596215'},
        ],
        "free": ['shrmstay', 'cfl'],
    },
    "jan-monday": {
        "oracle": [
            {"label": 'Responsible AI for Managers',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002868826154'},
            {"label": 'Foundations of Responsible AI',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003003089513'},
        ],
        "free": ['mollick', 'mmai'],
    },
    "jan-thursday": {
        "oracle": [
            {"label": 'Developing Adaptability as a Manager',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857638225'},
            {"label": 'Navigating Ambiguity',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856640967'},
        ],
        "free": ['adapt', 'dweck'],
    },
    "jan-tuesday": {
        "oracle": [
            {"label": 'What Is Generative AI?',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857283770'},
            {"label": 'Top Ten AI Prompts',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002934576075'},
        ],
        "free": ['mollick', 'wef'],
    },
    "jan-workshop": {
        "oracle": [
            {"label": 'Prompt Engineering with ChatGPT',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857373384'},
            {"label": 'AI Productivity Hacks to Reimagine Your Workday and Career',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857362271'},
        ],
        "free": ['mmai', 'deloitte'],
    },
    "jun-monday": {
        "oracle": [
            {"label": 'Upskilling and Reskilling Your Workforce',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857242228'},
            {"label": 'Human Resources: Strategic Workforce Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002967757630'},
        ],
        "free": ['sadun', 'wef'],
    },
    "jun-thursday": {
        "oracle": [
            {"label": 'Decision Making Excellence',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003100146234'},
            {"label": 'Data-Backed Decision Making',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857188789'},
        ],
        "free": ['gilbert', 'worklife'],
    },
    "jun-tuesday": {
        "oracle": [
            {"label": 'Becoming AI-First: A 90-Day Plan for Business Teams',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003069898991'},
            {"label": 'Introduction to Project Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003062262820'},
        ],
        "free": ['mollick', 'deloitte'],
    },
    "jun-workshop": {
        "oracle": [
            {"label": 'Strategic Planning Foundations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003080794351'},
            {"label": 'Change Management',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002897794772'},
        ],
        "free": ['wef', 'ideacast'],
    },
    "mar-monday": {
        "oracle": [
            {"label": 'The Coaching Lab - A 3-Part Series for Building Coaching Skills',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002696622540'},
            {"label": 'Coaching Employees through Difficult Situations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857564343'},
        ],
        "free": ['atdcoach', 'cfl'],
    },
    "mar-thursday": {
        "oracle": [
            {"label": 'Empathy at Work',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856848505'},
            {"label": 'Effective Listening',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003043042218'},
        ],
        "free": ['listen', 'convo'],
    },
    "mar-tuesday": {
        "oracle": [
            {"label": 'Having Career Conversations with Your Team',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856509316'},
            {"label": 'Building a Leadership Development Plan',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001863876247'},
        ],
        "free": ['dweck', 'mt1on1'],
    },
    "mar-workshop": {
        "oracle": [
            {"label": 'Powerful Questions to Build Team Trust, Engagement, and Psychological Safety',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002889351882'},
            {"label": 'The Coaching Lab - A 3-Part Series for Building Coaching Skills',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002696622540'},
        ],
        "free": ['cfl', 'atdment'],
    },
    "may-monday": {
        "oracle": [
            {"label": 'Performance Management Foundations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002987328913'},
            {"label": 'Measuring Team Performance',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857511183'},
        ],
        "free": ['mtbasics', 'ideacast'],
    },
    "may-thursday": {
        "oracle": [
            {"label": 'Developing Self-Awareness',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857551351'},
            {"label": 'Strategies to Improve Self-Awareness',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856977695'},
        ],
        "free": ['eurich', 'dweck'],
    },
    "may-tuesday": {
        "oracle": [
            {"label": 'Receiving Feedback with an Open Mind',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002733071337'},
            {"label": 'Employee Engagement Essentials',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003102009960'},
        ],
        "free": ['eurich', 'ideacast'],
    },
    "may-workshop": {
        "oracle": [
            {"label": 'Having Difficult Conversations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857628178'},
            {"label": 'HRVU: Managing Difficult Conversations',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001747867709'},
        ],
        "free": ['mtbasics', 'cfl'],
    },
    "nov-monday": {
        "oracle": [
            {"label": 'Driving Internal Mobility as a People Manager',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857296981'},
            {"label": 'Promoting Internal Mobility as a Manager',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856580693'},
        ],
        "free": ['ideacast', 'cfl'],
    },
    "nov-thursday": {
        "oracle": [
            {"label": 'Building Your Professional Network',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300001635002672'},
            {"label": 'Managing Your Professional Network',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856819272'},
        ],
        "free": ['burkus', 'netpod'],
    },
    "nov-tuesday": {
        "oracle": [
            {"label": 'Navigating Internal Mobility as an Employee',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857046731'},
            {"label": 'Creating Your Internal Mobility Career Plan',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857307403'},
        ],
        "free": ['weakties', 'deloitte'],
    },
    "nov-workshop": {
        "oracle": [
            {"label": 'Rock Your LinkedIn Profile',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002958309506'},
            {"label": 'Creating Your Personal Brand',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857187823'},
        ],
        "free": ['wef', 'giver'],
    },
    "oct-monday": {
        "oracle": [
            {"label": 'Skills-First Talent Management',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857337579'},
            {"label": 'Considering Transferable Skills in Talent Acquisition and Retention',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857069154'},
        ],
        "free": ['rework', 'shrmstay'],
    },
    "oct-thursday": {
        "oracle": [
            {"label": 'Applied Curiosity',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857664663'},
            {"label": 'Lose Your Fear of Asking Questions at Work',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002856548322'},
        ],
        "free": ['convo', 'worklife'],
    },
    "oct-tuesday": {
        "oracle": [
            {"label": 'Navigate: Using the Talent Marketplace for Career Growth at Vanderbilt',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003063355965'},
            {"label": 'Skills and the Internal Talent Marketplace',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002857338453'},
        ],
        "free": ['wef', 'deloitte'],
    },
    "oct-workshop": {
        "oracle": [
            {"label": 'Human Resources: Strategic Workforce Planning',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300002967757630'},
            {"label": 'Manager Monday - Talent Marketplace',
             "url": 'https://ecsr.fa.us2.oraclecloud.com/fscmUI/redwood/learner/learn/redirect?learningItemType=ORA_COURSE&learningItemId=300003069406051'},
        ],
        "free": ['rework', 'wef'],
    },
}


def for_slug(slug):
    """(oracle, free) as lists of (label, url); empty lists if unmapped."""
    e = COURSE.get(slug)
    if not e:
        return [], []
    oracle = [(o["label"], o["url"]) for o in e["oracle"]]
    free = [FREE[k] for k in e["free"] if k in FREE]
    return oracle, free
