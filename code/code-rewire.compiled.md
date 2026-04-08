# /code rewire — compiled checklist

---

# All Types

## .anchor/config.yaml

- [ ] File exists at anchor root
- [ ] Has `rid:` field
- [ ] Has `traits:` field (list of trait names)

## {FolderName}.md (marker file)

- [ ] File exists with name matching the folder name exactly
- [ ] If RID differs from folder name, contains `(See Anchor [[{NAME}]])`
- [ ] If folder name IS the anchor name, this file serves as the anchor page

## {NAME}.md (anchor page)

- [ ] Has H1 heading: `# {RID} — {FolderName}` when RID differs from folder name, or `# {NAME}` when they match
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

- [ ] `Code` symlink exists and resolves to an existing directory (linked mode) OR `.git/` exists at anchor root (inline mode)

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
- [ ] `Code` symlink — create only when Code trait is present

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
- [ ] H1 heading: `# {RID} — {FolderName}` when RID differs from folder name, or `# {NAME}` when they match
- [ ] Dispatch table header: `-[[{NAME}]]-` in first cell, `><br>:` markers in second cell
- [ ] Dispatch table separator row: `---`, `^^^`, `...`, or `+++` in left cell enables auto-management below
- [ ] Per-row `+` suffix on wiki-link rows (e.g., `[[Name]]+`) to show grandchildren for that row
- [ ] Standard rows order: External, User, Plan, Execute, Dev, Research
- [ ] Project-specific rows go AFTER standard rows
- [ ] `.anchor/config.yaml` must have `rid:` and `traits:` at minimum
- [ ] Dispatch pages link to ALL their children — no orphan files
- [ ] Every subfolder that has files needs a dispatch page
- [ ] Every markdown file and folder inside an anchor is prefixed with `{NAME}`
- [ ] Rewire only adds missing links and fixes structure — never deletes content
- [ ] Rewire does not create missing files — only links existing ones
- [ ] Rewire does not modify file content — only dispatch tables and Files tree
