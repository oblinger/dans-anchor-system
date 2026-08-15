---
description: Fable spec-vs-impl + latent-bug scan of the Warden rule engine — well-tested but freshly extracted, so the corpus-resolution / config-fallback seams are the target.
---

# [[Warden]] · F234 — Fable scan — Warden engine
Adversarial Fable audit of the Warden rule engine (`~/bin/warden` → `engine/warden`; Python engine + Rust sidecar).

next:: Assess prior Fable coverage + ROI, then run the scoped scan.

## Summary

Warden is 3,687 LOC of Python across 11 `warden_*.py` modules plus a 1,483-LOC Rust `rs/` sidecar: rule compilation → firing → daemon. Unlike the SKA-side targets it is **well-tested** (73 `test_*` functions) — which makes it an ideal **spec-vs-impl** Fable target (a good test net lets Fable reason against expected behavior). The risk surface is its **youth**: freshly extracted from `dans-anchor-system` (T008) with the `warden_root` corpus-resolution decoupling and F188 mirror-route seams still fresh — exactly where path-resolution and config-fallback bugs lurk after an extraction. Part of the [[F253 — Fable multi-codebase scan campaign (roadmap)|F253 scan campaign]].

## Success Criteria

**Tier:** 1 (agent-immediate) — every reported bug ships with a concrete repro (corpus layout / config → wrong rule firing or wrong root resolution).
**Blocks next:** none.

**What done looks like.** A verified latent-bug list (hypothesis + repro), orchestrator-triaged (never trusted), confirmed bugs fixed, the rest filed.
**How verified.** Each finding's repro runs against the engine and demonstrates the defect; clean pass = no confirmed bugs in the scoped surface. The existing 73-test suite must stay green through any fix.

## Design — the scan protocol

**Shepherd FIRST:** assess prior Fable coverage (**none recorded**) and ROI. Good test net + fresh extraction seams → high ROI as a spec-vs-impl pass; proceed.

Run the Fable recipe (global `CLAUDE.md` § Fable-5 audit) with the test suite as the behavioral spec: find where the implementation diverges from what the tests imply, and adversarially construct corpus/config inputs that break root-resolution or rule-firing. Hypothesis + repro, never vague concerns. Delegate sub-exploration to a lighter model; verify (never trust).

**Scope (high-yield surface):** the `warden_root` corpus-resolution decoupling and any config/path fallback introduced by the T008 extraction; the compile → fire → daemon branches; the F188 mirror-route logic; the Python↔Rust sidecar boundary.
**Model:** Fable 5 (`claude-fable-5`).

## Status

**Ready** — spec complete, parked in Later (off the crank frontier, awaiting user greenlight to run); migrate when kicked off (see [[F253 — Fable multi-codebase scan campaign (roadmap)|F253]] — #3).

next action: assess prior Fable coverage + incremental ROI, then run the adversarial spec-vs-impl Fable scan on the scoped surface (§ Design).


**Where this stands (the row's Next, 2026-08-15):** assess prior Fable coverage + ROI, then run the scoped scan

## Resolved
