---
description: "Fix-by-default + leveled automation; rules carry Python checks distilled into a merged module."
---

# [[Audit]] · F002 — Audit fix-by-default + Python rule functions

## Summary

Two coupled upgrades to the F161 audit engine ([[F001 — Rule-driven audit engine — resolve, run, judge|F001]]):

1. **Audit fixes by default.** `/audit` (and the engine) stop being report-only. The default run **corrects** what it can — applying deterministic mechanical repairs and bounded ("not too radical") judgment fixes — and surfaces only what genuinely needs the user. `dry` becomes the opt-out for report-only. This makes "audit" mean what the user actually wants ("the whole point of auditing is to correct it"), and turns the examples/anchors into things the audit *converges* rather than just describes.

2. **Rules can carry Python.** Beyond the built-in checker primitives, a document/anchor rule may carry a small Python check `(path, content)` that **prints violations to stdout**, designed to run in **milliseconds**. The `/distill` skill merges all such rule bodies into a pre-computed module in the config folder; a write-hook runs it **every time a file is written**, flagging a violation the moment it's introduced — a fast, always-on guardrail distinct from the heavier on-demand `/audit` pass.

The design home for all of this is the **rule-set subsystem's design docs** (PRD + Architecture + API docs) — including the aspirational multi-level fixing model and the installed write-hook.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** `/audit <anchor>` (no `dry`) applies mechanical `fix::` repairs + bounded judgment fixes and re-runs to convergence; `/audit <anchor> dry` reports without writing. A document rule authored as a python-rule (`(path, content)` printing violations to stdout) is distilled into the merged config-folder module and, on a `Write`/`Edit` of a matching file, flags its violation within milliseconds. The **rule-set** PRD + Architecture + API docs exist and state the fix-by-default + leveled-fixing + python-rule + distill + write-hook goals.

**How it will be verified.** (1) Break a mechanical rule in a scratch copy of [[HBR]], run `/audit` non-dry, confirm it auto-repairs and the re-run is green; run with `dry`, confirm no write. (2) Author a trivial python-rule (e.g. "no tab characters"), `/distill`, `Write` a violating file, confirm the write-hook flags the violation sub-second. (3) `audit-plan.py` ships `fix::` support + a python-rule loader; `ls` the rule-set Design folder shows PRD + Architecture + API docs.

## Design

### Thrust 1 — fix-by-default + leveled fixing

**Default = fix; `dry` = report.** The `/audit` contract flips: the default run corrects, `dry` is report-only. This unifies with the engine's existing three-stage shape (resolve → run → judge) by adding a **fix stage**:

- **Mechanical fixes** — each `checked` rule may carry a **`fix::`** companion to its `check::` (a repair primitive paired to the check). On a non-dry run the engine applies every `fix::` whose `check::` failed, then re-runs to confirm. Precedent already exists piecemeal (`audit-dispatch`, `audit-q --fix`, `audit-architecture` A3, `audit-api-doc` spacing) — this generalizes it into one `fix::` mechanism.
- **Bounded judgment fixes** — "standard" fixing is **not purely mechanical**: the agent makes *modest, low-risk* judgment corrections (the existing "drive the residual to zero / `None` is a real recommendation" discipline), but **not radical** ones (never invents a whole missing Goals section; never rewrites prose wholesale). Radical/ambiguous findings still surface to the user.

**Leveled fixing (aspirational — not built now).** Fixing aggressiveness is a **level**, and eventually **each application/anchor is pinned to its level** (careful subsystems fix conservatively; scratch ones fix freely). For v1 there is exactly one level — **`standard`** (mechanical + bounded judgment, as above) — and `dry` (no fixing). The multi-level model (`off` / `mechanical` / `standard` / `aggressive`, per-anchor setting) is recorded as the **direction** in the audit design docs, not implemented yet.

