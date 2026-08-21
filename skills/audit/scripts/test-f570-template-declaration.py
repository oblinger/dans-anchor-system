#!/usr/bin/env python3
"""F570 — a template declares itself (`stencil:: V1.0`) and what it produces (`path::`).

Dan's ruling, 2026-08-20: the filename stops carrying mechanism. A declaration
below the cut-line says the file IS a stencil template and which STEN grammar it
was written against; a second declaration names the file it instantiates to. The
name goes back to being for humans, and `R-template-04` is reversed — the
constant middle it used to flag (`_Computer Template.md`) is now the recommended
form.

**§4 is the reason this file exists.** The first cut of `_CUTLINE_RE` read
`-{3,}` — ASCII hyphen only. `R-template-08` says "≥3 dashes **of any kind**",
and the canonical form the corpus actually writes is
`✂ ──── template notes ──── ✂`, whose rule is **U+2500 BOX DRAWINGS LIGHT
HORIZONTAL**. So the class matched **zero of 29** live templates — and because
a missing cut-line makes both new checkers defer to `R-template-08`, both
returned `pass` on the entire corpus while checking nothing. It would have read
as a permanent clean green. Every dash spelling is pinned below.

  §1  the stencil declaration — present, absent, malformed version
  §2  the path declaration — present, absent (with the derived fix), doubled
  §3  scope — a non-template file is untouched; the ` Template` suffix is
      title-case and is a prefilter, not proof
  §4  the cut-line matches dashes OF ANY KIND, against the real corpus bytes
  §5  the two in-repo exemplars actually carry the declarations
  §6  ruleset parity — both rules wired, and -04 reversed rather than deleted

Run: python3 test-f570-template-declaration.py
"""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent.parent
RULESET = REPO / "rulesets" / "R-template.md"
FEX = REPO / "examples" / "FEX Templates"


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_f570", HERE / "audit-plan.py")
FAILURES = []
CUT = "✂ ──── template notes ──── ✂"


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def run(fn, notes, name="_Computer Template.md", body="# {{HOSTNAME}}\nbody.\n"):
    td = tempfile.mkdtemp()
    root = Path(td)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    f = root / name
    f.write_text(f"{body}\n{CUT}\n{notes}\n", encoding="utf-8")
    return fn(f, root, None)


STEN = ap.chk_template_stencil_declared
PATH = ap.chk_template_path_declared
FULL = "stencil:: V1.0\npath:: {{PURCHASE_DATE}} {{HOSTNAME}}.md\n"

print("1. The stencil declaration")
check("a well-formed `stencil:: V1.0` passes", run(STEN, FULL)[0], "pass")
st, d = run(STEN, "path:: x.md\n")
check("absent → fail", st, "fail")
check("...and the message names the fix", "stencil:: V1.0" in d, True)
check("...and says the filename is only a migration fallback",
      "migration fallback" in d, True)
# The version is the half that will matter longest — a template that cannot say
# which grammar it was written against cannot be migrated when STEN changes.
for bad in ("1.0", "v1", "V1", "latest", "V1.0.0"):
    check(f"malformed version `{bad}` → fail",
          run(STEN, f"stencil:: {bad}\n")[0], "fail")
check("the V prefix is required (Dan, 2026-08-20)",
      run(STEN, "stencil:: V2.3\n")[0], "pass")

print("2. The path declaration")
check("a well-formed `path::` passes", run(PATH, FULL)[0], "pass")
st, d = run(PATH, "stencil:: V1.0\n")
check("absent → fail", st, "fail")
# Migration is mechanical, so the message carries the answer rather than making
# the author reconstruct the rule that was just reversed.
check("...and the message carries the fix derived from the filename",
      "path:: Computer.md" in d, True)
check("two `path::` lines → fail",
      run(PATH, "stencil:: V1.0\npath:: a.md\npath:: b.md\n")[0], "fail")
# A declared path can hold structure — the capability a filename never had.
check("a multi-segment path is legal",
      run(PATH, "stencil:: V1.0\npath:: {{YEAR}}/{{MONTH}}/{{SLUG}}.md\n")[0], "pass")

print("3. Scope — the suffix is a prefilter, not proof")
for n in ("Computer.md", "_Computer template.md", "_Computer Templates.md", "README.md"):
    check(f"{n!r} is out of scope", run(STEN, "", name=n)[0], "pass")
