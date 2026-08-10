---
description: Messages facet — the agent's per-anchor, append-only log of background-process messages. Distinct from `{slug} Inbox.md` which is the user's drop-zone for raw input.
---

| -[[DAS Messages]]- | → [[DAS]] → [[FCT]] → [DAS Messages](hook://p/DAS%20Messages)  |
| --- | --- |
| Related | [[templates/messages.md\|messages template]],  [[DAS Inbox]],  [[DAS Backlog]],  [[DAS Track]],  [[DAS Anchor Tree]],   |
| Examples | [[HBR Messages\|minimal]],  [[HBR Messages\|with real system messages]],   |
| Rules | [[R-messages]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Messages
Spec for the **Messages facet** — the per-anchor file `{slug} Messages.md` that holds background-process notes for the agent, separate from the user's raw-input `{slug} Inbox.md`. It is an **append-only log**; the read-on-every-pause contract this line used to assert was measured in 2026-08 and does not exist — see § Retention.

**Cardinality: one per anchor** — each anchor has exactly one `{slug} Messages.md` file in `{slug} Track/`.

## Retention — the file is append-only, and has never been cleared

**Measured 2026-08-05 (TINK T133), across every anchor:** no `{slug} Messages.md` has ever been cleared. Every one still holds its first entry from 2026-06-02, the day the facet went live — `ATT Messages.md` 828 lines, `HA Messages.md` 1478, with no gaps and no truncation. The "cleared on every pause" phrasing that appears in this facet's history, in several dispatch tables, and in the frontmatter of ~40 instances describes a mechanism that **was never built**: no code in the standard, the rules, or the writers implements or invokes it.

So the honest description of what exists is an **append-only event log**. Almost all of its content is one line per backlog write — `[INFO] backlog at <path> was edited` — emitted by `~/bin/backlog_watch`, an fswatch daemon that lives outside this repo and is the only writer of that format.

**The cost is not the growth; it is that the channel is dead.** The file is never read, which is exactly why unbounded growth went unnoticed for two months. A background process with something genuinely urgent to say has nowhere that gets read, and the read-on-pause contract that would make writing here worthwhile has never run. Any repair has to fix the reading before the retention: a cleared log nothing reads is the same dead channel, emptier.

Until that is settled the claim is stated plainly rather than left implied — see [[TINK Backlog#^T133|TINK T133]], which carries the measurement and the open decision.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. It defines the `{slug} Messages.md` facet; it is not itself a messages file.)*

- **Inclusion test** — content belongs here only when it defines how Messages files are structured, written, read, or pruned across anchors; per-anchor message content or single-anchor examples belong elsewhere. Routing for displaced content: project-wide rules → CLAUDE.md; markdown-rendering → [[R-markdown]]; Inbox-facet rules → [[DAS Inbox]].
- **Load-bearing distinction to preserve** — the frontmatter `description` and R-messages-03 both fix the Messages-vs-Inbox split (agent-read background notes vs. user-dropped raw input); any edit that loosens or removes that distinction breaks the facet's reason for existing.
- **Cross-references to keep in sync** — [[DAS Anchor Tree]] dispatch tables, [[DAS Anchor Tree]] tree, and any anchor template that scaffolds a `{slug} Messages.md`.
- **Conventions** — refer to sibling facets by their CAB filename (`~~[[DAS Inbox]]~~`, `[[DAS Backlog]]`); refer to per-anchor instances with the `{slug}` placeholder, never a concrete anchor's name.
