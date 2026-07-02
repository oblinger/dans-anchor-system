---
description: "deferred work — roadmap milestones M0–M5"
---
# Warden Backlog

## Active

_None._

## Ready

- **Rule-system testing regime (F214)** [Ready] — stand up the five-layer suite (unit · differential Python↔Rust · golden corpus · performance · e2e) incrementally alongside M1–M3. Continuous gate, not a phase. → [[F214 — Rule-system testing regime]]
- **Agent-state model (F216)** [Designed] — design complete 2026-07-01: closed five-state taxonomy, signal inventory, mechanical classifier (pending-question predicate + debounce invariants), four-rung fallback ladder (moment ledger → tmux pane → transcript → residual), environment contract. Two forks open (Q2 scope; `asking` past session end); implementation rides M2. → [[F216 — Agent-state model — sensing what the agent is doing]]
- **Conversation-content gating (F217)** [Ready] — rules that gate on *what the agent said and didn't say* in a turn (e.g. "whenever the agent asks the user X, surface guidance about its reasoning"); adds a bounded, lazy `turn` view, gated mechanically or by `ask_oracle`. Depends on F216. → [[F217 — Conversation-content gating — rules on what was said]]

## Now

- **M0 — freeze the language design** [Questions] — finalize the unified trigger taxonomy and the conjunction model; resolve F209/F210 open questions (phase default, `git:*` first-class, `tool:pre` veto, `if::` grammar). → [[F209 — Unified trigger taxonomy + when language]], [[F210 — Conjunction binding + indexing]]
  - Map every existing trigger surface (`compact`, `markdown-write`, `skill:*`) onto a canonical moment path with no orphans.

## Next

- **M1 — Rule compiler / installer** [Ready] — design + skeleton: active-set resolution (per anchor), index selection, per-moment pre-compilation, the install + fire contract. Pilot by porting `R-query-14` to fire via the compiler. → [[F211 — Rule compiler and installer]]

## Later

- **M2 — Python reference implementation** — full compile→install→fire loop in Python; the behavioral oracle; reuses `audit-plan.py`. → [[F212 — Python reference implementation]]
- **M3 — Rust performance implementation** — fire-time hot path under the per-moment ms budget; behavior-identical to the Python reference (differential-tested). → [[F213 — Rust performance implementation + ms budget]]
- **Activation self-audit rules (F219)** [Later] — the two rules that guard the trait-driven activation wiring: *base-trait-present* (no anchor obeys nothing) and *every-ruleset-reachable-from-some-trait* (no orphaned ruleset). Warden auditing its own wiring; lands after M1's per-trait active-set. → [[F219 — Activation self-audit rules — base-trait + ruleset-reachability]]
- **M4 — Migrate existing surfaces** — fold `audit-q` autofire, F091 `compact` / `markdown-write`, and the `audit-on-write` distill module onto the unified compiler; remove bespoke per-rule hook code.
- **M5 — Perf hardening** — profile the hot path, set + enforce the budget policy (advisory vs. demote-to-audit), verify cache invalidation under a stress workload.

## Done

_None._
