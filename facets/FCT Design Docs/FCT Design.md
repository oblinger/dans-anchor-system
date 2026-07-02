---
description: "design facet — the {NAME} Design/ folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required)"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Design](hook://p/FCT%20Design)

# FCT Design
The Design folder facet — marks an anchor as following the designed-lifecycle convention; folder presence is the gate.

**Related:** [[FCT PRD]],  [[FCT Architecture]],  [[FCT Testing]],  [[FCT Design Dispatch\|Dispatch]]
**Examples:** [[CAE Design\|minimal]],  [[HBR Design\|fuller]]

**Linkage** — this facet's existence ⟺ the anchor has been architected by the [[architect]] skill; the two share one design folder, [[Architect Design]] (hosted on the behavioral core), reachable from either page per [[SKA Decisions]] D10.

| Table of Contents |  |
|---|---|
| [[#Location]] |  |
| [[#Folder shape]] |  |
| [[#Design vs. user docs vs. reference]] |  |
| [[#Required vs optional children]] |  |
| [[#Scaffolding — pre-wire the whole structure]] |  |
| [[#Lifecycle gate behavior]] |  |
| [[#Trait system — what's still in scope]] |  |
| [[#Trait applicability]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — The Design facet is triggered by the **existence of a `{NAME} Design/` folder** (not by any `.anchor` trait field). When the folder exists, three children are required (PRD, Architecture, Testing), several others are recommended, and the `/design` skill operates on the anchor. Cardinality: **one per anchor** — an anchor has at most one Design folder. The embedded `R-design` ruleset encodes the auditable rules; `# BRIEF` is the agent-maintenance guide.

The Design facet is the **structural marker** that an anchor follows the designed-lifecycle convention. **If `{NAME} Design/` exists, the anchor is in design-mode** — `/design` operates on it, the PRD → UX Design → API Design → Architecture → Testing → Decisions → Roadmap pipeline applies, and the design sub-facets become the canonical homes for what the anchor *is* and *how it works*.

The six-phase pipeline pairs UX Design (the *human* user surface) and API Design (the *programmatic* user surface) as peer facets — cut by **who the consumer is**, not by where the surface lives. Either may be N/A for a given anchor; both are common for anchors with both a CLI and a library form (e.g. [[CAE]]).

This facet replaces the historical `Code` trait check that gated `/design` to "Code-trait anchors only." That check conflated two orthogonal questions:

- **What's being built?** (artifact kind — code, paper, methodology, …) — that's the trait system's job.
- **Is it designed?** (lifecycle posture — PRD-then-Architecture-then-Testing-then-Code, vs. just-write-it) — that's THIS facet's job.

Most code projects are designed. Most papers are designed. But some quick scripts aren't, and the trait gate was lying. The folder-presence gate doesn't lie — if you mkdir `{NAME} Design/`, you're committing to the convention; if you don't, you're not.

## Location

`{anchor}/{NAME} Design/` — anchor-folder directly under the anchor root, alongside the separate sibling trees `{NAME} Track/` (execution state), `{NAME} User Docs/` (the consumer-facing manual), and `{NAME} Dev Docs/` (module docs). **Architecture is a child of Design**, not an anchor-root sibling — F094's root placement was reversed 2026-06-27 (architecture is a design artifact).

## Folder shape

The Design folder is an anchor folder with the standard structure:

```
{NAME} Design/
├── .anchor                       ← folder-anchor marker (empty or YAML)
├── {NAME} Design.md              ← dispatch page; anchor file (matches folder name)
├── {NAME} PRD.md                 ← REQUIRED — product requirements (per CAB PRD). May be a folder.
├── {NAME} Architecture.md        ← REQUIRED — system architecture (per CAB Architecture). May be a folder.
├── {NAME} Testing.md             ← REQUIRED — strategy + proposed-tests overview (per CAB Testing)
├── {NAME} Decisions.md           ← RECOMMENDED — load-bearing recorded decisions (per FCT Decisions)
├── {NAME} Roadmap.md             ← RECOMMENDED — sequencing-design: milestones + ordering (per CAB Roadmap)
├── {NAME} Features/              ← RECOMMENDED — per-feature design docs F<NNN> — <title>.md (per CAB Features)
│   ├── {NAME} Features.md        ← Features dispatch / index
│   └── F<NNN> — <Title>.md       ← one per feature
├── {NAME} UX Design.md           ← OPTIONAL — when the anchor has a human user-facing surface (per CAB UX Design)
├── {NAME} API Design.md          ← OPTIONAL — when the anchor has a programmatic user-facing surface (per CAB API Design)
├── {NAME} Interface.md           ← OPTIONAL — when there's a layer-contract surface (per CAB Interface)
└── {NAME} CLI.md                 ← OPTIONAL — when the anchor ships a CLI (per CAB CLI; downstream of UX Design)
```

**Roadmap + Features relocated to Design 2026-06-10** (previously lived in `{NAME} Track/`). Reasoning: feature docs are themselves design artifacts (each carries Summary + Success Criteria + Design + Open Questions); the roadmap is sequencing-design. The PRD / Architecture / Testing cross-reference features and stories; keeping everything in one Design folder removes the cross-folder reference burden. See [[FCT Features]] / [[FCT Roadmap]] for the per-facet specs.

The dispatch page `{NAME} Design.md` is the dispatch table (per [[FCT Design Dispatch]] — different facet covering the dispatch-page format).

## Design vs. user docs vs. reference

Three buckets, split by **who reads them and why** — only the first lives in `{NAME} Design/`:

| Bucket | The reader is… | Read to… | Home |
|---|---|---|---|
| **Design** (this folder) | a builder / maintainer | *understand why & how* it's built | `{NAME} Design/` — PRD, UX/API Design, Architecture, Decisions, Roadmap, Features |
| **User docs** | a consumer | *learn how to do a task* (tutorials, how-tos) | a **separate** `{NAME} User Docs/` tree (or the published / SKL surface) — **never** in Design |
| **Reference** | someone working *against* it | *look up an exact detail* (the precise format / API spec) | a **role, not a third folder** (below) |

**Reference is a migrating role.** A spec (a rule-language format, an API reference) is *authored during design* — so it sits in `{NAME} Design/` while it is still moving — and *consulted by users* — so it **graduates to `{NAME} User Docs/` (or the published reference) once stable**. There is no third folder; a reference doc simply changes homes as it matures. So the standing rule is **two physical trees** — `{NAME} Design/` (blueprint) and `{NAME} User Docs/` (manual) — with reference docs migrating from the first to the second.

**Architecture is a Design child**, not a user doc — it's the *why/how-structured* story, author-facing. It is a single `{NAME} Architecture.md` by default and upgrades to a `{NAME} Architecture/` folder-doc when it grows subsystems; the same-named index keeps that upgrade link-transparent (see [[FCT Architecture]] / the `/architect` skill).

## Required vs optional children

**Required** when the Design folder exists:

| Child | Facet | Why required |
|---|---|---|
| `{NAME} PRD.md` | [[FCT PRD]] | What is being built. Every designed anchor needs a PRD; without one, "designed" has no anchor. |
| `{NAME} Architecture.md` | [[FCT Architecture]] | How it's structured. Decoupling design from architecture is fine in spirit but in practice every designed project has a structural story; making it required keeps the spine honest. |
| `{NAME} Testing.md` | [[FCT Testing]] | How we know it works. The verification contract; every designed project commits to one. |

**Recommended** (encouraged but not enforced):

| Child | Facet | When |
|---|---|---|
| `{NAME} Decisions.md` | [[FCT Decisions]] | The moment the first cross-cutting load-bearing decision needs durable recorded form. |
| `{NAME} Roadmap.md` | [[FCT Roadmap]] | Activated as soon as the project plans more than 1-2 milestones of work. |
| `{NAME} Features/` | [[FCT Features]] | Activated as soon as the first F-numbered feature doc lands. Holds all per-feature design docs (`F<NNN> — <title>.md`) + a `{NAME} Features.md` dispatch index. |

**Optional** (situational):

| Child | Facet | When |
|---|---|---|
| `{NAME} UX Design.md` | [[FCT UX Design]] | The anchor has a *human* user-facing surface (CLI commands, GUI screens, web pages, slash commands, doc entry points). |
| `{NAME} API Design.md` | [[FCT API Design]] | The anchor has a *programmatic* user-facing surface (library, sub-skill called by other skills, service, importable contract). Sibling peer to UX Design. |
| `{NAME} Interface.md` | [[FCT Interface]] | There's an *internal* layer/component contract distinct from the public API surface. |
| `{NAME} CLI.md` | [[FCT CLI]] | The anchor ships a CLI binary; CLI doc is the exhaustive flag/exit-code reference (downstream of UX Design). |

## Scaffolding — pre-wire the whole structure

**When `/design` runs in an anchor without a Design folder**, the orchestrator offers to scaffold one. Scaffolding creates:

- The `{NAME} Design/` folder + `.anchor` marker
- The dispatch page `{NAME} Design.md` with the standard dispatch-table shape
- The three required children (PRD, Architecture, Testing) each with their required-section spine (H1 + description:: + dispatch + required H2 stubs), bodies empty
- The recommended `{NAME} Decisions.md` with intro paragraph + placeholder
- Updates `{NAME} Track/{NAME} Status.md` (creating it if absent) — all design facets initialized to `none`

The user then iterates with `/design prd`, `/design architect`, etc. — each sub-skill enters assess mode against the placeholder and fills the body.

**Why pre-wire empty files vs scaffold-on-demand:** pre-wiring catches link-target errors before they accrue (every wiki-link points at a real file from the moment the dispatch table is written), gives the user obvious places to add content (no decisions about where to put things), and means the dispatch graph is correct from day one. The cost is a few placeholder files; the win is far fewer "file moved / link broken" bugs during early design work.

## Lifecycle gate behavior

`/design` and its sub-skills (`/design prd`, `/design architect`, `/design testing`, `/design roadmap`, `/design ux`) check **for the Design folder, not for the Code trait**:

- **Design folder exists** → operate normally (assess or bootstrap per the sub-skill's runbook).
- **Design folder absent** → offer to scaffold. If the user confirms, scaffold per § Scaffolding above and proceed. If declined, stop with a one-line explanation.

The `Code` trait is **deprecated as a `/design` gate** — kept for backward compatibility (existing anchors with `Code` in their `traits:` still work; no anchor is broken), but new anchors don't need it. Phase 2 vault sweep retires the trait from anchors where the Design folder is the better signal.

## Trait system — what's still in scope

The `traits:` field in `.anchor` continues to classify **what kind of thing** an anchor is, orthogonally from whether it's designed:

| Trait | Meaning | Used by |
|---|---|---|
| `Skill` | Anchor is a Claude Code skill | Skill-related conventions |
| `Paper` | Anchor produces written work (paper, article, report) | Paper-trait conventions |
| `Topic` | Anchor is a topic surface (reference collection, not produced output) | Topic-trait conventions |
| `Simple` | Anchor is small and doesn't carry the full structure | Simple-trait conventions |
| `Publishable` | Anchor publishes externally (web, etc.) | `/publish` |
| ~~`Code`~~ | (Deprecated as a `/design` gate. May still appear on legacy anchors.) | — |

A Code-shaped project that's designed has the `{NAME} Design/` folder AND benefits from the `/code` skill cluster for implementation operations. That cluster (`/code mint`, `/code test`, `/code release`) is unaffected by this facet — it's about the WHAT-to-build operations downstream of design.

## Trait applicability

Any anchor that commits to the designed-lifecycle convention.

## Audit

`/audit design` (future) would flag the rules captured in `R-design` below — folder presence, required-child presence, dispatch wiring, Status file initialization, etc.

## See also

- [[FCT Design Dispatch]] — distinct facet covering the `{NAME} Design.md` dispatch-page format
- [[FCT PRD]] — required child facet
- [[FCT Architecture]] — required child facet
- [[FCT Testing]] — required child facet
- [[FCT Decisions]] — recommended child facet
- [[FCT Status]] — `{NAME} Status.md` tracks design-phase completeness
- [[design]] — orchestrator skill; gate moved from Code-trait check to Design-folder check 2026-06-10
- [[CAE Design]] — worked example
- F140 (vault sweep — retire `Code` trait from anchors with Design folder)

# RULESET R-design
include::
where:: anchor
description:: design facet — the `{NAME} Design/` folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required)

Embedded ruleset for the Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-design-01 — Folder presence IS the gate (checked)

If `{anchor}/{NAME} Design/` exists, the anchor is in design-mode. The `Code` trait field in `.anchor` is NOT consulted by `/design` or its sub-skills.

**Check pattern:** for each anchor referenced by `/design`, the resolution path uses `ls "{anchor}/{NAME} Design"` not `grep Code .anchor`.

**Why:** structure is honest; trait fields can drift. Folder existence is observable.

### RULE R-design-02 — Required children present when folder exists (checked)
check:: design_folder_children PRD Architecture Testing

When `{NAME} Design/` exists, the folder contains at minimum: `{NAME} Design.md`, `{NAME} PRD.md`, `{NAME} Architecture.md`, `{NAME} Testing.md`.

**Check pattern:** for each existing Design folder, assert the four files exist (or `{NAME} Architecture/` folder form, per CAB Architecture).

**Why:** these three children carry the load-bearing design content. Missing any of them means the anchor advertises a design process it doesn't deliver.

### RULE R-design-03 — Dispatch page lists every present child (sampled)

The `{NAME} Design.md` dispatch table contains a wiki-link row for every `.md` file (or folder-doc) present in `{NAME} Design/`, with a one-line description.

**Check pattern:** parse `{NAME} Design.md`'s dispatch table; enumerate files in `{NAME} Design/`; assert one-to-one cover modulo intentional exclusions (the dispatch file itself, the `.anchor` marker).

**Why:** the dispatch page is the navigation hub; missing rows hide content from the reader.

### RULE R-design-04 — Status file initialized when Design folder exists (sampled)
check:: status_facets_initialized prd ux architecture testing roadmap

When `{NAME} Design/` exists, `{NAME} Track/{NAME} Status.md` exists with the standard five design-facet lines (`prd::`, `ux::`, `architecture::`, `testing::`, `roadmap::`) per [[FCT Status]].

**Check pattern:** for each existing Design folder, assert `{NAME} Track/{NAME} Status.md` exists with the five facets declared (any cell value is valid; absence of the file is the failure).

**Why:** `/design`'s picker reads Status.md; missing file means the picker can't auto-dispatch.

### RULE R-design-05 — `Code` trait is deprecated as a `/design` gate (stated)

New anchors don't add `Code` to `.anchor` `traits:` to enable `/design`. Existing anchors with `Code` aren't broken; F140 sweep retires the trait from anchors that have a Design folder.

**Check pattern:** stated for now; F140 sweep mechanically retires the trait field.

**Why:** the Code trait was a misnomer — it gated "designed lifecycle" via "is this code," which is the wrong axis. Folder presence is the right signal.

### RULE R-design-06 — Optional children only when applicable (stated)

`{NAME} UX Design.md` exists when the anchor has user-facing interface; `{NAME} API.md` when public surface is contract; `{NAME} CLI.md` when ship a CLI; `{NAME} Interface.md` when layer contract. Don't author empty optionals.

**Check pattern:** for each optional child present, sample its body — bare H1 + description with no content is a creation-without-commitment failure mode.

**Why:** empty optional facets pollute the dispatch and confuse readers. Author them when you have content; omit them otherwise.

### RULE R-design-07 — Scaffolding creates pre-wired structure, not bare folder (sampled)

When `/design` scaffolds a Design folder, the operation creates all required children with their required-section spines populated (H1 + description + dispatch + required H2 stubs), not just an empty folder.

**Check pattern:** sample freshly-scaffolded Design folders; assert each required child has its required-H2 stubs (per its facet spec).

**Why:** dispatch links work from day one; user has obvious places to add content; "file moved / link broken" bugs avoided.

### RULE R-design-08 — No empty/boilerplate Design folder; presence asserts a maintained design (checked)

The `{NAME} Design/` folder exists **iff** the anchor has real design content — a PRD, design docs, or feature docs (feature docs are themselves design artifacts and migrate INTO the Design folder). A folder containing only template boilerplate (empty `prd`/`plan`/`principles`/`discussion` stubs) does **not** count as a design: during migration, **wipe the boilerplate and omit the Design folder entirely**. Add the folder later, when the first real design or feature doc lands — or via `/design` scaffolding (R-design-07), which is the user's explicit commitment-to-design and the one case where a freshly-spined folder is expected before content arrives.

**Check pattern:** for each `{NAME} Design/`, assert at least one child carries distinct authored content (not a bare H1 + description stub); a folder whose every child is boilerplate — and that was not just scaffolded by `/design` — is a violation: remove it.

**Why:** folder presence is a trait (cf. R-design-01) — its existence tells the reader "this anchor has a maintained design." An empty placeholder folder lies about that state and clutters the tree; absence honestly signals "not yet designed."

# BRIEF

- **This file is the CAB Design facet spec** — it defines the `{NAME} Design/` folder convention (folder-presence gate, required vs. optional children, scaffolding, lifecycle gate behavior) and embeds the `R-design` ruleset. It is the authority cited by `/design` and its sub-skills.
- **NOT for per-child facet content** — PRD / Architecture / Testing / UX Design / API Design / Decisions / Roadmap / Features each have their own `CAB <X>.md` spec. Link to those; do not inline their rules or sections here.
- **Inclusion test for the body** — content belongs here if it answers "what is the Design folder, what must it contain, when does /design scaffold it, and how does the folder-presence gate work?" Anything narrower (a child facet's internal shape) belongs in that child's spec.
- **`R-design` ruleset is co-located** — the `# RULESET R-design` H1 at the bottom is the ruleset embedded per F133. Keep it after the prose spec, use `include::` / `description::` Dataview fields, and number rules `R-design-NN` sequentially. Don't split it into a sibling file.
- **Code-trait deprecation is load-bearing** — R-design-05 and the § Trait system table mark `Code` as a deprecated `/design` gate. If you re-add it as a gate anywhere, you re-introduce the conflation this facet was created to fix (F140 sweep tracks the retirement).
- **Dispatch graph claim** — § Scaffolding promises pre-wired files so wiki-links resolve from day one. If you change the required-children list, update the scaffolder runbook in `/design` and the R-design-02 check pattern in lockstep.
- **See Also is a navigation contract** — each child facet wiki-link in § See also is the resolution target a `/design` sub-skill uses to find its spec. Don't rename or remove a row without updating the corresponding sub-skill.
