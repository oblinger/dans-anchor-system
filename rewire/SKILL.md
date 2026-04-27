---
name: rewire
description: >
  Idempotent structural repair for any anchor. Ensures all files are linked,
  dispatch tables are wired, and the skeleton is consistent.
  Use when the user says: "rewire", "fix the structure", "wire it up",
  "check the wiring", "fix dispatch tables", "rewire the backlog",
  "rewire the dev docs for MUX".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Rewire

Idempotent structural repair for any anchor. Ensures all files are linked, dispatch tables are wired, and the skeleton is consistent. Safe to run anytime — only adds, never deletes.

## Usage

| Form | Meaning |
|------|---------|
| `/rewire` | Full rewire — run the entire checklist for the current anchor |
| `/rewire the <facet>` | Focused rewire — ensure the named facet exists, is in the right location, and is wired into its parent dispatch tables. Create any missing intermediate structure. |
| `/rewire the <facet> for <anchor>` | Focused rewire on a specific anchor (when not obvious from context) |

### Focused Rewire (`rewire the <facet>`)

The named item must be a CAB facet. The goal is: **every dispatch table from the anchor page down has the correct rows with the correct entries for this facet.**

**CRITICAL: Check the tables, not just the files.** The most common failure is confirming the facet file exists and reporting "done" without checking whether the dispatch tables have the correct rows. You must verify and fix every table in the chain.

#### Canonical dispatch table format

This is the reference example. Every anchor page dispatch table must follow this structure. When rewiring a facet, match the row format exactly — correct row name, correct position, correct wiki-link format for the label, correct entries.

<!-- compiled:start source=CAB/cab-facets/CAB-slug-Page-reference -->

```
| -{NAME}-                             | ><br>:                                                                                                                                    |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| External                             | [Repo](https://github.com/oblinger/repo), [Project Page](https://oblinger.github.io/gitproj/repo/)                                      |
| [[{NAME} User/{NAME} User\|User]]+  | [[{NAME} User Guide\|User Guide]], [[{NAME} Cards\|Cards]]                                                                               |
| [[{NAME} Plan\|Plan]]+              | [[{NAME} PRD\|PRD]], [[{NAME} System Design\|System Design]], [[{NAME} UX Design\|UX]], [[{NAME} Features\|Features]], [[{NAME} Discussion\|Discussion]] |
| [[{NAME} Plan\|Execute]]            | [[{NAME} Inbox\|Inbox]], [[{NAME} Open Questions\|Open Q]], [[{NAME} Backlog\|Backlog]], [[{NAME} Roadmap\|Roadmap]]                     |
| [[{NAME} Dev/{NAME} Dev\|Dev]]+     | [[{NAME} Files\|Files]], [[{NAME} Architecture\|Architecture]]                                                                           |
| Research                             | [[{NAME} Research\|Research]], [[{NAME} References\|References]]                                                                         |
| ...                                  |                                                                                                                                           |
```

**Standard row order:** External, User, Plan, Execute, Dev, Research. Omit rows not relevant to this anchor. Do not reorder. Do not append new rows at the end — insert in the correct position.

**Row label format:**
- External, Research — plain text
- User — `[[{NAME} User/{NAME} User\|User]]+`
- Plan — `[[{NAME} Plan\|Plan]]+`
- Execute — `[[{NAME} Plan\|Execute]]` (links to Plan folder, no `+`)
- Dev — `[[{NAME} Dev/{NAME} Dev\|Dev]]+`

**Entry format:** Each entry is `[[{NAME} FacetName\|Short Name]]` — full wiki-link with escaped pipe and short display alias.

<!-- compiled:end -->

#### Steps

1. **Look up the facet** — read the matching file in `~/.claude/skills/CAB/cab-facets/` to find which row it belongs in and what its entry should look like

2. **Fix the anchor page dispatch table** — open `{NAME}.md`. Match the table against the canonical format above. Ensure the correct row exists in the correct position with the facet entry in it. If the row is missing, add it in the right position — not at the end.

3. **Fix intermediate dispatch tables** — if the facet lives in a subfolder (e.g., `{NAME} Plan/`), ensure the subfolder and its dispatch page exist, and that dispatch page has a row with the facet linked in it.

4. **Create the facet file** — if it doesn't exist, create it following the facet spec. Unlike full rewire, focused rewire DOES create the target file.

## What Rewire Does NOT Do

- Does not modify file content — only touches dispatch tables and links
- Does not delete anything — purely additive

## Runbook (full rewire)

1. Detect anchor traits from `.anchor` (`traits:` list) or frontmatter `cab-traits:`
2. Execute the **All Types** checklist below
3. Execute the section for EACH of this anchor's traits (e.g., Code, Topic, Skill)
4. Execute the **Universal Rules** checklist below
5. Report what was fixed

