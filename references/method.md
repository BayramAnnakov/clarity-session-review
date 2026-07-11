# How to watch a session recording (staged method, v4)

*Canonical home of the method (v4 adds the round-2 lessons: JS events-panel harvest,
player mechanics, DB/source triangulation).
The unit of watching is never "a recording" — it is a QUESTION scoped to a TIME-WINDOW.
A session's information lives in three layers with different access costs; escalate
only when the cheaper layer can't answer.*

| Layer | What it holds | Where it lives | Access cost |
|---|---|---|---|
| 1 — Events | pages, clicks + element text, dead/rage clicks, text-entry, **Page hidden/visible**, durations | API/MCP timeline — **TRUNCATED to ~5 events per page-visit**: aggregates are floors; the FULL log lives only in the player | seconds per 100 sessions |
| 2 — UI states | what the user SAW at moment X (modal copy, agent message, errors, banner) | player frame at a timestamp; full events panel | ~2 actions per still |
| 3 — Dynamics | cursor trajectory, hover-linger, hesitation-retreat, scroll rhythm | the replay stream — extractable as DATA via the pointer-trace poller | ~1-2 min per window |

## Stage 0 — the question, or don't watch
Write the discriminating question BEFORE opening the player. No question → no watching.

## Stage 1 — structured triage (API/MCP, all sessions)
Pull timelines; classify every session; most close here. **Cheap aggregate layer
first:** the Clarity MCP `query-analytics-dashboard` tool returns untruncated
aggregates (dead-click %, rage %, top pages, referrers, geo, JS errors) — get the
census shape from it before touching recordings. Hygiene:
- **Attribute first**: browser-uid across unrelated workspaces = team session →
  exclude (uid-level: exclude that uid everywhere). Verify a sign-in flow for "new
  user" claims. Dedup cross-account humans. **Collapse Clarity fragmentation** — a
  burst of same-uid single-page rows in one minute is ONE visit, not N sessions.
- **Duration discipline**: subtract hidden-tab time (totalDuration AND activeDuration
  include it).
- **Truncation**: API timelines carry ~5 events/page-visit — event counts are floors.
- **Favorite everything relevant today** (30-day rolling retention; favorites persist).
- Output per surviving session: hypothesis + exact window(s) where the answer lives.

## Stage 1.5 — the player's own AI (free hypotheses)
Per-session Insights tab + list-level Copilot summary. Hypotheses, never evidence.

## Stage 2 — full events + targeted stills (layer-2 questions)
Open the player once per flagged session:

**(a) Harvest the complete events panel in ONE JavaScript pass** — do not
scroll-screenshot it. In the player tab (`javascript_tool`), collect the event rows
by innerText pattern:

```js
let results = [];
document.querySelectorAll('div, li').forEach(el => {
  const t = (el.innerText || '').trim();
  if (/^(Click|Page hidden|Page visible|Dead click|Selected text|Resized page|Rage click|Text input|Quick back click|Smart event|Entered text)[\s\S]{0,120}\d{2}:\d{2}$/.test(t)
      && el.children.length <= 6 && !t.includes('\n\n')) {
    results.push(t.replace(/\n+/g, ' ')
                  .replace(/https?:\S+/g, '<url>')   // strip URLs or output gets blocked
                  .replace(/[?&]\S+/g, ''));
  }
});
[...new Set(results)].filter(r => (r.match(/\d{2}:\d{2}/g)||[]).length === 1);
```

Slice the array if it exceeds output limits. This recovers everything the API
truncated (Smart events, Entered text, Quick back clicks included).

**(b) Targeted stills**: seek to each decisive window and screenshot the frame.
Player mechanics (all verified the hard way):
- Wait ~8-9s after navigation for the player to load; autoplay state is ambiguous —
  your first play/pause click may pause it. Screenshot to confirm the clock.
- **Seek by clicking the timeline bar, then VERIFY the on-screen clock and nudge** —
  pixel math is unreliable (markers, margins). The ±10s buttons are flaky; prefer
  timeline clicks.
- The "Recording ended" dialog blocks everything — close via its X.
- Playing through a window: press play, `wait` N seconds, screenshot — repeat. For a
  10-60s decisive window this beats frame-hunting.

