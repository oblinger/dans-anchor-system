---
description: "deferred work — roadmap milestones M0–M5"
---
# Warden Backlog

## Active

_None._

## Ready


## Now

- **Conversation-content gating (F217)** [3 Questions] — designed 2026-07-01: `turn` view (7 members, transcript+ledger sourced, lazy + capped), mechanical predicate tier, `ask_oracle` binary-verdict idiom with prefilter discipline + two-wall loop prevention, 3 example rules. Forks open: live-path judgment, prior-turn window, predicate surface. Implementation rides M2; the shared asks-question predicate is specified in [[F216 — Agent-state model — sensing what the agent is doing|F216]].
  - **Next:** User answers Q1–Q3 (live-path, prior-turn window, predicate surface); on acceptance, propagate the `turn` row into the `Warden Semantics.md` environment table (noted in the doc's Status).
- **Rule-system testing regime (F214)** [Active] — Q1 resolved 2026-07-01 (user): CI = GitHub Actions in ob-skills NOW (`.github/workflows/warden-tests.yml`, golden-corpus job; migrates wholesale at extraction). Continuous gate — layers join as milestones land. Designed; design landed 2026-07-01: five layers with concrete contracts; golden corpus live at [[Warden Corpus]] (runner + 4 seed goldens against the shipped audit engine, FAIL/STALE re-bless flow verified). Unit + e2e ride the build milestone; differential + perf gates ride the Rust milestone. → [[F214 — Rule-system testing regime]]
- **Agent-state model (F216)** [2 Questions] — designed; design complete 2026-07-01: closed five-state taxonomy, signal inventory, mechanical classifier (pending-question predicate + debounce invariants), four-rung fallback ladder (moment ledger → tmux pane → transcript → residual), environment contract. Two forks open (Q2 scope; `asking` past session end); implementation rides M2. → [[F216 — Agent-state model — sensing what the agent is doing]]
- **F209 — Unified trigger taxonomy + `when::` language (M0 freeze)** [3 Questions] — → [[F209 — Unified trigger taxonomy + when language]] · finalize the trigger taxonomy: phase default for bare moments, `git:*` first-class vs derived, `skill:pre/post` emission point. Then map every existing trigger surface (`compact`, `markdown-write`, `skill:*`) onto a canonical moment path with no orphans.
- **F210 — Conjunction binding + indexing (M0 freeze)** [2 Questions] — → [[F210 — Conjunction binding + indexing]] · pin the `if::` guard vocabulary (fixed vs registry) and whether `where::` precedence resolves before index choice; then the language freezes.

## Next

- **M1 — Rule compiler / installer** [Ready] — design + skeleton: active-set resolution (per anchor), index selection, per-moment pre-compilation, the install + fire contract. Pilot by porting `R-query-14` to fire via the compiler. → [[F211 — Rule compiler and installer]]
  - **Next:** After the M0 language freeze ([[F209 — Unified trigger taxonomy + when language|F209]]/[[F210 — Conjunction binding + indexing|F210]] answers), design the compile→install→fire contract + skeleton; pilot with `R-query-14`.

## Later

- **M2 — Python reference implementation** — full compile→install→fire loop in Python; the behavioral oracle; reuses `audit-plan.py`. → [[F212 — Python reference implementation]]
- **M3 — Rust performance implementation** — fire-time hot path under the per-moment ms budget; behavior-identical to the Python reference (differential-tested). → [[F213 — Rust performance implementation + ms budget]]
- **Activation self-audit rules (F219)** [Later] — the two rules that guard the trait-driven activation wiring: *base-trait-present* (no anchor obeys nothing) and *every-ruleset-reachable-from-some-trait* (no orphaned ruleset). Warden auditing its own wiring; lands after M1's per-trait active-set. → [[F219 — Activation self-audit rules — base-trait + ruleset-reachability]]
- **M4 — Migrate existing surfaces** — fold `audit-q` autofire, F091 `compact` / `markdown-write`, and the `audit-on-write` distill module onto the unified compiler; remove bespoke per-rule hook code.
- **M5 — Perf hardening** — profile the hot path, set + enforce the budget policy (advisory vs. demote-to-audit), verify cache invalidation under a stress workload.

## Done

_None._
