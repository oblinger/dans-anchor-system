---
description: "the build sequence — design → compiler → Python ref → Rust perf → testing regime"
---

# Warden Roadmap

The sequenced plan to a **strong landing spot**: Warden running, and complete enough to codify a large fraction of SKA's facets, skills, disciplines, and operations as real rules — with strong testing that the whole system fires correctly. Requirements + perf budgets: [[Warden PRD]]. The language surface is [[Warden Semantics]] / [[Warden Rule]]; worked rules are [[Warden Examples]] + [[Warden Examples Extended]].

> [!info] The shape of this plan
> Every cheap, decision-dense activity — language, engine design, test design, corpus proof, replan — is **batched ahead of the single expensive thing (the build)**. We spend the big execution budget once, against a spec validated four ways. Milestones are sequential; "Done-when" gates the next. Test design lands at M3 but tests **run continuously** from M6 on.

## Live push — user directive 2026-07-02 (re-sequences the milestones)

The engine is built and differential-tested ahead of schedule ([[F211 — Rule compiler and installer|F211]] compile+fire+cache, [[F212 — Python reference implementation|F212]] reference loop + doc-fire, verdict-identical to `audit-plan`, CI-gated). The user directed us to **go live now and drive all the way to a system in real use**, compressing M6/M7 and pulling M8's Rust forward.

> [!important] This list IS the build order — do not ask, execute it top to bottom
> User directive 2026-07-02: *"go ahead and build a roadmap with these pieces in it, so you don't have to ask me in the future what the order is. The order is what the roadmap says."* When Warden work is up next, take the **first unchecked item below** and build it. No ordering question to the user.

**Done:**

1. **Kill switch first** ✅ *(2026-07-02)* — an instant, global, no-edit disable so a broken rule pulls out of every environment in one move. → [[F220 — Live hook install + kill switch|F220]].
2. **Live hook install (pilot surface)** ✅ *(2026-07-02)* — the compiled engine wired into the real `settings.json` hook surface; live steer-only, inert-by-default. → [[F220 — Live hook install + kill switch|F220]].
3. **Live-integration test class** ✅ *(2026-07-02)* — a `warden-selftest` ruleset + funky trait + a harness that drives a real agent and proves the hook fired via the log; each case run on/off to prove the kill switch. Caught the live-only path-quoting bug on its first run. → [[F221 — Live-integration test class|F221]].
4. **Rust engine, phase 1 (selection)** ✅ *(2026-07-02)* — `warden/rs/` `warden-rs` computes the fire plan **byte-for-byte identical** to the Python reference across the live corpus × trait sets + synthetic fixtures (standing differential gate + `cargo test` + CI); **2.65 ms** cold, ~7.5× the Python cold path. → [[F213 — Rust performance implementation + ms budget|F213]].
5. **Moment-corpus golden case** ✅ *(2026-07-02)* — the golden corpus now spans the moment fire path (`warden-moment` engine locks the emitted steer); en route, fixed the corpus runner's `--engine` override (the "warden differential" gate had been a silent no-op). → [[F214 — Rule-system testing regime|F214]].
6. **First real dogfood live** ✅ *(2026-07-02)* — `R-warden-dev` (`warden-dev` trait on `warden/.anchor`) fires a genuinely-useful `session:start` orientation steer in the Warden anchor, proven through the real dispatcher (fires in-anchor, inert elsewhere, kill-switchable). Past the selftest-only pilot: Warden audits its own dev workflow. → [[F220 — Live hook install + kill switch|F220]].

**Next — the fixed order (execute top-down, no re-asking):**

