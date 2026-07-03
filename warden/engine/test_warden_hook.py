#!/usr/bin/env python3
"""Tests for warden_hook.py — the live hook dispatcher (F220).

Covers the event→moment mapping, the kill switch (checked before any work), the
dispatch→fire→log path (the selftest rule writes its marker), and active-set
gating (an anchor without the funky trait fires nothing). Hermetic: a scratch
`WARDEN_HOME` holds both the compiled corpus and the selftest log, so nothing
touches the real `~/.warden`. Runnable standalone.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import warden_hook as wh  # noqa: E402

_HOME = None  # a compiled scratch WARDEN_HOME shared across the dispatch tests


def _compiled_home() -> Path:
    """Compile the corpus once into a scratch home; reuse for the process."""
    global _HOME
    if _HOME is None:
        _HOME = Path(tempfile.mkdtemp(prefix="warden-hook-test-")) / "home"
        env = {**os.environ, "WARDEN_HOME": str(_HOME)}
        out = subprocess.run([str(HERE / "warden"), "compile"],
                             capture_output=True, text=True, env=env)
        assert out.returncode == 0, out.stderr
        assert (_HOME / "rules-ir.json").is_file(), "compile produced no IR"
    return _HOME


def _anchor(tmp: Path, traits: str) -> Path:
    a = tmp / "FX"
    a.mkdir(parents=True)
    (a / ".anchor").write_text(f"slug: FX\ntraits: [{traits}]\n", encoding="utf-8")
    return a


def test_event_to_moments():
    e = wh.event_to_moments
    assert e({"hook_event_name": "PostToolUse", "tool_name": "Write",
              "tool_input": {"file_path": "x.md"}}) == ["tool:post:Write", "write:markdown"]
    assert e({"hook_event_name": "PostToolUse", "tool_name": "Bash"}) == ["tool:post:Bash"]
    assert e({"hook_event_name": "PreToolUse", "tool_name": "Bash"}) == ["tool:pre:Bash"]
    assert e({"hook_event_name": "PreToolUse", "tool_name": "Skill",
              "tool_input": {"skill": "audit-q"}}) == ["skill:pre:audit-q"]
    assert e({"hook_event_name": "UserPromptSubmit"}) == ["prompt:submit"]
    assert e({"hook_event_name": "SessionStart"}) == ["session:start"]
    assert e({"hook_event_name": "PreCompact"}) == ["session:compact"]
    assert e({"hook_event_name": "Nonsense"}) == []
    print("PASS  event_to_moments")


def test_kill_switch():
    with tempfile.TemporaryDirectory() as td:
        os.environ.pop("WARDEN_DISABLED", None)
        old = os.environ.get("WARDEN_HOME")
        os.environ["WARDEN_HOME"] = td
        try:
            assert wh.disabled() is False, "enabled by default"
            (Path(td) / "DISABLED").write_text("x", encoding="utf-8")
            assert wh.disabled() is True, "sentinel file disables"
            (Path(td) / "DISABLED").unlink()
            assert wh.disabled() is False
            os.environ["WARDEN_DISABLED"] = "1"
            assert wh.disabled() is True, "env var disables"
            os.environ.pop("WARDEN_DISABLED")
        finally:
            if old is None:
                os.environ.pop("WARDEN_HOME", None)
            else:
                os.environ["WARDEN_HOME"] = old
    print("PASS  kill_switch")


def _read_markers(home: Path) -> list[dict]:
    fp = home / "selftest.log"
    if not fp.is_file():
        return []
    return [json.loads(ln) for ln in fp.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_dispatch_fires_and_logs():
    home = _compiled_home()
    (home / "selftest.log").unlink(missing_ok=True)
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "warden-selftest, Commit")
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(anchor / "note.md")}, "cwd": str(anchor)}
            steers = wh.dispatch(event)
            # a markdown Write fires BOTH tool:post:Write and write:markdown
            assert len(steers) == 2, steers
            markers = _read_markers(home)
            rules = {m["rule"] for m in markers}
            assert rules == {"R-warden-selftest-01", "R-warden-selftest-02"}, markers
            assert all(m["anchor"] == "FX" for m in markers), markers
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  dispatch_fires_and_logs")


def test_trait_gating():
    home = _compiled_home()
    (home / "selftest.log").unlink(missing_ok=True)
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")  # no warden-selftest trait
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(anchor / "note.md")}, "cwd": str(anchor)}
            assert wh.dispatch(event) == [], "fired without the funky trait"
            assert _read_markers(home) == [], "logged without the funky trait"
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  trait_gating")


def main():
    test_event_to_moments()
    test_kill_switch()
    test_dispatch_fires_and_logs()
    test_trait_gating()
    print("\nall warden_hook tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
