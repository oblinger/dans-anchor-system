#!/usr/bin/env python3
"""T555 — R-doc-structure-03 needs headings, not only length.

Reported from `Log/VOX/`: writing a meeting transcript fired *"417 lines with no
TOC table"*. A `type: vox-transcript` doc has an H1 and a `## Transcript` and
nothing else, so the TOC the rule asked for would point at the only section.

**The corpus had already voted, which is what makes this a defect rather than a
preference.** `2026-08-15 Juan — game break signals and metrics.md` is 1,072
lines with no TOC; `2026-08-10 Lewis on Singapore.md` is 6,631. The rule had
been firing and being ignored — the failure mode the audit discipline names,
where a warning agents learn to skip trains them to skip warnings generally.

The rule's own Check pattern always read *"heading count + body lines"*; only
the body-lines half was ever implemented. So this is the checker catching up to
its ruleset, not a new policy — the third such case in two days (T556, T561),
and one that `ruleset-parity.py` could NOT have caught, because both halves
already used the same words.

**4, not a round number.** Measured vault-wide before choosing: 381 docs fire,
`< 4` silences 40 and leaves 341, and both transcripts above carry exactly 3
headings. §3 pins the boundary at 3-vs-4 so a later "tidy it to 5" has to
argue with a fixture.

Run: python3 test-t555-toc-needs-headings.py
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-doc-structure.md"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def doc(headings, lines=400, toc=False):
    """A long doc with `headings` headings (H1 counts) and optionally a TOC."""
    out = ["# The Title", "One line of orientation."]
    if toc:
        out += ["", "| Table of Contents |  |", "| --- | --- |"]
        out += [f"| **[[#S{i}]]** | what it is |" for i in range(1, headings)]
    for i in range(1, headings):
        out += ["", f"## S{i}", "body"]
    out += ["filler"] * lines
    return "\n".join(out) + "\n"


def verdict(text, name="A Doc.md"):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        f = root / name
        f.write_text(text)
        return ap.chk_toc_table_iff_long(f, root, [])


print("1. A long flat doc no longer fires")
for h in (1, 2, 3):
    st, msg = verdict(doc(h))
    check(f"{h} heading(s), 400+ lines", st, "pass")

print("2. A long SECTIONED doc still does — the gate is not a mute")
st, msg = verdict(doc(6))
check("6 headings, no TOC, still fails", st, "fail")
check("...and the message now names the heading count",
      "6 headings" in msg, True)
check("6 headings WITH a TOC passes", verdict(doc(6, toc=True))[0], "pass")

print("3. The boundary is 3-vs-4, the number the measurement chose")
check("3 headings passes (the transcript shape)", verdict(doc(3))[0], "pass")
check("4 headings fails", verdict(doc(4))[0], "fail")

print("4. Length still matters — a short doc was never in scope")
check("a 4-heading SHORT doc passes", verdict(doc(4, lines=10))[0], "pass")

print("5. The earlier exemptions are untouched")
check("Q.md is still exempt", verdict(doc(9), name="Q.md")[0], "pass")
check("a queries projection is still exempt",
      verdict(doc(9), name="ZZ queries.md")[0], "pass")
check("an Inbox is still exempt", verdict(doc(9), name="ZZ Inbox.md")[0], "pass")
check("a Messages log is still exempt",
      verdict(doc(9), name="ZZ Messages.md")[0], "pass")

print("6. The two live transcripts the report named")
VOX = Path.home() / "ob/kmr/Log/VOX"
named = ["2026-08-15 Juan — game break signals and metrics.md",
         "2026-08-10 Lewis on Singapore.md"]
seen = 0
for n in named:
    f = VOX / n
    if not f.is_file():
        continue
    seen += 1
    lines = ap._strip_fenced(ap._read(f)).splitlines()
    hd = sum(1 for ln in lines if ap._ANY_HEADING_RE.match(ln))
    print(f"       ({n[:44]} — {len(lines)} lines, {hd} headings)")
    check(f"{n[:28]} no longer fires",
          ap.chk_toc_table_iff_long(f, Path.home() / "ob/kmr", [])[0], "pass")
    check("...and it is long enough that only the heading gate saves it",
          len(lines) >= 300, True)
check("the named transcripts were found", seen, 2)

print("7. The ruleset text says what the checker does (the T552 lesson)")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-doc-structure-03\b.*?(?=\n### RULE |\Z)", text, re.S)
check("R-doc-structure-03 is present", bool(m), True)
if m:
    body = m.group(0)
    check("...states the flat-document exemption",
          "fewer than 4 headings" in body, True)
    check("...and that BOTH halves are required now",
          "heading count AND body lines" in body, True)
    check("...carries the measured 381/40/341", "381" in body and "341" in body, True)
    check("...names the two transcripts the corpus voted with",
          "6,631" in body, True)
    check("...says why this beat a vox-transcript frontmatter exemption",
          "vox-transcript" in body, True)

print()
if FAILURES:
    print(f"test-t555-toc-needs-headings: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t555-toc-needs-headings: all checks pass")
