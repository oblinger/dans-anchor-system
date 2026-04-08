---
description: Moving an anchor to a new location — concept and related skills
---

# CAB Move

Moving an anchor means relocating its folder and updating every system that references it by path. This is a multi-step operation that touches several systems.

## What a Move Involves

1. **Physical move** — relocate the folder (never copy — duplicates cause wiki-link ambiguity)
2. **HookAnchor reindex** — update the command's path so `ha -p` resolves correctly
3. **Claude session migration** — rename the Claude Code project directory so sessions follow the anchor
4. **Path scan** — find and update hardcoded paths in config files, scripts, and docs
5. **Docs rebuild** — if the anchor publishes docs, rebuild with the new base path
6. **RID index update** — if the anchor has a RID, verify the index entry points to the new location

## Related Skills

| Skill | Role in a Move |
|-------|---------------|
| `/cab move` | The primary action — orchestrates the full move workflow (all 8 steps) |
| `/cab migrate` | Different concept — converts an anchor from one CAB type to another (e.g., Simple → Code). Not part of a move. |
| `/cab migrate-claude` | Substep of `/cab move` — handles Step 3 (Claude session migration). Exists as a standalone skill for cases where only the session needs updating, but during a move it's called automatically by `/cab move`. |

## When to Use Each

- **Moving an anchor to a new folder** → `/cab move` (handles everything, including Claude migration)
- **Changing an anchor's type** (e.g., adding a code repo to a simple anchor) → `/cab migrate`
- **Only the Claude session path is wrong** (anchor already moved by other means) → `/cab migrate-claude`
