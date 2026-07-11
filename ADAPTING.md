# Adapting this skill to your product

The method is product-neutral, but it only produces *findings* (not anecdotes) when
it's wired to your product's specifics. This is the checklist that replaces the
internal config the skill was born with. Fill each item once; it becomes your
compounding codebook.

Think of it as the counterpart to principle 2 (*attribute before interpreting*) and
principle 3 (*replay + database + source = a finding*): both need to know **where your
truth lives**.

## 1. Clarity access

- **Project.** The Clarity project ID for the site whose recordings you're reviewing.
- **API token.** A Clarity data-export token, stored outside the repo (an env var or a
  file the tooling reads). The direct API caps `count` at 250 per request and rate-limits
  under load — plan day-slices for wide windows (see `references/periodic-review.md`).
- **MCP server (optional).** If you drive Clarity from an agent, the Clarity MCP server
  exposes `list-session-recordings`, `query-analytics-dashboard` (the untruncated
  aggregate layer — use it FIRST as the census), and the docs resource.

## 2. Your URL → identity join (principle 2)

First check whether you can simply wire Clarity's
[Identify API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/identify-api)
(`clarity("identify", customId)` on login — hashed client-side, filterable across the
dashboard, recordings, and heatmaps). That is the first-class attribution mechanism,
and everything below becomes the fallback for sessions recorded before you wired it.

If it's not wired yet, find the identity your **session-entry URLs** already carry:

- What's the URL shape of your app? Which path segment is the **account/workspace ID**,
  and which is the **object ID** (the specific record the user was looking at)?
  - Example shape: `app.example.com/{accountId}/{objectType}/{objectId}`.
- Which table does the account ID join to (users / accounts / workspaces)?
- Which table does the object ID join to (the conversation, order, document, lead…)?
  This is what lets you pin the *exact* record and disambiguate multi-user accounts.
- Note any query params that mark a **value-moment surface** (e.g. `?panel=…`) — useful
  as a triage population filter.
- **If your URLs carry no identity at all** (anonymous-majority B2C — storefronts,
  content sites): instrument the Identify API + custom tags at login/checkout going
  forward, join purchasers via order-confirmation URLs, and accept that for past
  sessions the only person-proxy is the browser-uid — report **rates over a cleaned
  uid cohort**, not people counts; a true people count is not recoverable retroactively.

## 3. Your database — where the real outcome lives (principle 3)

List the tables/fields that record what *actually* happened, so a replay can be
triangulated against ground truth. Typical ones:

- **Subscription / trial state** — the field a "your plan has ended" banner reads from.
- **Integration / connect rows** — the row that proves an OAuth/connect actually
  succeeded (the webhook-created record), so a watched "connect attempt" can be
  confirmed or refuted.
- **Outbound actions** — message/send/action rows with their status enums, so a
  status-column claim can be checked against real state.
- **The conversation / activity log** — the messages or events tied to the object ID.
- Note your column-naming convention and how to connect (never hardcode credentials —
  read them from an env var / secrets file).

## 4. Your exclusion list (principle 2, 6)

- Enumerate **team / test / internal accounts** — the ones that must never count as
  external users.
- **uid-level exclusion:** any browser-uid that EVER touches an excluded account is
  excluded EVERYWHERE. Compute the excluded-uid set once and propagate it across the
  whole pull — a single misattributed session becomes a confidently wrong finding.
- Note any **off-instrument** accounts (e.g. customers who pay off-platform) so a "$0 /
  no activity" reading isn't mistaken for a real gap.

## 5. Your frontend source (principle 3, 7; dead-click module)

- Where does your UI source live, and how do you grep it? The dead-click module and the
  UI-clarity source-lint both need to confirm, in code, whether an element has an
  `onClick`/link (a *proven* false affordance, cited `file:line`) and whether any label
  resolver maps one label to more than one state.
- Which component(s) render the status labels / lifecycle states users read? Those are
  the first place principle 7's source-lint looks.

## 6. Your working-surface path segment (heatmap module)

Clarity heatmaps aggregate by URL. Because your URLs are per-account/per-object, an
`is exactly` match pools only a handful of visits. Switch the matcher to **`contains`**
and enter the **path segment of your main working surface** (e.g. a chat route like
`/c/`, a checkout `/checkout/`, a dashboard `/app/`) to aggregate the whole surface for
the dead-click / scroll / attention maps.

- Note whether your app **page-scrolls or scrolls inside a nested container.** If it's a
  fixed app-shell with nested scroll, Clarity's scroll & attention maps are **blind to
  in-container depth** — don't read "100% reached every depth" as "users saw everything"
  (see the nested-scroll blind spot in `references/method.md`).

## 7. Your agent runtime (Mode B, the periodic census)

If you run the at-scale periodic review as a multi-agent workflow:

- Which orchestration runtime, and what's its **rate-limit reset window**? (The watch
  phase is the bottleneck and can hit limits; the workflow is built to resume from a
  journal — schedule a fallback trigger just past your reset.)
- Where do watchers write their per-session **observation files**? (One file per session
  → the synthesis reads files, not one giant context.)

## 8. Your feedback + call channels (cadences)

- Where does user feedback land (a support inbox, a feedback address)? Motive is never
  on tape — pre-call prep and finding-explanation both mine it.
- Your product-analytics notes / instrument map: the living gotcha list this skill reads
  before the first run of the day, and writes new method lessons back into.

---

Once these eight are filled, every principle in `SKILL.md` has a concrete referent, and
the method runs at full strength on your product.
