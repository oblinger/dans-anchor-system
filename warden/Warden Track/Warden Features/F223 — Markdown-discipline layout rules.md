---
description: "F223 — Markdown-discipline / progressive-disclosure layout rules — the conditional, multi-check document-layout rules that fire live on write (roadmap item 8, the deliberate stress test)"
---

# [[Warden]] · F223 — Markdown-discipline layout rules

## Summary

Roadmap item 8 ([[Warden Roadmap]] § Live push) — the deliberate **stress test** the user chose: the document-layout rule family (markdown discipline, progressive disclosure, document organization) where a rule is *conditional and multi-check* — one rule that first determines what it is looking at, then makes several assertions. The genuine test of whether a declarative rule engine can *shape* how documents are laid out, not just lint isolated lines. Ships as `RULESET R-progressive` (embedded in [[DAS progressive-disclosure]] per the F133 convention, catalog stub at `library/Rulesets/R-progressive/`), wired into the [[R-doc]] umbrella so it fires live on every markdown write via the audit-on-write path ([[F222 — Doc-fire on write|F222]] + the F177 global hook).

User directive 2026-07-05: *"BUILD it, and we will see how it does. I will check it in usage."*

## Success Criteria

**Tier:** 3 (live-environment behavior — user-observable; the user checks it in usage)
**Blocks next:** [[Warden Roadmap]] item 9 (Rust phase 2)

**What done looks like.** Two layout rules fire on every markdown write and steer real, fixable findings with **zero false positives** across the whole doc corpus:

- **R-spine-01** — a doc never carries BOTH its own dispatch-masthead and a `:>>` breadcrumb (the two navigation forms are alternatives; per [[feedback_breadcrumb_vs_dispatch_table]]).
- **R-progressive-02** — progressive-disclosure section spacing: every `## H2` is preceded by a blank line, and no trailing blank at EOF.

**How it will be verified.** Repo-wide validation (784 docs) shows only genuine violations and no false positives; `fire_audit` fires the rules verdict-identically through both the audit-plan and warden engines (the golden corpus is re-blessed with the new pass verdicts); and the rules fire live on a real markdown write through the dispatcher.

## Design

- **Conditional + multi-check, but reliability-first.** The rules were designed to the user's brief (dispatch-table-by-context + blank-line placement) and then **pruned hard against false positives**, because they fire globally on every write (via the F177 audit-on-write hook) — a noisy rule is worse than no rule. Two whole directions were dropped once repo-wide validation exposed them as unreliable:
  - **"anchor page must HAVE a masthead"** — dropped. A per-file checker cannot classify anchor-page-ness across the vault (most anchor folders carry no `.anchor` file), so requiring a masthead false-positived on 136 real anchor pages. That direction is `R-anchor-page`'s kind-aware job.
  - **"non-anchor must NOT have a masthead"** — narrowed to the reliable core. Detecting *any* `-[[…]]-` row flagged facet/discipline docs that *illustrate* mastheads. The reliable signal is a **self-masthead** — a first cell `-[[<this doc's name>]]-` — plus fenced-example stripping; only then is a masthead unambiguously the doc's own.
  - **"no doubled blank line"** — dropped (widely tolerated: 70+ docs). **"no blank after H1"** — dropped (anchor-page-only, `R-anchor-page-07`'s job).
- **The checkers** (`skills/audit/scripts/audit-plan.py`): `chk_dispatch_table_by_context` (self-masthead ∧ `:>>` → fail) and `chk_progressive_disclosure_layout` (blank-before-H2 + no-trailing-blank, fence-aware). Reused by both the audit-plan engine and the warden reference engine through the shared checker registry — no parallel code.
- **Live surface.** In `R-doc` (`always`), so it rides both audit-on-write paths already live. No recompile — the doc-fire path reads audit-plan directly.

## Status

**Built + LIVE 2026-07-05.** `R-progressive` (2 rules) is authored, wired into `R-doc`, and firing. **Repo-wide validation: 13 genuine findings across 784 docs, 0 false positives** (3 both-navigation docs — `FEX Architecture`, `CAE User Docs`, `CAE Dev Docs`; 10 spacing — 5 glued-H2, 5 trailing-blank). Fires verdict-identically through `fire_audit` on both engines; the golden corpus is re-blessed (doc cases gained R-progressive pass verdicts, both engines agree). The F177 audit-on-write hook surfaced R-spine-01 live on the very first edit that added it to `R-doc` — which is exactly how the one design bug (treating a ruleset-stub anchor page as needing a masthead) was caught and removed before it could be noisy. The one Warden-anchor finding (`Warden Survey.md`'s glued `## Overview`) is fixed as the demonstration; the other 12 are left for the live system to surface in usage.

## Open questions

1. **Widen the assertions once trusted.** The conditional "present-direction" (which anchor pages must carry a masthead) is deliberately deferred to `R-anchor-page`. If a reliable anchor-page classifier emerges (e.g., from the compiler's anchor index), R-spine-01 could regain the full both-ways conditional. Revisit after the rules have soaked in usage.
