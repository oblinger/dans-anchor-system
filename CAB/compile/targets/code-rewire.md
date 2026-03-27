# Compile: code-rewire

## Output
~/.claude/skills/code/code-rewire.compiled.md

## Sources

Read these files and extract the structural requirements:

- `~/.claude/skills/CAB/cab-parts/CAB Anchor Page.md` — dispatch table format, standard row sequence, frontmatter requirements
- `~/.claude/skills/CAB/cab-parts/CAB Folder.md` — marker file, folder naming
- `~/.claude/skills/CAB/cab-parts/CAB Docs.md` — Docs dispatch page structure
- `~/.claude/skills/CAB/cab-parts/CAB Dev Dispatch.md` — Dev dispatch page structure
- `~/.claude/skills/CAB/cab-parts/CAB Plan Dispatch.md` — Plan dispatch page structure
- `~/.claude/skills/CAB/cab-parts/CAB User Dispatch.md` — User dispatch page structure
- `~/.claude/skills/CAB/cab-parts/CAB Claude.md` — CLAUDE.md requirements
- `~/.claude/skills/CAB/cab-types/Code Anchor.md` — code-specific files (Code symlink, Dev, User, Files.md)
- `~/.claude/skills/CAB/cab-types/Topic Anchor.md` — topic-specific structure
- `~/.claude/skills/CAB/cab-types/Skill Anchor.md` — skill-specific structure (SKILL.md)

## How to Compile

For each anchor type, produce a checklist organized by relative file path. Under each path, list every requirement as a checkbox item. The agent executing `/code rewire` will:

1. Detect the anchor type
2. Jump to the section for that type
3. Walk down the checklist file-by-file

Group the checklist into sections:
- **All Types** — checks that apply regardless of type
- **Code Anchor** — additional checks for code type
- **Topic Anchor** — additional checks for topic type
- **Skill Anchor** — additional checks for skill type

Under each file path heading, list:
- Whether the file must exist
- Required frontmatter fields
- Required content (dispatch table rows, links, breadcrumbs)
- Required structure (H1, tables, sections)

## Extras

These rules don't appear explicitly in any CAB spec but must be in the compiled output:

- Wiki-links in tables: always escape pipe as `\|` — `[[target\|alias]]` not `[[target|alias]]`
- Blank line before every markdown table or it won't render
- Frontmatter must have both `cab-type:` and `description:`
- Breadcrumb format: `:>> [[parent]] → [Name](hook://p/Name%20Here)`
- Dispatch table header: `-[[RID]]-` in first cell, `+: description` in second cell
- Standard rows order: External, User, Plan, Execute, Dev, Research — verify against [[CAB Anchor Page]] reference example, not from memory
- Project-specific rows go AFTER standard rows
- `.anchor/config.yaml` must have `rid:` and `type:` at minimum
- Dispatch pages link to ALL their children — no orphan files in any folder
- Every subfolder that has files needs a dispatch page
