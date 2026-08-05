# RULESET R-facet-spec
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file: DAS *.md, DAS */DAS *.md, !DAS.md, !DAS {workflow,Linked Mode,code-repo,role,granularity,progressive-disclosure,anchor-dag,markdown,mode,verification,ask-format,rust,technical-answer,dated-entry-stream,file-association,formats}.md, !DAS State.md, !DAS Facets.md, !DAS Rulesets.md, !DAS Skills.md, !DAS Disciplines.md, !DAS Docs.md, !DAS Templates.md, !DAS Examples.md, !DAS Primitives.md, !DAS Anchor.md, !DAS Code.md, !DAS Design Docs.md, !DAS Dispatch.md, !DAS Doc.md, !DAS Output.md, !DAS Track.md, !DAS Linked Mode.md, !DAS Traits.md, !DAS Design.md, !DAS US-*.md, !DAS TSK User Guide.md, !DAS Aspects.md, !DAS Disciplines Brief.md, !DAS Dispatch Table Design.md`
description:: The rules for authoring a facet — what every `DAS <Name>.md` (a facet definition) must contain and conform to. **Distinct from the umbrella [[R-facet]]**, which aggregates each materialized facet's *own* embedded rules (so an anchor's `{slug} Backlog.md`, `{slug} Testing.md`, … get audited); `R-facet-spec` instead governs the **facet-spec documents themselves**, in the `facets/` catalog. The where-glob matches anchor-relative paths (facets/ is its own anchor, so specs sit at depth 0-1). **Depth-1 is gated to folder-form facet specs by requiring a `DAS `-prefixed parent folder (`DAS */DAS *.md`)** — a facet in folder form is always `DAS <Name>/DAS <Name>.md`, so this structurally excludes group-profile/reference docs that live in non-`DAS` subfolders (`design/<group>/DAS <Group> Design.md`, `skills/<x>/DAS <Name>.md`) without hand-listing each. **Depth-0 collisions in *other* anchors** (a discipline `disciplines/DAS <name>.md`, or a skill reference doc in its own sub-anchor like `DAS State`) are still excluded by explicit name — the anchor-relative glob can't tell them from a real `facets/DAS <Name>.md`, and the engine has no character classes. The robust end-state is to scope R-facet-spec's *adoption* to the facets anchor so the depth-0 denylist can retire (see [[TINK Backlog#^T031|T031]]); until then a new discipline/reference `DAS <Name>.md` in another anchor leaks loudly (facet rules fire on its write) until added to the exclusion list.

Embedded here per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention. Tiers: **checked** (mechanically verifiable), **sampled** (spot-checked), **stated** (a principle the author honors). The authoritative model these rules enforce is [[DAS Aspects]] § Facet + § Spec-doc structure.

## Location & registration

### RULE R-facet-spec-01 — One spec file per facet (checked)
Each facet is defined by exactly one spec doc — `facets/DAS <Name>.md` (single-file), or `facets/DAS <Name>/DAS <Name>.md` (folder form when the facet grows large, parallel to Architecture).
**Check pattern:** the facet's catalog row resolves to one `DAS <Name>.md` (or its folder-form root); no second spec defines the same facet.
**Why:** one authoritative source per facet — split or duplicate specs drift and the audit can't decide which wins.

### RULE R-facet-spec-02 — Name is the facet's name, singular (checked)
check:: facet_h1_form
The filename and H1 read `DAS <Name>`, with `<Name>` in **singular** form (the facet is used as a kind/adjective — "the Backlog facet").
**Check pattern:** H1 matches `# DAS <Name>`; `<Name>` is not a needless plural.
**Why:** facet names are used as adjectives; singular reads correctly (per the singular-naming convention) and keeps `DAS Facet` (the kind) distinct from `DAS Facets` (the index).

### RULE R-facet-spec-03 — Registered in the index (checked)
check:: facet_registered
Every facet spec has a wiki-link row in [[DAS Facets]], in the semantic group matching its category (Structure / Design / Execute / Code / User / …) — promoted out of the staging `...` row once its category is clear.
**Check pattern:** the spec's name appears as a link in exactly one [[DAS Facets]] group row.
**Why:** the index is the discovery surface; an unregistered facet is invisible to anyone browsing the catalog.

## Anchor-page top (a facet spec is itself an anchor page)

### RULE R-facet-spec-04 — Frontmatter `description:` present (checked)
check:: frontmatter_has description
The file opens with YAML frontmatter carrying a non-empty one-line `description:`.
**Check pattern:** frontmatter block exists with a `description:` value.
**Why:** the description is what surfaces in dispatch tables and search; without it the facet is a blank row.

