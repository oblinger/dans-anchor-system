---
description: raw incoming content to process
---

# DAS Inbox
Facet spec for the `{slug} Inbox.md` drop-zone file — the chronological log of raw input pasted in for later processing into the anchor's planning docs.

| -[[DAS Inbox]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Inbox](hook://p/DAS%20Inbox) |
| --- | --- |
| Related | [[DAS Discussion]],  [[DAS Backlog]],  [[DAS PRD]],  [[DAS Roadmap]],   |
| Examples | [[FEX Inbox\|example]],   |
| Rules | [[R-fct-inbox]],   |

**TLDR** — A single `{slug} Inbox.md` file (one per anchor) is the paste-first drop zone for raw input; processed entries stay with a `DONE` or `MOVED →` status tag as a permanent log.

**Cardinality:** one per anchor.

The inbox (`{slug} Inbox.md`) is a drop zone for raw input — long descriptions, change requests, design thoughts, reference material — pasted in for processing and integration into the planning and execution docs.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Inbox.md` — Inbox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Inbox

| -[[FEX Inbox]]- |  |
| --- | --- |
| --- | |

Items below have been processed and moved to their destination docs.

## 2026-02-28 — Retry backoff tuning    `DONE`
User reported exponential backoff too aggressive for short tasks. Captured in [[CAE Open Questions#14]].

Original input:
> When I schedule a 2-second task and it fails, the retry waits 4s, then 8s, then 16s. For quick tasks this feels excessive. Could we cap the backoff or use linear for tasks under 10s?

## 2026-02-25 — Priority starvation fix    `MOVED → CAE Roadmap#M3`
Discussed promotion logic for starved low-priority tasks. Design notes moved to [[CAE Discussion#2026-02-25]]. Implementation planned for M3.

## 2026-02-20 — Initial feature brainstorm    `DONE`
Raw feature list from kickoff meeting. Items distributed to [[HBR PRD]] and [[HBR Backlog]].

---

# Format Specification

## Location

`{slug} Inbox.md` lives at the anchor root, alongside the anchor page.

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
