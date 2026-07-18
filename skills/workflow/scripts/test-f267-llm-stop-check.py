#!/usr/bin/env python3
"""test-f267-llm-stop-check.py — the F267 LLM stage-2 stop-check in crank-stop-hook.py.

Deterministic + offline: the LLM call (`claude -p`) is mocked, so the suite tests
the extraction / guard / fail-open / parse / log paths without a real model call.
Set F267_LIVE=1 to additionally run one real Haiku classification.
"""
import importlib.util
import json
import os
import subprocess as real_subprocess
import tempfile
from pathlib import Path

HOOK = Path.home() / ".claude/skills/workflow/scripts/crank-stop-hook.py"


def _load():
    spec = importlib.util.spec_from_file_location("csh", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _transcript(td, final_text):
    tx = td / "tx.jsonl"
    tx.write_text("\n".join(json.dumps(x) for x in [
        {"type": "user", "message": {"content": "do the thing"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {}}]}},
        {"type": "user", "message": {"content": [
            {"type": "tool_result", "content": "ok"}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": final_text}]}},
    ]))
    return tx


class _MockSubprocess:
    """Stand-in for the `subprocess` module: `.run` returns a canned stdout."""
    SubprocessError = real_subprocess.SubprocessError
    TimeoutExpired = real_subprocess.TimeoutExpired

    def __init__(self, stdout):
        self._stdout = stdout

    def run(self, *a, **k):
        class R:
            pass
        r = R()
        r.stdout = self._stdout
        r.returncode = 0
        return r


PASS = 0
FAIL = 0


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def main():
    m = _load()
    td = Path(tempfile.mkdtemp())
    m.GATE_DIR = td
    m.LLM_CHECK_LOG = td / "llm-check.jsonl"

    mux = ("Cleaned up the duplicates. Standing by on one decision: give me "
           "the go and I'll deploy the fix.")
    tx = _transcript(td, mux)

    # 1 — extraction
    t = m._last_assistant_text(str(tx))
    check("give me the go" in t and "Standing by" in t,
          "extracts the final assistant message")

    # 2 — recursion guard
    os.environ[m.LLM_RECURSION_ENV] = "1"
    m._llm_ask_check({"transcript_path": str(tx)}, "TEST")
    check(not m.LLM_CHECK_LOG.exists(), "recursion guard (env set) → no log")
    del os.environ[m.LLM_RECURSION_ENV]

    # 3 — fail-open when the LLM call raises
    class _Raise:
        SubprocessError = real_subprocess.SubprocessError
        TimeoutExpired = real_subprocess.TimeoutExpired

        def run(self, *a, **k):
            raise OSError("no claude")
    m.subprocess = _Raise()
    m._llm_ask_check({"transcript_path": str(tx)}, "TEST")
    check(not m.LLM_CHECK_LOG.exists(), "fail-open (LLM raises) → no crash, no log")

    # 4 — short message is skipped (no log, no call)
    m.subprocess = _MockSubprocess('{"asking": true, "summary": "x"}')
    m._llm_ask_check({"transcript_path": str(_transcript(td, "ok"))}, "TEST")
    check(not m.LLM_CHECK_LOG.exists(), "short final message (<15 chars) → skipped")

    # 5 — mocked asking=true → one verdict row logged, parsed correctly
    m.subprocess = _MockSubprocess(
        '{"asking": true, "summary": "Approve deploy of the fix?"}')
    m._llm_ask_check({"transcript_path": str(_transcript(td, mux))}, "MUX")
    lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
    rec = json.loads(lines[-1]) if lines else {}
    check(len(lines) == 1 and rec.get("asking") is True
          and rec.get("anchor") == "MUX" and "ts" in rec,
          "mocked asking=true → verdict logged (asking/anchor/ts)")

    # 6 — markdown-fenced JSON is still parsed
    m.LLM_CHECK_LOG.unlink(missing_ok=True)
    m.subprocess = _MockSubprocess('```json\n{"asking": false, "summary": ""}\n```')
    m._llm_ask_check({"transcript_path": str(_transcript(td, mux))}, "MUX")
    lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
    rec = json.loads(lines[-1]) if lines else {}
    check(len(lines) == 1 and rec.get("asking") is False,
          "fenced ```json``` output is parsed")

    m.subprocess = real_subprocess

    # optional — one real Haiku call
    if os.environ.get("F267_LIVE"):
        m.LLM_CHECK_LOG.unlink(missing_ok=True)
        m._llm_ask_check({"transcript_path": str(_transcript(td, mux))}, "LIVE")
        lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
        rec = json.loads(lines[-1]) if lines else {}
        check(rec.get("asking") is True, "LIVE Haiku call classifies MUX msg asking=true")

    print("-" * 40)
    print(f"F267 LLM stop-check test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
