# RULESET R-openspec
include::
description:: OpenSpec mappability guards — the constraints that keep DAS structure mechanically projectable onto the OpenSpec layout (specs / changes / templates / schema.yaml), so the future TAS extraction stays a filter, not a rewrite.

Standing constraint per [[SKA PRD]] § System Layers & the Adoption Ladder (ratified 2026-07-12): TAS *declares* the OpenSpec standard, and every new piece of DAS structure must stay mappable onto OpenSpec's layout. Verdict + gap analysis: [[SKA OpenSpec Compatibility]]. Conversion itself is [[F230 — OpenSpec conversion|F230]]; these rules only guard mappability in the meantime. OpenSpec reference: the canonical repo `Fission-AI/OpenSpec` (docs/concepts.md for the spec/change formats, schemas/spec-driven/schema.yaml for artifact declarations).

### RULE R-openspec-01 — OpenSpec-reserved names stay unsquatted (checked)

The DAS repo root carries no top-level `specs/`, `changes/`, `openspec/`, or `project.md` — and no `config.yaml` with non-OpenSpec semantics — until F230 introduces them with their OpenSpec meanings (behavioral specs, change folders, project context). Squatting a reserved name with other content would make the eventual conversion a rename instead of a drop-in.

**Check pattern:** list the repo root; fail if any of `specs`, `changes`, `openspec`, `project.md` exists, or `config.yaml` exists without an OpenSpec project declaration.

**Why:** OpenSpec ignores unknown siblings but owns these exact names; keeping them free is what makes F230 additive.

### RULE R-openspec-02 — Every template binds 1:1 to a facet spec (checked)

Every `templates/<name>.md` (excluding the pattern spec `DAS Templates.md`) has a same-named facet spec `facets/DAS <Name>.md`, title-cased from the bare template name (`backlog.md` ⟷ `DAS Backlog.md`). OpenSpec has no bare templates folder — every template must be declared by a `schema.yaml` artifact (`id` / `generates` / `template` / `instruction`), and the 1:1 correspondence is exactly the data that declaration is generated from.

**Check pattern:** for each file in `templates/*.md` except `DAS Templates.md`, verify `facets/DAS <Titlecased-name>.md` exists; fail on any orphan template (and flag facet specs whose declared template is missing, once hub tables carry that link).

**Why:** without the pairing, the `schema.yaml` export needs hand-authoring — the projection stops being mechanical.

### RULE R-openspec-03 — Templates are provenance-clean skeletons (stated)

A committed template carries the bare `:>>` breadcrumb marker (per the F229 Decision B: HookAnchor expands it locally), never an expanded vault breadcrumb (`:>> [[kmr]] → [[SYS]] → …`) and never personal refs (`[[SKA …]]`, `F<NNN>` feature links, user-specific paths). Templates are the exported OpenSpec surface; personal provenance in them leaks Dan's vault into every adopter's skeleton. Enforce at the publish/export boundary, not on-write — the local ha daemon legitimately expands the marker in the working checkout, and fighting it on-write is a known losing loop.

**Why:** provenance legibility (ratified discipline #3) — every file must land classifiable as generic vs personal, and templates must land generic.

### RULE R-openspec-04 — Facet normative constraints live in RULE blocks (stated)

A facet spec's checkable structural constraints live in its `# RULESET R-<facet>` block as `### RULE` headings (format per [[DAS Ruleset]]), not only in loose body prose. The RULE heading is the unit that exports to an OpenSpec `### Requirement:`; a constraint that exists only as prose is invisible to the projection and silently drops out of the exported spec.

**Why:** the facet → spec mapping is heading-driven; prose-only requirements make the export lossy.

### RULE R-openspec-05 — Checked rules carry a scenario seed (sampled)

Every RULE whose enforcement tag is `(checked)` or `(sampled)` carries a `check::` binding or a `**Check pattern:**` line describing the concrete pass/fail observation. OpenSpec hard-errors on an added or modified requirement without at least one `#### Scenario:` (the accepted scenario tax); the check seed is the material a Given/When/Then scenario is generated from at export.

**Check pattern:** for each `### RULE … (checked)` / `… (sampled)` heading in `rulesets/` and facet-embedded RULESET blocks, verify the rule body (heading to next heading) contains `check::` or `**Check pattern:**`.

**Why:** a checked rule with no stated check cannot produce a scenario — the export would fail their validator.

### RULE R-openspec-06 — Feature docs keep the change-folder partition (stated)

A feature doc keeps its proposal-material (`## Summary`), task-material (`## Execution Plan` or equivalent plan section), and design-material (`## Decisions`, `## Design notes`) in separate H2 sections. F230 converts a feature into an OpenSpec change folder by cutting the doc into `proposal.md` / `tasks.md` / `design.md`; interleaving the three concerns under one heading turns that mechanical cut into an editorial rewrite.

**Why:** feature ≈ change is the core F229 noun-mapping; the partition is what keeps it a file split rather than a rewrite.

### RULE R-openspec-07 — No new nesting in kind folders (stated)

New facet, discipline, ruleset, and template spec files land at their kind root (`facets/DAS X.md`, `disciplines/DAS X.md`, `rulesets/R-x.md`, `templates/x.md`) — flat-by-kind per the ratified Q2a decision. The surviving legacy category folders (`facets/FCT */`, `disciplines/DSC */`) are tracked F229 migration debt, not precedent; skill-part subfolders deliberately kept per the batch map are exempt. Flat kinds are what let the TAS extraction and the `schema.yaml` projection enumerate a kind by listing one directory.

**Why:** nesting reintroduces the folder-taxonomy the Q2a decision retired and breaks the one-directory-per-kind enumeration the projection assumes.

### RULE R-openspec-08 — Conformant dirs follow OpenSpec exactly, once they exist (stated)

When F230 lands `specs/` + `changes/`: each capability's file is named exactly `spec.md`; requirements use `### Requirement:` headings with RFC-2119 wording and at least one `#### Scenario:` block each; change deltas sit under `## ADDED Requirements` / `## MODIFIED Requirements` / `## REMOVED Requirements`; completed changes archive to date-prefixed folders under `changes/archive/`. Conformance inside these directories is total — anything DAS-specific rides alongside (`.anchor`, design fan-out), never inside the OpenSpec-owned files' required structure. Verified mechanically by `openspec validate --strict` once the dirs exist.

**Why:** these two directories are the conformance boundary — partial conformance inside them is nonconformance to their tooling.
