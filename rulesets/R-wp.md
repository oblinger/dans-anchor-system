# RULESET R-wp
include:: [[R-stream]] 
where:: `file:{anchor}/**/* WP/**, !**/DAS *.md`
description:: the `{slug} WP/` work-products zone — dated polished outputs
selector-note:: Spelled `* WP/` rather than `{slug} WP/` deliberately ([[TINK Backlog#^T164|T164]], 2026-08-08). A WP zone is a **folder** facet, so it carries its own `.anchor` and is only ever audited scoped on itself — and at that scope `{slug}` resolves to the zone's OWN folder name, since its `.anchor` declares no `slug:` and `_anchor_name` falls back to the directory name. `{slug} WP/` therefore expanded to `AIS WP WP/` and matched nothing on the one live instance. The `* WP/` form is what [[R-rocks]] already uses and what actually fires.

What `/audit` checks on an anchor's Work Products zone. Cardinality: one zone per anchor, many entries within. Format of this set: [[DAS Ruleset]].

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
