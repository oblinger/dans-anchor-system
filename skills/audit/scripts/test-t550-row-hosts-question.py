#!/usr/bin/env python3
"""T550 — C57 sees all four ways a backlog row hosts its own question, and
`_arrow_target` recognises all three row-document filename conventions.

F329 shipped one gate: `state` refuses a write that ADDS a pending inline
`- **Q<n>` sub-bullet to a row. Naming ONE host shape taught the next writer to
use another — SONAR T048 and T049 were both written after F329 shipped, each
carrying a full lettered yes/no inside a `- **User:**` sub-bullet, which no
check inspected. Dan found them by eye. C57 tests the invariant instead of a
shape: a row that asks the user something must have a doc to host the asking.

The second half is the defect C57 surfaced on its first run. `_arrow_target`
decides whether a row has its own doc by `basename.startswith(f"{id} ")` — a
test written for the legacy `F332 — Title` filename, which is the only one of
the three coexisting conventions that puts the row's identifier at the head of
the name. F298 moved the slug in front of it (`SONAR F006 - Title`) and F300
dropped the kind letter (`TINK332 - Title`), so every row whose doc carries
either later convention read as having NO own doc, and every caller fell
through to counting the row's inline Qs — which is 0 on exactly those rows,
because migrating a row is what moves its questions out of it. Eight fully
migrated TINK rows and SONAR F006 were reported by C57 as unmigrated, and
behind that false positive C24/C48/C50 had been silently passing vault-wide on
the same rows for the same reason: asking about a document they never found.

The match must stay narrow: a fused basename whose NUMBER matches but whose doc
H1 declares a different kind letter is not the row's doc.

Run: python3 test-t550-row-hosts-question.py
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


def kinds_for(findings, ident):
    """The shape list C57 named for one row, parsed back out of the message."""
    for f in findings:
        if f.code == "C57" and f"'{ident}'" in f.message:
            head = f.message.index("question (") + len("question (")
            return sorted(f.message[head:f.message.index(") — per F329")]
                          .split(", "))
    return []


BACKLOG = """---
description: "fixture"
---

# ZZ Backlog
Fixture backlog for the T550 / C57 assertions.

## Now

- **T042 — a migrated row, doc in the FUSED filename form** [User] — → [[ZZ042 - A migrated row|T042]] — the record lives in the doc. ^T042
  - **User:** One yes/no — should the sync join the corp pages? See [[ZZ042 - A migrated row|T042]].

- **T043 — a row hosting a lettered question in its User sub-bullet** [User] — the SONAR shape: no doc, and the whole fork is here. ^T043
  - **User:** Should `cap_b` join the fields the sync writes?
    - **(A)** Yes — one small change to an existing script.
    - **(B)** No — the two surfaces stay independent.

- **T044 — a row with a pending inline Q sub-bullet** [Questions] — the one shape F329's gate refuses at mint. ^T044
  - **Q1 — which way does this go?** — context here.
    - **Recommendation:** None

- **Q001 — a standalone Q-row** [Questions] — the row IS the question. ^Q001
    - **(A)** one option
    - **(B)** another option

- **T045 — a row whose Verify poses a question with nowhere to live** [Verify] — no doc pointer at all. ^T045
  - **Verify:** Does the strip read right at a glance? · *why-user: taste*

- **T046 — a legacy-named doc still resolves as the row's own** [User] — → [[T046 — An old-form doc|T046]] — kept for the startswith path. ^T046
  - **User:** One yes/no — ratify the naming? See [[T046 — An old-form doc|T046]].

- **T047 — a plain Ready row that asks nothing** [Ready] — → [[ZZ047 - Nothing to ask|T047]] — no question anywhere. ^T047
  - **Next:** run the thing.

## Done

- **T048 — a done row that still carries its old lettered ask** [Done] — history, not a migration target. ^T048
  - **User:** Which way?
    - **(A)** one
    - **(B)** two
"""

DOC_T042 = """---
description: "the migrated record"
---

# [[ZZ]] · T042 — A migrated row
One line.

## Status

**User** — waits on the yes/no.
"""

DOC_F042 = """---
description: "a FEATURE that shares the number"
---

