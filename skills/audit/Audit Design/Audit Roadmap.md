# Audit Roadmap
description:: milestones


## [x] M-Engine — Rule-driven engine

**Status:** Shipped — resolve/run/judge deployed (single + batch); where:: hardening pending.

**Reference:** [[Audit Architecture]] § Components + § Data flow

**Tests:** every R-anchor-page rule reports pass on the FEX examples; a deliberately-broken rule reports fail; second run reuses cached verdicts.

### [x] M-Engine.1 — Resolve → run → judge  [F001]

The matcher + scheduler: detect facets, flatten rulesets, bind rules to targets via `where::`, run mechanical by script (verdict-cached), judge the rest by agent.

- [x] `where::` selector (always / file / anchor / sentinel)
- [x] Mechanical run with content-hash verdict caching
- [x] Agent judge pass + recorded verdicts
- [x] Both `/audit anchor` and `/audit doc` surfaces

### [ ] M-Engine.2 — Backtick where:: parser swap  [F007]

Backtick-wrap every `where::` expression; coordinated parser change gated by a green rule-set test suite before and after.

- [ ] Selector parser strips surrounding backticks
- [ ] Snapshot match-sets identical before/after the file swap

### .

## [ ] M-Fix — Fix-by-default + automation levels

**Status:** Active — F002 first increment landed (resolution gap closed); fix stage + the four levels pending.

**Reference:** [[Audit PRD]] § Automation scale; [[Audit Architecture]] § Automation level as a fix-stage parameter

**Tests:** break a mechanical rule in a scratch [[HBR]] → `/audit` repairs + re-run green; `dry` writes nothing.

### [~] M-Fix.1 — Fix-by-default + leveled fixing  [F002]

`fix::` companion to `check::`; default run corrects (Standard), `dry` reports; level masks the fixer set.

- [x] Resolution gap closed — R-doc includes design-facet rulesets; mechanical checkers run
- [ ] `fix::` companion + fix-by-default run mode
- [ ] Bounded-judgment fix stage
- [ ] Four-level parameter (Informational / Online / Standard / Aggressive)

### [ ] M-Fix.2 — Deletion mark + `/audit sweep`

Annotate-don't-delete: a rule implying removal wraps content in a `Recommend deleting` callout; a separate `/audit sweep` removes only marked blocks. (Roadmap is the spec — no feature doc yet.)

- [ ] `Recommend deleting` callout emitter on removal-implying rules
- [ ] `/audit sweep` operation (removes marked blocks only)

### .

## [x] M-OnWrite — Online correction path

**Status:** Shipped (markdown slice, vault-wide) — distill generalization + test workflow pending.

**Reference:** [[Audit Architecture]] § Data flow; [[Audit Stories]] US-AUDIT-1

**Tests:** the F003 on-write checklist workflow — mechanical catch, clean pass, judgment reminder, relevance gate, throttle, speed.

### [x] M-OnWrite.1 — Closed-off E2E slice  [F004]

PostToolUse hook auto-fixes mechanical findings in place, messages the agent about subjective ones.

### [x] M-OnWrite.2 — Vault-wide rollout + safety guard  [F005]

Vault-wide scope + the alphanumeric-subsequence no-delete guard (any letter/digit-dropping fix reverts to a flag).

### [x] M-OnWrite.3 — Markdown rule library  [F008]

Rules-as-markdown hygiene library + loader/runner.

### [ ] M-OnWrite.4 — Distill generalization + reminders  [F003]

Extend the distilled module beyond the markdown slice to the full corpus; `where::`-gated judgment-title reminders, throttled once per file per session.

- [ ] `/distill` bakes the doc/anchor corpus into the merged module
- [ ] Judgment reminders surfaced + throttled
- [ ] Single test workflow asserts the whole checklist

### [ ] M-OnWrite.5 — Rule-attention discipline  [F006]

When and how the agent attends to surfaced rules at write-time.

### .

## [x] M-Q — Q.md + structural sub-audit rules

**Status:** Shipped — the q-family + architecture validation are in place; ask.md coverage in verify.

**Reference:** [[Audit PRD]] § Scope

### [x] M-Q.1 — Q.md constraint validator  [F009]

### [x] M-Q.2 — Bracket ↔ H2 consistency  [F010]

### [x] M-Q.3 — Designing requires justification  [F011]

### [x] M-Q.4 — H3-form Open Questions  [F012]

### [x] M-Q.5 — ask.md ↔ feature-doc drift check  [F013]

### [ ] M-Q.6 — ask.md coverage + backtick-filepath link  [F014]

### [x] M-Q.7 — Architecture-doc validation  [F015]

### .

## [ ] M-Migrate — Refactor legacy sub-audits onto the engine

**Status:** Later — sub-audits are preserved and working today; re-express them as rulesets the unified engine resolves and runs, retiring the bespoke scripts as each is covered.

**Reference:** [[Audit PRD]] § Scope; [[Audit Architecture]] § Where the rule format lives

### [x] M-Migrate.1 — Retire `/lint` into `/audit`  [F016]

Hard rename, 1:1 subaction map, vault-wide reference sweep.

### [ ] M-Migrate.2 — Sub-audits as rulesets

Re-express `structure / docs / dispatch / code / publish / integrity` as engine-run rulesets; retire the hand-written scripts.

### [ ] M-Migrate.3 — Per-anchor level pinning

Each anchor declares its explicit-pass level; the engine masks the fixer set. Online hooks stay pinned to Online.

### .
