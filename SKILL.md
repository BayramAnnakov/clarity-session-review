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

It was paid for a second time, harder. A later investigation watched every relevant
replay, censused the database, read the source, and ran an expert panel — **and still
landed on the wrong mechanism**, because nobody had walked the step. **Seven claims
died in that run; five belonged to the analyst.** Every one of them was killed by a
query or a click, never by an argument. Principles 3, 6 and 8 and the refuter are what
they cost.

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
review, and the discovery modules: first-session comprehension, input-struggle /
abandoned-intent, person-arc, success-session shape) live in
[references/method.md](references/method.md).

Pair this with your own product-analytics notes — the instrument map, the
denominator discipline, and the access paths for your database and analytics. Read
your Clarity gotcha list before the first run of the day; new lessons go back into it.

## The eight principles (each one paid for)

1. **Question before player.** The unit of watching is a QUESTION scoped to a
   time-window, never "a recording". No discriminating question → no watching.
   Triage generates the questions; the player answers them. And keep the question
   PORTFOLIO balanced: pathology ("why did X fail") is one family of four —
   comprehension (what did a first-timer understand), workflow shape (how successful
   users actually get value), and journey (what changed between visit 1 and visit N)
   are the others. A portfolio that only asks pathology questions routes the player
   only to wreckage and is structurally blind to everything else replays uniquely
   show (see the discovery modules in `references/method.md`).
2. **Attribute before interpreting.** If you've wired Clarity's [Identify API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/identify-api)
   (`clarity("identify", customId)` — hashed client-side, filterable across
   dashboard/recordings/heatmaps), that is the first-class join: use it. If you
   haven't (most products), session-entry URLs usually carry identity — and wiring
   the Identify API is the proper fix to schedule. If your app's URLs embed account and object IDs
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
   **And a database column is not user behavior until you know what WRITES it.** Grep
   for the writer before you interpret the value: a cron, a migration, a vendor webhook
   or an admin action can set the same field a user's action would. An integration row
   flipping to `isActive = false` read like *a vendor revoking sessions* and nearly
   shipped as "the trust price is a recurring toll" — it was **our own 30-day dormancy
   reaper**. Status enums lie the same way: a row marked `declined` may record the
   *action's* terminal state, not *a human declining*. Field semantics belong in your
   instrument map, next to the denominators.
