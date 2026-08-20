#!/usr/bin/env python3
"""F302 — R-template-11: a specimen opening below `# H1` declares its anchor.

Two mistakes were made writing this rule, and both are pinned here because both
were the kind that reads as fine until something measures it.

**The glyph was called unpinned when it had been pinned for two weeks.** The
first draft shipped -11 and -12 as `(stated)` on the reasoning that
`STEN Language` had not fixed the marker's spelling — F302's design doc
describes the two forms in *meaning* ("this deep or deeper" / "exactly this
deep") and never quotes them, so reading only F302 supports that conclusion.
`STEN Language`'s own construct table has carried `# ... LOG` and `# == LOG`
since M2, 2026-08-07. §5 asserts the glyphs directly against that file so the
claim cannot rot back.

**The corpus was called empty by searching the wrong thing.** The same draft
recorded "zero section-named files", measured with a filename search for
`_* Section Template.md`. The name is explicitly NOT the mechanism — the form
is — so searching the name found nothing while searching the shape finds two,
both written long before any marker existed. §4 keeps both real specimens as
fixtures, because a rule whose corpus is empty proves nothing when it passes.

  §1  the ambiguous middle fails — opens at `##`/`###`, no marker;
  §2  both marker forms satisfy it, at any depth;
  §3  the spine is skipped — `:>>` breadcrumb, masthead table, frontmatter;
  §4  the two real specimens in the vault still fail, by shape not by name;
  §5  the glyphs match `STEN Language`, and whole-document is its default;
  §6  ruleset parity — the rule, its check ref, the measured counts.

Run: python3 test-f302-template-anchor.py
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
STEN = REPO / "Stencil" / "STEN Language.md"


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_f302", HERE / "audit-plan.py")
FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def run(body, name="_{{THING}} Template.md"):
    td = tempfile.mkdtemp()
    root = Path(td)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    f = root / name
    f.write_text(body, encoding="utf-8")
    return ap.chk_template_anchor_declared(f, root, None)


print("1. The ambiguous middle fails — below H1, no marker")
st, d = run("### {{DATE}} — {{TITLE}}\nbody.\n")
check("### with no marker fails", st, "fail")
check("...names the depth it saw", "`###`" in d, True)
check("...offers both marker forms", "..." in d and "==" in d, True)
check("...also offers the raise-to-H1 escape", "raise it to" in d, True)
check("## with no marker fails", run("## {{X}}\nbody.\n")[0], "fail")

print("2. Both marker forms satisfy it, at any depth")
check("`... NAME` at H1", run("# ... LOG\n### {{DATE}}\n")[0], "pass")
check("`== NAME` at H1", run("# == LOG\n### {{DATE}}\n")[0], "pass")
check("`... NAME` at H3", run("### ... LOG\nbody.\n")[0], "pass")
check("`== NAME` at H2", run("## == LOG\nbody.\n")[0], "pass")
check("a marker on a variable heading", run("## ... {{SECTION}}\nbody.\n")[0], "pass")
# Whole-document is STEN's default, so a plain H1 needs no marker at all.
check("a plain `# H1` passes with no marker", run("# {{HOSTNAME}}\nbody.\n")[0], "pass")

print("3. The spine is skipped before the first heading is read")
# A specimen is live markdown, so it carries what a real instance carries — and
# a real page may open with a breadcrumb or masthead ABOVE its H1. Reading line
# one instead of the first HEADING called five conformant templates defects.
check("`:>>` breadcrumb then H1",
      run(":>> [[kmr]] → [[Topic]] → [X](hook://p/X) \n# {{X}}\nbody.\n")[0], "pass")
check("masthead table then H1",
      run("| -[[X]]- | → [[DAS]] |\n| --- | --- |\n| Related | [[Y]] |\n\n# {{X}}\nb.\n")[0],
      "pass")
check("frontmatter then H1",
      run("---\ndescription: d\n---\n\n# {{X}}\nbody.\n")[0], "pass")
check("frontmatter + breadcrumb then a bare `###` still FAILS",
      run("---\nd: e\n---\n\n:>> [[a]] → [b](hook://p/b) \n### {{D}}\nx.\n")[0], "fail")

print("4. The two real specimens in the vault — found by SHAPE, not by name")
vault = Path.home() / "ob" / "kmr"
real = {}
for f in vault.rglob("_* Template.md"):
    s = str(f)
    if "/Yore/" in s or "/Closet/" in s:
        continue
    st, _ = ap.chk_template_anchor_declared(f, f.parent, None)
    real.setdefault(st, []).append(f.name)
fails = sorted(real.get("fail", []))
check("the corpus is NOT clean — the rule has something to bite on",
      len(fails) >= 2, True)
for want in ("_{{READ_DATE}} {{PAPER_TITLE}} Template.md", "_BUY {{CATEGORY}} Template.md"):
    check(f"still flagged: {want}", want in fails, True)
# The name search that produced the wrong "zero" — kept as a live assertion so
# the two numbers can never drift back into agreeing by accident.
by_name = [f for f in vault.rglob("_* Section Template.md") if "/Yore/" not in str(f)]
check("...while the NAME search still finds zero", len(by_name), 0)

print("5. The glyphs agree with STEN Language, which pinned them at M2")
sten = STEN.read_text(encoding="utf-8")
check("STEN specifies `# ... LOG`", "`# ... LOG`" in sten, True)
check("STEN specifies `# == LOG`", "`# == LOG`" in sten, True)
check("STEN makes whole-document the no-marker default",
      "a stencil with no anchor marker governs the whole file" in sten, True)
check("the checker's regex accepts exactly those two heads",
      [bool(ap._STEN_ANCHOR_RE.match(x)) for x in ("... LOG", "== LOG", "~~ LOG", "...LOG")],
      [True, True, False, False])

print("6. The ruleset states it (the T552 parity discipline)")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-template-11\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-template-11 exists", bool(m), True)
if m:
    b = m.group(0)
    check("...is marked (checked), not (stated)", "(checked)" in b.splitlines()[0], True)
    check("...wires the checker", "check:: template_anchor_declared" in b, True)
    check("...quotes both glyphs", "`# ... NAME`" in b and "`# == NAME`" in b, True)
    check("...says the spine is skipped", "spine is skipped" in b, True)
    check("...carries the measured counts", "24 root-anchored" in b, True)
    check("...records WHY the earlier zero was wrong",
          "the name is not the mechanism" in b, True)
    check("...scopes out the no-heading case deliberately",
          "no heading at all is deliberately out of scope" in b, True)
m12 = re.search(r"### RULE R-template-12\b.*?(?=\n### RULE |\n## |\Z)", text, re.S)
check("R-template-12 exists", bool(m12), True)
if m12:
    b12 = m12.group(0)
    # -12 is still (stated), but for the RIGHT reason now: a missing resolver,
    # not a missing notation.
    check("...blames the missing resolver, not the notation",
          "scope-ladder resolver" in b12, True)
    check("...says the notation is NOT what is missing",
          "not a missing notation" in b12, True)
check("the checker is registered",
      ap.registry().get("template_anchor_declared") is not None, True)

print()
if FAILURES:
    print(f"test-f302-template-anchor: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-f302-template-anchor: all checks pass")
