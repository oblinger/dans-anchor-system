---
description: "F229 — the last M4 piece: retire audit-on-write.sh (the sole surviving bespoke vault-wide hook) once the audit-on-write trait's coverage decision is made."
---

# [[Warden]] · F229 — Retire bespoke vault-wide hooks — M4 completion

## Summary

The completion slice of roadmap milestone **M4 — migrate existing surfaces**. Inventory (2026-07-05): of the three bespoke surfaces M4 named, **two are already gone** — no audit-q-autofire or F091 compact/markdown-write drivers remain in `settings.json`; Warden absorbed those surfaces (R-query-14 fires through the compiled engine; `write:markdown` / `session:compact` are dispatcher moments). The sole survivor is **`audit-on-write.sh`** (F177/F004), the PostToolUse markdown-audit hook, live vault-wide.

M4a (Done 2026-07-05) gave Warden's `audit-on-write` trait path full behavioral parity — `warden_docfire.fire_on_write` delegates check + fix to `audit-plan.execute_on_write` itself (same fixer registry, same never-delete floor). What remains is the Q1 coverage decision, then the mechanical retirement.

## Success Criteria

**Tier:** 1 (agent-immediate once Q1 is answered)
**Blocks next:** none — closes roadmap M4.

**What done looks like.** `audit-on-write.sh` and its `settings.json` PostToolUse entry are removed; the roots file is retired; on-write markdown auditing flows only through the Warden dispatcher at whatever coverage Q1 chose; no double-fire anywhere; `warden off` silences the surface entirely.

**How it will be verified.** A markdown write with a known mechanical fail in (a) an adopting anchor and (b) a previously-`__VAULT__`-covered non-adopting anchor: steers appear per the Q1 coverage choice, exactly once each; `warden off` → zero. The F177 fixtures (`test-audit-on-write.sh`) re-pointed or retired with the hook.


## Resolved

### Q1 — How does `audit-on-write` coverage go vault-wide so the bespoke hook can retire? — RESOLVED (user, 2026-07-06): (A′) anchor-base membership + first-class root anchor + file-path governance ^F229-Q1

**Choice: (A′)** — option (A) refined in discussion: (1) the implicit base trait went **first-class** — renamed `anchor-base`, documented at [[anchor-base]], its members compiled policy (`ANCHOR_BASE_TRAITS` → `ir.base_traits`, expanded by both dispatchers; `warden compile` warns if a `.anchor` declares it); **`audit-on-write` is its first member**, so every anchor audits markdown on write. (2) The **vault-root `.anchor` went first-class** (description + traits, `root: false` DAG key preserved) — every un-anchored vault path resolves to it, making base coverage vault-complete by construction. (3) **`write:`/`read:` moments + the doc-fire are governed by the FILE's anchor** (fall back to cwd for moment rules; doc-fire is strictly file-anchored) — parity with the retired file-scoped hook, and the right semantic: the file's anchor owns the file. (4) `audit-on-write.sh` retired. Future work parked by the user: anchors over the coding tree (`~/ob/proj`) — scan-range, churn, and explicitly-registered out-of-scan anchors — deliberately deferred.

## Status

**Done 2026-07-06 — A′ built, verified live, bespoke hook retired.** All four pieces landed: `anchor-base` rename (engine + Rust + tests + [[Warden Semantics]] § Activation) with the [[anchor-base]] trait spec; `base_traits` stamped into the IR and expanded via `effective_traits` in both dispatchers; vault-root `.anchor` first-classed; file-anchor governance for write/read moments + doc-fire (`test_audit_on_write` pins base-implied, file-anchored, cwd-elsewhere, and un-anchored-file cases). **Retired**: the `audit-on-write.sh` settings.json entry (backup kept), the script + `test-audit-on-write.sh`, and the `__VAULT__` roots file. **Live-verified through the installed Rust dispatcher**: a failing write in a non-declaring anchor steers once (base-implied); a failing write on an un-anchored vault path steers once, governed by the root anchor (`@ kmr`), from a session cwd'd outside the vault; `warden off` → silence. All 10 unit suites + 10 cargo + both differentials + corpus 7/7 + perf gate green; live corpus recompiled (`base_traits: [audit-on-write]`), daemon bounced. **Roadmap M4 is complete — every bespoke hook surface has folded onto the unified engine.**

**Earlier status:**

**Questions** (2026-07-05) — split out of the M4 backlog row when M4a landed; Q1 (the coverage/adoption decision) is the only gate, reserved to the user per the F218 Q2 adoption doctrine.
