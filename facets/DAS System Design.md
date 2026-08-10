---
description: "the current technical-architecture document for a software project anchor"
---

| -[[DAS System Design]]- | → [[DAS]] → [[FCT]] → [DAS System Design](hook://p/DAS%20System%20Design)  |
| --- | --- |
| Related | [[DAS PRD]],  [[DAS Decisions]],  [[DAS Discussion]],  [[DAS UX Design]],   |
| Examples | [[FEX System Design\|the declared four-section shape]],   |
| Rules | [[R-fct-system-design]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS System Design
Facet spec for `{slug} System Design.md` — the current technical-architecture document (components, data model, decisions) for a software project anchor.

**TLDR** One per anchor. `{slug} System Design.md` lives in `{slug} Design/` and records the *current* detailed technical design — modules, flows, protocols, configuration. Sections are named after the system it describes; there is no fixed spine. Rulings go in [[DAS Decisions]], the high-level view in [[DAS Architecture]], rationale in [[DAS Discussion]].

**Cardinality: one per anchor** — a software project anchor has exactly one System Design document at any given time.

The System Design document (`{slug} System Design.md`) is the **detailed technical spec** for a software project — module structure, data flows, protocols, configuration. It sits below [[DAS Architecture]], which carries the high-level decomposition, and it records the current design rather than the history of how it was reached.

**Working example:** [[FEX System Design]] — in-repo, and see the note there on what it does and does not demonstrate.

Worked instances are linked in the masthead `Examples` row rather than pasted here (per [[R-facet-spec]]-20): a spec defines the kind, and an embedded instance rots when the example moves. The instances that taught this facet its current shape are [[HA System Design]] and [[SKA System Design]].

# Format Specification

## Location

`{slug} System Design.md` lives in `{slug} Design/`.

## Top of doc (canonical, per F060)

Every System Design opens with the standard top-of-doc format: YAML frontmatter + `# {slug} System Design` H1 + dispatch-table placeholder. The **TOC**, **Components**, **Data Model**, and **Decisions** tables are all topic tables (the doc's payload) — they stay as distinct tables BELOW the dispatch table per F060 § Q5.

## Document Structure

**There is no required section list.** A System Design names its sections after the *system it describes* — the vault's instances carry `Protocol Module`, `Frame-interval computation`, `Day boundary — the 05:00 rule`, `Numpad Controls`, `Storage Architecture`, `Operating Modes`. Across 14 instances running 41 to 1,790 lines, no two share a spine, and the facet does not impose one on domains it has never seen.

Three things are constant:

### Orientation first
The first body H2 orients the reader before the detail starts. The name is free — `## Overview`, `## Architecture Overview`, `## Problem Statement`, `## What the anchor system is` are all live — but the position and the job are not. Nine of the twelve substantive instances already do this; it is the one section the corpus genuinely agrees on.

### Decisions live in `{slug} Decisions.md`
Durable rulings and their rationale go in the anchor's own [[DAS Decisions]] file, never in a `## Decisions` section here (`R-fct-system-design-05`). Ruled by Dan 2026-08-05: specialized content like decisions gets its own file. A decision inlined in a design doc is invisible to anything reading the decision log, and it makes this document a second place a reader has to check.

### The high-level view belongs to `{slug} Architecture`
[[DAS Architecture]] carries the subsystem decomposition, the figure, and the principles. System Design carries the detail underneath: how the modules are structured, how data moves, what the protocols and configuration are. When both exist, System Design **links** Architecture rather than restating it.

## Lifecycle

- **Create** after the PRD and Open Questions have stabilized enough to design against
- **Update** when architecture changes — this is the current spec, not a historical log
- **Rulings** land in [[DAS Decisions]] as they are made, not in a section here
- **Current spec only** — rationale and alternatives belong in Discussion

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative shape is the body + [[R-fct-system-design]]; worked instances are linked in the masthead `Examples` row.)*

- **Spec, not an instance** — don't pile real architecture, decisions, or component tables here; those live in per-anchor `{slug} System Design.md` files. Inclusion test: content belongs here only if it specifies *how System Design docs are shaped vault-wide* — section names, ordering, table formats, lifecycle, top-of-doc conventions. Anchor-local rules go in `{slug} Rules.md` / `{slug} Decisions.md`; rationale-and-alternatives narrative goes in [[DAS Discussion]] (cite, don't inline).
- **What is enforced, and what is deliberately not** — [[R-fct-system-design]] checks the `{slug} Design/` location (R-01) and the absence of a `## Decisions` section (R-05); everything about section *naming* is `stated`, because the corpus does not support a fixed spine. **Don't re-add a required-H2 rule.** The set carried one from authoring until 2026-08-05 and it matched **zero of 14 instances** — it survived only because a dead `where::` glob meant it never fired. If a future spine is wanted, measure it against the corpus before writing it down.
- **Re-derived 2026-08-05** ([[TINK Backlog#^Q004|Q004]]) from [[HA System Design]] and [[SKA System Design]] plus twelve others, on Dan's ruling that the Architecture doc stays high-level and specialized content like decisions gets its own file. The `{slug} Decisions.md` boundary (R-05) and the [[DAS Architecture]] boundary (R-06) both come from that ruling, not from the corpus.
- **Sibling boundaries:** PRD → [[DAS PRD]]; cross-cutting decisions and rationale → [[DAS Decisions]] / [[DAS Discussion]]; user-facing UX → [[DAS UX Design]]. Link sideways, don't restate.
- **The exemplar demonstrates the spec; it does not ratify it** — when the inline reference example and [[FEX System Design]] drift, update both in the same edit. But note that [[FEX System Design]] is *constructed*, not quoted: no System Design doc in the vault matches the four declared H2s (the two mature instances carry `Components / Data Flow / Configuration / Key Design Constraints` and fifteen free-form H2s). The structure below is therefore unvalidated against practice — see [[TINK Backlog#^T116|T116]] before treating it as settled.