**Naming.** Keep the verb `/audit` (it is wired into ~12 sub-actions, many feature docs, dispatch tables, and the F161 engine — renaming is high-churn). The default simply *fixes*; `dry` reports. (If a fixing-verb rename is ever wanted, `/conform` is the leading candidate — deferred.)

### Thrust 2 — Python rule functions, distilled + write-hook-triggered

Beyond named built-in primitives, a rule may carry a **Python check** for documents and anchors. The contract, authoring, compilation, and trigger:

- **Contract.** A rule body is Python that, given the target, **prints one violation message per line to stdout** (no output = pass). It receives the file's **path** and **content** (two strings) — `content` for in-place text scans, `path` for rules that walk the filesystem (e.g. "this doc's sibling X must exist"). Stdout-as-the-channel is what lets many rule bodies be concatenated into one module and run in one shot, the caller simply reading stdout.
- **Two authoring formats** (both allowed):
  1. **Embedded** — a ```python``` block inside the rule's markdown (the F081 `audit-markdown` pattern), fine for tiny rules.
  2. **Separated rule-set file** — the rule's Python lives in its own file *alongside the main facet* (a sibling rule-set file). **Usually preferred**, so facet specs don't bloat into huge code-bearing files. The rule references its separated body.
- **Distill → a pre-computed merged module.** The **`/distill`** skill compiles **all** the document/anchor rule bodies that exist across the rule sets into **special merged Python module(s) in the config folder** (e.g. `~/.config/ob-skills/…`). A distill run gathers every rule's Python and merges the bodies together, so at runtime there is already a precomputed module that applies all applicable rules in quick succession — no per-write discovery/parse cost.
- **Fast by design.** Each rule is meant to run in **milliseconds**; because they are pre-distilled and merged, a file write checks the whole applicable group cheaply.
- **Hook-triggered on write.** A `PostToolUse` hook on `Write`/`Edit` runs the distilled module against the just-written file **every time a file is written**, flagging any violation immediately — an always-on guardrail, separate from the heavier on-demand `/audit`.

### Deliverable — capture all of this in the RULE SET design docs

This is **rule-set** territory, not merely audit — so the home for it is the **rule-set subsystem's design docs**. Create/update them to fully describe the mechanism:

- **PRD** — the rule-set system's purpose: rules carry checks (built-in primitive, embedded Python, or separated rule-set file); `/audit` runs them (resolve→run→judge→**fix**, fix-by-default + leveled fixing aspirational); the fast subset is distilled + hook-triggered on write.
- **Architecture** — the moving parts and data flow: rule formats → `/distill` → the merged module(s) in the config folder → the **`PostToolUse` write-hook that gets installed** (the installed hook itself is described here) → stdout-violation reporting. The audit pipeline (engine + `fix::`) is the on-demand consumer of the same rule sets.
- **API docs** — the rule-author-facing contract: the Python check signature/stdout convention, the embedded vs separated-file formats, how a rule declares its body, and the distill/merge interface.

(The audit pipeline's own resolve→run→judge→fix design — F161 + this feature's fix stage — is cross-referenced from the rule-set Architecture; the rule sets are the shared substrate both `/audit` and the write-hook consume.)

### Relationship to F161

F161 delivered resolve → run (mechanical, verdict-cached) → judge (agent) + both `/audit anchor` and `/audit doc` surfaces. F166 adds the **fix stage** (`fix::` + bounded-judgment, fix-by-default) and the **python-rule + write-hook** guardrail, and writes the audit design docs that house the whole direction.

## Status

