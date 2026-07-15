---
description: "Curated, versioned bundles of rules."
---

# DAS Rulesets
The catalog of rulesets — portable, checkable rule bundles — organized by the nine subsystems in [[DAS]] order (each ruleset lives with the group that owns its constraint; *Meta* is a proposed tenth group for the system's own vocabulary).

| -[[DAS Rulesets]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [rulesets](hook://rulesets) → [DAS Rulesets](hook://p/DAS%20Rulesets)<br>: Curated, versioned bundles of rules. |
| --- | --- |
| Related | [[Rulesets Brief\|Brief]],  [[DAS Ruleset]],  [[DAS Decisions]],   |
|  |  |
|  | **RULESET GROUPS** — organized by the nine subsystems, in [[DAS]] order |
| [[DAS Anchor Design\|Anchor]]+ | [[R-anchor]],  [[R-dot-anchor]],  [[R-anchor-page]],  [[R-anchor-tree]],  [[R-anchor-group]],  [[R-project-page]],  [[R-naming]],  [[R-dispatch-table]],  [[R-dispatch-group]],  [[R-fct-folder]],  [[R-fct-move]],  [[R-fct-claude]],  [[R-fct-interface]],  [[R-topic]],  [[R-simple]],   |
| [[DAS Hygiene Design\|Hygiene]]+ | [[R-ruleset]] (governs the rule files themselves),  [[R-facet-spec]],  [[R-pathguard]] (PreToolUse deny),,,,   |
| [[DAS Tracking Design\|Tracking]]+ | [[R-backlog]],  [[R-query]],  [[R-status]],  [[R-log]],  [[R-messages]],  [[R-roadmap]],  [[R-completed-roadmap]],  [[R-track-group]],  [[R-track-dispatch]],  [[R-fct-icebox]],  [[R-fct-inbox]],  [[R-fct-plan-dispatch]],  [[R-state-region]] (F236 advisory on the state-managed doc regions — Open Questions / Resolved / Status),,,   |
| [[DAS Design Design\|Design]]+ | [[R-design]],  [[R-prd]],  [[R-stories]],  [[R-architecture]],  [[R-files-architecture]],  [[R-ux]],  [[R-api]],  [[R-decisions]],  [[R-discussion]],  [[R-design-gate]],  [[R-fct-system-design]],  [[R-fct-features]],  [[R-design-dispatch]],  [[R-design-docs-group]],  [[R-layering]],  [[R-arch]] (umbrella: [[R-single-source-of-truth]] · [[R-one-path]] · [[R-interfaces-folder]] · [[R-factory-pegboard]] · [[R-ownership]]),  [[R-process]] (umbrella: [[R-design-gate]] · [[R-stable-ids]] · [[R-exception-discipline]] · [[R-wrapper-cli]]),,,,   |
| [[DAS Code Design\|Code]]+ | [[R-code]],  [[R-code-mirror]],  [[R-code-repository]],  [[R-code-surface]],  [[R-git]],  [[R-cli]],  [[R-wrapper-cli]],  [[R-versions]],  [[R-module-doc]],  [[R-all-files]],  [[R-changes]],  [[R-specs]],  [[R-openspec]],  [[R-test]],  [[R-testing]],  [[R-dev-dispatch]],  [[R-mac]],  [[R-ios]],   |
| [[DAS Doc Design\|Doc]]+ | [[R-doc]],  [[R-markdown]] (supersedes legacy [[R-md]]),  [[R-doc-structure]],  [[R-doc-facet]],  [[R-progressive]],  [[R-brief]],  [[R-cards]],  [[R-paper]],  [[R-wp]],  [[R-output-group]],  [[R-fct-outputs]],  [[R-fct-user-dispatch]],  [[R-documentation-site]],  [[R-file-association]],  [[R-dated-entry-stream]],  [[R-diagram]] (umbrella: [[R-diagram-geometry]] · [[R-sugiyama]] · [[R-c4]] · [[R-wcag-contrast]] · [[R-bringhurst-typography]] · [[R-tufte-data-ink]] · [[R-svg-hygiene]]),  [[R-svg-jiggle]],,,,   |
| *Owner (cross-cutting)* | [[R-ob]] (owner-scoped umbrella — applies to every anchor Dan owns, by owner not subsystem: [[R-ob-state-mgt]] · [[R-ob-observability]] · [[R-ob-cmd-proc]] · [[R-ob-remote-ops]]), |
| *Meta (proposed)* | [[R-facet]] (per-facet umbrella),  [[R-trait]] (per-trait umbrella),  [[R-skill]] (per-skill umbrella),  [[R-skill-md]],  [[R-skill-anchor]],  [[R-template]], |
| --- | |
| [[Diagram]] | Diagram authoring + validation rules: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate. |
| [[rulesets/README]] |  |

*(Search, Drive, and Utility own no rulesets — Search constrains via its type rules, Drive via the workflow discipline, Utility via the owner-scoped [[R-ob]] axis.)*

## Status

**Phase 3 scaffolding.** Materialized: [[R-code]] (containing [[R-mac]]); [[R-doc]] (containing [[R-markdown]]); [[R-diagram]] (umbrella over 7 methodology sub-sets, 22 rules total — factored 2026-06-09 per F132 Phase 1); [[R-ob]] (containing 3 sub-sets, 18 rules total); [[R-facet]] now has eleven materialized children: [[R-testing]] (9 rules), [[R-status]] (10 rules), [[R-log]] (9 rules), [[R-stories]] (9 rules), [[R-prd]] (9 rules), [[R-design]] (7 rules), [[R-naming]] (5 rules), [[R-roadmap]] (11 rules), [[R-completed-roadmap]] (6 rules), [[R-ux]] (8 rules), [[R-api]] (9 rules), the last two landed 2026-06-11 as paired peer facets cutting human vs programmatic user surface. **Design pipeline live** — folder presence (`{slug} Design/`) replaces the Code-trait gate; CAB Design facet governs scaffolding + required-children invariants; F140 sweeps the Code trait out of vault anchors. CAB-aligned umbrellas [[R-trait]] / [[R-skill]] remain structural placeholders awaiting rule population as `rulesets/R-*.md` files. Trait-scoped children ([[R-paper]] / [[R-simple]] / [[R-skill-anchor]] / [[R-topic]]) are placeholders pending migration into `traits/<Trait>.md` specs. **2026-07-14 (T021):** catalog reorganized to the nine subsystem groups (was CAB-umbrella / cross-cutting / owner-scoped axes); each group's profile now carries its Rulesets row.

## Research

- [[2026-06-08 diagram-auditing-methodologies]] — survey of 20 sources on diagram-validation methodologies (PCB DRC, Sugiyama / Purchase graph-drawing aesthetics, C4 / Sourcetrail checklists, Bertin / Tufte / Munzner, WCAG contrast). Seed material for the [[R-diagram]] set's 22-rule checklist.
