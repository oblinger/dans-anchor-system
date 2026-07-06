---
description: "F218 deliverable — the mined design-rules catalog. UPGRADED 2026-07-05 (Q3 = A): all nine families live under library/Rulesets/ as R-arch / R-process children; this doc keeps the mining record, the parked-borderline list, and the executed housekeeping."
---

# [[Warden]] · Design-Rules Catalog Proposal

The [[F218 — Design-rules catalog — ship with skills, adopt per-application|F218]] mining pass, presented as one reviewable package (per Q2: agent proposes, user reviews and upgrades — nothing is auto-created or auto-adopted). Six corpora were mined in parallel: **HA** (`prj/Hook Anchor/`), **SVP** (`SV/ww/svar-docs/sv-pipe/SVP Docs/`), **MUX** (`prj/ClaudiMux/MuxUX/`), **A2X** (`SV/ww/svar-docs/alg2-experimental/A2X/`), **SKD** (`prj/ClaudiMux/Skill Docket App/`), **SVAR** (`SV/ww/svar-docs/SVAR Design/`). A family enters this proposal only when it recurs across **≥3 projects** (or was named in the F108 commissioning message). Each block below is a draft ruleset in the exact live format — headed `PROPOSED RULESET`, which the warden scan's `# RULESET` sentinel does not match, so none of this compiles into the corpus until upgraded.

**Upgrade mechanics.** To adopt a family, say so (e.g. "upgrade R-single-source-of-truth" or "upgrade all"). The agent then: (1) strips `PROPOSED ` from the heading and moves the block to its proposed home under `library/Rulesets/`, (2) adds the catalog stub row in [[Rulesets]] and the `include::` in its umbrella ([[R-arch]] / [[R-process]] already name several of these as awaited children), (3) recompiles the warden corpus. **Adoption stays per-application**: an upgraded ruleset fires for an app only when that app's `.anchor` takes the trait — upgrade puts the rule on the shelf; each app still opts in.

**What the mining did NOT re-propose.** The live [[R-ob]] umbrella already covers three families this scan re-confirmed everywhere: state/config through the data singleton + no hardcoded config values ([[R-ob-state-mgt]], seen in HA "Oblinger's Rules" + MUX audits), no silent fallbacks + OS-bridge logging ([[R-ob-observability]], seen as HA P05/P08 + MUX no-silent-fallbacks), and the dispatcher pattern ([[R-ob-cmd-proc]], seen as MUX single-dispatcher + HA command-queue + SKD event routing). Those are catalog successes — already shipped; the recurrence evidence simply validates them.

## Upgraded 2026-07-05 — all nine families are live (Q3 = A)

Per the F218 Q3 review (user, 2026-07-05: upgrade all nine), every proposed block moved out of this doc into the live catalog — `PROPOSED ` stripped, promoted to standalone rulesets with their recurrence evidence, wired as `include::` children of their umbrellas, and compiled into the warden corpus:

- **[[R-arch]]** (15 rules): [[R-single-source-of-truth]] (3), [[R-one-path]] (3), [[R-interfaces-folder]] (3), [[R-factory-pegboard]] (3), [[R-ownership]] (3) — `library/Rulesets/R-arch/`
- **[[R-process]]** (14 rules): [[R-design-gate]] (4), [[R-stable-ids]] (4), [[R-exception-discipline]] (3), [[R-wrapper-cli]] (3) — `library/Rulesets/R-process/`

Adoption stays per-application: an upgraded ruleset fires for an app only when its `.anchor` takes the trait (or the `arch` / `process` umbrella trait).

## Borderline candidates — parked pending more recurrence

Real signals that stopped short of the ≥3-project bar or extend an existing set rather than founding a new one; future mining passes should re-test them:

- **Timing governors in config, each naming its failure mode** (HA P10) — a sharp, portable extension of [[R-ob-state-mgt]]-03; candidate `R-ob-state-mgt-04` when a second project exhibits it.
- **Write-if-changed gating on all production file writes** (HA P07/R01) — motivated by watcher cascades; portable wherever file-watchers exist.
- **Idempotent convergence, forward-only** (MUX "diffs against reality and takes the minimum actions"; SKD "No rollback — the system keeps converging forward") — two strong statements; one more instance makes it a family.
- **Test-energy budgeting: property-based + differential over hand-written examples where inputs are combinatorial** (SVP F004; A2X behavior-not-implementation) — the natural seed for the [[R-test]] placeholder's `R-property-based`.
- **Bundle self-containment** (MUX no-`~/bin`-at-runtime; global CLAUDE.md packaged-apps rule) — already enforced globally via CLAUDE.md; catalog capture would be for per-app adoption symmetry.
- **Draft-first / never present a blank page** (A2X Master Flow; SKD skeleton-first) — agent-workflow style more than application architecture; may belong beside the skills, not R-arch.

## Housekeeping — executed 2026-07-05

The legacy `~/.claude/skills/rule/rulesets/oblinger-rules.md` (OB-R01/02/03/05, consumed by the old `/rule create`/`/rule sync`) duplicates [[R-ob-state-mgt]]-01/02/03 and [[R-ob-observability]]-01 nearly verbatim — two sources of truth for the user's own portable rules. Recommend: retire the legacy file to a redirect at [[R-ob]] once no `/rule sync` consumer depends on it (HA's `HA Rules.md` § Inherited Rules cites it as its sync source, so HA's sync pointer moves to R-ob in the same pass). This is R-single-source-of-truth-01 applied to the catalog itself.

**Executed in the same pass:** the legacy file is now a redirect at `skills/rule/rulesets/oblinger-rules.md` (its distinct residue — Python check patterns, one Rust fallback shape, the per-project audit convention — absorbed into [[R-ob-observability]]-01 first); HA's `HA Rules.md` § Inherited Rules pointer moved to [[R-ob]]; `skills/rule/sets/README.md` updated.
