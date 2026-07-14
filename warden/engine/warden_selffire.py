"""warden_selffire — writer scripts self-fire Warden (fork 9 option A, 2026-07-13).

Warden's write coverage is the `PostToolUse Write|Edit` hook — agent tool
calls only. Files written by scripts (queries-render, state/backlog-edit,
md-toc, audit fixers) bypass every moment, leaving the vault's most
systematically-produced surfaces ungoverned (the F230/C46 incident: a
non-conformant queries render circulated for days with nothing firing).

Option A closes the gap at the writer: after a script writes a file it calls
`fire_write(path)`, which synthesizes the same PostToolUse payload an agent
Write would produce and pipes it to the installed hook dispatcher — identical
dispatch path, identical rules, identical fire log.

Best-effort by design: Warden disabled or uninstalled (kill switch, no hook
in settings.json) means silence — matching hook behavior — and a self-fire
must never break the write it reports on. Steer text goes to stderr so the
invoking agent sees findings inline in the script's output.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

_SETTINGS = Path.home() / ".claude" / "settings.json"
_hook_cmd_cache: Optional[list[str]] = None
_hook_cmd_resolved = False


def _hook_command() -> Optional[list[str]]:
    """The installed PostToolUse warden dispatcher from settings.json — the
    same binary agent writes go through, so rust/python cutovers are picked
    up automatically. None when Warden isn't installed."""
    global _hook_cmd_cache, _hook_cmd_resolved
    if _hook_cmd_resolved:
        return _hook_cmd_cache
    _hook_cmd_resolved = True
    try:
        settings = json.loads(_SETTINGS.read_text(encoding="utf-8"))
        for entry in settings.get("hooks", {}).get("PostToolUse", []):
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                if "warden" in cmd.lower():
                    # Commands are shell-quoted ('/path/warden-rs' hook);
                    # split on the trailing verb, strip the quotes.
                    parts = cmd.rsplit(" ", 1)
                    if len(parts) == 2:
                        _hook_cmd_cache = [parts[0].strip("'\""), parts[1]]
                    return _hook_cmd_cache
    except (OSError, ValueError, KeyError):
        pass
    return None


def fire_write(path: Path | str, quiet: bool = False) -> Optional[str]:
    """Report a script-written file to Warden as if the agent Write tool wrote
    it. Returns the steer text (also printed to stderr unless quiet), or None
    when Warden is off/uninstalled, times out, or has nothing to say. Never
    raises."""
    cmd = _hook_command()
    if cmd is None:
        return None
    payload = json.dumps({
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": str(path)},
    })
    try:
        result = subprocess.run(
            cmd + ["hook"] if cmd[-1] != "hook" else cmd,
            input=payload, text=True, capture_output=True, timeout=10,
        )
        out = (result.stdout or "").strip()
        if not out:
            return None
        ctx = (json.loads(out).get("hookSpecificOutput", {})
               .get("additionalContext", "")).strip()
        if ctx and not quiet:
            print(f"[warden self-fire] {ctx}", file=sys.stderr)
        return ctx or None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
