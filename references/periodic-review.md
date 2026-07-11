# Periodic review — reviewing ALL sessions in a window (the recurring mode)

*Mode B of the skill (Mode A = targeted investigation). Goal: a recurring
"session-intelligence report" — the Voice-of-Customer analogue for product behavior —
over EVERY session in a time window. Born from a real run over 462 sessions; its
report generator is the reference implementation (see `../examples/`) — the workflow
script itself remains internal. Same seven principles as Mode A; the difference is
orchestration at scale.*

## Scope decision (state it up front)
"Review ALL recordings" = **census 100% · replay-watch ~5-8% (the flagged set) ·
triangulate 100% of findings.** Watching every session is ~30-40h of serial browser
time spent mostly on hidden tabs and 10-second bounces. The census is the pattern
instrument; replays are the microscope for what the census can't explain. Expect
~25-40 flagged sessions on the first run; the pattern library shrinks that each period.

## The shape — four phases; the middle two are ONE resumable Workflow

```
0. SCOUT      inline Python, no agents      pull → enrich → batch          ~15 min
1. TRIAGE     parallel agents (Workflow)    classify all from timelines    ~10 min
2. WATCH      SERIAL agents (Workflow)      replay-watch the flagged set   the bottleneck
3. SYNTH+REFUTE parallel agents (Workflow)  patterns → refute → report     ~15 min
```

Run phases 1-3 as a **Workflow** so the run is resumable (survives session limits).

## Phase 0 — scout (inline, deterministic, no agents)
- **Pull** via the direct API / Clarity MCP. **The `count` cap is 250, and 250 recent
  sessions ≈ a few days of traffic for a mid-volume product** — so a 2-week window needs
  several **day-slices** with explicit `start`/`end` (ISO-8601 UTC) and dedup on session
  link. The API 503s under load — back off ~90s and retry; don't hammer. Save the raw
  pull JSON: it preserves player links even after the recording expires from retention.
- **Enrich**: join every workspace/account UUID to your product database → emails,
  subscription status, usage. Apply your canonical exclusion list.
- **uid-level exclusion**: any browser-uid that EVER touches an excluded workspace is
  excluded EVERYWHERE (principle 2). Compute the excluded-uid set once, propagate.
- **Compact** the timelines (strip full URLs to relative paths — full URLs get
  output-blocked by the harness's cookie/query filter) and cut into ~25-session batch
  files for the fan-out.

## Phase 1 — triage fan-out (parallel agents)
One classifier per ~25-session batch, **schema-forced** output (class, flag, excluded,
ws, emails, question, window, priority). Give every classifier the skill's triage
rubric + a **known-actors list** (named users, competitors, prior-cohort members,
already-watched keys) so classes stay consistent across batches and nothing is
re-watched. Merge inline: dedup, count, build the watch-list = flagged ∧ not-excluded,
priority-sorted, **capped ~2 per workspace** so one heavy user can't eat the watch budget.

## Phase 2 — watch (SERIAL — the hard constraint)
The browser is a single shared resource and background tabs throttle → watchers run
**one at a time in a loop**, never parallel (`for … { await agent(…) }`). Two tricks:
- **Fresh context per watcher** (a new agent per session, not one long agent):
  screenshots are token-heavy; a fresh context caps every watcher at one session's
  images.
- **Each watcher writes its observation file to disk** (`observations/<key>.md`) and
  returns a structured summary → the synthesis reads files, not one giant context.
Each watcher runs the Mode-A method (`method.md`): events-panel harvest → hidden-tab
read → targeted stills → favorite. Favorite the FLAGGED set only (not all 462).

## Phase 3 — synthesize + refute (parallel) → report
- **Synthesis** agent reads all classifications + all observation files + the
  thin-forensics JSON → candidate patterns, each tagged new/recurring/contradicts +
  strength = weakest evidence tier.
- **Adversarial refuter per top pattern** (parallel, DB access), default-to-refuted:
  kill it via hidden-tab inflation, fragmentation, team/test, cross-account,
  single-user generalization, seasonality. Publish the *surviving* form. On one real
  run this re-scoped 4 of 5 candidate patterns (e.g. a suspected activation-killer
  turned out to be a migration artifact). **Not optional.**
- **Report** (inline): generate the HTML from the data JSONs with the report generator
  — reproducible, never hand-transcribed. Standard sections + real-denominator lead
  (SKILL.md). Render → eyeball → deliver.

## Cheaper census: the dashboard tool (do this BEFORE Python forensics)
The Clarity MCP `query-analytics-dashboard` tool returns **untruncated aggregates** —
dead-click %, rage-click %, top pages, referrers, geo, device, JS errors — that no
recordings loop can match cheaply. Use it for the census + the dead-click-% UX-debt
KPI; reserve recordings for the flagged deep-dives. (The first run hand-rolled a
poor-man's Python version before this tool was wired — don't repeat that.)

## Surviving session limits (why it's a Workflow)
Every completed agent is journaled. On a session-limit stall (which is SILENT — no
completion notification), resume with `Workflow({scriptPath, resumeFromRunId})`:
completed watchers replay from cache instantly — the browser is NOT re-driven (verify
via `observations/*.md` mtimes: anything older than the resume time was replayed, not
re-watched) — and only the limit-failed agents run live. Schedule a wakeup just past
the reset (your agent runtime's rate-limit reset window) as a fallback trigger. The one
real run hit the limit mid-watch (10 of that phase's 16 watchers done; 21 sessions
watched across the whole run) and resumed losslessly.

## Cost & cadence
First run ≈ 2-4h wall (watching dominates), ~1.5-3M tokens. **Biweekly** fits the
~30-day retention with margin (favorite-on-flag protects the tail). Semi-attended, not
cron — the watch phase drives a real Chrome tab. Each run's confirmed patterns join
the next run's triage rubric, so the flag rate — and the expensive watch phase —
shrinks every period (the codebook compounds, like a VoC coding scheme).

## Denominator reminder
Lead the report with people, not sessions (principle 6). The first run's 462 sessions
was ~26 distinct external people after stripping team/test (16%), thin bounces (58%),
hidden-tab inflation, and fragmentation (one user = 59 "sessions"). Every rate reads
against that number.
