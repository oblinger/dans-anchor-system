---
description: "design facet — the {slug} Design/ folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required)"
group: folder
---

| -[[DAS Design Folder]]- | → [[DAS]] → [[FCT]] → [DAS Design Folder](hook://p/DAS%20Design%20Folder)  |
| --- | --- |
| Related | [[DAS PRD]],  [[DAS Architecture]],  [[DAS Testing]],  [[DAS Design Dispatch\|Dispatch]],   |
| Examples | [[HBR Design\|minimal]],  [[HBR Design\|fuller]],   |
| Rules | [[R-design]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Docs]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Design
The Design folder facet — marks an anchor as following the designed-lifecycle convention; folder presence is the gate.

**Linkage** — this facet's existence ⟺ the anchor has been architected by the [[architect]] skill; the two share one design folder, [[DAS Architect Design]] (hosted on the behavioral core), reachable from either page (§ What the folder's existence claims).

**TLDR** — The Design facet is triggered by the **existence of a `{slug} Design/` folder** (not by any `.anchor` trait field). When the folder exists, three children are required (PRD, Architecture, Testing), several others are recommended, and the `/design` skill operates on the anchor. Cardinality: **one per anchor** — an anchor has at most one Design folder. The embedded `R-design` ruleset encodes the auditable rules; `# BRIEF` is the agent-maintenance guide.

The Design facet is the **structural marker** that an anchor follows the designed-lifecycle convention. **If `{slug} Design/` exists, the anchor is in design-mode** — `/design` operates on it, the PRD → UX Design → API Design → Architecture → Testing → Decisions → Roadmap pipeline applies, and the design sub-facets become the canonical homes for what the anchor *is* and *how it works*.

The six-phase pipeline pairs UX Design (the *human* user surface) and API Design (the *programmatic* user surface) as peer facets — cut by **who the consumer is**, not by where the surface lives. Either may be N/A for a given anchor; both are common for anchors with both a CLI and a library form (e.g. [[HBR]]).

This facet replaces the historical `code` trait check that gated `/design` to "Code-trait anchors only." That check conflated two orthogonal questions:

- **What's being built?** (artifact kind — code, paper, methodology, …) — that's the trait system's job.
- **Is it designed?** (lifecycle posture — PRD-then-Architecture-then-Testing-then-Code, vs. just-write-it) — that's THIS facet's job.

Most code projects are designed. Most papers are designed. But some quick scripts aren't, and the trait gate was lying. The folder-presence gate doesn't lie — if you mkdir `{slug} Design/`, you're committing to the convention; if you don't, you're not.

## Location

`{anchor}/{slug} Design/` — anchor-folder directly under the anchor root, alongside the separate sibling trees `{slug} Track/` (execution state), `{slug} User Docs/` (the consumer-facing manual), and `{slug} Dev Docs/` (module docs). **Architecture is a child of Design**, not an anchor-root sibling — F094's root placement was reversed 2026-06-27 (architecture is a design artifact).

## Folder shape

The Design folder is an anchor folder with the standard structure:

```
{slug} Design/
├── .anchor                       ← folder-anchor marker (empty or YAML)
├── {slug} Design.md              ← dispatch page; anchor file (matches folder name)
├── {slug} PRD.md                 ← REQUIRED — product requirements (per DAS PRD). May be a folder.
├── {slug} Architecture.md        ← REQUIRED — system architecture (per DAS Architecture). May be a folder.
├── {slug} Testing.md             ← REQUIRED — strategy + proposed-tests overview (per DAS Testing)
├── {slug} Decisions.md           ← RECOMMENDED — load-bearing recorded decisions (per DAS Decisions)
├── {slug} Roadmap.md             ← RECOMMENDED — sequencing-design: milestones + ordering (per DAS Roadmap)
├── {slug} Features/              ← RECOMMENDED — per-feature design docs F<NNN> — <title>.md (per DAS Features)
│   ├── {slug} Features.md        ← Features dispatch / index
│   └── F<NNN> — <Title>.md       ← one per feature
├── {slug} UX Design.md           ← OPTIONAL — when the anchor has a human user-facing surface (per DAS UX Design)
├── {slug} API Design.md          ← OPTIONAL — when the anchor has a programmatic user-facing surface (per CAB API Design)
├── {slug} Interface.md           ← OPTIONAL — when there's a layer-contract surface (per CAB Interface)
└── {slug} CLI.md                 ← OPTIONAL — when the anchor ships a CLI (per CAB CLI; downstream of UX Design)
```

**Roadmap + Features relocated to Design 2026-06-10** (previously lived in `{slug} Track/`). Reasoning: feature docs are themselves design artifacts (each carries Summary + Success Criteria + Design + Open Questions); the roadmap is sequencing-design. The PRD / Architecture / Testing cross-reference features and stories; keeping everything in one Design folder removes the cross-folder reference burden. See [[DAS Features]] / [[DAS Roadmap]] for the per-facet specs.

