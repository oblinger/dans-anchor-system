#!/usr/bin/env python3
"""audit-integrity — detect backlog edits that bypassed backlog-edit.py.

Compares each anchor's backlog file mtime against the last-script-run
timestamp recorded in ~/.config/ob-skills/backlog-edit/state.json by
backlog-edit.py.

  - bypass — backlog mtime > state last_run + tolerance (an agent or the
             user edited the file directly without going through the
             canonical mutation API)
  - unknown — no state entry for this anchor (script was never used on it;
              all observed edits are direct)
  - clean — backlog mtime <= state last_run + tolerance (the script's
            recorded write is the most recent change)

The audit does NOT distinguish agent-bypass from user-direct-edit (e.g.
the user editing Backlog.md in Obsidian) — both look identical. The
report flags both; the user filters by familiarity with their own edits.

Usage:
    audit-integrity [--anchor SLUG] [--json] [--tolerance SECONDS]

Default tolerance: 5 seconds. Default output: text. Default scope: all
anchors with a Backlog.md file under the vault root.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
VAULT_ROOT = HOME / "ob" / "kmr"
STATE_FILE = HOME / ".config" / "ob-skills" / "backlog-edit" / "state.json"
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/")


def find_all_backlogs(vault_root: Path):
    """Walk the vault for `<SLUG> Backlog.md` files."""
    matches = []
    for root, dirs, files in os.walk(vault_root):
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        for f in files:
            if f.endswith(" Backlog.md"):
                slug = f[: -len(" Backlog.md")]
                matches.append((slug, Path(root) / f))
    return matches


def read_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text()).get("anchors", {})
    except json.JSONDecodeError:
        return {}


def classify(backlog_path: Path, state_entry, tolerance_seconds: int):
    """Return (status, mtime_iso, last_run_iso, delta_seconds)."""
    mtime = datetime.fromtimestamp(backlog_path.stat().st_mtime, tz=timezone.utc)
    mtime_iso = mtime.isoformat(timespec="seconds")
    if state_entry is None:
        return ("unknown", mtime_iso, None, None)
    try:
        last_run = datetime.fromisoformat(state_entry["last_run"])
    except (KeyError, ValueError):
        return ("unknown", mtime_iso, None, None)
    last_run_iso = last_run.isoformat(timespec="seconds")
    delta = (mtime - last_run).total_seconds()
    if delta > tolerance_seconds:
        return ("bypass", mtime_iso, last_run_iso, delta)
    return ("clean", mtime_iso, last_run_iso, delta)


def format_delta(delta_seconds):
    if delta_seconds is None:
        return "—"
    if delta_seconds < 60:
        return f"+{int(delta_seconds)}s"
    if delta_seconds < 3600:
        return f"+{int(delta_seconds / 60)}m"
    if delta_seconds < 86400:
        return f"+{delta_seconds / 3600:.1f}h"
    return f"+{delta_seconds / 86400:.1f}d"


def run_audit(scope_anchor=None, tolerance=5):
    state = read_state()
    backlogs = find_all_backlogs(VAULT_ROOT)
    if scope_anchor:
        backlogs = [(s, p) for s, p in backlogs if s == scope_anchor]
    results = []
    for slug, path in sorted(backlogs):
        status, mtime_iso, last_run_iso, delta = classify(
            path, state.get(slug), tolerance
        )
        results.append({
            "slug": slug,
            "path": str(path.relative_to(VAULT_ROOT)) if path.is_relative_to(VAULT_ROOT) else str(path),
            "status": status,
            "backlog_mtime": mtime_iso,
            "script_last_run": last_run_iso,
            "delta_seconds": delta,
        })
    return results


def print_text(results):
    bypass = [r for r in results if r["status"] == "bypass"]
    unknown = [r for r in results if r["status"] == "unknown"]
    clean = [r for r in results if r["status"] == "clean"]

    print(f"/audit integrity — {len(results)} backlog(s) scanned")
    print(f"  clean: {len(clean)}  bypass: {len(bypass)}  unknown: {len(unknown)}")
    print()

    if bypass:
        print("## Bypass — backlog edited after the script's last recorded run")
        print(f"  (tolerance threshold: see --tolerance; agent or user direct edit)")
        for r in bypass:
            print(f"  - {r['slug']:8s}  mtime {r['backlog_mtime']}  last script-run {r['script_last_run']}  delta {format_delta(r['delta_seconds'])}")
        print()

    if unknown:
        print("## Unknown — anchor has never been touched by backlog-edit.py")
        print(f"  (no state entry; the backlog file exists but its edits are all direct)")
        for r in unknown:
            print(f"  - {r['slug']:8s}  mtime {r['backlog_mtime']}")
        print()

    if not bypass and not unknown:
        print("All scanned anchors are clean — every backlog's most recent edit")
        print("was through backlog-edit.py.")


def main(argv):
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--anchor", help="restrict to a single slug")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument("--tolerance", type=int, default=5,
                   help="seconds of grace between script last-run and backlog mtime (default 5)")
    args = p.parse_args(argv[1:])

    results = run_audit(scope_anchor=args.anchor, tolerance=args.tolerance)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_text(results)
    bypass_count = sum(1 for r in results if r["status"] == "bypass")
    return 1 if bypass_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
