#!/usr/bin/env python3
"""T104 / T105 — `R-anchor-page-01` asserts no `.anchor` field; both were wrong.

T068 measured the `slug:` contradiction and left it standing, because resolving it
meant changing a LIVE anchor-page rule under a user hold. Dan called it 2026-08-02
(T104): slug not required, inferred as the standard indicates. Told that this cleared
only 125 of ~1,210 failures because the rest were the `traits:` half, he made the
second call in the same sitting (T105): traits was never meant to be required either.

He is right on the documents — [[ANC Standard]] § Standard fields says "none is
required … an empty `.anchor` … is already a complete anchor" and gives `traits` the
default `[simple]`; [[DAS Dot Anchor]] says "every key is optional". And the
justification written into the rule for keeping `traits:` — that an empty `.anchor`
makes breadcrumb inference skip to the grandparent — was mis-transcribed from the
audit-anchor checklist, where the incident is attached to **`slug:`**. It also does
not reproduce: 720 `.anchor` files in the live vault are zero-byte, and 182 of the
232 child docs beneath them name their empty anchor in the breadcrumb correctly.

So the rule now asserts nothing. What survives is the CONDITIONAL shape, which was
always the right one: `R-code-repository-01` asserts `code:` only when `traits:`
already declares the code trait. Absence of a field is a default, not a defect.

    python3 test-t104-slug-optional.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def anchor(name, dotfile):
    d = ROOT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(dotfile, encoding="utf-8")
    return d


print("The rule asserts neither field — it asserts nothing at all")

RS = _S.parent.parent.parent.parent / "rulesets" / "R-anchor-page.md"
block, _ = ap.extract_ruleset_block(RS.read_text(encoding="utf-8"))
by_id = {r["id"]: r for r in ap.parse_ruleset_block(block, RS)["rules"]}
check("R-anchor-page-01 carries no check:: at all",
      by_id["R-anchor-page-01"].get("check"), None)
# The checker itself stays — R-code-repository-01 uses it in the CONDITIONAL shape
# that is correct: assert `code:` only when `traits:` already declares the code trait.
check("...and is marked stated, not checked",
      by_id["R-anchor-page-01"]["tier"], "stated")

no_slug = anchor("Harbor", "traits: [code]\ndescription: x\n")
check("the old two-field form would have failed this anchor on slug",
      ap.chk_anchor_has(no_slug, no_slug, ["slug", "traits"]),
      ("fail", "missing in .anchor: slug"))
# T105: `traits:` went the same way as `slug:`. Both ANC Standard and DAS Dot Anchor
# say no field is required; 1,085 of 1,332 `.anchor` files declare no traits, and the
# breadcrumb-inference incident cited to justify it was mis-transcribed from the
# audit-anchor checklist, where it is attached to `slug:` — and does not reproduce.
no_traits = anchor("Bare", "description: x\n")
check("...and this one on traits — neither is asserted now",
      ap.chk_anchor_has(no_traits, no_traits, ["traits"]),
      ("fail", "missing in .anchor: traits"))
check("an empty .anchor is a complete anchor — ANC § Standard fields",
      ap._anchor_slug(anchor("Hollow", "")), "Hollow")

print("\nThe implied slug — explicit when declared, else the basename verbatim")

check("declared slug wins", ap._anchor_slug(anchor("Docket", "slug: DKT\n")), "DKT")
check("absent slug falls back to the basename", ap._anchor_slug(no_slug), "Harbor")
check("a quoted slug is unquoted",
      ap._anchor_slug(anchor("Quoted", 'slug: "QTD"\n')), "QTD")
# ANC is explicit that the implied slug is COMPUTED, never written back — the
# fallback must not tempt anyone into materialising it into the file.
check("the fallback does not write anything into .anchor",
      (no_slug / ".anchor").read_text(encoding="utf-8"),
      "traits: [code]\ndescription: x\n")

print("\nEverything downstream already resolved through the implied slug")

# This is the load-bearing claim behind dropping the requirement: nothing needed
# the explicit field, so nothing breaks when it is absent.
(no_slug / "Harbor.md").write_text("# Harbor\n\nOrientation.\n", encoding="utf-8")
check("the entry page resolves by basename when no slug is declared",
      ap._entry_page(no_slug).name, "Harbor.md")
check("...so the entry-page rule passes",
      ap.chk_entry_page_matches_slug(no_slug, no_slug, "")[0], "pass")
check("...and the H1 rule matches against the inferred slug",
      ap.chk_h1_matches_slug(no_slug, no_slug, ""), ("pass", "bare-name: Harbor"))
# A declared slug must still be honoured over the basename, or "inferred" would
# have quietly become "always the folder name".
d = anchor("Docket2", "slug: DK2\ntraits: [code]\n")
(d / "DK2.md").write_text("# DK2 - Docket Two\n\nOrientation.\n", encoding="utf-8")
check("a declared slug still takes precedence for the entry page",
      ap._entry_page(d).name, "DK2.md")
check("...and for the H1",
      ap.chk_h1_matches_slug(d, d, "")[0], "pass")
check("file-naming sees both the inferred slug and the basename",
      sorted(set(ap._ancestor_anchor_slugs(no_slug)) & {"Harbor"}), ["Harbor"])

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
