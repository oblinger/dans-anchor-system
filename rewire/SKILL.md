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

## What Rewire Does

The rule is simple: **add what's missing in the canonical top of the dispatch table; never delete anything.**

- Adds rows if a canonical row (External, User, Plan, Execute, Dev, Research) is missing.
- Adds items inside those rows if expected items are missing.
- Fixes order and format of canonical rows when wrong.

That's the entire scope. Beyond the canonical row set, rewire does nothing — any other rows in the table (custom groupings, project-specific rows, anything rewire doesn't recognize) are read-only. Don't touch them.

**No deletions, ever.** Not rows. Not items. Not user content. Even if something looks "wrong," rewire's response is to add what's needed, not remove what's there.

## Three duplicate guards (per F059)

Before any add-action, rewire runs the matching guard. If the guard trips, **rewire does not add** — it surfaces the finding for user adjudication via `/ask`.

| Add action | Guard | Failure mode if skipped |
|---|---|---|
| Adding a row to a dispatch table | Scan the table for any row whose link target resolves to the same file as the new row's target | Two rows pointing at the same file |
| Adding a dispatch table to a file | Scan the file for any existing dispatch-table-like structure (`-[[NAME]]-`, `\| NAME \|`, `\| -NAME- \|`) | Two dispatch tables in the same file (the DMUX bug — F059 root cause) |
| Creating a file | `find` for any file in the anchor with the same basename | Two `{NAME} Backlog.md` files in different folders |

The principle: rewire's "add what's missing" pattern must recognize **non-canonical equivalents** before adding. The legacy-vs-canonical equivalence check is the heart of the guard.

## Move policy (per F059)

Rewire splits "misplaced file" into two categories:

- **Obviously misplaced** — the file's basename matches a CAB facet whose canonical location is unambiguously defined by spec. Rewire moves these silently in default mode.
- **Possibly correctly placed** — anything else (basename matches no canonical facet, OR the file is in a plausible-looking location). Default mode **asks** the user before moving (via `/ask`).

Canonical-location table (auto-move candidates) — **updated per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] 2026-06-01** for the four-bucket Track / User / Design / Dev layout:

| Basename pattern | Canonical location |
|---|---|
| `{NAME} Docs.md` | `{NAME} Docs/` |
| `{NAME} Track.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Backlog.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Roadmap.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Icebox.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Inbox.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Questions.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} ask.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Rules.md` | `{NAME} Docs/{NAME} Track/` |
| `{NAME} Features.md` | `{NAME} Docs/{NAME} Track/{NAME} Features/` |
| `{NAME} User.md` | `{NAME} Docs/{NAME} User/` |
| `{NAME} Guide.md` | `{NAME} Docs/{NAME} User/` |
| `{NAME} Installation.md` | `{NAME} Docs/{NAME} User/` |
| `{NAME} CLI.md` | `{NAME} Docs/{NAME} User/` |
| `{NAME} FAQ.md` | `{NAME} Docs/{NAME} User/` |
| `{NAME} Design.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} Architecture.md` | `{NAME} Docs/{NAME} Design/{NAME} Architecture/` |
| `{NAME} Interface.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} UX Design.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} Data Model.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} Principles.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} PRD.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} Design Discussion.md` | `{NAME} Docs/{NAME} Design/` |
| `{NAME} Dev.md` | `{NAME} Docs/{NAME} Dev/` |
| `{NAME} Files.md` | `{NAME} Docs/{NAME} Dev/` |

**Retired (legacy locations during F094 migration window):**

| Legacy basename / location | New canonical location |
|---|---|
| `{NAME} Plan.md` | → `{NAME} Track.md` (Track Dispatch) |
| `{NAME} Triage.md` | → retired per F075; Q.md is the triage surface |
| `{NAME} System Design.md` | → folded into `{NAME} Architecture/` (Design bucket) |
| Old `{NAME} User/{NAME} Interface.md` | → `{NAME} Design/{NAME} Interface.md` |
| Old `{NAME} User/{NAME} Architecture/` | → `{NAME} Design/{NAME} Architecture/` |
| Old `{NAME} Plan/{NAME} UX Design.md` | → `{NAME} Design/{NAME} UX Design.md` |

