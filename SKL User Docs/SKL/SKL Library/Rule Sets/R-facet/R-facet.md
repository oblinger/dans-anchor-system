# RULESET R-facet
description:: Umbrella rule set aggregating the per-facet rule sets that live inside CAB facet spec files (CAB Backlog → R-backlog, CAB Decisions → R-decisions, CAB Rules → R-rules, etc.). An anchor that adopts R-facet commits to following every CAB facet's structural rules.
includes::

> [!info] How this set is wired
> Per the 2026-06-09 design decision, each CAB facet spec file (`CAB <facet>.md`) contains a `# RULESET R-<facet>` second-H1 block with the facet's structural rules — co-located with the prose that explains the facet. This file is the catalog-side umbrella that walks all those embedded rule sets via `includes::` so adopters get a single name to pull.
>
> The `includes::` line is empty for now — the embedded rule sets don't yet exist in the CAB facet files. As each facet's RULESET block lands (starting with [[CAB Rules]] as the first worked example), its name is appended to `includes::` above.

## Adoption

```markdown
# {NAME} Decisions
include:: [[R-facet]]
```

This single include pulls in every CAB facet's structural rules. Audit walks the included sets and verifies the anchor's facet files satisfy them. Use cases:

- A new anchor that wants to be CAB-conformant: one-liner adoption.
- An audit pass that checks every facet file's structure in one walk.
- Cherry-pick override: include `R-facet` AND override individual facet rules in the anchor's `{NAME} Rules.md`.

## See also

- [[CAB Rules]] — meta-spec for the RULESET format; first facet expected to land an embedded `R-rules` block.
- [[CAB Decisions]] — the master adoption file in an anchor; this is where `include:: [[R-facet]]` belongs.
- [[Rule Sets]] — parent catalog.
