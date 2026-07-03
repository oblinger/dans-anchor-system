---
description: "F221 — Live-integration test class — drive a real agent through a moment and prove the hook fired, end to end"
---

# [[Warden]] · F221 — Live-integration test class

## Summary

The **end-to-end / live** test layer [[F214 — Rule-system testing regime|F214]] names but leaves un-built: prove a rule **actually fires in a live Claude Code session**, not just in-process. The failure the user predicts is that *the live integrations are what break* — the engine can be perfect and the `settings.json` wiring, the event JSON shape, the anchor resolution, or the steer-injection path can still be wrong. This layer catches exactly that: a **test ruleset** (`R-warden-selftest`) whose rules fire on easily-triggered moments and **write a marker to a log**, activated by a dedicated **`warden-selftest` trait**; a test anchor adopts the trait; a **real agent is driven** (the Task/subagent tool, or a headless `claude` invocation, or the user's own ask agent) through the triggering moment; then the harness **reads the log** and asserts the marker landed — the rule fired live.

User directive 2026-07-02: *"we want to make sure that we have very, very, very strong testing of all different categories, including all the way end to end, live hook testing… I bet it's gonna be the live integrations that break… create a whole class of test rules in a test ruleset… a funky trait that we can give ask just to verify that these rules are triggering as they should."*

## Success Criteria

**Tier:** 3 (live-environment verification — the thing that proves go-live worked)
**Blocks next:** dogfooding the real SKA rulesets (M7)

**What done looks like.** A repeatable harness that: (1) stands up a scratch anchor with the `warden-selftest` trait; (2) drives a **real agent** to perform each piloted moment (write a file → `tool:post:Write` / `write:markdown`; run a skill → `skill:pre`; submit a prompt → `prompt:submit`; etc.); (3) reads `~/.warden/selftest.log` and asserts each expected marker fired, with the right moment + anchor; (4) flips `warden off` and re-runs, asserting **no** markers (the kill switch works live). One marker per piloted moment class — the coverage goal is ≥1 live-fired case per registered event.

**How it will be verified.** The harness is a `just`/script recipe that returns PASS/FAIL mechanically (per the dev discipline — an automated e2e test, not a manual reproduction). It runs the drive-agent-and-check-log loop for every selftest rule and diffs the log against the expected marker set. Green = the live integration works end to end.

## Design

- **The selftest ruleset (`R-warden-selftest`).** One when-rule per piloted moment, each body appending a structured line to `~/.warden/selftest.log`: `{ts, moment, anchor, rule, marker}`. Deliberately side-effecting (a log write) so firing is observable from outside the session. Lives in a spec doc under the corpus so it is never active except where the trait is adopted.

- **The `warden-selftest` trait.** A dedicated trait whose `include::` pulls in `R-warden-selftest`. Only an anchor that declares `traits: [warden-selftest]` activates these rules — so the selftest surface is inert everywhere else (active-set gating, F211). The "funky trait we can give ask": drop it into a scratch anchor's `.anchor`, and any agent operating there fires the selftest rules.

- **Driving a real agent.** Three drive modes, cheapest-first: (a) **in-process subagent** — spawn a Task/subagent told to write a file / run a skill in the scratch anchor; (b) **headless `claude`** — `claude -p "<action>"` in the scratch anchor for a fully out-of-process session; (c) **the user's ask agent** — the user (or a bridged agent) types the action at a real prompt. All three converge on the same assertion: the marker is in the log. The harness prefers (a)/(b) for CI; (c) is the manual confirmation the user described.

- **Reading back the proof.** The harness tails `~/.warden/selftest.log`, filters to the run's timestamp window + anchor, and asserts the expected `(moment, rule)` markers are present (and, for the kill-switch case, absent). The log is the ground truth the user asked for — *"look at the log… see that it actually triggered."*

- **Kill-switch coverage.** Every live case runs twice — once `warden on` (marker expected), once `warden off` (marker forbidden) — so the disable is proven live, not just unit-tested.

## Status

**Designed 2026-07-02** — rides [[F220 — Live hook install + kill switch|F220]] (needs the live dispatcher + selftest trait wired). Extends [[F214 — Rule-system testing regime|F214]]'s end-to-end layer from "named" to "built."

## Open questions

1. **CI vs. local for the drive-a-real-agent loop.** Headless `claude` in GitHub Actions needs auth/secrets; the in-process subagent path may be the CI-runnable form while headless is local-only. Decide once the harness shape is proven locally.
