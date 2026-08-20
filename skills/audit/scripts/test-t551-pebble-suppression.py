#!/usr/bin/env python3
"""T551 — a row parked behind a pebble does not appear on Dan's screen.

Dan, 2026-08-18: *"There shouldn't be any references to things blocked on
pebbles that are visible to me."* Under the umbrella-pebble model a pebble is a
cohesive chunk of work and the rows belonging to it hang off it, parked, until
he pulls the whole pebble — so a `[Blocked <SLUG> P####]` row is inventory
inside a container he already knows about, and putting it on Q.md defeats the
point of having containerised it (*"I'm getting overwhelmed by the size of the
backlog"*).

Two things this file pins that are easy to get wrong:

  **Transitivity.** ATT T193 is `[Blocked T192]` and T192 is pebble-blocked.
  Suppressing only the direct edge leaks the container back onto the screen
  through the chain.

  **Q.md only.** The per-anchor `{slug} queries.md` is the agent's working view
  and must keep showing every row — the owning agent still has to see its own
  inventory. This is why the filter is applied to the ROW SET handed to one of
  the two renders rather than built into `build_queries_body`, which stays
  total over whatever it is given (F284).

**A note on what this is worth today, recorded so nobody mistakes it for the
thing that fixed Atticus's symptom.** The four ATT rows he named are already
off Dan's screen, for an unrelated reason: `## Later` stopped rendering on
2026-08-19 and `_row_should_render` is False for every Later row, which is
where C16 parks every `[Blocked]` row. That change is itself under observation
(TINK F332's Verify window restarted the same day), so it is a horizon policy
that may move. This filter states the pebble rule independently of it, and the
case it covers on its own is a pebble-blocked row still sitting on the frontier
— between the write and the next `audit-q --fix` that moves it. §3 pins exactly
that, because it is the only case where the two rules do not overlap.

Run: python3 test-t551-pebble-suppression.py
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "qr", Path(__file__).resolve().parent / "queries-render.py")
qr = importlib.util.module_from_spec(_spec)
sys.modules["qr"] = qr
_spec.loader.exec_module(qr)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def row(ident, bracket, horizon="Later"):
    return qr.Row(line_num=1, raw_line="", horizon=horizon, identifier=ident,
                  is_h3=False, bracket=bracket, body="", arrow_link=None)


print("1. The direct edge — a row blocked on a pebble handle")
rows = [
    row("T177", "Blocked ATT P0004"),
    row("T187", "Blocked ATT P0004"),
    row("T198", "Blocked ATT P0011"),
    row("T500", "Blocked T012"),          # blocked on an ordinary row
    row("T501", "Ready", "Now"),
    row("T502", "Blocked"),               # bare, pre-gate form; names no edge
]
check("the three pebble-blocked rows",
      sorted(qr.pebble_suppressed_ids(rows, "ATT")), ["T177", "T187", "T198"])

print("2. Transitivity — the chain must not leak the container back")
chain = [
    row("T192", "Blocked ATT P0004"),
    row("T193", "Blocked T192"),          # ATT's real case
    row("T194", "Blocked T193"),          # one link further
    row("T195", "Blocked ATT-T194"),      # anchor-qualified spelling of the same edge
    row("T600", "Blocked T601"),          # a chain that never reaches a pebble
    row("T601", "Blocked T602"),
    row("T602", "Ready", "Now"),
]
check("the whole chain suppresses",
      sorted(qr.pebble_suppressed_ids(chain, "ATT")),
      ["T192", "T193", "T194", "T195"])

print("3. The case the Later-renders-nothing rule does NOT cover")
# A pebble-blocked row still on the frontier: C16 will move it to Later on the
# next --fix, but until then it renders, and this is the only window in which
# the two rules disagree.
frontier = [row("T700", "Blocked ATT P0004", "Now"),
            row("T701", "Ready", "Now")]
check("a Now-horizon pebble row is eligible to render",
      qr._row_should_render(frontier[0]), True)
check("...and is suppressed anyway",
      sorted(qr.pebble_suppressed_ids(frontier, "ATT")), ["T700"])

print("4. Handle spellings")
for label, bracket, want in [
    ("`<SLUG> P####` (the live form)", "Blocked ATT P0004", True),
    ("hyphenated", "Blocked ATT-P0004", True),
    ("bare `P####`", "Blocked P0004", True),
    ("lowercase slug", "Blocked att P0004", True),
    ("an ordinary row id", "Blocked T0004", False),
    ("an F-row id", "Blocked F004", False),
    ("a qualified row id", "Blocked ATT-F041", False),
    ("a bare Blocked", "Blocked", False),
    ("not blocked at all", "Ready", False),
    ("Waiting with a date", "Waiting 2026-09-20", False),
]:
    check(label, "T1" in qr.pebble_suppressed_ids([row("T1", bracket)], "ATT"),
          want)

print("5. A cycle terminates instead of spinning")
cycle = [row("T1", "Blocked T2"), row("T2", "Blocked T1"),
         row("T3", "Blocked ATT P0001")]
check("cycle does not hang and does not over-suppress",
      sorted(qr.pebble_suppressed_ids(cycle, "ATT")), ["T3"])

print("6. Nothing is suppressed when no pebble is involved")
plain = [row("T1", "Ready", "Now"), row("T2", "Blocked T1"),
         row("T3", "Questions", "Next")]
check("empty set", qr.pebble_suppressed_ids(plain, "ATT"), set())

print()
if FAILURES:
    print(f"test-t551-pebble-suppression: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t551-pebble-suppression: all checks pass")
