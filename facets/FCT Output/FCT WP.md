---
description: dated work products — papers, reports, polished outputs
---
# FCT WP

Facet spec for the **Work Products** zone of an anchor — dated, polished outputs (papers, reports, analyses) organized as one folder per work product under `{slug} WP/`.

**Location:** `{NAME} Docs/Work Products/YYYY-MM-DD {Title}.md   (dated work product)`


Work Products — polished, dated outputs of human+agent collaboration. Papers, reports, analyses, presentations.

## Location

`{slug} WP/` at the anchor root (not inside Docs). Created on first use via `/cab wp`.

## Structure

```
{Anchor}/
├── {slug} WP/
│   ├── {slug} WP.md                         dispatch page (reverse chronological)
│   ├── 2026-03-28 Architecture Review/
│   │   └── 2026-03-28 Architecture Review.md
│   └── 2026-04-15 Security Audit/
│       ├── 2026-04-15 Security Audit.md
│       └── appendix-a.md
```

## Naming

- Folder and main file share the same name: `{date} {name}/` contains `{date} {name}.md`
- Date format: `YYYY-MM-DD`
- No slug prefix on files inside WP (date + name provides uniqueness)
- Always a folder, even for single-file work products — they often grow

## Dispatch Page

`{slug} WP/{slug} WP.md` follows the F060 top-of-doc format: H1 + dispatch-table placeholder, with the reverse chronological work-product listing folded into the dispatch table:

```markdown
# {NAME} WP

| -[[{NAME} WP]]- | ><br>: work products |
| --- | --- |
| [[2026-04-15 Security Audit]] |  |
| [[2026-03-28 Architecture Review]] |  |
| --- |  |
```

The `---` separator at the bottom enables rewire/rescan to auto-list any remaining work-product folders.

Each work-product file (`{date} {name}.md`) follows the F060 top-of-doc inside the file: H1 + dispatch-table placeholder above the work body.

## Anchor Page Row

When the WP folder is created, a **Work** row is added to the anchor dispatch table after the standard rows:

```
| Work | [[{slug} WP\|WP]] |
```

## Distinction from Other Dated Content

| Type | Location | Created by | Purpose |
|------|----------|-----------|---------|
| **WP** | `{slug} WP/` at root | `/cab wp` on request | Polished work products |
| **Outputs** | `{slug} Outputs/` in Plan | `stat add` automatically | Agent-generated reports |
| **Log** | anchor page or log file | manual | Informal notes and history |
| **Features** | `{slug} Features/` in Plan | `/code feature` | Feature design specs |

# BRIEF

- **This file is the facet spec** for the Work Products zone of an anchor — it defines the location, structure, naming, dispatch-page shape, and the anchor-page **Work** row that wires WP into the anchor. Edit here to change the *rule*; do NOT inline any specific anchor's work-product content.
- **Inclusion test:** something belongs in WP only if it is a **polished, dated output** of human+agent collaboration (paper, report, analysis, presentation). Agent-generated reports go to `{slug} Outputs/` in Plan; feature design specs go to `{slug} Features/`; informal notes go to the anchor page or a log file — see the *Distinction from Other Dated Content* table; do not blur those lines.
- **Naming is load-bearing:** folder and main file share the exact name `{date} {name}` with date in `YYYY-MM-DD`; no slug prefix on files inside WP; always a folder even for single-file work products. Renaming the convention breaks `/cab wp`, rewire/rescan auto-listing, and the dispatch page's reverse-chronological ordering.
- **The `---` separator at the bottom of the dispatch table is structural**, not decorative — it is the marker that rewire/rescan uses to auto-list any remaining work-product folders. Do not remove it.
- **NOT for**: project-wide markdown / linking rules ([[R-markdown]] and CLAUDE.md), Brief-discipline rules ([[FCT Brief]]), or anchor-local maintenance content (lives in `{NAME} Rules.md` / `{NAME} Decisions.md`).
- **When the spec changes** (e.g. WP location moves, naming changes, the dispatch-page shape is revised), update the example block, the *Anchor Page Row* snippet, and the *Distinction from Other Dated Content* table together so they stay consistent — readers cite all three.
