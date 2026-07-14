# RULESET R-fct-interface
include::
where:: `file: **/{slug} Interface.md, **/{slug} * Interface.md`
description:: The rules every `{slug} Interface.md` (and sub-Interface) must satisfy — layer-completeness, hiding discipline, required structural links, and lifecycle gates.

### RULE R-fct-interface-01 — Layer-completeness: required sections present (checked)
Every top-level Interface doc contains at minimum a brief paragraph naming the layer + what callers gain, and at least one of: `## Public Modules`, `## Schemas`, `## CLI Surface`. Sub-Interfaces follow the same rule for their own layer.
**Check pattern:** the file has a non-empty H1-summary paragraph and at least one of the listed sections.
**Why:** an Interface that omits the caller vocabulary fails its core completeness invariant — a caller cannot use the layer from it.

### RULE R-fct-interface-02 — Required link from Files.md row 1 (checked)
`{slug} Files.md` row 1 (the repo-root row) ends with `→ [[{slug} Interface]]`.
**Check pattern:** `{slug} Files.md` row 1 ends with the Interface wiki-link.
**Why:** the Files entry point must direct readers to the layer contract first; a missing link makes the Interface invisible to file-tree navigation.

### RULE R-fct-interface-03 — Required link from User/Design dispatch (checked)
`{slug} User.md` (or `{slug} Design.md` if the anchor uses the Design dispatch) lists `[[{slug} Interface]]` as a top-level entry.
**Check pattern:** the dispatch page includes a `[[{slug} Interface]]` link.
**Why:** the dispatch page is the caller's entry; an Interface not listed there cannot be discovered without knowing to search for it.

### RULE R-fct-interface-04 — Human-review gate before Done (stated)
An Interface transitions to `[Done]` only after user verification that it accurately describes the layer contract (per [[SKA workflow]] § Interface-validation gate). Auto-generated or agent-only drafts are `[Designing]` until reviewed.
**Check pattern:** status on the backlog row is not `[Done]` unless the Interface has passed user review.
**Why:** layer-completeness and correctness can only be confirmed by a caller-perspective review; agent drafts are starting points, not finished contracts.