The dispatch page `{slug} Design.md` is the dispatch table (per [[DAS Design Dispatch]] — different facet covering the dispatch-page format).

## Design vs. user docs vs. reference

Three buckets, split by **who reads them and why** — only the first lives in `{slug} Design/`:

| Bucket | The reader is… | Read to… | Home |
|---|---|---|---|
| **Design** (this folder) | a builder / maintainer | *understand why & how* it's built | `{slug} Design/` — PRD, UX/API Design, Architecture, Decisions, Roadmap, Features |
| **User docs** | a consumer | *learn how to do a task* (tutorials, how-tos) | a **separate** `{slug} User Docs/` tree (or the published / SKL surface) — **never** in Design |
| **Reference** | someone working *against* it | *look up an exact detail* (the precise format / API spec) | a **role, not a third folder** (below) |

**Reference is a migrating role.** A spec (a rule-language format, an API reference) is *authored during design* — so it sits in `{slug} Design/` while it is still moving — and *consulted by users* — so it **graduates to `{slug} User Docs/` (or the published reference) once stable**. There is no third folder; a reference doc simply changes homes as it matures. So the standing rule is **two physical trees** — `{slug} Design/` (blueprint) and `{slug} User Docs/` (manual) — with reference docs migrating from the first to the second.

**Architecture is a Design child**, not a user doc — it's the *why/how-structured* story, author-facing. It is a single `{slug} Architecture.md` by default and upgrades to a `{slug} Architecture/` folder-doc when it grows subsystems; the same-named index keeps that upgrade link-transparent (see [[DAS Architecture]] / the `/architect` skill).

## Required vs optional children

**Required** when the Design folder exists:

| Child | Facet | Why required |
|---|---|---|
| `{slug} PRD.md` | [[DAS PRD]] | What is being built. Every designed anchor needs a PRD; without one, "designed" has no anchor. |
| `{slug} Architecture.md` | [[DAS Architecture]] | How it's structured. Decoupling design from architecture is fine in spirit but in practice every designed project has a structural story; making it required keeps the spine honest. |
| `{slug} Testing.md` | [[DAS Testing]] | How we know it works. The verification contract; every designed project commits to one. |

**Recommended** (encouraged but not enforced):

| Child | Facet | When |
|---|---|---|
| `{slug} Decisions.md` | [[DAS Decisions]] | The moment the first cross-cutting load-bearing decision needs durable recorded form. |
| `{slug} Roadmap.md` | [[DAS Roadmap]] | Activated as soon as the project plans more than 1-2 milestones of work. |
| `{slug} Features/` | [[DAS Features]] | Activated as soon as the first F-numbered feature doc lands. Holds all per-feature design docs (`F<NNN> — <title>.md`) + a `{slug} Features.md` dispatch index. |

**Optional** (situational):

| Child | Facet | When |
|---|---|---|
| `{slug} UX Design.md` | [[DAS UX Design]] | The anchor has a *human* user-facing surface (CLI commands, GUI screens, web pages, slash commands, doc entry points). |
| `{slug} API Design.md` | [[DAS API Design]] | The anchor has a *programmatic* user-facing surface (library, sub-skill called by other skills, service, importable contract). Sibling peer to UX Design. |
| `{slug} Interface.md` | [[DAS Interface]] | There's an *internal* layer/component contract distinct from the public API surface. |
| `{slug} CLI.md` | [[DAS CLI]] | The anchor ships a CLI binary; CLI doc is the exhaustive flag/exit-code reference (downstream of UX Design). |

## Scaffolding — pre-wire the whole structure

**When `/design` runs in an anchor without a Design folder**, the orchestrator offers to scaffold one. Scaffolding creates:

- The `{slug} Design/` folder + `.anchor` marker
- The dispatch page `{slug} Design.md` with the standard dispatch-table shape
- The three required children (PRD, Architecture, Testing) each with their required-section spine (H1 + description:: + dispatch + required H2 stubs), bodies empty
- The recommended `{slug} Decisions.md` with intro paragraph + placeholder
- Updates `{slug} Track/{slug} Status.md` (creating it if absent) — all design facets initialized to `none`

The user then iterates with `/design prd`, `/design architect`, etc. — each sub-skill enters assess mode against the placeholder and fills the body.

**Why pre-wire empty files vs scaffold-on-demand:** pre-wiring catches link-target errors before they accrue (every wiki-link points at a real file from the moment the dispatch table is written), gives the user obvious places to add content (no decisions about where to put things), and means the dispatch graph is correct from day one. The cost is a few placeholder files; the win is far fewer "file moved / link broken" bugs during early design work.

## Lifecycle gate behavior

`/design` and its sub-skills (`/design prd`, `/design architect`, `/design testing`, `/design roadmap`, `/design ux`) check **for the Design folder, not for the Code trait**:

