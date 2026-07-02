---
description: "F212 — Python reference implementation"
---

# [[Warden]] · F212 — Python reference implementation

## Summary

The **reference implementation** of the whole compile→install→fire loop in Python: clear over fast, the executable spec. It owns authoring-time compilation, the agent-judgment path, and the execution of rules' own Python `trigger`/`guard`. It is the **behavioral oracle** — the Rust performance implementation ([[F213 — Rust performance implementation + ms budget|F213]]) is validated against it by differential testing, so neither can drift silently. It builds directly on today's `audit-plan.py` (already the Python Resolve→Run→Judge engine).

## Success Criteria

**Tier:** 1 (agent-immediate, after F211)
**Blocks next:** [[F213 — Rust performance implementation + ms budget|F213]]

**What done looks like.** The full loop runs in Python: resolve active set → compile per-moment modules → install → fire on a simulated moment stream → emit steers/fixes. All M0–M1 rules fire correctly; the differential harness ([[F214 — Rule-system testing regime|F214]]) records golden outcomes.

**How it will be verified.** The golden-corpus suite (rules × fixtures × moments → recorded verdicts/steers) passes; the ported `R-query-14` fires identically to today's `audit-q.py` autofire.

## Design

- **Reuse** the existing `audit-plan.py` resolver/flattener/selector as the compiler's front half.
- **Add** the moment-indexer, per-moment module builder, an in-process moment dispatcher (simulating the hook surface), and the steer/fix emitter.
- **Expose** a stable verdict/steer API the differential harness snapshots.
- Clarity-first: this is the spec, so readability and exhaustive comments over micro-optimization.

## Status

**Planned** — M2 of [[Warden Roadmap]]. Depends on F211. Reuses `audit-plan.py` (F001, shipped).

## Resolved

1. Module representation that is *also* faithfully portable to Rust (data-table interchange vs. Python-only source emission).
2. How the in-process dispatcher maps to the real harness hook events (PreToolUse/PostToolUse/SessionStart) for the e2e tests.
