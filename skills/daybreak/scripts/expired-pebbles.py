#!/usr/bin/env python3
"""Print every rostered Lumen pebble whose DATED tempo has already passed.

A dated `tempo::` is a one-shot: the pebble surfaces on its day and then leaves the
briefing forever, answered or not. So an unanswered dated pebble goes silent exactly
when it becomes most overdue, and the only surviving trace is that it is still listed
on the roster. That is what this finds.

Cadence tempos (`daily`, `weekly`, `<date> -> daily`) and `waiting` are skipped: they
keep surfacing on their own and cannot fall into this hole.

Silence is a real answer. Exits 0 either way -- this is a reporter, not a gate.
"""

import datetime
import glob
import os
import sys

PEBBLES = os.path.expanduser(
    "~/ob/kmr/SYS/Staff/Lumen/Lumen Track/Lumen Pebbles"
)
ROSTER = os.path.join(PEBBLES, "Lumen Pebbles.md")

# An arrow means "dormant until <date>, THEN at a cadence" -- never a one-shot.
CADENCE = {"daily", "weekly", "waiting", ""}


def field(path, key):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(key):
                return line[len(key):].strip()
            if not line.strip():
                break  # key block ends at the first blank line
    return ""


def main():
    today = datetime.date.today().isoformat()
    if len(sys.argv) > 1:
        today = sys.argv[1]  # let a caller ask "what expires by <date>?"

    try:
        with open(ROSTER, encoding="utf-8") as fh:
            roster = fh.read()
    except FileNotFoundError:
        print(f"expired-pebbles: roster not found at {ROSTER}", file=sys.stderr)
        return 0

    for path in sorted(glob.glob(os.path.join(PEBBLES, "Lumen P0*.md"))):
        name = os.path.basename(path)[:-3]
        if f"[[{name}|" not in roster:
            continue  # retired -- already settled, correctly silent
        tempo = field(path, "tempo::")
        if "→" in tempo or tempo in CADENCE:
            continue
        day = tempo.split()[0]
        if day < today:
            print(f"EXPIRED {day}  {name}  {field(path, 'line::')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