During F094 Phase 1, rewire **recognizes both the old and new locations** for files that haven't been migrated yet (`{NAME} Plan/` still exists for some anchors, `{NAME} Track/` exists for others). When both exist on an anchor, the new location is canonical; rewire flags the old one for migration.

Anything not on this table → "possibly correctly placed" → rewire asks via `/ask` before moving.

### Aggressive mode (`--aggressive` flag)

`/rewire --aggressive` skips the "ask" step and moves any file whose basename matches a CAB facet, regardless of category. Emit a **dry-run preview** before applying so the user sees the full set before it lands — this is the one safety net for the autonomous mode.

### Exceptions

Before proposing any move (aggressive or otherwise), rewire reads `{NAME} Rules.md § Rewire Exceptions`. Format is a markdown table under a `## Rewire Exceptions` H2, with two columns: `Path | Reason`. Paths are anchor-relative. Matching rows are **skipped silently** — rewire neither moves nor asks. If `## Rewire Exceptions` H2 is absent from `{NAME} Rules.md`, treat as empty list. See [[CAB Rules]] § Optional sections.

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
- [ ] Standard rows appear in this order: External, User, Plan, Execute, Dev, Research. Add missing ones; do not delete or reorder anything else.
- [ ] Custom rows the user added are preserved as-is, wherever they sit.
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

## Default doc top-of-file (per F060)

The canonical top-of-doc for **every** `.md` file inside an anchor is:

1. Optional YAML frontmatter (when the doc needs `description:` or other metadata).
2. `# {DocTitle}` H1 line.
3. Blank line.
4. A dispatch table starting with the slug placeholder `-[[{basename}]]-` in the first cell.

The dispatch-table **placeholder form** (what a generator emits before rewire fills it in) is:

```
| -[[{basename}]]- | |
| --- | --- |
| --- | |
```

The right-cell of the header is left empty; rewire fills it with `><br>: <description-from-frontmatter>`. The third row is the auto-management separator (`---` left-cell, empty right-cell) — rewire fills it with auto-listed sibling/child rows per [[CAB Anchor Page]] § Separators and Auto-Management.

Recognition pattern: the **first cell containing `-[[NAME]]-`** is the dispatch-table marker — same recognition used elsewhere in rewire and by `ha --rescan`. No new syntax.

- [ ] Every `.md` file inside the anchor has an H1 line, immediately followed (one blank line) by a dispatch table whose first cell is `-[[{basename}]]-`.
- [ ] If an H1 exists but no dispatch table follows: insert the canonical empty placeholder (three rows above) and re-process so the body of rewire's other checks fill it in.
- [ ] If a legacy `:>>` breadcrumb, plain-prose `> [[parent]]` breadcrumb, or `n::` / `desc::` inline metadata line precedes the H1: **delete the legacy line** and insert the placeholder. If the legacy line carried a description, move it into YAML frontmatter as `description: …` before deleting.
- [ ] The placeholder's empty right-cell of the header gets filled with `><br>: <description>` (description sourced from YAML frontmatter `description:` field).
- [ ] The `---` auto-management separator row at the bottom of the placeholder triggers auto-listing of sibling/child docs in the user zone above it (per [[CAB Anchor Page]] § Separators).

**Heuristic for pre-existing tables in a doc** (per F060 Q5):
- A table whose rows are **wiki-links to sibling/child docs** is a **navigation table** — fold its rows into the dispatch table (above the `---` separator).
- A table whose rows are the **doc's payload** (e.g. CLASSES, SCAFFOLDS, METADATA, TOC, command reference) is a **topic table** — leave it as a distinct table after the dispatch table.
- The dispatch table always sits at the top, directly under the H1.

**Migration policy — forward-only.** Existing files with legacy breadcrumbs migrate organically when modified (i.e. rewire only inserts the placeholder during a focused or full rewire pass that touches the file). No bulk sweep — the mass anchor-root migration remains [[CAB Backlog]] F001 in `## Later`.

**Exceptions to the placeholder rule.** A small set of facet docs are explicit F060 exceptions because they have custom H1-only tops or a fixed required structure:

