---
description: "design surface for /query — routes to the shared resolution-layer PRD and the query rules"
---
# SKL Query Design

| -[[SKL Query Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [[SKL Query]] → [SKL Query Design](hook://p/SKL%20Query%20Design)<br>: design surface for `/query` |
| --- | --- |

`/query`'s design is **shared with `/groom`** — the two are one **resolution layer** (groom plans the backlog frontier; query consolidates the irreducible residue into the asking surface), so their design lives in a single PRD rather than two that drift.

## Where the design lives

- **[[Query PRD]]** — **the design home. Start here.** The shared resolution-layer PRD for both `/query` and `/groom`: the goals, the `F` / `T` / `M` / `R` work-item-identity model, the groom frontier, the five groomed states, the five-part question bar, and how triage / groom / query compose into one autonomous machine. (Named "Query PRD" for link stability; read it as the resolution-layer PRD.)
- **[[FCT Query]]** — the **facet**: what a valid `{NAME} queries.md` file must look like — the `R-query` ruleset (five fixed sections, the `V<n>` / `Q<n>` handles, and the 🚨 hard requirement that every named artifact is a live wiki-link). This is the format `/audit doc` and the on-write hook enforce.
- **[[facets/FCT Track/Backlog\|FCT Backlog]]** — the `R-backlog` ruleset and the **five groomed states → body-contract → rule** table (states 2/4/5 — Questions, Verify, Watching — are the residue `/query` surfaces).
- **[[skills/workflow/SKILL.md\|workflow — the state graph]]** — the canonical **state graph**: every bracket, the Definition of Ready, and the transitions both skills cite.
- **[[skills/query/SKILL.md\|SKILL]]** — the `/query` **runbook** (the procedure the skill follows, not the design rationale).

## User-facing reference

- **[[SKL Query]]** — the plain-language "what `/query` does for me" page.
