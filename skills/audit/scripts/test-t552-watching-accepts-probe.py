#!/usr/bin/env python3
"""T552 — a `[Watching]` row may carry a `- **Probe:**` instead of a Verify,
and R-backlog-04's own text must say so.

T237 relaxed R-backlog-04 for `[Watching*]` rows — the F305 agent-owned
deferred check is a legitimate alternative to a user-answered Verify — and
fixed three code sites: the `define` refusal, F240's ownership gate, and
audit-q C41. It missed two, and both are on the path a real row takes.

  1. `chk_backlog_verify_concrete` in audit-plan.py — the Warden-side checker.
  2. `rulesets/R-backlog.md` — the prose those checkers implement.

Atticus hit both on 2026-08-18: `state set` accepted ATT T202 in its designed
`[Watching 2026-08-23]` + Probe shape, and Warden fired on the same write.
Advisory, not a refusal — which is worse, not better: every future
Watching+Probe row nags forever, and a warning agents learn to skip trains
them to skip warnings generally.

Atticus's generalization is what this file is really pinning: *"a grep for the
BEHAVIOUR would have found the three; only a grep for the RULE ID finds the
fourth."* A ruleset that nothing verifies is the one copy that can drift, so
§4 asserts the prose and the checker agree about which fields are accepted.
That is a narrow form of checker↔ruleset agreement — it catches the field
going out of sync, not every possible disagreement — and it is the form that
would have caught this one.

The relaxation must stay narrow. `[Verify*]` is the USER-owned family; letting
a Probe satisfy it would be a way to park a user check where the user never
sees it, so §3 pins that a Verify row is not helped by a Probe.

Run: python3 test-t552-watching-accepts-probe.py
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

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-backlog.md"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


HEAD = """---
description: "fixture"
---

# ZZ Backlog
Fixture backlog for the T552 assertions.

## Later

"""


def verdict(row_block):
    """Run backlog_verify_concrete over a one-row fixture backlog."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        f = root / "ZZ Backlog.md"
        f.write_text(HEAD + row_block)
        return ap.CHECKERS["backlog_verify_concrete"](f, root, [])[0]


print("1. A [Watching] row is satisfied by a Probe — the T237 relaxation")
check("Watching + Probe passes", verdict(
    "- **T1 — a designed watching row** [Watching 2026-08-23] — body ^T1\n"
    "  - **Probe:** on 2026-08-23 re-run the soak counts and compare to 14.\n"
), "pass")
check("Watching + Verify still passes", verdict(
    "- **T2 — the older shape** [Watching 2026-08-23] — body ^T2\n"
    "  - **Verify:** did the crash recur in the last week? no = fixed.\n"
), "pass")
check("Watching with NEITHER still fails", verdict(
    "- **T3 — half-authored** [Watching 2026-08-23] — body ^T3\n"
    "  - **Next:** something the agent does.\n"
), "fail")

print("2. The bare and timed Watching forms behave the same")
check("bare [Watching] + Probe passes", verdict(
    "- **T4 — bare form** [Watching] — body ^T4\n"
    "  - **Probe:** once `fired` reaches 21 — re-run the soak counts.\n"
), "pass")

print("3. The Verify family is NOT relaxed — a Probe does not stand in")
check("[Verify] + Probe only fails", verdict(
    "- **T5 — a user check** [Verify] — body ^T5\n"
    "  - **Probe:** the agent will look at the log next week.\n"
), "fail")
check("[Verify-by] + Probe only fails", verdict(
    "- **T6 — a dated user check** [Verify-by 2026-09-01] — body ^T6\n"
    "  - **Probe:** the agent will look at the log next week.\n"
), "fail")
check("[Verify] + Verify passes", verdict(
    "- **T7 — a real user check** [Verify] — body ^T7\n"
    "  - **Verify:** does the strip read right at a glance? · *why-user: taste*\n"
), "pass")

print("4. The ruleset text agrees with the checker about accepted fields")
text = RULESET.read_text(encoding="utf-8")
rule = re.search(r"### RULE R-backlog-04\b.*?(?=\n### RULE )", text, re.S)
check("R-backlog-04 is present in the ruleset", bool(rule), True)
if rule:
    body = rule.group(0)
    check("...and names `- **Probe:**` as accepted on Watching",
          "**Probe:**" in body, True)
    check("...and still names `- **Verify:**`", "**Verify:**" in body, True)
    # The stale form: a check pattern that keys Verify and Watching together
    # off one required field is exactly the sentence that was wrong.
    check("...and no longer says Verify-or-Watching requires Verify",
          bool(re.search(r"bracket starts `Verify` or `Watching`", body)), False)
# The state table (row 5) is a second copy of the same claim in the same file,
# and it is the one Atticus found first.
table_row = re.search(r"^\|\s*5\s*\|\s*\*\*Watching\*\*.*$", text, re.M)
check("the state table's Watching row exists", bool(table_row), True)
if table_row:
    check("...and it mentions Probe too", "Probe" in table_row.group(0), True)

print()
if FAILURES:
    print(f"test-t552-watching-accepts-probe: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t552-watching-accepts-probe: all checks pass")
