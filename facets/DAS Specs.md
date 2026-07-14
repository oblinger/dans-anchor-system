---
description: "specification for the OpenSpec-conformant specs/ folder — per-capability behavioral contracts with RFC-2119 requirements and Given/When/Then scenarios"
---

# DAS Specs
Specification for the **Specs** facet — the OpenSpec-conformant `specs/` folder holding the anchor's durable behavioral contract, one capability per folder.

| -[[DAS Specs]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Specs](hook://p/DAS%20Specs) |
| --- | --- |
| Related | [[DAS Changes]],  [[DAS Architecture]],  [[DAS Testing]],  [[F230 — OpenSpec conversion\|F230]],   |
| Skills | [[skills/finalize/SKILL\|/finalize]] (archive-merge writes here) |
| Rules | [[R-specs]],   |
| Examples | none yet — first adoption pending ([[F230 — OpenSpec conversion\|F230]]) |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Disciplines Brief]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Location:** `specs/` at the anchor root (lowercase, [OpenSpec](https://github.com/Fission-AI/OpenSpec/)-conformant). One folder per **capability**, each holding exactly one file named `spec.md` — nothing else (verified against OpenSpec's own repo; everything richer lives in the anchor's design docs).

**Cardinality:** at most one `specs/` folder per anchor. Adopted deliberately alongside `changes/` (per F230); anchors without OpenSpec adoption keep their behavioral contract in `{slug} Design/` as before.

## What a spec is

`specs/<capability>/spec.md` is the **current behavioral contract** for one capability — what the system does now, not how it got there and not what it might do. History lives in archived [[DAS Changes|changes]]; rationale lives in `{slug} Design/`. Specs are only ever modified by `/finalize`'s archive-merge folding in a change's delta — hand-edits bypass the change discipline and are an audit finding.

## Spec file format

- `# <Capability>` H1, one-paragraph purpose statement.
- `## Requirements` — each requirement a `### Requirement: <name>` H3 using RFC-2119 keywords (**MUST** / **SHOULD** / **MAY**).
- Each requirement carries one or more `#### Scenario: <name>` blocks in Given/When/Then form — the scenario doubles as the acceptance test ([[DAS Testing]] scenario tests derive from these).

## Delta semantics (how changes modify specs)

A change's `specs/<capability>/spec.md` delta marks its requirements `## ADDED` / `## MODIFIED` / `## REMOVED`. On `/finalize`:

- **ADDED** — requirement appended to the capability's spec (capability folder created if new).
- **MODIFIED** — the named requirement's section replaced wholesale.
- **REMOVED** — the named requirement's section deleted.

The merge is per-requirement-section, mechanical, and idempotent; conflicts (a MODIFIED requirement that doesn't exist, an ADDED one that already does) fail loudly rather than merging silently.

# BRIEF

*(Maintainer note — agent-facing cautions.)*

- **Exactly one `spec.md` per capability folder** — resist adding sibling files; they break OpenSpec conformance. Richer material belongs in `{slug} Design/`.
- **Never hand-edit specs/ to "fix" drift** — route the fix through a change (`/change` → `/finalize`), or the change history stops being the audit trail.
- **PRD stays out** — OpenSpec's proposal.md is per-change "why"; the durable PRD remains at `{slug} Design/{slug} PRD.md` (Ours, per the F230 migration map).
