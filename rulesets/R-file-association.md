# RULESET R-file-association
include::
where:: `anchor`
description:: Rules for the general typed-association pattern — three placement methods, cardinality→placement, parent + plural-suffix naming, one-way migration, one-form-per-parent, parent linkage, sibling-folder shape, and the citing-facet method declaration.

Embedded ruleset for the file-association discipline, co-located with the spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. These are the **general** association rules (promoted up from the dated specialization per F154); the dated-only rules live in [[R-dated-entry-stream]]. Catalog stub at [[R-file-association]] under [[R-doc]].

### RULE R-file-association-01 — Three named placement methods (stated)

The discipline defines exactly three placement methods: inline `# {Facet}` H1 (1), sibling file `{Parent} {Facet}[s].md` (2), sibling folder `{Parent} {Facet}s/` (3). Citing facets pick a subset and declare a default; no fourth method is introduced ad hoc.

**Check pattern:** for each citing facet, assert its method declaration is a subset of {1, 2, 3} with a named default.

**Why:** a bounded method set is the point — readers (and the agent) learn three shapes and recognize them everywhere. Ad-hoc methods erode the discipline.

### RULE R-file-association-02 — Cardinality drives placement (stated)

The placement method follows cardinality: single+small → method 1 (inline); single+large or a flat handful → method 2 (sibling); many+substantial → method 3 (folder). Datedness does not change this — cardinality does.

**Check pattern:** stated; a folder (method 3) holding one item, or an inline H1 dominating the parent, is a smell to flag.

**Why:** keeps placement predictable and keeps small associations from prematurely earning folders.

### RULE R-file-association-03 — Naming is parent prefix + plural facet suffix when extracted (checked)

When extracted (methods 2–3 holding multiple items): the file/folder name is `{Parent Name} {Facet}s` (plural suffix). The inline form and a single-item sidecar stay singular. Method 3's inner anchor file matches the folder name.

**Check pattern:** regex-match extracted instances against `{Parent}\s+\w+s\.md|/`; assert the method-3 anchor file matches its folder name.

**Why:** the plural signals the extracted-multiple form; the parent prefix preserves what the association is *about*.

### RULE R-file-association-04 — Migration is one-way (stated)

Associations migrate `1 → 2 → 3` as they grow. Reverse migration is allowed only as a deliberate refactor with explicit user ack; the agent never auto-downgrades.

**Why:** downgrading loses git-blame granularity (per-item history); the cost is paid once on extraction and reversing pays it again for nothing.

### RULE R-file-association-05 — One form per parent at a time (checked)

A parent has at most one materialized form of a given facet's association: inline H1 XOR sibling file XOR sibling folder. Mixed coexistence is forbidden.

**Check pattern:** per (parent, facet) pair, count materialized forms; assert ≤ 1.

**Why:** mixed forms drift — new items land in the wrong place; readers don't know which is current.

### RULE R-file-association-06 — Dispatch linkage from parent when extracted (checked)

When extracted to method 2 or 3, the parent links to it from its dispatch table (or a `(See …)` line near the top); the inline `# {Facet}` H1 is removed simultaneously.

**Check pattern:** for each extracted instance, grep the parent for a wiki-link to it AND assert no inline `# {Facet}` H1 remains.

**Why:** the link makes the extracted association discoverable; the simultaneous H1 removal enforces one-form-per-parent.

### RULE R-file-association-07 — Sibling-folder shape (checked)
check:: file_association_folder_structure

Method 3: the folder `{Parent} {Facet}s/` contains an anchor file `{Parent} {Facet}s.md` (H1 = filename) with a dispatch table of all items, PLUS one file per item. (Per-item file naming is dimension-specific — dated streams add an ISO prefix per [[R-dated-entry-stream]].)

**Check pattern:** for each method-3 folder, assert the anchor file exists, the dispatch lists every item file, and item files follow the facet's naming.

**Why:** the folder form is only useful if its structure is predictable.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella) and applies to every document (`always`). It is the **general** typed-association pattern; its dated specialization [[R-dated-entry-stream]] inherits these rules and adds reverse-chronological + ISO-naming extras.

## Adoption

A convention set on the `R-doc` umbrella — pulled into **`/audit doc`** via `R-doc`'s `include::` line. Citing disciplines/facets reference it explicitly where they constrain attachment (e.g. [[DAS dated-entry-stream]] delegates its general placement rules here).

## See also

- [[DAS file-association]] — discipline spec this ruleset enforces.
- [[DAS dated-entry-stream]] — dated specialization that inherits this ruleset.
- [[R-doc]] — documentation-conventions catalog row this stub sits under.
- [[R-dated-entry-stream]] — the dated sub-discipline's stub.
- [[DAS Rulesets]] — top-level catalog.
