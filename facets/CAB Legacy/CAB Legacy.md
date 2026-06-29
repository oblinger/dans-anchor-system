---
description: "holding area — the dissolved CAB anchor, preserved verbatim pending per-doc placement review"
---

# CAB Legacy — preserved CAB content (placement review pending)

This folder holds the **entire former `CAB/` anchor** (the Common Anchor Blueprint), relocated here verbatim during the SKA phase-3 consolidation (2026-06-27). Nothing was merged or deleted — the tree was moved intact so that:

- every inbound `[[CAB …]]` wiki-link keeps resolving (Obsidian resolves by basename, so relocation does not break links); and
- the foundational convention specs are preserved and traceable until each doc's final placement is decided.

**Why a holding area instead of scattering into the live FCT facets:** every CAB convention doc has an apparent FCT counterpart (e.g. `CAB Naming Conventions` ↔ `[[FCT Naming]]`, `CAB Page Conventions` ↔ `[[FCT Anchor Page]]`). Placing each one therefore requires a **merge-or-supersede decision per doc** — which the user should drive — rather than dropping duplicate spec files next to the live FCT docs (that would violate single-source-of-truth). The CAB Aspects (68 inbound refs) and CAB Base (36 inbound refs) docs are the load-bearing centers of this network.

## CAB → FCT Migration Map (F218 execution worksheet)

