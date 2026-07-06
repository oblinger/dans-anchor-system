#!/usr/bin/env python3
"""Differential test: `warden-rs hook` ≡ `warden_hook.py` (F213 phase 2).

The Rust dispatcher must be behavior-identical to the Python live hook — same
event payloads in, same hook output out (structurally: hookEventName +
additionalContext; the JSON whitespace differs between json.dumps and
serde_json). Each case pipes the identical event JSON into both dispatchers
under the same scratch `WARDEN_HOME` (compiled corpus + a running resident
daemon for the Rust side's Python-body round-trips) and diffs the parsed
output. Cases cover: python-body rules firing (selftest anchor), trait gating
(silence), audit-on-write (daemon doc-fire), the kill switch, and malformed
stdin. Requires `cargo build --release` (run by the test if the binary is
missing). Runnable standalone.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RS = HERE.parent / "rs"
BIN = RS / "target" / "release" / "warden-rs"
sys.path.insert(0, str(HERE))

_HOME = None
_PROC = None


def _env(home: Path, **extra) -> dict:
    return {**os.environ, "WARDEN_HOME": str(home), **extra}


def _compiled_home() -> Path:
    global _HOME
    if _HOME is None:
        _HOME = Path(tempfile.mkdtemp(prefix="warden-hookrs-test-")) / "home"
        out = subprocess.run([str(HERE / "warden"), "compile"],
                             capture_output=True, text=True, env=_env(_HOME))
        assert out.returncode == 0, out.stderr
    return _HOME


def _ensure_binary():
    if not BIN.is_file():
        out = subprocess.run(["cargo", "build", "--release"], cwd=RS,
                             capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
    assert BIN.is_file()


def _start_daemon(home: Path):
    global _PROC
    _PROC = subprocess.Popen(
        [sys.executable, str(HERE / "warden_daemon.py"), "--serve", "--idle-exit", "120"],
        env=_env(home), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        time.sleep(0.1)
        if (home / "daemon.sock").exists():
            return
    raise AssertionError("daemon did not come up")


def _run(cmd: list, event: dict | str, env: dict) -> dict | None:
    raw = event if isinstance(event, str) else json.dumps(event)
    out = subprocess.run(cmd, input=raw, capture_output=True, text=True, env=env)
    assert out.returncode == 0, f"{cmd} exited {out.returncode}: {out.stderr}"
    return json.loads(out.stdout) if out.stdout.strip() else None


def _both(event: dict | str, env: dict) -> tuple:
    py = _run(["python3", str(HERE / "warden_hook.py")], event, env)
    rs = _run([str(BIN), "hook"], event, env)
    return py, rs


def _anchor(tmp: Path, traits: str) -> Path:
    a = tmp / "FX"
    a.mkdir(parents=True)
    (a / ".anchor").write_text(f"slug: FX\ntraits: [{traits}]\n", encoding="utf-8")
    return a


def _diff_case(name: str, event: dict | str, env: dict, expect_output: bool | None = None):
    py, rs = _both(event, env)
    assert py == rs, f"{name}: python {py!r} != rust {rs!r}"
    if expect_output is True:
        assert py is not None, f"{name}: expected steers, both silent"
    if expect_output is False:
        assert py is None, f"{name}: expected silence, got {py!r}"
    print(f"PASS  differential: {name}")


def main():
    home = _compiled_home()
    _ensure_binary()
    _start_daemon(home)
    env = _env(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            selftest = _anchor(Path(td) / "s", "warden-selftest, Commit")
            plain = _anchor(Path(td) / "p", "Commit")
            aow = _anchor(Path(td) / "a", "audit-on-write")
            bad = aow / "FX Messages.md"
            bad.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")

            # 1. python-body rules fire through the daemon (2 selftest steers)
            _diff_case("selftest write fires body_py rules",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(selftest / "note.md")},
                        "cwd": str(selftest)}, env, expect_output=True)
            # 2. trait gating — same event, no funky trait, both silent
            _diff_case("trait gating silences",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(plain / "note.md")},
                        "cwd": str(plain)}, env, expect_output=False)
            # 3. audit-on-write — the doc-fire steers through the daemon
            _diff_case("audit-on-write doc-fire",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(bad)},
                        "cwd": str(aow)}, env, expect_output=True)
            # 4. session:start on a plain anchor — nothing keyed, silent
            _diff_case("session:start plain anchor",
                       {"hook_event_name": "SessionStart", "cwd": str(plain)}, env,
                       expect_output=False)
            # 5. kill switch — env var silences both (before any work)
            _diff_case("kill switch (env)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(selftest / "note.md")},
                        "cwd": str(selftest)},
                       _env(home, WARDEN_DISABLED="1"), expect_output=False)
            # 6. malformed stdin — both no-op, exit 0
            _diff_case("malformed stdin", "not json {", env, expect_output=False)
            # 7. non-anchor cwd — both silent
            _diff_case("non-anchor cwd",
                       {"hook_event_name": "SessionStart", "cwd": "/"}, env,
                       expect_output=False)
    finally:
        if _PROC and _PROC.poll() is None:
            _PROC.kill()
    print("\nall warden-rs hook differential tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
