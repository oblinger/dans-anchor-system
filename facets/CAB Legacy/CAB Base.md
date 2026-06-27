---
cssclasses:
  - monospace
---

# CAB Base

The base specification shared by all anchor types.
- [[CAB All Files]] provides the full list of possible files in all types.


{[[CAB Folder|CAB Folder]]}/
├── {CAB Folder}.md           [[CAB Folder|marker file]]
├── [[CAB Anchor Page|{NAME}.md]]                    primary entry point (if NAME ≠ folder)
│
├── {NAME} [[CAB Architecture|Architecture]]/   system-architecture story (root-level folder)
│   ├── {NAME} Architecture.md          entry-point doc + subsystem docs
│   └── {NAME} API.md                   public-API sub-doc (optional)
│
├── {NAME} Track/                    work tracking (Track trait) — [[CAB Track Dispatch]]
│   ├── {NAME} Track.md              dispatch page
│   ├── {NAME} [[CAB Backlog|Backlog]].md   the workflow-state core (required for Track)
│   ├── {NAME} [[CAB Roadmap|Roadmap]].md   milestones with checkbox tracking (optional)
│   ├── {NAME} [[CAB Icebox|Icebox]].md     cold-storage / someday-maybe (optional)
│   ├── {NAME} [[CAB Features|Features]]/   dated feature specs
│   │   └── {NAME} Features.md            feature index (reverse chronological)
│   ├── {NAME} [[CAB Inbox|Inbox]].md       raw content to process (optional)
│   └── {NAME} ask.md                       agent-regenerated ask snapshot; also holds anchor-level questions (optional)
│
├── {NAME} Design/                   high-level system spec — [[CAB Design Dispatch]]
│   ├── {NAME} Design.md             dispatch page
│   ├── {NAME} [[CAB Interface|Interface]].md      top-level layer contract (required for Code anchors)
│   ├── {NAME} [[CAB UX Design|UX Design]].md      user-interaction shape
│   ├── {NAME} Data Model.md         data shapes & schemas (when applicable)
│   ├── {NAME} Principles.md         load-bearing rules & invariants (when applicable)
│   ├── {NAME} PRD.md                product requirements (when applicable)
│   └── {NAME} Design Discussion.md  design trade-off conversations (when applicable)
│
├── {NAME} User Docs/                end-user / consumer guides — [[CAB User Dispatch]]
│   ├── {NAME} User Docs.md          dispatch page
│   ├── {NAME} [[CAB Guide|Guide]].md          primary user guide
│   ├── {NAME} Installation.md       installation instructions (when applicable)
│   ├── {NAME} CLI.md                CLI command reference (when applicable)
│   ├── {NAME} FAQ.md                user-facing FAQs (optional)
│   └── {NAME} [[CAB Cards|Cards]]/  quick-reference cards (optional)
│
├── {NAME} Dev Docs/                 audit-tied implementation reference — [[CAB Dev Dispatch]]
│   ├── {NAME} Dev Docs.md           dispatch page
│   ├── {NAME} [[CAB Files|Files]].md      audit-generated file tree (codebase map)
│   └── &lt;per-module docs&gt;            e.g. {NAME} &lt;ModuleName&gt;.md
│
└── [[CAB Claude|CLAUDE.md]]                    Claude Code config (optional)

**Root-level docs folders (Gen-3 — no `{NAME} Docs/` container; tracked by F157).**
The five canonical docs folders sit **directly at the anchor root** (the old `{NAME} Docs/` wrapper is removed) and map to audiences. Note the naming asymmetry: Architecture / Design / Track carry **no** "Docs" suffix; User Docs / Dev Docs **do**.

- **`{NAME} Architecture/`** — the system-architecture story (entry-point doc + subsystem docs + `{NAME} API.md`). Its **own root-level folder**, NOT nested under `{NAME} Design/` (per [[CAB Architecture]] / [[FCT Architecture]]).
- **`{NAME} Design/`** — the system designer / architect (PRD, UX Design, Interface, Decisions, Data Model, Principles, Design Discussion). Interface is required for Code anchors.
- **`{NAME} Track/`** — the planning agent (Backlog, Features, Roadmap, …).
- **`{NAME} User Docs/`** — the end-user / consumer (Guide, CLI, Installation, FAQ).
- **`{NAME} Dev Docs/`** — the implementer (Files.md tree at `{NAME} Dev Docs/{NAME} Files.md` + per-module reference docs).

Associated code repository (when the anchor has the `code` trait) is
declared in `.anchor`'s `code:` key — absolute path, or relative to
the anchor root (e.g. `code: .` for inline, `code: ../../proj/foo`
for linked). See [[CAB Code Repository]].
.                                See also: [[CAB Documentation Site]]