### RULE R-facet-spec-05 — H1 → one-line summary → dispatch table (checked)
check:: facet_dispatch_top
The H1 is immediately followed (no blank line) by a one-sentence summary, then a blank line, then the dispatch table whose first row is the breadcrumb.
**Check pattern:** the line after the H1 is prose (not blank, not a table); a breadcrumb dispatch table follows.
**Why:** the standard anchor-page top — a facet spec is an anchor page and must be navigable like one (per [[DAS Anchor Page]], F060).

### RULE R-facet-spec-06 — Related row is lateral-only (sampled)
The dispatch table's `Related` row carries only lateral / cross-cutting links — never the breadcrumb ancestors, the parent, or the facet's own contents.
**Check pattern:** no `Related` entry duplicates a breadcrumb hop or the parent anchor.
**Why:** the Related row earns its space with links you can't already reach by ordinary navigation (per the anchor-page Related rule).

### RULE R-facet-spec-07 — Substantial specs carry a TLDR (sampled)
check:: facet_tldr_if_substantial
A facet spec with a non-trivial body opens its preface zone (after the dispatch table, before the first body H2) with a `**TLDR**` block per [[DAS progressive-disclosure]].
**Check pattern:** a `**TLDR**` line precedes the first body `## `; small specs (a few sentences) are exempt.
**Why:** lets a reader graze the facet's shape in five seconds without reading the whole spec.

## What a facet spec conveys — mostly via the ruleset (sections optional)

**Only two parts are *required*: the `# RULESET` (R-facet-spec-18) and the `# BRIEF` (R-facet-spec-22).** Everything in this group is content a facet spec should make *knowable* — but the required ruleset is the natural carrier for the load-bearing parts (detection, format, constraints), so dedicated prose sections for them are **optional**, not mandated.

### RULE R-facet-spec-08 — Makes the facet's identity knowable (sampled)
The spec conveys, in a sentence, the narrow aspect this facet names — via the H1 summary, an Overview, or a `## What it is`. A dedicated section is optional; the statement is not.
**Check pattern:** a one-sentence "this facet is X" is findable near the top.
**Why:** the reader must learn the facet's identity before any rule about it makes sense.

### RULE R-facet-spec-09 — Makes detection knowable (sampled)
The spec (typically its ruleset) makes clear how presence is decided. Default is **file-existence**; any other mechanism (folder-existence, capability check, …) is stated **explicitly**.
**Check pattern:** detection is findable; non-default detection is named, not assumed.
**Why:** detection is owned by the spec, not hard-coded globally — a folder or file-less facet is mis-detected if a reader assumes "look for the file" (per [[DAS Aspects]] § Facet).

### RULE R-facet-spec-10 — Makes cardinality knowable (sampled)
check:: facet_cardinality_declared
The spec makes cardinality clear — `one` (one per anchor) or `many`.
**Check pattern:** `one` / `many` (or an explicit cardinality statement) is findable.
**Why:** audits and skills behave differently for `one` vs `many`; leaving it implicit invites bugs.

### RULE R-facet-spec-11 — Makes the instance format knowable (sampled)
The spec (typically its ruleset) conveys the instance format: filename pattern, frontmatter, body requirements, naming.
**Check pattern:** the format is findable in the spec or its ruleset.
**Why:** the format is the contract an instance is audited against; without it "conformance" is undefined.

### RULE R-facet-spec-12 — Constraints stated where they exist — a section is optional (stated)
When a facet has legal-usage rules (mutual exclusion, co-requirement, format invariants) they are stated — **usually inside the ruleset**, not a separate `## Constraints` prose section. A dedicated Constraints section is **optional**, not required.
**Why:** the ruleset is the enforceable home for constraints; a parallel prose section is redundant more often than not.

### RULE R-facet-spec-13 — Expected-Usage guidance is optional (stated)
Recommended (non-binding) patterns — common combinations, typical scale, skill pairings — may be included when useful. A dedicated `## Expected Usage` section is **optional**, not required.
**Why:** guidance helps but isn't load-bearing; its absence is not a defect.

### RULE R-facet-spec-14 — Names the skills and audits that attach (sampled)
The spec names which skills write/read the facet and which audits check it (in prose or a section).
**Check pattern:** the acting skills/audits are findable.
**Why:** a facet nobody writes, reads, or checks is dead structure; the attach list is how behavior finds the facet.

### RULE R-facet-spec-15 — Triggers section only when triggers are declared (checked)
check:: triggers_section_iff_declared
A `## Triggers` section appears **only** when the facet declares behavioral triggers, with an H3 per trigger type (`### compact`, `### markdown-write`) carrying the agent-read prose (per [[DAS Aspects]] § Triggers, F091).
**Check pattern:** if `## Triggers` is present, it has ≥ 1 typed H3; if the facet declares no triggers, the section is absent (not empty).
**Why:** triggers are anchor-resident and lazily resolved from the body H3s; an empty or malformed Triggers section misfires the resolution.

