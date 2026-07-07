---
description: "the layer contract — who calls Warden, the public surface, guarantees vs non-guarantees, and what callers must never depend on"
---

# Warden Interface

The human-authored layer-contract for the Warden engine (per R-interfaces-folder-03, authored 2026-07-06 when the anchor adopted [[R-arch]]): what callers may rely on, and what is internal. Architecture: [[Warden Architecture]]; runtime detail: [[Warden Runtime]].

## Callers of record

- **Claude Code's hook runner** — the primary caller: every installed `settings.json` entry invokes `warden-rs hook` with the event JSON on stdin ([[Warden Architecture]] §6).
- **The `/audit` skill family** — the explicit on-demand path over the same corpus (`audit-plan.py`; the doc-fire delegates back to it).
- **The user and agents via the `warden` CLI** — `on · off · compile · install · uninstall · status · daemon · fire · log`.
- **`audit-q.py`** — autofires `skill:audit-q`-keyed rules on every run (the F211 pilot surface).

## Public surface

- **The `warden` CLI verbs** — the sanctioned command surface for everything operational (R-wrapper-cli): kill switch, corpus compile, hook install/uninstall, daemon lifecycle, manual moment fire, and the fire log (`warden log`, F231 — which rules were considered/fired at each moment and the steer text verbatim).
- **The hook stdin/stdout contract** — event JSON in; either nothing, `systemMessage` steers, or a `hookSpecificOutput.permissionDecision: deny` (PreToolUse only) out. Malformed input, missing IR, or a down daemon produce silence, never a block.
- **The rule-authoring language** — `RULE`/`RULESET` sentinels, `when::`/`where::`/`if::`, prose/Python bodies ([[Warden Rule]], [[Warden Semantics]]): the stable authoring contract the corpus is written against.
- **`.anchor` trait adoption** — `traits:` lists activate rulesets per anchor; [[anchor-base]] is implicit everywhere.

## Guarantees

- **Fail-open, never blocking** — any engine failure (daemon down, IR missing, body exception, over-budget fire) degrades to silence or a plain steer; the sole intentional block is a `deny` rule at `tool:pre`.
- **One kill switch** — `warden off` silences every environment instantly; no per-surface disable dance.
- **Never-delete floor** — no automated fix drops a letter or digit; unfixable findings surface as steers.
- **Engine equivalence** — the Python reference and the Rust dispatcher produce identical output, enforced by two differential gates in CI; a divergence is a release-blocking bug, not drift.
- **Stable rule identity** — `R-<slug>-NN` ids are permanent, never recycled, never renumbered by composition.

## Non-guarantees

- **Latency is a budget, not a promise** — per-moment budgets (tool:pre 2 ms / post+write 10 ms / else 100 ms) are advisory-enforced (logged, never dropped); a cold daemon start pays a one-time warmup.
- **`skill:post` is approximated** — v1 treats it as `skill:pre` ([[Warden Roadmap]] § Beyond v1).
- **Steers are advice** — a `tell` reaches the agent's context; nothing forces compliance. Only `deny` compels.
- **A Python-bodied `deny` is best-effort** *(2026-07-06 latent-bug audit; posture ruled T013 Q1)* — every current veto rule (R-pathguard, R-ob-remote-ops) carries a Python body, so its evaluation rides the resident daemon; when the daemon is cold or down, the Rust dispatcher skips the owed round-trip and the tool call **proceeds un-vetoed** (fail-open by design). The busy-window is bounded: the daemon serves each connection on its own thread (one slow rule body never queues another session's veto behind it), and the dispatcher waits at most ~2 s at `tool:pre` (20 s post-hoc) before skipping. Guarantee-grade blocks need declaratively-expressible denies the Rust dispatcher can evaluate in-process — tracked on the backlog (T016).
- **Sub-anchor coverage is not inherited** — traits do not cascade; a nested `.anchor` shadows its parent's adoption (nearest wins). Guard rules must be adopted where the guarded files actually live.

## What's hidden — do not depend on

- **The daemon IPC protocol and socket path** (`~/.warden/daemon.sock`) — `warden-rs hook` and `warden_daemon.py` co-evolve them freely.
- **The IR schema** (`rules-ir.json`) and the emitted `rules_all.py` — compiler-private artifacts; recompiled from source at will. Author rules, never IR.
- **`~/.warden/` layout** beyond the `DISABLED` sentinel — logs, caches, the reval store are internal.
- **Engine module internals** — the `warden_*.py` functions are not a library API; the CLI and the hook contract are the only stable entry points.
