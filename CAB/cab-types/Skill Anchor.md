# Skill Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Claude Code skill groups — organized collections of action workflows, reference data, and scripts that live inside `~/.claude/skills/`. Each skill folder is a self-contained anchor whose entry point is `SKILL.md`.

## Deltas from Base

- **No `{NAME} Docs/`** — no planning docs subfolder
- **No repository** — lives inside the skills folder, not its own repo
- **No CLAUDE.md** — `SKILL.md` serves as both identity and configuration
- **No `{CAB Folder}.md` marker** — `SKILL.md` is the marker and entry point
- **`SKILL.md` frontmatter** — YAML with `name`, `description`, `tools`, `user_invocable` (required by Claude Code)
- **Dispatch table** — `SKILL.md` contains an Actions table mapping `/skill action` to workflow files
- **File naming** — lowercase, hyphenated: `{name}-{action}.md`, not Title Case
- **Optional sub-folders** — reference data organized by kind (parts, rules, types, scripts)

## Structure

```
~/.claude/skills/
├── SKL User Docs/
│   ├── SKL User Guide.md        Central user guide
│   └── SKL {Name} Guide.md     User docs for this skill (if needed)
├── {name}/
│   ├── SKILL.md                  Entry point — metadata, dispatch, quick reference
│   ├── {name}-{action}.md        Action workflow files (one per action)
│   ├── {name}-{topic}.md         Topic/reference files (optional)
│   ├── {name}-{sub}/             Reference data sub-folders (optional)
│   │   └── *.md                  Individual spec/reference files
│   └── *.py                      Scripts (optional)
```

## Anchor Page and RID

The main page for a skill anchor is `SKILL.md`, not an anchor page file.

**⚠️ Do NOT create a `{name}.md` marker file in the skill folder** if the skill has a SKA project anchor with the same name (e.g., `DEV/DEV.md` in Skill Agent). On macOS case-insensitive filesystems, `dev.md` and `DEV.md` are the same to Obsidian's link resolver, causing ambiguity.

The SKA project anchor IS the anchor for `[[{NAME}]]` links. The skill's `SKILL.md` is reached via `[[{name}/SKILL]]`.

### RID file (`{RID}.md`)

If the skill has a RID that differs from the folder name AND doesn't collide with a SKA project name, a RID alias file can be created. Otherwise, use the SKA project anchor as the RID destination.

## User Docs

User-facing documentation lives in the `SKL User Docs/` folder at the skills repo root — one file per skill, prefixed with `SKL`:

```
~/.claude/skills/
├── SKL User Docs/
│   ├── SKL User Guide.md      Central user guide — links to all skill docs
│   ├── SKL Audit Guide.md     User docs for /audit
│   ├── SKL Rule Guide.md      User docs for /rule
│   └── ...
├── audit/
│   └── SKILL.md               Lean recipe (links to SKL Audit Guide)
```

Each SKILL.md links to its user docs at the top: `User docs: [[SKL {Name} Guide]]`

When creating a new skill, also create `SKL User Docs/SKL {Name} Guide.md` if the skill needs user documentation. Add a row to `SKL User Guide.md`.


## SKA Project Anchor (for complex skills)

Skills that need design planning, PRDs, or design discussions get a **project anchor** under `Skill Agent/`:

```
Skill Agent/
└── {NAME}/                          SKA project anchor (design docs)
    ├── {NAME}.md                    Anchor page
    └── {NAME} Docs/
        └── {NAME} Plan/
            ├── {NAME} Plan.md
            ├── {NAME} PRD.md
            └── {NAME} Discussion.md
```

This separates:
- **Skill folder** (`~/.claude/skills/{name}/`) — the skill itself + user docs. Ships to users.
- **SKA project** (`Skill Agent/{NAME}/`) — design thinking, PRDs, research. Stays in vault.

The skill folder is lowercase (`cab`, `dev`, `ctrl`). The SKA project is uppercase RID (`LINT`, `DEV`, `CTRL`). They live in different directories so no filesystem collision.


## Examples

**Minimal** (research) — `SKILL.md` + 2 action files + anchor page + RID

**Moderate** (dev) — `SKILL.md` + 5 action files + 1 topic file + anchor page + reference files

**Complex** (cab) — `SKILL.md` + 8 action files + 3 sub-folders (parts, rules, types) + User Docs + SKA project with PRD and design discussions + Python scripts

## Audit

Type-specific structure checks for Skill Anchors.

### Required files
- `SKILL.md` with frontmatter (name, description, tools, user_invocable)
- Action files referenced from the SKILL.md dispatch table

### Not expected
- No standard anchor page (SKILL.md replaces it)
- No `{NAME} Docs/` folder (skill files ARE the docs)
