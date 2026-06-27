---
description: "holding area — the dissolved CAB anchor, preserved verbatim pending per-doc placement review"
---

# CAB Legacy — preserved CAB content (placement review pending)

This folder holds the **entire former `CAB/` anchor** (the Common Anchor Blueprint), relocated here verbatim during the SKA phase-3 consolidation (2026-06-27). Nothing was merged or deleted — the tree was moved intact so that:

- every inbound `[[CAB …]]` wiki-link keeps resolving (Obsidian resolves by basename, so relocation does not break links); and
- the foundational convention specs are preserved and traceable until each doc's final placement is decided.

**Why a holding area instead of scattering into the live FCT facets:** every CAB convention doc has an apparent FCT counterpart (e.g. `CAB Naming Conventions` ↔ `[[FCT Naming]]`, `CAB Page Conventions` ↔ `[[FCT Anchor Page]]`). Placing each one therefore requires a **merge-or-supersede decision per doc** — which the user should drive — rather than dropping duplicate spec files next to the live FCT docs (that would violate single-source-of-truth). The CAB Aspects (68 inbound refs) and CAB Base (36 inbound refs) docs are the load-bearing centers of this network.

## Proposed placement (for user review — NOT yet executed)

| Doc | Proposed disposition |
|---|---|
| [[CAB Naming Conventions]] | merge into / supersede by [[FCT Naming]] |
| [[CAB Page Conventions]] | merge into / supersede by [[FCT Anchor Page]] |
| [[CAB Repository Structure]] | merge into / supersede by [[FCT Code Repository]] |
| [[CAB Documentation Publishing]] | merge into / supersede by [[FCT Documentation Site]] |
| [[CAB Aspects]] | reconcile with [[FCT Facet]] + [[FCT Primitives]] (authoritative Aspect/Trait/Facet model) |
| [[CAB Base]] | reconcile file-tree skeleton with [[FCT Anchor]] |
| [[CAB Markdown Formatting]] | merge into / supersede by `[[DSC markdown]]` discipline |
| [[CAB Dispatch Table Design]] | pair with [[FCT Dispatch Table]] (design rationale) |
| [[CAB Docs Conventions]] | reconcile with [[FCT Design Docs]] / [[FCT Track]] (roadmap + deferral format) |
| [[CAB Template]] | net-new — promote to an FCT Template facet (or [[FCT Primitives]]) |
| [[CAB Defined Terms]] | net-new glossary — promote or fold into a vault glossary |
| [[CAB Rust Rules]] | net-new — language-specific discipline (e.g. DSC rust) |
| [[CAB Research]] | net-new — Paper-trait convention |
| [[CAB Integrations]] | net-new thin — opt-in tools cross-ref |
| [[CAB Maintenance]] | net-new thin — at-rest validation checklist (audit/lint) |
| [[CAB Conventions]] | umbrella index — retire once members are placed |
| [[CAB Disciplines]] / [[CAB Disciplines Brief]] | reconcile with the disciplines (DSC) system |
| [[CAB Log]] | net-new — CAB change history + rewire-spec source; keep |
| [[CAB Base\|CAB.md]] / CAB.md (anchor root) | conceptual entry point — fold into FCT system |
| LINT/ (LINT Tool, LINT Log, LINT Design, LINT PRD, LINT Rules, LINT System Suppressions) | operational tooling → SKA / the `audit` skill. **Note:** `LINT/audit-docs.py` is a known **duplicate** of `skills/audit/scripts/audit-docs.py` (single-source-of-truth cleanup); `LINT PRD.md` is an empty stub (deletable). |
| compile/ (compile.md + targets) | operational tooling → SKA / rewire skill |
| CAB Design/CAB Maintain Design.md | skill design → the `maintain` skill |

Until the user decides, treat the contents here as **frozen**. The `CAB/CAB Track/` backlog has already been migrated: its one substantive item (legacy anchor-root page migration) became SKA **F217**; the `B-QFix` audit residuals were reconciled into SKA's own `B-QFix` (CAE/CSE-targeted residuals dropped as their targets were relocated).
