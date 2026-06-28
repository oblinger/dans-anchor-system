---
description: dated work products — papers, reports, polished outputs
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT WP](hook://p/FCT%20WP)

# FCT WP
Facet spec for the **Work Products** zone of an anchor — dated, polished outputs (papers, reports, analyses) organized as one folder per work product under `{slug} WP/`.

**Related:** [[FCT Log]],  [[FCT Feature]],  [[FCT Brief]],  [[FCT Dispatch]]
**Examples:** [[AIS WP\|example dispatch page]]

**Location:** `{NAME} Docs/Work Products/YYYY-MM-DD {Title}.md   (dated work product)`

Work Products — polished, dated outputs of human+agent collaboration. Papers, reports, analyses, presentations.

**Cardinality:** one `{slug} WP/` zone per anchor (the folder + dispatch page), containing **many** individual dated work-product entries.

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

| -[[{NAME} WP]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Output]] → [FCT WP](hook://p/FCT%20WP)<br>: work products |
| --- | --- |
| [[2026-04-15 Security Audit]] |  |
| [[2026-03-28 Architecture Review]] |  |
| --- | |

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

# RULESET R-wp
include::
where:: file:{ANCHOR}/{NAME} WP/**/*
description:: the `{NAME} WP/` work-products zone — dated polished outputs

What `/audit` checks on an anchor's Work Products zone. Cardinality: one zone per anchor, many entries within. Format of this set: [[FCT Ruleset]].

### RULE R-wp-01 — `{slug} WP/` lives at the anchor root with one dispatch page (checked)

The Work Products zone is `{slug} WP/` at the anchor root (not inside `Docs/`), containing a single `{slug} WP.md` dispatch page plus per-work-product folders.

**Check pattern:** `{slug} WP/{slug} WP.md` exists at the anchor root.

### RULE R-wp-02 — Folder and main file share the dated name (checked)

Each work product is a folder `YYYY-MM-DD {Title}/` containing `YYYY-MM-DD {Title}.md` of the same name; the date is `YYYY-MM-DD`; files inside WP carry no slug prefix (date + name gives uniqueness).

**Check pattern:** each WP folder name matches `^\d{4}-\d{2}-\d{2} `; its main file basename equals the folder name.

### RULE R-wp-03 — Always a folder, even for a single-file work product (stated)

A work product is always a folder (it often grows appendices), never a bare file directly under `{slug} WP/`.

### RULE R-wp-04 — Dispatch page is reverse-chronological and ends with the `---` auto-list marker (checked)

`{slug} WP.md` follows F060 (H1 + dispatch placeholder), lists work products newest-first, and ends with a `| --- | |` separator so rewire/rescan auto-lists remaining folders.

**Check pattern:** the dispatch table's last row is the `---` auto-list separator; entries are in descending date order.

### RULE R-wp-05 — Anchor page carries a `Work` row when the WP zone exists (checked)

When `{slug} WP/` exists, the anchor dispatch table carries a `| Work | [[{slug} WP\|WP]] |` row.

**Check pattern:** `{slug} WP/` exists ⇔ the anchor page has a `Work` row linking it.

# BRIEF

- **This file is the facet spec** for the Work Products zone of an anchor — it defines the location, structure, naming, dispatch-page shape, and the anchor-page **Work** row that wires WP into the anchor. Edit here to change the *rule*; do NOT inline any specific anchor's work-product content.
- **Inclusion test:** something belongs in WP only if it is a **polished, dated output** of human+agent collaboration (paper, report, analysis, presentation). Agent-generated reports go to `{slug} Outputs/` in Plan; feature design specs go to `{slug} Features/`; informal notes go to the anchor page or a log file — see the *Distinction from Other Dated Content* table; do not blur those lines.
- **Naming is load-bearing:** folder and main file share the exact name `{date} {name}` with date in `YYYY-MM-DD`; no slug prefix on files inside WP; always a folder even for single-file work products. Renaming the convention breaks `/cab wp`, rewire/rescan auto-listing, and the dispatch page's reverse-chronological ordering.
- **The `---` separator at the bottom of the dispatch table is structural**, not decorative — it is the marker that rewire/rescan uses to auto-list any remaining work-product folders. Do not remove it.
- **NOT for**: project-wide markdown / linking rules ([[R-markdown]] and CLAUDE.md), Brief-discipline rules ([[FCT Brief]]), or anchor-local maintenance content (lives in `{NAME} Rules.md` / `{NAME} Decisions.md`).
- **When the spec changes** (e.g. WP location moves, naming changes, the dispatch-page shape is revised), update the example block, the *Anchor Page Row* snippet, and the *Distinction from Other Dated Content* table together so they stay consistent — readers cite all three.