- **Design folder exists** → operate normally (assess or bootstrap per the sub-skill's runbook).
- **Design folder absent** → offer to scaffold. If the user confirms, scaffold per § Scaffolding above and proceed. If declined, stop with a one-line explanation.

The `code` trait is **deprecated as a `/design` gate** — kept for backward compatibility (existing anchors with `code` in their `traits:` still work; no anchor is broken), but new anchors don't need it. Phase 2 vault sweep retires the trait from anchors where the Design folder is the better signal.

## What the folder's existence claims — and what its absence does not

A `{slug} Design/` folder existing means the anchor **has been architected** — its design is the [[architect]] skill's subject, walked and checked for completeness. There is deliberately **no separate "design discipline"**: the architect skill carries the rules and the Design facet is the artifact it maintains. (Its sibling is asymmetric on purpose — a Track facet existing ⟺ the anchor runs the [[workflow]] discipline. Tracking is continuous, so it is a way of working; architecting is periodic, so it is a skill.)

**Absence is valid, never an error.** No Design folder means "not architected" — a claim the anchor is entitled to make, and one it may make forever. So an empty Design scaffold is safe to delete anywhere, and a missing one is not a finding. The one population that overrides this is the SKA sub-project (skill / facet / discipline / example), where the folder is mandatory from creation — see [[R-anchor-page]] § SKA sub-project.

**A design folder covers a coherent design *unit*, not one object.** Where a facet and its behavioral core are two objects describing one design — the Track facet with the [[workflow]] discipline, this facet with the [[architect]] skill — they share **one** folder, hosted on the behavioral core, and **both** dispatch pages carry a Design row pointing at it. Two mutually-referential design folders for one design is the failure this prevents. The facet keeps its own `# RULESET` regardless: a structural contract is a different kind of document from a design folder's rationale.

**The masthead Design row's member order is fixed, and is NOT this page's pipeline order.** The row lists PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features ([[R-anchor-page]]-13); the lifecycle pipeline above runs PRD → UX Design → API Design → Architecture → Testing → Decisions → Roadmap. They answer different questions — *where does the reader look first* versus *what gets written first* — so neither is a typo for the other. Do not "correct" one to match the other.

## Trait system — what's still in scope

The `traits:` field in `.anchor` continues to classify **what kind of thing** an anchor is, orthogonally from whether it's designed:

| Trait | Meaning | Used by |
|---|---|---|
| `skill` | Anchor is a Claude Code skill | Skill-related conventions |
| `paper` | Anchor produces written work (paper, article, report) | Paper-trait conventions |
| `topic` | Anchor is a topic surface (reference collection, not produced output) | Topic-trait conventions |
| `simple` | Anchor is small and doesn't carry the full structure | Simple-trait conventions |
| `Publishable` | Anchor publishes externally (web, etc.) | `/publish` |
| ~~`code`~~ | (Deprecated as a `/design` gate. May still appear on legacy anchors.) | — |

A Code-shaped project that's designed has the `{slug} Design/` folder AND benefits from the `/code` skill cluster for implementation operations. That cluster (`/code mint`, `/code test`, `/code release`) is unaffected by this facet — it's about the WHAT-to-build operations downstream of design.

## Trait applicability

Any anchor that commits to the designed-lifecycle convention.

## Audit

`/audit design` (future) would flag the rules captured in `R-design` below — folder presence, required-child presence, dispatch wiring, Status file initialization, etc.

## See also

- [[DAS Design Dispatch]] — distinct facet covering the `{slug} Design.md` dispatch-page format
- [[DAS PRD]] — required child facet
- [[DAS Architecture]] — required child facet
- [[DAS Testing]] — required child facet
- [[DAS Decisions]] — recommended child facet
- [[DAS Status]] — `{slug} Status.md` tracks design-phase completeness
- [[design]] — orchestrator skill; gate moved from Code-trait check to Design-folder check 2026-06-10
- [[HBR Design]] — worked example
- F140 (vault sweep — retire `code` trait from anchors with Design folder)

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the `R-design` ruleset is embedded below.)*

- **Scope / inclusion test** — content belongs here only if it answers "what is the Design folder, what must it contain, when does `/design` scaffold it, how does the folder-presence gate work?" Per-child facet content (PRD / Architecture / Testing / UX / API / Decisions / Roadmap / Features) lives in each child's own `CAB <X>.md` spec — link, never inline.
- **Code-trait deprecation is load-bearing** — R-design-05 and § Trait system mark `code` as a deprecated `/design` gate; re-adding it as a gate anywhere re-introduces the conflation this facet was created to fix (F140 tracks the retirement).
- **Change the required-children list in lockstep** — § Scaffolding promises pre-wired files so wiki-links resolve from day one; if the required-children list changes, update the `/design` scaffolder runbook and the R-design-02 check pattern together.
- **See Also is a navigation contract** — each child-facet wiki-link in § See also is the resolution target a `/design` sub-skill uses to find its spec; don't rename or remove a row without updating the corresponding sub-skill.
