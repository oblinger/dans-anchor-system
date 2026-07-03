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

_**Live push — user directive 2026-07-02** ([[Warden Roadmap]] § Live push): go live now + test live all the way + Rust forward. Priority order below._

- **F220 — Live hook install + kill switch** [Active] — wire the compiled engine into the real `settings.json` hook surface, steer-only on a pilot (`audit-q` + selftest), with an instant global kill switch (`warden off`). Safety-first: kill switch before go-live. → [[F220 — Live hook install + kill switch]]
  - **Next:** building foundation-first — kill switch (`~/.warden/DISABLED` sentinel + `warden on|off|status`) + the `warden_hook.py` dispatcher (event→moment map, lazy fire, fail-safe no-op) + the `warden` CLI (install/uninstall/fire).
- **F221 — Live-integration test class** [Ready] — the e2e/live layer F214 named but didn't build: `R-warden-selftest` ruleset + `warden-selftest` trait, and a harness that **drives a real agent through a moment and proves the hook fired via the log**. Each case run twice (on/off) to prove the kill switch. Rides F220. → [[F221 — Live-integration test class]]
  - **Next:** author the selftest ruleset + trait; build the drive-agent-and-check-log harness once F220's dispatcher is live.
- **F213 — Rust performance implementation** [Ready] — *pulled forward from M8 per the live push.* Fire-time hot path, behavior-identical to the Python reference (the differential oracle), under the per-moment ms budget. → [[F213 — Rust performance implementation + ms budget]]
  - **Next:** scaffold the Rust crate consuming the shared IR table; differential-test against `warden_engine` on the golden corpus.
- **Moment-corpus golden case** [Ready] — extend the golden corpus from doc-audit to the **moment fire path** (bless R-query-14's steer output as a moment-stream case), then test it live on the system. Rides F220/F221.

- **M1 — Rule compiler / installer** [Ready] — design + skeleton: active-set resolution (per anchor), index selection, per-moment pre-compilation, the install + fire contract. Pilot by porting `R-query-14` to fire via the compiler. → [[F211 — Rule compiler and installer]]
  - **Next:** **Engine complete 2026-07-02 — every Success Criterion met at the engine level.** `warden_compile.py` (single + `--root` corpus compile of all 449 vault rules; when-rules→`moments`, tier doc-rules→`doc_rules` with `check`/`judge`/`track` actions; per-function constant encapsulation; recompile cache on the scan-index hash), `warden_fire.py` (moment dispatcher — indexed dispatch + active-set gating), and `warden_engine.py` (the lazy scan→compile→fire reference loop = F212's oracle). `R-query-14` fires end-to-end; 4 engine test suites green (`test_warden_{scan,compile,fire,engine}.py`). **Only remaining piece = live-hook install (M4):** wiring the compiled moment-modules into the real Claude Code hook surface — high-blast-radius, its own session. Vault-wide active-set adoption also awaits the trait→ruleset bindings per **F218** (propose→review), but the engine resolves active-set from whatever `.anchor` traits are declared.

## Later

- **M2 — Python reference implementation** [Ready] — **reference loop + both fire paths built 2026-07-02.** `warden_engine.py` (lazy scan→compile→fire, the behavioral oracle; `R-query-14` fires through it) **plus `warden_docfire.py`** — the IR-driven doc-audit fire path, **verdict-identical to `audit-plan --run`**: the golden corpus runs through a `warden` engine adapter and matches the audit-plan-blessed `expected.json` verdict-for-verdict (4/4, same signature); `test_warden_docfire.py` is a standing differential test (warden ≡ audit-plan every case). `WardenEngine.fire_audit` owns the audit surface; the **"golden-corpus suite passes" Success Criterion is met.** Remaining: the moment-side steer **snapshot API** + mapping the in-process dispatcher to real hook events for e2e. Reuses `audit-plan.py`. → [[F212 — Python reference implementation]]
- **M3 — Rust performance implementation** — fire-time hot path under the per-moment ms budget; behavior-identical to the Python reference (differential-tested). → [[F213 — Rust performance implementation + ms budget]]
- **Activation self-audit rules (F219)** [Later] — the **ruleset-reachability** rule guarding trait-driven activation (*every-ruleset-reachable-from-some-trait* — no orphaned ruleset); the base-trait-present check retired now the base trait is implicit (2026-07-02). Warden auditing its own wiring; lands after M1's per-trait active-set. → [[F219 — Activation self-audit rules — base-trait + ruleset-reachability]]
- **Design-rules catalog (F218)** [Later] — migrated from SKA F108 2026-07-02 (user: pull it into Warden). The user's recurring architectural rules (single `Interfaces/` folder, factory construction, peg-board registry, design-sign-off gate) authored as Warden rulesets, mined from existing PRDs/Principles/Architecture docs (propose→review), adopted per-application by `.anchor` trait. Q1 (rides the ruleset system — no separate store) + Q2 (agent proposes, user upgrades) resolved. *Content* over the engine; lands behind M1. → [[F218 — Design-rules catalog — ship with skills, adopt per-application]]
- **M4 — Migrate existing surfaces** — fold `audit-q` autofire, F091 `compact` / `markdown-write`, and the `audit-on-write` distill module onto the unified compiler; remove bespoke per-rule hook code. **Seam proven 2026-07-02:** `warden_docfire.py` already fires the tier doc-rules verdict-identically to `audit-plan --run` by reusing its checker registry through `run_checker` (the golden corpus passes through the `warden` engine) — so the doc-audit surface migrates without any parallel checker code. Remaining M4 = the *live-hook install* (wiring compiled moment-modules into the real Claude Code hook surface) + retiring the bespoke per-rule hook drivers.
- **M5 — Perf hardening** — profile the hot path, set + enforce the budget policy (advisory vs. demote-to-audit), verify cache invalidation under a stress workload.

## Done

_None._
