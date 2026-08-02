---
description: "design-pipeline docs for the Audit skill"
---

# DAS Audit Design

| -[[DAS Audit Design\|Audit Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [design](hook://design) → [[Audit]] → [DAS Audit Design](hook://p/DAS%20Audit%20Design)<br>: design-pipeline docs for the Audit skill |
| --- | --- |
| [[DAS Audit PRD\|PRD]]  | product requirements — what /audit produces and for whom |
| [[DAS Audit Stories\|Stories]]  | user stories elaborating the PRD |
| [[DAS Audit UX Design\|UX Design]]  | invocation surface + output format |
| [[DAS Audit API Design\|API Design]]  | engine API — audit-plan.py interfaces |
| [[DAS Audit Architecture\|Architecture]]  | system-architecture story — modules, data flow |
| [[DAS Audit System Design\|System Design]]  | how the audit engine is built |
| [[DAS Audit Files Architecture\|Files Architecture]]  | file-tree map of the audit skill |
| [[DAS Audit Decisions\|Decisions]]  | durable rulings; cites rulesets |
| [[DAS Audit Testing\|Testing]]  | test strategy + cases |
| [[DAS Audit Rules Redesign\|Rules Redesign]]  | Warden-native audit-rules pipeline — entry doc for the reserved /plan cycle (F132) |
| [[DAS Audit Roadmap\|Roadmap]]  | milestones |
| [[Audit Features\|Features]]  | feature design records (kept at `skills/audit/`, not under `design/` — T041 Q3) — the per-feature docs defining V2 audit |
| [[DAS Audit Completed Roadmap\|Completed Roadmap]]  | shipped milestones |
| ... |  |

Design is the umbrella for system-spec content for the **Audit** skill — PRD, UX Design, Architecture, and the rest of the design pipeline. Member order follows the canonical Design-row order ([[R-anchor-page]]-13): PRD → (Stories) → UX Design → (CLI) → API → Architecture → (System / Files) → Decisions → Testing → Roadmap. As a SKA sub-project the Audit skill owns this design but no tracking or status ([[DAS Track]] § Who owns a Track folder); see [[DAS Design Docs]] for the canonical Design-dispatch shape.
