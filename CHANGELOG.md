# Changelog

All notable changes to this skill are documented here. This is a public snapshot
of a living internal skill; the principles are battle-tested, the examples anonymized.

## [1.2.0] — 2026-07

From a second, harder autopsy: an investigation that watched every relevant replay,
censused the database, read the source, and ran an expert panel — and still shipped
the wrong mechanism, because nobody had walked the step. Seven claims died in that
run; five belonged to the analyst. Every one was killed by a query or a click, never
by an argument.

- **New principle 8 — "Walk the step before you explain it."** Replays show WHERE
  people stop; only executing the step yourself shows WHAT you were asking of them.
  Partial execution is worse than none (it manufactures confidence): the walk that
  halted at a credential field missed that the real ask was password *plus a live 2FA
  code*. If you can't complete a step (credentials, payment), hand it to a human for
  full-path screenshots — never infer a flow's tail. New Stage 4.5 in `method.md`.
- **Principle 6 rebuilt — a rate is four claims, not one.** Added three limbs beside
  the people-not-sessions denominator: strip bots before a segment carries a rate;
  every member could have done it *for the whole window* (a rate spanning a feature
  ship-date is an era artifact); and the trap that survives the rest — *somebody must
  have ATTEMPTED it* (an unattempted step and a failing step are identical in every
  instrument). New "Before any RATE ships" gate in `method.md` with the one query that
  catches it.
- **Principle 3 extended — a column is not behavior until you know what WRITES it.**
  A cron, migration, or vendor webhook can set the field a user's action would; grep
  the writer before interpreting the value.
- **Refuter aimed at the WELD** — when two true findings fuse into a memorable story,
  the weld is the part with no evidence; check the correlation's outcome variable is
  the one your mechanism explains, and hunt one counterexample on purpose.
- **Report contract — a cold-read gate.** Test the report the way you test the
  product: hand it to a no-context reader (or a subagent) and ask what they own,
  what's decided vs open, and whether anything is being asked of them. Answer-first
  page 1; DECIDED vs OPEN with a name on every line; one dated changelog instead of
  scattered strikethroughs; own errors named first.
- **Blind spots promoted from footnotes to GATES** — the third-party-flow interior is
  unobservable (say it in the sentence); absence of complaint disconfirms nothing.

## [1.1.0] — 2026-07

Discovery modules, from a four-perspective product-expert review whose consensus
was: the forensic layer is best-in-class, but the question portfolio only asks
pathology questions — the pipeline routes the player exclusively to failure
signals, leaving replay-unique discovery classes unharvested.

- **Principle 1 extended**: the question portfolio spans four families —
  pathology, comprehension, workflow shape, journey.
- **Four new modules** in `references/method.md`, each running through the
  existing gates (evidence tiers, claim-type verification rows, refuter):
  - *First-session comprehension watch* (EXPERIMENT — promote/kill on a
    2-period hit rate; agent-label validity spot-checked by a human re-watch);
  - *Input-struggle / abandoned-intent forensics* (events-tier: the DB holds
    only submitted inputs — the replay is the sole record of abandoned intent);
  - *Person-arc / return-visit deltas* (second-session-first-action, fluency
    deltas; first-week accounts exempt from the watch cap);
  - *Success-session workflow shape* (~5 value-moment sessions per period —
    the pipeline never flags these, because nothing failed).
- **Report contract additions**: an *opportunities (no fix attached)* section
  (unmet needs aren't force-fitted into the defect template) and a *struggle
  reel* (≤5 clips watched by the team — exposure, not verification).
- **Budget guardrail**: hold the exploration budget constant as the triage
  codebook compounds — a flag rate that only shrinks is a discovery death
  spiral.

## [1.0.1] — 2026-07

Fixes from an adversarial evaluation of the public snapshot (two cold-adopter
execution tests + a live API run + fact-checks against Clarity docs and the
skill's own source-run data):

- **Corrected a false claim**: Clarity DOES have an
  [Identify API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/identify-api) —
  it is now the recommended first-class join in principle 2; the URL→identity
  join is the fallback. Added an anonymous-majority B2C adaptation path.
- **New Clarity-facts appendix** (`references/method.md`): every product-snapshot
  claim (endpoint + request schema, 250-count cap, quotas, retention incl.
  9-month favorites, truncation, heatmap types, player DOM, masking, duration
  semantics) in one date-stamped table, each with a self-check.
- Truncation restated as endpoint/version-dependent (the skill's own run data
  contains 60+-event page-visits); the floors discipline is unchanged.
- De-universalized n=1 statistics ("50-60% of any pull", "expect ~25-40
  flagged") and added a high-traffic sampling path to Mode B; dead-click
  classes labeled as general with one product's instances.
- Hardened the events-panel harvest (repeat-click counts preserved,
  empty-result diagnostic, locale/version caveats).
- Doc-rot pass: removed a committed tool-call artifact, reconciled watch
  counts, fixed stale cross-references, defined OEC, unclaimed the internal
  Mode B workflow script, committed the reference `examples/report.html`, and
  made the example's stat cards derive from its own census data.

## [1.0.0] — 2026-07

First public release. Distilled from two real runs of the method:

- a **targeted deep-dive** where replay-watching overturned four timeline-based
  conclusions (a "bailed at redirect" user had spent two minutes inside OAuth; a
  "five-day starer" was a hidden background tab; a "never-returned" user had
  returned; a dramatic "struggle session" was an internal teammate's own browser);
- a **first at-scale periodic run** — 462 raw sessions resolved to ~26 distinct
  people, 21 watched end-to-end, via a resumable multi-agent workflow.

Includes:

- The seven principles (each one paid for by a specific mistake).
- Two modes: targeted investigation and the periodic session-intelligence census.
- `references/method.md` — per-session mechanics + the standing modules
  (Clarity-instruments toolkit, thin-session forensics, dead-click analysis with a
  verify-first gate, UI-clarity review).
- `references/periodic-review.md` — the at-scale multi-agent workflow
  (scout → triage fan-out → serial watch → synthesize + adversarial refute), resumable.
- `ADAPTING.md` — the checklist for wiring the method to your own product.
- `examples/` — a templatized report generator.
