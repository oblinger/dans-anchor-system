---
description: documentation hub — links to Plan, Dev, User
---
# FCT Docs

**Location:** `{slug} Docs/{slug} Docs.md`


The `{slug} Docs/` folder organizes all planning, design, and published documentation for an anchor. It contains three subfolder areas: Plan (specs and tracking), User (end-user docs), and Dev (developer/module docs).

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Docs.md` — top-level dispatch. Open it (and its sibling `CAE Plan/`, `CAE User/`, `CAE Dev/` dispatch pages) for the real file shape.

# Format Specification

## Dispatch Tree

Every subfolder has a **dispatch page** with a dispatch table listing its contents. This creates a navigable tree:

1. **Anchor page** (`{slug}.md`) — dispatch table with Plan, User, Dev as row labels that link to their respective dispatch pages. Key items from each area appear inline in the row.
2. **`{slug} Plan.md`** — dispatch table listing all planning docs (PRD, System Design, Roadmap, etc.)
3. **`{slug} User.md`** — dispatch table listing all user-facing docs (User Guide, Config Reference, etc.)
4. **`{slug} Dev.md`** — dispatch table listing Files, Architecture, and all module docs
5. **`{slug} Docs.md`** — top-level dispatch linking to Plan, Dev, User

The anchor page row labels are wiki-links to the subfolder dispatch pages:

```markdown
| [[HBR Track|Plan]]   | [[HBR PRD|PRD]], [[CAE System Design|System Design]], ... |
| [[HBR Track|Execute]] | [[FEX Inbox|Inbox]], [[Q#CAE Triage|Triage]], ... |
| [[CAE User/CAE User|User]] | [[CAE User Guide|User Guide]], [[CAE Cards|Cards]] |
| [[CAE Dev/CAE Dev|Dev]]   | [[FEX Files|Files]], [[CAE core|core]], ... |
```

Clicking a row label navigates to the subfolder dispatch page, which has the complete list. The inline items are just highlights — the dispatch page is the authoritative index.

**Verification:** Walk the link tree from `{slug} Docs.md`. Every `.md` file in the Docs folder should be reachable. If a page is orphaned, add a link from its parent or create a missing dispatch page.


## Planning Docs — `{slug} Docs/`

Most anchors (beyond simple ones) have a `{slug} Docs/` folder containing planning and tracking documents:

| File | Purpose |
|------|---------|
| `{slug} Inbox.md` | Raw input drop zone — captures unprocessed input for integration |
| `{slug} PRD.md` | Product requirements / planning brief |
| `{slug} Roadmap.md` | High-level plan and milestones (see [[DAS Roadmap]]) |
| `{slug} Backlog.md` | Low-priority ideas and deferred work (see [[CAB Backlog]]) |
| `{slug} Icebox.md` | Cold-storage / someday-maybe items (see [[DAS Icebox]]) — optional |
| `{slug} Todo.md` | Active task tracking |
| `{slug} Features/` | Individual feature specs (see [[DAS Features]]) |
| `{slug} {Module}.md` | Source code module documentation (see [[DAS Module Doc]]) |

Not all files are required — create what's useful for the anchor. The Inbox is always created with new anchors.

## Inbox — `{slug} Inbox.md`

Every anchor has an Inbox file inside `{slug} Plan/`. This is a drop zone for raw input — long descriptions, change requests, design thoughts — that the user pastes in for an AI agent to read and integrate into the planning and documentation for this anchor.

- **Location:** Inside `{slug} Plan/`, alongside the PRD and other planning docs
- **Format:** Reverse chronological dated sections
- **Lifecycle:** Content is pasted in, processed by the agent, then left as a record. Rarely revisited after processing.
- **Purpose:** Staging area for unprocessed input + persistent log of what was communicated

## Published Docs — `docs/`

Repo-based anchors have a `docs/` folder for user-facing documentation that will be published or shipped with the project:

| File | Purpose |
|------|---------|
| `{slug} User Guide.md` | End-user documentation |
| `{slug} Architecture.md` | Technical architecture overview |

All published doc files use the `{slug}` prefix to avoid namespace collisions in Obsidian.

### Location by Anchor Type

The `docs/` folder lives in different places depending on anchor type:

- **Private Repo** — `docs/` at the anchor root (same level as `.git/`)
- **Public Repo** — `docs/` inside the repo subfolder (`{kebab-name}/docs/`)

Simple anchors and paper anchors typically don't have published docs.

See [[TRT]] for details on each anchor type.
