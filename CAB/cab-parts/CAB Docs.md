# CAB Docs

The `{NAME} Docs/` folder organizes all planning, design, and published documentation for an anchor. It contains three subfolder areas: Plan (specs and tracking), User (end-user docs), and Dev (developer/module docs).

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

```
TSK Docs/
├── TSK Docs.md                    Dispatch — links to Plan, Dev, User
│
├── TSK Plan/                      Planning & execution
│   ├── TSK Plan.md                Dispatch table of all planning docs
│   ├── TSK PRD.md
│   ├── TSK System Design.md
│   ├── TSK Roadmap.md
│   ├── TSK Backlog.md
│   ├── TSK Inbox.md
│   └── TSK Open Questions.md
│
├── TSK User/                      User-facing documentation
│   ├── TSK User.md                Dispatch table of all user docs
│   └── TSK User Guide.md
│
└── TSK Dev/                       Developer & implementation docs
    ├── TSK Dev.md                  Dispatch table — Files, Architecture, modules
    ├── TSK Architecture.md
    └── TSK execution/              Mirrors source tree
        └── TSK Scheduler.md        Module doc
```

Each dispatch page uses a dispatch table:

```markdown
| -[[TSK Plan]]-                           | +: planning and execution docs  |
| ---------------------------------------- | ------------------------------- |
| [[TSK PRD|PRD]]                         | product requirements            |
| [[TSK System Design|System Design]]     | architecture and design         |
| [[TSK Inbox|Inbox]]                     | raw input to process            |
| [[TSK Open Questions|Open Questions]]   | unresolved decisions            |
| [[TSK Backlog|Backlog]]                 | deferred work                   |
| [[TSK Roadmap|Roadmap]]                 | milestones                      |
```

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
| [[TSK Plan|Plan]]   | [[TSK PRD|PRD]], [[TSK System Design|System Design]], ... |
| [[TSK Plan|Execute]] | [[TSK Inbox|Inbox]], [[TSK Open Questions|Open Questions]], ... |
| [[TSK User/TSK User|User]] | [[TSK User Guide|User Guide]], [[TSK Cards|Cards]] |
| [[TSK Dev/TSK Dev|Dev]]   | [[TSK Files|Files]], [[TSK core|core]], ... |
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
| `{NAME} Todo.md` | Active task tracking |
| `{NAME} Features/` | Individual feature specs (see [[CAB Features]]) |
| `{NAME} {Module}.md` | Source code module documentation (see [[CAB Module Doc]]) |

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

See [[CAB Types]] for details on each anchor type.
