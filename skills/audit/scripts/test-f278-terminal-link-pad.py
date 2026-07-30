#!/usr/bin/env python3
"""F278 — terminal links carry exactly one trailing space (R-markdown-16), and
R-markdown-14 does not strip that space back off.

The defect class this guards is not "the pad is missing" — it is
NON-IDEMPOTENCE. HA F135 was reverted once already because a padded link, once
strikethrough-wrapped, stranded its pad and oscillated on every pass. This rule
runs on EVERY agent write, so a non-idempotent implementation corrupts files
continuously instead of failing loudly. Most assertions below are therefore
fixpoint assertions: apply twice, get the same bytes.

The other half is cross-rule: R-markdown-14 (strip trailing whitespace) and
R-markdown-16 (add one trailing space) both fire on the same lines. If they
disagree they fight inside warden forever. `both_fixers_reach_a_joint_fixpoint`
is the assertion that they don't.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(spec)
sys.modules["ap"] = ap          # @dataclass needs the module registered
spec.loader.exec_module(ap)

FAILS = []


def check(name, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def write(text):
    d = Path(tempfile.mkdtemp())
    p = d / "T.md"
    p.write_text(text, encoding="utf-8")
    return p


def pad(p):
    return ap.fix_md_terminal_link_pad(p, p.parent, [])


def strip(p):
    return ap.fix_md_trailing_ws(p, p.parent, [])


print("F278 — terminal-link pad")

# ---- the predicate, ported from HA -----------------------------------------
E = ap._ends_with_terminal_link
check("wiki link is terminal", E("see [[Foo]]"))
check("aliased wiki link is terminal", E("see [[Foo\\|Bar]]"))
check("struck wiki link is terminal", E("see ~~[[Foo]]~~"))
check("markdown link is terminal", E("see [x](http://a)"))
check("hook link is terminal", E("see [SYS](hook://p/SYS)"))
check("already-padded link is NOT terminal", not E("see [[Foo]] "))
check("link before punctuation is NOT terminal", not E("see [[Foo]]."))
check("link before block-anchor is NOT terminal", not E("see [[Foo]] ^abc"))
check("bare prose paren is NOT terminal", not E("a sentence (in parens)"))
check("plain text is NOT terminal", not E("just words"))

# ---- padding ----------------------------------------------------------------
p = write("- see [[Foo]]\n- plain text\n")
pad(p)
check("pad appends exactly one space", p.read_text() == "- see [[Foo]] \n- plain text\n",
      repr(p.read_text()))

before = p.read_text()
changed, _ = pad(p)
check("pad is idempotent — second run is a no-op", not changed and p.read_text() == before,
      repr(p.read_text()))

# ---- never two spaces (a <br> hard break) -----------------------------------
p = write("- see [[Foo]]\n")
pad(p); pad(p); pad(p)
check("three applications never produce a <br> hard break",
      p.read_text() == "- see [[Foo]] \n", repr(p.read_text()))

# ---- the F135 strikethrough oscillation -------------------------------------
p = write("- see [[Foo]] \n")
# a padded link later goes broken and is wrapped in place by the strikethrough pass
p.write_text(p.read_text().replace("[[Foo]] ", "~~[[Foo]]~~ "), encoding="utf-8")
changed, _ = pad(p)
check("struck-and-padded link is a fixpoint (the F135 revert case)",
      not changed and p.read_text() == "- see ~~[[Foo]]~~ \n", repr(p.read_text()))

# ---- exclusions -------------------------------------------------------------
p = write("| a | [[Foo]] |\n| b | c |\n")
changed, _ = pad(p)
check("table rows are left to ha", not changed, repr(p.read_text()))

p = write("```\nsee [[Foo]]\n```\n")
changed, _ = pad(p)
check("fenced code is skipped", not changed, repr(p.read_text()))

p = write("---\ndescription: see [[Foo]]\n---\n\nbody\n")
changed, _ = pad(p)
check("YAML frontmatter is skipped", not changed, repr(p.read_text()))

# ---- R-markdown-14 must not strip the pad back off --------------------------
p = write("- see [[Foo]] \n")
changed, _ = strip(p)
check("trailing-ws fixer PRESERVES the pad", not changed and p.read_text() == "- see [[Foo]] \n",
      repr(p.read_text()))

p = write("- see [[Foo]]   \n- words   \n")
strip(p)
check("trailing-ws fixer collapses over-padding to the canonical one space, "
      "and still strips ordinary trailing space",
      p.read_text() == "- see [[Foo]] \n- words\n", repr(p.read_text()))

# ---- the joint fixpoint: the two rules must not fight ------------------------
src = ("- see [[Foo]]\n"
       "- see ~~[[Bar]]~~\n"
       "- see [x](http://a)\n"
       "- plain words   \n"
       "- link then text [[Baz]] trailing\n"
       "| cell | [[Qux]] |\n")
p = write(src)
for _ in range(4):                       # interleave both fixers repeatedly
    pad(p); strip(p)
settled = p.read_text()
pad(p); strip(p)
check("both fixers reach a JOINT fixpoint (no strip/re-pad oscillation)",
      p.read_text() == settled, repr(p.read_text()))
check("no line in the joint fixpoint ends in two spaces (<br>)",
      not any(l.endswith("  ") for l in settled.split("\n")), repr(settled))

# ---- checker agrees with fixer ----------------------------------------------
p = write("- see [[Foo]]\n")
v, _ = ap.chk_md_terminal_link_pad(p, p.parent, [])
check("checker fails on an unpadded terminal link", v == "fail")
pad(p)
v, _ = ap.chk_md_terminal_link_pad(p, p.parent, [])
check("checker passes once the fixer has run", v == "pass")
v, _ = ap.chk_md_trailing_ws(p, p.parent, [])
check("trailing-ws checker does not flag the pad", v == "pass")

print(f"\n{'FAILED: ' + ', '.join(FAILS) if FAILS else 'all assertions pass'}")
sys.exit(1 if FAILS else 0)
