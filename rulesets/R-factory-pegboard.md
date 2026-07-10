# RULESET R-factory-pegboard
include::
description:: Instances are created through factories registered on a per-subsystem pegboard, so the architecture's wiring is visible in one place.

Commissioned in F108 and canonical in SVP F006: "concrete instances are **never constructed directly** — they're built by **factories**, which are registered on a **pegboard** (a per-subsystem registry) … Swapping an implementation … is a pegboard registration, not a code edit at the call site." SKD instantiates the same shape: "Sys is the pegboard — every module and subsystem hangs off it" (`SKD Track/SKD System Design.md`).

### RULE R-factory-pegboard-01 — Business code never constructs concretes directly (sampled)

Object instances are created through factory functions. **Check pattern:** for a sampled concrete class, search for direct constructor calls outside its factory and tests; each is a violation.

### RULE R-factory-pegboard-02 — Factories register on a per-subsystem pegboard (checked)

**Check pattern:** the subsystem has a central registry module where each architectural piece registers its factory; a factory reachable only by direct import from a call site is unregistered wiring.

### RULE R-factory-pegboard-03 — Swaps are registrations, not call-site edits (stated)

Substituting an implementation (real vs mock, backend A vs B) is a pegboard registration change. If a swap requires touching call sites, the wiring has leaked out of the pegboard.
