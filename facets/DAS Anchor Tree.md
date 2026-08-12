---
cssclasses:
  - monospace
description: anchor master tree — every possible doc/folder in an anchor, linked to its facet spec
group: file
---

| -[[DAS Anchor Tree]]- | → [[DAS]] → [[FCT]] → [DAS Anchor Tree](hook://p/DAS%20Anchor%20Tree)  |
| --- | --- |
| Related | [[DAS Anchor Page]],  [[DAS Anchor]],  [[DAS Facet]],   |
| Examples | [[HBR\|minimal Code anchor]],  [[HBR\|fuller anchor with components]],   |
| Rules | [[R-anchor]],  [[R-anchor-tree]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Changes]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Dot Anchor]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Anchor Tree
The annotated master file tree showing every possible file and folder that may appear inside a DAS anchor, with each named element wiki-linked to its governing facet spec.

**Cardinality: one per anchor** — each anchor has exactly one canonical file tree (this spec is the reference; an anchor's actual tree is its on-disk directory).

An anchor is a standardized folder structure that serves as the home for a project, topic, or content area. This tree is the canonical reference for the files common to all anchors.

**TLDR** — The annotated master file tree for a DAS anchor: every recognized file/folder placeholder wiki-linked to its governing facet spec. Two trees: the anchor folder tree (top) and the optional Code Repository tree (bottom). Use this as a lookup when setting up or auditing an anchor's on-disk structure.

> **Note:** This file serves as the reference example itself — the annotated file tree below IS the canonical illustration of a complete anchor structure.

Placeholders: `{slug}` stands for the anchor's name and `{CAB Folder}` for the anchor folder's name; each named element wiki-links its governing facet spec, aliased to the on-disk filename when the link target differs (e.g. `~~[[DAS Anchor Page|{slug}.md]]~~`).

{[[DAS Folder|CAB Folder]]}/
├── {CAB Folder}.md                       [[DAS Folder|marker file]]   (if NAME ≠ folder)
├── [[DAS Anchor Page|{slug}.md]]                             Primary entry point
│
├── {slug} [[DAS Design Dispatch|Design]]/               Design specs (PRD, UX, Interface, Architecture, Features, Roadmap)
│   ├── {slug} Design.md                  Dispatch page
│   ├── {slug} [[DAS Architecture|Architecture]].md       System-architecture story (single file → {slug} Architecture/ folder-doc, + subsystem docs / optional {slug} API.md, once it grows)
│   ├── {slug} [[DAS PRD|PRD]].md                 Product requirements
│   ├── {slug} [[DAS UX Design|UX Design]].md           UX spec (screens & external APIs)
│   ├── {slug} Interface.md               Top-level layer contract (required for Code anchors)
│   ├── {slug} Decisions.md               Load-bearing rulings & invariants
│   ├── {slug} [[DAS Features|Features]]/              Dated feature specs
│   │   ├── {slug} Features.md
│   │   ├── 2026-01-15 User Auth.md
│   │   └── ...
│   ├── {slug} [[DAS Roadmap|Roadmap]].md             Milestones with checkbox tracking
│   └── {slug} [[DAS Discussion|Discussion]].md  Design conversations
│
├── {slug} [[DAS Track|Track]]/                 Work-tracking metadata
│   ├── {slug} Track.md                   Dispatch page
│   ├── {slug} [[DAS Backlog|Backlog]].md             Workflow-state core (required for Track)
│   ├── {slug} [[DAS Icebox|Icebox]].md              Cold-storage / someday-maybe (optional)
│   └── {slug} [[DAS Inbox|Inbox]].md               Raw content to process (optional)
│
├── {slug} [[DAS User Dispatch|User Docs]]/              User-facing documentation
│   ├── {slug} User Docs.md               Dispatch page
│   ├── {slug} Guide.md                   Primary user guide
│   └── CONFIG_REFERENCE.md
│
├── {slug} [[DAS Dev Dispatch|Dev Docs]]/                Developer & implementation docs
│   ├── {slug} Dev Docs.md                Dispatch page (links Files + all modules)
│   ├── {slug} [[DAS All Files|Files]].md               File map with → doc links
│   ├── {slug} engine/                    ← mirrors src/engine/
│   │   ├── {slug} engine.md              [[DAS Module Doc|Module doc]] for the folder
│   │   └── {slug} Scheduler.md           [[DAS Module Doc|Module doc]] for a class
│   └── {slug} api/                       ← mirrors src/api/
│       ├── {slug} api.md
│       └── {slug} Router.md
│
├── {slug} [[DAS Cards|Cards]]/                         Cheat sheets & flashcards (optional)
├── [[DAS Claude|CLAUDE.md]]                             Claude Code config (optional)
└── [[DAS Code Repository|Code]] -> {repo-path}                   Symlink to code repository (optional)

─── Optional [[DAS Code Repository]] (under ~/ob/proj/) ───

{repo}/                          [[DAS Code Repository]]
├── .git/
├── README.md
├── justfile                     [[DAS Code Repository|Standard task recipes]]
├── docs/                        [[DAS Documentation Site|sync-pushed]] from the anchor's docs folders
│   ├── user/                    ← from {slug} User Docs/
│   └── dev/                     ← from {slug} Dev Docs/
└── src/						 See [[DAS Module Doc]] for format of linked module docs.

## Software Design Documents

Software project anchors keep their design documents in `{slug} Design/` — including the system-architecture story (`{slug} Architecture`, a single `.md` → a `{slug} Architecture/` folder-doc once it grows subsystems). These are specification-only — they contain the current design, not the history of how it was reached.

{slug} PRD.md — **Product Requirements** — Defines what the product does: goals, user stories, scope, constraints, success criteria. The PRD also contains a design workflow table (see below) that links to the other design documents and describes their sequence.

{slug} UX Design.md — **UX Design** — Specifies screens, navigation flows, user interactions, and visual layout. Current spec only — no rationale or alternatives.

{slug} Architecture — **Architecture** — A child of `{slug} Design/`: a single `{slug} Architecture.md` that upgrades to a `{slug} Architecture/` folder-doc (entry-point + subsystem docs + optional `{slug} API.md`) once it grows. Specifies system architecture, component boundaries, data models, APIs, and technical decisions. See [[DAS Architecture]]. Current spec only — no rationale or alternatives.

{slug} Discussion.md — **Discussion** (optional) — Extended conversations about design choices, trade-offs, and redesign decisions. This is the place for "why" and "what we considered." Use dated sections. Unlike the other design docs, this file is a log, not a specification.

Anchor-level questions are surfaced through `/ask` into `{slug} Track/{slug} queries.md`; per-anchor status is surfaced into the vault-wide `~/ob/kmr/Q.md` (the standalone `{slug} Triage.md` and `{slug} Questions.md` Plan-era docs are retired).

### Design Workflow

The PRD should include a workflow table like this to orient readers:

| Step | Document | Purpose |
|------|----------|---------|
| 1 | {slug} Design/{slug} PRD.md | Clarify requirements and scope |
| 2 | {slug} Track/{slug} queries.md | Items needing user input (via `/ask`) |
| 3 | {slug} Design/{slug} UX Design.md | Design user-facing experience |
| 4 | {slug} Design/{slug} Architecture.md | Design technical architecture |
| 5 | {slug} Dev Docs/{slug} Files.md + Dev Docs/ | File tree and module docs |
| 6 | {slug} Design/{slug} Roadmap.md | Implementation milestones |
| 7 | Dispatch tree | Verify all docs reachable from the anchor page (see [[DAS Anchor Page]]) |

Steps are iterative — resolving open questions may require revisiting the PRD or UX design.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + ruleset R-anchor-tree above; each named element's full semantics live in its linked facet spec.)*

- **One line of inline annotation max per element** — full semantics, rules, and shape live in the linked facet spec ([[DAS Backlog]], [[DAS Anchor Page]], etc.); don't grow this page into a multi-paragraph spec for any single facet.
- **Inclusion test for adding a row** — the element is a recognized DAS anchor file/folder (named via the `{slug}` / `{CAB Folder}` placeholders) that can legitimately appear in *some* anchor; one-off project-specific files do NOT belong here.
- **§ Software Design Documents is descriptive, not prescriptive** — its per-document paragraphs only orient readers; the authoritative shape of each doc lives in its own facet spec. Don't drift those summaries away from the linked specs.
