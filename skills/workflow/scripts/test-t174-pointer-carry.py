#!/usr/bin/env python3
"""T174 — `state set --body` must not silently sever a row's `→ [[doc]]` pointer.

`--body` is a whole-body REPLACEMENT. Passing a completion write-up therefore
deleted the only edge from a backlog row to its feature doc, and the F102 check
noticed the pointer was gone and responded by *skipping* the `## Status` block
check — spending the one signal that could have caught it on excusing it.

The fix carries a leading pointer from the existing body onto a replacement that
lacks one, unless `--drop-pointer` says to sever it deliberately. These tests
cover the pure decision function and the live CLI round-trip.

Run: python3 test-t174-pointer-carry.py
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / "state"

_passed = 0
_failed = 0


def check(label, got, want):
    global _passed, _failed
    if got == want:
        _passed += 1
        print(f"  ok    {label}")
    else:
        _failed += 1
        print(f"  FAIL  {label}\n          got:  {got!r}\n          want: {want!r}")


def _load_carry():
    """Lift the two definitions out of `state` without importing the whole CLI —
    `state` has no .py suffix and running it top-to-bottom would parse argv."""
    src = STATE.read_text(encoding="utf-8")
    start = src.index("_ARROW_POINTER_RE = re.compile")
    end = src.index("def _delegate_row_edit")
    ns = {}
    exec("import re\n" + src[start:end], ns)
    return ns["_carry_doc_pointer"]


print("The pure decision — when a pointer is carried and when it is left alone")

carry = _load_carry()

out, carried = carry("→ [[Doc A|F1]] — old text", "new body, no pointer")
check("a replacement with no pointer inherits the old one",
      (out, bool(carried)), ("→ [[Doc A|F1]] · new body, no pointer", True))

out, carried = carry("→ [[Doc A|F1]] — old", "→ [[Doc B|F2]] — new")
check("a replacement that already names a doc is left untouched",
      (out, bool(carried)), ("→ [[Doc B|F2]] — new", False))

out, carried = carry("a row that never had a pointer", "new body")
check("nothing is invented when the old body had no pointer",
      (out, bool(carried)), ("new body", False))

out, carried = carry("", "new body")
check("an empty old body carries nothing", (out, bool(carried)), ("new body", False))

out, carried = carry("→ [[Doc A|F1]] — old", "")
check("an empty new body is left alone rather than reduced to a bare pointer",
      (out, bool(carried)), ("", False))

# The pointer regex must match the real corpus shape: a piped wiki-link whose
# display half carries an em-dash, which is what every feature row uses.
real = "→ [[Tink310 - Stream: one reverse-chronological facet at three volumes|F310 — Stream]] — body"
out, carried = carry(real, "replacement")
check("the piped, em-dashed link form real rows use is recognised",
      bool(carried) and out.startswith("→ [[TINK310 - Stream"), True)


print("\nThe live CLI round-trip — a real row, restored byte-exact afterwards")

BACKLOG = pathlib.Path.home() / "ob/kmr/SYS/Staff/Tink/Tink Track/Tink Backlog.md"
ROW = "F303"


def rowline():
    for ln in BACKLOG.read_text(encoding="utf-8").split("\n"):
        if ln.rstrip().endswith("^" + ROW):
            return ln
    return ""


if not BACKLOG.exists() or not rowline():
    print(f"  skip  {ROW} not present — live leg needs a real row carrying a pointer")
else:
    original = rowline()
    body = original.split("] — ", 1)[1].rsplit(" ^" + ROW, 1)[0]
    if not re.match(r"^→\s+\[\[", body):
        print(f"  skip  {ROW}'s body does not lead with a pointer")
    else:
        stripped = re.sub(r"^→\s+\[\[[^\]]+\]\]\s*—\s*", "", body)
        r = subprocess.run(
            [str(STATE), "set", "TINK", "Backlog", ROW, "--body", stripped],
            capture_output=True, text=True,
        )
        check("the CLI announces the carry on stderr rather than doing it silently",
              "carried the row's doc pointer" in r.stderr, True)
        check("the pointer is present in the row after a pointer-less --body",
              bool(re.match(r"^→\s+\[\[", rowline().split("] — ", 1)[1])), True)

        subprocess.run([str(STATE), "set", "TINK", "Backlog", ROW, "--body", body],
                       capture_output=True, text=True)
        check("the row is restored byte-exact, so this test leaves no trace",
              rowline(), original)


print(f"\n{_passed} passed, {_failed} failed")
sys.exit(1 if _failed else 0)