| **[[TRT]]**    |                                                       |
| ----------------------- | ----------------------------------------------------- |
| [[Simple Anchor]]       | Folder + anchor page only                             |
| [[Topic Anchor]]        | Evergreen knowledge, child anchors, routing hub       |
| [[Code Anchor]]         | Code repo — inline (`code: .`) or linked (`code:` path) |
| [[Paper Anchor]]        | Document revision with version table + sections       |
| [[Skill Anchor]]        | Claude Code skill group in ~/.claude/skills/          |
| [[Track]]               | Capability: driven through a backlog/planning lifecycle (drive loop) |

| **[[CAB Conventions]]**         |                                              |
| ---------------------------------- | -------------------------------------------- |
| [[CAB Defined Terms]]           | Dated folder, dated sections                 |
| [[CAB Markdown Formatting]]     | Vertical spacing, named lists, file trees, TOC |
| [[CAB Naming Conventions]]      | slugs, file prefixes, auxiliary commands        |
| [[CAB Page Conventions]]        | Description field, link table conventions     |
| [[CAB Docs Conventions]]        | Standard documents, roadmap format            |
| [[CAB Documentation Publishing]] | Private vs user docs, MkDocs, generators    |
| [[CAB Repository Structure]]    | Key repo files, justfile, site/ folder        |
| [[CAB Rust Rules]]              | Workspace, shared util crate, Cargo conventions |
| [[CAB Integrations]]            | Git, GitHub Pages, Claude, tmux               |
| [[CAB Research]]                | Research folder, paper structure              |
| [[CAB Maintenance]]             | Validation checklist                          |


| **[[CAB Skills]]**    |                                     |
| ------------------------ | ----------------------------------- |
| [[CAB Setup]]         | Create a new anchor                 |
| [[CAB Tidy]]          | Validate and correct structure      |
| [[CAB PR Flow]]       | Iterative PR-based development      |
| [[CAB Pilot Flow]]    | Top-down design then implementation |
| [[CAB Move]]          | Move anchor, update all paths       |
| [[CAB Migrate]]       | Convert between anchor types        |
| [[cab-slug-scan]]      | Sync slug index                       |
| [[CAB Streams]]       | Content stream definitions          |

(`CAB Disciplines` category retired 2026-05-12 — disciplines collapsed into [[CAB Conventions]]. `CAB Template File` superseded by [[CAB Template]] under Conventions.)

# BRIEF

- **This file is the canonical base spec** shared by all anchor types — the file-tree skeleton + the three dispatch tables ([[TRT]], [[CAB Conventions]], [[CAB Skills]]). Trait-specific shape lives in `CAB <Trait>.md`; facet-specific shape lives in `CAB <Facet>.md`. Keep this file the *shared substrate*, not the union of everything.
- **The file tree is load-bearing** — paths, slot names, and wiki-links inside the tree are referenced by skills (tidy, lint, migrate, rewire) and by every other CAB facet. Do not rename slots, reorder the Gen-3 root-level docs folders (Architecture / Design / Track / User Docs / Dev Docs — no `{NAME} Docs/` container), or drop wiki-links without sweeping every dependent spec.
- **Inclusion test for a row in the three dispatch tables**: it must apply across *most* anchor types or be a system-wide convention/skill. Trait-only or facet-only items belong in their own CAB facet, not here. Conversely, anything that legitimately belongs in this base spec must appear in exactly one of the three tables — no orphaned mentions.
- **Do NOT inline trait or facet detail** — link to `CAB <Trait>.md` / `CAB <Facet>.md` instead. The base spec names the slot; the facet spec governs its contents. Piling facet rules here causes drift between this file and the facet specs.
- **Migration notes are historical context, not active spec** — the Gen-3 root-level-folders note (F157, superseding the F094 container shape) and the "Disciplines retired" line at the bottom are kept for archaeology. When the migration completes vault-wide, fold them into the body or move to a Yore note; don't let migration prose accumulate.
- **When adding a new trait, facet, convention, or skill**: add the row to the appropriate dispatch table here AND create / update its `CAB <X>.md` page. The bidirectional link is the integrity invariant — a row here without a target page (or vice versa) is a bug surfaced by `cab-lint`.
- **Authority**: this spec is cited by every anchor's structure-validation flow ([[tidy]], [[lint]], [[rewire]], [[migrate]]). Breaking changes here ripple to every anchor in the vault — propose via a feature on SKA, not an in-place edit.
