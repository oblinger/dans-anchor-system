#!/usr/bin/python3
"""nudge-check.py — tier-2 reach for LUMEN Nudge (Lumen T005).

Lumen can only interrupt while it is running, so a 🔔 row is otherwise honoured
only at the next Daybreak (day-granularity). This runs from a launchd agent on a
short interval, reads LUMEN Nudge, and fires `~/bin/alert` on any due 🔔 row that
resolves to a concrete time — so an hour-critical nudge lands at its hour without
Lumen being open.

The Tempo column (2026-08-06, replacing `Due`) answers two questions in one cell:
*when do I raise this next*, and *how often after that*. Grammar:

    2026-08-07 07:00            one moment, then the row is done
    2026-08-10                  one day, no hour           -> Daybreak's job
    daily / weekly              recurring, no hour          -> Daybreak's job
    2026-08-07 07:00 -> daily   first at that moment, every day after at 07:00
    2026-08-06 10:00 -> weekly  first at that moment, same weekday+time after
    every 3 hours / hourly      sub-day repeat from now
    waiting                     blocked on a person or event, no clock

Only tempos carrying a concrete TIME fire here. Day-only and bare-cadence rows
stay Daybreak's job — the daemon cannot fire at an unknown hour, and hour-critical
things belong on the calendar anyway (see LUMEN Nudge § BRIEF).

Fire-once-per-occurrence: fired rows are recorded in a local sidecar (NOT the
vault), keyed by occurrence-bucket + What, so a `daily` row alerts once per day
rather than every interval. A row edited to new text is a new key and may fire
again — acceptable and rare.

Usage:  nudge-check.py [path-to-nudge-file]   (arg overrides for testing)
        nudge-check.py --selftest             (parser tests, no alerts)
Uses system /usr/bin/python3 — launchd runs with a bare environment, so no
dependency on the login shell or a conda env.
"""
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
NUDGE = HOME / "ob/kmr/SYS/Staff/Lumen/LUMEN Nudge.md"
FIRED = HOME / ".config/anchor-system/lumen/nudge-fired.txt"
ALERT = HOME / "bin/alert"
COLOR = "orange"  # attention, not alarm-red — reserved for genuinely time-critical

DT = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?$")
EVERY_H = re.compile(r"^(?:every\s+(\d+)\s+hours?|hourly)$", re.I)
ARROW = re.compile(r"\s*(?:->|→)\s*")


def parse_tempo(cell):
    """-> (start dt|None, cadence, has_time). cadence: None|'daily'|'weekly'|('hours',n)."""
    s = cell.strip().strip("`").strip()
    if not s or s.lower() in ("waiting", "next run"):
        return None, None, False

    parts = ARROW.split(s, 1)
    head, tail = parts[0].strip(), (parts[1].strip().lower() if len(parts) > 1 else "")

    cadence = None
    if tail in ("daily", "weekly"):
        cadence = tail
    elif tail:
        m = EVERY_H.match(tail)
        if m:
            cadence = ("hours", int(m.group(1)) if m.group(1) else 1)

    # head may itself be a bare cadence (no date)
    hl = head.lower()
    if hl in ("daily", "weekly"):
        return None, hl, False
    m = EVERY_H.match(hl)
    if m:
        return None, ("hours", int(m.group(1)) if m.group(1) else 1), False

    m = DT.match(head.replace("—", "").strip())
    if not m:
        return None, cadence, False
    day, hhmm = m.group(1), m.group(2)
    if not hhmm:
        return datetime.strptime(day, "%Y-%m-%d"), cadence, False
    return datetime.strptime(f"{day} {hhmm}", "%Y-%m-%d %H:%M"), cadence, True


def occurrence(start, cadence, has_time, now):
    """Latest due occurrence at/before now, or None. Only time-bearing tempos fire."""
    if not has_time or start is None:
        return None
    if now < start:
        return None
    if cadence is None:
        return start
    if cadence == "daily":
        today = now.replace(hour=start.hour, minute=start.minute,
                            second=0, microsecond=0)
        return today if now >= today else today - timedelta(days=1)
    if cadence == "weekly":
        n = (now - start).days // 7
        return start + timedelta(weeks=n)
    if isinstance(cadence, tuple) and cadence[0] == "hours":
        n = int((now - start).total_seconds() // (cadence[1] * 3600))
        return start + timedelta(hours=cadence[1] * n)
    return None


def load_fired():
    return set(FIRED.read_text().splitlines()) if FIRED.exists() else set()


def record(keys):
    FIRED.parent.mkdir(parents=True, exist_ok=True)
    with FIRED.open("a") as f:
        for k in keys:
            f.write(k + "\n")


def main(path):
    if not path.exists():
        return
    fired = load_fired()
    now = datetime.now()
    newly = []
    for line in path.read_text().splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("Tempo", "Due") or set(cells[0]) <= {"-"}:
            continue
        tempo_raw, alert_col, what = cells[0], cells[1], cells[2]
        if "🔔" not in alert_col:
            continue
        start, cadence, has_time = parse_tempo(tempo_raw)
        occ = occurrence(start, cadence, has_time, now)
        if occ is None:
            continue  # day-only, bare cadence, waiting, or not yet due
        key = f"{occ:%Y-%m-%d %H:%M}|{what}"
        if key in fired:
            continue
        subprocess.run([str(ALERT), f"{what}  ·  due {occ:%Y-%m-%d %H:%M}", COLOR])
        newly.append(key)
    if newly:
        record(newly)


def selftest():
    now = datetime(2026, 8, 9, 9, 0)
    cases = [
        ("`2026-08-07 07:00`",           "2026-08-07 07:00"),  # one-shot, past
        ("`2026-08-07 07:00 → daily`",   "2026-08-09 07:00"),  # today's occurrence
        ("`2026-08-06 10:00 → weekly`",  "2026-08-06 10:00"),  # week 0; next is 8/13
        ("`2026-08-10`",                 None),                # day-only -> Daybreak
        ("`2026-08-06 → daily`",         None),                # no hour  -> Daybreak
        ("`daily`",                      None),
        ("`weekly`",                     None),
        ("`waiting`",                    None),
        ("`2026-08-11 09:00`",           None),                # future
        ("`every 3 hours`",              None),                # no anchor -> Daybreak
    ]
    ok = True
    for cell, want in cases:
        s, c, ht = parse_tempo(cell)
        occ = occurrence(s, c, ht, now)
        got = f"{occ:%Y-%m-%d %H:%M}" if occ else None
        flag = "ok " if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  {flag} {cell:<30} -> {got}   (want {want})")
    print("selftest", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(Path(arg[0]) if arg else NUDGE)
