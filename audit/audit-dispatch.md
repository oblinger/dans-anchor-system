# /audit dispatch — build / repair an anchor's dispatch table (fix-by-default)

Takes one anchor (or folder) and brings its **dispatch table** to good form — the **Masthead** (breadcrumb + anchor-kind structural rows + curated one-off links) followed by the optional **Member zone** (member list / member groups, manual / auto / hybrid). **Fixes by default** — like `/audit q`, it applies the repair rather than just reporting it, because dispatch-table shape is mechanical to get right. Low-confidence choices (grouping categories, structural-vs-member ambiguity) surface to the user; everything mechanical is applied.

Enforces the structure spec'd in [[CAB Dispatch Table]] (see [[F155 — Dispatch-table structure spec + CAE worked examples|F155]] for the Masthead + Member-zone model). The per-anchor counterpart of the vault-wide walk defined in [[anchor-dag]]: SYS owns whole-vault connectivity; `/audit dispatch` owns one table's shape.

## When to use

- `/audit dispatch <anchor>` — repair one anchor's dispatch table.
- `/audit dispatch` (in an anchor's cwd) — repair the current anchor.
- Called by the [[anchor-dag]] walk to fix a node's down-links + table form.
- Add `dry` anywhere in the args to report the proposed table without writing it.

## Distinction from `/audit structure`

`/audit structure` *diagnoses* broad structural issues across an anchor (missing files, broken links, orphans) and files a backlog row. `/audit dispatch` *fixes* exactly one thing — the **shape of one dispatch table** — by default. Use `/audit dispatch` to make a table good; use `/audit structure` to find what's wrong across the anchor.

## Runbook

### 1. Read the anchor
- Resolve the anchor folder (walk up to `.anchor` if not given).
- Read the `.anchor` (slug, **traits** — esp. `Collection`, the identity trait, `Code`/`Topic`/etc.).
- Enumerate **on-disk children**: sub-anchors (folders with `.anchor`), key docs, sub-folders with their own dispatch pages.
- Read the **current dispatch table** (if any) on the anchor page.

### 2. Compute the Masthead
The fixed top block — always present:
1. **Breadcrumb row** — `| -[[{NAME}]]- | → [[kmr]] → … → [{NAME}](hook://…) |`. Fix the parent chain to match the anchor's actual location (the up-edge of [[SYS Anchor DAG]]).
2. **Structural rows** — the anchor-kind standard rows. For a `Code` anchor: `Design` / `User` / `Dev` rows linking to its sub-folder dispatch pages (per [[CAB Anchor Page]]). For a `Topic` anchor: its sub-topic routing rows. Include only rows whose target sub-folders exist.
3. **Curated one-off links** — preserve any hand-added links already in the table that don't match a structural or member row (the user pinned them on purpose). Never drop curated links.

### 3. Compute the Member zone (only if the anchor is a Collection)
If the anchor has the `Collection` trait (or is clearly an enumeration of homogeneous children), render its **members** below the Masthead:
- **member list vs member groups** — flat list if ≤ 15 members; **grouped** if > 15 (per [[progressive-disclosure]]'s size rule + [[granularity]]). For groups, derive categories from the members (sub-folder, name-prefix, date-bucket) — *this categorization is the low-confidence part; surface it.*
- **manual / auto / hybrid** — if members are uniform and order doesn't matter, emit an **auto** form (`---` separator → children auto-list, or `...` compact). If the user has pinned/ordered rows, keep them **manual** above a `---` auto-fill line (**hybrid**). Mark expandable groups with `+`.
- **dated members** — if members are dated ([[dated-entry-stream]]), list newest-first with the ISO-prefixed names.

### 4. Diff and apply (fix-by-default)
- Diff the **ideal** table (Masthead + Member zone) against the **current** table.
- **Apply mechanically** (no ask): add missing child down-links; fix the breadcrumb; apply the grouping threshold; remove rows pointing at deleted children; normalize the table form per [[md dispatch-table]] (cell shape, pipe-escapes, figure-space TOC).
- **Surface (don't auto-decide)**: grouping category names when > 15 members; any child that's ambiguous between a structural row and a member; any curated link that now looks stale. Present these as a short list for the user to confirm/redirect.

### 5. Report
```
/audit dispatch — {anchor}
  Applied: +N child links, breadcrumb fixed, grouped {M} members into {K} categories.
  Confirm: category names {…}? stale curated link [[X]] — keep or drop?
```
On `dry`: print the proposed table instead of writing it.

## Confidence model

Mirrors [[anchor-dag]]'s two-table report at single-anchor scope: **mechanical fixes applied silently** (missing links, breadcrumb, threshold, normalization); **semantic choices surfaced** (group categories, structural-vs-member ambiguity, stale-curated-link calls). Loop until the table is clean, same discipline as `/audit q`.

## Related

- [[CAB Dispatch Table]] — the Masthead + Member-zone structure this enforces.
- [[CAB Anchor Page]] — breadcrumb + structural-row conventions.
- [[progressive-disclosure]] — member list vs member groups (List / Grouped, > 15 rule).
- [[Collection]] — the trait that means "this anchor has a Member zone."
- [[granularity]] — compact → grouped graduation.
- [[anchor-dag]] — the corpus-level discipline whose walk calls this per anchor ([[SYS Anchor DAG]] is this vault's application of it).
- [[F155 — Dispatch-table structure spec + CAE worked examples|F155]] — the full structure spec this enforces (pending).