## Stage 3 — pointer-trace poller (layer-3 dynamics, window-scoped)
The replay iframe is same-origin; the virtual cursor is a DOM node
(`.clarity-pointer-move`), clicks are `.clarity-click`/`.clarity-click-ring` nodes.
- Skip-inactivity OFF for dynamics (a user motionless READING is the signal);
  1× for measurement.
- Poll ~150ms: cursor left/top + `elementsFromPoint` → first element not
  `clarity-*` and not CANVAS → record `{playerClock, x, y, element}` deduped.
- **Timestamp against the on-screen PLAYER CLOCK** (immune to speed/skip).
- Harvest as dwell segments (linger / trajectory / approach-then-retreat).
- **Validation gate before any trace claim beats INFERRED**: (a) known API clicks
  appear at the right time on the right element; (b) 1× vs 2× agree; (c) skip on/off
  reconcile; (d) probe input density (tween-interpolation means sub-second structure
  is synthetic). Publish effective resolution; refuse claims below it.
- Filmstrip fallback: `screencapture -v`/ffmpeg at 1× (NOT gif_creator — it captures
  ~nothing during passive playback); record once, re-extract frames at higher fps.

## Stage 3.5 — full-watch calibration
Watch UNSCOPED at 1× when: weekly calibration (~1/cohort), session <3-4 min active,
stages contradict, or the session feeds a load-bearing decision. Log what full
watching catches that the pipeline missed.

## Stage 4 — triangulate before it becomes a finding
- **Your product database** is ground truth for outcomes — the tables that record the
  real OUTCOME: a watched OAuth attempt vs the connect-action rows (created only on the
  provider's success webhook); a banner on screen vs the subscription-state / quota
  columns; "never used again" vs the conversation-message census; identity vs the user
  names/emails.
- **Source code** explains surprising UI states: grep the frontend/backend for the
  copy string (e.g. a banner's render condition, an email's eligibility logic) —
  replay + DB + source together turned "weird banner" into a source-confirmed copy
  bug with a measured 0/5 conversion baseline.
- **URL identifiers are join keys**: your product's session-entry URLs (e.g.
  `app.example.com/{accountId}/{objectType}/{objectId}`) — the object UUID resolves the
  exact record in your database (what was asked, what the agent replied) and separates
  users sharing an account.
- **Referrer chains stitch sessions into stories**: a session starting with
  `referrer=<your OAuth provider's hosted-auth domain>` is a bounce-back from hosted
  auth; hour-apart sessions can be one user-day.
- **Enrichment-column anomalies are findings** — scan the joined account-info for
  suspicious uniformity, not just per-session behavior: a few thousand accounts sharing
  one subscription-expiry date (a migration artifact stamping legacy free accounts with
  one expiry) surfaced from the enrichment data, on no recording at all.
- Cross-instrument timestamps: align player-relative, API wall-clock, and DB UTC
  before claiming sequence.

## Stage 5 — human watch
Only for intent/emotion judgment calls that survive Stage 4. Hand over: player link +
the question + the timestamp window — never "watch this recording".

## Output contract (every watched session)
MEASURED (events/DB) / OBSERVED (frames or trace — describe, don't interpret) /
INFERRED (motive, labeled) + the Stage-0 answer. Every OBSERVED line carries
provenance: `[stage | instrument | speed | skip on/off | resolution | window covered]`.
Negative evidence states coverage + resolution. Per session, one appendix row:
**who (workspace + user) · player link · the moments to seek to · the claim · what a
verifier should check · depth label (REPLAY/TIMELINE)** — the
`reviewed-recordings.md` pattern. Contradictions update the upstream census.

---

# Clarity instruments — use the whole toolkit, not just recordings (standing module)

We default to session recordings + per-session events and leave ~80% of Clarity
unused. Pull these via the `query-analytics-dashboard` MCP tool (natural-language,
give an explicit date range) or the dashboard — most need NO watching and form the
census + issue-discovery layer. What each finds (30-day window, verified):

- **Aggregate frustration metrics — get these FIRST as the census layer.** One query
  returns dead clicks / rage clicks / quick backs / excessive scrolling totals
  (e.g. 523 / 10 / 153 / 0). Untruncated and cross-session — unlike per-session
  floors. **Exclusions apply** — team/test/internal accounts appear in the totals;
  strip them.
- **Dead-click ranking = the aggregate metric, NOT per-session floors.** "Top pages by
  dead click count" is the correct ranking layer for the dead-click module (the run
  used per-session floors of 164; the aggregate was 523). Then per-target verify
  (copy-select / reading-tap / false-affordance) — the count stays an upper bound, and
  it's dominated by copy-out users (one heavy user's 77 were mostly text-selection).
