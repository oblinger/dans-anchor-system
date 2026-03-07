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
~/.claude/skills/{name}/
├── SKILL.md                      Entry point — metadata, dispatch, quick reference
├── {name}-{action}.md            Action workflow files (one per action)
├── {name}-{topic}.md             Topic/reference files (optional)
├── {name}.md                     Anchor page for Obsidian navigation
├── {TLC}.md                      TLC alias (optional, if TLC ≠ folder name)
├── {name}-{sub}/                 Reference data sub-folders (optional)
│   └── *.md                      Individual spec/reference files
└── *.py                          Scripts (optional)
```

## Anchor Page and TLC

The main page for a skill anchor is `SKILL.md`, not the anchor page. The anchor page and TLC file are navigation aids that point to `SKILL.md`.

### Anchor page (`{name}.md`)

Every skill folder has an anchor page matching the folder name. It contains a wiki-link to the SKILL file:

```
(See [[{name}/SKILL|{NAME} Skill]])
```

The wiki-link format `[[{name}/SKILL|display text]]` links to `SKILL.md` inside the skill's folder. The display text is the human-readable skill name.

### TLC file (`{TLC}.md`)

If the skill has a TLC that differs from the folder name, create a separate TLC file with the same wiki-link:

```
(See [[{name}/SKILL|{NAME} Skill]])
```

For example, the research skill has folder name `research` and TLC `RSH`. Both `research.md` and `RSH.md` contain the same link to `[[research/SKILL|Research Skill]]`.

If the TLC matches the folder name (e.g., `cab/` with TLC `CAB`), only one file is needed.

## Examples

**Minimal** (research) — `SKILL.md` + 2 action files + anchor page + TLC

**Moderate** (dev) — `SKILL.md` + 5 action files + 1 topic file + anchor page

**Complex** (cab) — `SKILL.md` + 8 action files + 3 sub-folders (parts, rules, types) with 40+ reference files