<!-- compiled:start source=CAB/compile/targets/code-rewire.md -->

# All Types

## .anchor

- [ ] File exists at anchor root
- [ ] Has `slug:` field (or derived from title/folder name)
- [ ] Has `traits:` field (list of trait names)

## {FolderName}.md (marker file)

- [ ] File exists with name matching the folder name exactly
- [ ] If slug differs from folder name, contains `(See Anchor [[{NAME}]])`
- [ ] If folder name IS the anchor name, this file serves as the anchor page

## {NAME}.md (anchor page)

- [ ] Has H1 heading: `# {slug} — {FolderName}` when slug differs from folder name, or `# {NAME}` when they match
- [ ] Has YAML frontmatter with `cab-traits:` field (list)
- [ ] Has YAML frontmatter with `description:` field
- [ ] Has dispatch table with `-[[{NAME}]]-` in first cell of header row
- [ ] Dispatch table header second cell has `>` (breadcrumb) and/or `:` (description), separated by `<br>` (e.g., `><br>: short description`)
- [ ] Blank line exists before the dispatch table
- [ ] All wiki-link aliases inside tables use escaped pipe: `[[target\|alias]]`
- [ ] Standard rows appear in this order: External, User, Plan, Execute, Dev, Research
- [ ] Project-specific rows appear AFTER all standard rows
- [ ] Rows that do not apply to this anchor's traits are omitted entirely (not left empty)
- [ ] User row label links to `[[{NAME} User/{NAME} User\|User]]` with `+` suffix if folder exists
- [ ] Plan row label links to `[[{NAME} Plan\|Plan]]` with `+` suffix if folder exists
- [ ] Execute row label links to `[[{NAME} Plan\|Execute]]`
- [ ] Dev row label links to `[[{NAME} Dev/{NAME} Dev\|Dev]]` with `+` suffix if folder exists
- [ ] External and Research row labels are plain text (not wiki-links)
- [ ] Table ends with a separator row to enable auto-management of remaining children: `---` (alpha), `^^^` (reverse alpha), `...` (compact), or `+++` (alpha with grandchildren)
- [ ] Every file listed in inline row links actually exists

## {NAME} Docs/{NAME} Docs.md

- [ ] File exists if `{NAME} Docs/` folder exists
- [ ] Has dispatch table linking to Plan, Dev, User subfolders
- [ ] Links to every subfolder dispatch page that exists

## {NAME} Docs/{NAME} Plan/{NAME} Plan.md

- [ ] File exists if `{NAME} Plan/` folder exists
- [ ] Has dispatch table with `-[[{NAME} Plan]]-` in first cell
- [ ] Dispatch table header second cell has `><br>:` markers (breadcrumb + description)
- [ ] Table ends with a separator row (`---` or `^^^`) for auto-management
- [ ] Links to every `.md` file in the Plan folder (PRD, System Design, UX Design, Discussion, Roadmap, Backlog, Inbox, Open Questions, Research, Features)
- [ ] `{NAME} Features/` folder exists under Plan with `{NAME} Features.md` index inside it
- [ ] Features index links to all dated feature files (reverse chronological)
- [ ] Only links files that actually exist — no dead links
- [ ] No orphan files in Plan folder missing from dispatch table

## {NAME} Docs/{NAME} Dev/{NAME} Dev.md

- [ ] File exists if `{NAME} Dev/` folder exists
- [ ] Has dispatch table with `-[[{NAME} Dev]]-` in first cell
- [ ] Dispatch table header second cell has `><br>:` markers (breadcrumb + description)
- [ ] Table ends with a separator row for auto-management
- [ ] Files row appears first in body rows
- [ ] Architecture row appears second in body rows
- [ ] Module doc rows are grouped by source folder with bold folder headers (`**folder/**`)
- [ ] Links to every module doc `.md` file in the Dev folder
- [ ] No orphan files in Dev folder missing from dispatch table

## {NAME} Docs/{NAME} User/{NAME} User.md

- [ ] File exists if `{NAME} User/` folder exists
- [ ] Has dispatch table with `-[[{NAME} User]]-` in first cell
- [ ] Dispatch table header second cell has `><br>:` markers (breadcrumb + description)
- [ ] Table ends with a separator row for auto-management
- [ ] Links to every `.md` file in the User folder
- [ ] No orphan files in User folder missing from dispatch table

## CLAUDE.md

- [ ] File exists at anchor root (if anchor is used with Claude Code)
- [ ] Contains mission statement
- [ ] Contains working directory declaration
- [ ] Contains key files section listing important files and purposes
- [ ] Contains commands section with relevant shell commands
- [ ] If agentic project: first line is `You are the Pilot for the {PROJECT} project. Role: ~/.claude/skills/role/role-pilot.md`
- [ ] Exists at anchor root only — not duplicated inside the repo