**Active** — user greenlit implementation 2026-06-14 ("yes I really do want to wire it up so the audit engine does its own where-clause checking"). First increment landed (commit `098d6bb`): the **resolution gap** is closed — R-doc's `include::` now lists the design-doc facet rulesets (R-doc-structure, R-prd, R-architecture, R-testing, R-decisions, R-stories), so `/audit doc` binds each to its `where::` targets and the already-existing PRD/Testing/etc. checkers run mechanically (verified: R-prd-01..06 on HBR PRD). New `no_dispatch_table` checker added (R-stories-12) — a non-anchor story with a masthead now mechanically fails. **Remaining:** `fix::` companion + fix-by-default run mode; bounded-judgment fix stage; `/distill` merged-module + write-hook generalization beyond R-markdown (F177 shipped the R-markdown slice); checkers for the R-architecture / R-decisions / R-stories-01..11 rules still at judge-level; settle the design-docs-as-anchors question before a general `dispatch_table_iff_anchor` checker.

## Resolved

### Q1 — Python rule-function signature + return shape (resolved 2026-06-13)
**Choice:** (A)

Signature is `(path, content)` (two strings), but violations are **printed to stdout** — one message per line, empty output = pass — rather than returned. Stdout-as-channel is what lets many rule bodies be concatenated into one distilled module and run in a single shot, the caller reading stdout. Incorporated into Design § Thrust 2.

> Original Q context:
> - **Q1 — Python rule-function signature + return shape** — A rule may carry a Python check. Proposed contract: `def check(path: str, content: str) -> list[str]` — receives the file's path and its full text, returns a list of violation messages (empty = pass). The two-arg form lets a rule either scan the text in-place *or* walk the filesystem from `path`.
>   - (A) `(path, content) -> list[str]` (violations; `[]` = pass) — **recommended**; messages are the finding text, naturally many-per-file.
>   - (B) `(path, content) -> str | None` (one message or None) — simpler but caps a rule at one finding.
>   - (C) `(path, content) -> bool` — least informative; no message to surface/fix from.
> - **Recommendation:** Strong (A) — matches how the engine already emits `(rule, target, detail)` verdicts; a fixer can pair to it later.

### Q2 — Where the Python lives + relation to F081 `audit-markdown` (resolved 2026-06-13)
**Choice:** (A)+(B)

Both formats allowed: an embedded ```python``` block in the rule (F081 pattern, for tiny rules) OR — usually preferred — a separated rule-set file living alongside the main facet, so facet specs don't bloat with code. Generalizes F081. Incorporated into Design § Thrust 2.

> Original Q context:
> - **Q2 — Where the Python lives + relation to F081 `audit-markdown`** — [[F008 — audit markdown — markdown hygiene rule library|F008]] already established "rules-as-markdown": each rule is one `.md` file with YAML frontmatter + an embedded ```python``` block compiled at load. This feature looks like the *generalization* of that to documents + anchors.
>   - (A) Reuse the F081 pattern verbatim — a rule's Python is an embedded ```python``` block in its rule markdown, compiled at load; the F161 `check::` ref can name either a built-in primitive *or* such a python-rule. **Recommended.**
>   - (B) Separate `.py` files alongside the rule markdown (one fn per file).
> - **Recommendation:** Lean (A) — one rules-as-markdown mechanism, F081 becomes a special case of the general engine; avoids a second rule-authoring format.

### Q3 — Which hook fires the fast checks (resolved 2026-06-13)
**Choice:** (A)

A `PostToolUse` hook on Write/Edit runs the `/distill`-compiled merged module (in the config folder) against the just-written file every write — immediate flagging, separate from on-demand `/audit`. Incorporated into Design § Thrust 2 + the rule-set Architecture (which describes the installed hook). Incorporated into Design § Deliverable.

> Original Q context:
> - **Q3 — Which hook fires the fast checks** — "checked every time you write the file." The fast python-rule group needs a trigger.
>   - (A) A `PostToolUse` hook on `Write`/`Edit`/`NotebookEdit` — runs the doc's applicable fast rules against the just-written file, flags violations inline. **Recommended.**
>   - (B) A `Stop`/`PreCompact` hook (batch at end of turn).
>   - (C) Both — PostToolUse for immediate flagging, Stop for a sweep.
> - **Recommendation:** Lean (A) for v1 (immediate, per-write); (C) later.



