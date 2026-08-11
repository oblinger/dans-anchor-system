# RULESET R-design
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: design facet — the `{slug} Design/` folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required)

Embedded ruleset for the Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[TINK Backlog#^T208|T208]]).

### RULE R-design-01 — Folder presence IS the gate (checked)

If `{anchor}/{slug} Design/` exists, the anchor is in design-mode. The `code` trait field in `.anchor` is NOT consulted by `/design` or its sub-skills.

**Check pattern:** for each anchor referenced by `/design`, the resolution path uses `ls "{anchor}/{slug} Design"` not `grep Code .anchor`.

**Why:** structure is honest; trait fields can drift. Folder existence is observable.

### RULE R-design-02 — Required children present when folder exists (checked)
check:: design_folder_children PRD Architecture Testing

When `{slug} Design/` exists, the folder contains at minimum: `{slug} Design.md`, `{slug} PRD.md`, `{slug} Architecture.md`, `{slug} Testing.md`.

**Check pattern:** for each existing Design folder, assert the four files exist (or `{slug} Architecture/` folder form, per CAB Architecture).

**Why:** these three children carry the load-bearing design content. Missing any of them means the anchor advertises a design process it doesn't deliver.

### RULE R-design-03 — Dispatch page lists every present child (sampled)

The `{slug} Design.md` dispatch table contains a wiki-link row for every `.md` file (or folder-doc) present in `{slug} Design/`, with a one-line description.

**Check pattern:** parse `{slug} Design.md`'s dispatch table; enumerate files in `{slug} Design/`; assert one-to-one cover modulo intentional exclusions (the dispatch file itself, the `.anchor` marker).

**Why:** the dispatch page is the navigation hub; missing rows hide content from the reader.

### RULE R-design-04 — Status file initialized when Design folder exists (sampled)
check:: status_facets_initialized prd ux architecture testing roadmap

When `{slug} Design/` exists, `{slug} Track/{slug} Status.md` exists with the standard five design-facet lines (`prd::`, `ux::`, `architecture::`, `testing::`, `roadmap::`) per [[DAS Status]].

**Check pattern:** for each existing Design folder, assert `{slug} Track/{slug} Status.md` exists with the five facets declared (any cell value is valid; absence of the file is the failure).

**Why:** `/design`'s picker reads Status.md; missing file means the picker can't auto-dispatch.

### RULE R-design-05 — `code` trait is deprecated as a `/design` gate (stated)

New anchors don't add `code` to `.anchor` `traits:` to enable `/design`. Existing anchors with `code` aren't broken; F140 sweep retires the trait from anchors that have a Design folder.

**Check pattern:** stated for now; F140 sweep mechanically retires the trait field.

**Why:** the Code trait was a misnomer — it gated "designed lifecycle" via "is this code," which is the wrong axis. Folder presence is the right signal.

### RULE R-design-06 — Optional children only when applicable (stated)

`{slug} UX Design.md` exists when the anchor has user-facing interface; `{slug} API.md` when public surface is contract; `{slug} CLI.md` when ship a CLI; `{slug} Interface.md` when layer contract. Don't author empty optionals.

**Check pattern:** for each optional child present, sample its body — bare H1 + description with no content is a creation-without-commitment failure mode.

**Why:** empty optional facets pollute the dispatch and confuse readers. Author them when you have content; omit them otherwise.

### RULE R-design-07 — Scaffolding creates pre-wired structure, not bare folder (sampled)

When `/design` scaffolds a Design folder, the operation creates all required children with their required-section spines populated (H1 + description + dispatch + required H2 stubs), not just an empty folder.

**Check pattern:** sample freshly-scaffolded Design folders; assert each required child has its required-H2 stubs (per its facet spec).

**Why:** dispatch links work from day one; user has obvious places to add content; "file moved / link broken" bugs avoided.

### RULE R-design-08 — No empty/boilerplate Design folder; presence asserts a maintained design (checked)

The `{slug} Design/` folder exists **iff** the anchor has real design content — a PRD, design docs, or feature docs (feature docs are themselves design artifacts and migrate INTO the Design folder). A folder containing only template boilerplate (empty `prd`/`plan`/`principles`/`discussion` stubs) does **not** count as a design: during migration, **wipe the boilerplate and omit the Design folder entirely**. Add the folder later, when the first real design or feature doc lands — or via `/design` scaffolding (R-design-07), which is the user's explicit commitment-to-design and the one case where a freshly-spined folder is expected before content arrives.

**Check pattern:** for each `{slug} Design/`, assert at least one child carries distinct authored content (not a bare H1 + description stub); a folder whose every child is boilerplate — and that was not just scaffolded by `/design` — is a violation: remove it.

**Why:** folder presence is a trait (cf. R-design-01) — its existence tells the reader "this anchor has a maintained design." An empty placeholder folder lies about that state and clutters the tree; absence honestly signals "not yet designed."

## Adoption

Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[TINK Backlog#^T208|T208]]).

## See also

- [[DAS Design Folder]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
