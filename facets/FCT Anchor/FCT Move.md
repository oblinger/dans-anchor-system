---
description: Moving an anchor to a new location — concept and related skills
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Move](hook://p/FCT%20Move)

# FCT Move
A move relocates an anchor's folder and updates every system that references it by path.

**Related:** [[FCT Migrate]],  [[FCT Install]],  [[FCT Anchor]],  [[FCT Anchor Page]]
**Examples:** [[SKL Move\|skill runbook]],  [[SKA move\|managing anchor]]

**TLDR** — A Move is a multi-step orchestrated operation: physical folder relocation + HA reindex + Claude session rename + path scan. Distinct from Migrate (type change) and Fix Session (session-only repair). Cardinality: **one per anchor** (an anchor has at most one current location; move is a one-time operation per anchor per event).

## What a Move Involves

1. **Physical move** — relocate the folder (never copy — duplicates cause wiki-link ambiguity)
2. **HookAnchor reindex** — update the command's path so `ha -p` resolves correctly
3. **Claude session migration** — rename the Claude Code project directory so sessions follow the anchor
4. **Path scan** — find and update hardcoded paths in config files, scripts, and docs
5. **Docs rebuild** — if the anchor publishes docs, rebuild with the new base path
6. **slug index update** — if the anchor has a slug, verify the index entry points to the new location

## Related Skills

| Skill | Role in a Move |
|-------|---------------|
| `/cab move` | The primary action — orchestrates the full move workflow (all 8 steps) |
| `/cab migrate` | Different concept — converts an anchor from one CAB type to another (e.g., Simple → Code). Not part of a move. |
| `/fix session` | Substep of `/cab move` — handles Step 3 (Claude session migration). Exists as a standalone skill for cases where only the session needs updating, but during a move it's called automatically by `/cab move`. |

## When to Use Each

- **Moving an anchor to a new folder** → `/cab move` (handles everything, including Claude migration)
- **Changing an anchor's type** (e.g., adding a code repo to a simple anchor) → `/cab migrate`
- **Only the Claude session path is wrong** (anchor already moved by other means) → `/fix session`

# RULESET R-fct-move
include::
description:: The rules every Move operation must satisfy — physical relocation, system reindex, and session migration in a single orchestrated pass.

### RULE R-fct-move-01 — Move is executed atomically via `/cab move` (checked)
A move is never performed piecemeal by hand; it is always orchestrated through the `/cab move` skill, which sequences all six steps in order.
**Check pattern:** no anchor whose location changed has a stale `ha -p` path (HA reindex was run).
**Tier:** checked

### RULE R-fct-move-02 — Physical relocation uses move, never copy (checked)
The folder is moved (renamed/relocated) rather than copied; the old location must not remain.
**Check pattern:** after a move, no duplicate folder exists at the old path.
**Tier:** checked

### RULE R-fct-move-03 — Claude session path is updated as part of the move (checked)
Step 3 (session migration) is always executed; it is not optional even when the old session directory appears functional.
**Check pattern:** the Claude Code project directory name matches the anchor's current on-disk path after the move.
**Tier:** sampled

### RULE R-fct-move-04 — Cardinality: one per anchor per move event (stated)
An anchor has at most one current location; each move event is a discrete, non-concurrent operation. Parallel moves of the same anchor are not supported.
**Check pattern:** no anchor has two in-flight move operations simultaneously.
**Tier:** stated

# BRIEF

- **This file is the CAB Move facet spec** — it defines the *concept* of moving an anchor (what steps a move entails, what systems must be updated) and routes to the skills that perform the work. It is authoritative for the move-workflow shape.
- **NOT a runbook and NOT an implementation** — step-by-step procedural detail for executing a move belongs in the `/cab move` SKILL.md runbook, not here. Keep this file conceptual; keep behavior in the skill.
- **Inclusion test** — only content that describes *what a move IS* (the conceptual steps, the systems involved, the boundary against migrate/fix-session) belongs here. Per-skill mechanics, edge cases, and command syntax go in the respective skill files.
- **Boundary discipline** — Move vs. Migrate vs. Fix Session is the load-bearing distinction; preserve the Related Skills table and the When to Use Each guidance so users land on the right verb. If a new related skill enters this space, add a row rather than blurring the existing definitions.
- **Step list is the contract** — the numbered "What a Move Involves" list is referenced by `/cab move` and downstream skills. Renumbering or removing a step silently breaks references; add new steps at the end or with an explicit sub-number, never reorder.
- **Linking convention** — skills are referenced as `/cab move`, `/cab migrate`, `/fix session` (slash-command form in backticks), not as wiki-links to SKILL.md files. Keep this consistent — readers scan for the slash form.
