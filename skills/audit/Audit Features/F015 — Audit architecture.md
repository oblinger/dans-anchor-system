---
description: "Architecture-doc validation: diagram-then-table shape + wiki-link integrity. Shipped, auto-run by /architect."
---

# [[Audit]] · F015 — Audit architecture

## Summary

`/architect` ships new and updated architecture docs but has no validator — drift accumulates silently. The user has named two structural rules that should be mechanically enforced:

- **R1** — Every subsystem doc, including the main `<NAME> Architecture.md`, must begin with a block diagram at the top of the body (after H1 + optional brief intro), followed immediately by a table listing all components shown in that diagram. The diagram-then-table pattern is the doc's contract with the reader: "here's the shape, here's the legend."
- **R2** — Every component reference in those tables must be a wiki-link. Plain-text module names that resolve to a vault doc are violations — the reader needs to click through, and the audit needs to verify the link integrity.

This feature commissions a new audit-family member, `/audit architecture`, on the same wiring pattern as `/audit q` / `/audit markdown` / `/audit docs`: a standalone skill that `/architect` auto-invokes as its last step, but that can also be invoked independently.


## Design

### Rules (v1)

| ID | Rule | Auto-fix? |
|---|---|---|
| **A1** | Every reachable Architecture doc must contain a block diagram in one of the accepted formats (Mermaid fence OR image embed) within the first 30 lines after H1. | No (manual fix — agent or user adds diagram). |
| **A2** | The block diagram must be followed (within 5 lines, allowing blank-line spacing) by a markdown table. | No (manual fix). |
| **A3** | Every cell in the component table that names a vault file (basename match) must be a wiki-link `[[X]]` rather than plain text — except cells tagged `[ext: <name>]` for intentional external refs. | Yes — wrap matching basenames in `[[...]]` if `X.md` exists exactly once in the vault index. Ambiguous matches (multiple `X.md` in the vault) → report-only. |
| **A4** | The component table must follow the diagram-then-table pair; an Arch doc with EITHER a diagram OR a table but not both (in order) violates the shape rule. | No (manual). |

### Detection — what counts as a subsystem doc

Reachability from each anchor's main `<NAME> Architecture.md`, walked transitively via wiki-links to docs whose basename matches the same arch-doc pattern (`<X> Architecture` / `<X> Arch`). The walk terminates at non-arch docs. The main Architecture doc is included.

Implementation: reuses `audit-q.py`'s `links_in_file` + `headings_in` primitives via Python import.

### Diagram format

- **Mermaid code fence:** ```` ```mermaid ... ``` ```` — detected by the language tag on the fence.
- **Image embed:** `![[<name>.svg]]`, `![[<name>.png]]`, `![[<name>.excalidraw]]` — detected by the `![[X.<ext>]]` embed shape with an image/diagram extension.

The "first 30 lines after H1" gives writers room for a brief intro paragraph (1-3 lines) before the diagram, but no more — "at the top" was the user's explicit framing.

### Component table

Right after the diagram (within 5 lines), the doc must contain a markdown table. Recommended shape — but the audit doesn't enforce column structure beyond "is a table":

```text

| Component | Role | Notes |
|---|---|---|
| [[ComponentA]] | Renders ... | Owns the dispatch loop |
| [[ComponentB]] | Coordinates ... | |

```

### Wiki-link integrity in the table

For each cell of the component table, the audit:

1. Splits the cell into tokens.
2. For each token that exactly matches the stem of a `.md` file in the vault index AND isn't already inside a `[[...]]` AND isn't inside an `[ext: ...]` tag → flag as a violation.
3. Auto-fix when the match is unambiguous (exactly one `X.md` in the vault); report-only on ambiguous (multi-anchor) basenames.

### Where the audit fires

A standalone `/audit architecture` skill, auto-invoked as the last step of every `/architect` sub-skill. The audit's output is a list of findings; non-zero findings DO NOT block `/architect` from minting — they're surfaced as report items, and severely broken docs (no diagram at all) become a backlog row `[Ready]` so the agent or user can address them out-of-band.

### Implementation

