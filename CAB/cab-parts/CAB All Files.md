---
cssclasses:
  - monospace
---

# CAB All Files

An anchor is a standardized folder structure that serves as the home for a project, topic, or content area.
See [[CAB Base]] shows files common to all anchors.

> **Note:** This file serves as the reference example itself — the annotated file tree below IS the canonical illustration of a complete anchor structure.

{[[CAB Folder|CAB Folder]]}/
├── {CAB Folder}.md                       [[CAB Folder|marker file]]   (if NAME ≠ folder)
├── [[CAB Anchor Page|{NAME}.md]]                             Primary entry point
│
├── {NAME} [[CAB Docs|Docs]]/
│   ├── {NAME} Docs.md                    Dispatch page
│   │
│   ├── {NAME} Plan/                      Planning & spec
│   │   ├── {NAME} Plan.md                Dispatch page
│   │   ├── {NAME} [[CAB PRD|PRD]].md                 Product requirements
│   │   ├── {NAME} [[CAB Open Questions|Open Questions]].md      Unresolved questions
│   │   ├── {NAME} [[CAB UX Design|UX Design]].md           UX spec (screens & external APIs)
│   │   ├── {NAME} [[CAB System Design|System Design]].md       System architecture & impl design
│   │   ├── {NAME} [[CAB Discussion|Discussion]].md  Design conversations
│   │   ├── {NAME} [[CAB Features|Features]]/              Dated feature specs
│   │   │   ├── {NAME} Features.md
│   │   │   ├── 2026-01-15 User Auth.md
│   │   │   └── ...
│   │   ├── {NAME} [[CAB Backlog|Backlog]].md             Deferred work
│   │   ├── {NAME} [[CAB Files|Files]].md               File map with → doc links
│   │   ├── {NAME} [[CAB Roadmap|Roadmap]].md             Milestones with checkbox tracking
│   │   └── {NAME} [[CAB Inbox|Inbox]].md               Raw content to process
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
│       │   ├── {NAME} engine.md         [[CAB Module Doc|Module doc]] for the folder
│       │   └── {NAME} Scheduler.md      [[CAB Module Doc|Module doc]] for a class
│       └── {NAME} api/                  ← mirrors src/api/
│           ├── {NAME} api.md
│           └── {NAME} Router.md
│
├── {NAME} [[CAB Cards|Cards]]/                         Cheat sheets & flashcards (optional)
├── [[CAB Claude|CLAUDE.md]]                             Claude Code config (optional)
└── [[CAB Code Repository|Code]] -> {repo-path}                   Symlink to code repository (optional)



─── Optional [[CAB Code Repository]] (under ~/ob/proj/) ───

{repo}/                          [[CAB Code Repository]]
├── .git/
├── README.md
├── justfile                     [[CAB Repository Structure|Standard task recipes]]
├── docs/                        [[CAB Documentation Site|sync-pushed]] from {NAME} Docs/
│   ├── user/                    ← from {NAME} User/
│   └── dev/                     ← from {NAME} Dev/
└── src/						 See [[CAB Module Doc]] for format of linked module docs.


## Software Design Documents

Software project anchors use four design documents in Plan/. These are specification-only — they contain the current design, not the history of how it was reached.

{NAME} PRD.md — **Product Requirements** — Defines what the product does: goals, user stories, scope, constraints, success criteria. The PRD also contains a design workflow table (see below) that links to the other design documents and describes their sequence.

{NAME} Open Questions.md — **Open Questions** — Tracks unresolved questions that block design decisions. Each question should state what it blocks and what information is needed to resolve it. Questions are removed or moved to Discussion once resolved.

{NAME} UX Design.md — **UX Design** — Specifies screens, navigation flows, user interactions, and visual layout. Current spec only — no rationale or alternatives.

{NAME} System Design.md — **System Design** — Specifies system architecture, component boundaries, data models, APIs, and technical decisions. Current spec only — no rationale or alternatives.

{NAME} Discussion.md — **Discussion** (optional) — Extended conversations about design choices, trade-offs, and redesign decisions. This is the place for "why" and "what we considered." Use dated sections. Unlike the other design docs, this file is a log, not a specification.


### Design Workflow

The PRD should include a workflow table like this to orient readers:

| Step | Document | Purpose |
|------|----------|---------|
| 1 | {NAME} PRD.md | Clarify requirements and scope |
| 2 | {NAME} Open Questions.md | Surface and resolve unknowns |
| 3 | {NAME} UX Design.md | Design user-facing experience |
| 4 | {NAME} System Design.md | Design technical architecture |
| 5 | {NAME} Files.md + Dev/ | File tree and module docs |
| 6 | {NAME} Roadmap.md | Implementation milestones |
| 7 | Dispatch tree | Verify all docs reachable from Docs.md (see [[CAB Docs]]) |

Steps are iterative — resolving open questions may require revisiting the PRD or UX design.
