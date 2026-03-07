# CAB Docs

The `{NAME} Docs/` folder organizes all planning, design, and published documentation for an anchor. It contains three subfolder areas: Plan (specs and tracking), User (end-user docs), and Dev (developer/module docs).

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

```
TSK Docs/
├── TSK Docs.md                    Dispatch page
│
├── TSK Plan/                      Planning & spec
│   ├── TSK Plan.md                Dispatch page
│   ├── TSK PRD.md                 Product requirements
│   ├── TSK Open Questions.md      Unresolved questions
│   ├── TSK System Design.md       System architecture
│   ├── TSK Roadmap.md             Milestones
│   ├── TSK Backlog.md             Deferred work
│   ├── TSK Files.md               File tree map
│   └── TSK Inbox.md               Raw content to process
│
├── TSK User/                      User-facing documentation
│   ├── TSK User.md                Dispatch page
│   └── TSK User Guide.md          End-user guide
│
└── TSK Dev/                       Developer & implementation docs
    ├── TSK Dev.md                  Dispatch page (links Files + all modules)
    ├── TSK Architecture.md         System-level design
    └── TSK execution/              Mirrors source tree
        └── TSK Scheduler.md        Module doc
```

---



# Format Specification

## Dispatch Tree

Every markdown file in the Docs folder must be reachable by walking wiki-links from `{NAME} Docs.md`. The structure:

1. **`{NAME} Docs.md`** — top dispatch. Links to Plan, Dev, User, Design areas.
2. **`{NAME} Dev.md`** — Dev dispatch. Links to [[CAB Files|{NAME} Files]] (the file tree) and all module aggregator pages.
3. **Module aggregators** (e.g., `{NAME} App.md`) — link to individual class/struct docs.
4. **Individual docs** — leaf pages with a breadcrumb line back to their aggregator: ` [[parent]] → This Page`

The Dev dispatch page links to Files because Files is the bridge between "what files exist" and "what they do" — it's the natural starting point when exploring the codebase.

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