## The ruleset — REQUIRED

### RULE R-facet-spec-18 — Every facet spec has a ruleset — REQUIRED (checked)
check:: facet_has_ruleset
Every facet spec has a companion `# RULESET R-<facet>` — a **standalone `rulesets/R-<facet>.md` file linked from the spec's masthead `Rules` row** (the repo default since 2026-07-13, superseding the F133 embedded default; anchor-local specs may still embed inline). Either form is the one part that makes the facet **validatable and creatable** — detection, format, and constraints in auditable form. Linked-sibling example: [[FEX Manifest]] → [[R-fex-manifest]]; embedded (anchor-local) example: [[FEX Pin]].
**Check pattern:** the spec embeds a `# RULESET R-<facet>` H1 (≥ 1 `### RULE`), or links a sibling `[[R-<facet>]]`.
**Why:** prose rots and varies; the ruleset is the single source an audit reads and an author follows to build a conformant instance. Without it we don't actually know how to validate or create the facet — so it is required, not optional. (One of the two required parts, alongside the `# BRIEF`.)

### RULE R-facet-spec-16 — Rules are enforceable statements (sampled)
Each rule (and any constraint) is phrased so an audit could validate it — a forbidden/required/exclusive/invariant statement, not vague prose.
**Check pattern:** rule bodies read as testable claims ("exactly one per anchor", "no absolute paths"), not "should generally…".
**Why:** a rule exists to be checked; an unfalsifiable one can't gate anything.

### RULE R-facet-spec-17 — Compose by default; exclude only on logical incompatibility (stated)
A mutual-exclusion rule is declared only when two things make contradictory claims about the same underlying thing — never for tidiness.
**Check pattern:** each exclusion names the *logical* conflict it resolves.
**Why:** over-restriction blocks valid, useful compositions (per [[DAS Aspects]] § Constraints governing principle).

## Facet vs Trait — don't conflate

### RULE R-facet-spec-19 — A facet is a narrow file/folder aspect, not a paradigm (stated)
If the thing is a specific file or folder, it's a Facet (here). If it names what the anchor *is* — a declared paradigm in `traits:` — it's a [[DAS Traits|Trait]], authored under `traits/`.
**Check pattern:** the spec describes a file/folder-shaped aspect, not "this anchor is a Code/Skill/… project".
**Why:** the two have different detection (file vs `traits:` lookup) and different homes; a misfiled Trait-as-Facet is detected wrong and audited wrong.

### RULE R-facet-spec-20 — Defines a kind, never an instance (sampled)
The spec defines the facet *kind*; it does not paste a project's concrete instance into itself. Worked instances/definitions are **linked** in the dispatch `Examples` row, never embedded.
**Check pattern:** no full concrete instance is inlined; examples are links.
**Why:** an embedded instance blurs spec-vs-example and rots when the example moves (the lesson [[DAS Facet]] itself follows).

## Authority & maintenance

### RULE R-facet-spec-28 — No retired location stated as live (checked)
check:: no_retired_location

