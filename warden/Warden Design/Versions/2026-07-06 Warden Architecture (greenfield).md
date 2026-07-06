---
description: "greenfield architecture draft (2026-07-06) — the shipped system decomposed fresh from PRD + features, unanchored from the live doc's structure; input to /architect update"
---

# Warden Architecture (greenfield draft, 2026-07-06)

A fresh decomposition of Warden **as built** (post-M8: F211–F223, F229, the veto surface), derived from [[Warden PRD]] + the feature docs, deliberately not anchored on the live doc's section flow. Seven subsystems.

| Subsystem | One line |
|---|---|
| **Corpus & Language** | the rules on disk — `RULE`/`RULESET` markdown, `include::` composition, three homes, `when ∧ where ∧ if` |
| **Compiler** | scan + compile → `rules-ir.json` + `rules_all.py`; recompile cache; base-trait + declared-trait stamps |
| **Live Dispatch** | the installed Rust hook + the Python reference dispatcher: event → moments → anchor governance → fire → tell/deny |
| **Resident Interpreter** | the warm daemon: preloaded rule bodies over a Unix socket; session registry, once-per-turn dedup, auto-reload |
| **Interpretation Environment** | the lazy `ctx` the bodies run against: file/anchor/git/event + agent-state + turn content + oracle + the re-eval economy |
| **Doc-Fire & Audit Bridge** | the `write:markdown` doc-audit path delegating check+fix to `audit-plan` — two consumers, one corpus |
| **Activation & Governance** | which rules are in force where: `.anchor` traits, the implicit anchor-base, file-anchor vs cwd-anchor per moment, nearest-wins |

Cross-cutting: the **five-layer test regime** (unit · golden corpus · two differentials · perf · live-e2e) and the **kill switch** (`warden off` silences every subsystem at once).

## Module partition

Every source module in exactly one subsystem:

| Subsystem | Modules |
|---|---|
| Corpus & Language | (no code — the vault's markdown + [[FCT Ruleset]] spec) |
| Compiler | `warden_scan.py`, `warden_compile.py` |
| Live Dispatch | `rs/src/hook.rs` (installed), `warden_hook.py` (reference), `rs/src/lib.rs` (selection) |
| Resident Interpreter | `warden_daemon.py` |
| Interpretation Environment | `warden_fire.py` (ctx build + fire), `warden_agent.py`, `warden_reval.py` |
| Doc-Fire & Audit Bridge | `warden_docfire.py` (+ `audit-plan.py`, owned by the audit skill) |
| Activation & Governance | (policy, not a module — realized in `warden_compile.ANCHOR_BASE_TRAITS`, `warden_fire.effective_traits`, the hooks' per-moment anchor pick) |
| CLI / lifecycle | `engine/warden` |
| Test regime | `test_warden_*.py`, `cargo test`, `Warden Corpus/` |

## Data flow

Authoring: markdown rules → **Compiler** → IR + emitted module (`~/.warden/`). Live: Claude Code event → **Live Dispatch** (kill switch, moments, governance) → declarative rules answered natively; Python bodies → **Resident Interpreter** → bodies evaluate over the **Interpretation Environment** → steers/denies re-interleaved and emitted. Writes additionally route through the **Doc-Fire bridge**. The explicit `/audit` path consumes the same corpus without the hook front-end.

## Notable deltas a fresh eye sees vs. the pre-build design

1. **The Interpretation Environment is a real subsystem now** — agent-state (F216), turn content + oracle (F217), and the re-eval economy (F215) shipped as three modules with shared lazy-view discipline (reads never raise); the design docs treat them as scattered `ctx` footnotes.
2. **Activation & Governance earned subsystem rank** — anchor-base (F229), the vault-root anchor, per-moment file-vs-cwd governance, and nearest-wins shadowing are load-bearing policy with real failure modes (the 2026-07-06 veto-surface audit), not a paragraph under adoption.
3. **The audit bridge is a boundary, not a merger** — Warden deliberately delegates doc check+fix execution to `audit-plan` (M4a) rather than absorbing it; the fixer registry and never-delete floor live on the audit side of the line.
