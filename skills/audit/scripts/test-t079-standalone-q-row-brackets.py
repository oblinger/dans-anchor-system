#!/usr/bin/env python3
"""T079 — the five bracket checks must all recognise an F275 standalone Q-row.

F275 shipped a backlog row whose identifier is `Q<n>` and where the row IS the
question: no feature doc, no arrow link, and sub-bullets that are ask-format
options (`- **(A)** …`) rather than nested `- **Q<n> —` headers. Exactly ONE of
the five checks that reason about brackets was taught the shape — C24's checker
carries the exemption and even documents it. The other four fire on every
standalone Q-row that exists.

The reported symptom was a silent discard: `state -a Tink Backlog Q001 set
--status Questions` printed success and left `[Designing]` on disk. The cause is
not in `state` at all — `state` runs `audit-q --fix` as a post-write step, and
`apply_c24_fix` counted zero inline Qs on the row (its sub-bullets are options,
not Q-headers), concluded the bracket over-claimed, and rewrote it back.

The dangerous one is the pair C23/`apply_c23_fix`: reading zero pending Qs on a
`[Designing]` standalone Q-row, it concludes design is over and promotes the row
to `[Ready]` — bracketing a question awaiting the user as agent-executable work,
where a crank will pick it up.

Correct semantics: a standalone Q-row is SELF-BACKING and is exactly one pending
question, so its honest bracket is `[Questions]`.

The exemption must stay narrow. Ordinary F-rows must still be counted against
their linked doc, and an ordinary `[Designing]` row must still owe a link and a
justification — those are the assertions that would catch an over-broad fix.

Run: python3 test-t079-standalone-q-row-brackets.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "aq", Path(__file__).resolve().parent / "audit-q.py")
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def codes_for(findings, ident):
    """Every finding code raised against a row, by identifier substring."""
    return sorted({f.code for f in findings if f"'{ident}'" in f.message})


BACKLOG = """---
description: "fixture"
---

# ZZ Backlog
Fixture backlog for the T079 standalone-Q-row assertions.

## Now

- **Q001 — a standalone Q-row, still open** [Designing] — the row IS the
  question; no feature doc exists and none should. ^Q001
    - **(A)** one option
    - **(B)** another option
  - **Recommendation:** None

- **Q002 — a standalone Q-row already bracketed right** [Questions] — same
  shape, correct bracket; the fixer must leave it alone. ^Q002
    - **(A)** one option
    - **(B)** another option

- **T5 — an ordinary designing row with no link** [Designing] — still owes a
  link and a justification. ^T5

- **QFix — a row whose identifier merely starts with Q** [Designing] — must NOT
  be mistaken for a standalone Q-row. ^QFix

- **T6 — a Ready row whose body discusses brackets** [Ready] — reports that the
  file keeps `[Designing]` after the write. The word in the body must not make
  this read as a [Designing] row. ^T6
"""


def build(tmp):
    root = Path(tmp)
    (root / ".anchor").write_text("slug: ZZ\n")
    f = root / "ZZ Backlog.md"
    f.write_text(BACKLOG)
    entries = aq.backlog_entries(f, {})
    return f, entries


print("1. The standalone Q-row is recognised, and only it")
check("Q001 recognised", aq._is_standalone_q_row("Q001"), True)
check("Q7 (unpadded) recognised", aq._is_standalone_q_row("Q7"), True)
check("QFix NOT recognised", aq._is_standalone_q_row("QFix"), False)
check("T5 NOT recognised", aq._is_standalone_q_row("T5"), False)
check("empty NOT recognised", aq._is_standalone_q_row(None), False)

with tempfile.TemporaryDirectory() as td:
    bfile, entries = build(td)

    print("2. C23 calls the standalone row [Questions], never [Ready]")
    c23 = aq.check_c23_designing_resolves(entries)
    q001 = [f for f in c23 if "'Q001'" in f.message]
    check("Q001 gets exactly one C23 finding", len(q001), 1)
    check("...naming [Questions]", "[Questions]" in q001[0].message, True)
    check("...NOT promoting to [Ready]", "[Ready]" in q001[0].message, False)
    check("...mechanically fixable", q001[0].mechanically_fixable, True)
    check("ordinary T5 still flagged", bool([f for f in c23 if "'T5'" in f.message]), True)

    print("3. C33 does not demand a feature-doc link from it")
    c33 = aq.check_c33_designing_needs_link(entries)
    check("Q001 not flagged", codes_for(c33, "Q001"), [])
    check("ordinary T5 still flagged", codes_for(c33, "T5"), ["C33"])
    check("QFix still flagged", codes_for(c33, "QFix"), ["C33"])

    print("4. C25 does not demand a separate justification")
    c25 = aq.check_c25_designing_justification([bfile], {})
    q001_c25 = [f for f in c25 if f.surface_line == 10]
    check("Q001 not flagged", q001_c25, [])
    check("ordinary T5 still flagged",
          bool([f for f in c25 if f.surface_line == 21]), True)
    # A [Ready] row whose BODY quotes `[Designing]` is not a [Designing] row.
    # Live false positive on Tink T079 — a bug report about bracket handling
    # was flagged for a justification it does not owe.
    check("T6 (bracket named in body prose) not flagged",
          [f.surface_line for f in c25 if f.surface_line == 27], [])

    print("5. C34 does not call the row's own header an illegal inline Q")
    c34 = aq.check_c34_inline_q_in_row_body([bfile])
    check("no C34 findings on the Q-rows",
          [f.surface_line for f in c34 if f.surface_line in (10, 16)], [])

print("6. apply_c23_fix rewrites [Designing] → [Questions], not [Ready]")
with tempfile.TemporaryDirectory() as td:
    bfile, entries = build(td)
    changed, log = aq.apply_c23_fix(bfile, entries)
    after = bfile.read_text()
    check("file changed", changed, True)
    check("Q001 now [Questions]", "- **Q001 — a standalone Q-row, still open** [Questions]" in after, True)
    check("Q001 NOT promoted to [Ready]", "**Q001" in after and "[Ready]" in after.split("^Q001")[0], False)

print("7. apply_c24_fix leaves a correctly-bracketed standalone Q-row alone")
print("   (this is the silent revert T079 reported)")
with tempfile.TemporaryDirectory() as td:
    bfile, entries = build(td)
    before = bfile.read_text()
    changed, log = aq.apply_c24_fix(bfile, entries)
    after = bfile.read_text()
    check("Q002 still [Questions]",
          "- **Q002 — a standalone Q-row already bracketed right** [Questions]" in after, True)
    check("not reverted to [Designing]",
          "- **Q002 — a standalone Q-row already bracketed right** [Designing]" in after, False)

print("8. Round-trip: the two fixers agree, so the bracket is stable")
with tempfile.TemporaryDirectory() as td:
    bfile, _ = build(td)
    for _ in range(3):
        aq.apply_c23_fix(bfile, aq.backlog_entries(bfile, {}))
        aq.apply_c24_fix(bfile, aq.backlog_entries(bfile, {}))
    after = bfile.read_text()
    check("Q001 settles at [Questions]",
          "- **Q001 — a standalone Q-row, still open** [Questions]" in after, True)
    check("Q002 settles at [Questions]",
          "- **Q002 — a standalone Q-row already bracketed right** [Questions]" in after, True)

print()
if FAILURES:
    print(f"test-t079-standalone-q-row-brackets: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t079-standalone-q-row-brackets: all checks pass")
