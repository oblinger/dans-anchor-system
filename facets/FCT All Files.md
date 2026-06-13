---
cssclasses:
  - monospace
description: master file tree listing all possible anchor files
---
# CAB All Files

The annotated master file tree showing every possible file and folder that may appear inside a CAB anchor, with each named element wiki-linked to its governing facet spec.

An anchor is a standardized folder structure that serves as the home for a project, topic, or content area.
See [[CAB Base]] shows files common to all anchors.

> **Note:** This file serves as the reference example itself — the annotated file tree below IS the canonical illustration of a complete anchor structure.

{[[FCT Folder|CAB Folder]]}/
├── {CAB Folder}.md                       [[FCT Folder|marker file]]   (if NAME ≠ folder)
├── [[FCT Anchor Page|{NAME}.md]]                             Primary entry point
│
├── {NAME} [[CAB Docs|Docs]]/
│   ├── {NAME} Docs.md                    Dispatch page
│   │
│   ├── {NAME} Plan/                      Planning & spec
│   │   ├── {NAME} Plan.md                Dispatch page
│   │   ├── {NAME} [[FCT PRD|PRD]].md                 Product requirements
│   │   ├── {NAME} [[FCT Triage|Triage]].md                Triage inbox (agent-owned; status of the anchor)
│   │   ├── {NAME} [[FCT Questions|Questions]].md             À la carte questions facet (agent-owned)
│   │   ├── {NAME} [[FCT UX Design|UX Design]].md           UX spec (screens & external APIs)
│   │   ├── {NAME} [[FCT System Design|System Design]].md       System architecture & impl design
│   │   ├── {NAME} [[FCT Discussion|Discussion]].md  Design conversations
│   │   ├── {NAME} [[FCT Features|Features]]/              Dated feature specs
│   │   │   ├── {NAME} Features.md
│   │   │   ├── 2026-01-15 User Auth.md
│   │   │   └── ...
│   │   ├── {NAME} [[CAB Backlog|Backlog]].md             Deferred work
│   │   ├── {NAME} [[FCT Icebox|Icebox]].md              Cold-storage / someday-maybe (optional)
│   │   ├── {NAME} [[FCT Files|Files]].md               File map with → doc links
│   │   ├── {NAME} [[FCT Roadmap|Roadmap]].md             Milestones with checkbox tracking
│   │   └── {NAME} [[FCT Inbox|Inbox]].md               Raw content to process
│   │
│   ├── {NAME} User/                      User-facing documentation
│   │   ├── {NAME} User.md
│   │   ├── {NAME} User Guide.md
│   │   └── CONFIG_REFERENCE.md
│   │
│   └── {NAME} Dev/                       Developer & implementation docs
│       ├── {NAME} Dev.md                Dispatch page (links Files + all modules)
│       ├── {NAME} Architecture.md       System-level design
│       ├── {NAME} engine/               ← mirrors src/engine/
│       │   ├── {NAME} engine.md         [[FCT API Doc|Module doc]] for the folder
│       │   └── {NAME} Scheduler.md      [[FCT API Doc|Module doc]] for a class
│       └── {NAME} api/                  ← mirrors src/api/
│           ├── {NAME} api.md
│           └── {NAME} Router.md
│
├── {NAME} [[FCT Cards|Cards]]/                         Cheat sheets & flashcards (optional)
├── [[FCT Claude|CLAUDE.md]]                             Claude Code config (optional)
└── [[FCT Code Repository|Code]] -> {repo-path}                   Symlink to code repository (optional)



─── Optional [[FCT Code Repository]] (under ~/ob/proj/) ───

{repo}/                          [[FCT Code Repository]]
├── .git/
├── README.md
├── justfile                     [[CAB Repository Structure|Standard task recipes]]
├── docs/                        [[FCT Documentation Site|sync-pushed]] from {NAME} Docs/
│   ├── user/                    ← from {NAME} User/
│   └── dev/                     ← from {NAME} Dev/
└── src/						 See [[FCT API Doc]] for format of linked module docs.


## Software Design Documents

Software project anchors use four design documents in Plan/. These are specification-only — they contain the current design, not the history of how it was reached.

{NAME} PRD.md — **Product Requirements** — Defines what the product does: goals, user stories, scope, constraints, success criteria. The PRD also contains a design workflow table (see below) that links to the other design documents and describes their sequence.

