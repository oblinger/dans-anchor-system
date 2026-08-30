# RULESET R-design
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: design facet — the `{slug} Design/` folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required)

Embedded ruleset for the Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[Tink Backlog#^T208|T208]]).

### RULE R-design-01 — Folder presence IS the gate (checked)

If `{anchor}/{slug} Design/` exists, the anchor is in design-mode. The `code` trait field in `.anchor` is NOT consulted by `/design` or its sub-skills.

**Check pattern:** for each anchor referenced by `/design`, the resolution path uses `ls "{anchor}/{slug} Design"` not `grep Code .anchor`.

**Why:** structure is honest; trait fields can drift. Folder existence is observable.

### RULE R-design-02 — The PRD is present when the folder exists; every other child earns its keep (checked)
check:: design_folder_children PRD

When `{slug} Design/` exists, it contains `{slug} Design.md` (the spine — R-spine) and `{slug} PRD.md` (or the `{slug} PRD/` folder form). Nothing else is required: `{slug} Architecture.md`, `{slug} Testing.md` and the optional children appear when there is content for them, never to complete a set.

**Check pattern:** for each existing Design folder, assert the PRD exists as a file or a folder.

**Why:** ruled by Dan 2026-08-29 ([[Tink Backlog#^T625|TINK T625]]): *"the design rule should simply say documents earn their keep by need, and the only thing that's not optional is the PRD."* A thing that deserves to exist always has an answer to *what is this for*, so requiring the PRD costs nothing legitimate and catches exactly the case worth catching — something built that nobody can state the purpose of. An architecture earns its keep once the solution has enough structure to merit one. Until this day the rule demanded all four and [[Agent Recipes]] said the opposite (*"a file appears when it has content, never to complete the set"*); every agent Design folder in the vault failed it, owing fifteen documents between them that nobody was going to write. **Testing is still required, but not as a sibling document**: the PRD must *indicate* it — an inline H2 when narrow, a spine entry to `{slug} Testing.md` when it is a discipline of its own, or an explicit *"no meaningful test yet, because X"*, which is a legal answer (the `/audit q` precedent: `None` is a real recommendation, *empty* is the author not having tried). That obligation lives in [[R-prd]], where the PRD's own shape is checked, not here.

### RULE R-design-03 — Dispatch page lists every present child (sampled)

The `{slug} Design.md` dispatch table contains a wiki-link row for every `.md` file (or folder-doc) present in `{slug} Design/`, with a one-line description.

**Check pattern:** parse `{slug} Design.md`'s dispatch table; enumerate files in `{slug} Design/`; assert one-to-one cover modulo intentional exclusions (the dispatch file itself, the `.anchor` marker).

**Why:** the dispatch page is the navigation hub; missing rows hide content from the reader.

### RULE R-design-04 — Status file, when present, carries the five facet lines (sampled)
check:: status_facets_initialized prd ux architecture testing roadmap

When `{slug} Track/{slug} Status.md` exists, it carries the standard five design-facet lines (`prd::`, `ux::`, `architecture::`, `testing::`, `roadmap::`) per [[DAS Status]]. **Its absence is not a failure.** `state status <slug> show` creates the file with every facet at `none` the first time `/design` reads it, so nothing breaks when it is missing — and a Status file written only to satisfy a check is five `none` lines that lie about a design nobody has started.

Narrowed 2026-08-29 ([[Tink Backlog#^T627|T627]], on [[Atticus|Atticus]]'s report): the rule fired on exactly the trigger T625 retired for R-design-02 — *a Design folder exists* — and Dan's ruling there reaches here unchanged: documents earn their keep by need, and only the PRD is not optional. Measured 2026-08-29 across Staff: ATT, CFO and LUMEN failed it for want of a file the picker would have created on its own.

**Check pattern:** for each existing Design folder, if `{slug} Track/{slug} Status.md` exists, assert the five facets are declared (any cell value is valid). A missing file passes.

**Why:** `/design`'s picker reads Status.md — and creates it when absent. The only defect it cannot recover from is a file that exists with the lines missing.

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

Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[Tink Backlog#^T208|T208]]).

## See also

- [[DAS Design Folder]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
