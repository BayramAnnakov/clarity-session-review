# Changelog

All notable changes to this skill are documented here. This is a public snapshot
of a living internal skill; the principles are battle-tested, the examples anonymized.

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
