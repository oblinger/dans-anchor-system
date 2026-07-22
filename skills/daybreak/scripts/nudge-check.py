#!/usr/bin/python3
"""nudge-check.py — tier-2 reach for LUM Nudge (Lumen T005).

Lumen can only interrupt while it is running, so a 🔔 row is otherwise honoured
only at the next Daybreak (day-granularity). This runs from a launchd agent on a
short interval, reads LUM Nudge, and fires `~/bin/alert` on any past-due 🔔 row
whose Due carries a real time — so an hour-critical nudge lands at its hour
without Lumen being open.

Fire-once: fired rows are recorded in a local sidecar (NOT the vault), keyed by
Due+What, so a nudge does not re-alert every interval. A row edited to a new time
or text is a new key and may fire again — acceptable and rare.

Only ISO `YYYY-MM-DD HH:MM` Due values with a concrete time fire here. Day-only
(`—` time) rows and the `waiting` / `next run` literals stay Daybreak's job — the
daemon cannot fire at an unknown hour, and hour-critical things belong on the
calendar anyway (see LUM Nudge § BRIEF).

Usage:  nudge-check.py [path-to-nudge-file]   (arg overrides for testing)
Uses system /usr/bin/python3 — launchd runs with a bare environment, so no
dependency on the login shell or a conda env.
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
NUDGE = Path(sys.argv[1]) if len(sys.argv) > 1 else HOME / "ob/kmr/SYS/Staff/Lumen/LUM Nudge.md"
FIRED = HOME / ".config/anchor-system/lumen/nudge-fired.txt"
ALERT = HOME / "bin/alert"
COLOR = "orange"  # attention, not alarm-red — reserved for genuinely time-critical

ROW_TIME = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})$")


def load_fired():
    if FIRED.exists():
        return set(FIRED.read_text().splitlines())
    return set()


def record(keys):
    FIRED.parent.mkdir(parents=True, exist_ok=True)
    with FIRED.open("a") as f:
        for k in keys:
            f.write(k + "\n")


def main():
    if not NUDGE.exists():
        return
    fired = load_fired()
    now = datetime.now()
    newly = []
    for line in NUDGE.read_text().splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        due_raw, alert_col, what = cells[0], cells[1], cells[2]
        if "🔔" not in alert_col:
            continue
        due = due_raw.strip("`").strip()
        if not ROW_TIME.match(due):
            continue  # day-only or literal — Daybreak's job, not the daemon's
        due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
        if due_dt > now:
            continue  # not due yet
        key = f"{due}|{what}"
        if key in fired:
            continue  # already fired once
        subprocess.run([str(ALERT), f"{what}  ·  due {due}", COLOR])
        newly.append(key)
    if newly:
        record(newly)


if __name__ == "__main__":
    main()
