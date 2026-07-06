---
description: "Walk the current anchor's backlog and move it toward the **groomed state** — promote every item it can to **Ready**, park items that need user input in dated feature docs, repair link integrity."
---
# /Groom
Walk the current anchor's backlog and move it toward the **groomed state** — promote every item it can to **Ready**, park items that need user input in dated feature docs, repair link integrity. Convergent: safe to call anytime; never interrupts you mid-run.

| -[[SKL Groom]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [SKL Groom](hook://p/SKL%20Groom)<br>: the `/groom` skill |
| --- | --- |
| Related | [[skills/groom/SKILL.md\|SKILL]],   |
| [[SKL Groom Design\|Design]] |  |

DMUX trigger: **`groom`** (prefix-trigger; whatever you dictate after becomes the argument). Slash invocation: `/groom`, `/groom roadmap`, `/groom milestone {N}`, `/groom F{n}`.


## What "Ready" means

> An item is *Ready* when the agent believes it knows how to do this task without further involvement of the user.

Sharper than "questions resolved." If the task still hides any "wait, what about X?" that you'd have to answer, it's **not** Ready — it's *blocked on questions*, and the work belongs in a feature doc until those questions resolve.


## How it works

`/groom` works the **frontier** — the tasks that could be next for execution (everything under `## Now` / `## Next`, plus the next unmet roadmap milestone). For each frontier item the agent investigates quietly — reads related docs, infers from context, drafts a spec, runs lightweight planning — then drives it into one of **five groomed states**, each with a body contract a rule checks:

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
| `/groom roadmap` | Roadmap's next milestone instead of the backlog. |
| `/groom roadmap <milestone>` | Named roadmap milestone. |
| `/groom F<n>` | Single item, by F-number. |
| `/groom <item name>` | Single item by name match. |


## Idempotence

Safe to run repeatedly. Items already Ready, Active, blocked-on-questions, Verify, Done, or in Legwork are skipped. Running twice with no new info should produce no diff on the second pass.


## Design principle

`/groom` processes the entire batch autonomously before involving you: every question it can't resolve is parked in `{NAME} queries.md`, never raised mid-run. Each round-trip costs scrollback context and stalls the batch — the whole design targets *one* pile to answer, not a trickle of interruptions. The full rationale lives in the design: **[[SKL Groom Design]]** → **[[Query PRD]]**.
