# RULESET R-fct-icebox
include::
where:: `file: **/{slug} Icebox.md`
description:: Rules every `{slug} Icebox.md` instance must satisfy — location, cardinality, and entry format.

### RULE R-fct-icebox-01 — Location is inside the Track folder (checked)
The file lives at `{slug} Track/{slug} Icebox.md` — not at the anchor root or alongside Backlog at a different path.
**Check pattern:** path matches `*/{slug} Track/{slug} Icebox.md`.
**Why:** the Track folder groups all tracking docs together; a misplaced Icebox is not found by skills expecting the canonical path.

### RULE R-fct-icebox-02 — At most one per anchor (checked)
No more than one `{slug} Icebox.md` exists per anchor root. The facet is **optional** — most anchors do not have one.
**Check pattern:** count of `*Icebox.md` files under `{slug} Track/` ≤ 1.
**Why:** cardinality is one; two Icebox files under the same anchor produce split inventories that drift apart.

### RULE R-fct-icebox-03 — Entries are definition-list items under H2 sections (sampled)
Each frozen item is a definition-list bullet — `- **Name** — reason it's frozen` — grouped under an H2 section (e.g. `## Frozen`, `## Maybe Someday`, `## Revisit Later`). A bare unstructured list is non-conformant.
**Check pattern:** the file body contains at least one `## ` H2 section and at least one `- **…**` bullet with an em-dash.
**Why:** the definition-list + section structure lets a reader scan quickly and see the freeze reason, which determines whether a thaw trigger applies.

### RULE R-fct-icebox-04 — Items move by intent to consider, not age (stated)
Movement into or out of the Icebox is triggered by whether the user *intends to consider* the item, not by how old it is. An old item still under consideration belongs in the Backlog; a new item the user has decided is out of scope belongs in the Icebox.
**Check pattern:** no date-based or age-based pruning rule is declared in the file.
**Why:** age-based deletion defeats the "durable parking" purpose; the correct trigger for removal is genuine obsolescence, not elapsed time.
