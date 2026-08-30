# RULESET R-file-association
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: Rules for the general typed-association pattern — three placement methods, cardinality→placement, parent + plural-suffix naming, one-way migration, one-form-per-parent, parent linkage, sibling-folder shape, and the citing-facet method declaration.

Embedded ruleset for the file-association discipline, co-located with the spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. These are the **general** association rules (promoted up from the dated specialization per F154); the dated-only rules live in [[R-stream]]. Catalog stub at [[R-file-association]] under [[R-doc]].

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

Method 3: the folder `{Parent} {Facet}s/` contains an anchor file `{Parent} {Facet}s.md` (H1 = filename) whose **dispatch area** lists all items, PLUS one file per item. (Per-item file naming is dimension-specific — dated streams add an ISO prefix per [[R-stream]].)

The dispatch area is the masthead **table rows plus the list items below them** — both forms count. The reference instance [[HBR Features]] carries its three feature docs as a bullet list under a `^^^` auto-management separator, and four other vault folders use that shape; this rule read "dispatch table" literally until 2026-08-02 (T103a), which would have failed all five. What is NOT the dispatch area: a prose paragraph mentioning an item, and a fenced example listing one.

**Check pattern:** for each method-3 folder, assert the anchor file exists, the dispatch area lists every item file, and item files follow the facet's naming. A folder is method-3 only if its plural suffix **names a registered facet** — `facets/DAS {Facet}.md` exists.

**The plural suffix alone is evidence of nothing** ([[Tink Backlog#^T561|T561]], 2026-08-20, from [[Eli]]). This rule's checker recognised a method-3 folder by `\s+\w+s$` and nothing else, and the vault-wide count is the argument: **372 folders in scope, 271 of them failing** — a rule wrong three times out of four. What it was failing was `NJDB Databricks`, `NJDB Weights & Biases`, `@Buck Shlegeris`, `My Dates`, `Cap tables`, `SV Wings`, `Moms Files` — company names, a person, and ordinary topic folders whose last letter happens to be `s`, each told to grow a dispatch table over items it does not have. Requiring the suffix to name a registered facet leaves **100 in scope and 48 failing**, and the 48 are real: mostly `{slug} Features/` folders across the fleet with no `{slug} Features.md` index, which [[DAS Features]] does require. Nothing that was passing is lost — a folder leaving scope was either already passing or was never a facet folder.

**Two residuals, stated rather than absorbed.** *(a)* The `{Parent}` half of `R-file-association-03` is still unchecked here: requiring the prefix to match an enclosing folder or declared slug would cut scope to 53 and findings to 27, but it would also drop **75** currently-passing folders, because a multi-word facet name (`SVAR Dev Docs`, `SVW User Docs`) puts a qualifier between parent and facet and the naive split reads `SVAR Dev` as the parent. That refinement waits on the multi-word-facet question. *(b)* A singular/plural coincidence still admits a few — `2025-10-07 Derm Docs` matches because `Doc` is a facet — and *(a)* is what removes it, which is the argument for doing *(a)* properly rather than patching around it.

**The pebble stores need no clause of their own *here*.** T561 paired this rule with the `{slug} Pebbles/` store, where `stone` writes `{slug} P####.md` into the folder and keeps its control file one level up at `{slug} Pebble.md` — 19 such folders vault-wide, **19 of 19** carrying no namesake, a universal shape rather than a deviation. There is no `DAS Pebble` facet, so they leave *this* rule's scope with the other 223 and an explicit exemption would be dead code. Their **other** reported failure is real and fleet-wide, and is fixed in its own ruleset: see [[R-anchor-page]] § R-anchor-page-02.

**Why:** the folder form is only useful if its structure is predictable.

exception-grading::
  measured 2026-08-19 - ten `*Pebbles/` folders exist vault-wide (SV, SYS, MED,
      BUY, SVH, HA, FIN, Eli, NJ, HERMES) and NOT ONE carries a `*Pebbles.md`.
      `stone` writes `{slug} P####.md` into the folder and keeps the control
      file one level up, so the folder is a store, not an anchor. Re-run before
      treating this as current; it is recorded because re-deriving it costs a
      vault scan, not because of what it implies.
  note - this rule's trigger is `re.search(r"\s+\w+s$", folder)`, the folder
      NAME, with no test that it holds a facet's items. Every exception graded
      here is therefore graded against a heuristic rather than against the rule
      as written. Durable fix: [[Tink Backlog#^T561|TINK T561]]; when it lands
      these rows suppress nothing and `R-exception-discipline-07` reports them
      stale, which is the signal to delete them.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella) and applies to every document (`always`). It is the **general** typed-association pattern; its dated specialization [[R-stream]] inherits these rules and adds reverse-chronological + ISO-naming extras.

## Adoption

A convention set on the `R-doc` umbrella — pulled into **`/audit doc`** via `R-doc`'s `include::` line. Citing disciplines/facets reference it explicitly where they constrain attachment (e.g. [[DAS stream]] delegates its general placement rules here).

## See also

- [[DAS file-association]] — discipline spec this ruleset enforces.
- [[DAS stream]] — dated specialization that inherits this ruleset.
- [[R-doc]] — documentation-conventions catalog row this stub sits under.
- [[R-stream]] — the dated sub-discipline's stub.
- [[DAS Rulesets]] — top-level catalog.
