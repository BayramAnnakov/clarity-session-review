# Changelog

All notable changes to this skill are documented here. This is a public snapshot
of a living internal skill; the principles are battle-tested, the examples anonymized.

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
