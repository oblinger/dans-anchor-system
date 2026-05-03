# /Triage

Surface the **status of the anchor** — every backlog item except those in `## Later` and `## Icebox` — into one batched inbox at `{NAME} Triage.md`. The user reads it to see where everything stands and what's waiting on them; questions get answered with shorthand.

DMUX trigger: **`triage`** (prefix-trigger; speaking `triage` stashes `/triage`, parallel to `snip` / `commission` / `fortify` / `groom`). Punctuation: **`"`** (a single double-quote as the entire message), parallel to `crank`/`'` and `/land`/`.`. Slash invocation: `/triage`, `/triage roadmap`, `/triage milestone {N}`.


## What it does

Walks the anchor's backlog, computes per-state and per-horizon counts, picks an anchor TAG (`[U]` / `[A]` / `[U+A]` / `[G]` / `[?]` / `[]`), and writes a destructively-rewritten `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`. The whole file is agent-owned; the user reads and responds.

**Also regenerates the anchor's per-anchor section in `~/ob/kmr/Q.md`** — the vault-level Agent Status dashboard. Both `/ask` and `/triage` produce a fresh local triage + a fresh Q.md per-anchor section on every invocation.

Pairs with `/groom` (which *creates* `[Questions]` state by parking work) and `/roster` (state-of-the-work). `/triage` is roster-for-status: same per-bucket counts, plus pipe-grouped totals and the anchor TAG.


## What you'll see

The Triage file opens at the end of every run. Top of the file is a banner:

```
# [U+A]  [[ACME]] Triage  -  Questions 2    Verify 1   |   Active 1    Ready 1   |   Now 2    Next 1    Later 1    Icebox 0
```

The TAG (`[U+A]` / `[U]` / `[A]` / `[G]` / `[?]` / `[]`) tells you at a glance what the anchor needs:
- **`[U]`** — your input is needed (Questions or Verify items).
- **`[A]`** — agent has Ready/Active work to crank.
- **`[U+A]`** — both.
- **`[G]`** — items in Now/Next that need grooming (no U or A items yet).
- **`[?]`** — only Later items; nothing prioritized.
- **`[]`** — nothing anywhere.

Below the banner, items are grouped under workflow-state H2s — `## Active`, `## Ready`, `## Now`, `## Next` — exactly mirroring the backlog (Later and Icebox are not listed in the body, only counted in the banner). Within each H2, items appear in **source order from the backlog**.

Each row shows a status bracket with count: `**[3 Questions]**`, `**[Verify]**`, `**[Ready]**`, `**[5 Ready]**` (milestone with 5 sub-items), `**[Active]**`. Eye lands on the bracket and knows what kind of attention the item needs.

If à la carte questions exist, one bullet line directly under the H1 links to them: `- **[N Questions]**  [[{NAME} Questions]]`.

Example body:

```
# [U+A]  [[CAE]] Triage  -  Questions 2    Verify 1   |   Active 1    Ready 1   |   Now 2    Next 1    Later 1    Icebox 0
- **[3 Questions]**  [[CAE Questions]]
## Active
- **[Active]** [[F1 — Cron Syntax]] — Cron expressions for recurring task schedules.
## Ready
- **[Ready]** [[F3 — Retry Backoff Polish]] — Tune exponential-backoff caps after user feedback.
## Now
- **[4 Questions]** [[F2 Task Groups]] — Rendering of task groups.
- **[Verify]** [[F7 — Webhook Notifications]] — Webhook fires on task completion.
	- Verify by triggering a test job and confirming the configured URL receives a POST with the documented JSON payload (see [[CAE PRD]] § Webhooks).
## Next
- **[5 Questions]** [[F4 Priority Levels]] — 2 pending Qs (Q1, Q3).
```

No blank lines anywhere in the body. No meta prose. Maximum signal density.


## How you respond

| You say | Agent does |
|---|---|
| `F5 Q4: yes` | Resolves Q4 in F5's feature doc with answer "yes". Moves the question to `### Resolved`. |
| `Q4: yes` (after announcing sticky context "I'm in F5 now") | Same as above. Sticky context survives turn-to-turn until you switch ("now F12"). |
| `verified F23` / `F23 verified` | Moves F23's backlog row from its workflow H2 (with `[Verify]` bracket) to `## Done`; updates feature-doc Status to Done. |
| `F23 nope, X is broken` | Captures rejection; agent files a follow-up bullet on the backlog row and continues design. |
| `{NAME} Q3: …` | Resolves à la carte Q3 in `{NAME} Questions.md` (e.g., "SKA Q3: option A"). |


## Compound usage

**"triage and groom"** (or "groom and then triage") — runs `/groom` first to park new items in `[Questions]`, then `/triage` to surface the inbox. Pilot-level natural-language interpretation; both skills stay small.


## When to invoke

- After a long session where the agent has been parking questions; you want to see what's piled up.
- Whenever you switch context and want to know where the anchor stands.
- After a `/groom` run to immediately surface the freshly-parked items.
- Default check-in at the start of an engagement session.


## Idempotence

Strictly idempotent + destructive. The whole file (below YAML frontmatter) is agent-owned and rewritten on every run. There are no marker comments, no preserve-user-edits regions — anything the user wants to persist belongs in the relevant feature doc, not the Triage file.
