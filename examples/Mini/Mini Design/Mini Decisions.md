---
description: "the OPTIONAL central Decisions file — holds only Mini's cross-cutting / value decisions; everything doc-specific lives in that doc's own ## Decisions section"
---
# Mini Decisions
include::

This is the **optional** central Decisions file. It holds only Mini's **cross-cutting / value** decisions — the ones that belong to no single design doc. Architecture-specific decisions live next to the architecture, in [[Mini Architecture#Decisions]]; a smaller anchor with no cross-cutting decisions would have **no** file here at all.

### D02 — Zero-setup: add no infrastructure (checked)

**Choice.** Mini adds nothing a user must install, run, or administer — no database, no daemon, no config server.

**Why.** Zero setup is Mini's whole reason to exist; every concrete choice serves it (e.g. the plain-text store, [[Mini Architecture#D01|D01]]). This is a **value statement** — the load-bearing *why* behind Mini's recurring choices — so it lives in the central file rather than buried in one doc.
