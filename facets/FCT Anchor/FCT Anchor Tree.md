---
cssclasses:
  - monospace
description: anchor master tree — every possible doc/folder in an anchor, linked to its facet spec
---
# FCT Anchor Tree
The annotated master file tree showing every possible file and folder that may appear inside a CAB anchor, with each named element wiki-linked to its governing facet spec.

| -[[FCT Anchor Tree]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Anchor Tree](hook://p/FCT%20Anchor%20Tree)<br>: anchor master tree — every possible doc/folder in an anchor, linked to its facet spec |
| --- | --- |
| Related | [[FCT Anchor Page]],  [[CAB Base]],  [[CAB Docs]],  [[FCT Facet]],   |
| Examples | [[CAE\|minimal Code anchor]],  [[HBR\|fuller anchor with components]],   |

**Cardinality: one per anchor** — each anchor has exactly one canonical file tree (this spec is the reference; an anchor's actual tree is its on-disk directory).

An anchor is a standardized folder structure that serves as the home for a project, topic, or content area.
See [[CAB Base]] shows files common to all anchors.

**TLDR** — The annotated master file tree for a CAB anchor: every recognized file/folder placeholder wiki-linked to its governing facet spec. Two trees: the anchor folder tree (top) and the optional Code Repository tree (bottom). Use this as a lookup when setting up or auditing an anchor's on-disk structure.

> **Note:** This file serves as the reference example itself — the annotated file tree below IS the canonical illustration of a complete anchor structure.

{[[FCT Folder|CAB Folder]]}/
├── {CAB Folder}.md                       [[FCT Folder|marker file]]   (if NAME ≠ folder)
├── [[FCT Anchor Page|{NAME}.md]]                             Primary entry point
│
├── {NAME} [[FCT Architecture|Architecture]]/            System-architecture story (root-level folder)
│   ├── {NAME} Architecture.md            Entry-point doc + subsystem docs
│   └── {NAME} API.md                     Public-API sub-doc (optional)
│
├── {NAME} [[FCT Design Dispatch|Design]]/               Design specs (PRD, UX, Interface, Features, Roadmap)
│   ├── {NAME} Design.md                  Dispatch page
│   ├── {NAME} [[FCT PRD|PRD]].md                 Product requirements
│   ├── {NAME} [[FCT UX Design|UX Design]].md           UX spec (screens & external APIs)
│   ├── {NAME} Interface.md               Top-level layer contract (required for Code anchors)
│   ├── {NAME} Decisions.md               Load-bearing rulings & invariants
│   ├── {NAME} [[FCT Features|Features]]/              Dated feature specs
│   │   ├── {NAME} Features.md
│   │   ├── 2026-01-15 User Auth.md
│   │   └── ...
│   ├── {NAME} [[FCT Roadmap|Roadmap]].md             Milestones with checkbox tracking
│   └── {NAME} [[FCT Discussion|Discussion]].md  Design conversations
│
├── {NAME} [[FCT Track Dispatch|Track]]/                 Work-tracking metadata
│   ├── {NAME} Track.md                   Dispatch page
│   ├── {NAME} [[CAB Backlog|Backlog]].md             Workflow-state core (required for Track)
│   ├── {NAME} [[FCT Icebox|Icebox]].md              Cold-storage / someday-maybe (optional)
│   └── {NAME} [[FCT Inbox|Inbox]].md               Raw content to process (optional)
│
├── {NAME} [[FCT User Dispatch|User Docs]]/              User-facing documentation
│   ├── {NAME} User Docs.md               Dispatch page
│   ├── {NAME} Guide.md                   Primary user guide
│   └── CONFIG_REFERENCE.md
│
├── {NAME} [[FCT Dev Dispatch|Dev Docs]]/                Developer & implementation docs
│   ├── {NAME} Dev Docs.md                Dispatch page (links Files + all modules)
│   ├── {NAME} [[FCT All Files|Files]].md               File map with → doc links
│   ├── {NAME} engine/                    ← mirrors src/engine/
│   │   ├── {NAME} engine.md              [[FCT Module Doc|Module doc]] for the folder
│   │   └── {NAME} Scheduler.md           [[FCT Module Doc|Module doc]] for a class
│   └── {NAME} api/                       ← mirrors src/api/
│       ├── {NAME} api.md
│       └── {NAME} Router.md
│
├── {NAME} [[FCT Cards|Cards]]/                         Cheat sheets & flashcards (optional)
├── [[FCT Claude|CLAUDE.md]]                             Claude Code config (optional)
└── [[FCT Code Repository|Code]] -> {repo-path}                   Symlink to code repository (optional)



─── Optional [[FCT Code Repository]] (under ~/ob/proj/) ───

{repo}/                          [[FCT Code Repository]]
├── .git/
├── README.md
├── justfile                     [[CAB Repository Structure|Standard task recipes]]
├── docs/                        [[FCT Documentation Site|sync-pushed]] from the anchor's docs folders
│   ├── user/                    ← from {NAME} User Docs/
│   └── dev/                     ← from {NAME} Dev Docs/
└── src/						 See [[FCT Module Doc]] for format of linked module docs.


## Software Design Documents

Software project anchors keep their design documents in `{NAME} Design/`; the system-architecture story lives in its own root-level `{NAME} Architecture/` folder. These are specification-only — they contain the current design, not the history of how it was reached.

{NAME} PRD.md — **Product Requirements** — Defines what the product does: goals, user stories, scope, constraints, success criteria. The PRD also contains a design workflow table (see below) that links to the other design documents and describes their sequence.

{NAME} UX Design.md — **UX Design** — Specifies screens, navigation flows, user interactions, and visual layout. Current spec only — no rationale or alternatives.

{NAME} Architecture/ — **Architecture** — Its own root-level folder (entry-point `{NAME} Architecture.md` + subsystem docs + optional `{NAME} API.md`). Specifies system architecture, component boundaries, data models, APIs, and technical decisions. See [[FCT Architecture]]. Current spec only — no rationale or alternatives.

{NAME} Discussion.md — **Discussion** (optional) — Extended conversations about design choices, trade-offs, and redesign decisions. This is the place for "why" and "what we considered." Use dated sections. Unlike the other design docs, this file is a log, not a specification.

Anchor-level questions are surfaced through `/query` into `{NAME} Track/{NAME} queries.md`; per-anchor status is surfaced into the vault-wide `~/ob/kmr/Q.md` (the standalone `{NAME} Triage.md` and `{NAME} Questions.md` Plan-era docs are retired).


### Design Workflow

The PRD should include a workflow table like this to orient readers:

| Step | Document | Purpose |
|------|----------|---------|
| 1 | {NAME} Design/{NAME} PRD.md | Clarify requirements and scope |
| 2 | {NAME} Track/{NAME} queries.md | Items needing user input (via `/query`) |
| 3 | {NAME} Design/{NAME} UX Design.md | Design user-facing experience |
| 4 | {NAME} Architecture/{NAME} Architecture.md | Design technical architecture |
| 5 | {NAME} Dev Docs/{NAME} Files.md + Dev Docs/ | File tree and module docs |
| 6 | {NAME} Design/{NAME} Roadmap.md | Implementation milestones |
| 7 | Dispatch tree | Verify all docs reachable from the anchor page (see [[FCT Anchor Page]]) |

Steps are iterative — resolving open questions may require revisiting the PRD or UX design.

# RULESET R-anchor-tree
include::
where:: file: **/FCT Anchor Tree.md
description:: Rules governing the FCT Anchor Tree facet spec — the annotated master file tree of a CAB anchor. Covers content integrity, naming conventions, tree rendering, and cross-reference sync.

### RULE R-anchor-tree-01 — Every named element is wiki-linked to its facet spec (checked)
Every named file or folder placeholder in the tree (e.g. `{NAME} Backlog.md`, `CLAUDE.md`) carries a `[[FCT <Name>]]` wiki-link to the governing facet spec. Inline aliases to the on-disk filename are permitted (`[[FCT Anchor Page|{NAME}.md]]`).
**Check pattern:** no unlinked placeholder name in the tree body (scan for `{NAME} <Word>.md` lines lacking `[[`).
**Tier:** checked

### RULE R-anchor-tree-02 — Box-drawing characters and monospace cssclass are preserved (checked)
The tree uses Unicode box-drawing characters (`├──`, `│`, `└──`). The frontmatter must carry `cssclasses: monospace` (or a list including `monospace`) so the tree renders correctly in Obsidian.
**Check pattern:** frontmatter contains `cssclasses` with `monospace`; tree lines contain `├──` or `└──`.
**Tier:** checked

### RULE R-anchor-tree-03 — Two trees are kept separate by the Optional divider (sampled)
The anchor folder tree (top) and the optional Code Repository tree (bottom) are separated by a `─── Optional … ───` divider line. No code-repo paths appear above the divider; no anchor-tree placeholders appear below it.
**Check pattern:** the divider line `─── Optional` is present; `{repo}/` section is below it.
**Tier:** sampled

### RULE R-anchor-tree-04 — Cross-reference sync with CAB Base, SKILL.md, and CAB Rules.md (stated)
When adding or removing a named element in the tree, the corresponding dispatch tables in `CAB Base.md`, `SKILL.md`, and `CAB Rules.md` are updated to stay in sync.
**Check pattern:** stated principle; agent verifies on each tree-content edit.
**Tier:** stated

# BRIEF

- **This file is the canonical illustration of a complete CAB anchor file tree** — it is itself the reference example, not just a description of one. Every name in the tree wiki-links to the facet spec that governs that name.
- **NOT a place to author facet semantics.** Each named file/folder gets ONE line of inline annotation max; full semantics, rules, and shape live in the linked `CAB <Facet>.md` (`[[CAB Backlog]]`, `[[FCT Anchor Page]]`, etc.). Don't grow this page into a multi-paragraph spec for any single facet.
- **Inclusion test for adding a row:** the element is a recognized CAB anchor file/folder (named via the `{NAME}` / `{CAB Folder}` placeholders) that can legitimately appear in *some* anchor. One-off project-specific files do NOT belong here.
- **Naming conventions:** placeholders use `{NAME}` for the anchor name and `{CAB Folder}` for the folder name; wiki-link the canonical facet, aliased to the on-disk filename when the link target differs (e.g. `[[FCT Anchor Page|{NAME}.md]]`). Preserve the box-drawing characters (`├──`, `│`, `└──`) — the monospace `cssclasses` frontmatter is load-bearing for tree rendering.
- **Two trees live here**: the anchor folder tree (top) and the optional Code Repository tree (bottom, separated by `─── Optional ... ───`). Keep them separated; don't merge code-repo files into the anchor tree.
- **Load-bearing cross-references** — `CAB Base.md`, `SKILL.md`, and `CAB Rules.md` index this file's contents per the SKA CLAUDE.md cross-reference checklist. When adding or removing a named element here, verify the corresponding dispatch tables in those three files stay in sync.
- **Software Design Documents section is descriptive, not prescriptive** — the per-document paragraphs orient readers to the four (now six) Plan/ design docs; the authoritative shape of each lives in its own `CAB <Facet>.md`. Don't drift those summaries away from the linked specs.
