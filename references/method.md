# How to watch a session recording (staged method)

*Canonical home of the method.
The unit of watching is never "a recording" — it is a QUESTION scoped to a TIME-WINDOW.
A session's information lives in three layers with different access costs; escalate
only when the cheaper layer can't answer.*

| Layer | What it holds | Where it lives | Access cost |
|---|---|---|---|
| 1 — Events | pages, clicks + element text, dead/rage clicks, text-entry, **Page hidden/visible**, durations | API/MCP timeline — **may be TRUNCATED** (endpoint/version-dependent; see Clarity-facts appendix): aggregates are floors; the player events panel is the complete log | seconds per 100 sessions |
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
- **Truncation**: API timelines may be truncated (endpoint/version-dependent) — treat
  event counts as floors, and spot-check one dense session's API timeline against its
  player events panel before relying on API counts for anything load-bearing.
- **Favorite everything relevant today** (30-day rolling retention; favorites are kept
  ~9 months, not forever).
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
  // keep only the OUTERMOST element of a nested identical chain (one per rendered row)
  const p = el.parentElement;
  if (p && (p.innerText || '').trim() === t) return;
  if (/^(Click|Page hidden|Page visible|Dead click|Selected text|Resized page|Rage click|Text input|Quick back click|Smart event|Entered text)[\s\S]{0,120}\d{2}:\d{2}$/.test(t)
      && el.children.length <= 6 && !t.includes('\n\n')) {
    results.push(t.replace(/\n+/g, ' ')
                  .replace(/https?:\S+/g, '<url>')   // strip URLs or output gets blocked
                  .replace(/[?&]\S+/g, ''));
  }
});
// remaining identical rows are REPEATED EVENTS (a hammered dead click) — evidence,
// not noise: keep them with counts instead of Set-deduping them away
const rows = results.filter(r => (r.match(/\d{2}:\d{2}/g)||[]).length === 1);
const counts = new Map();
rows.forEach(r => counts.set(r, (counts.get(r) || 0) + 1));
[...counts].map(([r, n]) => n > 1 ? `${r} ×${n}` : r);
```

Slice the array if it exceeds output limits. This recovers everything the API
truncated (Smart events, Entered text, Quick back clicks included).

**If the harvest returns `[]` on a session that visibly has events, diagnose before
trusting it as "quiet":** count elements matching only the trailing-timestamp anchor
(`[...document.querySelectorAll('div,li')].filter(el => /\d{2}:\d{2}$/.test((el.innerText||'').trim())).length`).
Nonzero ⇒ the event LABELS changed (a Clarity release, or a non-English UI locale —
the alternation above is English-fitted); zero ⇒ the panel DOM restructured
(re-derive the selector). `el.children.length <= 6` is version-fitted, not a player
invariant. An empty harvest is a broken harvester until proven otherwise.

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

**Record the DEVICE for every watched session — it is an attribution field, not
metadata.** The player's Info tab gives device · OS · viewport · location · Clarity's
own "User intent" score. Read it BEFORE interpreting behaviour: a 440×796 MobileSafari
session and a 1536×742 desktop session are different products. *(Paid for: three
"silent" signups read as low-intent tyre-kickers until the Info tab showed all three
were on phones — one of them inside the Google App's in-app webview — and the source
then proved the welcome card's only handlers were hover-based, i.e. dead on touch.
Device turned an anecdote into a defect class.)*
Negative evidence states coverage + resolution. Per session, one appendix row:
**who (workspace + user) · player link · the moments to seek to · the claim · what a
verifier should check · depth label (REPLAY/TIMELINE)** — the evidence-appendix
pattern (one file a verifier can walk link by link). Contradictions update the
upstream census.

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
  Last clicks · plus Scroll · Attention · Area · Conversion). **The URL-match trick is
  essential:**
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

Thin sessions (<30s, ≤1 click; 50-60% of all sessions on our runs — measure your own
share) are a separate instrument, not noise. Aggregate them (Python over the pull JSON) by **entry-URL
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
- (d) **No affordance may depend SOLELY on hover/focus — those events do not exist on
  touch.** Lint every interactive-looking surface for a root whose only handlers are
  `onMouseEnter` / `onMouseLeave` / `onFocus` / `onBlur` and which has **no `onClick`**.
  On a phone that surface is inert *and* never gives the feedback that would tell the
  user it is inert. *(Real instance: a big onboarding card whose root played a video on
  hover to signal "I'm alive" and carried no click handler — only a small inner button
  worked. On desktop the hover-video partly rescued it; on mobile it was a dead image.
  A watched iPhone user tapped the card body twice, got nothing, and ended up in the
  wrong flow.)* Coverage-independent and diffable — the lint's strongest suit, since no
  amount of desktop replay-watching reveals it.
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

## Cross-instrument gate — check UNITS and POPULATION before believing a contradiction

*(Paid for, and it is the easiest self-own in the method: comparing one instrument's
**logged-in users** against another's **sessions**, I "discovered" that our analytics was
blind to mobile. It wasn't. Same-unit comparison — sessions vs sessions — showed the two
instruments agreeing within 15%. The false contradiction was a units error, and it very
nearly shipped as a finding about the instrument.)*

Before publishing ANY "instrument A contradicts instrument B" claim, clear four gates:
1. **Same unit.** sessions ≠ visits ≠ browsers ≠ people ≠ logged-in users. Name the unit
   in the sentence; if the two numbers have different units, there is no contradiction yet.
2. **Same window and timezone**, stated.
3. **Same population filter** — one instrument's number is usually pre-login-inclusive,
   bot-filtered, or team-excluded when the other's isn't.
4. **Population overlap, spot-checked by NAME.** Can instrument B even *see* the specific
   individuals A found? Look up 3-5 named users in both. Blindness is real (ad-blockers,
   ITP, in-app webviews) — but prove it per-user before asserting it in aggregate, and
   remember it makes B's counts **floors**, not fictions.

A contradiction that survives all four is a finding. One that doesn't is arithmetic.

**The dead-click gate is one row of a general claim-type verification table — write the
row before trusting any classifier signal.** For each claim class: *required raw evidence ·
known false-positive modes · alternate explanations that must die.* E.g. dead-click →
{a real Dead-click event exists} · {copy-select drag, reading-tap} · {is it actually a
selection? a working control clicked once?}. never-returned → {no session cross-day} ·
{adblock invisibility, cross-account return} · {did they return under another uid?}.
Adding a claim class means adding its row first; a signal with no row is a hypothesis,
not a finding.

Taxonomy (from one product's census — 164 dead clicks / 23 sessions, floors —
pre-gate, so counts are upper bounds that include copy-select + reading-taps). The
CLASSES are general; the named instances are one product's (an AI outreach tool) —
map them to your own domain rather than hunting for these exact elements:

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
3. **Disabled controls during async work** (e.g. while an AI agent or a long job
   runs) — users hammer a disabled Send / primary-action button (watched: 3 dead
   action-button clicks in one session).
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

# Discovery modules — balancing the question portfolio

*Added after a four-perspective product-expert review (2026-07) whose consensus was:
the forensic pipeline is excellent and points the player only at FAILURE signals —
drop-offs, dead clicks, anomalies. A method that only asks pathology questions is
structurally blind to everything else replays uniquely show: how a first-timer's
comprehension forms, what intent gets typed and abandoned, how successful users
actually work, and what changes between visits. These four modules add those question
families.*

**Guardrails (non-negotiable).** Every module runs THROUGH the existing discipline —
Stage-0 question, evidence tiers, appendix rows, the refuter — never around it.
Before using any NEW claim class, write its claim-type verification row (required raw
evidence · known false-positive modes · alternate explanations that must die); a
signal with no row is a hypothesis. The pointer-trace poller STAYS gated: no
hesitation / approach-retreat claims unless a named decision needs sub-second
dynamics AND the Stage-3 validation gate passes — motionless-reading windows and
`Page hidden` attention carry most of the comprehension signal at frame-tier cost.

## First-session comprehension watch — EXPERIMENT

*Status: experiment, 2 periods. Promote to standing only if it produces findings that
change decisions at ≥ the flagged-set rate.*

Every genuinely-new external human's first engaged session gets ONE full 1× watch,
skip-inactivity OFF — exempt from the triage gate and the per-workspace watch cap.
"Genuinely new" is an attribution claim: verify a sign-up flow and dedup
cross-account humans (principle 2) before calling anyone new. At low traffic this is
a handful of sessions per period — the cheapest attack on activation there is.

Harvest (replay-unique: the database shows the activation OUTCOME; only the tape
shows the PATH):
- what was on screen during motionless-READING windows — what got read vs skipped;
- the first thing tried, and the gap between what onboarding DISPLAYS and what the
  user ATTENDS to.

### The output contract — DO NOT ask for "the moment comprehension broke"

*(Paid for. The first run of this module required a field called "the moment
comprehension broke". The watcher produced confident motive stories; on the mandated
human re-watch the reviewer agreed with the BEHAVIOUR 2/2 and said **"not sure"** about
the motive **2/2**. Of course he did — **motive is never on tape**; it is in this
skill's own blind-spot list. The module was asking for an unfalsifiable field, which is
precisely the confident-wrong-story failure the whole skill exists to prevent.)*

Each watched first session outputs exactly three things:

1. **The DIVERGENCE POINT (OBSERVED — behavioural only).** Timestamp + frame where the
   user's behaviour departed from the designed path, stated with **no mental state in
   the sentence**: "opened the example, then opened the menu, then left — never typed",
   NOT "did not understand that he had to type". If you cannot write it without a verb
   like *understood / realised / expected / was confused*, you are inferring. A verifier
   must be able to confirm this line from the frames alone.
2. **AT LEAST TWO competing explanations (INFERRED — labelled).** Never one. One
   explanation is a story; two force the uncertainty into the open. ("(a) the pre-filled
   composer read as already-done; (b) low intent — a 10-second tyre-kick.")
3. **The PROBE.** The single question — to the user, or to a cold-reader — that would
   discriminate between (a) and (b). This is the deliverable that closes the gap; the
   watch alone never will.

**The validity check tests #1, not #2.** Each period, a human re-watches a sample and
confirms the DIVERGENCE POINT; publish that agreement rate. Never ask a reviewer to
ratify a motive — they will say "not sure", and they will be right.

Known false-positive modes (the claim-type row): a backgrounded tab is not stalled
comprehension (read `Page hidden`/`visible` first); auto-translate artifacts; a
"first session" that is a cross-account return; masked text misread as ignored text.
Route each divergence point two ways: an OPPORTUNITY row in the report, and a real
question for that user ("at MM:SS you opened the example and then left — what were you
looking for?").

## Input-struggle / abandoned-intent forensics (standing — events-tier, cheap)

The events harvest already captures `Entered text` / `Text input` rows and then no
module reads them; and the masking ▪-count trick tracks attempt LENGTH without
reading a character of content. The product database holds only SUBMITTED inputs —
the replay is the sole record of what users wanted to say and abandoned. Per input
surface, from the harvest:
- re-entry count and clear-and-retype cycles; dwell before the first keystroke;
- the **abandonment field** — the last field touched before the session died;
- validation-error loops (error copy in frame + repeated input on the same field);
- for your primary free-text surface (a chat/prompt box, search, a long form field):
  drafts typed-then-deleted, rephrase loops (attempt length shrinking across tries,
  via ▪ counts), composed-but-never-submitted.

Triangulate every abandoned-intent claim against the database: confirm no submission
row exists for that window. Known false-positive modes: ordinary composition editing
(one rewrite ≠ struggle — require ≥2 clear-and-retype cycles or an abandonment);
paste events (instant length jump); IME/autocomplete artifacts.
Output: surface · sessions · struggle class · abandoned y/n · DB-confirmed-absent ·
links. An abandoned draft is an unmet need in the user's own (redacted) words —
route it to the report's Opportunities section.

## Person-arc / return-visit deltas (standing)

The identity stitching built for denominator hygiene — uid collapse, URL joins,
referrer chains — gets repointed at BEHAVIOR. For each human with ≥2 real visits in
the window:
- **Second-session-first-action:** what they went to FIRST on return, and within how
  many seconds — straight to the working surface, a re-orientation loop, or
  re-reading onboarding they'd already seen. The most honest revealed-preference
  signal of what value the user thinks the product has. Timeline-tier for most
  sessions; replay-tier when ambiguous.
- **Fluency delta:** time-to-first-meaningful-action on visit 1 vs visit N;
  hesitations that vanish (habituation) vs persist (standing UX debt); a dead-click
  that recurs across weeks before the account goes quiet. Only a replay distinguishes
  a confident return from a lost one — the database logs identical outcome rows for
  both.

First-week accounts are EXEMPT from the per-workspace watch cap: the cap protects the
census from heavy users; it must not slice a new signup's week-1 arc into
disconnected samples.
Known false-positive modes: cross-device humans (uid undercounts — state coverage); a
"return" that is a teammate on the account (attribution); parked-tab heartbeats are
not returns (classify via thin-session forensics first). Any pattern generalized from
ONE arc goes through the refuter's single-user-generalization row.
Feed: the report's "users to call" rows, with the timestamps already attached.

## Success-session workflow shape (standing)

Each period, DB-select ~5 sessions where the value moment was REACHED — the
behavioral pipeline never flags these, because nothing failed — and watch HOW the
work was actually done:
- order of operations vs the designed path; workarounds; copy-outs (the demand
  dead-click class 2 already proved); external round-trips — the quick-backs metric
  RANKS them; watch the top cases instead of stopping at the aggregate;
- what users do AROUND the product to make it work.

The database proves the outcome happened; only the tape shows the detours the user
survived to get there — roadmap material dictated by behavior instead of opinion.
Known false-positive modes: a power user's idiosyncrasy is not "the workflow"
(require the same shape from ≥2 independent humans, else label it single-user); team
members demoing (attribution).
Feed: the Opportunities section + the pattern table, strength-tagged as usual.

---

# Clarity-facts appendix — product-snapshot claims, verified 2026-07

Everything this skill asserts about Clarity-the-product is a snapshot, not a law.
This table is the single home for those facts. Re-verify a row before leaning on it;
when one fails its self-check, update it HERE (a method lesson, per the routing rule).
Never cite an instrument or behavior you haven't verified in YOUR Clarity build —
inventing instruments is the exact error the dead-click gate forbids.

| Fact (verified 2026-07) | Self-check / failure mode |
|---|---|
| **Identify API exists**: `clarity("identify", customId)` — hashed client-side, filterable across dashboard/recordings/heatmaps ([docs](https://learn.microsoft.com/en-us/clarity/setup-and-installation/identify-api)) | If wired, prefer it over the URL-join for attribution. |
| **Recordings pull**: `POST https://clarity.microsoft.com/mcp/recordings/sample`, Bearer = a Data Export token (Clarity → Settings → Data Export). `count` ≤ 250 (default 100). The date range is REQUIRED and must be nested as `filters.date = {start, end}` (ISO-8601 UTC with milliseconds) — a top-level-only `start`/`end` returns HTTP 500. `sortBy` is an integer enum (0/1 = session start desc/asc, 2/3 = duration, 4/5 = click count, 6/7 = page count). Schema source: `@microsoft/clarity-mcp-server` on npm. | Observed sort behavior doesn't always match the enum name — verify ordering on a 3-session pull before trusting it. Quotas are undocumented: be frugal; the API 503s under load (back off ~90s). The separate aggregate Data Export API is documented at 10 requests/project/day. |
| **MCP server**: `@microsoft/clarity-mcp-server` (npm), e.g. `npx @microsoft/clarity-mcp-server --clarity_api_token=<token>` — exposes `list-session-recordings` + `query-analytics-dashboard`. | Tool-not-found ⇒ the server isn't registered in your agent config, not a Clarity outage. |
| **Retention**: recordings ~30 days rolling; favorited/labeled sessions ~9 months; heatmap data ~9 months ([docs](https://learn.microsoft.com/en-us/clarity/setup-and-installation/data-retention)). | If retention shortens, cadence math silently loses the tail — favorite-on-flag the day a cohort is defined. |
| **Timeline truncation is endpoint/version-dependent** — an early pull capped near ~5 events per page-visit; a 2026-07 `recordings/sample` pull returned 60+ events on one page-visit. | Spot-check one dense session's API timeline against its player events panel each run; treat API counts as floors regardless of what you find. |
| **Heatmap types**: Click (All/Dead/Rage/Error/First/Last), Scroll, Area, Attention, Conversion — and NO hover map (hover is a Hotjar feature) ([docs](https://learn.microsoft.com/en-us/clarity/heatmaps/)). | Fails safe if it rots (you'd merely under-use a new map type) — but never CITE a map you haven't opened. |
| **Player DOM**: virtual cursor `.clarity-pointer-move`, clicks `.clarity-click`/`.clarity-click-ring`; events panel rows are English-UI text. | Implementation details — any Clarity release can break them. The Stage-3 validation gate is mandatory before any trace claim; the Stage-2 harvest needs its empty-result diagnostic. |
| **Masking**: `▪` runs preserve character counts (the decode trick). | Masking is an implementation detail — a masking change would make decodes confidently wrong; re-verify against a known string when in doubt. |
| **Durations**: `totalDuration` AND `activeDuration` both include hidden-tab time (re-confirmed 2026-07: a "5m32s active" zero-click backgrounded session with the two fields exactly equal). | If Clarity ever fixes `activeDuration`, the prescribed hidden-tab subtraction would double-correct — re-verify the two-fields-equal tell periodically. |