## General dispatch integrity

- [ ] Every subfolder containing files has a dispatch page
- [ ] Every dispatch page links to ALL its children — no orphan files
- [ ] Walking from `{NAME} Docs.md` reaches every `.md` file in the Docs tree

---

# Code Anchor

## {NAME}.md (anchor page — code-specific)

- [ ] Has External row with repo URL
- [ ] Has Dev row linking to Dev dispatch page with `+` suffix
- [ ] Has User row with `+` suffix if User folder exists

## Code / .git/

- [ ] `.anchor` has a `code:` key that resolves to an existing directory (absolute, or relative to anchor root; `.` for inline)

## README.md

- [ ] Exists in the repo root

## CLAUDE.md (code-specific)

- [ ] Exists at anchor root only — NOT inside the repo

## {NAME} Docs/{NAME} Dev/

- [ ] Folder exists with dispatch page `{NAME} Dev.md`
- [ ] `{NAME} Files.md` exists inside Dev folder
- [ ] Files.md lists source files with wiki-links to module docs where they exist
- [ ] Dev dispatch page links to all module docs in the Dev folder

## {NAME} Docs/{NAME} User/

- [ ] Folder exists with dispatch page `{NAME} User.md`

## justfile (if present in repo)

- [ ] Has at minimum a `test` recipe

---

# Topic Anchor

## {NAME}.md (anchor page — topic-specific)

- [ ] Functions as a routing hub — links to sub-topics or content pages

## {NAME} Docs/

- [ ] Folder exists with dispatch page
- [ ] `{NAME} Plan/` subfolder exists with planning docs

## Conditional structure (create only when another trait requires)

- [ ] `{NAME} Dev/` folder — create only when Code trait is present
- [ ] `{NAME} User/` folder — create only when Code trait is present
- [ ] `.anchor` `code:` key — add only when the `code` trait is present

---

# Skill Anchor

## SKILL.md

- [ ] File exists as the entry point (replaces standard anchor page)
- [ ] Has YAML frontmatter with `name:` field
- [ ] Has YAML frontmatter with `description:` field
- [ ] Has YAML frontmatter with `tools:` field
- [ ] Has YAML frontmatter with `user_invocable:` field
- [ ] Contains Actions dispatch table mapping `/skill action` to workflow files
- [ ] Every action file referenced in the dispatch table exists
- [ ] Links to user docs: `User docs: [[SKL {Name} Guide]]` (if user docs exist)

## File naming

- [ ] All files use lowercase hyphenated names: `{name}-{action}.md`
- [ ] No Title Case file names inside the skill folder

## Conditional structure (create only when another trait requires)

- [ ] Standard `{NAME}.md` anchor page — create only when another trait requires it (SKILL.md replaces it by default)
- [ ] `{NAME} Docs/` folder — create only when another trait requires it
- [ ] `CLAUDE.md` — create only when another trait requires it (SKILL.md replaces it by default)
- [ ] `{FolderName}.md` marker file — create only when another trait requires it (SKILL.md is the marker by default)

## SKA project anchor (if complex skill)

- [ ] Lives under `Skill Agent/{NAME}/` — separate from the skill folder
- [ ] Has `{NAME}.md` anchor page
- [ ] Has `{NAME} Docs/{NAME} Plan/` with planning docs

---

# Universal Rules

- [ ] Wiki-links in tables: always escape pipe as `\|` — `[[target\|alias]]` not `[[target|alias]]`
- [ ] Blank line before every markdown table or it will not render
- [ ] Frontmatter must have both `cab-traits:` (list) and `description:`
- [ ] H1 heading: `# {slug} — {FolderName}` when slug differs from folder name, or `# {NAME}` when they match
- [ ] Dispatch table header: `-[[{NAME}]]-` in first cell, `><br>:` markers in second cell
- [ ] Dispatch table separator row: `---`, `^^^`, `...`, or `+++` in left cell enables auto-management below
- [ ] Per-row `+` suffix on wiki-link rows (e.g., `[[Name]]+`) to show grandchildren for that row
- [ ] Standard rows order: External, User, Plan, Execute, Dev, Research
- [ ] Project-specific rows go AFTER standard rows
- [ ] `.anchor` file must exist (can be empty — properties derive from folder name)
- [ ] Dispatch pages link to ALL their children — no orphan files
- [ ] Every subfolder that has files needs a dispatch page
- [ ] Every markdown file and folder inside an anchor is prefixed with `{NAME}`
- [ ] Rewire only adds missing links and fixes structure — never deletes content
- [ ] Rewire does not create missing files — only links existing ones
- [ ] Rewire does not modify file content — only dispatch tables and Files tree

<!-- compiled:end -->
