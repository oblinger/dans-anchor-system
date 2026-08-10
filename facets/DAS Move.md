---
description: "`/move` relocates an anchor folder to a new path and updates every path-dependent system that indexes it — HookAnchor, Claude Code session history, hardcoded paths inside the anchor's own configs, …"
---

| -[[DAS Move]]- | → [[DAS]] → [[FCT]] → [DAS Move](hook://p/DAS%20Move)  |
| --- | --- |
| Related | [[DAS Migrate]],  [[DAS Install]],  [[DAS Anchor]],  [[DAS Anchor Page]],   |
| Rules | [[R-fct-move]],   |
| Examples | [[DAS Move\|skill runbook]],  [[SKA move\|managing anchor]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Move
A move relocates an anchor's folder and updates every system that references it by path.

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

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative contract is the body above; step-by-step move mechanics live in the `/cab move` SKILL.md runbook, never here.)*

- **Inclusion test** — only content describing *what a move IS* (the conceptual steps, the systems involved, the boundary against migrate / fix-session) belongs here; per-skill mechanics, edge cases, and command syntax go in the respective skill files.
- **Step list is the contract** — the numbered § What a Move Involves list is referenced by `/cab move` and downstream skills; add new steps at the end or with an explicit sub-number, never renumber or reorder.
- **Boundary discipline** — Move vs. Migrate vs. Fix Session is the load-bearing distinction; preserve the Related Skills table and the When to Use Each guidance so users land on the right verb, and add a row for any new related skill rather than blurring the existing definitions.
- **Linking convention** — reference skills in slash-command form in backticks (`/cab move`, `/cab migrate`, `/fix session`), not as wiki-links to SKILL.md files.
