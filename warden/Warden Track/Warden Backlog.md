---
description: "deferred work — roadmap milestones M0–M5"
---
# Warden Backlog

## Active

_None._

## Ready


## Now

- **Conversation-content gating (F217)** [Designed] — designed 2026-07-01, revised 2026-07-02 (user review): `agent.turn` view (6 content members, nested under `agent`, transcript+ledger sourced, lazy + capped; `agent.is_asking` the sole asking predicate), mechanical predicate tier, `ask_oracle` binary-verdict idiom with prefilter discipline + two-wall loop prevention, 3 example rules. Q1–Q3 resolved 2026-07-02 (user accepted the Leans): delegated self-check live path, current-turn-only v1, minimal predicate surface. Implementation rides M2; the shared question heuristic is specified in [[F216 — Agent-state model — sensing what the agent is doing|F216]]; `agent.turn` propagated into [[Warden Semantics]]. → [[F217 — Conversation-content gating — rules on what was said]]
- **Rule-system testing regime (F214)** [Designed] — standing gate, no standalone next step (unit + e2e layers ride the build milestone, differential + perf ride Rust; rebracketed from stale [Active] 2026-07-02). Q1 resolved 2026-07-01 (user): CI = GitHub Actions in ob-skills NOW (`.github/workflows/warden-tests.yml`, golden-corpus job; migrates wholesale at extraction). Continuous gate — layers join as milestones land. Designed; design landed 2026-07-01: five layers with concrete contracts; golden corpus live at [[Warden Corpus]] (runner + 4 seed goldens against the shipped audit engine, FAIL/STALE re-bless flow verified). Unit + e2e ride the build milestone; differential + perf gates ride the Rust milestone. → [[F214 — Rule-system testing regime]]
- **Agent-state model (F216)** [Designed] — reframed 2026-07-01 to the user's right-now model: `asking` = the turn just ended addressing a question (AskUserQuestion dialog moment + text heuristic; `queries.md` retired as a state signal — it's anchor state); both forks resolved by the reframe; `paused` state (stopped with open tasks) + `agent.state_seconds`/`agent.open_tasks` properties (accepted 2026-07-02). Implementation rides M2. → [[F216 — Agent-state model — sensing what the agent is doing]]
- **F209 — Unified trigger taxonomy + `when::` language (M0 freeze)** [Designed] — → [[F209 — Unified trigger taxonomy + when language]] · all questions resolved 2026-07-02 (user): phase default (`tool`→`post`, `skill`→`pre`), `git:*` first-class family, `skill:pre` now / `skill:post` deferred to V2/V3 ([[Warden Roadmap]] § Beyond v1). Designed and ready to freeze; the M0 language freeze now waits only on [[F210 — Conjunction binding + indexing|F210]], then freeze both. Remaining build step: map every existing trigger surface (`compact`, `markdown-write`, `skill:*`) onto a canonical moment path with no orphans.
- **F210 — Conjunction binding + indexing (M0 freeze)** [Designed] — → [[F210 — Conjunction binding + indexing]] · all questions resolved 2026-07-02 (user accepted the Leans): `if::` guard vocabulary = fixed set (`git-aspect`/`mode`/`trait`/`facet`, Python escape hatch), `where::` precedence = resolved-first. **M0 language freeze complete** (with F209) — the `when::`/`where::`/`if::` surface is locked.

## Next

- **M1 — Rule compiler / installer** [Ready] — design + skeleton: active-set resolution (per anchor), index selection, per-moment pre-compilation, the install + fire contract. Pilot by porting `R-query-14` to fire via the compiler. → [[F211 — Rule compiler and installer]]
  - **Next:** **Compile→fire vertical built + tested 2026-07-02.** `warden_compile.py` (parse F180 when-rule grammar → clause-split → emit IR + module) compiles `R-query` to exactly the § IR schema worked example; `warden_fire.py` (moment dispatcher: `moments[moment]` lookup → active-set filter → declarative guard → emitted body → steers) fires the real `R-query-14` end-to-end. `test_warden_compile.py` + `test_warden_fire.py` (both green) pin the IR row, the emitted-body autofire steer, **indexed dispatch**, and **active-set gating** — the F211 Success-Criteria core. Remaining is downstream/content-gated, **not free execution**: live-hook install rides **M4**; full-anchor active-set needs the trait→ruleset `include::` bindings authored per **F218** (propose→review); tier doc-rule emission + the recompile cache ride the from-index compile. Engine complete; vault-wide exercise gated on M4 + F218.

## Later

- **M2 — Python reference implementation** — full compile→install→fire loop in Python; the behavioral oracle; reuses `audit-plan.py`. → [[F212 — Python reference implementation]]
- **M3 — Rust performance implementation** — fire-time hot path under the per-moment ms budget; behavior-identical to the Python reference (differential-tested). → [[F213 — Rust performance implementation + ms budget]]
- **Activation self-audit rules (F219)** [Later] — the **ruleset-reachability** rule guarding trait-driven activation (*every-ruleset-reachable-from-some-trait* — no orphaned ruleset); the base-trait-present check retired now the base trait is implicit (2026-07-02). Warden auditing its own wiring; lands after M1's per-trait active-set. → [[F219 — Activation self-audit rules — base-trait + ruleset-reachability]]
- **Design-rules catalog (F218)** [Later] — migrated from SKA F108 2026-07-02 (user: pull it into Warden). The user's recurring architectural rules (single `Interfaces/` folder, factory construction, peg-board registry, design-sign-off gate) authored as Warden rulesets, mined from existing PRDs/Principles/Architecture docs (propose→review), adopted per-application by `.anchor` trait. Q1 (rides the ruleset system — no separate store) + Q2 (agent proposes, user upgrades) resolved. *Content* over the engine; lands behind M1. → [[F218 — Design-rules catalog — ship with skills, adopt per-application]]
- **M4 — Migrate existing surfaces** — fold `audit-q` autofire, F091 `compact` / `markdown-write`, and the `audit-on-write` distill module onto the unified compiler; remove bespoke per-rule hook code.
- **M5 — Perf hardening** — profile the hot path, set + enforce the budget policy (advisory vs. demote-to-audit), verify cache invalidation under a stress workload.

## Done

_None._