- `{NAME} Triage.md` — H1 banner already encodes breadcrumb + dispatch info per [[CAB Triage]] § H1 banner. Skip placeholder check.
- `{NAME} Questions.md` — H1-only top with no dispatch table per [[CAB Questions]] § H1. Skip placeholder check.
- **Feature docs** (`F<n> — {Title}.md` inside `{NAME} Features/`) — H1 carries an inline breadcrumb (`# [[{NAME}]] · F<n> — {Title}`) per [[CAB Features]] § Document zone. Placeholder is optional, not required; rewire neither inserts nor strips it.
- **`SKILL.md`** (skill anchor entry point) — fixed frontmatter + body structure per [[CAB Skill]]. F060 applies to the sibling `{Slug}.md` anchor root page, not to SKILL.md itself.
- **`CLAUDE.md`** — Claude Code configuration file. Not a CAB doc.
- **`website/index.md`** and other Jekyll-published pages — not CAB facet docs; the front matter uses the cayman layout, not CAB frontmatter. F060 doesn't apply.
- **`README.md`** at repo root — GitHub-rendered front page; uses repo conventions, not CAB frontmatter.

Add exceptions sparingly; the default is **every doc** gets the placeholder.

## Folder templates

A folder template is a folder whose name begins with an underscore — `_{Name} Template/` — that captures the canonical shape for a sibling kind. See [[CAB Template]] for the discipline.

- [ ] **Detect folder templates** — for every folder, check if it contains any child folder matching the glob `_* Template/`. If yes, the parent folder has a folder template.
- [ ] **Detect markdown-file templates** — for every folder, also check for any child file matching `_* Template.md`. If yes, the parent folder has a file-level template.
- [ ] **Folder-level template earns a dispatch row** — the parent folder's dispatch page MUST contain a row linking to the template. The row sits at the **top of the user zone** (above the `---` auto-management separator), so it surfaces immediately when opening the folder. Canonical row format:
  ```
  | Template | [[_{Name} Template]] |
  ```
  The wiki-link resolves by basename (folder templates link to the inside marker file `_{Name} Template.md`; file templates link to the template file directly).
