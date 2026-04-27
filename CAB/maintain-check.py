#!/usr/bin/env python3
"""Maintain check — scan maintenance table, find out-of-date items.

Usage:
    python3 maintain-check.py <anchor-path>

Outputs markdown to stdout listing items that need maintenance.
Outputs nothing if everything is current.
"""

import json
import os
import sys
import glob
from pathlib import Path


def find_maintenance_table(anchor_path: Path) -> Path | None:
    """Find the *Maintenance.md file in the Plan folder."""
    for md in anchor_path.rglob("*Maintenance.md"):
        if "Plan" in str(md):
            return md
    return None


def parse_maintenance_table(table_path: Path, event: str | None = None) -> list[dict]:
    """Parse the maintenance table markdown into rows.
    If event is None, return only file-based triggers (skip : prefixed).
    If event is set (e.g., 'pr'), return only rows with that :event trigger.
    """
    rows = []
    content = table_path.read_text(errors="replace")
    in_table = False
    for line in content.split("\n"):
        if not line.startswith("|"):
            in_table = False
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        trigger, action, desc = parts[1], parts[2], parts[3]
        if trigger in ("Trigger", "Source", "---", "") or "---" in trigger:
            in_table = True
            continue
        if not in_table or not trigger:
            continue
        # Strip backticks from trigger
        trigger = trigger.strip("`")
        if event:
            # Only return event triggers matching this event
            if trigger == f":{event}":
                rows.append({"trigger": trigger, "action": action, "description": desc})
        else:
            # Only return file triggers (skip : prefixed)
            if not trigger.startswith(":"):
                rows.append({"trigger": trigger, "action": action, "description": desc})
    return rows


def load_state(state_path: Path) -> dict:
    """Load the state file."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except Exception:
            return {}
    return {}


def save_state(state_path: Path, state: dict):
    """Save the state file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2))


def _load_code_path(anchor_path: Path) -> Path | None:
    """Read the `code:` key from the anchor's .anchor file and resolve it.
    Absolute paths are returned as-is; relative paths resolve against the
    anchor root. Returns None if the anchor has no code key.
    """
    anchor_file = anchor_path / ".anchor"
    if not anchor_file.is_file():
        return None
    try:
        import yaml
        cfg = yaml.safe_load(anchor_file.read_text()) or {}
    except Exception:
        return None
    code_val = cfg.get("code")
    if not code_val:
        return None
    p = Path(code_val)
    return p if p.is_absolute() else (anchor_path / p).resolve()


def get_newest_mtime(anchor_path: Path, source_pattern: str) -> float:
    """Get the newest mtime for a source pattern (supports globs).

    If the pattern starts with `Code/`, resolve the prefix via the
    `code:` key in the anchor's `.anchor` file (absolute, or relative
    to anchor root). No fallback to a legacy `Code` symlink.
    """
    if source_pattern.startswith("Code/"):
        code_root = _load_code_path(anchor_path)
        if code_root is None:
            raise RuntimeError(
                f"Maintenance trigger {source_pattern!r} uses the `Code/` "
                f"prefix but the anchor at {anchor_path} has no `code:` "
                f"key in its .anchor file. Add `code: <path>` to .anchor."
            )
        pattern = str(code_root / source_pattern[len("Code/"):])
    else:
        pattern = str(anchor_path / source_pattern)

    # Expand globs
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        # Try as a literal file
        p = Path(pattern)
        if p.exists():
            return p.stat().st_mtime
        return 0.0

    newest = 0.0
    for m in matches:
        try:
            mt = os.stat(m).st_mtime
            if mt > newest:
                newest = mt
        except OSError:
            continue
    return newest


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    anchor_path = Path(sys.argv[1]).resolve()
    table_path = find_maintenance_table(anchor_path)
    if not table_path:
        sys.exit(0)

    rows = parse_maintenance_table(table_path)
    if not rows:
        sys.exit(0)

    state_path = anchor_path / ".skl" / "maintain" / "state.json"
    state = load_state(state_path)

    pending = []
    state_changed = False

    for row in rows:
        trigger = row["trigger"]
        current_mtime = get_newest_mtime(anchor_path, trigger)
        if current_mtime == 0.0:
            continue  # source doesn't exist

        recorded = state.get(trigger, {})
        last_verified = recorded.get("last_verified", 0.0)

        if current_mtime > last_verified:
            pending.append(row)
            # Update source_mtime in state
            state[trigger] = {
                "source_mtime": current_mtime,
                "last_verified": last_verified,
            }
            state_changed = True

    if state_changed:
        save_state(state_path, state)

    if pending:
        print("⚠ **Maintenance needed** — run `/dev maintain` or `/cab maintain`:")
        for p in pending:
            print(f"  - `{p['trigger']}` → {p['action']}: {p['description']}")


if __name__ == "__main__":
    main()
