#!/usr/bin/env python3
"""test-simple-facet-form.py — the simple-facet-form exemption in R-spine-02.

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
check("checklist essence under `# [[26ACME]] Plan`",
      verdict("26ACME Plan.md", "---\ndescription: x\n---\n# [[26ACME]] Plan\n\n- [ ] do the thing\n"), "pass")

# 2. table essence → waived
check("table essence under a fused-breadcrumb H1",
      verdict("APP Roster.md", "# [[APP]] Roster\n\n| a | b |\n| --- | --- |\n"), "pass")

# 3. aliased slug link still matches the filename prefix
check("aliased `# [[26ACME|OMNI]] Plan` still matches prefix",
      verdict("26ACME Plan.md", "# [[26ACME|OMNI]] Plan\n\n- [ ] x\n"), "pass")

print("The exemption does NOT over-relax")

# 4. H1 wiki-link target != filename prefix → not a simple facet head → still required
check("wiki-link target unequal to filename prefix is NOT exempt",
      verdict("26ACME Plan.md", "# [[Something Else]] Plan\n\n- [ ] x\n"), "fail")

# 5. an ordinary doc (plain H1) with a list directly under still fails
check("ordinary doc, list under a plain H1, still requires orientation",
      verdict("Some Note.md", "# Some Note\n\n- item one\n- item two\n"), "fail")

# 6. a bare `# [[26ACME]]` with no facet name is not the form (needs `{Facet}` after)
check("H1 wiki-link with no trailing facet name is not exempt",
      verdict("26ACME.md", "# [[26ACME]]\n\n- [ ] x\n"), "fail")

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

# --------------------------------------------------------------------------
# T092 — an indented H1 is still an H1
#
# CommonMark allows an ATX heading up to THREE leading spaces; four makes it an
# indented code block. Obsidian renders ` # SRC` as an H1 accordingly. The head
# scan used to require column 0, so an indented head was SKIPPED and the scan
# walked on to the file's next `# ` — in practice the `# BRIEF` section every
# anchor page carries — and blamed that line for the missing orientation line.
#
# The wrong LINE NUMBER is the damage, not the wrong verdict: the finding points
# at a heading that is not the problem, so the obvious remediation is to add a
# second H1 with an orientation line above BRIEF. That is exactly what happened
# to `Topic/Search/SRC.md` on 2026-08-01 — a page whose real head was correct.
# Hence the message assertions below, not just pass/fail.

def message(filename, body):
    d = pathlib.Path(tempfile.mkdtemp())
    f = d / filename
    f.write_text(body, encoding="utf-8")
    return ap.chk_doc_head_orientation_line(f, f.parent, [])[1]


print("Indented H1 (0-3 leading spaces) is recognized as the head (T092)")

# 10-12. one, two and three leading spaces are all valid ATX heads
for n in (1, 2, 3):
    check(f"{n}-space-indented H1 + orientation line passes",
          verdict("SRC.md", f"{' ' * n}# SRC\nWhat this file is.\n\n## Body\n"), "pass")

# 13. THE REGRESSION: the SRC.md shape — indented head, correct orientation line,
#     and a later column-0 `# BRIEF`. Pre-T092 this failed and named BRIEF's line.
SRC_SHAPE = (":>> [[kmr]] → [[Topic]] → [[SRC]]\n"
             " # SRC\n"
             "The search anchor.\n"
             "\n"
             "# BRIEF\n"
             "\n"
             "- agent-facing note\n")
check("indented head + correct orientation + later `# BRIEF` passes",
      verdict("SRC.md", SRC_SHAPE), "pass")

# 14. and when it DOES fail, it must blame the indented head's own line (2), never
#     the later `# BRIEF` (line 5) — the misdirection T092 was filed for.
BAD_SHAPE = (":>> [[kmr]] → [[Topic]] → [[SRC]]\n"
             " # SRC\n"
             "\n"
             "- straight to a list, no orientation line\n"
             "\n"
             "# BRIEF\n"
             "\n"
             "- agent-facing note\n")
check("failure names the indented head's line, not the later `# BRIEF`",
      "line 2" in message("SRC.md", BAD_SHAPE), True)
check("failure does NOT name the `# BRIEF` line",
      "line 6" in message("SRC.md", BAD_SHAPE), False)

print("The relaxation does not over-reach")

# 15. FOUR spaces is an indented code block per CommonMark, not a heading — a doc
#     whose only `# ` is 4-indented has no head at all and stays out of scope.
check("4-space-indented `# ` is a code block, not an H1 (out of scope)",
      verdict("Note.md", "Some prose.\n\n    # not a heading\n"), "pass")

# 16. a `# ` inside a fence is still ignored, indented or not
check("indented `# ` inside a fence is not read as the head",
      verdict("Note.md", "# Note\nWhat this is.\n\n```python\n  # a comment\n```\n"), "pass")

# 17-18. the two head-shape exemptions key off the DE-INDENTED H1 text, so an
#     indented ruleset / simple-facet head stays exempt rather than being newly
#     selected by the relaxed scan and then failing for want of an orientation line.
check("indented `# RULESET` head is still exempt",
      verdict("R-x.md", " # RULESET R-x\nwhere:: `always`\n\nProse body.\n"), "pass")
check("indented simple-facet head is still exempt",
      verdict("26ACME Plan.md", "  # [[26ACME]] Plan\n\n- [ ] x\n"), "pass")

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
