---
description: "the skill that builds it"
---

| -[[DAS Ask]]- | : the `/ask` skill<br>→ [[DAS]] → [docs](hook://docs) → [DAS Ask](hook://p/DAS%20Ask)  |
| --- | --- |
| Related | [[skills/ask/SKILL.md\|SKILL]],  [[DAS ask-inline]],   |
| [[Query PRD\|Design]]  |  |
| ... |  |

# DAS Ask
The **`/ask` skill** is the universal asking subroutine.

The **`/ask` skill** is the system for *not* asking you questions piecemeal. Whenever an agent has decisions it can't make itself, `/ask` eliminates every one it can (guessing reversible calls, running checks itself, inferring from the code), then consolidates the irreducible remainder into one place you can answer in a single pass — the anchor's `{slug} queries.md` — and surfaces it on the vault-wide dashboard `[[Q]]`. You never get a trickle of one-off pings.


## What you'll see

**The vault-wide dashboard `[[Q]]`** (`~/ob/kmr/Q.md`) lists every anchor that needs you or has agent-runnable work. Bind a key to it; one press surfaces everything across all your agents. Its H1 banner counts two buckets — **Runnable** (agent-actionable: Ready + Active) and **User** (needs you: Questions + user-gated actions). Below it, each anchor is a section headed by its own banner (the slug links to that anchor's `{slug} queries.md`), then one bullet per item. Most-recently-touched anchors sort to the top; an anchor with zero items drops off automatically and reappears when something lands.

Each anchor's section is a copy of its `{slug} queries.md` — the per-anchor queue file. **That file is mechanically rendered** (`queries-render.py`, on every state change): you never hand-edit it. To change what it shows, the agent edits the *source* — a backlog row or a feature doc's `## Open Questions` — and the render follows.

Questions themselves live at their source, in one of two places:

- **Document-attached** — a question about a specific feature/PRD lives in that doc's `## Open Questions` H2, directly below the H1.
- **Backlog-attached** — a row with no doc carries its own question inline; the queue file surfaces it with a pending-count.


## How agents invoke it

You rarely invoke `/ask` yourself — parent skills do (`/feature`, `/groom`, `/crank`, `/code plan`) when they have decisions to park. Direct forms:

- `/ask` — sweep the anchor: consolidate every open question into `{slug} queries.md` and glance it.
- `/ask --doc <path> <q1> [<q2> …]` — author numbered questions straight into that doc's `## Open Questions` block (used by other skills).


## Question format

Every question carries an explicit recommendation strength, so you can scan many at once and rubber-stamp the confident ones. Each option is on its own line; the recommendation is always present (even when `None`).

| Strength | What you should do |
|---|---|
| **Strong** | Rubber-stamp unless you disagree. |
| **Lean** | Quick read; consider before accepting. |
| **None** | Genuine uncertainty — apply your judgment. |

A question only reaches you if the agent genuinely can't answer it: reversible/self-checkable calls are decided and recorded, never asked (that's the whole point).


## How you respond

The shorthand is uniform. `F005 Q4: yes` resolves Q4 in F005's feature doc and archives it. After you name a feature once, bare `Q4: yes` sticks to it. The agent records the answer at its source and the render trims it from the queue on the next pass.


## Active vs Parking mode

**Active** — you're engaging now ("let's design X"): the agent **glances** the file (opens it at you). **Parking** — you've deferred ("put it on the backlog"): the agent files the questions but does **not** glance; they wait for you on `[[Q]]`. When ambiguous the default is parking — an unwanted glance interrupts deferred work, while a missed glance costs nothing (you re-engage by opening `[[Q]]`).


## Cross-references

- `[[Q]]` — the vault-wide dashboard, kept current by the render.
- [[Query PRD]] — the design; [[skills/ask/SKILL.md|SKILL]] — the agent-loaded runbook.
