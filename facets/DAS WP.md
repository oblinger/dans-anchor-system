---
description: dated work products — papers, reports, polished outputs
group: folder
---

| -[[DAS WP]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS WP](hook://p/DAS%20WP) |
| --- | --- |
| Related | [[DAS Log]],  [[DAS Feature]],  [[DAS Brief]],  [[DAS Dispatch]],   |
| Examples | [[AIS WP\|example dispatch page]],   |
| Rules | [[R-wp]],   |
| ... |  |

# DAS WP
Facet spec for the **Work Products** zone of an anchor — dated, polished outputs (papers, reports, analyses) organized as one folder per work product under `{slug} WP/`.

**Location:** `{slug} WP/{slug} {Title}/` at the anchor root — one folder per work product, per § Location below.

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
# {slug} WP

| -[[{slug} WP]]- | : work products<br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Output]] → [DAS WP](hook://p/DAS%20WP) |
| --- | --- |
| [[2026-04-15 Security Audit]] |  |
| [[2026-03-28 Architecture Review]] |  |
| --- | |
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

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above.)*

- **This is the facet spec, not an instance** — edit here to change the *rule*; never inline a specific anchor's work-product content.
- **Inclusion test + what doesn't belong** — WP holds only **polished, dated** human+agent outputs; agent-generated reports go to `{slug} Outputs/`, feature specs to `{slug} Features/`, informal notes to the anchor page / log (see the *Distinction from Other Dated Content* table). NOT for project-wide markdown / linking rules ([[R-markdown]], CLAUDE.md), Brief-discipline rules ([[DAS Brief]]), or anchor-local maintenance content (`{slug} Rules.md` / `{slug} Decisions.md`).
- **Tooling consumers** — the `{date} {name}` naming convention and the bottom `| --- | |` auto-list marker are read by `/cab wp` and rewire/rescan; don't rename the convention or remove the marker without updating them.
- **Cross-ref integrity** — when the spec changes (location, naming, dispatch-page shape), update the example block, the *Anchor Page Row* snippet, and the *Distinction from Other Dated Content* table together — readers cite all three.
