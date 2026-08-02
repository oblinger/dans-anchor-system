# RULESET R-dot-anchor
include::
where:: `file: **/.anchor`
description:: the `.anchor` file — anchor metadata declaration

### RULE R-dot-anchor-01 — `.anchor` is valid YAML; every field is optional (checked)
The `.anchor` file parses as YAML. **No key is required** — presence alone is the declaration. `slug` in particular is optional: an anchor without one is addressed by its **basename**, which [[ANC Standard]] defines as the anchor's durable identity, and consumers needing a guaranteed handle use the **implied slug** (explicit slug when declared, otherwise the basename verbatim).
**Check pattern:** the file loads as YAML. Do not assert any key's presence.
**Why:** this rule previously required a non-empty `slug`, on the reasoning that "without a slug the anchor cannot be referenced." That reasoning is false in this system, measured 2026-08-02 (T068): DAS's own `_anchor_name` already falls back to the folder name when `slug:` is absent — ANC's implied slug, arrived at independently — and every `where:: {slug}` selector resolves through it. The corpus never obeyed the strict rule either: **1,147 of 1,332 `.anchor` files, 86%, declare no `slug`.** A requirement contradicted by the tooling and by six anchors in seven was drift, not strictness.

**Note the live tension this does NOT resolve.** [[R-anchor-page]]-01 is wired `check:: anchor_has slug traits` and still fails an anchor page whose `.anchor` omits either — roughly **1,093 anchors**. That rule is deliberately left alone here: it is an anchor-page rule, its blast radius is the anchor-page corpus, and the anchor-page format is under an explicit user hold (SKA F217) pending a working session. Reconciling it belongs to that session, not to this one.

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (stated)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[DAS Traits]], `code` → [[DAS Code Repository]], `parents` → [[DAS anchor-dag]], `slug`/naming → [[DAS Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.
