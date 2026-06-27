---
description: CAE Decisions Details — companion to `CAE Decisions.md`. Why / rationale / examples / tests / source-provenance per D-number. Optional: only present when there's detail worth recording.
---

# CAE Decisions Details

> Companion to [[CAE Decisions]]. Each H2 below mirrors a D-entry in the canonical list and carries its rationale + supplementary detail. Decisions.md is the operational reference; this file is the contextual depth.

## D01

**Why:** parallel scheduling paths diverge under load and make starvation invisible. A single queue and a single time source give one place to reason about priority, fairness, and test determinism.

## D02

**Why:** silent fallbacks mask broken production. We want failure to surface in dev, not after deployment.

## D03

**Why:** flaky tests destroy trust. A test that depends on `sleep()` will eventually fail on a slow machine.

## D04

**Rationale:** Obsidian has a flat namespace across the vault. Unprefixed names collide with other anchors.
