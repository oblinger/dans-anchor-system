---
description: "the Facet primitive — what a facet is and how to write its spec"
---
# FCT Facet
A narrow, usually file-based aspect of an anchor — and the spec for how to write one.

| -[[FCT Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [FCT Facet](hook://p/FCT%20Facet)<br>: the Facet primitive — what a facet is and how to write its spec |
| --- | --- |
| Related | [[FCT Skill]],  [[FCT Ruleset]],  [[FCT Facets]] (the index),  [[CAB Aspects]], |
| Examples | [[FEX Manifest\|single-file, one]],  [[FEX Pin\|single-file, many]],  [[FEX Bundle\|folder, many]],   |

# Facet Document Structure
A facet spec is one file (`facets/FCT <Name>.md`), authoritative for that facet. Its parts, top to bottom — densest first, per [[DSC progressive-disclosure]]:

- **H1** — `# FCT <Name>`: the slug-name and the full name.
- **One-line summary** — a single sentence on the line directly under the H1 (no blank line between).
- **Dispatch table** — the breadcrumb row, then `Related` (lateral links only) and `Examples`.
- **Document structure** — this dense outline, placed first so a reader sees the doc's shape before any prose.
- **Overview** — a short paragraph: what the facet is and what it's for. *(Optional.)*
- **The Aspect contract** — content the body usefully conveys, mostly via the rule set (section shapes vary; **not** fixed H2s; all optional): what it is · how it's detected (+ cardinality `one` / `many`) · format · constraints · expected usage · skills and audits that attach · triggers.
- **`# RULESET R-<facet>`** — **REQUIRED.** The embedded rule set: how to validate and create the facet — detection, format, and constraints in auditable form (e.g. [[R-fex-manifest]]). It's how we know what the facet is and how to check it.
- **`# BRIEF`** — **REQUIRED.** Agent-facing documentation (per [[FCT Brief]]) — what an agent reads before editing this facet. (Agent ≈ maintainer, but the audience is the agent, not the user.)

For a worked facet, open an example in the dispatch table above — there is no embedded copy here, because a facet is itself a full anchor page and embedding one inside this spec just blurs example-vs-spec. The enforceable form of the rules below is the embedded **`R-facet-spec`** rule set.


# Facet Overview
A **facet** is a narrow, usually file-based aspect of an anchor — one specific structural feature (a `Backlog` file, an `Architecture` doc, a website subfolder), defined by its own spec doc and detected (by default) through file-existence. This page is the spec for *the facet kind itself*: what a facet is and the shape every facet spec doc takes. It is the singular **definition**; [[FCT Facets]] (plural) is the **index** of all concrete facets.

A facet **defines a kind**. The concrete `<NAME> Backlog.md` inside a real project is an *instance* of the Backlog facet, not a facet itself — keep the two apart.

Facets are one of the two kinds of [[CAB Aspects|Aspect]] — the narrow, file-based kind; the broad declared-paradigm kind is the [[CAB Traits|Trait]] (full distinction: [[CAB Aspects]] § Trait vs Facet). The shared model lives in [[CAB Aspects]]; this page is the facet-authoring view of it.


# RULESET R-facet-spec
include::
where:: file:facets/FCT *.md
description:: The rules for authoring a facet — what every `FCT <Name>.md` (a facet definition) must contain and conform to. **Distinct from the umbrella [[R-facet]]**, which aggregates each materialized facet's *own* embedded rules (so an anchor's `{NAME} Backlog.md`, `{NAME} Testing.md`, … get audited); `R-facet-spec` instead governs the **facet-spec documents themselves**, in the `facets/` catalog.

Embedded here per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention. Tiers: **checked** (mechanically verifiable), **sampled** (spot-checked), **stated** (a principle the author honors). The authoritative model these rules enforce is [[CAB Aspects]] § Facet + § Spec-doc structure.

## Location & registration

### RULE R-facet-spec-01 — One spec file per facet (checked)
Each facet is defined by exactly one spec doc — `facets/FCT <Name>.md` (single-file), or `facets/FCT <Name>/FCT <Name>.md` (folder form when the facet grows large, parallel to Architecture).
**Check pattern:** the facet's catalog row resolves to one `FCT <Name>.md` (or its folder-form root); no second spec defines the same facet.
**Why:** one authoritative source per facet — split or duplicate specs drift and the audit can't decide which wins.

### RULE R-facet-spec-02 — Name is the facet's name, singular (checked)
The filename and H1 read `FCT <Name>`, with `<Name>` in **singular** form (the facet is used as a kind/adjective — "the Backlog facet").
**Check pattern:** H1 matches `# FCT <Name>`; `<Name>` is not a needless plural.
**Why:** facet names are used as adjectives; singular reads correctly (per the singular-naming convention) and keeps `FCT Facet` (the kind) distinct from `FCT Facets` (the index).

### RULE R-facet-spec-03 — Registered in the index (checked)
Every facet spec has a wiki-link row in [[FCT Facets]], in the semantic group matching its category (Structure / Design / Execute / Code / User / …) — promoted out of the staging `...` row once its category is clear.
**Check pattern:** the spec's name appears as a link in exactly one [[FCT Facets]] group row.
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
**Why:** the standard anchor-page top — a facet spec is an anchor page and must be navigable like one (per [[FCT Anchor Page]], F060).

### RULE R-facet-spec-06 — Related row is lateral-only (sampled)
The dispatch table's `Related` row carries only lateral / cross-cutting links — never the breadcrumb ancestors, the parent, or the facet's own contents.
**Check pattern:** no `Related` entry duplicates a breadcrumb hop or the parent anchor.
**Why:** the Related row earns its space with links you can't already reach by ordinary navigation (per the anchor-page Related rule).

### RULE R-facet-spec-07 — Substantial specs carry a TLDR (sampled)
A facet spec with a non-trivial body opens its preface zone (after the dispatch table, before the first body H2) with a `**TLDR**` block per [[DSC progressive-disclosure]].
**Check pattern:** a `**TLDR**` line precedes the first body `## `; small specs (a few sentences) are exempt.
**Why:** lets a reader graze the facet's shape in five seconds without reading the whole spec.

## What a facet spec conveys — mostly via the rule set (sections optional)

**Only two parts are *required*: the `# RULESET` (R-facet-spec-18) and the `# BRIEF` (R-facet-spec-22).** Everything in this group is content a facet spec should make *knowable* — but the required rule set is the natural carrier for the load-bearing parts (detection, format, constraints), so dedicated prose sections for them are **optional**, not mandated.

### RULE R-facet-spec-08 — Makes the facet's identity knowable (sampled)
The spec conveys, in a sentence, the narrow aspect this facet names — via the H1 summary, an Overview, or a `## What it is`. A dedicated section is optional; the statement is not.
**Check pattern:** a one-sentence "this facet is X" is findable near the top.
**Why:** the reader must learn the facet's identity before any rule about it makes sense.

### RULE R-facet-spec-09 — Makes detection knowable (sampled)
The spec (typically its rule set) makes clear how presence is decided. Default is **file-existence**; any other mechanism (folder-existence, capability check, …) is stated **explicitly**.
**Check pattern:** detection is findable; non-default detection is named, not assumed.
**Why:** detection is owned by the spec, not hard-coded globally — a folder or file-less facet is mis-detected if a reader assumes "look for the file" (per [[CAB Aspects]] § Facet).

### RULE R-facet-spec-10 — Makes cardinality knowable (sampled)
The spec makes cardinality clear — `one` (one per anchor) or `many`.
**Check pattern:** `one` / `many` (or an explicit cardinality statement) is findable.
**Why:** audits and skills behave differently for `one` vs `many`; leaving it implicit invites bugs.

### RULE R-facet-spec-11 — Makes the instance format knowable (sampled)
The spec (typically its rule set) conveys the instance format: filename pattern, frontmatter, body requirements, naming.
**Check pattern:** the format is findable in the spec or its rule set.
**Why:** the format is the contract an instance is audited against; without it "conformance" is undefined.

### RULE R-facet-spec-12 — Constraints stated where they exist — a section is optional (stated)
When a facet has legal-usage rules (mutual exclusion, co-requirement, format invariants) they are stated — **usually inside the rule set**, not a separate `## Constraints` prose section. A dedicated Constraints section is **optional**, not required.
**Why:** the rule set is the enforceable home for constraints; a parallel prose section is redundant more often than not.

### RULE R-facet-spec-13 — Expected-Usage guidance is optional (stated)
Recommended (non-binding) patterns — common combinations, typical scale, skill pairings — may be included when useful. A dedicated `## Expected Usage` section is **optional**, not required.
**Why:** guidance helps but isn't load-bearing; its absence is not a defect.

### RULE R-facet-spec-14 — Names the skills and audits that attach (sampled)
The spec names which skills write/read the facet and which audits check it (in prose or a section).
**Check pattern:** the acting skills/audits are findable.
**Why:** a facet nobody writes, reads, or checks is dead structure; the attach list is how behavior finds the facet.

### RULE R-facet-spec-15 — Triggers section only when triggers are declared (checked)
check:: triggers_section_iff_declared
A `## Triggers` section appears **only** when the facet declares behavioral triggers, with an H3 per trigger type (`### compact`, `### markdown-write`) carrying the agent-read prose (per [[CAB Aspects]] § Triggers, F091).
**Check pattern:** if `## Triggers` is present, it has ≥ 1 typed H3; if the facet declares no triggers, the section is absent (not empty).
**Why:** triggers are anchor-resident and lazily resolved from the body H3s; an empty or malformed Triggers section misfires the resolution.

## The rule set — REQUIRED

### RULE R-facet-spec-18 — Every facet spec embeds a rule set — REQUIRED (checked)
Every facet spec carries an embedded `# RULESET R-<facet>` (per the F133 convention; a tiny facet may have just a few rules). It is the one part that makes the facet **validatable and creatable** — detection, format, and constraints in auditable form (e.g. [[FEX Manifest]] → [[R-fex-manifest]]).
**Check pattern:** the spec contains a `# RULESET R-<facet>` H1 with ≥ 1 `### RULE` entry.
**Why:** prose rots and varies; the rule set is the single source an audit reads and an author follows to build a conformant instance. Without it we don't actually know how to validate or create the facet — so it is required, not optional. (One of the two required parts, alongside the `# BRIEF`.)

### RULE R-facet-spec-16 — Rules are enforceable statements (sampled)
Each rule (and any constraint) is phrased so an audit could validate it — a forbidden/required/exclusive/invariant statement, not vague prose.
**Check pattern:** rule bodies read as testable claims ("exactly one per anchor", "no absolute paths"), not "should generally…".
**Why:** a rule exists to be checked; an unfalsifiable one can't gate anything.

### RULE R-facet-spec-17 — Compose by default; exclude only on logical incompatibility (stated)
A mutual-exclusion rule is declared only when two things make contradictory claims about the same underlying thing — never for tidiness.
**Check pattern:** each exclusion names the *logical* conflict it resolves.
**Why:** over-restriction blocks valid, useful compositions (per [[CAB Aspects]] § Constraints governing principle).

## Facet vs Trait — don't conflate

### RULE R-facet-spec-19 — A facet is a narrow file/folder aspect, not a paradigm (stated)
If the thing is a specific file or folder, it's a Facet (here). If it names what the anchor *is* — a declared paradigm in `traits:` — it's a [[CAB Traits|Trait]], authored under `CAB Traits/`.
**Check pattern:** the spec describes a file/folder-shaped aspect, not "this anchor is a Code/Skill/… project".
**Why:** the two have different detection (file vs `traits:` lookup) and different homes; a misfiled Trait-as-Facet is detected wrong and audited wrong.

### RULE R-facet-spec-20 — Defines a kind, never an instance (sampled)
The spec defines the facet *kind*; it does not paste a project's concrete instance into itself. Worked instances/definitions are **linked** in the dispatch `Examples` row, never embedded.
**Check pattern:** no full concrete instance is inlined; examples are links.
**Why:** an embedded instance blurs spec-vs-example and rots when the example moves (the lesson [[FCT Facet]] itself follows).

## Authority & maintenance

### RULE R-facet-spec-21 — The umbrella model lives in CAB Aspects (stated)
The spec does not duplicate the Aspect / Trait / Facet vocabulary, the six-section rationale, or the composability matrix — it links [[CAB Aspects]].
**Check pattern:** shared-model content is referenced, not restated.
**Why:** one source of truth for the umbrella model; copies drift from it.

### RULE R-facet-spec-22 — Every facet spec carries a `# BRIEF` — REQUIRED (checked)
The spec ends with a `# BRIEF` H1 — **agent-facing documentation** (per [[FCT Brief]]): what an agent reads *before editing* this facet spec — what belongs, what doesn't, the inclusion test, cross-reference-integrity notes. The agent is usually the maintainer, but the audience is the agent, not the user.
**Check pattern:** a `# BRIEF` H1 exists with agent-facing maintenance bullets.
**Why:** the BRIEF is how the next agent edits the spec correctly without re-deriving its conventions, and keeps foreign content from piling in. Required on every facet spec — one of the two required parts, alongside the `# RULESET`.

## Design-facet extras (when the facet is a Design doc)

### RULE R-facet-spec-23 — Phase-gated design facets carry a `status::` field (checked)
A facet that gates a design phase (Architecture, Testing, …) declares a `status::` dataview field — `drafting | in-review | accepted` — in its instance frontmatter, and the spec says so.
**Check pattern:** the spec's Format names a `status::` field with the three values, for design-gating facets.
**Why:** `status::` is the gate signal `/design` reads; a phase-gating facet without it can't unblock the next phase.

### RULE R-facet-spec-24 — Links peer facets in `## See also` (sampled)
A facet that sits among peers (the Design or Track groups) links them in a `## See also`, and names its authoring skill if one exists.
**Check pattern:** a `## See also` lists peer facets + the authoring skill (e.g. `/design testing` for [[FCT Testing]]).
**Why:** facets are read as a set; a peerless spec hides the doc the reader needs next.

# BRIEF

- **This is the spec for the *facet* primitive** — what a facet is and the shape of a facet spec doc. Sibling to [[FCT Skill]] (skill primitive) and [[FCT Ruleset]] (rule-set primitive); indexed from [[FCT Primitives]].
- **Carries the embedded `R-facet-spec` rule set** — the enforceable rules for authoring *any* facet. Keep it distinct from the umbrella [[R-facet]] (which aggregates each facet's *instance* rules); `R-facet-spec` governs facet *spec docs*. Keep the `Facet Document Structure` bullet list and the rule set in sync — the list is the readable form, the RULESET is the auditable form.
- **Singular, not the index.** [[FCT Facets]] (plural) is the *catalog* of concrete facets; this page (singular) *defines the kind*. The Primitives-row "Facet" link points here.
- **Don't embed a worked example.** A facet example is itself a full anchor page (dispatch table, sections, often a paired rule set); embedding one inside this spec confuses example-vs-spec. Describe the shape with the `Facet Document Structure` bullet list; link real examples in the dispatch `Examples` row.
- **`Examples` lists *facets* (definitions), never instances.** A project's `Architecture.md` is an *instance* of the Architecture facet — it belongs on that facet's own page, not here. Label each `Examples` entry by what kind of facet example it is (small / complete; single-file / folder / many-cardinality).
- **The umbrella model lives in [[CAB Aspects]]** — don't duplicate the Aspect/Trait/Facet vocabulary or the composability matrix here; link to it.