A facet spec must not state a **retired** anchor location as though it were current. The one retired token today is **`{slug} Docs/`**, withdrawn 2026-08-05 ([[TINK Backlog#^T118|T118]]). Its replacements are not a rename: `Docs/{slug} Plan/` and `Docs/{slug} Design/` both collapse into **`{slug} Design/`**, `Docs/{slug} Dev/` becomes **`{slug} Dev Docs/`**, and `{slug} Outputs/` moves under **`{slug} Track/`**.

**Provenance is explicitly allowed.** A note telling a reader who finds a legacy tree that the path is superseded is what makes the retirement legible, and four such notes stand in the corpus by design ([[DAS PRD]], [[DAS Features]], [[DAS Roadmap]], [[DAS Discussion]]). The unit of judgement is therefore the **containing paragraph**, not the line: a mention accompanied by a history word (*previously*, *legacy*, *superseded*, *deprecated*, *retired*, *formerly*, *used to*, *no longer*, *migrat…*) passes; a bare location claim fails.

**Check pattern:** for each paragraph containing `{slug} Docs`, the paragraph also carries one of the provenance words. Paragraph rather than line because a provenance sentence often leads into a bulleted path, and a line-scoped check would push authors toward repeating the history in every bullet.

**Why:** the three subfolders landed in three different places, so a corpus that half-remembers the old tree files documents in three different wrong places at once — a *worse* failure than the original inconsistency. [[DAS]] is published to be read by someone with none of this vault's history; "the spec says one thing, every example does another" is the fastest way to lose that reader.

### RULE R-facet-spec-21 — The umbrella model lives in CAB Aspects (stated)
The spec does not duplicate the Aspect / Trait / Facet vocabulary, the six-section rationale, or the composability matrix — it links [[DAS Aspects]].
**Check pattern:** shared-model content is referenced, not restated.
**Why:** one source of truth for the umbrella model; copies drift from it.

### RULE R-facet-spec-22 — Every facet spec carries a `# BRIEF` — REQUIRED (checked)
check:: regex_present ^#+\s*BRIEF
The spec ends with a `# BRIEF` H1 — **agent-facing documentation** (per [[DAS Brief]]): what an agent reads *before editing* this facet spec — what belongs, what doesn't, the inclusion test, cross-reference-integrity notes. The agent is usually the maintainer, but the audience is the agent, not the user.
**Check pattern:** a `# BRIEF` H1 exists with agent-facing maintenance bullets.
**Why:** the BRIEF is how the next agent edits the spec correctly without re-deriving its conventions, and keeps foreign content from piling in. Required on every facet spec — one of the two required parts, alongside the `# RULESET`.

## Design-facet extras (when the facet is a Design doc)

### RULE R-facet-spec-23 — Phase-gated design facets carry a `status::` field (checked)
A facet that gates a design phase (Architecture, Testing, …) declares a `status::` dataview field — `drafting | in-review | accepted` — in its instance frontmatter, and the spec says so.
**Check pattern:** the spec's Format names a `status::` field with the three values, for design-gating facets.
**Why:** `status::` is the gate signal `/design` reads; a phase-gating facet without it can't unblock the next phase.

### RULE R-facet-spec-24 — Links peer facets in `## See also` (sampled)
A facet that sits among peers (the Design or Track groups) links them in a `## See also`, and names its authoring skill if one exists.
**Check pattern:** a `## See also` lists peer facets + the authoring skill (e.g. `/design testing` for [[DAS Testing]]).
**Why:** facets are read as a set; the See-also row is how a reader discovers the siblings.

### RULE R-facet-spec-25 — Masthead carries an Examples row spanning the facet's instantiation kinds (checked)
check:: facet_examples_row
The dispatch masthead includes an **`Examples`** row linking worked instances that **span the range** of how this facet is instantiated — at minimum a *minimal* and a *maximal* instantiation, plus any other meaningful breakdown (by trait, by cardinality form, by sub-kind). Each entry is a wiki-link (never an embedded instance — R-facet-spec-20), aliased to name which kind it exemplifies, e.g. `[[HBR Backlog\|minimal]]`, `[[SKA Backlog\|maximal]]`.
**Check pattern:** the masthead has an `Examples` row carrying at least one wiki-link.
**Why:** a reader learns a facet fastest from real instances at the edges of its range — one example shows the shape, the spread shows the variation the format must absorb. (Worked-example facets that *are* the instance, e.g. those under `examples/`, are exempt; this governs the `facets/` catalog.)

### RULE R-facet-spec-26 — A body reference example is live markdown, never fenced (stated)
Usually a facet spec carries **no** reference example in its body — the worked instances are linked in the Examples row (R-25). If a spec does inline a small reference example *of markdown*, it is written as **live markdown** (so its wiki-links, headings, and tables render), never wrapped in a triple-backtick code fence — a fence makes markdown inert (per [[DAS markdown]] R-markdown-11). Code fences stay correct for literal **non-markdown** content (shell, JSON, a `key: value` data file, a file tree).
**Why:** a fenced markdown "example" renders as dead text — links go inert, structure doesn't show — defeating its purpose. Prefer a linked instance; inline only when a tiny illustration genuinely helps, and keep it live.

### RULE R-facet-spec-27 — Standalone facet examples carry the `FEX` prefix, in the facet-group folder (checked)
A worked example that is **not** a natural instance in a project world (a dispatch-table gallery, a layout exemplar) is a standalone teaching artifact. It is named **`FEX <Name>.md`** (`FEX` = example, parallel to `DAS` = spec) and lives as a plain file **in the facet's group folder** — `facets/DAS <Group>/FEX <Name>.md`, beside the `DAS` specs. It does **not** get its own anchor folder; a set of related ones may be gathered by a `FEX <Group>` gallery page in that folder. Examples that are natural project instances (`HBR CLI`, `SKA Backlog`) keep the project slug and live in that project world — this rule governs only the standalone kind.
**Check pattern:** a facet-teaching example under `facets/**/` is named `FEX <Name>.md`, sits inside a `DAS <Group>` folder, and has no sibling `.anchor` promoting it to its own anchor.
**Why:** the prefix makes example-vs-spec legible at a glance, and co-locating in the existing group anchor gives cross-facet examples a home without spawning a per-facet anchor for each.
