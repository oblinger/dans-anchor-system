#!/usr/bin/python3
"""nudge-check.py — tier-2 reach for LUMEN's pebbles (Lumen T005, TINK F311/F312 M5).

Lumen can only interrupt while it is running, so a 🔔 pebble is otherwise
honoured only at the next Daybreak (day-granularity). This runs from a launchd
agent on a short interval, reads the pebbles in `Lumen Track/Lumen Pebbles/`,
and fires `~/bin/alert` on any due `alert:: 🔔` pebble whose `tempo::` resolves
to a concrete time — so an hour-critical nudge lands at its hour without Lumen
being open.

Until 2026-08-13 this read the `Lumen Nudge.md` table; F312 M5 migrated that
register to one file per pebble. The `tempo::` grammar is unchanged (canonical
spec: DAS Stone Keys § Pebble's keys):

    2026-08-07 07:00            one moment, then the pebble is done
    2026-08-10                  one day, no hour           -> Daybreak's job
    daily / weekly              recurring, no hour          -> Daybreak's job
    2026-08-07 07:00 -> daily   first at that moment, every day after at 07:00
    2026-08-06 10:00 -> weekly  first at that moment, same weekday+time after
    every 3 hours / hourly      sub-day repeat from now
    waiting                     blocked on a person or event, no clock

Only tempos carrying a concrete TIME fire here. Day-only and bare-cadence
pebbles stay Daybreak's job — the daemon cannot fire at an unknown hour, and
hour-critical things belong on the calendar anyway.

Fire-once-per-occurrence lives IN THE VAULT now: after firing, the daemon
writes `last-raised::` into the pebble itself, and a pebble fires only when
its due occurrence is later than its `last-raised::`. That one field is also
the answer to "when's the last time I was reminded?" — the old sidecar
(~/.config/anchor-system/lumen/nudge-fired.txt) kept that history where
Daybreak could not read it, which was F311's split-history defect. The sidecar
is no longer written.

A pebble with `state:: declined` never fires. Archived/done pebbles live in
subfolders and are not scanned.

Usage:  nudge-check.py [path-to-pebbles-folder]   (arg overrides for testing)
        nudge-check.py --selftest                 (parser tests, no alerts)
Uses system /usr/bin/python3 — launchd runs with a bare environment, so no
dependency on the login shell or a conda env.
"""
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
PEBBLES = HOME / "ob/kmr/SYS/Staff/Lumen/Lumen Track/LUMEN Pebbles"
ALERT = HOME / "bin/alert"
COLOR = "orange"  # attention, not alarm-red — reserved for genuinely time-critical

DT = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?$")
EVERY_H = re.compile(r"^(?:every\s+(\d+)\s+hours?|hourly)$", re.I)
ARROW = re.compile(r"\s*(?:->|→)\s*")
KEY = re.compile(r"^([A-Za-z][\w-]*)::\s?(.*)$")


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


def read_keys(path):
    """The `key:: value` block at the top of a stone file (DAS Stone Keys)."""
    keys = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = KEY.match(line)
        if not m:
            break
        keys[m.group(1)] = m.group(2).strip()
    return keys


def write_last_raised(path, stamp):
    """Set `last-raised::` in the pebble's key block, preserving everything else.
    Inserted before `appears::` (machine-written last) when absent."""
    lines = path.read_text(encoding="utf-8").splitlines()
    end = 0
    while end < len(lines) and KEY.match(lines[end]):
        end += 1
    new = f"last-raised:: {stamp}"
    for i in range(end):
        if lines[i].startswith("last-raised::"):
            lines[i] = new
            break
    else:
        at = end
        for i in range(end):
            if lines[i].startswith("appears::"):
                at = i
                break
        lines.insert(at, new)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(folder):
    if not folder.is_dir():
        return
    now = datetime.now()
    for p in sorted(folder.glob("*.md")):
        k = read_keys(p)
        if "line" not in k:
            continue  # not a stone file
        if "🔔" not in k.get("alert", ""):
            continue
        if k.get("state", "open") == "declined":
            continue
        start, cadence, has_time = parse_tempo(k.get("tempo", ""))
        occ = occurrence(start, cadence, has_time, now)
        if occ is None:
            continue  # day-only, bare cadence, waiting, or not yet due
        last = k.get("last-raised", "")
        if last:
            try:
                if occ <= datetime.strptime(last, "%Y-%m-%d %H:%M"):
                    continue  # this occurrence already raised
            except ValueError:
                pass  # unparseable last-raised:: — treat as never raised
        subprocess.run([str(ALERT), f"{k['line']}  ·  due {occ:%Y-%m-%d %H:%M}", COLOR])
        write_last_raised(p, f"{now:%Y-%m-%d %H:%M}")


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

    # key-block + dedup logic, on a scratch pebble
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "LUMEN P9999.md"
        p.write_text("line:: test pebble\ntempo:: 2026-08-07 07:00\n"
                     "alert:: 🔔\nappears:: LUMEN\n\nbody text\n")
        k = read_keys(p)
        t1 = k.get("tempo") == "2026-08-07 07:00" and "🔔" in k.get("alert", "")
        print(f"  {'ok ' if t1 else 'FAIL'} key-block parse")
        ok &= t1
        write_last_raised(p, "2026-08-09 09:00")
        k2 = read_keys(p)
        t2 = k2.get("last-raised") == "2026-08-09 09:00"
        keys_order = [l.split("::")[0] for l in p.read_text().splitlines()
                      if KEY.match(l)]
        t3 = keys_order == ["line", "tempo", "alert", "last-raised", "appears"]
        t4 = "body text" in p.read_text()
        print(f"  {'ok ' if t2 else 'FAIL'} last-raised write")
        print(f"  {'ok ' if t3 else 'FAIL'} key order (before appears::)")
        print(f"  {'ok ' if t4 else 'FAIL'} body preserved")
        ok &= t2 and t3 and t4
        # dedup: occurrence <= last-raised must not refire
        s, c, ht = parse_tempo(k2["tempo"])
        occ = occurrence(s, c, ht, datetime(2026, 8, 10, 9, 0))
        t5 = occ is not None and occ <= datetime.strptime(k2["last-raised"], "%Y-%m-%d %H:%M")
        print(f"  {'ok ' if t5 else 'FAIL'} one-shot dedup via last-raised")
        ok &= t5

    print("selftest", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(Path(arg[0]) if arg else PEBBLES)
