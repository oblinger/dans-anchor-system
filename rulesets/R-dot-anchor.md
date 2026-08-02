# RULESET R-dot-anchor
include::
where:: `file: **/.anchor`
description:: the `.anchor` file — anchor metadata declaration

### RULE R-dot-anchor-01 — `.anchor` is valid YAML; every field is optional (checked)
The `.anchor` file parses as YAML. **No key is required** — presence alone is the declaration. `slug` in particular is optional: an anchor without one is addressed by its **basename**, which [[ANC Standard]] defines as the anchor's durable identity, and consumers needing a guaranteed handle use the **implied slug** (explicit slug when declared, otherwise the basename verbatim).
**Check pattern:** the file loads as YAML. Do not assert any key's presence.
**Why:** this rule previously required a non-empty `slug`, on the reasoning that "without a slug the anchor cannot be referenced." That reasoning is false in this system, measured 2026-08-02 (T068): DAS's own `_anchor_name` already falls back to the folder name when `slug:` is absent — ANC's implied slug, arrived at independently — and every `where:: {slug}` selector resolves through it. The corpus never obeyed the strict rule either: **1,147 of 1,332 `.anchor` files, 86%, declare no `slug`.** A requirement contradicted by the tooling and by six anchors in seven was drift, not strictness.

**The live rule was reconciled too** (2026-08-02, T104). [[R-anchor-page]]-01 was wired `check:: anchor_has slug traits`; on the user's call it is now `anchor_has traits`, so the two specs and the enforcement all agree. Measured at that rule's own `where::`: **125 anchors newly pass, 1,085 still fail on the `traits:` half, 122 already passed.** The `traits:` requirement is deliberately untouched — it is what guards the breadcrumb-inference incident the rule was written for, and it is a separate question.

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (stated)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[DAS Traits]], `code` → [[DAS Code Repository]], `parents` → [[DAS anchor-dag]], `slug`/naming → [[DAS Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.
