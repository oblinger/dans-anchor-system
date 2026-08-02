# RULESET R-dot-anchor
include::
where:: `file: **/.anchor`
description:: the `.anchor` file — anchor metadata declaration

### RULE R-dot-anchor-01 — `.anchor` is valid YAML; every field is optional (checked)
The `.anchor` file parses as YAML. **No key is required** — presence alone is the declaration. `slug` in particular is optional: an anchor without one is addressed by its **basename**, which [[ANC Standard]] defines as the anchor's durable identity, and consumers needing a guaranteed handle use the **implied slug** (explicit slug when declared, otherwise the basename verbatim).
**Check pattern:** the file loads as YAML. Do not assert any key's presence.
**Why:** this rule previously required a non-empty `slug`, on the reasoning that "without a slug the anchor cannot be referenced." That reasoning is false in this system, measured 2026-08-02 (T068): DAS's own `_anchor_name` already falls back to the folder name when `slug:` is absent — ANC's implied slug, arrived at independently — and every `where:: {slug}` selector resolves through it. The corpus never obeyed the strict rule either: **1,147 of 1,332 `.anchor` files, 86%, declare no `slug`.** A requirement contradicted by the tooling and by six anchors in seven was drift, not strictness.

**The live rule was reconciled too, in both halves** (2026-08-02). [[R-anchor-page]]-01 was wired `check:: anchor_has slug traits`. T104 dropped `slug:` on the user's call, clearing 125 of that rule's 1,210 failures; told the remaining 1,085 were the `traits:` half, he made the second call in the same sitting (T105) — **`traits:` was never intended to be required either**, and the rule now asserts nothing. The two specs and the enforcement finally agree with each other, and with this rule's own *every field is optional* heading.

The discarded `traits:` justification is worth recording, because it was wrong in an instructive way: it claimed an empty `.anchor` makes breadcrumb inference skip to the grandparent. That incident is real, but the [[audit-anchor]] checklist attaches it to **`slug:`** — the sentence was mis-transcribed onto the wrong field. It also fails to reproduce: **720 `.anchor` files in the live vault are zero-byte**, and of the 232 child docs beneath them carrying a breadcrumb, **182 name their empty anchor correctly** (the other 50 are hand-written short trails like `:>> [[SVAR]]`, not inference dropping a level).

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (stated)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[DAS Traits]], `code` → [[DAS Code Repository]], `parents` → [[DAS anchor-dag]], `slug`/naming → [[DAS Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.
