---
description: "Vault-wide rollout + the alphanumeric-subsequence no-delete safety guard. Shipped, verified across 507 docs."
---

# [[Audit]] · F005 — Doc audit-on-write — vault-wide rollout + safety guard

## Summary

F177 proved the audit-on-write plumbing on a closed-off slice (one auto-fix rule, one message rule, two fixtures, a 3/3 integration test). F179 takes it to real scope: **wider rule coverage** (a set of non-deleting correct-or-flag rules), a **hard no-delete safety invariant**, **vault-wide scope** (every `.md` under `~/ob/kmr`), and — the load-bearing deliverable — an **agent-driven verification harness** that proves, across the rule set and a sample of real docs, that corrections fire, messages fire, and **clean docs are never modified** (zero false-positives is the safety property that makes vault-wide acceptable).

F177 remains the proven core. F166 remains the home for the always-on `/distill` fast-path and leveled fixing.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** The hook runs over a wider rule set on every `.md` write under the vault. Each auto-fix rule repairs a synthesized violation and re-checks green; each flag rule emits the agent message and leaves the file unchanged. Critically, running the hook over a sample of **already-clean real docs produces ZERO changes** (no false fixes, no deletions). Angle brackets written outside backticks are caught (flagged) in any file, anchor or not.

**How it will be verified.** A dynamic workflow fans out: (1) per wired rule, an agent synthesizes a violating doc, drives it through the hook, asserts correct/flag + no content deletion; (2) a no-collateral-damage pass runs the hook over N real clean docs across the vault and asserts zero diffs. Re-runnable via `test-audit-on-write.sh` (extended) + the workflow report. Green = corrections + messages proven and false-positive rate 0.

## Design

### Safety invariant (the thing that makes vault-wide OK)
A FIXER may only **insert, escape, or normalize** characters; it may **never delete document content**. Enforced **structurally**, not per-fixer: after any fix, the engine asserts the document's **alphanumeric character sequence is preserved as a subsequence** (insertions/escapes/whitespace-normalization OK; any deletion of letters/digits fails). A fix that violates this is **reverted on disk** and downgraded to a flag message. This is the empirical guarantee behind "safe to run vault-wide."

### Scope (Q3 = B)
Every `.md` under `~/ob/kmr` is audited on write (`.git/` and the like skipped). Loose docs (no enclosing `.anchor`) get **only the general markdown rules** — the anchor-relative rules have `where::` selectors that never bind to a file outside an anchor, so they're naturally N/A. The angle-bracket flag applies everywhere — the user's explicit driver: no angle brackets written to any file.

### Rule coverage — v1 wired set (all non-deleting)
- **Auto-fix:** table blank-lines (`R-markdown-02`, done) · wiki-link pipe-escape inside tables (`R-markdown-01`) · em-dash spaced form ` -- ` → ` — ` in prose, never in code/fences (`R-markdown-05`, conservative) · trailing whitespace (new).
- **Flag only:** fence-contains-markdown (`R-markdown-11`, done) · **angle-brackets outside backticks** (new — the priority rule) · (more flag rules fold in later).

### Timing (Q1 = B)
Synchronous, leaning on the flatten cache; same-turn fixes/messages. Loose docs touch only the small `R-markdown` set, so they're cheap. The millisecond `/distill` fast-path is the F166 follow-on for scale.

### Agent verification approach (the workflow)
Two fan-outs via dynamic workflow:
1. **Per-rule correctness** — one agent per wired rule: synthesize a minimal doc violating exactly that rule, run it through the hook, assert (auto-fix → repaired + re-check passes + alphanumeric content preserved; flag → message present + file unchanged).
2. **No-collateral-damage** — sample real clean `.md` across the vault; run the hook on each; assert **zero diff**. Any diff is a defect (false fix) and fails the gate.
A synthesis agent rolls verdicts into a report: per-rule pass/fail + false-positive count (must be 0).

## Status

**Done** (2026-06-14) — implemented + agent-verified at scale. Engine: 3 new checkers + 3 fixers + the **alphanumeric-subsequence no-delete safety guard** (a fix that would delete any letter/digit is reverted on disk and downgraded to a flag). Rules wired (R-markdown): -01 pipe-escape + -05 em-dash → auto-fix; **-13 angle-brackets-outside-backticks → flag** (the priority rule); -14 trailing-whitespace → auto-fix; atop F177's -02/-11. Hook is **vault-wide** — every `.md` under `~/ob/kmr` via the `__VAULT__` roots sentinel; `.git`/`node_modules` skipped. **Verification (dynamic workflow, 28 agents):** 6/6 rules pass (independent synthesize→hook→assert per rule); no-collateral-damage sweep checked **507 real vault docs — 0 content-loss / non-idempotent defects, 0 errors** (229 legitimately fixed). Regression harness green (6 rules + content-preservation + idempotence). The user will additionally verify in normal use.

## Resolved

### Q1 — Timing / performance model (resolved 2026-06-14)
**Choice:** (B) — synchronous, leaning on the flatten cache; same-turn fixes/messages. `/distill` millisecond fast-path deferred to F166 for true scale. Incorporated into Design § Timing.

### Q2 — Auto-fix vs flag boundary; angle brackets (resolved 2026-06-14)
**Choice:** (A) — angle brackets outside backticks are **flagged** (the right fix needs judgment). Auto-fix is reserved for unambiguous, non-deleting normalizers (table spacing, trailing whitespace, table pipe-escape, conservative prose em-dash). General principle: auto-fix only when the repair is provably safe AND non-deleting AND intent-unambiguous; everything else flags. Incorporated into Design § Rule coverage + Safety invariant.

### Q3 — Vault-wide scope (resolved 2026-06-14)
**Choice:** (B) — every `.md` under `~/ob/kmr`, anchor or not, because angle brackets must never be written to any file. Loose docs get only the general markdown rules (anchor-relative rules' `where::` selectors don't bind outside an anchor). Incorporated into Design § Scope.
