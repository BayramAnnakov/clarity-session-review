#!/usr/bin/env python3
"""Templatized session-intelligence report generator.

The report is DATA-DRIVEN and reproducible: you re-run it, you don't rewrite it.
This example uses inline synthetic data; in a real run these lists are loaded from the
run's data JSONs (the triage classifications, the watched-session observations, etc.).

It encodes three TEMPLATE INVARIANTS the skill requires on every report — enforced by
asserts so a run can't silently drop them:
  1. Every headline number carries its SOURCE (sessions vs database).
  2. The mix chart always carries a plain-language caption that explains the bar.
  3. Every finding pairs with a recommended action + an owner.

Run:  python3 build_report.py   ->  writes report.html
"""
import html, os

BASE = os.path.dirname(os.path.abspath(__file__))
esc = html.escape

# --- census (in a real run: computed from the triage classifications) ------------
# bucket -> (count, colour, label, is_real_activity)
CENSUS = [
    ('core_task',   62, '#2a78d6', 'core task',      True),
    ('reviewing',   28, '#5a9be0', 'reviewing',      True),
    ('hit_a_gate',  14, '#c85a2a', 'hit a gate',     True),
    ('novel',        6, '#6d5bd0', 'novel',          True),
    ('signin_only', 41, '#c9c7bf', 'sign-in only',   False),
    ('bounce',     180, '#dedcd3', 'thin bounce',    False),
    ('parked_tab',  49, '#b7b5ac', 'parked tab',     False),
    ('team_or_test',82, '#efeee8', 'team/test',      False),
]
TOTAL = sum(c for _, c, _, _, _ in CENSUS)
act_n = sum(c for _, c, _, _, real in CENSUS if real)
noise_n = TOTAL - act_n
# distinct people can NOT be derived from session buckets (principle 6) — it comes
# from the attribution join; in a real run load it from the enrichment data.
PEOPLE = '~26'
thin_n = sum(c for k, c, _, _, _ in CENSUS if k in ('signin_only', 'bounce', 'parked_tab'))

barseg = ''.join(
    f'<span style="width:{100*c/TOTAL:.1f}%;background:{col}" title="{lab}: {c}"></span>'
    for _, c, col, lab, _ in CENSUS)

def legend(real):
    return ' '.join(
        f'<span><i style="background:{col}"></i>{lab} {c}</span>'
        for _, c, col, lab, r in CENSUS if r == real and c >= 3)

# --- headline stats: (number, caption, SOURCE) -----------------------------------
# INVARIANT 1: the third element (source) must be non-empty for every stat.
STATS = [
    (PEOPLE, 'real external people (the true audience)',        'from sessions, after removing noise'),
    (f'{100*thin_n//TOTAL}%', 'of sessions were thin — bounces, sign-in-only, parked tabs', 'from sessions (computed from the census)'),
    ('1',    'user reached the connect step — none new',   'from sessions + database'),
    ('~2k',  'accounts carry a migrated shared expiry date',    'from database (all accounts)'),
]
assert all(len(s) == 3 and s[2].strip() for s in STATS), \
    "TEMPLATE INVARIANT 1: every stat card must carry a source label"
statcards = ''.join(
    f'<div class="stat"><div class="big">{esc(b)}</div>'
    f'<div class="cap">{cap}</div><div class="src">{esc(src)}</div></div>'
    for b, cap, src in STATS)

# INVARIANT 2: the mix chart always carries a caption that explains the bar.
bar_caption = (
    f"How to read the bar: each session falls into one bucket, and a segment's width is "
    f"that bucket's share of all {TOTAL}. The <b>coloured</b> buckets are real product "
    f"activity ({act_n} sessions); the <b>greys</b> are noise — sign-ins, bounces, "
    f"background tabs, and team/test ({noise_n}). That grey majority is why {TOTAL} "
    f"sessions is really {PEOPLE} people.")
assert bar_caption.strip(), "TEMPLATE INVARIANT 2: the mix chart must carry a caption"

# --- findings (in a real run: the refuter-survived patterns) ---------------------
# INVARIANT 3: every finding has a recommendation ('rec') and an owner.
FINDINGS = [
    dict(rank=1, conf='Confirmed', owner='backend', tag='example',
         title='This is where a refuter-survived finding goes',
         body='State what the replays + database + source jointly show. Label every '
              'number with its source. Keep motive INFERRED and say so.',
         rec='State the specific change, and (where useful) how to prevent recurrence '
             '— e.g. a unit test upstream.',
         ev=[('example session', 'https://clarity.microsoft.com/player/PROJECT/SESSION/PAGE')]),
    dict(rank=2, conf='Confirmed · map + code', owner='frontend', tag='false affordance',
         title='A dead-click / UI-clarity finding, source-confirmed',
         body='The dead-click map named the exact element; the frontend source confirmed '
              'it has no click handler (cite file:line). A proven false affordance, not '
              'an inferred one.',
         rec='Make the surface act, or stop it looking interactive. Reproduce via '
             'Heatmaps → Dead clicks → URL contains &lt;your working-surface segment&gt;.',
         ev=[]),
]
assert all(f.get('rec', '').strip() and f.get('owner', '').strip() for f in FINDINGS), \
    "TEMPLATE INVARIANT 3: every finding must carry a recommendation and an owner"