{NAME} Triage.md — **Triage** — Agent-owned inbox showing the **status of the anchor** — every item except those in `## Later` and `## Icebox`, grouped by workflow state (Active / Ready / Now / Next), in source order from the backlog. Status brackets carry counts (`**[3 Questions]**`, `**[Verify]**`). H1 banner has an anchor TAG (`[U]` / `[A]` / `[U+A]` / `[G]` / `[?]` / `[]`) plus pipe-grouped totals. À la carte questions live in the sibling `{NAME} Questions.md` facet; Triage just carries a bullet line linking to it. Destructively rewritten on each `/ask` or `/triage` run; the user reads and responds with shorthand.

{NAME} Questions.md — **Questions** — Agent-owned facet for **à la carte** (cross-cutting, anchor-level, agent-raised) questions that don't belong to any feature doc. Same `## Open Questions` block format as feature docs (per [[SKA ask]]); same Phase 1 / 2 / 3 lifecycle. Created on first à la carte `/ask` against the anchor; updated on every à la carte `/ask`.

{NAME} UX Design.md — **UX Design** — Specifies screens, navigation flows, user interactions, and visual layout. Current spec only — no rationale or alternatives.

{NAME} System Design.md — **System Design** — Specifies system architecture, component boundaries, data models, APIs, and technical decisions. Current spec only — no rationale or alternatives.

{NAME} Discussion.md — **Discussion** (optional) — Extended conversations about design choices, trade-offs, and redesign decisions. This is the place for "why" and "what we considered." Use dated sections. Unlike the other design docs, this file is a log, not a specification.


### Design Workflow

The PRD should include a workflow table like this to orient readers:

| Step | Document | Purpose |
|------|----------|---------|
| 1 | {NAME} PRD.md | Clarify requirements and scope |
| 2 | {NAME} Triage.md | Inbox of items needing user input (auto-generated) |
| 3 | {NAME} UX Design.md | Design user-facing experience |
| 4 | {NAME} System Design.md | Design technical architecture |
| 5 | {NAME} Files.md + Dev/ | File tree and module docs |
| 6 | {NAME} Roadmap.md | Implementation milestones |
| 7 | Dispatch tree | Verify all docs reachable from Docs.md (see [[CAB Docs]]) |

Steps are iterative — resolving open questions may require revisiting the PRD or UX design.

# BRIEF

- **This file is the canonical illustration of a complete CAB anchor file tree** — it is itself the reference example, not just a description of one. Every name in the tree wiki-links to the facet spec that governs that name.
- **NOT a place to author facet semantics.** Each named file/folder gets ONE line of inline annotation max; full semantics, rules, and shape live in the linked `CAB <Facet>.md` (`[[CAB Backlog]]`, `[[FCT Anchor Page]]`, etc.). Don't grow this page into a multi-paragraph spec for any single facet.
- **Inclusion test for adding a row:** the element is a recognized CAB anchor file/folder (named via the `{NAME}` / `{CAB Folder}` placeholders) that can legitimately appear in *some* anchor. One-off project-specific files do NOT belong here.
- **Naming conventions:** placeholders use `{NAME}` for the anchor name and `{CAB Folder}` for the folder name; wiki-link the canonical facet, aliased to the on-disk filename when the link target differs (e.g. `[[FCT Anchor Page|{NAME}.md]]`). Preserve the box-drawing characters (`├──`, `│`, `└──`) — the monospace `cssclasses` frontmatter is load-bearing for tree rendering.
- **Two trees live here**: the anchor folder tree (top) and the optional Code Repository tree (bottom, separated by `─── Optional ... ───`). Keep them separated; don't merge code-repo files into the anchor tree.
- **Load-bearing cross-references** — `CAB Base.md`, `SKILL.md`, and `CAB Rules.md` index this file's contents per the SKA CLAUDE.md cross-reference checklist. When adding or removing a named element here, verify the corresponding dispatch tables in those three files stay in sync.
- **Software Design Documents section is descriptive, not prescriptive** — the per-document paragraphs orient readers to the four (now six) Plan/ design docs; the authoritative shape of each lives in its own `CAB <Facet>.md`. Don't drift those summaries away from the linked specs.
