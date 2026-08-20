#!/usr/bin/env python3
"""T363 — R-spine-03 exempts a folder-form backlog, and only that.

The rule fired on **every `state` mutation** to 13 folder-form backlogs across
9 anchors. Reported three times in three days ([[SONAR]] twice, [[LUMEN]] once)
and logged as "known noise" by three prior sessions before that — which is the
cost being paid: a rule that is correct, unactionable and permanent trains
agents to skim the whole warning tier, and that tier carries the findings that
ARE actionable.

Ruled T363 Q1 = (A), 2026-08-19: a folder-form backlog fronts a folder and it
already links its members — as derived pointer rows in `## Now` / `## Next` /
`## Later`, which carry status and horizon a masthead link-list could not.

**Two things keep the exemption from becoming a hole**, and both are asserted
below because both are load-bearing:

  1. It is keyed to the machine `<!-- state:backlog -->` stamp, NOT to "the
     body has links". `state` writes that stamp and nothing acquires it by
     accident, so no future index doc can claim the same licence for prose
     that happens to link a sibling.
  2. The one thing a horizon body cannot show is a member doc whose row
     RETIRED — SONAR017, an open question to Dan, unreferenced anywhere in the
     vault for three days. That is closed by `audit-q` C58
     (`test-t363-orphan-row-docs.py`), not by this exemption, and this
     exemption is only safe because that one exists.

§4 pins the checker against the ruleset text, the T552 lesson: a rule relaxed
in code and not in its prose is a rule whose one uncheckable copy has drifted.

Run: python3 test-t363-folder-backlog-exempt.py
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

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-spine.md"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


STAMPED = """---
description: "fixture"
---

# ZZ Backlog
The index, with its members as horizon rows rather than a masthead.

<!-- state:backlog q0 -->

## Now

- **T001 — a row** [Ready] — → [[ZZ001 - A row|T001]] — body ^T001
"""

UNSTAMPED = STAMPED.replace("<!-- state:backlog q0 -->\n\n", "")


def verdict(index_text, folder_name="ZZ Backlog", extra_member=True,
            index_name=None):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        folder = root / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        f = folder / f"{index_name or folder_name}.md"
        f.write_text(index_text)
        if extra_member:
            (folder / "ZZ001 - A row.md").write_text("# ZZ001 - A row\nbody\n")
        return ap.chk_summary_present_iff_complex(f, root, [])[0]


print("1. The exemption applies to a stamped folder-form backlog")
check("stamped index with members passes", verdict(STAMPED), "pass")

print("2. ...and to nothing else")
check("the SAME file without the stamp still fails",
      verdict(UNSTAMPED), "fail")
# A non-namesake file is `file`-scope and R-spine-03 never applied to it, so
# the end-to-end verdict cannot separate "exempted by the stamp" from "was
# never in scope". The predicate is where that distinction is testable, and §4
# asserts it directly: `_is_state_backlog_namesake` refuses a stamped file that
# is not its folder's namesake, so a stray stamp can never buy silence for a
# page that IS in folder scope.
check("a non-namesake file was never in folder scope to begin with",
      verdict(STAMPED, index_name="Not The Namesake"), "pass")

print("3. The pre-existing passes are untouched")
check("no other member in the folder — nothing to summarize",
      verdict(UNSTAMPED, extra_member=False), "pass")

print("4. `_is_state_backlog_namesake` is narrow")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "ZZ Backlog").mkdir()
    good = root / "ZZ Backlog" / "ZZ Backlog.md"
    good.write_text(STAMPED)
    check("namesake + stamp", ap._is_state_backlog_namesake(good), True)
    bad_name = root / "ZZ Backlog" / "Other.md"
    bad_name.write_text(STAMPED)
    check("stamp but not the namesake", ap._is_state_backlog_namesake(bad_name), False)
    bad_stamp = root / "ZZ Backlog" / "ZZ Backlog.md"
    bad_stamp.write_text(UNSTAMPED)
    check("namesake but no stamp", ap._is_state_backlog_namesake(bad_stamp), False)
    check("a file that does not exist", ap._is_state_backlog_namesake(root / "nope" / "nope.md"), False)

print("5. The ruleset text says what the checker does (the T552 lesson)")
text = RULESET.read_text(encoding="utf-8")
rule = re.search(r"### RULE R-spine-03\b.*?(?=\n### RULE )", text, re.S)
check("R-spine-03 is present", bool(rule), True)
if rule:
    body = rule.group(0)
    check("...names the state:backlog stamp as the key",
          "state:backlog" in body, True)
    check("...says the exemption is keyed to the stamp, not to body links",
          "not to" in body and "body has links" in body, True)
    check("...points at C58 for the gap it does not cover",
          "C58" in body, True)

print()
if FAILURES:
    print(f"test-t363-folder-backlog-exempt: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t363-folder-backlog-exempt: all checks pass")