- **Quick backs (NEW — was unused).** A click out to an external site, user bounces
  straight back. **High on a working page = users round-tripping to an external site
  (e.g. LinkedIn) to vet records → they want in-app detail** (e.g. ~52 of 153 on one
  active user's working pages). **High on `/sign-in` = auth-flow friction / OAuth
  bounce** (e.g. 23).
- **JavaScript errors + click errors — check EVERY run.** A silent-breakage guard the
  behavioral method cannot see; state the result even when clean (e.g. 0 — a clean
  bill). "Click errors" (JS error right after a click) auto-tags the session — filter to it.
- **Heatmaps (validated — visual, dashboard only, NOT the NL API).** Open
  Heatmaps → pick map type (Click has a sub-menu: All / Dead / Rage / Error / First /
  Last clicks · plus Scroll · Attention · Area). **The URL-match trick is essential:**
  your product's URLs are per-account/per-object, so `is exactly` pools only a handful
  of visits. Switch the matcher to **`contains`** and enter the path segment of your
  main working surface (e.g. a chat route like `/c/`) to aggregate the whole working
  surface. What the maps deliver:
  - **Dead-click / all-click MAP → the exact ELEMENT.** E.g. (`contains /c/`, 30 dead
    clicks): assistant text referencing the record list = **40%**, stat-counter chips =
    **13%**, data-table row div = **10%**. This UPGRADES a false-affordance finding from
    behavioral-inference to element-confirmed — the map is the confirmation layer the
    dead-click module's rank step points to.
  - **Scroll MAP → the fold question, and it can return a decisive NEGATIVE.** E.g.
    100% of visitors "reached" every depth 5–70%, 0% drop-off → the working surface is a
    **fixed app-shell that doesn't page-scroll**; the connect CTA is **not** below the
    fold, so the funnel drop is behavioural, not placement. A ruled-out hypothesis is a
    real finding — it redirects the fix.
  - **Attention MAP** shows time-per-region; degenerate when the page doesn't scroll.
  Two standing caveats: **(1) representative-snapshot** — Clarity overlays aggregated
  data on ONE captured DOM (often a team/internal session); layout/fold/element questions
  are valid across users, but the pooled DATA includes excluded workspaces (note it).
  **(2)** device-type param defaults to desktop; the date picker sometimes won't widen
  from the heatmap view — a 3-day aggregate is usually enough for element ranking and
  aligns with the 30-day census direction.
  - **BLIND SPOT — nested scroll.** Clarity's scroll & attention maps measure DOCUMENT
    scroll. If the app scrolls inside a nested container (e.g. a data table with its own
    scroll), the maps are blind to in-container depth → "did users reach row #30 / scroll
    their whole list" is UNANSWERABLE via heatmap (needs replays or product instrumentation).
    Don't read "100% reached every depth" as "users saw everything."
- **Funnels (code-free):** build your key conversion funnel (e.g. the connect/activation
  funnel) in Clarity to visualize the drop without reconstructing it from your product DB.
- **Inactive pages** insight — surfaces surfaces nobody interacts with. **Smart events /
  User-intent** — auto-detected key actions + engagement tiers. **Filters** — cohort by
  "has JS error", "has rage click", device, country, referrer, UTM.

Coverage honesty: name which instruments you ran. "We reviewed sessions" ≠ "we used
Clarity" — recordings are one of ~10 families.

# Thin-session forensics (standing module — no watching required)

Thin sessions (<30s, ≤1 click; typically 50-60% of all sessions) are a separate
instrument, not noise. Aggregate them (Python over the pull JSON) by **entry-URL
class × referrer domain × browser-uid × duration**, with uid-level exclusion (any
uid that EVER touches an excluded workspace is excluded everywhere). What they carry:

- **OAuth bounce-backs**: referrer `<your OAuth provider's hosted-auth domain>` →
  returns from the hosted connect flow (the detector re-found all three of one user's
  touches).
- **Parked-tab heartbeats**: thin sessions entering directly on a working-surface URL =
  the tab is still open — a live, free re-engagement surface; series per uid measure it.
- **Auth loops**: a uid with ≥3 sign-in-entry sessions and no workspace ever =
  someone repeatedly failing/abandoning sign-in (watch ONE of them).
- **Acquisition census (poor-man's)**: entry×referrer distribution — e.g. thin
  sessions referred from your marketing site = the marketing→app handoff leak, measured.
- **Email-click forensics**: `utm_` in entry URLs separates human email clicks from
  scanner hits (and near-zero utm sessions corroborate "email retrieves no one").
- **Competitor recon**: repeat thin sessions from known competitor accounts.

Output: `data/thin_forensics.json` (aggregates + repeat-uid table + bounce list) —
feeds the synthesis alongside classifications and watch observations.

# UI-clarity review — audit what the UI SHOWS, not only what users click (standing module)

*Maturity: the SOURCE-LINT below is mechanical and proven (4 issues from one file).
The cold-read + frame parts are a MATURING instrument — one catch so far, by a human not
the method; detectors still validating. Don't present frame-flagged items at the same
confidence as source-linted ones.*

The behavioral pipeline (clicks, dead clicks, selections) is STRUCTURALLY BLIND to
problems that produce NO event: a misleading label, a status with no next action, a
stage-name used as a status. The user misreads it or gives up, and never clicks.
(Real instance: a status column showed a red label whose text implied a pending
user-goal but actually meant "no reply in 7 days" — one label for three opposite
states; the pipeline had watched that account but was scoped to clicks.)
Run these in order — most mechanical first.

## 1 — Source lint (LEAD here — mechanical, coverage-independent, diffable)
Where status labels resolve centrally (e.g. a single status-resolver module in your
frontend source), lint the state table for invariants:
- (a) **No label maps to >1 state/semantic.** One `statusLabel` reused across success /
  danger / disabled ⇒ the meaning lives only in colour + tooltip. (The real instance:
  one label mapped to success at one resolver line, danger at another, disabled at a
  third — while a clear unambiguous label for that state already existed elsewhere in the
  same resolver.)
- (b) **Every user-ball state exposes a next action.** A state the user can act on
  (Connected → send; No reply → follow up; Replied → reply) but the UI gives no control.
- (c) **Meaning survives colour + tooltip stripped.** If removing colour and hover
  leaves the label ambiguous, it fails.
Output: file:line + the failing invariant. Coverage-INDEPENDENT — audits states that
never rendered in any watched session (Failed/Canceled variants often don't); it will
even catch a misspelled status enum for free.
**The real fix is upstream, not here:** these invariants belong as a UNIT TEST in
your frontend codebase (assert no resolver step-variant shares a label with a different
semantic; assert every user-ball state exposes an action) — catches the class at commit
time, forever, reviewer-independent. The skill CONSUMES that lint's output; it doesn't
substitute for it. Recommend the test; owner = the owning frontend engineer.
**Limits (state them):** detects incoherence, not incomprehension — a label used for ONE
state can still read as a CTA and mislead (passes the lint, fails the user); blind to
styling/juxtaposition (a "Connection sent" pill styled like the live button beside it
is a CSS fact no label-lint sees); misses scattered inline JSX, i18n catalogs, and
backend/LLM-served strings; no prioritization (enumerates every incoherence equally).

## 2 — Cold-read comprehension probe (makes "read it as a user" falsifiable)
"Read each label as a user" is taste until you instrument it. Give a CONTEXT-FREE agent
(ideally 2-3) the frame and ask "what does each label mean, and what would you do next?"
Diff against source truth. Mismatch = a comprehension defect with a measurable rate
("3 of 3 cold readers read the red status label as a pending goal; source says no-reply").
This is the prediction-vs-ground-truth version of "label doesn't mean what it says" —
same spirit as the refuter pass. Catches what the lint can't (incomprehension).

## 3 — Frames for composition (what source can't see)
From captured frames, flag control-styled elements in action contexts and elements
styled like an adjacent live control (the status-pill case). Juxtaposition/styling class;
also your unknown-unknowns pass.

## Real confusion signals you own (NOT the imagined hover map)
- **Clarity has NO hover heatmap** — verified: Click / Scroll / Area / Conversion /
  Attention maps only; hover is Hotjar. Do NOT cite one (inventing an instrument is the
  exact error the dead-click gate forbids). For hover-linger use the per-session
  pointer-trace poller (Layer 3) with its validation gate, labeled OBSERVED — never
  aggregate.
- **Grep the confusing label string in your product's conversation-message table + your
  support/feedback threads** — users who don't understand a label ask about it IN WORDS.
  Real, existing, MEASURED-tier, zero new instrumentation.

## Reporting gate (against false-positive flood)
A UI-clarity finding is reportable ONLY with (a) a prod-DB PREVALENCE number (how many
real leads/users sit in that state) and (b) a stated COST (wrong next action / silent
abandonment). "Needs a hover to understand" would otherwise flag half of any SaaS UI
(icons, timestamps, truncation) — the gate keeps it honest. Report "states never
observed rendered" from the source enumeration so coverage isn't overclaimed.

Complement of dead-click analysis: dead-click = "acted, nothing happened"; UI-clarity =
"would be misled / can't act, but never clicks."

# Dead-click analysis (standing module)

**Dead clicks are the cheapest UI/UX-debt instrument we have** — a dead click is a
user telling you, without words, "I expected this to do something." Every recurring
dead-click target is a mismatch between perceived and real affordance; the fix
direction depends on which way the mismatch runs. Run this every review — it needs no
watching (API + dashboard), and it repeatedly surfaces issues the funnel numbers hide.

## Verify-first gate — a dead-click COUNT is NOT a defect count (calibration)
Clarity's "Dead click" label fires on THREE different behaviors and only one is a
defect. Before citing any dead click, classify it — cheaply, from the events panel:
- **Copy-select drag-start** → the click is the start of a text selection. Tell: an
  adjacent `Selected text` event (often a whole RUN of them). This is copy-out, NOT a
  defect (route to the copy-out finding). *One session — the "dead click" sat inside a
  run of Selected-text events; a false positive.*
- **Reading-tap on prose being read** → stray taps on a message body / record-card
  description while reading, spread out, no selection, no repetition. Low signal.
  *Another — taps on inert record-card title / rationale prose.*
- **Genuine false affordance** → a *control-styled* element (button/pill/tile) in an
  *action context*, clicked REPEATEDLY with no reaction. This is the defect.
  *A third — a green "Connection sent" status pill, styled like the live action button
  beside it in a suggested-actions row, hammered 5×.*

Gate: (1) **is there a real dead-click EVENT** in this session (not just a
classifier's hypothesis — two sessions had ZERO dead-click events yet were cited);
(2) is it copy-select or reading-tap (drop it); (3) only a repeated click on a
control-styled target in an action context survives as a defect. The automated watchers
over-called this class; a human watch caught it — this is exactly the Stage-5 role.
**Don't trust the count; verify each target.**

**This gate is one row of a general claim-type verification table — write the row
before trusting any classifier signal.** For each claim class: *required raw evidence ·
known false-positive modes · alternate explanations that must die.* E.g. dead-click →
{a real Dead-click event exists} · {copy-select drag, reading-tap} · {is it actually a
selection? a working control clicked once?}. never-returned → {no session cross-day} ·
{adblock invisibility, cross-account return} · {did they return under another uid?}.
Adding a claim class means adding its row first; a signal with no row is a hypothesis,
not a finding.

Taxonomy (from the census — 164 dead clicks / 23 sessions, floors —
pre-gate, so counts are upper bounds that include copy-select + reading-taps):

1. **Whole-surface false affordance — the biggest, most actionable class.** A
   card / tile / banner / list-row that contains a *small* inner CTA, but the whole
   visual container reads as clickable — so clicks land on the body, image, heading,
   or padding, not the button. **Fix = make the ENTIRE surface clickable** (the
   opposite of "make it inert"). Named instances: two **onboarding welcome cards** —
   each a headline with a small inner CTA — where Clarity click-dots cluster on the
   banner body, not the button (flagged from a shared recording — users appear to click
   the banner body, not the small button); an **onboarding tile** (one user dead-clicked
   it). The strongest confirmed instance: a **"Connection sent" status pill** —
   green, checkmark, styled exactly like the live action button beside it in a
   suggested-actions row, hammered 5×; the user wants to act on the sent request
   (open the message / thread), the pill is inert. (A record-card title / rationale
   prose is also inert and draws stray taps, but weakly — that's reading-tap territory
   per the gate above, not a crisp defect.)
   Detection: cluster dead clicks by nearest interactive ancestor — if a real CTA
   shares the container, it's this class.
2. **Pseudo-interactive text — make it honest.** Agent reasoning/"Thoughts" lines,
   criteria chips, drafted-message text that users **select-copy** (copy is
   INFERRED — clipboard is invisible). Here the fix runs the other way: either add a
   real affordance (a copy button, an expand toggle — the copy-out demand is genuine)
   or make the text visibly non-interactive so it stops inviting clicks.
3. **Disabled controls while the agent works** — users hammer a disabled Send /
   primary-action button (watched: 3 dead action-button clicks in one session).
   Clarity's Dead-click label is unreliable here (any DOM reaction suppresses it);
   instrument a `*.DisabledClick` event for an unambiguous impatience signal, and
   consider queuing the message + a "you can type while I work" affordance.
4. **Status chips/steppers styled as actions — no target** (a sub-case of class 1,
   the confirmed one). One user hammered the green **"Connection sent"** pill 5× and,
   in another session, clicked the **"Pending acceptance"** stepper — both are
   outreach-STATUS indicators dressed as actions. The user wants to act on the sent
   request (open the message / thread / advance it). Fix: make it live (deep-link to
   the pending request / queued message) OR de-button it to a plain status chip with
   the next step stated inline ("waiting for X to accept — we'll message automatically").
   The "Trial x/xx" badge is the softer version — clicking the counter = wanting a
   limit/upgrade panel that doesn't open (a feature gap, and often NOT labeled a dead
   click, so verify the event exists before citing it).
5. **Translate/locale artifacts** — auto-translate breaking React interactivity.
6. **Rage-adjacent repeats** (same target ≥3×) — track via the rage-click filter.

**Dead-click analysis is a MANDATORY separate section in every report** (not folded
into patterns). Its procedure:
1. **Rank targets by frequency** — use the **aggregate dead-click metric**
   (`query-analytics-dashboard`: "top pages by dead click count") as the ranking layer,
   NOT per-session floors (untruncated, cross-session). Exclusions apply. Then drill to
   the element via the dead-click heatmap.
2. **Classify** each top target (the 6 classes above) and tag a **fix direction**:
   whole-surface-clickable / add-affordance / make-inert / link-it / instrument.
3. **Triangulate each top target two ways** — this is what turns "people click here"
   into a confirmed defect:
   - **Frontend source (the decisive check):** grep your frontend source for the
     element's text / component and confirm whether it actually has an `onClick`, is
     wrapped in a link/`<button>`, or is inert markup. A dead click on an element the
     source shows has NO handler = a proven false affordance (this is the check run
     manually on the welcome banners → "confirm the area is not clickable"). Cite
     the file:line.
   - **Product DB:** does the action the user was reaching for have any backing? (e.g. a
     dead-clicked "Connection sent" chip → is there a message-action row it *could*
     link to; a record-card click → did that record get acted on).
4. **Output**: a ranked table — target · surface · dead-click count (floor) · class ·
   fix direction · source confirmation (file:line, has-handler y/n) · session links.

Monthly cadence: track the dashboard dead-click % as the standing UX-debt KPI; every
new surface gets a dead-click check 2 weeks post-ship.