- `~/.claude/skills/audit/scripts/audit-architecture.py` — the validator. Reuses `audit-q.py` primitives via `import` (audit-q supports this via `sys.modules["audit_q"] = mod`).
- `~/.claude/skills/audit/audit-architecture.md` — the skill runbook.
- `/architect` SKILL.md gains a post-condition step: invoke `/audit architecture --scope reach` after every sub-skill run.
- CLI: `audit-architecture [--scope reach|anchor|file|all] [--anchor NAME] [--file PATH] [--fix] [--dry]`. Default scope is `reach`.
- Findings emitted with codes `A1`–`A4`; integrates with audit-family's standard report shape.


## Status

Implementing — all 5 design Qs accepted 2026-05-26 (Lean recommendations all rubber-stamped). Mint in progress.


## Resolved

### Q1 — Skill or tail-pass?
**Choice:** (A) Standalone `/audit architecture` skill auto-invoked by `/architect` (and its sub-skills).

Matches the audit family pattern (`/audit q`, `/audit markdown`, `/audit docs` all live as standalone skills with auto-wiring post-conditions). Allows independent re-runs when the user fixes one doc by hand. Failing the audit doesn't block `/architect` minting — issues surface as report items / backlog rows, not gates.

### Q2 — Subsystem-doc detection
**Choice:** (D) Reachability — start at each anchor's main `<NAME> Architecture.md` and walk wiki-links to docs whose basename matches `<X> Architecture` / `<X> Arch` until closure.

Matches `/architect`'s existing folder-anchor model. The walker stays exactly in the same dispatch graph the agent already uses. Avoids per-file marker drift and false-positives on non-arch docs that happen to live in an `Architecture/` folder (e.g., `Versions/`).

### Q3 — Diagram format
**Choice:** (C) Mermaid code fence OR image embed accepted.

Matches the user's existing usage. Each subsystem picks what reads best — Mermaid for small graphs, image embed (e.g., Excalidraw export) when the graph gets too big to fit in one screen of Mermaid (the user explicitly named this case 2026-05-26).

### Q5 — Wiki-link integrity scope
**Choice:** (C) Every basename in any cell must be a wiki-link, with `[ext: <name>]` opt-out tag for intentional external refs.

The user said "all of the linkages should be wiki-links" — strict on internal refs. The opt-out tag prevents false-positives on legitimate external names (third-party services, language types, etc.).

### Q8 — When the audit fires
**Choice:** (B) Auto-invoked at the end of `/architect` and every sub-skill. No wider auto-wiring (skip `/triage`, `/groom`).

Architecture docs are touched almost exclusively through `/architect`. Wider auto-wiring would add noise to every `/triage` run without value. Manual invocation always available via `/audit architecture` as a backstop.

### Main Architecture doc obeys the same rule
**Choice:** Yes — `<NAME> Architecture.md` itself must have a block diagram (showing subsystems) + component table (listing them).

Per the user's explicit framing in the commissioning message: *"every subsystem, including the main architecture, needs to begin with a block diagram right at the top. followed by a table of all of the components within that diagram right below it."* The main Arch doc's table CAN double as its existing subsystem dispatch table (the table is already there in current docs; the audit just verifies the diagram precedes it).

### Strictness — diagram and table at the top, not anywhere
**Choice:** Strict-with-intro-tolerance. Diagram must appear within the first 30 lines after H1 (allowing a 1-3 line intro paragraph); table must follow within 5 lines of the diagram.

The user's framing was "right at the top" — strict was the clear intent. The 30-line / 5-line buffers give writers minimal room for orienting prose without letting the diagram drift into the middle of the doc. Auto-decided per F068: visible (the agent or user sees a violation immediately when opening the doc), low recoverability (loosening the threshold later is a one-number change).

### Auto-fix policy — mechanical wraps only, no scaffold generation
**Choice:** Auto-fix wraps unambiguous basename references in `[[...]]` when a unique vault match exists. Does NOT auto-generate missing diagrams or tables — those require human/agent design judgment.

Auto-generating a "scaffold" diagram would produce wrong content that would then need to be fixed anyway; the audit's value is identifying the gap, not filling it with junk. Wrap-in-brackets is mechanically safe — same operation as `/audit q`'s wiki-link auto-fix passes. Auto-decided per F068: visible, low recoverability.