check("title-case ` Template.md` IS in scope",
      run(STEN, "", name="_Computer Template.md")[0], "fail")
# R-template-04 reversed: a constant middle is now the RECOMMENDED form, and
# nothing may flag it.
check("a constant middle is fine — no rule objects",
      run(STEN, FULL, name="_Computer Template.md")[0], "pass")
# A file with no cut-line at all defers to R-template-08 rather than reporting
# a missing declaration into a region that does not exist.
td = tempfile.mkdtemp(); root = Path(td)
(root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
nc = root / "_Computer Template.md"
nc.write_text("# {{X}}\nno cut-line here.\n", encoding="utf-8")
check("no cut-line → defers to R-template-08", STEN(nc, root, None)[0], "pass")

print("4. The cut-line matches dashes OF ANY KIND — the vacuous-pass bug")
DASHES = {"U+2500 box-drawing (the canonical form)": "─",
          "ASCII hyphen": "-", "en dash": "–", "em dash": "—",
          "horizontal bar": "―", "minus sign": "−",
          "U+2501 heavy box-drawing": "━"}
for label, ch in DASHES.items():
    line = f"{ch*4} template notes {ch*4}"
    check(f"cut-line matches {label}", bool(ap._CUTLINE_RE.match(line)), True)
check("scissors are optional", bool(ap._CUTLINE_RE.match("---- template notes ----")), True)
check("case-insensitive", bool(ap._CUTLINE_RE.match("──── TEMPLATE NOTES ────")), True)
check("fewer than 3 dashes does not match",
      bool(ap._CUTLINE_RE.match("-- template notes --")), False)
# Against the real bytes, not a reconstruction of them.
real = FEX / "_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md"
if real.is_file():
    hit = [ln for ln in real.read_text(encoding="utf-8").splitlines()
           if ap._CUTLINE_RE.match(ln)]
    check("matches the live exemplar's actual cut-line", len(hit), 1)
    check("...and that line really is U+2500, not ASCII",
          "─" in hit[0] if hit else False, True)

print("5. The in-repo exemplars carry the declarations")
found = sorted(FEX.rglob("_* Template.md")) if FEX.is_dir() else []
check("both exemplars are present", len(found), 2)
for f in found:
    check(f"{f.name} declares stencil", STEN(f, f.parent, None)[0], "pass")
    check(f"{f.name} declares path", PATH(f, f.parent, None)[0], "pass")
# The folder template is the one that proves the new capability: its path names
# a folder AND the marker inside it, which one filename segment cannot do.
folder = [f for f in found if "DISK_LABEL" in f.name]
if folder:
    txt = folder[0].read_text(encoding="utf-8")
    check("the folder exemplar declares a multi-segment path",
          "path:: {{DISK_LABEL}}/{{DISK_LABEL}}.md" in txt, True)

print("6. The ruleset states it (the T552 parity discipline)")
text = RULESET.read_text(encoding="utf-8")
for rule, ref in (("R-template-13", "template_stencil_declared"),
                  ("R-template-14", "template_path_declared")):
    m = re.search(rf"### RULE {rule}\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
    check(f"{rule} exists", bool(m), True)
    if m:
        check(f"...{rule} wires its checker", f"check:: {ref}" in m.group(0), True)
        check(f"...{rule} is marked (checked)", "(checked)" in m.group(0).splitlines()[0], True)
m13 = re.search(r"### RULE R-template-13\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
if m13:
    check("...-13 records the 0-of-36 migration measurement", "0 of 36" in m13.group(0), True)
    check("...-13 keeps the filename as an explicit fallback",
          "fallback" in m13.group(0), True)
m04 = re.search(r"### RULE R-template-04\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-template-04 still exists (reversed, not deleted)", bool(m04), True)
if m04:
    b = m04.group(0)
    check("...-04 no longer demands a variableized middle",
          "the middle IS the instance-name pattern" in b, False)
    check("...-04 states the reversal and quotes the reason",
          "very weird file names" in b, True)
    check("...-04 says the form it used to flag is now recommended",
          "now the recommended one" in b, True)
check("both checkers are registered",
      [ap.registry().get(k) is not None
       for k in ("template_stencil_declared", "template_path_declared")], [True, True])

print()
if FAILURES:
    print(f"test-f570-template-declaration: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-f570-template-declaration: all checks pass")
