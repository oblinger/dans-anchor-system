---
description: "completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap"
---

# DAS Completed Roadmap
The migration target for completed milestones — preserves shipped milestone structure in newest-to-oldest order alongside the forward-looking Roadmap.

| -[[DAS Completed Roadmap]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Completed Roadmap](hook://p/DAS%20Completed%20Roadmap) |
| --- | --- |
| Related | [[templates/completed-roadmap.md\|completed-roadmap template]],  [[DAS Roadmap]],  [[DAS Design Folder]],  [[DAS Features]],  [[DAS Design Docs]],   |
| Examples | [[FEX Completed Roadmap\|example]],   |
| Rules | [[R-completed-roadmap]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — One doc per anchor (when any milestone has migrated). Lives at `{slug} Design/{slug} Completed Roadmap.md`. Newest migrated milestone at top; standalone-completed-features groupings interleave between milestones. Cardinality: **one per anchor**.

The Completed Roadmap is the **migration target** for whole milestones that reach completion. Roadmap stays forward-looking; this doc captures everything that's shipped — preserving the milestone structure that the project used to plan it.

**Name choice — provenance:** discussed in [[F144 — Completed Roadmap + named milestones]]. *History* was rejected because it implies temporal precision (which we don't claim). *Completed Roadmap* describes what the doc actually contains: preserved milestone structure with rough chronology. If precise temporal order is ever wanted, a separate `History` doc can hold it; the Completed Roadmap is not that.

## Location

`{slug} Design/{slug} Completed Roadmap.md` — sibling of `{slug} Roadmap.md`.

## Structure — newest at top

The Completed Roadmap reads top-to-bottom as **newest to oldest by migration date**. Two kinds of section alternate:

1. **Standalone-completed-features groupings** — `## Completed standalone features (since <last-migration>)`. These accumulate as features reach Done that aren't part of any milestone (the common case for backlog-pulled features). The grouping at the top of the doc is the *current* one; new completions append here. When the next milestone migrates in, this grouping is "sealed" (no more entries added) and a fresh one starts at the top.

2. **Migrated milestone sections** — `## [x] M-<Name> — <Milestone Title> (migrated <YYYY-MM-DD>)`. Inserted below the most recent standalone-features grouping at migration time. The milestone keeps its full structure: sub-items, Status line, reference block.

### Section order, top to bottom

The two section kinds alternate down the page, newest first:

- **H1** — `# {slug} Completed Roadmap`.
- **Current standalone grouping** — `## Completed standalone features (since <date>)` at the very top, each line `- [x] [[F<NNN> — <Title>]] — (Done <date>)`.
- **Most-recent migrated milestone** — `## [x] M-<Name> — <Title> (migrated <date>)`, followed by its preserved `**Status:**` line, reference block (`**Tests:**`, …), and its `- [x] [[F<NNN> — M-<Name>.<n>: …]]` sub-item bullets (with any `[~]` deferred sub-items retained).
- **Interleaved standalone groupings** — `## Completed standalone features (between M-<X> and M-<Y>)` capturing features that completed in that window.
- **Older migrated milestones** — same shape as above, continuing down in reverse-chronological order.

**Why this structure (provenance — discussed in [[F144]]):**

Top-to-bottom = newer-to-older gives rough chronology without claiming temporal precision. Standalone-features groupings between milestones capture "things that got done between milestone shipments" without forcing them into a fake milestone. Partial milestone work that got done before the milestone was abandoned can land in the standalone grouping at migration time (no forced grouping).

## What migrates and when

**Migration unit is the whole milestone.** Trigger: every sub-item is `[x]`, parent milestone heading is `[x]`. Migration moves:

- The milestone H2 heading (with its `[x]` checkbox)
- The Status line + reference block
- All sub-items (in current state — `[x]` for done, `[~]` for deferred, etc.)
- Any per-sub-item Reference block content

Migration is **append at top below current standalone grouping, then seal the standalone grouping**. The standalone grouping reads "since X" — where X is the previous milestone migration. After the new milestone gets inserted, a fresh empty standalone grouping is created at the very top with the new "since" date.

**Migration is currently manual.** F145 will ship `state roadmap migrate M-<Name>` to automate this.

## When a milestone is abandoned, not completed

If a milestone is being dropped (not all sub-items will land), the user has a choice:

- **Drop entirely** — delete the milestone from the roadmap; do not migrate to Completed Roadmap. Lost.
- **Salvage completed sub-items** — at migration time, transfer the `[x]` sub-items from the abandoned milestone into the current standalone-completed-features grouping. The milestone heading itself is dropped. The completed work survives as standalone features.

This handles the "we did some of M-Auth's sub-items before realizing we wanted to scope it down" case.

## Trait applicability

Any anchor that uses CAB Roadmap. Activated as soon as the first milestone migrates.

## Preface zone

Per [[DAS progressive-disclosure]]:

- **Dispatch table** — Required.
- **TLDR** — Optional. May summarize: "N milestones migrated, latest M-X on YYYY-MM-DD."
- **Figure** — N/A.

## See also

- [[DAS Roadmap]] — parent facet; the forward-looking roadmap is the migration source
- [[DAS Features]] — feature docs; the M-position is encoded in their titles per R-roadmap-10
- [[DAS Design Folder]] — Completed Roadmap is an OPTIONAL child of {slug} Design/; activated when the first milestone migrates
- [[F144 — Completed Roadmap + named milestones]] — the feature that landed this convention
- F145 (future) — `state roadmap migrate` script automation

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + embedded `R-completed-roadmap` RULESET above; design rationale is [[F144 — Completed Roadmap + named milestones]].)*

- **TODO: link a worked example** — no real `{slug} Completed Roadmap.md` instance exists yet (the facet landed with F144; no milestone has migrated). When the first ships, add it to `## See also` and reference it from § Structure in place of the prose outline.
- **Keep spec ↔ embedded RULESET aligned** — when the spec body changes a structural rule (location, order, preservation, naming), mirror it in the matching `R-completed-roadmap` rule and bump the check pattern; never put per-anchor migrated-milestone content here (it lives in `{anchor}/{slug} Design/{slug} Completed Roadmap.md`).
- **Inclusion test for a new rule** — it constrains the *structure* of the completed-roadmap doc (location, order, preservation, naming), not the forward-looking Roadmap ([[DAS Roadmap]]) or feature-doc shape ([[DAS Features]]).
- **Cross-reference integrity is load-bearing** — the `## See also` links to [[DAS Roadmap]], [[DAS Features]], [[DAS Design Folder]], and F144/F145 wire this facet into the CAB graph; don't drop them when refactoring.
