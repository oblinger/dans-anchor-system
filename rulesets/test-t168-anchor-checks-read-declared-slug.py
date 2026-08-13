#!/usr/bin/env python3
"""test-t168-anchor-checks-read-declared-slug.py — the anchor-scoped checks
resolve `{slug}` from `.anchor`, not from the folder name.

TINK T168. Four checkers build a `{slug}`-named path and then look for it on
disk. All four read `anchor_root.name` -- the FOLDER basename -- while their own
rule text and docstrings say `{slug}`. For the 75 vault anchors whose declared
slug genuinely differs from their folder (`HA` in `Hook Anchor/`, `DKT` in
`Docket/`, `ATT` in `Atticus/`), the constructed path names nothing:

    anchor_root / "Hook Anchor Design"     <- does not exist
    anchor_root / "HA Design"              <- the real folder

and the check hits its own `if not design.is_dir(): return "pass"` guard. It
does not fail, and it does not warn. **It passes, having measured nothing** --
75 anchors silently exempted from rules the corpus believed were enforced.

Measured 2026-08-13 across the live vault, comparing the folder-reading version
against the slug-reading one: **43 anchors change verdict, and every single one
moves `pass` -> `fail`. Not one moves `fail` -> `pass`.** A bug that only ever
under-reports is a bug whose zero was a claim about the instrument.

The assertions below pin the property directly rather than through the live
corpus, so they keep holding as anchors come and go.

    python3 test-t168-anchor-checks-read-declared-slug.py
"""
import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
AUDIT = HERE.parent / "skills" / "audit" / "scripts"

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


spec = importlib.util.spec_from_file_location("audit_plan", AUDIT / "audit-plan.py")
assert spec and spec.loader
ap = importlib.util.module_from_spec(spec)
sys.modules["audit_plan"] = ap
spec.loader.exec_module(ap)

root = pathlib.Path(tempfile.mkdtemp())


def build(folder, slug, *, design_children=(), status_body=None, legacy_oq=False):
    """An anchor whose folder and slug differ, laid out under the SLUG."""
    d = root / folder
    (d / f"{slug} Design").mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(f"slug: {slug}\n", encoding="utf-8")
    (d / f"{folder}.md").write_text(f"# {folder}\n", encoding="utf-8")
    for c in design_children:
        (d / f"{slug} Design" / f"{slug} {c}.md").write_text("x\n", encoding="utf-8")
    if legacy_oq:
        (d / f"{slug} Design" / f"{slug} Open Questions.md").write_text("x\n", encoding="utf-8")
    if status_body is not None:
        track = d / f"{slug} Track"
        track.mkdir(parents=True, exist_ok=True)
        (track / f"{slug} Status.md").write_text(status_body, encoding="utf-8")
    return d


# The shape that produced the silent exemption: folder `Hook Anchor`, slug `HA`,
# every child laid out as `HA Design/` -- and a REQUIRED CHILD MISSING. A checker
# reading the folder cannot even see the folder, so it cannot see what is absent.
print("A slug-named layout is SEEN, so a genuine violation in it is reported")
d = build("Hook Anchor", "HA", design_children=["PRD"])
check("missing Design child fails (folder != slug)",
      ap.chk_design_folder_children(d, d, ["PRD", "Testing"])[0], "fail")
check("the message names the missing child",
      "Testing" in ap.chk_design_folder_children(d, d, ["PRD", "Testing"])[1], True)

d = build("Docket", "DKT", design_children=["PRD", "Testing"])
check("complete Design children pass",
      ap.chk_design_folder_children(d, d, ["PRD", "Testing"])[0], "pass")

print("\nStatus file is looked for under the slug, not the folder")
d = build("Atticus", "ATT", design_children=["PRD"])
check("absent `{slug} Track/{slug} Status.md` fails",
      ap.chk_status_facets_initialized(d, d, ["prd", "ux"])[0], "fail")
d = build("Munger", "CFO", design_children=["PRD"],
          status_body="prd:: x\nux:: y\n")
check("present Status with the facet lines passes",
      ap.chk_status_facets_initialized(d, d, ["prd", "ux"])[0], "pass")
d = build("Anchorage", "ANC", design_children=["PRD"], status_body="prd:: x\n")
check("Status missing a facet line fails",
      ap.chk_status_facets_initialized(d, d, ["prd", "ux"])[0], "fail")

print("\nThe legacy Open Questions file is found under the slug")
d = build("ClaudiMux", "CMX", legacy_oq=True)
check("legacy `{slug} Open Questions.md` fails",
      ap.chk_no_legacy_open_questions_file(d, d, [])[0], "fail")
d = build("MuxUX", "MUX")
check("no legacy file passes", ap.chk_no_legacy_open_questions_file(d, d, [])[0], "pass")

print("\nA folder-named layout is NOT mistaken for a slug-named one")
# The inverse guard. If someone lays the tree out under the FOLDER name while
# declaring a different slug, the slug-named folder genuinely does not exist and
# `pass (N/A)` is the correct answer -- the check must not silently start
# reading the folder again as a fallback. No fallback logic.
d = root / "Alien Biology Framework"
(d / "Alien Biology Framework Design").mkdir(parents=True, exist_ok=True)
(d / ".anchor").write_text("slug: ABIO\n", encoding="utf-8")
check("folder-named Design folder is N/A, not a silent folder-read",
      ap.chk_design_folder_children(d, d, ["PRD"]), ("pass", "no Design folder (N/A)"))

# RED CHECK -- without it this whole file could pass against the OLD code and
# nobody would know. Re-implement the defect and prove the assertions catch it.
print("\nRed check — the folder-reading version fails these assertions")


def folder_reading_design_children(target, anchor_root, args):
    """The pre-T168 body, verbatim in the part that matters."""
    if target.is_file():
        return "pass", "not a folder"
    design = anchor_root / f"{anchor_root.name} Design"
    if not design.is_dir():
        return "pass", "no Design folder (N/A)"
    name = anchor_root.name
    missing = [a for a in args
               if not ((design / f"{name} {a}.md").is_file()
                       or (design / f"{name} {a}").is_dir())]
    return ("fail", "missing children: " + ", ".join(missing)) if missing else ("pass", "")


d = build("Hook Anchor", "HA", design_children=["PRD"])
check("the old body returns a VACUOUS pass on the same tree",
      folder_reading_design_children(d, d, ["PRD", "Testing"]),
      ("pass", "no Design folder (N/A)"))

print(f"\nT168 anchor checks read the declared slug: "
      f"{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