# [[ZZ]] · F042 — A feature sharing the number
One line.
"""


def build(tmp):
    root = Path(tmp)
    (root / ".anchor").write_text("slug: ZZ\n")
    backlog = root / "ZZ Backlog.md"
    backlog.write_text(BACKLOG)
    d42 = root / "ZZ042 - A migrated row.md"
    d42.write_text(DOC_T042)
    d46 = root / "T046 — An old-form doc.md"
    d46.write_text("# [[ZZ]] · T046 — An old-form doc\nOne line.\n")
    d47 = root / "ZZ047 - Nothing to ask.md"
    d47.write_text("# [[ZZ]] · T047 — Nothing to ask\nOne line.\n")
    index = aq.build_vault_index(root)
    entries = aq.backlog_entries(backlog, index)
    return backlog, entries, root


print("1. `_basename_is_own_doc` — number matches, kind confirmed from the H1")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d42 = root / "ZZ042 - A migrated row.md"
    d42.write_text(DOC_T042)
    dF = root / "ZZ042 - A feature sharing the number.md"
    dF.write_text(DOC_F042)

    def link(basename, path):
        return aq.LinkEntry(
            source_file=root / "x.md", source_line=1, source_col_start=1,
            source_col_end=2, raw="", kind="wiki", target_basename=basename,
            target_file_path=path)

    check("fused T-doc is T042's own",
          aq._basename_is_own_doc(link("ZZ042 - A migrated row", d42), "T042"),
          True)
    check("...and is NOT F042's own (H1 says T)",
          aq._basename_is_own_doc(link("ZZ042 - A migrated row", d42), "F042"),
          False)
    check("a fused F-doc sharing the number is not T042's own",
          aq._basename_is_own_doc(
              link("ZZ042 - A feature sharing the number", dF), "T042"),
          False)
    check("a different number never matches",
          aq._basename_is_own_doc(link("ZZ043 - Another", d42), "T042"), False)
    check("the legacy basename matches too",
          aq._basename_is_own_doc(link("T042 — A migrated row", d42), "T042"),
          True)
    check("the F298 slug-prefixed form matches (SONAR F006 shape)",
          aq._basename_is_own_doc(link("ZZ T042 - A migrated row", d42), "T042"),
          True)
    check("...and its kind letter is honoured",
          aq._basename_is_own_doc(link("ZZ F042 - A migrated row", d42), "T042"),
          False)
    check("zero-padding is not significant",
          aq._basename_is_own_doc(link("ZZ042 - A migrated row", d42), "T42"),
          True)
    check("unresolved link falls back to the number match",
          aq._basename_is_own_doc(link("ZZ042 - A migrated row", None), "T042"),
          True)

with tempfile.TemporaryDirectory() as td:
    backlog, entries, root = build(td)
    by_id = {e.identifier: e for e in entries}

    print("2. `_arrow_target` finds the fused doc — the regression itself")
    check("T042's own doc resolves",
          (aq._arrow_target(by_id["T042"]) or None) is not None, True)
    check("...to the fused basename",
          aq._arrow_target(by_id["T042"]).target_basename,
          "ZZ042 - A migrated row")
    check("legacy-named T046 still resolves (startswith path)",
          aq._arrow_target(by_id["T046"]).target_basename,
          "T046 — An old-form doc")
    check("a row with no arrow still returns None",
          aq._arrow_target(by_id["T043"]), None)

    print("3. `_labeled_subbullet_block` reads BELOW the label line")
    span = aq._row_span_lines(by_id["T043"])
    block = aq._labeled_subbullet_block(span, "User")
    check("the (A) option is in the block", "**(A)**" in block, True)
    check("the (B) option is in the block", "**(B)**" in block, True)
    # This is exactly what `_rows_with_subbullet_text` cannot see: C19 requires
    # each option on its OWN line, so a spec-conforming question hides its whole
    # decision shape below the one line that helper keeps.
    first_line_only = aq._rows_with_subbullet_text(backlog, "User").get("T043", "")
    check("...and invisible to the first-line-only helper",
          aq.has_inline_alternatives(first_line_only), False)

    print("4. C57 names the right shape for each row")
    c57 = aq.check_c57_row_hosts_question(entries, backlog)
    check("T043 — lettered options in a User sub-bullet",
          kinds_for(c57, "T043"), ["lettered(User)"])
    check("T044 — pending inline Q sub-bullet",
          kinds_for(c57, "T044"), ["inline-q"])
    check("Q001 — standalone Q-row",
          kinds_for(c57, "Q001"), ["q-row"])
    check("T045 — a question with no doc to live in",
          kinds_for(c57, "T045"), ["unhosted(Verify)"])

    print("5. C57 does NOT fire on a migrated row — the false positive that "
          "exposed the arrow defect")
    check("T042 clean (fused doc)", kinds_for(c57, "T042"), [])
    check("T046 clean (legacy doc)", kinds_for(c57, "T046"), [])
    check("T047 clean (asks nothing)", kinds_for(c57, "T047"), [])

    print("6. C57 leaves history alone")
    check("T048 in ## Done not flagged", kinds_for(c57, "T048"), [])

    print("7. Severity is a migration backlog, not a stop-gate")
    check("every C57 finding is an error (promoted 2026-09-04, T550)",
          sorted({f.severity for f in c57 if f.code == "C57"}), ["error"])
    check("none claims to be mechanically fixable",
          sorted({f.mechanically_fixable for f in c57 if f.code == "C57"}),
          [False])

print()
if FAILURES:
    print(f"test-t550-row-hosts-question: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t550-row-hosts-question: all checks pass")
