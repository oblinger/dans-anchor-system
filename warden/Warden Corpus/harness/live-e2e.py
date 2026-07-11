#!/usr/bin/env python3
"""Live end-to-end test (F221) — drive a REAL `claude` agent, prove the hook fired.

The end-to-end / live layer [[Warden Roadmap]] names: not "the dispatcher fires
in-process" (that is `test_warden_hook.py`) but "**Claude Code actually invokes
the hook in a real session**." This is the failure class the user flagged — the
engine can be perfect and the `settings.json` wiring / event shape / path
quoting still be wrong (the first run of this harness caught exactly that: an
unquoted hook path split on the space in "Skill Agent").

The loop, per piloted moment:

  1. stand up a scratch anchor with the `warden-selftest` funky trait +
     a project-scoped `.claude/settings.json` (via `warden install`);
  2. drive a **real** `claude -p` session in that anchor;
  3. read `$WARDEN_HOME/selftest.log` and assert the expected markers fired,
     with the right moment + anchor;
  4. flip `warden off` and re-drive — assert **no** markers (the kill switch
     works live, not just in a unit test).

Needs the `claude` CLI + working auth, so it is a **local / manual** gate, not
the fast CI unit loop (F221 OQ1). Run: `python3 live-e2e.py [--model sonnet]`.
Returns PASS/FAIL mechanically (exit 0 iff every live assertion holds).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                        # …/dans-anchor-system
WARDEN = REPO / "warden" / "engine" / "warden"

EXPECTED = {"session:start", "prompt:submit", "tool:post:Write", "write:markdown"}


def _warden(env: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(WARDEN), *args], env=env, capture_output=True, text=True)


def drive_agent(anchor: Path, env: dict, prompt: str, model: str) -> str:
    """Run one real headless claude session in `anchor`; return its stdout."""
    out = subprocess.run(
        ["claude", "-p", prompt, "--permission-mode", "bypassPermissions", "--model", model],
        cwd=str(anchor), env=env, capture_output=True, text=True, timeout=300)
    return (out.stdout or "") + (out.stderr or "")


def markers(home: Path) -> list[dict]:
    fp = home / "selftest.log"
    if not fp.is_file():
        return []
    return [json.loads(ln) for ln in fp.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="live-e2e")
    ap.add_argument("--model", default="sonnet", help="model for the driven agent (default: sonnet)")
    ap.add_argument("--keep", action="store_true", help="keep the scratch dir for inspection")
    args = ap.parse_args(argv)

    if shutil.which("claude") is None:
        print("live-e2e: `claude` CLI not found — this is a local/manual gate, skipping", file=sys.stderr)
        return 0

    tmp = Path(tempfile.mkdtemp(prefix="warden-live-e2e-"))
    home = tmp / "home"
    anchor = tmp / "anchor"
    anchor.mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: E2E\ntraits: [warden-selftest, Commit]\n", encoding="utf-8")
    env = {**os.environ, "WARDEN_HOME": str(home)}

    inst = _warden(env, "install", "--settings", str(anchor / ".claude" / "settings.json"))
    if inst.returncode != 0:
        print(f"live-e2e: install failed: {inst.stderr}", file=sys.stderr)
        return 1
    _warden(env, "on")

    fails: list[str] = []

    # CASE 1 — enabled: every piloted moment fires live.
    (home / "selftest.log").unlink(missing_ok=True)
    drive_agent(anchor, env, "Create a file named hello.md in the current directory "
                             "containing a single line of text. Then stop.", args.model)
    got = {m["moment"] for m in markers(home)}
    missing = EXPECTED - got
    if missing:
        fails.append(f"enabled: expected live firings missing {sorted(missing)} (got {sorted(got)})")
    else:
        print(f"PASS  enabled  → live firings {sorted(got)}")

    # CASE 2 — kill switch: `warden off` and nothing fires live.
    _warden(env, "off")
    (home / "selftest.log").unlink(missing_ok=True)
    drive_agent(anchor, env, "Create a file named hello2.md in the current directory "
                             "containing a single line of text. Then stop.", args.model)
    leaked = markers(home)
    if leaked:
        fails.append(f"kill switch: {len(leaked)} marker(s) fired despite `warden off`")
    else:
        print("PASS  warden off → NO live firings (kill switch works live)")
    _warden(env, "on")

    if not args.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print(f"scratch kept: {tmp}")

    if fails:
        print("\nFAIL")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("\nlive e2e passed — Warden fires in a real Claude Code session, and the kill switch stops it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
