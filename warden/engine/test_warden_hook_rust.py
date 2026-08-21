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
    # F328: pin the DAS hook registry to a scratch path so live registry
    # entries can never fire inside a differential run.
    base = {**os.environ, "WARDEN_HOME": str(home),
            "DAS_HOOK_REGISTRY": str(home / "das-registry"),
            "DAS_HOOK_LOG": str(home / "das-hook.log")}
    base.update(extra)
    return base


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
            # 8. C1: a SYMLINKED event path resolves to the same governing
            # anchor on both engines (Rust used to walk the literal path —
            # the link's parent has no .anchor, so it went silent).
            link = Path(td) / "link"
            os.symlink(selftest, link)
            _diff_case("symlinked file path governs by target anchor (F232 C1)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(link / "note.md")},
                        "cwd": "/"}, env, expect_output=True)
            # 9. C2: duplicate `traits:` keys — the Python reference's flow
            # search runs first, so the flow line wins even BELOW a block one
            # (Rust used to lock onto the first line whatever its shape).
            dup = Path(td) / "dup"
            dup.mkdir()
            (dup / ".anchor").write_text(
                "slug: DUP\ntraits:\n- warden-selftest\ntraits: [Commit]\n",
                encoding="utf-8")
            _diff_case("duplicate traits keys — flow wins (F232 C2)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(dup / "note.md")},
                        "cwd": str(dup)}, env)
            # 10. C2: a blank line INSIDE a block list — Python's regex
            # tolerates it (items after the blank still count); Rust used to
            # stop at the blank and drop the rest.
            blk = Path(td) / "blk"
            blk.mkdir()
            (blk / ".anchor").write_text(
                "slug: BLK\ntraits:\n- Commit\n\n- warden-selftest\n",
                encoding="utf-8")
            _diff_case("blank line inside block trait list (F232 C2)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": str(blk / "note.md")},
                        "cwd": str(blk)}, env, expect_output=True)
            # 11. C3: malformed payload FIELDS degrade per-field on both
            # engines — a non-string file_path / non-dict tool_input must not
            # zero out the dispatch (nor crash it).
            _diff_case("non-string file_path (F232 C3)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": {"file_path": {"evil": 1}},
                        "cwd": str(selftest)}, env)
            _diff_case("non-dict tool_input (F232 C3)",
                       {"hook_event_name": "PostToolUse", "tool_name": "Write",
                        "tool_input": "garbage", "cwd": str(selftest)}, env)
            _diff_case("non-string cwd (F232 C3)",
                       {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                        "tool_input": {"command": "echo hi"}, "cwd": 42}, env)
            # 12. F328 — both engines execute the DAS hook registry
            # identically: matching lines fire in file order, a child's
            # stdout joins additionalContext, a broken child is logged with
            # its exit and suppresses nothing, non-matching moments stay
            # silent. The log collects one pair of entries per engine.
            reg_home = Path(td) / "reg"
            reg_home.mkdir()
            tell = reg_home / "tell.sh"
            tell.write_text("#!/bin/bash\necho reg-tell\n")
            tell.chmod(0o755)
            broken = reg_home / "broken.sh"
            broken.write_text("#!/bin/bash\nexit 3\n")
            broken.chmod(0o755)
            registry = reg_home / "registry"
            registry.write_text(f"prompt:submit\t{broken}\n"
                                f"prompt:submit\t{tell}\n"
                                f"tool:pre:Bash\t{tell}\n")
            reg_log = reg_home / "log.txt"
            env_r = _env(home, DAS_HOOK_REGISTRY=str(registry),
                         DAS_HOOK_LOG=str(reg_log))
            py, rs = _both({"hook_event_name": "UserPromptSubmit",
                            "cwd": str(plain)}, env_r)
            assert py == rs, f"F328 registry: python {py!r} != rust {rs!r}"
            ctx = (py or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
            assert "reg-tell" in ctx, f"F328 registry: tell missing from {py!r}"
            log_text = reg_log.read_text()
            assert log_text.count("exit=3") == 2, f"broken child unlogged: {log_text}"
            assert log_text.count("  ok  ") == 2, f"working child unlogged: {log_text}"
            assert "tool:pre:Bash" not in log_text, f"moment filter leaked: {log_text}"
            print("PASS  differential: F328 registry fan-out (fire, isolate, filter)")
    finally:
        if _PROC and _PROC.poll() is None:
            _PROC.kill()
    print("\nall warden-rs hook differential tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
