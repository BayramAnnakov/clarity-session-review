# clarity-session-review

A reusable agent **skill** for reviewing [Microsoft Clarity](https://clarity.microsoft.com)
session recordings the way that produces **findings, not anecdotes** — and doesn't
let a half-trusted event timeline become a confident, wrong story.

It's a discipline, not a dashboard: question-scoped triage → attribution → replay-watch
→ database/source triangulation → a verifiable evidence appendix. It runs as a
[Claude Code](https://claude.com/claude-code) / Codex skill (a `SKILL.md` the agent
loads on demand), but the method reads fine as a plain playbook for a human, too.

## Why it exists

It was born the day replay-watching **overturned four timeline-based conclusions** in a
single investigation:

- a user filed as "bailed at the redirect" had actually spent **two minutes inside the
  hosted OAuth flow**;
- a "five-day starer" was a **hidden background tab**;
- a "never-returned" user **had returned**;
- a dramatic "48-minute struggle session" was an **internal teammate's own browser**.

Every one was read straight off the Clarity event timeline. Watching the replays — and
checking them against the product database and the frontend source — reversed all four.
This skill is the checklist that makes that the default, not the lucky exception.

## The eight principles (each one paid for by a specific mistake)

1. **Question before player.** No discriminating question → no watching.
2. **Attribute before interpreting.** Wire Clarity's Identify API if you can — it's
   the first-class join. Until then, session-entry URLs usually carry the identity —
   join it to your database before you interpret anything.
3. **A replay alone is a story; replay + database + source code is a finding.**
   Triangulate every load-bearing claim.
4. **TIMELINE ≠ REPLAY.** API timelines are truncated and masked — treat their counts as
   floors; never present a timeline read as watched.
5. **Every claim ships with its evidence coordinates** — link + timestamps + what to
   check. Verification should be a two-minute job.
6. **Count people, not sessions.** Clarity fragments one visit into many "sessions" (one
   user showed up as 59); on our runs 50-60% of a pull was thin bounces. One run's 462
   sessions was **~26 real people** — lead with that number.
7. **Audit what the UI *shows*, not only what users click.** The method is behavioral and
   blind to a misleading label or a status with no next action; a source-lint of the
   label code catches those. *(Provisional.)*
8. **Walk the step before you explain it.** Before theorizing about any step, execute it
   yourself on the real product, end to end. Replays tell you WHERE people stop; only
   walking tells you WHAT you were asking of them. **A partial walk is worse than none** —
   it manufactures confidence: one halted at a credential field and published a careful
   account of the ask, missing that the real ask was a password *and* a live 2FA code. If
   you can't finish a step (credentials, payment, a third-party account), hand it to a
   human for full-path screenshots — never infer a flow's tail.

## What's inside

| File | What it is |
|---|---|
| [`SKILL.md`](SKILL.md) | The skill: the eight principles, the two modes, the pipeline, the report contract, the replay-semantics gotcha list, the cadences, and the blind spots. |
| [`references/method.md`](references/method.md) | Per-session mechanics + the standing modules: the **Clarity-instruments toolkit** (recordings are 1 of ~10 families), **thin-session forensics**, **dead-click analysis** (with a verify-first gate — a dead-click *count* is not a defect count), the **UI-clarity review**, the **discovery modules** (first-session comprehension · input-struggle/abandoned-intent · person-arc/return-visit · success-session shape), and a date-stamped **Clarity-facts appendix**. |
| [`references/periodic-review.md`](references/periodic-review.md) | Mode B — the recurring "session-intelligence report" over ALL sessions in a window, as a **resumable multi-agent workflow** (scout → triage fan-out → serial watch → synthesize + adversarial refute). |
| [`ADAPTING.md`](ADAPTING.md) | The eight-item checklist to wire the method to **your** product (URL→identity join, your database, your exclusion list, your source paths…). |
| [`examples/`](examples/) | A templatized, data-driven report generator. |

## Two modes

- **Targeted investigation** — a specific question ("why did user X churn", "verify the
  fix", "what did this user do before the call"). Run the pipeline directly.
- **Periodic census** — the recurring report over *every* session in a window. Same
  principles, orchestrated as a resumable multi-agent workflow.

## Install (as an agent skill)

Clone, then symlink (so updates propagate) or copy into your agent's skills directory:

```bash
git clone https://github.com/BayramAnnakov/clarity-session-review
cd clarity-session-review

# Claude Code (global skills)
ln -s "$PWD" ~/.claude/skills/clarity-session-review
```

Then adapt it to your product with the [`ADAPTING.md`](ADAPTING.md) checklist. The
skill auto-loads when you ask your agent to "watch recordings", "check Clarity", "review
all sessions", "why did users drop off", "verify the fix", or "run the dead-click review".

Not using an agent? Read `SKILL.md` and the `references/` top-to-bottom — it's a
complete manual method.

## What this is not

- Not a Clarity API wrapper or a scraper — it's the *judgment layer* on top of Clarity's
  own tools (MCP, API, dashboard).
- Not a substitute for your analytics — it's the **replay** discipline that explains what
  the aggregate numbers can't, and names what the instrument is blind to.

## Credit & license

Distilled from real practice by [Bayram Annakov](https://www.linkedin.com/in/bayramannakov/).
This is a public snapshot of a living internal skill — the principles are battle-tested;
the examples are anonymized. Contributions and adaptations welcome.

MIT — see [LICENSE](LICENSE).
