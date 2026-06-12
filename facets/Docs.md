---
description: documentation hub — links to Plan, Dev, User
---
# CAB Docs

**Location:** `{NAME} Docs/{NAME} Docs.md`


The `{NAME} Docs/` folder organizes all planning, design, and published documentation for an anchor. It contains three subfolder areas: Plan (specs and tracking), User (end-user docs), and Dev (developer/module docs).

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Docs.md` — top-level dispatch.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

```
CAE Docs/
├── CAE Docs.md                    Dispatch — links to Plan, Dev, User
│
├── CAE Plan/                      Planning & execution
│   ├── CAE Plan.md                Dispatch table of all planning docs
│   ├── CAE PRD.md
│   ├── CAE System Design.md
│   ├── CAE Roadmap.md
│   ├── CAE Backlog.md
│   ├── CAE Icebox.md                  (optional)
│   ├── CAE Inbox.md
│   └── CAE Triage.md
│
├── CAE User/                      User-facing documentation
│   ├── CAE User.md                Dispatch table of all user docs
│   └── CAE User Guide.md
│
└── CAE Dev/                       Developer & implementation docs
    ├── CAE Dev.md                  Dispatch table — Files, Architecture, modules
    ├── CAE Architecture.md
    └── CAE execution/              Mirrors source tree
        └── CAE Scheduler.md        Module doc
```

Each dispatch page uses the standard top-of-doc format per F060 — H1 + dispatch table:

```markdown
# CAE Plan

| -[[CAE Track]]-                           | ><br>: planning docs            |
| ---------------------------------------- | ------------------------------- |
| [[CAE PRD\|PRD]]                         | product requirements            |
| [[CAE System Design\|System Design]]     | architecture and design         |
| [[CAE Inbox\|Inbox]]                     | raw input to process            |
| [[CAE Triage\|Triage]]                   | triage inbox (agent-owned)      |
| [[CAE Backlog\|Backlog]]                 | deferred work                   |
| [[CAE Icebox\|Icebox]]                   | cold-storage / someday-maybe (optional) |
| [[CAE Roadmap\|Roadmap]]                 | milestones                      |
| ---                                      |                                 |
```

The trailing `---` row is the auto-management separator — rewire auto-lists any remaining children below it.

---



# Format Specification

## Dispatch Tree

Every subfolder has a **dispatch page** with a dispatch table listing its contents. This creates a navigable tree:

1. **Anchor page** (`{NAME}.md`) — dispatch table with Plan, User, Dev as row labels that link to their respective dispatch pages. Key items from each area appear inline in the row.
2. **`{NAME} Plan.md`** — dispatch table listing all planning docs (PRD, System Design, Roadmap, etc.)
3. **`{NAME} User.md`** — dispatch table listing all user-facing docs (User Guide, Config Reference, etc.)
4. **`{NAME} Dev.md`** — dispatch table listing Files, Architecture, and all module docs
5. **`{NAME} Docs.md`** — top-level dispatch linking to Plan, Dev, User

The anchor page row labels are wiki-links to the subfolder dispatch pages:

```markdown
| [[CAE Track|Plan]]   | [[CAE PRD|PRD]], [[CAE System Design|System Design]], ... |
| [[CAE Track|Execute]] | [[CAE Inbox|Inbox]], [[Q#CAE Triage|Triage]], ... |
| [[CAE User/CAE User|User]] | [[CAE User Guide|User Guide]], [[CAE Cards|Cards]] |
| [[CAE Dev/CAE Dev|Dev]]   | [[CAE Files|Files]], [[CAE core|core]], ... |
```

Clicking a row label navigates to the subfolder dispatch page, which has the complete list. The inline items are just highlights — the dispatch page is the authoritative index.

**Verification:** Walk the link tree from `{NAME} Docs.md`. Every `.md` file in the Docs folder should be reachable. If a page is orphaned, add a link from its parent or create a missing dispatch page.


## Planning Docs — `{NAME} Docs/`

Most anchors (beyond simple ones) have a `{NAME} Docs/` folder containing planning and tracking documents:

| File | Purpose |
|------|---------|
| `{NAME} Inbox.md` | Raw input drop zone — captures unprocessed input for integration |
| `{NAME} PRD.md` | Product requirements / planning brief |
| `{NAME} Roadmap.md` | High-level plan and milestones (see [[CAB Roadmap]]) |
| `{NAME} Backlog.md` | Low-priority ideas and deferred work (see [[CAB Backlog]]) |
| `{NAME} Icebox.md` | Cold-storage / someday-maybe items (see [[CAB Icebox]]) — optional |
| `{NAME} Todo.md` | Active task tracking |
| `{NAME} Features/` | Individual feature specs (see [[CAB Features]]) |
| `{NAME} {Module}.md` | Source code module documentation (see [[CAB API Doc]]) |

Not all files are required — create what's useful for the anchor. The Inbox is always created with new anchors.

## Inbox — `{NAME} Inbox.md`

Every anchor has an Inbox file inside `{NAME} Plan/`. This is a drop zone for raw input — long descriptions, change requests, design thoughts — that the user pastes in for an AI agent to read and integrate into the planning and documentation for this anchor.

- **Location:** Inside `{NAME} Plan/`, alongside the PRD and other planning docs
- **Format:** Reverse chronological dated sections
- **Lifecycle:** Content is pasted in, processed by the agent, then left as a record. Rarely revisited after processing.
- **Purpose:** Staging area for unprocessed input + persistent log of what was communicated

## Published Docs — `docs/`

Repo-based anchors have a `docs/` folder for user-facing documentation that will be published or shipped with the project:

| File | Purpose |
|------|---------|
| `{NAME} User Guide.md` | End-user documentation |
| `{NAME} Architecture.md` | Technical architecture overview |

All published doc files use the `{NAME}` prefix to avoid namespace collisions in Obsidian.

### Location by Anchor Type

The `docs/` folder lives in different places depending on anchor type:

- **Private Repo** — `docs/` at the anchor root (same level as `.git/`)
- **Public Repo** — `docs/` inside the repo subfolder (`{kebab-name}/docs/`)

Simple anchors and paper anchors typically don't have published docs.

See [[CAB Traits]] for details on each anchor type.
