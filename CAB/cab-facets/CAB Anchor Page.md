---
description: anchor page format — the {slug}.md entry point
---
# CAB slug Page

**Location:** `{NAME}.md`


The primary entry point for an anchor: `{NAME}.md`. Contains the breadcrumb, a dispatch table, and optionally a heading with a description property and additional content.

**Working example:** [`~/.claude/skills/CAE/CAE.md`](../../CAE/CAE.md) — a complete, self-consistent anchor page in the canonical reference anchor. Use CAE when you need to see the actual file; use the reference below for a quick look.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---


# CAE — CAE example

| -[[CAE]]-                    | ><br>:                                                                                                                                    |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| External                     | [Repo](https://github.com/oblinger/cae-example), [Project Page](https://oblinger.github.io/gitproj/cae-example/)                          |
| [[CAE User/CAE User\|User]]+ | [[CAE User Guide\|User Guide]], [[CAE Cards\|Cards]]                                                                                      |
| [[CAE Plan\|Plan]]+          | [[CAE PRD\|PRD]], [[CAE System Design\|System Design]], [[CAE UX Design\|UX]], [[CAE Features\|Features]], [[CAE Discussion\|Discussion]] |
| [[CAE Plan\|Execute]]        | [[CAE Inbox\|Inbox]], [[CAE Open Questions\|Open Q]], [[CAE Backlog\|Backlog]], [[CAE Roadmap\|Roadmap]]                                  |
| [[CAE Dev/CAE Dev\|Dev]]+    | [[CAE Files\|Files]], [[CAE Architecture\|Architecture]]                                                                                  |
| Research                     | [[CAE Research\|Research]], [[CAE References\|References]], [[CAE Related Work\|Related Work]]                                            |
| ...                          |                                                                                                                                           |

*NOTE: Omit rows that aren't relevant for a given anchor type. Row labels (User, Plan, Dev) are wiki-links to the sub-folder dispatch pages — clicking them shows just that section's files.


---



# Format Specification

## Naming

An anchor has a **name** — the identifier used for its files and references:

- **slug** (optional) — A short uppercase code like `CLF`, `DMUX`, `HA`. Used when brevity matters.
- **Full Name** — The complete name in Title Case (e.g., "Claudifier", "2026 Daves Finances"). Always present.

If a slug exists, it is the `{NAME}` used for file naming (`{slug}.md`, `{slug} Docs/`). If no slug, the full name is used.

**Every markdown file and folder inside an anchor is prefixed with `{NAME}`** to avoid collisions in the shared Obsidian namespace. This applies to files, folders, and nested files alike (see [[CAB Naming Conventions]] for the full rule):
- `{NAME} PRD.md`, `{NAME} Todo.md`, `{NAME} Roadmap.md`
- `{NAME} Docs/`, `{NAME} Dev/`, `{NAME} bio/`
- `{NAME} bio/{NAME} Chemistry.md` — nested files still carry the prefix

## Format

```
---
description: One-line description of the anchor
cab-type: code
---

# {slug} — {Full Name}

| -{NAME}-       | ><br>: short description                      |
| -------------- | --------------------------------------------- |
| ...            |                                               |
```

## Heading

- **With slug**: `CLF — Claudifier` (as H1 heading)
- **Without slug**: `2026 Daves Finances` (as H1 heading)

## Description Property

The `description:` field goes in the YAML frontmatter (not inline). This is machine-readable and visible to Obsidian's metadata system.

```yaml
---
description: macOS enhancements to speed the use of Claude Code
cab-type: code
---
```

**Note:** Older anchors may use `desc::` inline after the heading. This is deprecated — migrate to `description:` in frontmatter.

## Dispatch Table

The anchor page uses a dispatch table to organize links to all related pages. The format follows the [[md dispatch-table]] convention:

- **Top-left cell** — `-[[{NAME}]]-` (wiki-link wrapped in dashes)
- **Top-right cell** — `>` for breadcrumb and `:` for description, separated by `<br>` (e.g., `><br>: short description`)
- **Body rows** — each row groups related docs. Row labels link to the sub-folder dispatch page when one exists.
- **External row** — plain text label in column 1, URL or links in column 2

**Table formatting:** Tables MUST have a blank line before them or they won't render. Escape the pipe in wiki-link aliases inside tables: `[[target\|alias]]` not `[[target|alias]]`. An unescaped `|` breaks the table column.

### Separators and Auto-Management

The table has two zones separated by a marker row:

- **User zone** (above the separator) — fully user-controlled. The system only strikes through deleted links.
- **System zone** (below the separator) — auto-managed. Wiped and regenerated on every rebuild with children not already listed in the user zone.

| Separator | Meaning |
|-----------|---------|
| `---` | Auto-list remaining children alphabetically with descriptions |
| `^^^` | Same, reverse alphabetical (dates float to top) |
| `...` | Compact — single row with comma-separated links |
| `+++` | Auto-list with grandchildren instead of descriptions |
| `!!!` | Clip — delete everything below (including itself). One-shot. |

Tables without a separator are frozen — the system won't add or remove rows.

### Per-Row Grandchildren (`+` suffix)

Append `+` after a wiki link in the left column to show that command's children in the right column:

```markdown
| [[CAE Dev/CAE Dev\|Dev]]+ | [[CAE Files\|Files]], [[CAE Architecture\|Architecture]] |
```

The `+` is outside the `]]` — it's a directive to the system, not part of the link.

### Standard Rows

| Row | Row label links to | Contents | Part |
|-----|-------------------|----------|------|
| **External** | (plain text) | Repo URL, project page URL | [[CAB Code Repository]], [[CAB Documentation Site]] |
| **User** | `[[{NAME} User/{NAME} User\|User]]` | User Guide, Cards | [[CAB Module Doc]], [[CAB Cards]] |
| **Plan** | `[[{NAME} Plan\|Plan]]` | PRD, System Design, UX, Features, Discussion | [[CAB PRD]], [[CAB System Design]], [[CAB UX Design]], [[CAB Features]], [[CAB Discussion]] |
| **Execute** | `[[{NAME} Plan\|Execute]]` | Inbox, Open Questions, Backlog, Roadmap | [[CAB Inbox]], [[CAB Open Questions]], [[CAB Backlog]], [[CAB Roadmap]] |
| **Dev** | `[[{NAME} Dev/{NAME} Dev\|Dev]]` | Files, Architecture, module docs | [[CAB Files]], [[CAB Module Doc]] |
| **Research** | (plain text) | Research notes, references, related work | [[CAB Research]] |

### Row Labels as Links

The row labels **User**, **Plan**, and **Dev** are wiki-links to their sub-folder dispatch pages:

```markdown
| [[CAE User/CAE User\|User]]   | [[CAE User Guide\|User Guide]], [[CAE Cards\|Cards]]   |
| [[CAE Plan\|Plan]]             | [[CAE PRD\|PRD]], [[CAE System Design\|System Design]] |
| [[CAE Dev/CAE Dev\|Dev]]       | [[CAE Files\|Files]], [[CAE Architecture\|Architecture]]|
```

Clicking the row label navigates to the sub-folder dispatch page, which has a complete list of that section's files. The inline links on the right are just highlights — the dispatch page is the authoritative index.

### Sub-Folder Dispatch Pages

Each Docs sub-folder has its own dispatch page that lists all its children:

| Page | Location | Lists |
|------|----------|-------|
| `{NAME} Plan.md` | `{NAME} Docs/{NAME} Plan/` | PRD, System Design, UX, Discussion, Roadmap, Backlog, Inbox, Open Questions, Features |
| `{NAME} Dev.md` | `{NAME} Docs/{NAME} Dev/` | Files, Architecture, all module docs |
| `{NAME} User.md` | `{NAME} Docs/{NAME} User/` | User Guide, any other user-facing docs |

These are the files that the row labels link to. See [[CAB Docs]] for the full dispatch tree structure.

Not all rows are required — omit rows that aren't relevant for the anchor type. Simple anchors may have no dispatch table at all.
