---
description: raw incoming content to process
group: file
---

| -[[DAS Inbox]]- | → [[DAS]] → [[FCT]] → [DAS Inbox](hook://p/DAS%20Inbox)  |
| --- | --- |
| Related | [[DAS Discussion]],  [[DAS Backlog]],  [[DAS PRD]],  [[DAS Roadmap]],   |
| Examples | [[FEX Inbox\|example]],   |
| Rules | [[R-fct-inbox]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Inbox
Facet spec for the `{slug} Inbox.md` drop-zone file — the chronological log of raw input pasted in for later processing into the anchor's planning docs.

**TLDR** — A single `{slug} Inbox.md` file (one per anchor) is the paste-first drop zone for raw input; processed entries stay with a `DONE` or `MOVED →` status tag as a permanent log.

**Cardinality:** one per anchor.

The inbox (`{slug} Inbox.md`) is a drop zone for raw input — long descriptions, change requests, design thoughts, reference material — pasted in for processing and integration into the planning and execution docs.

**Working example:** [[FEX Inbox]] — Inbox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# FEX Inbox

| -[[FEX Inbox]]- |  |
| --- | --- |
| --- | |

Items below have been processed and moved to their destination docs.

## 2026-08-23 — Dan's one-line summary for the anchor system description

*from: user · tag: note*

> **Dan, dictated 2026-08-21 02:43, addressed to Lumen and routed here:** *"Everything in local markdown organized into named anchors with standardized facets."* — *"Lumen, that's a summary that I want to put into the anchor system description."*
>
> **Where it belongs is yours to decide, not Lumen's** — the phrase "the anchor system description" has at least three candidate homes: the opening of [[DAS]] § Overview (which today runs four lines before it says what the thing *is*), the H1 subtitle, or the identity-cell / command-store description. Note the identity cell is **desc-synced from the command store**, so a hand edit there does not stick — it needs the sanctioned path.
>
> **Why this arrived two days late.** The memo was one of three MUSE ingest failed on 2026-08-19 → 08-21. Root cause was **iCloud eviction, not audio loss**: the Just Press Record files were 0-byte dataless stubs, so every read failed. Recovered 2026-08-23 by `brctl download` + re-ingest; all three landed. Nothing was lost.

## 2026-02-28 — Retry backoff tuning    `DONE`
User reported exponential backoff too aggressive for short tasks. Captured in [[FEX Decisions]] as D10.

Original input:
> When I schedule a 2-second task and it fails, the retry waits 4s, then 8s, then 16s. For quick tasks this feels excessive. Could we cap the backoff or use linear for tasks under 10s?

## 2026-02-25 — Priority starvation fix    `MOVED → FEX Roadmap#M3`
Discussed promotion logic for starved low-priority tasks. Design notes moved to the 2026-02-25 entry in the project's Discussion stream. Implementation planned for M3.

## 2026-02-20 — Initial feature brainstorm    `DONE`
Raw feature list from kickoff meeting. Items distributed to [[HBR PRD]] and [[HBR Backlog]].

---

# Format Specification

## Location

`{slug} Inbox.md` lives in `{slug} Track/`, alongside the other tracking surfaces.

## Top of doc (canonical, per F060)

Every Inbox file opens with the standard top-of-doc format: YAML frontmatter + `# {slug} Inbox` H1 + dispatch-table placeholder. See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

## Format
- Reverse chronological dated sections (H2)
- Each heading: `## YYYY-MM-DD — Topic    \`STATUS\``
- Status tags: `DONE` (processed in place), `MOVED → {destination}` (content relocated)
- Original input preserved as blockquotes when useful as a record

## Lifecycle
- Content is pasted in, then processed by an agent or the user who integrates it into the appropriate planning docs (PRD, Roadmap, Todo, Backlog)
- Processed entries remain with a status tag as a persistent log of what was communicated
- Rarely revisited after processing

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above.)*

- **Inclusion test** — a rule belongs here only if it constrains how an Inbox file is authored, located, formatted, or processed; cross-facet workflow (how entries promote to PRD/Roadmap/Backlog) and other surfaces' drop-zone semantics live in the destination facet specs, not here.
- **Status-tag vocabulary is tooling-consumed** — `DONE` and `MOVED → {destination}` (R-fct-inbox-03) are the only sanctioned tags; downstream tooling and agent skills key off these exact strings, so adding a tag requires updating the ruleset first.
- **Reference Example is illustrative, not authoritative** — on a format change update the Format Specification first, then sync the example; don't let the example drift into spec, and keep per-anchor variations in the working example ([[FEX Inbox]]), not inlined here.
- **Top-of-doc shape is owned by rewire** — cite `[[skills/rewire/SKILL]]` § Default doc top-of-file; don't re-specify the frontmatter / H1 / dispatch-placeholder here.
