#!/usr/bin/env python3
"""F296 — one definition of "the document's H1".

Sixteen checkers located the H1 with one of three hand-spelled patterns —
`^# \\S`, `^# `, `.startswith("# ")` — and every one of them demanded column zero
and exactly one space, over the raw file text. Three blindnesses fell out of that,
and the corpus says the least-discussed one was the worst:

  * MULTI-SPACE. `SYS/Atlas/Atlas.md` opens `#  Atlas  — glossary "what is X?"`
    with TWO spaces. `^# \\S` walks past it to the file's `# BRIEF` at line 374 and
    blames THAT line for the missing orientation line. This is T092's damage
    signature exactly; T092 read the cause as indentation and shipped `^ {0,3}`,
    which does not fix Atlas.md and never did.
  * FENCE. A `# comment` inside a ```python or ```bash block is read as the head.
    Fourteen vault docs did this; `Disk DU.md` reported its own `# BRIEF` "is not
    the last H1" because a shell example below it contained `# from anywhere`.
  * FRONTMATTER. A YAML `#` comment inside `---` fences is read as the head —
    `skills/bridge/templates/brief-template.md`, whose `# status_doc:` comment sat
    five lines above the real `# Brief — <task name>`.

All three now resolve in `_H1_RE` / `_first_h1`, which every site routes through.
Run standalone; no test framework.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(spec)
sys.modules["ap"] = ap
spec.loader.exec_module(ap)

FAILS = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        FAILS.append(label)


# -- the H1 predicate ---------------------------------------------------------

def h1(text):
    return ap._first_h1(text)


check("one space is still an H1", h1("# Title\nbody\n"), (0, "Title"))
check("TWO spaces after the hash — the Atlas.md form",
      h1('#  Atlas  — glossary "what is X?"\nrouter\n'),
      (0, 'Atlas  — glossary "what is X?"'))
check("a tab after the hash", h1("#\tTitle\nbody\n"), (0, "Title"))
check("up to three leading spaces (CommonMark ATX)",
      h1("   # Indented Title\nbody\n"), (0, "Indented Title"))
check("FOUR leading spaces is an indented code block, not a heading",
      h1("    # Not A Heading\n"), (None, None))
check("`#` with no space is not an H1 (that is a hashtag)",
      h1("#NotAHeading\n"), (None, None))
check("`##` is not an H1", h1("## Two\n"), (None, None))
check("an ATX closing sequence is not part of the heading text",
      h1("# Title #\nbody\n"), (0, "Title"))
check("a lone `#` on its own line is not an H1", h1("#\nbody\n"), (None, None))

# -- frontmatter --------------------------------------------------------------

FM = (
    "---\n"
    "mission: <one-line mission>\n"
    "# status_doc: <override path>\n"
    "# heartbeat: agent-managed\n"
    "---\n"
    "\n"
    "# Brief — <task name>\n"
    "\n"
    "Body.\n"
)
check("a YAML `#` comment in frontmatter is not the H1", h1(FM), (6, "Brief — <task name>"))
check("the returned index is in WHOLE-FILE coordinates",
      FM.splitlines()[h1(FM)[0]], "# Brief — <task name>")

# -- fences -------------------------------------------------------------------

FENCED = (
    "Prose with no heading.\n"
    "\n"
    "```python\n"
    "# Load the Iris dataset\n"
    "iris = load_iris()\n"
    "```\n"
)
check("a Python comment inside a fence is not the H1", h1(FENCED), (None, None))
check("a real H1 below a fenced comment wins",
      h1(FENCED + "\n# Real Head\n")[1], "Real Head")
check("tilde fences count too (the `_strip_fenced` route, not a local toggle)",
      h1("~~~\n# not a head\n~~~\n"), (None, None))
check("an info-string line INSIDE an open block does not close it",
      h1("````\n```python\n# still fenced\n````\n"), (None, None))

# -- the sixteen consumers ----------------------------------------------------
# Each of these is a REAL vault instance; the file paths are named in the docstring.

VAULT = Path.home() / "ob" / "kmr"


def verdict(fn, rel, anchor_rel=None):
    p = VAULT / rel
    if not p.is_file():
        return ("missing", rel)
    root = VAULT / anchor_rel if anchor_rel else p.parent
    return getattr(ap, fn)(p, root, [])[0]


atlas = "SYS/Atlas/Atlas.md"
if (VAULT / atlas).is_file():
    check("Atlas.md: the head is line 0, not the `# BRIEF` at 374",
          h1((VAULT / atlas).read_text(encoding="utf-8"))[0], 0)
    check("Atlas.md: chk_doc_head_orientation_line passes (T092's live miss)",
          verdict("chk_doc_head_orientation_line", atlas, "SYS/Atlas"), "pass")
    check("Atlas.md: chk_h1_after_frontmatter passes",
          verdict("chk_h1_after_frontmatter", atlas, "SYS/Atlas"), "pass")
    check("Atlas.md: chk_h1_no_frontmatter passes",
          verdict("chk_h1_no_frontmatter", atlas, "SYS/Atlas"), "pass")

du = "SYS/SYS Catalog/Disk/Disk DU/Disk DU.md"
if (VAULT / du).is_file():
    check("Disk DU.md: `# BRIEF` IS the last H1 — the shell example below it is fenced",
          verdict("chk_brief_is_last_h1", du), "pass")

forum = "prj/Forum/Forum Track/Design Docs/005 Forum Mechanics.md"
if (VAULT / forum).is_file():
    check("005 Forum Mechanics.md: a one-space-indented H1 is the head",
          h1((VAULT / forum).read_text(encoding="utf-8"))[1], "Forum Mechanics")

# A doc whose only `# ` lines are fenced code comments has NO H1. Previously the
# comment impersonated one and the doc passed — which is why three DKT feature
# docs and ABIO Todo had no head at all and nothing said so.
f041 = "prj/ClaudiMux/Docket/DKT Track/DKT Features/F041 — Unified Namespace.md"
if (VAULT / f041).is_file():
    check("F041: fenced `# treat each file…` comments do NOT supply an H1",
          verdict("chk_h1_present", f041), "fail")

# -- shared definition --------------------------------------------------------

check("_first_h1_idx agrees with _first_h1 (one definition, two views)",
      ap._first_h1_idx(FM.splitlines()), h1(FM)[0])
check("_breadcrumb_h1_positions agrees too",
      ap._breadcrumb_h1_positions(FENCED.splitlines() + ["", "# Real Head"])[1],
      h1(FENCED + "\n# Real Head\n")[0])

# -- setext is deliberately NOT an H1 here (measured, then reverted) ----------
# `===` in this vault is a divider, not an underline. Recognizing setext scored
# zero true heads and four false ones, including a git merge-conflict marker.

check("`Title` over `===` is NOT read as an H1",
      h1("Title\n=====\n\nbody\n"), (None, None))
check("a git conflict marker over `=======` is NOT an H1",
      h1("<<<<<<< HEAD\n=======\n\n:: item\n"), (None, None))

# -- empty frontmatter: the two spellings agreed after `_split_frontmatter` ----

check("empty frontmatter is frontmatter for `_first_h1`",
      h1("---\n---\n# SKA\nOrientation.\n"), (2, "SKA"))
check("...and for chk_h1_after_frontmatter, which used to trip on the `---`",
      ap._split_frontmatter("---\n---\n# SKA\n")[1], "# SKA\n")

# -- the EOF message names what is actually wrong (165 vault docs) ------------

import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    stub = Path(td) / "stub.md"
    stub.write_text("# Just A Head\n", encoding="utf-8")
    verd, msg = ap.chk_no_blank_after_h1(stub, Path(td), [])
    check("an H1-only stub fails...", verd, "fail")
    check("...but is not told to delete a blank line that is not there",
          "blank line" in msg, False)

    # -- chk_rule_numbers_unique: a mention is not a declaration --------------
    rs = Path(td) / "R-fx.md"
    rs.write_text(
        "# RULESET R-fx\n\n"
        "### RULE R-fx-01 — first (checked)\n"
        "Prose explaining why RULE R-fx-01 exists at all.\n\n"
        "### RULE R-fx-02 — second (checked)\n"
        "An example of the form:\n\n"
        "```markdown\n"
        "### RULE R-fx-01 — a fenced illustration\n"
        "```\n", encoding="utf-8")
    check("prose citing a rule id is not a duplicate declaration",
          ap.chk_rule_numbers_unique(rs, Path(td), [])[0], "pass")

    dupe = Path(td) / "R-dupe.md"
    dupe.write_text("# RULESET R-dupe\n\n"
                    "### RULE R-dupe-01 — a (checked)\n\n"
                    "### RULE R-dupe-01 — b (checked)\n", encoding="utf-8")
    check("a REAL duplicate heading still fails (masking is not suppression)",
          ap.chk_rule_numbers_unique(dupe, Path(td), [])[0], "fail")

    # -- chk_checked_rules_have_pattern: a fenced `#` does not end the body ---
    pat = Path(td) / "R-pat.md"
    pat.write_text(
        "# RULESET R-pat\n\n"
        "### RULE R-pat-01 — a rule (checked)\n\n"
        "```python\n"
        "# a comment at COLUMN ZERO inside the fence — an indented one would not\n"
        "# have reproduced this, which is why the first fixture written here was\n"
        "# not load-bearing. `DAS Ruleset.md` carried the column-zero form.\n"
        "def body(ctx):\n"
        "    return []\n"
        "```\n\n"
        "**Check pattern:** the field sits BELOW the code block.\n", encoding="utf-8")
    check("a fenced `# comment` does not terminate a rule body",
          ap.chk_checked_rules_have_pattern(pat, Path(td), [])[0], "pass")

    nopat = Path(td) / "R-nopat.md"
    nopat.write_text("# RULESET R-nopat\n\n"
                     "### RULE R-nopat-01 — a rule (checked)\n\n"
                     "Body with no field at all.\n", encoding="utf-8")
    check("a genuinely missing Check pattern still fails",
          ap.chk_checked_rules_have_pattern(nopat, Path(td), [])[0], "fail")

    # -- `# BRIEF` is matched by the parsed heading, not the literal line -----
    br = Path(td) / "B.md"
    br.write_text("# Doc\nOrientation.\n\n# BRIEF #\nAgent contract.\n", encoding="utf-8")
    check("`# BRIEF #` (ATX closing sequence) is still the BRIEF head",
          ap.chk_brief_is_last_h1(br, Path(td), [])[0], "pass")

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: " + ", ".join(FAILS))
    sys.exit(1)
print("all F296 H1-primitive assertions passed")
