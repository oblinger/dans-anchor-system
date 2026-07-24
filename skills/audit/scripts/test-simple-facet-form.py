#!/usr/bin/env python3
"""test-simple-facet-form.py — the simple-facet-form exemption in R-progressive-03.

A slug-prefixed facet page may fuse the breadcrumb into its H1
(`# [[{slug}]] {Facet}`, {slug} = the filename prefix) and lead with its essence
(a list / table / figure) instead of an orientation line. `doc_head_orientation_line`
recognizes that head and waives the orientation-line requirement — WITHOUT relaxing
it for ordinary docs (whose H1 is not a filename-prefix wiki-link).

    python3 test-simple-facet-form.py
"""
import importlib.util
import pathlib
import sys
import tempfile

S = (pathlib.Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def verdict(filename, body):
    d = pathlib.Path(tempfile.mkdtemp())
    f = d / filename
    f.write_text(body, encoding="utf-8")
    status, _ = ap.chk_doc_head_orientation_line(f, f.parent, [])
    return status


print("Simple facet form is exempt (fused-breadcrumb H1, essence follows directly)")

# 1. list essence directly under a fused-breadcrumb H1 → waived
check("checklist essence under `# [[26OMNI]] Plan`",
      verdict("26OMNI Plan.md", "---\ndescription: x\n---\n# [[26OMNI]] Plan\n\n- [ ] do the thing\n"), "pass")

# 2. table essence → waived
check("table essence under a fused-breadcrumb H1",
      verdict("APP Roster.md", "# [[APP]] Roster\n\n| a | b |\n| --- | --- |\n"), "pass")

# 3. aliased slug link still matches the filename prefix
check("aliased `# [[26OMNI|OMNI]] Plan` still matches prefix",
      verdict("26OMNI Plan.md", "# [[26OMNI|OMNI]] Plan\n\n- [ ] x\n"), "pass")

print("The exemption does NOT over-relax")

# 4. H1 wiki-link target != filename prefix → not a simple facet head → still required
check("wiki-link target unequal to filename prefix is NOT exempt",
      verdict("26OMNI Plan.md", "# [[Something Else]] Plan\n\n- [ ] x\n"), "fail")

# 5. an ordinary doc (plain H1) with a list directly under still fails
check("ordinary doc, list under a plain H1, still requires orientation",
      verdict("Some Note.md", "# Some Note\n\n- item one\n- item two\n"), "fail")

# 6. a bare `# [[26OMNI]]` with no facet name is not the form (needs `{Facet}` after)
check("H1 wiki-link with no trailing facet name is not exempt",
      verdict("26OMNI.md", "# [[26OMNI]]\n\n- [ ] x\n"), "fail")

print("Ordinary head shapes are unaffected")

# 7. a normal doc WITH an orientation line still passes
check("plain H1 + orientation line passes (unchanged)",
      verdict("Some Note.md", "# Some Note\nOne sentence saying what this is.\n\n- item\n"), "pass")

print("Ruleset spec heads are exempt (T051 — machine-read `# RULESET` head, not the orientation form)")

# 8. a `# RULESET` head with a VALUELESS `include::` field (the exact R-facet-spec
#    shape) must NOT misfire — pre-T051 the valueless field wasn't skipped, so
#    `include::` was read as the orientation line and `where::` as a wrapped 2nd line.
check("`# RULESET` head with valueless `include::` is exempt",
      verdict("R-facet-spec.md",
              "# RULESET R-facet-spec\ninclude::\nwhere:: `file: DAS *.md`\n"
              "description:: authoring a facet\n\nProse body follows.\n"), "pass")

# 9. an ordinary doc that merely mentions RULESET in its H1 text (not the `# RULESET`
#    head form) is still governed normally — the skip keys on the leading token only.
check("`# Ruleset notes` (ordinary H1) still requires orientation",
      verdict("Ruleset notes.md", "# Ruleset notes\n\n- a\n- b\n"), "fail")

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
