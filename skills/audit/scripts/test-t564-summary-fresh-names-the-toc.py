#!/usr/bin/env python3
"""T564 — R-progressive-05 names the TOC as the repair, and its anti-nag holds
across a write.

Found 2026-08-20 mid-edit on F308. The advisory read *"sections: 1 removed since
the summary was last written — re-read it and decide whether it still serves a
reader"*, so the agent rewrote the `## Summary` prose. Nothing happened. It
rewrote it again. Nothing happened again.

**`_disclosure_summary` never looks at `## Summary`.** It hashes the rows
`_SUMMARY_ROW_RE` matches — the TOC table or the dispatch masthead. The prose
section is not the summary region and never was, so the escape the rule's own
text promises (*"rewrite it and the unit set is re-blessed"*) is unreachable by
the route its message points at.

The actual repair was `md-toc.py`: `state` had removed `## Open Questions` when
Q5/Q6 migrated, and the TOC was still listing it — a dead `[[#Open Questions]]`
row a reader can click. **Measured on the live registry the same day: 9 of the
12 documents standing flagged carried exactly that dead row.** Three times in
four the rule detects a real defect and describes it as a different one.

**The second defect is in the same block and is worse**, because it is the one
the block exists to prevent. The anti-nag suppressed on
`prev["prompted"] == units` — a `{name: content-hash}` map — so ANY edit
anywhere in the document minted a fresh key and re-fired the same unanswered
prompt on the next write. Its own comment names that outcome as *"exactly how
the original prose rule died."* A key finer than its trigger is the same as no
key.

**Why the existing suite missed it, which is the transferable part.**
`test-f277-disclosure.py:70` asserts *"same drift does NOT re-fire"* by calling
the checker twice in a row **with no intervening write**. That proves the guard
holds when nothing changes — which is not the situation it was built for. Its
own docstring says ad-hoc fixtures failed because they *"never re-ran a checker
against unchanged drift"*; this is the adjacent hole, re-running against drift
that changed somewhere else. §2 below writes between every check for that
reason.

Run: python3 test-t564-summary-fresh-names-the-toc.py
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

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-progressive.md"

FAILURES = []
FILLER = "filler line\n" * 40


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def fresh_env():
    tmp = Path(tempfile.mkdtemp())
    ap.DISCLOSURE_REGISTRY = tmp / "disclosure.json"
    return tmp


def toc_doc(path, sections, extra_toc=()):
    """A TOC-backed doc. `extra_toc` lets the TOC name a section that is gone."""
    rows = "".join(f"| **[[#{s}]]** | what {s} covers |\n"
                   for s in list(sections) + list(extra_toc))
    body = "".join(f"## {s}\n\n{FILLER}" for s in sections)
    path.write_text(f"# {path.stem}\n\n| Table of Contents |  |\n|---|---|\n{rows}\n{body}")
    return path


def masthead_doc(path, sections):
    """A doc whose summary region is a dispatch masthead — rows name FILES."""
    rows = "".join(f"| -[[Sibling {i}]]- | a sibling page with a real gloss here |\n"
                   for i in range(3))
    body = "".join(f"## {s}\n\n{FILLER}" for s in sections)
    path.write_text(f"# {path.stem}\n\n{rows}| --- | |\n\n{body}")
    return path


print("1. The message names the TOC when a section came or went")
tmp = fresh_env()
f = toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(8)])
check("first sight blesses silently", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
# Remove a section the way `state` removes `## Open Questions` — body only,
# leaving the TOC row behind. That dead row is the point.
toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(7)], extra_toc=["S7"])
st, msg = ap.chk_summary_fresh(f, tmp, "")
check("a removed section fires", st, "fail")
check("...and the message names the TOC", "TOC table" in msg, True)
check("...and hands over the generator command", "md-toc.py" in msg, True)
check("...and warns off hand-editing the rows", "figure spaces" in msg, True)
check("...and still asks for the prose re-read afterwards",
      "leave it deliberately" in msg, True)

print("2. Regenerating the TOC is what actually clears it — prose is not")
tmp = fresh_env()
f = toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(8)])
ap.chk_summary_fresh(f, tmp, "")
toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(7)], extra_toc=["S7"])
check("fires once", ap.chk_summary_fresh(f, tmp, "")[0], "fail")
# (a) Rewrite the `## Summary`-style PROSE. This is what the old message
#     invited, and it must be shown to change nothing — it is the whole reason
#     the message was wrong rather than merely terse.
f.write_text(f.read_text().replace("filler line", "rewritten prose line", 20))
check("rewriting prose does NOT re-bless", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("...and it is still unresolved, not merely quiet",
      "S7" in re.sub(r"\n## .*", "", f.read_text().split("\n\n##")[0]), True)
# (b) Regenerate the TOC — drop the dead row. NOW the region hash moves.
toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(7)])
check("regenerating the TOC re-blesses", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("...and stays quiet after", ap.chk_summary_fresh(f, tmp, "")[0], "pass")

print("3. The anti-nag survives an intervening write (the T564 defect)")
# Twelve sections, not eight: this case removes TWO of them, and a doc that
# shrinks under `_disclosure_complex` exits the checker at its first line and
# returns a pass that means "not in scope", not "did not fire". Caught here by
# the fix's own fixture reading pass where it should have read fail.
tmp = fresh_env()
f = toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(12)])
ap.chk_summary_fresh(f, tmp, "")
toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(11)], extra_toc=["S11"])
check("fires on the removed section", ap.chk_summary_fresh(f, tmp, "")[0], "fail")
check("does not re-fire with no write between", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
# The case the old fixture never built: edit an UNRELATED section, then look
# again. Before the fix this re-fired, because the content hash of S3 was part
# of the suppression key.
for round_ in range(3):
    txt = f.read_text().replace("## S3\n\n" + FILLER,
                                "## S3\n\n" + f"round {round_} body\n" * 40)
    f.write_text(txt)
    check(f"quiet after unrelated edit #{round_ + 1}",
          ap.chk_summary_fresh(f, tmp, "")[0], "pass")
# But the drift GROWING must still speak.
toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(10)], extra_toc=["S10", "S11"])
check("the shrunken fixture is still in scope", ap._disclosure_complex(f), True)
check("a SECOND removed section fires again", ap.chk_summary_fresh(f, tmp, "")[0], "fail")

print("4. Content-fraction drift keeps the strict key — it must re-prompt")
tmp = fresh_env()
f = toc_doc(tmp / "Doc.md", [f"S{i}" for i in range(8)])
ap.chk_summary_fresh(f, tmp, "")
for i in (1, 2, 3):
    f.write_text(f.read_text().replace(f"## S{i}\n\n" + FILLER,
                                       f"## S{i}\n\n" + "CHANGED\n" * 40))
check("quarter-drift fires", ap.chk_summary_fresh(f, tmp, "")[0], "fail")
check("same drift stays quiet", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
f.write_text(f.read_text().replace("## S4\n\n" + FILLER, "## S4\n\n" + "MORE\n" * 40))
check("drifting FURTHER fires again — names-only key would have muted this",
      ap.chk_summary_fresh(f, tmp, "")[0], "fail")

print("5. A masthead-backed doc gets the generic message, not the TOC one")
tmp = fresh_env()
m = masthead_doc(tmp / "Container.md", [f"S{i}" for i in range(8)])
check("masthead is a summary region", ap._disclosure_summary(m)[0], True)
check("...but is not a TOC", ap._summary_is_toc(m), False)
ap.chk_summary_fresh(m, tmp, "")
masthead_doc(tmp / "Container.md", [f"S{i}" for i in range(7)])
st, msg = ap.chk_summary_fresh(m, tmp, "")
check("a removed section still fires", st, "fail")
check("...and does NOT send the agent to md-toc.py", "md-toc.py" in msg, False)
check("...it asks for the re-read instead", "still serves a reader" in msg, True)

print("5b. A CONTAINER page with a content TOC also gets the generic message")
# The shape of every backlog in the vault: a namesake page over a folder, so
# its units are its member FILES, and it carries a content TOC anyway. Without
# the `scope == "file"` gate all six live ones were told to run md-toc.py for a
# change in their sibling set, which the generator cannot see.
tmp = fresh_env()
d = tmp / "Bag"
d.mkdir()
c = toc_doc(d / "Bag.md", [f"S{i}" for i in range(12)])
for i in range(6):
    (d / f"Member {i}.md").write_text(f"# Member {i}\n\n{FILLER}")
check("it is container-scope, not file-scope", ap._disclosure_scope(c, tmp), "container")
check("...and it does carry a content TOC", ap._summary_is_toc(c), True)
ap.chk_summary_fresh(c, tmp, "")
(d / "Member 5.md").unlink()
st, msg = ap.chk_summary_fresh(c, tmp, "")
check("a removed MEMBER fires", st, "fail")
check("...counted as members, not sections", "members:" in msg, True)
check("...and does NOT send the agent to md-toc.py", "md-toc.py" in msg, False)

print("6. `_summary_is_toc` keys on the in-document target, not on the word TOC")
tmp = fresh_env()
p = tmp / "Mixed.md"
p.write_text("# T\n\n| Table of Contents |  |\n|---|---|\n| **[[Some Page]]** | not an outline row |\n")
check("a table of wiki-links to OTHER pages is not a TOC", ap._summary_is_toc(p), False)
p.write_text("# T\n\n| **[[#A Heading]]** | outline |\n")
check("a bare `[[#…]]` row is", ap._summary_is_toc(p), True)

print("7. The ruleset says what the checker does (the T552 parity discipline)")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-progressive-05\b.*?(?=\n### RULE |\Z)", text, re.S)
check("R-progressive-05 is present", bool(m), True)
if m:
    body = m.group(0)
    check("...states the region is NOT the `## Summary` prose",
          "NOT the prose" in body, True)
    check("...names md-toc.py as the add/remove repair", "md-toc.py" in body, True)
    check("...carries the measured 3-of-4 file-scope", "3 of those 4" in body, True)
    check("...and states the container-scope gate", "member files" in body, True)
    check("...explains the two anti-nag keys", "finer than its trigger" in body, True)
    check("...and that a masthead gets the generic message", "masthead" in body.lower(), True)

print()
if FAILURES:
    print(f"test-t564-summary-fresh-names-the-toc: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t564-summary-fresh-names-the-toc: all checks pass")
