---
description: Messages facet — the agent's per-anchor inbox of background-process messages that the agent reads on every pause. Distinct from `{slug} Inbox.md` which is the user's drop-zone for raw input.
---

# DAS Messages
Spec for the **Messages facet** — the per-anchor file `{slug} Messages.md` that holds background-process notes for the agent to read on every pause, separate from the user's raw-input `{slug} Inbox.md`.

| -[[DAS Messages]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Messages](hook://p/DAS%20Messages) |
| --- | --- |
| Related | [[templates/messages.md\|messages template]],  [[DAS Inbox]],  [[DAS Backlog]],  [[DAS Track]],  [[DAS Anchor Tree]],   |
| Examples | [[HBR Messages\|minimal]],  [[HBR Messages\|with real system messages]],   |
| Rules | [[R-messages]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Cardinality: one per anchor** — each anchor has exactly one `{slug} Messages.md` file at its root.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. It defines the `{slug} Messages.md` facet; it is not itself a messages file.)*

- **Inclusion test** — content belongs here only when it defines how Messages files are structured, written, read, or pruned across anchors; per-anchor message content or single-anchor examples belong elsewhere. Routing for displaced content: project-wide rules → CLAUDE.md; markdown-rendering → [[R-markdown]]; Inbox-facet rules → `CAB Inbox.md`.
- **Load-bearing distinction to preserve** — the frontmatter `description` and R-messages-03 both fix the Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input); any edit that loosens or removes that distinction breaks the facet's reason for existing.
- **Cross-references to keep in sync** — [[DAS Anchor Tree]] dispatch tables, [[DAS Anchor Tree]] tree, and any anchor template that scaffolds a `{slug} Messages.md`.
- **Conventions** — refer to sibling facets by their CAB filename (`~~[[DAS Inbox]]~~`, `[[DAS Backlog]]`); refer to per-anchor instances with the `{slug}` placeholder, never a concrete anchor's name.
[2026-07-12 20:13:05] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-12 21:17:03] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-12 21:26:26] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-13 21:30:31] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-13 23:45:16] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-13 23:47:25] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-15 13:29:45] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-15 13:30:16] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:01:28] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:27:23] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:27:30] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:27:56] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:27:58] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:28:00] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-16 10:37:06] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
