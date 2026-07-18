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
requires:: vault, anchor-cli, skill:ask, facet:backlog, facet:dispatch-table
subsystem:: [[DAS Hygiene Design]] — the Hygiene group's subsystem profile

Idempotent structural repair for any anchor. Ensures all files are linked, dispatch tables are wired, and the skeleton is consistent. Safe to run anytime — only adds, never deletes.

| Table of Contents |  |
|---|---|
| **[[#Usage]]** |  |
|    [[#Focused Rewire (`rewire the <facet>`)]] |  |
| **[[#What Rewire Does]]** |  |
| **[[#Three duplicate guards (per F059)]]** |  |
| **[[#Move policy (per F059)]]** |  |
|    [[#Aggressive mode (`--aggressive` flag)]] |  |
|    [[#Exceptions]] |  |
| **[[#Runbook (full rewire)]]** |  |
| **[[#.anchor]]** |  |
| **[[#{FolderName}.md (marker file)]]** |  |
| **[[#{slug}.md (anchor page)]]** |  |
| **[[#{slug} Docs/{slug} Docs.md]]** |  |
| **[[#{slug} Docs/{slug} Plan/{slug} Plan.md]]** |  |
| **[[#{slug} Docs/{slug} Dev/{slug} Dev.md]]** |  |
| **[[#{slug} Docs/{slug} User/{slug} User.md]]** |  |
| **[[#CLAUDE.md]]** |  |
| **[[#General dispatch integrity]]** |  |
| **[[#Default doc top-of-file (per F060)]]** |  |
| **[[#Folder templates]]** |  |
| **[[#{slug}.md (anchor page — code-specific)]]** |  |
| **[[#Code / .git/]]** |  |
| **[[#README.md]]** |  |
| **[[#CLAUDE.md (code-specific)]]** |  |
| **[[#{slug} Docs/{slug} Dev/ — audit-tied implementation reference]]** |  |
| **[[#{slug} Docs/{slug} User/ — curated synthesis layer]]** |  |
| **[[#justfile (if present in repo)]]** |  |
| **[[#{slug}.md (anchor page — topic-specific)]]** |  |
| **[[#{slug} Docs/]]** |  |
| **[[#Conditional structure (create only when another trait requires)]]** |  |
| **[[#SKILL.md (the agent-loaded code)]]** |  |
| **[[#{Slug}.md (anchor root page)]]** |  |
| **[[#{Slug} Docs/{Slug} Plan/]]** |  |
| **[[#File naming inside the skill folder]]** |  |
| **[[#DAS user-docs file]]** |  |
| **[[#Wired into the SKA Skills table at the top of `SKA.md`]]** |  |
| **[[#Slug-collision warning (skip these subdirs)]]** |  |

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

| -{slug}-                             | ><br>:                                                                                                                                    |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| External                             | [Repo](https://github.com/oblinger/repo), [Project Page](https://oblinger.github.io/gitproj/repo/)                                      |
| [[{slug} User/{slug} User\|User]]+  | [[{slug} User Guide\|User Guide]], [[{slug} Cards\|Cards]]                                                                               |
| [[{slug} Plan\|Plan]]+              | [[{slug} PRD\|PRD]], [[{slug} System Design\|System Design]], [[{slug} UX Design\|UX]], [[{slug} Features\|Features]], [[{slug} Discussion\|Discussion]] |
| [[{slug} Plan\|Execute]]            | [[{slug} Inbox\|Inbox]], [[{slug} Open Questions\|Open Q]], [[{slug} Backlog\|Backlog]], [[{slug} Roadmap\|Roadmap]]                     |
| [[{slug} Dev/{slug} Dev\|Dev]]+     | [[{slug} Files\|Files]], [[{slug} Architecture\|Architecture]]                                                                           |
| Research                             | [[{slug} Research\|Research]], [[{slug} References\|References]]                                                                         |
| ...                                  |                                                                                                                                           |

```

**Standard row order:** External, User, Plan, Execute, Dev, Research. Omit rows not relevant to this anchor. Do not reorder. Do not append new rows at the end — insert in the correct position.

**Row label format:**
- External, Research — plain text
- User — `[[{slug} User/{slug} User\|User]]+`
- Plan — `[[{slug} Plan\|Plan]]+`
- Execute — `[[{slug} Plan\|Execute]]` (links to Plan folder, no `+`)
- Dev — `[[{slug} Dev/{slug} Dev\|Dev]]+`

**Entry format:** Each entry is `[[{slug} FacetName\|Short Name]]` — full wiki-link with escaped pipe and short display alias.

<!-- compiled:end -->

#### Steps

1. **Look up the facet** — read the matching file in `~/.claude/skills/CAB/cab-facets/` to find which row it belongs in and what its entry should look like

2. **Fix the anchor page dispatch table** — open `{slug}.md`. Match the table against the canonical format above. Ensure the correct row exists in the correct position with the facet entry in it. If the row is missing, add it in the right position — not at the end.

3. **Fix intermediate dispatch tables** — if the facet lives in a subfolder (e.g., `{slug} Plan/`), ensure the subfolder and its dispatch page exist, and that dispatch page has a row with the facet linked in it.

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
| Creating a file | `find` for any file in the anchor with the same basename | Two `{slug} Backlog.md` files in different folders |

The principle: rewire's "add what's missing" pattern must recognize **non-canonical equivalents** before adding. The legacy-vs-canonical equivalence check is the heart of the guard.

## Move policy (per F059)

Rewire splits "misplaced file" into two categories:

- **Obviously misplaced** — the file's basename matches a CAB facet whose canonical location is unambiguously defined by spec. Rewire moves these silently in default mode.
- **Possibly correctly placed** — anything else (basename matches no canonical facet, OR the file is in a plausible-looking location). Default mode **asks** the user before moving (via `/ask`).

Canonical-location table (auto-move candidates) — **updated per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] 2026-06-01** for the four-bucket Track / User / Design / Dev layout:

| Basename pattern | Canonical location |
|---|---|
| `{slug} Docs.md` | `{slug} Docs/` |
| `{slug} Track.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Backlog.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Roadmap.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Icebox.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Inbox.md` | `{slug} Docs/{slug} Track/` |
| `{slug} queries.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Rules.md` | `{slug} Docs/{slug} Track/` |
| `{slug} Features.md` | `{slug} Docs/{slug} Track/{slug} Features/` |
| `{slug} User.md` | `{slug} Docs/{slug} User/` |
| `{slug} Guide.md` | `{slug} Docs/{slug} User/` |
| `{slug} Installation.md` | `{slug} Docs/{slug} User/` |
| `{slug} CLI.md` | `{slug} Docs/{slug} User/` |
| `{slug} FAQ.md` | `{slug} Docs/{slug} User/` |
| `{slug} Design.md` | `{slug} Docs/{slug} Design/` |
| `{slug} Architecture.md` | `{slug} Docs/{slug} Design/{slug} Architecture/` |
| `{slug} Interface.md` | `{slug} Docs/{slug} Design/` |
| `{slug} UX Design.md` | `{slug} Docs/{slug} Design/` |
| `{slug} Data Model.md` | `{slug} Docs/{slug} Design/` |
| `{slug} Principles.md` | `{slug} Docs/{slug} Design/` |
| `{slug} PRD.md` | `{slug} Docs/{slug} Design/` |
| `{slug} Design Discussion.md` | `{slug} Docs/{slug} Design/` |
| `{slug} Dev.md` | `{slug} Docs/{slug} Dev/` |
| `{slug} Files.md` | `{slug} Docs/{slug} Dev/` |

**Retired (legacy locations during F094 migration window):**

| Legacy basename / location | New canonical location |
|---|---|
| `{slug} Plan.md` | → `{slug} Track.md` (Track Dispatch) |
| `{slug} Triage.md` | → retired per F075; Q.md is the queue-file surface |
| `{slug} System Design.md` | → folded into `{slug} Architecture/` (Design bucket) |
| Old `{slug} User/{slug} Interface.md` | → `{slug} Design/{slug} Interface.md` |
| Old `{slug} User/{slug} Architecture/` | → `{slug} Design/{slug} Architecture/` |
| Old `{slug} Plan/{slug} UX Design.md` | → `{slug} Design/{slug} UX Design.md` |

During F094 Phase 1, rewire **recognizes both the old and new locations** for files that haven't been migrated yet (`{slug} Plan/` still exists for some anchors, `{slug} Track/` exists for others). When both exist on an anchor, the new location is canonical; rewire flags the old one for migration.

Anything not on this table → "possibly correctly placed" → rewire asks via `/ask` before moving.

### Aggressive mode (`--aggressive` flag)

`/rewire --aggressive` skips the "ask" step and moves any file whose basename matches a CAB facet, regardless of category. Emit a **dry-run preview** before applying so the user sees the full set before it lands — this is the one safety net for the autonomous mode.

### Exceptions

Before proposing any move (aggressive or otherwise), rewire reads `{slug} Rules.md § Rewire Exceptions`. Format is a markdown table under a `## Rewire Exceptions` H2, with two columns: `Path | Reason`. Paths are anchor-relative. Matching rows are **skipped silently** — rewire neither moves nor asks. If `## Rewire Exceptions` H2 is absent from `{slug} Rules.md`, treat as empty list. See [[DAS Ruleset]] § Optional sections.

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
- [ ] If slug differs from folder name, contains `(See Anchor [[{slug}]])`
- [ ] If folder name IS the anchor name, this file serves as the anchor page

## {slug}.md (anchor page)

- [ ] Has H1 heading: `# {slug} — {FolderName}` when slug differs from folder name, or `# {slug}` when they match
- [ ] Has YAML frontmatter with `cab-traits:` field (list)
- [ ] Has YAML frontmatter with `description:` field
- [ ] Has dispatch table with `-[[{slug}]]-` in first cell of header row
- [ ] Dispatch table header second cell has `>` (breadcrumb) and/or `:` (description), separated by `<br>` (e.g., `><br>: short description`)
- [ ] Blank line exists before the dispatch table
- [ ] All wiki-link aliases inside tables use escaped pipe: `[[target\|alias]]`
- [ ] Standard rows appear in this order: External, User, Plan, Execute, Dev, Research. Add missing ones; do not delete or reorder anything else.
- [ ] Custom rows the user added are preserved as-is, wherever they sit.
- [ ] User row label links to `[[{slug} User/{slug} User\|User]]` with `+` suffix if folder exists
- [ ] Plan row label links to `[[{slug} Plan\|Plan]]` with `+` suffix if folder exists
- [ ] Execute row label links to `[[{slug} Plan\|Execute]]`
- [ ] Dev row label links to `[[{slug} Dev/{slug} Dev\|Dev]]` with `+` suffix if folder exists
- [ ] External and Research row labels are plain text (not wiki-links)
- [ ] Table ends with a separator row to enable auto-management of remaining children: `---` (alpha), `^^^` (reverse alpha), `...` (compact), or `+++` (alpha with grandchildren)
- [ ] Every file listed in inline row links actually exists

## {slug} Docs/{slug} Docs.md

- [ ] File exists if `{slug} Docs/` folder exists
- [ ] Has dispatch table linking to Plan, Dev, User subfolders
- [ ] Links to every subfolder dispatch page that exists

## {slug} Docs/{slug} Plan/{slug} Plan.md

- [ ] File exists if `{slug} Plan/` folder exists
- [ ] Has dispatch table with `-[[{slug} Plan]]-` in first cell
- [ ] Dispatch table header second cell has `><br>:` markers (breadcrumb + description)
- [ ] Table ends with a separator row (`---` or `^^^`) for auto-management
- [ ] Links to every `.md` file in the Plan folder (PRD, System Design, UX Design, Discussion, Roadmap, Backlog, Inbox, Open Questions, Research, Features)
- [ ] `{slug} Features/` folder exists under Plan with `{slug} Features.md` index inside it
- [ ] Features index links to all dated feature files (reverse chronological)
- [ ] Only links files that actually exist — no dead links
- [ ] No orphan files in Plan folder missing from dispatch table

## {slug} Docs/{slug} Dev/{slug} Dev.md

- [ ] File exists if `{slug} Dev/` folder exists
- [ ] Has dispatch table with `-[[{slug} Dev]]-` in first cell
- [ ] Dispatch table header second cell has `><br>:` markers (breadcrumb + description)
- [ ] Table ends with a separator row for auto-management
- [ ] Files row appears first in body rows
- [ ] Architecture row appears second in body rows
- [ ] Module doc rows are grouped by source folder with bold folder headers (`**folder/**`)
- [ ] Links to every module doc `.md` file in the Dev folder
- [ ] No orphan files in Dev folder missing from dispatch table

## {slug} Docs/{slug} User/{slug} User.md

- [ ] File exists if `{slug} User/` folder exists
- [ ] Has dispatch table with `-[[{slug} User]]-` in first cell
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
- [ ] Walking from `{slug} Docs.md` reaches every `.md` file in the Docs tree

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

The right-cell of the header is left empty; rewire fills it with `><br>: <description-from-frontmatter>`. The third row is the auto-management separator (`---` left-cell, empty right-cell) — rewire fills it with auto-listed sibling/child rows per [[DAS Anchor Page]] § Separators and Auto-Management.

Recognition pattern: the **first cell containing `-[[NAME]]-`** is the dispatch-table marker — same recognition used elsewhere in rewire and by `ha --rescan`. No new syntax.

- [ ] Every `.md` file inside the anchor has an H1 line, immediately followed (one blank line) by a dispatch table whose first cell is `-[[{basename}]]-`.
- [ ] If an H1 exists but no dispatch table follows: insert the canonical empty placeholder (three rows above) and re-process so the body of rewire's other checks fill it in.
- [ ] If a legacy `:>>` breadcrumb, plain-prose `> [[parent]]` breadcrumb, or `n::` / `desc::` inline metadata line precedes the H1: **delete the legacy line** and insert the placeholder. If the legacy line carried a description, move it into YAML frontmatter as `description: …` before deleting.
- [ ] The placeholder's empty right-cell of the header gets filled with `><br>: <description>` (description sourced from YAML frontmatter `description:` field).
- [ ] The `---` auto-management separator row at the bottom of the placeholder triggers auto-listing of sibling/child docs in the user zone above it (per [[DAS Anchor Page]] § Separators).

**Heuristic for pre-existing tables in a doc** (per F060 Q5):
- A table whose rows are **wiki-links to sibling/child docs** is a **navigation table** — fold its rows into the dispatch table (above the `---` separator).
- A table whose rows are the **doc's payload** (e.g. CLASSES, SCAFFOLDS, METADATA, TOC, command reference) is a **topic table** — leave it as a distinct table after the dispatch table.
- The dispatch table always sits at the top, directly under the H1.

**Migration policy — forward-only.** Existing files with legacy breadcrumbs migrate organically when modified (i.e. rewire only inserts the placeholder during a focused or full rewire pass that touches the file). No bulk sweep — the mass anchor-root migration remains [[DAS Backlog]] F001 in `## Later`.

**Exceptions to the placeholder rule.** A small set of facet docs are explicit F060 exceptions because they have custom H1-only tops or a fixed required structure:

- `{slug} queries.md` — agent-owned page built on demand by `/ask`'s determination logic (frontmatter + H1 + sections, no dispatch table). Skip placeholder check.
- **Feature docs** (`F<n> — {Title}.md` inside `{slug} Features/`) — H1 carries an inline breadcrumb (`# [[{slug}]] · F<n> — {Title}`) per [[DAS Features]] § Document zone. Placeholder is optional, not required; rewire neither inserts nor strips it.
- **`SKILL.md`** (skill anchor entry point) — fixed frontmatter + body structure per [[DAS Skill]]. F060 applies to the sibling `{Slug}.md` anchor root page, not to SKILL.md itself.
- **`CLAUDE.md`** — Claude Code configuration file. Not a CAB doc.
- **`website/index.md`** and other Jekyll-published pages — not CAB facet docs; the front matter uses the cayman layout, not CAB frontmatter. F060 doesn't apply.
- **`README.md`** at repo root — GitHub-rendered front page; uses repo conventions, not CAB frontmatter.

Add exceptions sparingly; the default is **every doc** gets the placeholder.

## Folder templates

A folder template is a folder whose name begins with an underscore — `_{Name} Template/` — that captures the canonical shape for a sibling kind. See [[DAS Template]] for the discipline.

- [ ] **Detect folder templates** — for every folder, check if it contains any child folder matching the glob `_* Template/`. If yes, the parent folder has a folder template.
- [ ] **Detect markdown-file templates** — for every folder, also check for any child file matching `_* Template.md`. If yes, the parent folder has a file-level template.
- [ ] **Folder-level template earns a dispatch row** — the parent folder's dispatch page MUST contain a row linking to the template. The row sits at the **top of the user zone** (above the `---` auto-management separator), so it surfaces immediately when opening the folder. Canonical row format:
  ```

  | Template | [[_{Name} Template]] |

  ```
  The wiki-link resolves by basename (folder templates link to the inside marker file `_{Name} Template.md`; file templates link to the template file directly).
- [ ] **Generic templates (those living in `CAB/CAB Facets/`) do NOT get a dispatch row** in every consumer's dispatch. They are looked up by facet name; cluttering every dispatch with template links to vault-wide templates is the failure mode this rule prevents.
- [ ] **Audit category** — when a `_* Template/` folder or `_* Template.md` file exists in a parent but the parent's dispatch lacks the template row, flag as `missing-folder-template-row` (per [[DAS Template]] § Audit categories).
- [ ] **Orphan check** — when a template folder/file exists nowhere in any dispatch (not even its parent's), flag as `orphan-template`.

---

# Code Anchor

The synthesis-vs-reference split: **Dev** holds audit-tied implementation reference (Files tree + per-module docs); **User** holds curated synthesis (Interface + Architecture + Guide + Cards + CLI). The Interface is the *required* top-level human-authored layer contract; see [[DAS Interface]].

## {slug}.md (anchor page — code-specific)

- [ ] Has External row with repo URL
- [ ] Has Dev row linking to Dev dispatch page with `+` suffix
- [ ] Has User row with `+` suffix if User folder exists
- [ ] **Dev row contents** — primarily `[[{slug} Files]]` plus any per-module docs; does NOT include Interface or Architecture
- [ ] **User row contents** — `[[{slug} Interface]]` (required for code), `[[{slug} Guide]]`, `[[{slug} Architecture]]`, plus any other curated synthesis docs (Cards, CLI)

## Code / .git/

- [ ] `.anchor` has a `code:` key that resolves to an existing directory (absolute, or relative to anchor root; `.` for inline)

## README.md

- [ ] Exists in the repo root

## CLAUDE.md (code-specific)

- [ ] Exists at anchor root only — NOT inside the repo

## {slug} Docs/{slug} Dev/ — audit-tied implementation reference

- [ ] Folder exists with dispatch page `{slug} Dev.md`
- [ ] `{slug} Files.md` exists inside Dev folder (audit-generated tree)
- [ ] Files.md lists source files with wiki-links to module docs where they exist
- [ ] Files.md row 1 (repo root) ends with `→ [[{slug} Interface]]` — wiki-link by basename resolves to the Interface file in `{slug} User/`
- [ ] Dev dispatch page links to all per-module docs in the Dev folder
- [ ] **Interface is NOT in Dev** — flag as `dev-synthesis-misplaced` if `{slug} Interface.md` (or legacy `{slug} Rollup.md`) is found here; migrate to `{slug} User/`
- [ ] **Architecture is NOT in Dev** — same; migrate to `{slug} User/`

## {slug} Docs/{slug} User/ — curated synthesis layer

- [ ] Folder exists with dispatch page `{slug} User.md`
- [ ] **`{slug} Interface.md` exists here** — the required top-level human-authored layer contract; see [[DAS Interface]]
- [ ] **If `{slug} Interface.md` is absent:** auto-create a scaffold (H1 + canonical dispatch placeholder + TODO sections per [[DAS Interface]] § Document Structure) AND file a `## Now [Designing]` backlog row via the workflow skill's `state Backlog F+ define` (per [[SKA workflow]] § Mutation API — never edit `{slug} Backlog.md` directly):

  ```bash
  echo '- **F+ — Author top-level Interface for {slug}** [Designing] — Rewire scaffolded {slug} Interface.md on {YYYY-MM-DD}. Needs user collaboration to author the layer contract — see [[DAS Interface]]. → [[{slug} Interface]].' | \
      ~/.claude/skills/workflow/scripts/state --anchor {slug} Backlog F+ define
  ```

  The agent does NOT attempt to fill in the contract content — that's the user-collaboration step per [[DAS Interface]] § Interface-validation gate.

- [ ] **Legacy migration:** if `{slug} Rollup.md` exists (predecessor to Interface), do NOT auto-rename. Surface a `## Now [Designing]` backlog row via `state Backlog F+ define`:

  ```bash
  echo '- **F+ — Migrate {slug} Rollup → {slug} Interface** [Designing] — content review needed (see F062). → [[{slug} Rollup]].' | \
      ~/.claude/skills/workflow/scripts/state --anchor {slug} Backlog F+ define
  ```

  Per F060's forward-only policy, the rename happens when the user touches the anchor.
- [ ] `{slug} Architecture.md` exists here (system-level overview, module diagram, data flow)
- [ ] `{slug} Guide.md` exists here (the primary user guide; basename is `Guide` not `User Guide` per [[DAS User Dispatch]] § Filename convention)
- [ ] User dispatch page lists Interface (required for code) + Guide + Architecture, plus any Cards / CLI / topic-specific guides

## justfile (if present in repo)

- [ ] Has at minimum a `test` recipe

---

# Topic Anchor

## {slug}.md (anchor page — topic-specific)

- [ ] Functions as a routing hub — links to sub-topics or content pages

## {slug} Docs/

- [ ] Folder exists with dispatch page
- [ ] `{slug} Plan/` subfolder exists with planning docs

## Conditional structure (create only when another trait requires)

- [ ] `{slug} Dev/` folder — create only when Code trait is present
- [ ] `{slug} User/` folder — create only when Code trait is present
- [ ] `.anchor` `code:` key — add only when the `code` trait is present

---

# Skill Anchor

A skill anchor IS a CAB anchor — `SKILL.md` is the agent-loaded code, the rest of the structure is the design history (PRD / Backlog / Features). The full Skill Anchor spec lives in [[Skill Anchor]] (cab-trait); the working example is [[CSE]]. **All checks under "All Types" still apply** — what's listed below is in addition.

## SKILL.md (the agent-loaded code)

- [ ] File exists at anchor root
- [ ] YAML frontmatter has `name:` field (matching folder name, kebab-case)
- [ ] YAML frontmatter has `description:` field
- [ ] YAML frontmatter has `user_invocable:` field (boolean — `true` for invocable skills, `false` for disciplines)
- [ ] If invocable: contains Actions dispatch table mapping `/skill action` to workflow files
- [ ] Every action file referenced in the dispatch table exists
- [ ] Top of body links to user docs: `User docs: [[DAS {Slug}]]` and (optionally) `Anchor page: [[{Slug}]]`

## {Slug}.md (anchor root page)

- [ ] File exists at folder root, name = Title Case slug (e.g., `Groom.md`, `Backlog.md`)
- [ ] Skill-specific first dispatch row: `Skill | [[{folder}/SKILL\|SKILL.md]], [[DAS {Slug}|User Docs]]`
- [ ] Second dispatch row: `[[{Slug} Plan\|Plan]]+ | [[{Slug} PRD\|PRD]], [[{Slug} Backlog\|Backlog]], [[{Slug} Features\|Features]]`
- [ ] No `Dev` row — skill anchors don't have one (SKILL.md *is* the code)
- [ ] No `User` row — skill anchors don't have one (user docs live in the DAS docs tree)

## {Slug} Docs/{Slug} Plan/

- [ ] `{Slug} Plan.md` dispatch exists, links to PRD / Backlog / Features
- [ ] `{Slug} PRD.md` exists (placeholder OK if no design discussion yet)
- [ ] `{Slug} Backlog.md` exists with workflow-state H2s (Active / Ready / Now / Next / Later / Done)
- [ ] `{Slug} Features/` folder exists with `{Slug} Features.md` dispatch

## File naming inside the skill folder

- [ ] `SKILL.md` (uppercase, fixed)
- [ ] Action files: kebab-case, prefixed by folder name — `{folder}-{action}.md`
- [ ] Anchor docs: Title Case, prefixed by Slug — `{Slug} PRD.md`, `{Slug} Plan/{Slug} Backlog.md`

## DAS user-docs file

- [ ] User-doc file exists at `docs/<domain>/DAS {Slug}.md` in the dans-anchor-system repo (dossier hub page)
- [ ] H1 of that file matches the skill name
- [ ] Listed in the [[DAS Skills]] kind index (and reachable from `DAS Docs.md`)

## Wired into the SKA Skills table at the top of `SKA.md`

**This is required for every skill that ships user docs.** The SKA Skills table is the user-facing index — a skill that isn't in it is invisible to users browsing the anchor.

- [ ] Skill is referenced from the Skills table in `~/.claude/skills/SKA.md` (or `Bespoke/Skill Agent/SKA.md`)
- [ ] Cell format: `**[[DAS {Slug}|{folder}]]**` — link target is the SKL user-doc, display alias is the folder name (so the user sees `mode`, `groom`, etc., as it appears in `/<command>`)
- [ ] Placed in the appropriate column based on the skill's purpose:
  - **Workflow** — feature, groom, land, roster, ask, crank, audit (skills that move work through states)
  - **Build / Code** — code, fortify, mint (skills that produce or harden code)
  - **Anchor / Structure** — CAB, create, migrate, rewire, rule (skills that shape anchors / structure / rules)
  - **Investigation / Coord** — parley, research, role (skills that explore or coordinate)
  - **Environment / I-O / Content** — ctrl, edit, fix, IO, MD, product, snip (skills that interact with environment, files, or external systems)
  - **Disciplines** — finalize, query, workflow, **mode** (`user_invocable: false` skills cited by other skills)
- [ ] If `user_invocable: false`: skill goes in the **Disciplines** column.
- [ ] If no SKL user-doc exists: skill is hidden from the table (the table only shows skills with user-facing docs); rewire flags this as a finding rather than fixing.

## Slug-collision warning (skip these subdirs)

- [ ] If the skill folder shares a slug with a parent-level project anchor (e.g., `cab/` ↔ `Bespoke/Skill Agent/CAB/`, `io/` ↔ `Bespoke/Skill Agent/IO/`), do NOT create `{Slug}.md` anchor root in the skill folder — it would collide on macOS case-insensitive filesystems. The project anchor at the parent level carries the slug; the skill folder has only `SKILL.md` and action files.

---

# Universal Rules

- [ ] Wiki-links in tables: always escape pipe as `\|` — `[[target\|alias]]` not `[[target|alias]]`
- [ ] Blank line before every markdown table or it will not render
- [ ] Frontmatter must have both `cab-traits:` (list) and `description:`
- [ ] H1 heading: `# {slug} — {FolderName}` when slug differs from folder name, or `# {slug}` when they match
- [ ] Dispatch table header: `-[[{slug}]]-` in first cell, `><br>:` markers in second cell
- [ ] Dispatch table separator row: `---`, `^^^`, `...`, or `+++` in left cell enables auto-management below
- [ ] **Every `.md` file inside an anchor** (not just the anchor root) has the canonical top: H1 + dispatch-table placeholder with `-[[{basename}]]-` first cell. No legacy `:>>` / `> [[parent]]` breadcrumbs, no `n::` / `desc::` inline metadata. See § Default doc top-of-file above for the placeholder form and migration rules.
- [ ] Per-row `+` suffix on wiki-link rows (e.g., `[[Name]]+`) to show grandchildren for that row
- [ ] Standard rows order: External, User, Plan, Execute, Dev, Research
- [ ] Project-specific rows go AFTER standard rows
- [ ] `.anchor` file must exist (can be empty — properties derive from folder name)
- [ ] Dispatch pages link to ALL their children — no orphan files
- [ ] Every subfolder that has files needs a dispatch page
- [ ] Every markdown file and folder inside an anchor is prefixed with `{slug}`
- [ ] Rewire adds missing canonical rows and missing items in those rows. That's all. No deletions, ever — not rows, not items, not user content.
- [ ] Rewire does not create missing files — only links existing ones
- [ ] Rewire does not modify file content — only dispatch tables and Files tree

<!-- compiled:end -->
