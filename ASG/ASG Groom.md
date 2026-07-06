---
description: "/groom — get every task that could be next fully ready to execute; it never asks you a question mid-run."
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[ASG]] → [ASG Groom](hook://p/ASG%20Groom)
# /groom — user guide

**Full internals & design:** [[SKL Groom]]   ·   **Runtime spec:** [[skills/groom/SKILL.md\|SKILL.md]]

`/groom` walks the current anchor's backlog and gets every task that could be next fully ready to execute — planning it, declaring its next step, promoting it, or parking its blocking questions. Convergent: safe to call anytime.

DMUX trigger: **`groom`** (say "groom …" and it becomes `/groom …`). Slash: `/groom`, `/groom roadmap`, `/groom milestone {N}`, `/groom F{n}`.

## How it works

`/groom` works the **frontier** — the tasks that could be next (everything under `## Now` / `## Next`, plus the next unmet roadmap milestone). For each frontier item it investigates quietly, then drives it into one of **five groomed states**, each with a body contract a rule checks:

- **Executable** (`[Ready]`) → declares the concrete next step it'll take with zero involvement from you.
- **Questions** (`[Questions]`) → the open questions, each answerable in one shot, land in the anchor's `{NAME} queries.md`.
- **Blocked / Waiting** (`[Blocked]` / `[Waiting]`) → names exactly what it's blocked on or awaiting.
- **Verify** (`[Verify]`) → a concrete yes/no for you to confirm.
- **Watching** (`[Watching]`) → a shipped fix soaking, with the date the soak ends.

## It never asks you a question

`/groom` **raises zero questions in chat** — not even a trivial one. Every decision it can make itself, it makes; every genuine question for you gets written into `{NAME} queries.md` (the one place you answer things), never dropped into chat where it scrolls away. When you run `/groom` directly it ends by showing you `/triage` — the status of the anchor and what's waiting on you — and asks nothing.

After you answer the questions in the queries doc, re-run `/groom` to advance the next round.

## Scope arguments

| Invocation | Scope |
| --- | --- |
| `/groom` | The frontier — `## Now` / `## Next` + the next roadmap milestone. Default. |
| `/groom all` | Every pre-Ready item across the whole backlog, `## Later` included. |
| `/groom now` / `/groom next` / `/groom later` | Only that horizon. |
| `/groom legwork` | Only `## Legwork`. |
| `/groom roadmap` / `/groom roadmap <milestone>` | The roadmap's next (or a named) milestone. |
| `/groom F<n>` / `/groom <item name>` | A single item. |
