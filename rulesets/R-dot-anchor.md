# RULESET R-dot-anchor
include::
where:: `file: **/.anchor`
description:: the `.anchor` file — anchor metadata declaration

### RULE R-dot-anchor-01 — `.anchor` is valid YAML carrying a slug (checked)
The `.anchor` file parses as YAML and declares a non-empty `slug`.
**Check pattern:** the file loads as YAML and contains a `slug:` key with a non-empty value.
**Why:** the slug is the anchor's canonical identifier; every other field is optional, but without a slug the anchor cannot be referenced.

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (stated)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[DAS Traits]], `code` → [[DAS Code Repository]], `parents` → [[DAS anchor-dag]], `slug`/naming → [[DAS Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.
