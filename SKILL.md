---
name: clarity-session-review
description: >
  Review Microsoft Clarity session recordings the way that produces findings, not
  anecdotes: question-scoped triage → attribution → replay-watch → database/source
  triangulation → a verifiable evidence appendix. Use for funnel investigations
  ("why did users drop off / churn / not click X"), post-ship verification ("watch
  the next 10 users through the new surface"), pre-call prep ("what did user X
  actually do"), the monthly dead-click/UX-debt review, and the recurring
  session-intelligence report over ALL sessions in a window. Triggers: "watch
  recordings", "session replays", "check Clarity", "what did <user> do",
  "verify the fix", "dead clicks", "review all sessions", "session intelligence",
  "session-recording report", "what are users doing".
---

# Clarity session review

A discipline for turning Microsoft Clarity session recordings into findings you can
act on and a colleague can verify — instead of a folder of anecdotes and a
timeline you half-trust.

It was born the day replay-watching **overturned four timeline-based conclusions** in
a single investigation: a user we'd filed as "bailed at the redirect" had actually
spent two minutes inside the hosted OAuth flow; a "five-day starer" was a hidden
background tab; a "never-returned" user had returned; and a dramatic "48-minute
struggle session" turned out to be an internal teammate's own browser. Every one of
those was a confident, wrong story read off the event timeline. The skill exists so
that never happens silently again.

> This is a public snapshot of a living internal skill. The principles are
> battle-tested; the examples are anonymized. To wire it to your own product, see
> [ADAPTING.md](ADAPTING.md).

**Two modes.** (A) *Targeted investigation* — a specific question (why did user X
churn, verify a fix, pre-call prep): run the pipeline below directly. (B) *Periodic
census* — the recurring session-intelligence report over EVERY session in a window:
same principles, but orchestrated as a resumable multi-agent workflow — see
[references/periodic-review.md](references/periodic-review.md). The principles are
mode-agnostic; the mechanics differ at scale. Per-session mechanics and the standing
modules (instruments toolkit, dead-click analysis, thin-session forensics, UI-clarity
review) live in [references/method.md](references/method.md).

Pair this with your own product-analytics notes — the instrument map, the
denominator discipline, and the access paths for your database and analytics. Read
your Clarity gotcha list before the first run of the day; new lessons go back into it.

## The seven principles (each one paid for)

1. **Question before player.** The unit of watching is a QUESTION scoped to a
   time-window, never "a recording". No discriminating question → no watching.
   Triage generates the questions; the player answers them.
2. **Attribute before interpreting.** Clarity has no `identify()` — but session-entry
   URLs usually carry identity. If your app's URLs embed account and object IDs
   (e.g. `app.example.com/{accountId}/{objectType}/{objectId}`), the account ID joins
   to your user/account table and the object ID pins the exact record the user was
   looking at — disambiguating multi-user accounts. URL-matching also catches TEAM
   members browsing customer accounts, and one human may hold several accounts. Check
   the browser-uid across unrelated accounts, verify a sign-in flow for any "new user"
   claim, dedup cross-account humans. **uid-level exclusion**: a browser-uid that EVER
   touches an excluded (team/test) account is excluded EVERYWHERE, not just in that
   account. A misattributed session becomes a confidently wrong finding.
3. **A replay alone is a story; replay + database + source code is a finding.**
   Every load-bearing observation gets triangulated: what the screen showed (replay),
   what actually happened (the database — e.g. the connect/integration rows vs a
   watched OAuth attempt; the subscription-status field vs a "plan has ended" banner),
   and why the UI did that (frontend/backend source — e.g. the banner's render
   condition). When a UI state surprises you, grep the source for its copy string
   before theorizing.
4. **Label evidence depth honestly: TIMELINE ≠ REPLAY.** Clarity's API click-timelines
   are truncated (~5 events per page-visit) and their element text is partially masked
   — treat all timeline-derived counts as floors and never present a timeline-only read
   as watched. Findings state their tier: MEASURED (events/DB) / OBSERVED (frames,
   trace — describe, don't interpret) / INFERRED (motive — labeled).
5. **Every claim ships with its evidence coordinates.** Named user, player link, the
   timestamps to seek to, and what a verifier should check — the evidence-appendix
   pattern. Someone will re-watch to verify; make that a two-minute job, not an act
   of faith.
6. **Count people, not sessions.** Session counts are NOT user counts. Clarity
   fragments one continuous visit into many single-page "sessions" (multi-tab /
   buffering — one user's single five-minute visit showed up as **59 sessions**), and
   50-60% of any pull is thin bounces, on top of team/test and hidden-tab inflation.
   Before any rate, compute the REAL engaged denominator — distinct external humans who
   reached the product — and lead with it: one run's 462 raw sessions was **~26
   people**. A rate over raw session counts is almost always wrong; strip the noise
   first.
7. **Audit what the UI SHOWS, not only what users click.** *(Provisional — weight it
   below the battle-tested principles.)* The method is behavioral and blind to problems
   that produce no event: a misleading label, a status with no next action, a
   stage-name used as a status. The LEAD instrument is a mechanical SOURCE LINT of the
   label-resolving code (no label maps to more than one state/semantic; every state
   where the ball is in the user's court exposes an action) — coverage-independent,
   diffable, and best pushed UPSTREAM as a unit test. A cold-read comprehension probe +
   frames verify what source can't (incomprehension, styling). Gate every finding on
   database prevalence + stated cost. (`references/method.md` → UI-clarity review.)

## The pipeline

1. **Define the question(s)** and the session population (account IDs, date range,
   URL pattern — e.g. a query param that marks a value-moment surface).
2. **Pull sessions** via the Clarity MCP server / direct API. **Favorite everything
   relevant the same day** — retention is ~30 days rolling; favorites persist.
3. **Triage from timelines** (seconds per 100 sessions): classify every session,
   subtract hidden-tab time (both duration fields include it), attribute (principle 2).
   Most sessions close here. Output per survivor: hypothesis + the exact window(s)
   where the answer must live.
4. **Replay-watch the survivors** — staged method in
   [references/method.md](references/method.md): full events-panel harvest (one
   JavaScript pass, not scroll-screenshots), targeted frames at decisive moments,
   pointer-trace poller only for dynamics questions (with its validation gate). The
   browser is serially-shared — one session at a time; parallelize triage and
   analysis, never player-driving. At scale this is a serial watch loop inside a
   resumable workflow — see [references/periodic-review.md](references/periodic-review.md).
5. **Triangulate** every finding-grade observation against the database and, for
   surprising UI states, the source (principle 3). Sessions split by hour+ gaps can be
   one story — follow referrer chains (a session starting with a referrer from your
   auth provider's domain is a bounce-back from the OAuth flow). Also scan the
   ENRICHMENT data itself: suspicious uniformity is a finding (a few thousand accounts
   sharing one subscription-expiry date = a migration artifact — found in the account
   data, not on any recording).
5b. **Refute before you publish a pattern.** Every candidate pattern gets one
   adversarial pass (default-to-refuted, DB access) that tries to kill it via the usual
   suspects: hidden-tab inflation, fragmentation, team/test contamination, cross-account
   duplication, single-user generalization, seasonality. Publish the *surviving* form,
   not the first draft — on one at-scale run this re-scoped 4 of 5 patterns. A pattern
   that hasn't survived a refuter is a hypothesis.
6. **Dead-click analysis is a MANDATORY separate report section** (see the module in
   `references/method.md`): rank dead-click targets, classify each + fix direction, and
   triangulate the top ones against **frontend source** (grep the component to confirm
   the element has no `onClick`/link → a *proven* false affordance, cite file:line) AND
   the database. This is the cheapest UI/UX-debt instrument there is; it runs every
   review and catches issues the funnel numbers hide.
7. **Write the evidence appendix** (per-session: who, link, moments, claim, what to
   check, depth label) and fold conclusions into the investigation doc. Contradictions
   UPDATE the upstream census — never let stats silently rot. **Route the lessons:**
   METHOD lessons (how to watch/attribute/triangulate) → this skill + your analytics
   notes; PRODUCT findings (what users do, which surface leaks) → the report + your
   product docs. Folding product findings into a method skill is the fastest way to
   rot it.

## Standard report sections (every run)

**Lead with the real denominator** (distinct people, not raw sessions — principle 6),
then: census (mix + deltas vs last period) · funnel-stage classification · **pattern
table (new vs recurring, each strength-tagged, each refuter-survived)** · **dead-click
+ UI-clarity review (misleading labels / status-without-action, source-confirmed)** ·
thin-session forensics · watched-evidence appendix (verifiable links) · OEC + gate/OAuth
numbers · users to call. Every finding pairs with a recommended action + owner. Label
every number with its source (sessions vs database); explain any chart. HTML alongside
Markdown. **Generate the HTML from the data JSONs** with a `build_report.py` (see
[examples/](examples/)) — numbers reproducible, never hand-transcribed; the recurring
report is a re-run, not a rewrite.

## Reading the replay — semantics that will fool you (verified list)

- **`Page hidden`/`Page visible` is the real attention signal.** Foreground attention
  in first sessions often measures at 30-90 seconds; everything else is a backgrounded
  tab. Long "engaged" sessions dissolve into 2-8-second glances. Read these events
  before calling any session "staring", "struggling", or "engaged".
- **"User left site — N min" = a same-tab redirect** (e.g. into hosted OAuth). A
  **popup** window creates NO hidden/left-site event — clicks just continue in the main
  tab. The same button can behave both ways; don't assume.
- **Grey regions = unrecordable content** (cross-origin iframes/overlays, e.g. a
  hosted-auth widget), not emptiness.
- **Checkbox clicks log as `Click: "on"`** (the input value); five evenly-spaced "on"
  clicks down a column = row selection, not a mystery button.
- **Masked text `▪▪▪` preserves character counts** — "Start ▪×8 ▫ ▪×8" decodes to
  "Start outreach campaign". Count the blocks.
- **Clarity's "Dead click" label is unreliable for disabled controls** (any DOM
  reaction suppresses it) — but a Click row with no consequent UI change, repeated, is
  a user hammering a dead affordance. Selection events + dead clicks on message text =
  a copy attempt (the clipboard itself is invisible — copy is always INFERRED).
- **Auto-translated UIs** (via the browser's translate feature) show translated text in
  click events and are notorious for breaking framework interactivity — flag
  `Translate` artifacts before blaming the user.
- **Clarity fragmentation — one visit, many "sessions".** Clarity splits a single
  continuous visit into multiple single-page-view records (multi-tab, buffer flushes):
  one user's single five-minute workflow appeared as 59 "sessions" all stamped inside a
  five-minute window. Tell-tale: a burst of same-uid rows with the same minute, one page
  each. Collapse by uid+time before counting anything (see principle 6).
- **Timestamps**: the player clock is session-relative; API `start` fields can be
  wall-clock; align against database timestamps (UTC) before any cross-instrument claim.

## Regular cadences (why this skill exists)

- **Post-ship (the next-10 rule):** after ANY funnel-surface change, replay-watch the
  next ~10 users through it. At low/mid traffic, one watched session outweighs a month
  of event deltas — rate metrics can only detect step-changes.
- **Pre-call prep:** before a user call, watch that user's sessions end-to-end and
  bring the moments ("at 05:08 you hit the limit message — what were you trying to
  do?"). Check your feedback inbox too — the motive may already be voiced.
- **Monthly UX-debt:** pull dead-click floors by surface (API) + the dashboard's
  session-level dead-click % + rage-click filter; any new surface gets a dead-click
  check two weeks after shipping.
- **Weekly calibration:** one UNSCOPED 1× full-watch per active cohort — the
  unknown-unknowns detector; log what it catches that the pipeline missed (the method's
  own error rate).

## Known blind spots (say them with the findings)

A share of active users block Clarity and analytics entirely (ad-blockers) — the
product database is the only instrument for them; recordings predate nothing before the
Clarity snippet shipped; the OAuth interior is invisible (only entry, return, and the
integration's webhook row in your DB); clipboard and other-tab activity are invisible;
motive is never on tape — pair with chat mining, feedback-email threads, and calls.