7. **Doc-fire on write** ✅ *(2026-07-02)* — the doc-fire (audit-on-write) path fires live in the `write:markdown` moment: an anchor that adopts the `audit-on-write` trait has its doc-audit rules run on each markdown write, steering `fail` verdicts (never `error` — unimplemented checkers are rule-infra, not the writer's problem). Dispatcher wiring + opt-in trait gate + unit test; live-proven on the Warden anchor (adopted first, 0/38 real docs noisy). → [[F222 — Doc-fire on write|F222]].

8. **Markdown-discipline / progressive-disclosure stress-test rules** ✅ *(2026-07-05)* — the deliberate hard case, now live. `RULESET R-progressive` (2 conditional/multi-check rules — never-both self-masthead+`:>>`-breadcrumb, and section spacing) embedded in [[DSC progressive-disclosure]], wired into [[R-doc]], firing on every markdown write. **13 genuine findings across 784 docs, 0 false positives** — the reliability bar was the whole game (it fires globally), so two over-aggressive directions were pruned once repo-wide validation exposed them (anchor-page classification isn't reliable per-file; the self-masthead + fenced-example-stripping signal is). The F177 hook caught the one design bug live on the first edit. → [[F223 — Markdown-discipline layout rules|F223]].

9. **Rust engine, phase 2 (resident daemon)** ✅ *(2026-07-05)* — Rust owns the **whole** live hot path. `warden_daemon.py` (warm resident interpreter — IR + 459 rules preloaded, Unix-socket IPC, per-rule reference-path fire + warm doc-fire, auto-reload + idle-exit/respawn) + `warden-rs hook` (the live dispatcher in Rust: kill switch, event→moments, anchor/traits, differential-tested selection; Python bodies cross as an IPC round-trip and re-interleave into exact reference fire order) — **installed live** via `warden install --rust` and verified firing `R-warden-dev` through the daemon. Differential gate: identical hook output from both dispatchers (7/7 cases, in CI). Benched **2.98 ms** no-fire / **3.71 ms** Python-body-firing vs the Python hook's ~24 ms — ~7×. → [[F213 — Rust performance implementation + ms budget|F213]] phase 2.

**The live push is complete** — all nine items landed. Warden runs live with the Rust dispatcher on the hot path, the resident interpreter executing Python bodies warm, doc-fire on write, the stress-test layout rules, and the full test regime (unit + golden corpus + two differential gates + live-integration) green.

This is a conscious re-ordering: the design milestones (M1–M3) are substantially met, so we build + go-live + test-live in a tight loop rather than finishing all paper design first. The classic sequence below remains the reference for anything this push doesn't cover.

## The strong landing spot (definition of done)

Reached at the end of **M7**: Warden is installed and firing; a large fraction of SKA facets/skills/disciplines/operations are authored as Warden rules that fire at their moments; the test regime is green. **M8 (efficiency, incl. Rust) is a follow-on** — it makes the landed system fast, it is not part of being landed.

## Milestones

### M1 — Language completion & freeze

**Language questions resolved 2026-07-02** — [[F209 — Unified trigger taxonomy + when language|F209]] (taxonomy: phase defaults, `git:*` first-class, `skill:pre` now / `skill:post` V2/V3) and [[F210 — Conjunction binding + indexing|F210]] (`if::` vocabulary = fixed set, `where::` precedence = resolved-first) are all closed. The `when::`/`where::`/`if::` surface is locked. The diverse-family stress test below is the remaining freeze-insurance pass; a structural gap it surfaces reopens a specific point via the autopilot tripwire rather than the whole freeze.

Close the language. Review every gap the example work surfaced (G1 mechanical-edit verb, G2 ruleset helper namespace, G3 finding confidence — [[Warden Examples Extended]]), decide each **cosmetic** (a predicate / object member / verb — patch) or **structural** (changes the model — escalate), patch [[Warden Semantics]] / [[Warden Rule]] / [[Warden Architecture]], then **freeze**.

- **Diverse-family stress test (the freeze insurance).** Before freezing, hand-pick ~15–25 **deliberately difficult** rules from the corpus — one per family (dispatch, anchor-structure, naming, content-lint, LLM-judgment, `deny`, `edit`, agent-state, code, diagram, …) — and write each in Warden. The hard ones drive the language; this is what keeps the freeze from being a blind bet ahead of the full M4 proof.

**Done-when:** the diverse sample all expresses cleanly; every surfaced gap is resolved or consciously deferred with a recorded reason; the language docs carry no open gap that blocks rule authoring.

### M2 — Engine design

Spec the engine for the frozen language (designs, not code): the compiler/installer ([[F211 — Rule compiler and installer|F211]]), the Python reference architecture ([[F212 — Python reference implementation|F212]]), the resident runtime / daemon + OS-selected notifier ([[Warden Runtime]]), and trait-driven activation.

**Done-when:** a reader could implement each piece without a design decision left open; the fire-time contract, the compile step, and the activation resolution are fully specified.

### M3 — Testing & verification design

Spec the test regime ([[F214 — Rule-system testing regime|F214]]): unit checks, the **differential harness** (the oracle that keeps two implementations honest), the **golden corpus** (rules × fixtures × expected outcomes), performance gates, and the **end-to-end smoke** (a rule authored → adopted → fires at its moment in a live session).

**Done-when:** each test layer has a concrete spec + fixture plan; the differential-harness contract is defined well enough to validate M6 and M8.

### M4 — Corpus migration (the expressibility proof)

Express **all ~477 rules** across the facets, disciplines, and the ruleset library in the frozen Warden language, in place. Each hard rule yields an extended example + a named gap. This is the comprehensive proof the language is sufficient — beyond the M1 sample. (The first gold-standard file, `R-markdown`, and four recovered fan-out files are already done; the mechanical fan-out script is saved.)

**Done-when:** every non-meta rule is in Warden; the meta bucket (`FCT Ruleset` / `R-ruleset` self-spec) is reconciled by hand; all gaps are harvested into [[Warden Examples Extended]].

### M5 — Replan / redesign  *(scheduled, not contingent)*

Absorb everything M2–M4 taught. Re-read the harvested gaps and the engine/test designs together; apply any change the corpus proof forced. This **may ripple back** into the M2/M3 designs — that is expected, and is why build comes after. Re-run this whole roadmap as a planning pass: confirm the milestones still hold or revise them.

**Done-when:** the spec is internally consistent post-corpus; no known structural gap remains; the build scope is frozen.

### M6 — Build  *(the one autopilot phase)*

Implement the Python engine against the triple-validated spec: the full resolve → compile → install → fire loop ([[F212 — Python reference implementation|F212]]), then fold today's bespoke hook surfaces (`compact`, `markdown-write`, `audit-q`) onto it, and emit **`skill:pre`** mechanically from the Skill-tool invocation (`skill:post` is deferred to a later version — § Beyond v1; a v1 `skill:post` is treated as `skill:pre` per [[F209 — Unified trigger taxonomy + when language|F209]] Q3). Tests (M3) run green continuously.

**Done-when:** a real rule, authored in Warden, compiles, installs, and fires at its moment in a live session; the migrated surfaces behave unchanged; the regime is green.

### M7 — Dogfood on SKA  *(the acceptance test — strong landing here)*

Actually **use** Warden: codify a large fraction of SKA facets / skills / disciplines / operations as Warden rules and watch them fire. The corpus migrated at M4 becomes live, adopted, firing rulesets. Run it for real, Rust out.

**Done-when:** a large fraction of SKA's conventions are enforced by live Warden rules; authoring a new rule is a routine, low-friction act; the system has run in daily use without correctness regressions.

### M8 — Performance & efficiency (incl. Rust)  *(follow-on)*

Everything efficiency-oriented, parked behind a system that already works and has earned its keep: the Rust hot-path implementation ([[F213 — Rust performance implementation + ms budget|F213]]), perf hardening + budget enforcement, the re-evaluation economy build ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]), and semantic-update levels. The Rust impl is **behavior-identical** to the Python reference — the M3 differential harness is the oracle, zero verdict/steer divergence. Also parked here *(accepted 2026-07-02)*: **elapsed-time conditions in `when::`** (conjunctive when — the daemon schedules a timer at the threshold instead of rules polling `agent.state_seconds`; [[Warden Semantics]] § `when::`).