The actionable map driving [[SKA Backlog#^F218|F218]] (CAB → FCT content migration). **Action** legend: *supersede* = FCT doc already covers it, fold any unique content in then retire the CAB doc; *reconcile* = both are load-bearing, merge into the authoritative FCT model; *net-new* = no FCT home yet, create one (or route to the owning feature); *tooling* = operational code, relocate to a skill; *keep* = retain as-is. Status column starts blank — fill as F218 executes.

| CAB doc | → FCT target | Action | Status |
|---|---|---|---|
| [[CAB Naming Conventions]] | [[FCT Naming]] | supersede | ✅ 2026-06-29 — hard-exceptions folded → FCT Naming § Exception D + R-naming-06; slug-system content already in [[FCT Anchor Page]] / [[ATL Slugs]] / HA; stub redirects pending F191 link-sweep |
| [[CAB Page Conventions]] | [[FCT Anchor Page]] | supersede | ✅ 2026-06-29 — fully redundant; covered by [[FCT Anchor Page]] + [[FCT Dispatch Table]] (old link-table taxonomy is pre-Gen-3, superseded); nothing unique to fold; stub redirect pending F191 |
| [[CAB Repository Structure]] | [[FCT Code Repository]] | ⚠ re-scoped → **needs placement** | 2026-06-29 — **NOT a clean supersede.** [[FCT Code Repository]] is scoped to the `code:` *association mechanism* and its inclusion test **excludes** repo-internal conventions (justfile shape, test layout). CAB Repository Structure's content (justfile standard-recipe list `SETUP/BUILD/TEST/LINT/CHECK/DOCS/…`, key-files catalog, `site/` gitignore) is a cross-project convention with **no FCT home** → needs a **net-new home** (a `DSC justfile` / repo-conventions discipline?). Content preserved; surfaced as a query. |
| [[CAB Documentation Publishing]] | [[FCT Documentation Site]] | supersede | ✅ 2026-06-29 — fully covered by [[FCT Documentation Site]] (which is richer: canonical stack + two-tier + 3-output pattern); stray code-interface-style snippet routed to language disciplines; stub redirect pending F191 |
| [[CAB Markdown Formatting]] | [[DSC markdown]] | supersede | ✅ 2026-06-29 — core already in [[DSC markdown]]; folded the `＃` (U+FF03) + figure-space (U+2007) mechanics into [[DSC markdown]] § Mechanical rules; file-tree/TOC forms → [[md]] skill; date-format/dated-sections → [[FCT Log]]/[[FCT Naming]]; stub redirect pending F191 |
| [[CAB Aspects]] | **library umbrella — keep WHOLE** (no split); relocation + de-CAB rename → [[SKA Backlog#^F191\|F191]] | keep — **resolved 2026-06-29**, note below ↓ | ✅ 2026-06-29 — confirmed canonical: [[FCT Facet]]/[[FCT Primitives]]/[[TRT]] + every git-aspect trait all *delegate to it* for the matrix + umbrella model; slimmed (dropped F090 migration-history; fixed dead `CAB/CAB Facets/` paths → `facets/FCT`); physical move/rename owned by F191 |
| [[CAB Base]] | [[FCT Anchor Tree]] (tree) + [[TRT]] / [[SKL]] / DSC+FCT (3 routing tables) | supersede | ✅ 2026-06-29 — both halves rehomed: file-tree skeleton → [[FCT Anchor Tree]] (Gen-3, FCT-linked, now self-canonical — repointed its CAB Base sync refs + R-anchor-tree-04 + BRIEF); Traits table → [[TRT]]; Conventions table → DSC+FCT (the F218 supersede rows); Skills table → [[SKL]]. Stub redirect in place; ~36 inbound + F191 sweep |
| [[CAB Dispatch Table Design]] | [[FCT Dispatch Table]] Design companion (keep) | keep — **resolved 2026-06-29** | ✅ 2026-06-29 — NOT a supersede: it's the live design-rationale (standing decisions) that [[FCT Dispatch Table]] links as its `**Design:**` row. Fixed stale internal pointers (`[[DSC Dispatch Table]]` → [[FCT Dispatch Table]] — table was reclassified discipline→facet; `[[CAB Anchor Page]]` → [[FCT Anchor Page]]). Rename CAB→`FCT Dispatch Table Design` + relocate → F191 |
| [[CAB Docs Conventions]] | [[FCT Roadmap]] (format) + [[FCT Anchor Tree]] (docs index) | supersede | ✅ 2026-06-29 — fully covered: Standard-Documents table → [[FCT Anchor Tree]] + [[FCT Design Docs]]/[[FCT Track]] indexes; roadmap milestone/phase/deliverable format + deferral protocol → [[FCT Roadmap]] (richer, named-milestone convention, enforceable `R-roadmap-05`); CAB's numeric grammar is now FCT Roadmap's *legacy* form. Nothing unique; stub redirect; F191 sweep |
| [[CAB Disciplines]] / [[CAB Disciplines Brief]] | the DSC system | reconcile | |
| [[CAB Template]] | `FCT Template` / `DSC template` | net-new → **routed to [[SKA Backlog#^F220\|F220]]** | |
| [[CAB Defined Terms]] | vault glossary / [[Atlas]] | net-new (glossary) | |
| [[CAB Rust Rules]] | `DSC rust` | net-new (language discipline) | |
| [[CAB Research]] | Paper-trait convention | net-new (thin) | |
| [[CAB Integrations]] | opt-in tools cross-ref | net-new (thin) | |
| [[CAB Maintenance]] | audit/lint at-rest checklist | net-new (thin) | |
| [[CAB Conventions]] | — | umbrella index — retire once members placed | |
| CAB.md (root) / [[CAB Base\|CAB.md]] | FCT system entry point | fold conceptual entry | |
| [[CAB Log]] | — | keep (CAB change history + rewire-spec source) | |
| LINT/ (Tool, Log, Design, PRD, Rules, Suppressions) | the `audit` skill / SKA tooling | tooling — `LINT/audit-docs.py` is a dup of `skills/audit/scripts/audit-docs.py`; `LINT PRD.md` is an empty stub (deletable) | |
| compile/ (compile.md + targets) | the `rewire` skill / SKA tooling | tooling | |
| CAB Design/CAB Maintain Design.md | the `maintain` skill | skill design | |

**Companion features** (the rest of the "land everything in the new representation" set): branding retirement → [[SKA Backlog#^F191|F191]]; Decisions-record + skill-scaffold unification → [[SKA Backlog#^F221|F221]]; Template facet/discipline + placement sweep → [[SKA Backlog#^F220|F220]].

## CAB Aspects reconcile — resolved 2026-06-29 (keep-whole library umbrella; do NOT split)

**The fresh-read overturn.** An earlier pass recorded a "3-home split" (facet-half→FCT Facet, matrix→TRT, umbrella→library). Reading the actual delegation links overturned it: [[CAB Aspects]] is **the canonical, deliberately-centralized umbrella** for the Aspect/Trait/Facet model + the composability matrix, and the rest of the subsystem **delegates *to* it**, not the reverse. Three explicit statements prove this:

1. **[[FCT Facet]]** `R-facet-spec-21` + BRIEF — *"does not duplicate … the composability matrix — it links [[CAB Aspects]]."*
2. **[[TRT]]** BRIEF — *"Composability and exclusion rules are authoritative in [[CAB Aspects]]."*
3. **[[FCT Primitives]]** Overview — *"the deeper roots — anchor and aspect — are blueprint-level concepts … so they **live in the library** (see [[CAB Aspects]])."*

Splitting the doc would **hollow out the exact page ~14 files point at** and force ≥6 trait specs ([[PR]]/[[NoGit]]/[[Push]]/[[Commit]]/[[Track]]/[[TRT]]) to repoint their matrix citations *away* from the center — the opposite of consolidation. So the matrix and facet-half **stay put**; the delegating specs already say so.

**Hazard (recorded earlier, still cleared):** no built `/audit aspects` script exists (only `audit-q.py`), so the doc's matrix-enforcement / "six required sections" language is aspirational — editing it breaks no live audit.

**F218 action (done this pass — keep-and-slim, no relocation):**
1. **Kept whole** as the library umbrella (term + `Aspect ├ Trait └ Facet` tree + Constraints/Expected-Usage contract + the 12×12 composability matrix + anti-patterns + Triggers).
2. **Dropped** the `## Migration history` (F090) block — historical, no live home.
3. **Fixed** dead CAB-era paths inside it (`CAB/CAB Facets/<Name>.md` → `facets/FCT <Name>.md`).

**Owned by [[SKA Backlog#^F191|F191]] (not F218):** the physical relocation `facets/CAB Legacy/` → `library/`, the de-CAB **rename**, and the vault-wide `[[CAB Aspects]]` inbound-link sweep (~68 refs) — these are one atomic branding pass, wrong to do piecemeal for a single doc. No open user question remains.


Until the user decides, treat the contents here as **frozen**. The `CAB/CAB Track/` backlog has already been migrated: its one substantive item (legacy anchor-root page migration) became SKA **F217**; the `B-QFix` audit residuals were reconciled into SKA's own `B-QFix` (CAE/CSE-targeted residuals dropped as their targets were relocated).
