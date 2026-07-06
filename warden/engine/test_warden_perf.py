#!/usr/bin/env python3
"""Performance gate for the live hot path (F214 perf layer / F213 phase 2).

Benches the installed dispatcher end-to-end — fork+exec of `warden-rs hook`
with a real event on stdin — in the two shapes that matter: a **no-fire** call
(the typical hook invocation: pure Rust, no daemon contact) and a **firing**
call whose Python bodies round-trip to the resident daemon.

The PRD budgets (~2 ms `tool:pre`, ~10 ms `tool:post`) are measured and held
locally (2026-07-05 bench: 2.98 ms no-fire / 3.71 ms firing); this gate's job
in CI is to **fail on order-of-magnitude regressions** — e.g. the hot path
accidentally re-acquiring a Python interpreter startup (~24 ms local, more on
CI) — so the ceilings carry CI-runner headroom above the local numbers rather
than restating the budget. Hermetic (scratch WARDEN_HOME); runnable standalone.
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

# CI-tolerant ceilings (mean over N calls). A Python-startup regression lands
# well above both on any hardware.
NOFIRE_CEILING_MS = 20.0
FIRE_CEILING_MS = 30.0
N = 30


def _env(home: Path) -> dict:
    return {**os.environ, "WARDEN_HOME": str(home)}


def _bench(cmd: list, inp: str, env: dict, n: int = N) -> float:
    subprocess.run(cmd, input=inp, capture_output=True, text=True, env=env)  # warm FS
    t0 = time.perf_counter()
    for _ in range(n):
        out = subprocess.run(cmd, input=inp, capture_output=True, text=True, env=env)
        assert out.returncode == 0
    return (time.perf_counter() - t0) / n * 1000


def main():
    home = Path(tempfile.mkdtemp(prefix="warden-perf-test-")) / "home"
    env = _env(home)
    out = subprocess.run([str(HERE / "warden"), "compile"],
                         capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    if not BIN.is_file():
        out = subprocess.run(["cargo", "build", "--release"], cwd=RS,
                             capture_output=True, text=True)
        assert out.returncode == 0, out.stderr

    daemon = subprocess.Popen(
        [sys.executable, str(HERE / "warden_daemon.py"), "--serve", "--idle-exit", "300"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            time.sleep(0.1)
            if (home / "daemon.sock").exists():
                break
        with tempfile.TemporaryDirectory() as td:
            fire_a = Path(td) / "F"
            fire_a.mkdir()
            (fire_a / ".anchor").write_text("slug: F\ntraits: [warden-selftest, Commit]\n",
                                            encoding="utf-8")
            quiet_a = Path(td) / "Q"
            quiet_a.mkdir()
            (quiet_a / ".anchor").write_text("slug: Q\ntraits: [Commit]\n", encoding="utf-8")

            def ev(anchor: Path) -> str:
                return json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Write",
                                   "tool_input": {"file_path": str(anchor / "note.md")},
                                   "cwd": str(anchor)})

            quiet_ms = _bench([str(BIN), "hook"], ev(quiet_a), env)
            fire_ms = _bench([str(BIN), "hook"], ev(fire_a), env)
            print(f"warden-rs hook mean of {N}: no-fire {quiet_ms:.2f} ms "
                  f"(ceiling {NOFIRE_CEILING_MS}) · firing {fire_ms:.2f} ms "
                  f"(ceiling {FIRE_CEILING_MS})")
            assert quiet_ms < NOFIRE_CEILING_MS, \
                f"no-fire hot path regressed: {quiet_ms:.2f} ms ≥ {NOFIRE_CEILING_MS} ms"
            assert fire_ms < FIRE_CEILING_MS, \
                f"firing hot path regressed: {fire_ms:.2f} ms ≥ {FIRE_CEILING_MS} ms"
    finally:
        if daemon.poll() is None:
            daemon.kill()
    print("\nwarden perf gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
