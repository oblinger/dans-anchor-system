#!/usr/bin/env python3
"""test-f267-llm-stop-check.py — the F267 LLM stage-2 stop-check in crank-stop-hook.py.

Deterministic + offline: the LLM call (`claude -p`) is mocked, so the suite tests
extraction / guard / fail-open / parse / log AND the enforce path (fire-budget +
surfaced-check + block) without a real model call. Set F267_LIVE=1 to additionally
run one real Haiku classification.
"""
import importlib.util
import json
import os
import subprocess as real_subprocess
import tempfile
from pathlib import Path

HOOK = Path.home() / ".claude/skills/workflow/scripts/crank-stop-hook.py"
PASS = 0
FAIL = 0


def _load():
    spec = importlib.util.spec_from_file_location("csh", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _transcript(td, final_text, name="tx.jsonl"):
    tx = td / name
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


def _anchor(td, name, with_questions=False):
    a = td / name
    (a / "Track").mkdir(parents=True, exist_ok=True)
    body = "# BL\n\n## Now\n\n"
    if with_questions:
        body += "- **T001 — q** [Questions] — waiting ^T001\n"
    (a / "Track" / "X Backlog.md").write_text(body)
    return a


class _Mock:
    """subprocess stand-in: `.run` returns a canned stdout."""
    SubprocessError = real_subprocess.SubprocessError
    TimeoutExpired = real_subprocess.TimeoutExpired

    def __init__(self, stdout):
        self._stdout = stdout

    def run(self, *a, **k):
        class R:
            stdout = self._stdout
            returncode = 0
        return R()


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def _set_conf(m, mode, budget, fired=0):
    m.LLM_CONF.write_text(json.dumps({"mode": mode, "budget": budget, "fired": fired}))


def main():
    m = _load()
    td = Path(tempfile.mkdtemp())
    m.GATE_DIR = td
    m.LLM_CHECK_LOG = td / "llm-check.jsonl"
    m.LLM_CONF = td / "llm-check.conf"
    empty_anchor = str(_anchor(td, "empty"))
    q_anchor = str(_anchor(td, "hasq", with_questions=True))
    mux = ("Cleaned up the duplicates. Standing by on one decision: give me "
           "the go and I'll deploy the fix.")
    tx = _transcript(td, mux)

    def clear():
        m.LLM_CHECK_LOG.unlink(missing_ok=True)
        m.LLM_CONF.unlink(missing_ok=True)

    # 1 — extraction
    check("give me the go" in m._last_assistant_text(str(tx)),
          "extracts the final assistant message")

    # 2 — recursion guard
    clear()
    os.environ[m.LLM_RECURSION_ENV] = "1"
    r = m._llm_ask_check({"transcript_path": str(tx)}, "T", empty_anchor)
    check(r is None and not m.LLM_CHECK_LOG.exists(),
          "recursion guard (env set) → no log, no block")
    del os.environ[m.LLM_RECURSION_ENV]

    # 3 — fail-open when the LLM call raises
    clear()

    class _Raise:
        SubprocessError = real_subprocess.SubprocessError
        TimeoutExpired = real_subprocess.TimeoutExpired

        def run(self, *a, **k):
            raise OSError("no claude")
    m.subprocess = _Raise()
    r = m._llm_ask_check({"transcript_path": str(tx)}, "T", empty_anchor)
    check(r is None and not m.LLM_CHECK_LOG.exists(),
          "fail-open (LLM raises) → no crash, no log, no block")

    # 4 — short message skipped
    clear()
    m.subprocess = _Mock('{"asking": true, "summary": "x"}')
    r = m._llm_ask_check({"transcript_path": str(_transcript(td, "ok", "s.jsonl"))},
                         "T", empty_anchor)
    check(r is None and not m.LLM_CHECK_LOG.exists(),
          "short final message (<15 chars) → skipped")

    # 5 — INERT (no conf): asking=true logs a verdict but never blocks
    clear()
    m.subprocess = _Mock('{"asking": true, "summary": "Approve deploy?"}')
    r = m._llm_ask_check({"transcript_path": str(tx)}, "MUX", empty_anchor)
    lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
    rec = json.loads(lines[-1]) if lines else {}
    check(r is None and len(lines) == 1 and rec.get("asking") is True,
          "INERT: asking=true → logged, returns None (no block)")

    # 6 — fenced ```json``` parsed
    clear()
    m.subprocess = _Mock('```json\n{"asking": false, "summary": ""}\n```')
    m._llm_ask_check({"transcript_path": str(tx)}, "T", empty_anchor)
    lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
    check(len(lines) == 1 and json.loads(lines[-1]).get("asking") is False,
          "fenced ```json``` output is parsed")

    # 7 — ENFORCE budget=1, asking=true, empty queue → BLOCK + spend a fire
    clear()
    _set_conf(m, "enforce", 1, 0)
    m.subprocess = _Mock('{"asking": true, "summary": "Approve deploy?"}')
    r = m._llm_ask_check({"transcript_path": str(tx)}, "MUX", empty_anchor)
    spent = json.loads(m.LLM_CONF.read_text()).get("fired")
    check(isinstance(r, str) and "recorded in the queue" in r and spent == 1,
          "ENFORCE budget=1 + asking + empty queue → block, fire spent")

    # 8 — budget now spent → no block (still logs)
    r = m._llm_ask_check({"transcript_path": str(tx)}, "MUX", empty_anchor)
    check(r is None, "ENFORCE budget spent (fired>=budget) → no block")

    # 9 — asking=true but queue HAS an open [Questions] → surfaced → no block
    clear()
    _set_conf(m, "enforce", 1, 0)
    m.subprocess = _Mock('{"asking": true, "summary": "Approve deploy?"}')
    r = m._llm_ask_check({"transcript_path": str(tx)}, "MUX", q_anchor)
    check(r is None and json.loads(m.LLM_CONF.read_text()).get("fired") == 0,
          "ENFORCE + asking but queue has open question → surfaced → no block")

    # 10 — ENFORCE + asking=false → no block
    clear()
    _set_conf(m, "enforce", 1, 0)
    m.subprocess = _Mock('{"asking": false, "summary": ""}')
    r = m._llm_ask_check({"transcript_path": str(tx)}, "T", empty_anchor)
    check(r is None, "ENFORCE + asking=false → no block")

    m.subprocess = real_subprocess

    if os.environ.get("F267_LIVE"):
        clear()
        r = m._llm_ask_check({"transcript_path": str(tx)}, "LIVE", empty_anchor)
        lines = m.LLM_CHECK_LOG.read_text().splitlines() if m.LLM_CHECK_LOG.exists() else []
        check(lines and json.loads(lines[-1]).get("asking") is True,
              "LIVE Haiku call classifies MUX msg asking=true")

    print("-" * 40)
    print(f"F267 LLM stop-check test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
