---
description: Messages facet — the agent's per-anchor inbox of background-process messages that the agent reads on every pause. Distinct from `{slug} Inbox.md` which is the user's drop-zone for raw input.
---

# Messages Facet
Spec for the **Messages facet** — the per-anchor file `{slug} Messages.md` that holds background-process notes for the agent to read on every pause, separate from the user's raw-input `{slug} Inbox.md`.

| -[[DAS Messages]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Messages](hook://p/DAS%20Messages) |
| --- | --- |
| Related | [[templates/messages.md\|messages template]],  [[DAS Inbox]],  [[FCT Backlog]],  [[DAS Track]],  [[DAS Anchor Tree]],   |
| Examples | [[HBR Messages\|minimal]],  [[HBR Messages\|with real system messages]],   |
| Rules | [[R-messages]],   |

**Cardinality: one per anchor** — each anchor has exactly one `{slug} Messages.md` file at its root.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. It defines the `{slug} Messages.md` facet; it is not itself a messages file.)*

- **Inclusion test** — content belongs here only when it defines how Messages files are structured, written, read, or pruned across anchors; per-anchor message content or single-anchor examples belong elsewhere. Routing for displaced content: project-wide rules → CLAUDE.md; markdown-rendering → [[R-markdown]]; Inbox-facet rules → `CAB Inbox.md`.
- **Load-bearing distinction to preserve** — the frontmatter `description` and R-messages-03 both fix the Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input); any edit that loosens or removes that distinction breaks the facet's reason for existing.
- **Cross-references to keep in sync** — [[DAS Anchor Tree]] dispatch tables, [[DAS Anchor Tree]] tree, and any anchor template that scaffolds a `{slug} Messages.md`.
- **Conventions** — refer to sibling facets by their CAB filename (`~~[[FCT Inbox]]~~`, `[[DAS Backlog]]`); refer to per-anchor instances with the `{slug}` placeholder, never a concrete anchor's name.
[2026-07-12 20:13:05] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-12 21:17:03] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
[2026-07-12 21:26:26] [INFO] backlog at SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md was edited
