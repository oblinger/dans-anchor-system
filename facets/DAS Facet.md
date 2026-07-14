---
description: "the Facet primitive — what a facet is and how to write its spec"
---

# DAS Facet
A narrow, usually file-based aspect of an anchor — and the spec for how to write one.

| -[[DAS Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Facet](hook://p/DAS%20Facet) |
| --- | --- |
| Related | [[DAS Skill]],  [[DAS Ruleset]],  [[DAS Facets]] (the index),  [[DAS Aspects]], |
| Examples | [[FEX Manifest\|one per anchor example]],  [[FEX Pin\|many per anchor example]],  [[FEX Bundle\|many folders per anchor example]],   |
| Rules | [[R-facet]],  [[R-facet-spec]],   |
|  |  |
| **Table of Contents** |  |
| [[#Location & registration]] |  |
| [[#Anchor-page top (a facet spec is itself an anchor page)]] |  |
| [[#What a facet spec conveys — mostly via the ruleset (sections optional)]] |  |
| [[#The ruleset — REQUIRED]] |  |
| [[#Facet vs Trait — don't conflate]] |  |
| [[#Authority & maintenance]] |  |
| [[#Design-facet extras (when the facet is a Design doc)]] |  |
| **[[#BRIEF]]** |  |

# Facet Document Structure
A facet spec is one file (`facets/DAS <Name>.md`), authoritative for that facet. Its parts, top to bottom — densest first, per [[DAS progressive-disclosure]]:

- **H1** — `# DAS <Name>`: the slug-name and the full name.
- **One-line summary** — a single sentence on the line directly under the H1 (no blank line between).
- **Dispatch table** — the breadcrumb row, then `Related` (lateral links only) and `Examples`.
- **Document structure** — this dense outline, placed first so a reader sees the doc's shape before any prose.
- **Overview** — a short paragraph: what the facet is and what it's for. *(Optional.)*
- **The Aspect contract** — content the body usefully conveys, mostly via the ruleset (section shapes vary; **not** fixed H2s; all optional): what it is · how it's detected (+ cardinality `one` / `many`) · format · constraints · expected usage · skills and audits that attach · triggers.
- **`# RULESET R-<facet>`** — **REQUIRED.** The embedded ruleset: how to validate and create the facet — detection, format, and constraints in auditable form (e.g. [[R-fex-manifest]]). It's how we know what the facet is and how to check it.
- **`# BRIEF`** — **REQUIRED.** Agent-facing documentation (per [[DAS Brief]]) — what an agent reads before editing this facet. (Agent ≈ maintainer, but the audience is the agent, not the user.)

For a worked facet, open an example in the dispatch table above — there is no embedded copy here, because a facet is itself a full anchor page and embedding one inside this spec just blurs example-vs-spec. The enforceable form of the rules below is the embedded **`R-facet-spec`** ruleset.

# Facet Overview
A **facet** is a narrow, usually file-based aspect of an anchor — one specific structural feature (a `Backlog` file, an `Architecture` doc, a website subfolder), defined by its own spec doc and detected (by default) through file-existence. This page is the spec for *the facet kind itself*: what a facet is and the shape every facet spec doc takes. It is the singular **definition**; [[DAS Facets]] (plural) is the **index** of all concrete facets.

A facet **defines a kind**. The concrete `<slug> Backlog.md` inside a real project is an *instance* of the Backlog facet, not a facet itself — keep the two apart.

Facets are one of the two kinds of [[DAS Aspects|Aspect]] — the narrow, file-based kind; the broad declared-paradigm kind is the [[DAS Traits|Trait]] (full distinction: [[DAS Aspects]] § Trait vs Facet). The shared model lives in [[DAS Aspects]]; this page is the facet-authoring view of it.

# Examples of a facet — project instances vs standalone `FEX` artifacts
A facet's worked examples come in two kinds, and the **prefix tells them apart**:

- **Project instances** — a real `{slug} <Facet>.md` living inside a project example world ([[HBR]], [[FEX Repo]]) or an actual anchor. It keeps the project's slug (`HBR CLI`, `SKA Backlog`) and is linked from the `Examples` row (R-facet-spec-25).
- **Standalone teaching artifacts** — an example that belongs to *no* single project world (a dispatch-table gallery, a page-layout exemplar). It carries the **`FEX`** prefix — `FEX` marks "example" exactly as `DAS` marks "spec", so a reader tells them apart at a glance — and lives as a plain file **in the facet's group folder** (`facets/FEX <Name>.md`), beside the `DAS` specs. **No per-facet anchor is created** (that's the "bunch of anchors" trap); a set of related ones may be gathered by a `FEX <Group>` gallery/dispatch page in the same folder. Group-level placement is what lets a **cross-facet** example (one that teaches several facets at once) have a natural home.

Worked instances of the standalone kind: [[FEX Dispatch Examples]] (+ [[FEX Grouped Dispatch]] / [[FEX List Dispatch]] / [[FEX Figure Page]]) in `facets/`; [[FEX Scheduler]] in `examples/`.

# BRIEF

*(Maintainer note — facet-specific cautions for editing this spec.)*

- **`R-facet-spec` (embedded here) ≠ the umbrella [[R-facet]].** This page's ruleset governs facet *spec docs*; `R-facet` aggregates each materialized facet's *instance* rules. Keep the `Facet Document Structure` bullet list and the `R-facet-spec` ruleset **in sync** — the list is the readable form, the ruleset the auditable one.
- **This page deliberately embeds no worked example** (R-facet-spec-20) — it models the rule it states; don't add one.
