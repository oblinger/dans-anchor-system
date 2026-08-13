# RULESET R-dot-anchor
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: the `.anchor` file — anchor metadata declaration

> **Armed 2026-08-11 ([[TINK Backlog#^T212|T212]]) — the selector was the whole blocker, and the fix cost one judgment per anchor.**
>
> It read `where:: file: **/.anchor`, which matches nothing: anchor-mode scope is built from `rglob("*.md")`, so a `file:` term naming any non-`.md` path resolves empty and the set drops out of the plan with no warning. `.anchor` is reachable only through `where:: anchor`, whose synthetic target is the anchor root — which is what `chk_slug_is_a_handle` reads anyway, ignoring `target` entirely.
>
> **The price, measured on TINK: 988 judgment items before, 989 after — one.** `-02` was retiered `(stated)` → `(governing)`, the tier admitted for exactly this shape: it says where its siblings' rules live and makes no claim about any target, so `_needs_judgment` excludes it. `-01` was demoted `(checked)` → `(stated)` — it has no `check::` and there is no YAML-validity checker registered — and its one judgment per anchor is honest rather than wasted, unlike [[R-mac]]'s: *is this anchor's `.anchor` valid YAML* is a real question about all 1,395 of them, where *does this documentation anchor ad-hoc-sign its `.app`* is N/A by construction.
>
> **`-03` earns the arming on its own.** Run across the vault the moment the selector was fixed: of **1,395** `.anchor` files, **98** declare a `slug:` and **16** of those fail — `SYS Track`, `Career Track`, `Admin`, `Self`, and the whole `LST/HUD` family, each declaring a multi-word phrase where the grammar wants one uppercase token, plus `LST/HUD` restating its own basename. Sixteen findings that had been sitting behind an unmatchable glob.

### RULE R-dot-anchor-01 — `.anchor` is valid YAML; every field is optional (stated)
The `.anchor` file parses as YAML. **No key is required** — presence alone is the declaration. `slug` in particular is optional: an anchor without one is addressed by its **basename**, which [[ANC Standard]] defines as the anchor's durable identity, and consumers needing a guaranteed handle use the **implied slug** (explicit slug when declared, otherwise the basename verbatim).
**Check pattern:** the file loads as YAML. Do not assert any key's presence.
**Why:** this rule previously required a non-empty `slug`, on the reasoning that "without a slug the anchor cannot be referenced." That reasoning is false in this system, measured 2026-08-02 (T068): DAS's own `_anchor_name` already falls back to the folder name when `slug:` is absent — ANC's implied slug, arrived at independently — and every `where:: {slug}` selector resolves through it. The corpus never obeyed the strict rule either: **1,147 of 1,332 `.anchor` files, 86%, declare no `slug`.** A requirement contradicted by the tooling and by six anchors in seven was drift, not strictness.

**The live rule was reconciled too, in both halves** (2026-08-02). [[R-anchor-page]]-01 was wired `check:: anchor_has slug traits`. T104 dropped `slug:` on the user's call, clearing 125 of that rule's 1,210 failures; told the remaining 1,085 were the `traits:` half, he made the second call in the same sitting (T105) — **`traits:` was never intended to be required either**, and the rule now asserts nothing. The two specs and the enforcement finally agree with each other, and with this rule's own *every field is optional* heading.

The discarded `traits:` justification is worth recording, because it was wrong in an instructive way: it claimed an empty `.anchor` makes breadcrumb inference skip to the grandparent. That incident is real, but the [[audit-anchor]] checklist attaches it to **`slug:`** — the sentence was mis-transcribed onto the wrong field. It also fails to reproduce: **720 `.anchor` files in the live vault are zero-byte**, and of the 232 child docs beneath them carrying a breadcrumb, **182 name their empty anchor correctly** (the other 50 are hand-written short trails like `:>> [[SVAR]]`, not inference dropping a level).

### RULE R-dot-anchor-03 — A declared slug is all capitals unless it is the name, and never a restatement (checked)
check:: slug_is_a_handle

A `slug:` in `.anchor` takes **one of two forms**, and nothing else:

- **a shortening** — `^[A-Z0-9]+$`, one token, uppercase alphanumeric, no spaces (`WARD`, `TINK`, `WEB`). This is the ordinary case. A leading digit is legal: [[ANC Standard]] § Anchor retirement retires a slug in place by prefixing its two-digit creation year (`SKD` → `25SKD`), so `^[A-Z][A-Z0-9]*$` would condemn every retired slug.
- **the name itself** — the anchor's own name, carried in **the name's own case** (`Warden`). Legal when the name is already short enough to serve, and never upcased when it is.

Dan ruled the two-form grammar 2026-08-13 ([[TINK Backlog#^T150|T150]]). Declaring a slug declares that it **can be used as a prefix to differentiate things** — that is what a slug means, 100% of the time — and *by convention* it is also a shorthand: fewer characters, easier to type, and it keeps filenames from growing. But occasionally the original name is good enough to be the slug, and then the one thing that must not happen is **two different casings of the same word in circulation**. So `WARD` and `Warden` are both legal for the Warden anchor, and whichever is declared is the only spelling that appears.

**"The name" is the anchor page's title, not the folder.** They differ in case more often than they look like they would: Warden is folder `warden/` — lowercase to sit beside its `rs/` and `engine/` siblings, a repo-path convention rather than a display name — while the page is `Warden.md` and every prose reference is `[[Warden]]`. A prefix has to be visually right next to the name a reader knows.

A declaration is a **statement of intent**, in one of two forms — either is sufficient:

- **prefix intent** — files inside the anchor lead with it (`TINK Backlog.md`);
- **moniker intent** — it is the short form typed to refer to or navigate to the anchor (`WEB` for `Website`), even with nothing prefixed.

Moniker intent survives the two-form grammar unchanged. "A slug can be used as a prefix" is a **capability**, not a requirement — a slug declared purely for typing and navigation, with nothing prefixed at all, is still a slug.

A **restatement** is never a slug: a value **byte-identical to the folder basename** says nothing the basename did not already say, and the *implied* slug computes to the same value once it is gone. The test is against the folder specifically, because the folder is what the implied slug is computed from — a slug equal to the anchor **page's** name but not the folder's (`Warden` over `warden/`) is doing real work and stays. The implied slug is unconstrained by this rule — it is a basename, and basenames are long and sentence-cased on purpose.

**Check pattern:** for each `.anchor` declaring `slug`, assert it either matches `^[A-Z0-9]+$` or equals the anchor page's stem, and is not byte-identical to the folder basename. **No staff-roster exemption is needed** — the one [[TINK301 - Slug is a prefix identifier, basename is the semantic name|TINK F301]] wrote for `ASH`/`Ash` and `TINK`/`Tink` was subsumed the moment case-differing values stopped counting as restatements; those are ordinary shortenings under the first form. Deleting it removed a clause, not a protection.

**Why:** the slug exists to be visually separable from the name it prefixes, which uppercase achieves and a title-case multi-word string does not. Measured 2026-08-03 before this rule existed: **116 of 186 declarations were restatements** and 76 were not single tokens — including `2026-03-18 AI Model Pricing`, a perfectly good *basename* that was never a slug. Without a stated grammar the field silently became a second copy of the folder name, and `{slug}` interpolation in `where::` selectors inherited the confusion ([[TINK Backlog#^T111|T111]]).

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (governing)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[DAS Traits]], `code` → [[DAS Code Repository]], `parents` → [[DAS anchor-dag]], `slug`/naming → [[DAS Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.