**Done-when:** fire-time p99 meets the per-moment budget; differential tests show zero divergence; the efficiency gates are enforced.

## Beyond v1 — later versions (V2 / V3)

Deliberately parked past the strong landing (M7) and the M8 efficiency follow-on, so the first system ships, is tested end-to-end, and is **in real rule use** before we take on this complexity *(user, 2026-07-02)*:

- **`skill:post` — the end-of-skill moment.** v1 ships **`skill:pre` only** (emitted mechanically from the Skill-tool invocation — the precise, cooperation-free signal); a `skill:post` authored in v1 is accepted and treated as `skill:pre` ([[F209 — Unified trigger taxonomy + when language|F209]] Q3). "When did a runbook finish?" has no clean mechanical answer, so post lands later as a **ladder of increasingly-precise approximations**, none blocking, adopted in order: (1) **agent-stop catchall** — post-actions run when the agent stops (the universal floor); (2) **an agreed "done" sentinel** — one mutually-agreed phrase skills emit to mark end-of-work; (3) a **per-skill end-phrase registry**; (4) **next-moment inference** — a following tool use / hook implies the prior finished (caveat: recursive / nested tool use may break this, so it may be unusable as a reliable signal).

## The autopilot discipline — the structural tripwire

The plan assumes the M1/M4 gaps are **small** (extra predicates, object members, verbs). That assumption is held honestly by one rule: every gap is tagged **cosmetic** (patch and proceed) or **structural** (changes the execution model). A structural gap **stops the autopilot** and routes to an M5-style replan rather than being absorbed silently mid-build.

## The testing regime (summary — full spec in F214)

Because Warden instruments almost every action, correctness and performance regressions are both high-stakes. Five layers:

| Layer | What it proves | Runs |
|---|---|---|
| **Unit** | each checker primitive, each taxonomy match, each guard | every commit |
| **Differential (Python ↔ Rust)** | the two implementations agree on every `(rule, target, moment)` verdict/steer | every commit touching either impl (M8) |
| **Golden corpus** | a fixed set of rules × fixtures with recorded expected outcomes; catches semantic drift | every commit |
| **Performance** | per-moment p99 vs. budget; a regression fails CI | every impl commit |
| **End-to-end / live** | a rule authored → adopted → fires at its moment in a real session | per milestone |

Per the dev discipline: when a bug is found, **first write the failing test, then fix**; tests live in the repo, not `/tmp`; the differential harness is the primary oracle so neither implementation drifts silently.

## Sequencing at a glance

M1 freeze → M2 engine design → M3 test design → M4 corpus proof → M5 replan → **M6 build** → M7 dogfood on SKA *(strong landing)* → M8 efficiency + Rust.

All of M1–M5 is design / validation; M6 is the single expensive build; M7 is acceptance; M8 is follow-on.

## Open questions

1. ~~**Repo home for the implementations.**~~ **Resolved by the build (2026-07-02):** the Python reference lives at `warden/engine/`, the Rust crate at `warden/rs/` — both inside the Warden anchor, wired into CI.
2. ~~**Migration ordering (M6 surface fold).**~~ **Resolved by the build (2026-07-02):** `audit-q` was the pilot — `R-query-14` fires live through the compiled engine.
3. **Budget-enforcement policy (M8).** Advisory logging vs. hard demote-to-audit for over-budget rules (also [[Warden PRD]] Q3).