4. **Label evidence depth honestly: TIMELINE ≠ REPLAY.** Clarity's API click-timelines
   can be truncated (how much varies by endpoint and version — one pull capped near
   ~5 events per page-visit, a later one returned 60+) and their element text is
   partially masked — treat all timeline-derived counts as floors and never present a
   timeline-only read as watched. Findings state their tier: MEASURED (events/DB) / OBSERVED (frames,
   trace — describe, don't interpret) / INFERRED (motive — labeled).
5. **Every claim ships with its evidence coordinates.** Named user, player link, the
   timestamps to seek to, and what a verifier should check — the evidence-appendix
   pattern. Someone will re-watch to verify; make that a two-minute job, not an act
   of faith.
6. **Count people, not sessions — and prove they COULD have tried, and DID.** A rate is
   four claims, not one. Each of the four has killed a published finding on a real run.
   - **(a) The denominator is PEOPLE.** Session counts are NOT user counts. Clarity
     fragments one continuous visit into many single-page "sessions" (multi-tab /
     buffering — one five-minute visit showed up as **59 sessions**); thin bounces are
     often the majority of a pull (50-60% on our runs — measure yours); bots, team/test
     seats and hidden-tab time inflate everything. **Strip bots BEFORE any segment
     carries a rate** — a mostly-bot segment shows a spectacular conversion collapse
     that means nothing (a "mobile sign-in wall" evaporated when 38% of the segment
     turned out to be 2-second scanners). One run's 462 raw sessions was **~26 people**.
   - **(b) Every member COULD have done it — for the WHOLE window.** Did the affordance
     even exist? **A rate whose denominator spans a product change is fiction.** "137
     accepted invitations were never followed up" survived a census, a source read and
     three review passes — then collapsed on one query: the send button did not exist
     for most of that window. **Look up the ship date of the button before you publish
     the rate of its use.**
   - **(c) Somebody actually ATTEMPTED it.** ← the trap that survives (a) and (b), and
     the most expensive lesson in this skill. **An empty cell has two causes — nobody
     tried, or everybody failed — and they are IDENTICAL in every instrument you own.**
     "Nothing has converted through the integration since June 22" was read as a broken
     vendor flow, and a whole strategy was built on it; the flow was fine, **nobody had
     tried since June 22**. Before you explain a zero, **prove attempts**. If you cannot
     prove them, *that is the finding* — and it names the instrumentation you are
     missing: **log the START of every critical step, not only its success.**
   - **(d) The window was chosen BEFORE you saw the data.** The same integration got
     scored "80% broken" from one window; the monthly split read 75% / 80% / 20% / *n=0
     attempts*. A window picked after the fact is a hypothesis wearing a percentage.
7. **Audit what the UI SHOWS, not only what users click.** *(Provisional — weight it
   below the battle-tested principles.)* The method is behavioral and blind to problems
   that produce no event: a misleading label, a status with no next action, a
   stage-name used as a status. The LEAD instrument is a mechanical SOURCE LINT of the
   label-resolving code (no label maps to more than one state/semantic; every state
   where the ball is in the user's court exposes an action) — coverage-independent,
   diffable, and best pushed UPSTREAM as a unit test. A cold-read comprehension probe +
   frames verify what source can't (incomprehension, styling). Gate every finding on
   database prevalence + stated cost, and cite only instruments you've verified exist
   in your Clarity build — don't invent instruments (see the Clarity-facts appendix in
   `references/method.md`). (`references/method.md` → UI-clarity review.)
8. **Walk the step before you explain it.** Before theorizing about ANY step, go
   execute it yourself on the real product, end to end, and screenshot what the user
   actually sees. **Replays tell you WHERE people stop. Only walking tells you WHAT you
   were asking of them** — and this skill, being about watching, will never prompt you
   to do it. A three-day investigation (every relevant replay, database censuses, source
   archaeology, an expert panel) landed on the wrong mechanism for a step whose real ask
   sat **six clicks away on production and had never once been clicked**.
   **And partial execution is worse than none**, because it manufactures confidence: the
   first walk stopped at the scary field — a third-party credential form — and published
   a careful account of "what we ask users to do." The flow had a further step. The real
   ask was not *"lend us your password"* but *"hand over your password AND a live
   two-factor code"* — a different question, with a different answer, and the report had
   already reasoned past it. **If you cannot complete a step yourself** (credentials,
   payment, a real third-party account) — and you often should not — **STOP and hand it
   to a human**; get their screenshots of the *whole* path. Never infer the remainder of
   a flow you did not finish.

## The pipeline

1. **Define the question(s)** and the session population (account IDs, date range,
   URL pattern — e.g. a query param that marks a value-moment surface).
2. **Pull sessions** via the Clarity MCP server / direct API. **Favorite everything
   relevant the same day** — retention is ~30 days rolling; favorites are kept ~9
   months.
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
   duplication, single-user generalization, seasonality, and the **cross-instrument
   units/population gate** (`references/method.md`). Publish the *surviving* form,
   not the first draft — on one at-scale run this re-scoped 4 of 5 patterns. A pattern
   that hasn't survived a refuter is a hypothesis.
   **Publish the MECHANISM, not the RATE, when n is small.** A defect proven in the
   SOURCE is a finding at n=1 ("this card's root has no click handler — it cannot work
   on touch"); a *rate* over a handful of watched users is not ("75% of mobile signups
   went silent" — 3 of 4, p≈0.2, and one mobile user did fine). Replays and source give
   you mechanisms cheaply and rates expensively; lead with what you actually have, and
   state the n beside any rate you can't defend.
   **And send the refuter at the WELD.** When two findings fuse into one story — *"X is
   the currency that buys Y"* — the story becomes more memorable than either finding,
   and **the weld is the part with no evidence.** A genuinely exact correlation
   (p=0.0006, re-verified) was welded to a mechanism it had never tested: it predicted
   who *sent*, and was published as explaining who *connected*. Two different outcome
   variables, silently swapped, and the sentence was beautiful enough to survive a
   council and an adversarial advisor. **Name the weld out loud, check that the
   correlation's outcome variable is the one your mechanism explains, and go hunt one
   counterexample on purpose.** There was one sitting in the same table.
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
thin-session forensics · **opportunities (no fix attached)** — unmet needs surfaced by
the discovery modules (abandoned intents, round-trip demands, comprehension gaps),
each with evidence coordinates + database prevalence but deliberately WITHOUT a
recommended fix, so genuine discovery isn't force-fitted into the defect template ·
watched-evidence appendix (verifiable links) · **struggle reel** — ≤5 clips (player
link + timestamp + one line, 30-60s each) chosen for what they'd make the team FEEL,
watched together; aimed at exposure, not verification · your OEC (the
Overall Evaluation Criterion — the one metric the review is accountable to) + your
funnel-gate numbers (paywall/limit hits, OAuth/connect outcomes) · users to call
(where identifiable). Every DEFECT finding pairs with a recommended action + owner;
every OPPORTUNITY pairs with a validation step (who to call, what to probe) — not a
premature fix. Label
every number with its source (sessions vs database); explain any chart. HTML alongside
Markdown. **Generate the HTML from the data JSONs** with a `build_report.py` (see
[examples/](examples/)) — numbers reproducible, never hand-transcribed; the recurring
report is a re-run, not a rewrite.

**Cold-read gate — test the report the way you test the product (principle 8).** Before
it ships, hand it to a reader with NO context — a colleague, or a subagent given the
artifact and nothing else — and ask four questions: *What do you own? What is decided
versus still open? Is anyone asking you anything? Where did you stop reading?* **A
report whose findings are all correct and whose readers all answer "nothing is being
asked of me" has failed.** That is not hypothetical: four cold readers returned four
independent *"it asks me nothing"* on a report whose author believed he was requesting
their input, and the most senior of them read it and stood down. Structure that survives
the test: **the answer on page 1** (not page 10) · **DECIDED vs OPEN with a NAME on
every line** · **one dated changelog of every claim that died** (not strikethroughs
scattered through the body — a reader who never saw v1 does not need to watch you argue
with yourself) · a loud **SUPERSEDED** stamp on any plan the evidence has since demoted
· and **the author's own errors named first**, with the author's name on them. A
retraction the reader has to reconstruct is a trap, not a disclosure.

## Reading the replay — semantics that will fool you (verified list)

- **`Page hidden`/`Page visible` is the real attention signal.** Foreground attention
  in first sessions measured at 30-90 seconds on our runs; everything else is a
  backgrounded tab. Long "engaged" sessions dissolve into 2-8-second glances. Read these events
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
- **First-session watch (EXPERIMENT):** every genuinely-new external human's first
  engaged session gets one full 1× watch — exempt from the triage gate and the watch
  caps; required output: *the moment comprehension broke*. Promote or kill on its
  2-period hit rate (see the module in `references/method.md`).
- **Success-session sample:** each period, DB-select ~5 sessions where the value
  moment was REACHED and watch how the work was actually done — the behavioral
  pipeline never flags these, because nothing failed.
- **Weekly calibration:** one UNSCOPED 1× full-watch per active cohort — the
  unknown-unknowns detector; log what it catches that the pipeline missed (the method's
  own error rate). **Hold this budget constant** as the triage codebook compounds — a
  flag rate that only shrinks is efficiency for defect census and a death spiral for
  discovery; reinvest the savings into the discovery modules, not into watching less.

## Known blind spots — GATES, not footnotes

*(These were already written down. They were read, and overridden, and the findings
shipped anyway. A blind spot you list but do not gate on is decoration — so when a claim
sits on top of one of these, **the blind spot goes in the sentence, or the claim does not
go in the report.**)*

- **The interior of any third-party step is unobservable, and this is the gate that
  matters most.** Your recorder's script is not on the vendor's domain and never can be.
  You see entry, return, and the webhook row — never the screen, never the hesitation,
  never the refusal. **Any claim about *why* people abandon inside a hosted flow is
  inference, full stop.** An investigation that had never observed one human refuse at a
  credential screen nevertheless published refusal as its central mechanism — and had
  earlier *killed* the same hypothesis ("0 complaints in 416 messages") with the same
  blind instrument. **The same deafness, twice, in opposite directions, both times
  called a finding.** Say what you cannot see, in the sentence, next to the claim.
- **An unattempted step and a failing step are indistinguishable** in every instrument
  you own (principle 6c). Instrument the START of each critical step, not only its
  success — otherwise a zero is permanently unreadable.
- **Absence of complaint is not absence of anything.** Nobody writes to a chatbot to say
  *"I don't trust you with my password."* They close the tab. A chat/ticket census can
  confirm a fear exists; it can **never** disconfirm one.
- A share of active users block Clarity and analytics entirely (ad-blockers) — the
  product database is the only instrument for them, and all client-side counts are
  **floors**; recordings predate nothing before the Clarity snippet shipped; clipboard
  and other-tab activity are invisible; **motive is never on tape** — pair with chat
  mining, feedback-email threads, and calls.
