#!/usr/bin/env python3
"""T104 — `slug` is optional and inferred from the basename, per ANC Standard.

T068 measured the contradiction and left it standing, because resolving it meant
changing a LIVE anchor-page rule under a user hold. Dan called it 2026-08-02: make
slug not required and inferrable as the standard indicates.

The inference itself needed no work — `_anchor_slug` has always fallen back to the
folder name, and `_entry_page`, `chk_h1_matches_slug`, `chk_entry_page_matches_slug`
and `_ancestor_anchor_slugs` all resolve through it. That is the point worth pinning:
the requirement `R-anchor-page-01` enforced was already inferred everywhere
downstream, so the rule was asserting a field nothing actually needed.

Measured at the rule's own `where::`: **125 anchors newly pass, 1,085 still fail on
the `traits:` half, 122 were already passing.**

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


print("The rule no longer asserts slug")

RS = _S.parent.parent.parent.parent / "rulesets" / "R-anchor-page.md"
block, _ = ap.extract_ruleset_block(RS.read_text(encoding="utf-8"))
by_id = {r["id"]: r for r in ap.parse_ruleset_block(block, RS)["rules"]}
check("R-anchor-page-01 checks traits only",
      by_id["R-anchor-page-01"].get("check"), "anchor_has traits")

no_slug = anchor("Harbor", "traits: [code]\ndescription: x\n")
check("an anchor with traits but no slug passes",
      ap.chk_anchor_has(no_slug, no_slug, ["traits"]), ("pass", ""))
check("...and would have failed under the old two-field form",
      ap.chk_anchor_has(no_slug, no_slug, ["slug", "traits"]),
      ("fail", "missing in .anchor: slug"))

# The `traits:` half is deliberately untouched — it is what guards the DAS incident
# (an empty `.anchor` makes breadcrumb inference skip to the grandparent), and it
# is where 1,085 of the remaining failures live.
no_traits = anchor("Bare", "description: x\n")
check("traits is still required — the other half stands",
      ap.chk_anchor_has(no_traits, no_traits, ["traits"]),
      ("fail", "missing in .anchor: traits"))
missing = anchor("NoDot", "")
(missing / ".anchor").unlink()
check("a missing .anchor still fails outright",
      ap.chk_anchor_has(missing, missing, ["traits"]), ("fail", "no .anchor file"))

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
