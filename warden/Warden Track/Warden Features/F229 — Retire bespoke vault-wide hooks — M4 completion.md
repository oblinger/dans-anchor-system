---
description: "F229 — the last M4 piece: retire audit-on-write.sh (the sole surviving bespoke vault-wide hook) once the audit-on-write trait's coverage decision is made."
---

## Open Questions

### Q1 — How does `audit-on-write` coverage go vault-wide so the bespoke hook can retire? ^F229-Q1

With M4a landed (fixer parity — Warden's doc-fire behaviorally subsumes the bespoke F177 hook by construction), the only thing keeping `audit-on-write.sh` alive is **coverage**: it fires vault-wide (`__VAULT__` in `~/.config/ob-skills/audit-on-write-roots`), while Warden's replacement is trait-gated — and it currently **double-fires** with Warden's doc-fire in adopting anchors (e.g. Warden). Retiring it without an adoption move narrows coverage to adopting-anchors-only; adoption is the user's call (F218 Q2 doctrine: nothing is auto-adopted).

- **(A)** Fold `audit-on-write` into the implicit `_base` trait — every anchor gets doc-fire-on-write, exactly matching today's `__VAULT__` coverage; the bespoke hook retires with zero coverage change.
- **(B)** Per-anchor sweep — add the trait to the anchors that want it; the rest lose on-write auditing (accepting narrower coverage).
- **(C)** Keep the bespoke hook for now — live with the double-fire in adopting anchors; revisit after more Warden soak.
- **Recommendation:** Lean (A) — a coverage-preserving swap (same files audited, one engine instead of two), the Rust path is ~7× faster than the bash+python spin-up it replaces, and `warden off` remains the instant global kill.

# [[Warden]] · F229 — Retire bespoke vault-wide hooks — M4 completion

## Summary

The completion slice of roadmap milestone **M4 — migrate existing surfaces**. Inventory (2026-07-05): of the three bespoke surfaces M4 named, **two are already gone** — no audit-q-autofire or F091 compact/markdown-write drivers remain in `settings.json`; Warden absorbed those surfaces (R-query-14 fires through the compiled engine; `write:markdown` / `session:compact` are dispatcher moments). The sole survivor is **`audit-on-write.sh`** (F177/F004), the PostToolUse markdown-audit hook, live vault-wide.

M4a (Done 2026-07-05) gave Warden's `audit-on-write` trait path full behavioral parity — `warden_docfire.fire_on_write` delegates check + fix to `audit-plan.execute_on_write` itself (same fixer registry, same never-delete floor). What remains is the Q1 coverage decision, then the mechanical retirement.

## Success Criteria

**Tier:** 1 (agent-immediate once Q1 is answered)
**Blocks next:** none — closes roadmap M4.

**What done looks like.** `audit-on-write.sh` and its `settings.json` PostToolUse entry are removed; the roots file is retired; on-write markdown auditing flows only through the Warden dispatcher at whatever coverage Q1 chose; no double-fire anywhere; `warden off` silences the surface entirely.

**How it will be verified.** A markdown write with a known mechanical fail in (a) an adopting anchor and (b) a previously-`__VAULT__`-covered non-adopting anchor: steers appear per the Q1 coverage choice, exactly once each; `warden off` → zero. The F177 fixtures (`test-audit-on-write.sh`) re-pointed or retired with the hook.

## Status

**Questions** (2026-07-05) — split out of the M4 backlog row when M4a landed; Q1 (the coverage/adoption decision) is the only gate, reserved to the user per the F218 Q2 adoption doctrine.
