# RULESET R-one-path
include::
description:: For each operation there is exactly one current implementation path; superseded code is deleted, never parallel-maintained.

Recurs in HA + MUX + the global CLAUDE.md (no-legacy-accumulation). HA P06: "When a better approach replaces an older one, the older one is deleted entirely — not kept 'just in case,' not wrapped with a feature flag, not aliased for backward compatibility." MUX Multi-Path Audit: "`cmd_layout_load()` and `cmd_layout_apply()` are functionally identical … if a bug is fixed in one, the other will be missed."

### RULE R-one-path-01 — Exactly one current implementation path per operation (sampled)

For a sampled operation, trace how it can be invoked end-to-end. Two live code paths producing the same effect (old + new, flagged variants, aliased entry points kept for back-compat) is a violation: consolidate onto one and delete the other.

### RULE R-one-path-02 — Replaced code is deleted, not deprecated-in-place (checked)

**Check pattern:** search for `deprecated`, `legacy`, `_old`, `_v2`, `# TODO: remove`, dead feature flags. Each hit is a violation unless it carries a dated removal plan; "kept just in case" is not a justification — git history is the just-in-case.

### RULE R-one-path-03 — Near-duplicate logic consolidates behind one helper (sampled)

Two functions whose bodies differ only in a parameterizable detail merge into one shared helper. The test is the bug-fix test: if fixing a bug in one would require remembering to fix the other, they are one function written twice.
