#!/usr/bin/env python3
"""test-t584-stopgate-no-self-measurement.py — TINK T584.

The crank Stop-gate spawns `claude -p` to classify the agent's final message
(`_llm_ask_check`). That subprocess ends a turn like any other, which fires the
same Stop hook inside itself — and the recursion guard that exists for it sat
at the top of `_llm_ask_check`, which is reached AFTER the triage-line check and
`_triage_log`. So every checker stop was recorded as though an agent had
stopped.

WHY THAT IS A MEASUREMENT BUG, NOT A LOGGING NUISANCE. The checker emits JSON
and never a TRIAGE line, so each of its stops is a structurally guaranteed
`missing`. The F306 D4 plan is "log the verdict on every crank stop, read the
rate after a week of real use, promote to blocking once it is a known number" —
and the number was never the agents': it was inflated by the gate observing
itself. Sixteen days on, the mode was still `warn`.

The evidence was sitting in the log the whole time. `msg_tail` was added for
exactly this adjudication (its own comment says the first week's 72% miss rate
"was unreadable for exactly that reason"), and of the 5 real-anchor `missing`
records carrying one, 4 are verbatim ask-check JSON. The instrument to catch
this was built; the read it existed for had never been run.

And in `enforce` mode it would have BLOCKED the checker's subprocess — a crank
sentinel covers its cwd, so it arms, and it can never print a TRIAGE line.

The fix is one guard moved from one stage to the entrypoint. What this file
pins is that it stays there: the assertions below are about ORDER, because a
guard that is merely present but late is exactly what was wrong.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "crank-stop-hook.py"
loader = importlib.machinery.SourceFileLoader("crank_stop_hook", str(SRC))
spec = importlib.util.spec_from_loader("crank_stop_hook", loader)
csh = importlib.util.module_from_spec(spec)
sys.modules["crank_stop_hook"] = csh
loader.exec_module(csh)

TMP = Path(tempfile.mkdtemp())
PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


ENV = csh.LLM_RECURSION_ENV
# The source names the constant, not its value — match the identifier.
GUARD = "os.environ.get(LLM_RECURSION_ENV)"
text = SRC.read_text(encoding="utf-8")

try:
    # ============================================================
    print("== A: the guard is at the ENTRYPOINT, not one stage in ==")
    #
    # Order is the whole assertion. The guard was already present in the file
    # before this fix — it was simply reached too late to protect the two
    # things that mattered. So "does it appear?" proves nothing; "does it
    # appear before the logging?" is the test.
    # ============================================================
    i_hook = text.index("def warden_hook(")
    i_guard = text.index(GUARD, i_hook)
    i_triage_log = text.index("_triage_log(", i_hook)
    # The CALL SITE, with its paren — prose mentions of the function name in
    # the comments around the guard are not call sites, and matching one of
    # those made this assertion compare the fix against its own explanation.
    i_llm = text.index("_llm_ask_check(", i_hook)

    if i_guard < i_triage_log:
        ok("the recursion guard precedes `_triage_log` — the checker is not logged")
    else:
        no("the guard is still after the logging: the checker pollutes the data")

    if i_guard < i_llm:
        ok("and it precedes the LLM check, so nothing downstream can arm first")
    else:
        no("the guard sits after the LLM-check call site")

    # It must be a RETURN, not a flag consulted later — an early allow.
    seg = text[i_guard:i_guard + 200]
    if "return None" in seg:
        ok("it returns immediately (allow), rather than setting a flag to honour")
    else:
        no(f"the guard does not return at once: {seg[:120]!r}")

    # ============================================================
    print("== B: a checker's stop is allowed and leaves no trace ==")
    # ============================================================
    gate_dir = TMP / "stopgate"
    gate_dir.mkdir(parents=True, exist_ok=True)
    log = gate_dir / "triage-line.jsonl"
    csh.GATE_DIR = gate_dir
    csh.TRIAGE_LOG = log

    anchor = TMP / "FIX"
    (anchor / "FIX Track").mkdir(parents=True, exist_ok=True)
    (anchor / ".anchor").write_text("slug: FIX\nfeeds:\n", encoding="utf-8")

    # The exact shape seen in the live log: the checker's JSON verdict, ending
    # a turn in a cwd an anchor covers.
    payload = {"cwd": str(anchor),
               "transcript_path": str(TMP / "nonexistent.jsonl"),
               "hook_event_name": "Stop"}

    prev = os.environ.get(ENV)
    os.environ[ENV] = "1"
    try:
        out = csh.warden_hook(payload)
    finally:
        if prev is None:
            os.environ.pop(ENV, None)
        else:
            os.environ[ENV] = prev

    if out is None:
        ok("a stop inside the checker is ALLOWED — it can never satisfy the gate")
    else:
        no(f"the checker's own stop was gated: {out}")

    if not log.exists() or not log.read_text(encoding="utf-8").strip():
        ok("and nothing is written to the triage log, so D4's data stays clean")
    else:
        no(f"the checker still logged a verdict: {log.read_text()[:160]}")

    # ============================================================
    print("== C: the guard is narrow — a real stop is unaffected ==")
    #
    # A guard that silenced every stop would 'fix' this by disabling the gate.
    # With the env var absent the function must still do its work; the fixture
    # has no crank sentinel and no worklist, so allowing is the correct answer
    # here — what is asserted is that it got there by RUNNING, not by the
    # early return.
    # ============================================================
    os.environ.pop(ENV, None)
    reached = {"n": 0}
    real_sentinel = csh._crank_sentinel_for
    csh._crank_sentinel_for = lambda cwd: reached.__setitem__("n", reached["n"] + 1)
    try:
        csh.warden_hook(payload)
    except Exception:
        pass                      # downstream may fail on the stub; irrelevant
    finally:
        csh._crank_sentinel_for = real_sentinel

    if reached["n"] == 1:
        ok("without the env var the gate proceeds past the guard as before")
    else:
        no("a normal stop no longer reaches the gate body — the guard is too wide")

    # ============================================================
    print("== D: the guard the fix did NOT remove ==")
    #
    # `_llm_ask_check` keeps its own guard. Belt and braces is right here: the
    # entrypoint guard protects the logging path, and this one keeps protecting
    # the spawn path for any future caller that reaches the check directly.
    # ============================================================
    i_check = text.index("def _llm_ask_check(")
    nxt = text.index("\ndef ", i_check + 10)
    if GUARD in text[i_check:nxt]:
        ok("`_llm_ask_check` keeps its own guard — the spawn path stays protected")
    else:
        no("the inner guard was removed; a direct caller could recurse")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
