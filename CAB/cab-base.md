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
├── {NAME} [[CAB Docs|Docs]]/
│   ├── {NAME} Docs.md           dispatch page
│   └── {NAME} Plan/             planning & specification
│       ├── {NAME} PRD.md        product requirements
│       ├── {NAME} [[CAB Roadmap|Roadmap]].md    milestones with checkbox tracking
│       ├── {NAME} [[CAB Backlog|Backlog]].md    deferred work (optional)
│       ├── {NAME} [[CAB Icebox|Icebox]].md     cold-storage / someday-maybe (optional)
│       ├── {NAME} [[CAB Files|Files]].md      codebase map (optional)
│       ├── {NAME} [[CAB Features|Features]]/     dated feature specs
│       │   └── {NAME} Features.md   feature index (reverse chronological)
│       └── {NAME} [[CAB Inbox|Inbox]].md      raw content to process
│
├── {NAME} [[CAB Cards|Cards]]/                cheat sheets & flashcards (optional)
└── [[CAB Claude|CLAUDE.md]]                    Claude Code config (optional)

Associated code repository (when the anchor has the `code` trait) is
declared in `.anchor`'s `code:` key — absolute path, or relative to
the anchor root (e.g. `code: .` for inline, `code: ../../proj/foo`
for linked). See [[CAB Code Repository]].
.                                See also: [[CAB Documentation Site]]


| **[[CAB Traits]]**    |                                                       |
| ----------------------- | ----------------------------------------------------- |
| [[Simple Anchor]]       | Folder + anchor page only                             |
| [[Topic Anchor]]        | Evergreen knowledge, child anchors, routing hub       |
| [[Code Anchor]]         | Code repo — inline (`code: .`) or linked (`code:` path) |
| [[Paper Anchor]]        | Document revision with version table + sections       |
| [[Skill Anchor]]        | Claude Code skill group in ~/.claude/skills/          |

| **[[CAB Rules Index]]**         |                                              |
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
