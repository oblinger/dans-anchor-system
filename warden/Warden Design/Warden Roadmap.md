---
description: "the build sequence to a strong landing — language freeze, all design, corpus proof, replan, then one build, dogfood on SKA, efficiency last"
---

# Warden Roadmap

The sequenced plan to a **strong landing spot**: Warden running, and complete enough to codify a large fraction of SKA's facets, skills, disciplines, and operations as real rules — with strong testing that the whole system fires correctly. Requirements + perf budgets: [[Warden PRD]]. The language surface is [[Warden Semantics]] / [[Warden Rule]]; worked rules are [[Warden Examples]] + [[Warden Examples Extended]].

> [!info] The shape of this plan
> Every cheap, decision-dense activity — language, engine design, test design, corpus proof, replan — is **batched ahead of the single expensive thing (the build)**. We spend the big execution budget once, against a spec validated four ways. Milestones are sequential; "Done-when" gates the next. Test design lands at M3 but tests **run continuously** from M6 on.

## The strong landing spot (definition of done)

Reached at the end of **M7**: Warden is installed and firing; a large fraction of SKA facets/skills/disciplines/operations are authored as Warden rules that fire at their moments; the test regime is green. **M8 (efficiency, incl. Rust) is a follow-on** — it makes the landed system fast, it is not part of being landed.

## Milestones

### M1 — Language completion & freeze

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

Implement the Python engine against the triple-validated spec: the full resolve → compile → install → fire loop ([[F212 — Python reference implementation|F212]]), then fold today's bespoke hook surfaces (`compact`, `markdown-write`, `audit-q`) onto it. Tests (M3) run green continuously.

**Done-when:** a real rule, authored in Warden, compiles, installs, and fires at its moment in a live session; the migrated surfaces behave unchanged; the regime is green.

### M7 — Dogfood on SKA  *(the acceptance test — strong landing here)*

Actually **use** Warden: codify a large fraction of SKA facets / skills / disciplines / operations as Warden rules and watch them fire. The corpus migrated at M4 becomes live, adopted, firing rulesets. Run it for real, Rust out.

**Done-when:** a large fraction of SKA's conventions are enforced by live Warden rules; authoring a new rule is a routine, low-friction act; the system has run in daily use without correctness regressions.

### M8 — Performance & efficiency (incl. Rust)  *(follow-on)*

Everything efficiency-oriented, parked behind a system that already works and has earned its keep: the Rust hot-path implementation ([[F213 — Rust performance implementation + ms budget|F213]]), perf hardening + budget enforcement, the re-evaluation economy build ([[F215 — Re-evaluation economy — the significant-edit gate|F215]]), and semantic-update levels. The Rust impl is **behavior-identical** to the Python reference — the M3 differential harness is the oracle, zero verdict/steer divergence.

**Done-when:** fire-time p99 meets the per-moment budget; differential tests show zero divergence; the efficiency gates are enforced.

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

1. **Repo home for the implementations.** Python ref (+ later Rust) — new code anchor under SKA, or alongside the audit scripts? (Affects `.anchor` + build wiring.) Resolve in M2.
2. **Migration ordering (M6 surface fold).** Which existing surface ports first — `audit-q` (smallest, already `when::`) is the natural pilot.
3. **Budget-enforcement policy (M8).** Advisory logging vs. hard demote-to-audit for over-budget rules (also [[Warden PRD]] Q3).