- [ ] **Generic templates (those living in `CAB/CAB Facets/`) do NOT get a dispatch row** in every consumer's dispatch. They are looked up by facet name; cluttering every dispatch with template links to vault-wide templates is the failure mode this rule prevents.
- [ ] **Audit category** — when a `_* Template/` folder or `_* Template.md` file exists in a parent but the parent's dispatch lacks the template row, flag as `missing-folder-template-row` (per [[CAB Template]] § Audit categories).
- [ ] **Orphan check** — when a template folder/file exists nowhere in any dispatch (not even its parent's), flag as `orphan-template`.

---

# Code Anchor

The synthesis-vs-reference split: **Dev** holds audit-tied implementation reference (Files tree + per-module docs); **User** holds curated synthesis (Interface + Architecture + Guide + Cards + CLI). The Interface is the *required* top-level human-authored layer contract; see [[CAB Interface]].

## {NAME}.md (anchor page — code-specific)

- [ ] Has External row with repo URL
- [ ] Has Dev row linking to Dev dispatch page with `+` suffix
- [ ] Has User row with `+` suffix if User folder exists
- [ ] **Dev row contents** — primarily `[[{NAME} Files]]` plus any per-module docs; does NOT include Interface or Architecture
- [ ] **User row contents** — `[[{NAME} Interface]]` (required for code), `[[{NAME} Guide]]`, `[[{NAME} Architecture]]`, plus any other curated synthesis docs (Cards, CLI)

## Code / .git/

- [ ] `.anchor` has a `code:` key that resolves to an existing directory (absolute, or relative to anchor root; `.` for inline)

## README.md

- [ ] Exists in the repo root

## CLAUDE.md (code-specific)

- [ ] Exists at anchor root only — NOT inside the repo

## {NAME} Docs/{NAME} Dev/ — audit-tied implementation reference

- [ ] Folder exists with dispatch page `{NAME} Dev.md`
- [ ] `{NAME} Files.md` exists inside Dev folder (audit-generated tree)
- [ ] Files.md lists source files with wiki-links to module docs where they exist
- [ ] Files.md row 1 (repo root) ends with `→ [[{NAME} Interface]]` — wiki-link by basename resolves to the Interface file in `{NAME} User/`
- [ ] Dev dispatch page links to all per-module docs in the Dev folder
- [ ] **Interface is NOT in Dev** — flag as `dev-synthesis-misplaced` if `{NAME} Interface.md` (or legacy `{NAME} Rollup.md`) is found here; migrate to `{NAME} User/`
- [ ] **Architecture is NOT in Dev** — same; migrate to `{NAME} User/`

## {NAME} Docs/{NAME} User/ — curated synthesis layer

- [ ] Folder exists with dispatch page `{NAME} User.md`
- [ ] **`{NAME} Interface.md` exists here** — the required top-level human-authored layer contract; see [[CAB Interface]]
- [ ] **If `{NAME} Interface.md` is absent:** auto-create a scaffold (H1 + canonical dispatch placeholder + TODO sections per [[CAB Interface]] § Document Structure) AND file a `## Now` backlog row in `{NAME} Backlog.md`: `**F<n> — Author top-level Interface for {NAME}** [Designing] — Rewire scaffolded {NAME} Interface.md on {YYYY-MM-DD}. Needs user collaboration to author the layer contract — see [[CAB Interface]]. → [[{NAME} Interface]].` The agent does NOT attempt to fill in the contract content — that's the user-collaboration step per [[SKA workflow]] § Interface-validation gate.
- [ ] **Legacy migration:** if `{NAME} Rollup.md` exists (predecessor to Interface), do NOT auto-rename. Surface a `## Now [Designing]` backlog row: `**F<n> — Migrate {NAME} Rollup → {NAME} Interface** [Designing] — content review needed (see F062). → [[{NAME} Rollup]].` Per F060's forward-only policy, the rename happens when the user touches the anchor.
- [ ] `{NAME} Architecture.md` exists here (system-level overview, module diagram, data flow)
- [ ] `{NAME} Guide.md` exists here (the primary user guide; basename is `Guide` not `User Guide` per [[CAB User Dispatch]] § Filename convention)
- [ ] User dispatch page lists Interface (required for code) + Guide + Architecture, plus any Cards / CLI / topic-specific guides

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

A skill anchor IS a CAB anchor — `SKILL.md` is the agent-loaded code, the rest of the structure is the design history (PRD / Backlog / Triage / Features). The full Skill Anchor spec lives in [[Skill Anchor]] (cab-trait); the working example is [[CSE]]. **All checks under "All Types" still apply** — what's listed below is in addition.

## SKILL.md (the agent-loaded code)

- [ ] File exists at anchor root
- [ ] YAML frontmatter has `name:` field (matching folder name, kebab-case)
- [ ] YAML frontmatter has `description:` field
- [ ] YAML frontmatter has `user_invocable:` field (boolean — `true` for invocable skills, `false` for disciplines)
- [ ] If invocable: contains Actions dispatch table mapping `/skill action` to workflow files
- [ ] Every action file referenced in the dispatch table exists
- [ ] Top of body links to user docs: `User docs: [[SKL {Slug}]]` and (optionally) `Anchor page: [[{Slug}]]`

## {Slug}.md (anchor root page)

- [ ] File exists at folder root, name = Title Case slug (e.g., `Groom.md`, `Backlog Horizons.md`)
- [ ] Skill-specific first dispatch row: `Skill | [[{folder}/SKILL\|SKILL.md]], [[SKL {Slug}\|User Docs]]`
- [ ] Second dispatch row: `[[{Slug} Plan\|Plan]]+ | [[{Slug} PRD\|PRD]], [[{Slug} Backlog\|Backlog]], [[{Slug} Triage\|Triage]], [[{Slug} Features\|Features]]`
- [ ] No `Dev` row — skill anchors don't have one (SKILL.md *is* the code)
- [ ] No `User` row — skill anchors don't have one (user docs live in the SKL tree)

## {Slug} Docs/{Slug} Plan/

- [ ] `{Slug} Plan.md` dispatch exists, links to PRD / Backlog / Triage / Features
- [ ] `{Slug} PRD.md` exists (placeholder OK if no design discussion yet)
- [ ] `{Slug} Backlog.md` exists with workflow-state H2s (Active / Ready / Now / Next / Later / Done)
- [ ] `{Slug} Triage.md` exists with H1 banner format per [[CAB Triage]]
- [ ] `{Slug} Features/` folder exists with `{Slug} Features.md` dispatch

## File naming inside the skill folder

- [ ] `SKILL.md` (uppercase, fixed)
- [ ] Action files: kebab-case, prefixed by folder name — `{folder}-{action}.md`
- [ ] Anchor docs: Title Case, prefixed by Slug — `{Slug} PRD.md`, `{Slug} Plan/{Slug} Backlog.md`

## SKL user-docs file

- [ ] User-doc file exists at `~/.claude/skills/SKL User Docs/SKL Skills/SKL {Slug}.md` (or in a sub-folder for multi-variant skills, e.g. `SKL Mode/`)
- [ ] H1 of that file matches the skill name
- [ ] Listed in `SKL User Docs/SKL Skills.md` dispatch (if present)

## Wired into the SKA Skills table at the top of `SKA.md`

**This is required for every skill that ships user docs.** The SKA Skills table is the user-facing index — a skill that isn't in it is invisible to users browsing the anchor.

- [ ] Skill is referenced from the Skills table in `~/.claude/skills/SKA.md` (or `Bespoke/Skill Agent/SKA.md`)
- [ ] Cell format: `**[[SKL {Slug}\|{folder}]]**` — link target is the SKL user-doc, display alias is the folder name (so the user sees `mode`, `groom`, etc., as it appears in `/<command>`)
- [ ] Placed in the appropriate column based on the skill's purpose:
  - **Workflow** — feature, groom, land, roster, triage, crank, audit (skills that move work through states)
  - **Build / Code** — code, fortify, mint (skills that produce or harden code)
  - **Anchor / Structure** — CAB, create, migrate, rewire, rule (skills that shape anchors / structure / rules)
  - **Investigation / Coord** — parley, research, role (skills that explore or coordinate)
  - **Environment / I-O / Content** — ctrl, edit, fix, IO, MD, product, snip (skills that interact with environment, files, or external systems)
  - **Disciplines** — finalize, ask, workflow, backlog-horizons, **mode** (`user_invocable: false` skills cited by other skills)
- [ ] If `user_invocable: false`: skill goes in the **Disciplines** column.
- [ ] If no SKL user-doc exists: skill is hidden from the table (the table only shows skills with user-facing docs); rewire flags this as a finding rather than fixing.

## Slug-collision warning (skip these subdirs)

- [ ] If the skill folder shares a slug with a parent-level project anchor (e.g., `cab/` ↔ `Bespoke/Skill Agent/CAB/`, `io/` ↔ `Bespoke/Skill Agent/IO/`), do NOT create `{Slug}.md` anchor root in the skill folder — it would collide on macOS case-insensitive filesystems. The project anchor at the parent level carries the slug; the skill folder has only `SKILL.md` and action files.

---

# Universal Rules

- [ ] Wiki-links in tables: always escape pipe as `\|` — `[[target\|alias]]` not `[[target|alias]]`
- [ ] Blank line before every markdown table or it will not render
- [ ] Frontmatter must have both `cab-traits:` (list) and `description:`
- [ ] H1 heading: `# {slug} — {FolderName}` when slug differs from folder name, or `# {NAME}` when they match
- [ ] Dispatch table header: `-[[{NAME}]]-` in first cell, `><br>:` markers in second cell
- [ ] Dispatch table separator row: `---`, `^^^`, `...`, or `+++` in left cell enables auto-management below
- [ ] **Every `.md` file inside an anchor** (not just the anchor root) has the canonical top: H1 + dispatch-table placeholder with `-[[{basename}]]-` first cell. No legacy `:>>` / `> [[parent]]` breadcrumbs, no `n::` / `desc::` inline metadata. See § Default doc top-of-file above for the placeholder form and migration rules.
- [ ] Per-row `+` suffix on wiki-link rows (e.g., `[[Name]]+`) to show grandchildren for that row
- [ ] Standard rows order: External, User, Plan, Execute, Dev, Research
- [ ] Project-specific rows go AFTER standard rows
- [ ] `.anchor` file must exist (can be empty — properties derive from folder name)
- [ ] Dispatch pages link to ALL their children — no orphan files
- [ ] Every subfolder that has files needs a dispatch page
- [ ] Every markdown file and folder inside an anchor is prefixed with `{NAME}`
- [ ] Rewire adds missing canonical rows and missing items in those rows. That's all. No deletions, ever — not rows, not items, not user content.
- [ ] Rewire does not create missing files — only links existing ones
- [ ] Rewire does not modify file content — only dispatch tables and Files tree

<!-- compiled:end -->