def findcard(f):
    ev = ''
    if f['ev']:
        parts = [f'<a href="{e[1]}">{esc(e[0])} ↗</a>' for e in f['ev']]
        ev = f'<div class="evrow"><b>▶ Watch:</b> {" · ".join(parts)}</div>'
    cls = 'conf' if 'Confirmed' in f['conf'] else 'obs'
    return f'''<div class="finding">
 <div class="fh"><span class="rank">{f['rank']}</span><h3>{esc(f['title'])}</h3></div>
 <div class="chips"><span class="chip {cls}">{esc(f['conf'])}</span>
 <span class="chip tag">{esc(f['tag'])}</span><span class="chip owner">{esc(f['owner'])}</span></div>
 <p>{f['body']}</p>
 <div class="rec"><span class="reclabel">Recommendation</span>{f['rec']}</div>
 {ev}</div>'''

# --- evidence appendix: every watched session, one curated line ------------------
APPX = [
    ('user A', 'https://clarity.microsoft.com/player/PROJECT/SESSION/PAGE',
     'What the replay shows — the moment(s) a verifier should seek to.'),
    ('user B', 'https://clarity.microsoft.com/player/PROJECT/SESSION/PAGE',
     'One line, verifiable against the link. Depth-labelled if not fully watched.'),
]
appxrows = '\n'.join(
    f'<tr><td>{esc(w)}</td><td><a href="{u}">recording ↗</a></td>'
    f'<td class="lbl">{esc(t)}</td></tr>' for w, u, t in APPX)

HTML = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Session Intelligence — example</title><style>
:root{{--ink:#0d0d0d;--muted:#54534f;--faint:#8a8983;--line:#e7e6e0;--bg:#f4f3ef;--blue:#2a78d6;--green:#0f8a4f;--amber:#b8860b;--violet:#6d5bd0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,"Segoe UI",Arial,sans-serif;padding:30px 16px}}
.wrap{{max-width:920px;margin:0 auto}}
.card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:24px 28px;margin-bottom:16px}}
h1{{font-size:27px;letter-spacing:-.02em}} h2{{font-size:17px;margin-bottom:14px}} h3{{font-size:16px}}
.kick{{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}}
.dek{{color:var(--muted);font-size:14.5px;margin-top:7px}}
a{{color:#1c5cab;text-decoration:none}} a:hover{{text-decoration:underline}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:4px}}
.stat{{border:1px solid var(--line);border-radius:10px;padding:13px 15px}}
.stat .big{{font-size:27px;font-weight:700;line-height:1}} .stat .cap{{font-size:11.5px;color:var(--muted);margin-top:5px}}
.stat .src{{font-size:9.5px;color:var(--faint);margin-top:7px;text-transform:uppercase;letter-spacing:.04em}}
.bar{{height:24px;display:flex;border-radius:6px;overflow:hidden;margin:14px 0 8px;border:1px solid var(--line)}}
.bar span{{display:block}}
.leggroup{{display:flex;flex-wrap:wrap;gap:11px;font-size:11.5px;color:var(--muted);margin-top:7px}}
.leggroup .glab{{font-size:9.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);min-width:96px}}
.leggroup i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:middle}}
.finding{{border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}}
.fh{{display:flex;align-items:center;gap:11px}}
.rank{{flex:none;width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:9px 0 9px 37px}}
.chip{{font-size:10.5px;font-weight:600;padding:2px 8px;border-radius:5px;border:1px solid}}
.chip.conf{{color:var(--green);border-color:#a9d8bf;background:#eef8f1}}
.chip.obs{{color:var(--amber);border-color:#e2cf9a;background:#fbf6e9}}
.chip.tag{{color:var(--violet);border-color:#cbc3ee;background:#f3f1fc}}
.chip.owner{{color:var(--muted);border-color:#cfcec6}}
.finding p{{margin-left:37px;font-size:14px;color:#26251f}}
.rec{{margin:11px 0 0 37px;background:#f7f6f2;border:1px solid var(--line);border-radius:9px;padding:11px 14px;font-size:13.5px}}
.reclabel{{display:block;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--green);margin-bottom:4px}}
.evrow{{margin:11px 0 0 37px;font-size:12.5px;color:var(--muted);border-top:1px dashed var(--line);padding-top:9px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;font-size:10px;text-transform:uppercase;color:var(--muted);border-bottom:1.5px solid #cfcec6;padding:5px 8px 5px 0}}
td{{border-bottom:1px solid var(--line);padding:7px 8px 7px 0;vertical-align:top}} .lbl{{color:var(--muted)}}
</style></head><body><div class="wrap">

<div class="card">
<div class="kick">Session Intelligence · example</div>
<h1>What users actually did</h1>
<div class="dek">Every Clarity session over the window, classified; the substantive ones
watched end-to-end; each finding confirmed against the database or the frontend code.
Ordered by impact; each carries a recommended action and an owner.</div>
</div>

<div class="card">
<h2>Who was here <span class="dek">{TOTAL} sessions classified · {PEOPLE} distinct people</span></h2>
<div class="grid">{statcards}</div>
<div class="dek" style="margin:16px 0 0">{bar_caption}</div>
<div class="bar">{barseg}</div>
<div class="leggroup"><span class="glab">Real activity</span>{legend(True)}</div>
<div class="leggroup"><span class="glab">Noise &amp; excluded</span>{legend(False)}</div>
</div>

<div class="card">
<h2>Findings &amp; recommended actions</h2>
{''.join(findcard(f) for f in FINDINGS)}
</div>

<div class="card">
<h2>Sessions reviewed <span class="dek">open any link to verify the analysis</span></h2>
<table><tr><th style="width:18%">User</th><th style="width:14%">Recording</th><th>What it shows</th></tr>
{appxrows}
</table>
</div>

</div></body></html>'''

open(os.path.join(BASE, 'report.html'), 'w').write(HTML)
print("wrote report.html", len(HTML), "chars")
