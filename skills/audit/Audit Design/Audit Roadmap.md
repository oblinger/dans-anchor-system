---
description: "V2 audit milestones — flesh out the rule-processing engine first (fix-by-default, levels, distill/on-write), refactor the legacy sub-audits onto it later."
---

# Audit Roadmap

The arc: get the unified rule-processing engine fully built — fix-by-default, the four automation levels, distilled online correction — then migrate the existing hand-written sub-audits onto it. Earlier milestones flesh out the engine; the later one refactors the legacy surfaces.

## Shipped

- **M1 — Rule-driven engine.** Resolve → run (mechanical, verdict-cached) → judge (agent); `where::` selector; both `/audit anchor` and `/audit doc` surfaces. [[F001 — Rule-driven audit engine — resolve, run, judge|F001]].
- **M2 — On-write slice, vault-wide.** `PostToolUse` hook auto-fixes mechanical defects + flags subjective ones on every `.md` write under the vault, with the no-delete safety guard. [[F004 — Audit-on-write hook — closed-off E2E slice|F004]], [[F005 — Doc audit-on-write — vault-wide rollout + safety guard|F005]]; markdown rule library [[F008 — audit markdown — markdown hygiene rule library|F008]].

## Earlier — finish the engine

- **M3 — Fix-by-default + the four levels.** Generalize the `fix::` companion across rulesets; wire the automation level as a fix-stage parameter (Informational / Online / Standard / Aggressive); `/audit` fixes at Standard by default, `dry` reports. [[F002 — Audit fix-by-default + Python rule functions|F002]].
- **M4 — Distill generalization.** Extend the distilled on-write module beyond the markdown slice to the full doc/anchor rule corpus; `where::`-relevance-gated judgment-title reminders, throttled once per file per session. [[F003 — On-write rule hook + test workflow|F003]], with rule-attention discipline [[F006 — Rule triggering — when the agent attends to rules|F006]].
- **M5 — Deletion mark + sweep.** The `> [!info] Recommend deleting` callout as the universal annotate-don't-delete path, plus the separate `/audit sweep` operation that removes only marked content.
- **M6 — `where::` hardening.** Backtick-wrap every `where::` expression with a coordinated parser swap, gated by a green rule-set test suite before and after. [[F007 — Backtick all where:: expressions — parser swap|F007]].
- **M7 — Test workflow.** The cross-use on-write checklist runnable as one workflow that asserts each case and tallies pass/fail ([[F003 — On-write rule hook + test workflow|F003]] § Testing strategy).

## Later — migrate the legacy sub-audits

- **M8 — Refactor sub-audits onto the engine.** The hand-written sub-audits (`structure`, `docs`, `dispatch`, `q` + family, `architecture`, `code`, `publish`, `integrity`) are preserved today and re-expressed as rulesets the unified engine resolves and runs — retiring the bespoke scripts as each is covered. Includes folding the `q`-family checks ([[F009 — audit q — Q.md constraint validator|F009]], [[F010 — audit-q bracket-H2 consistency rules|F010]], [[F011 — audit-q — Designing requires justification|F011]], [[F012 — audit-q recognize H3-form Open Questions|F012]], [[F013 — audit-q ask.md ↔ feature-doc drift check|F013]], [[F014 — audit-q ask.md coverage + backtick-filepath link|F014]]) and `architecture` ([[F015 — Audit architecture|F015]]) into rules, and completing the `/lint` → `/audit` retirement ([[F016 — Migrate lint to audit|F016]]).
- **M9 — Per-anchor level pinning.** Each anchor declares its explicit-pass level (careful subsystems fix conservatively, scratch ones freely); the engine masks the fixer set to the declared level. The online hooks stay pinned to Online regardless.
