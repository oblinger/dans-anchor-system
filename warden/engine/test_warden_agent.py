#!/usr/bin/env python3
"""Scripted state fixtures for the F216 agent-state model (F214 layer 1).

Each fixture is a synthetic transcript JSONL tail (the Claude Code record
shape: `{"type": "user"|"assistant", "message": {...}, "timestamp": ISO}`)
driving the classifier into one state — mid-task, question dialog up, text
ask, stopped-with-open-work, clean land, long-quiet, crash ambiguity —
asserting `agent.state` (and skill / state_seconds / open_tasks) per the F216
design. Plus the Success-Criteria fixture rule: a `body_py` rule that fires
its tell only in the `asking` state, run through the reference fire path.
Runnable standalone (`python3 test_warden_agent.py`) — no test framework.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_agent as wa  # noqa: E402
import warden_fire as wf  # noqa: E402

NOW = datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc)
NOW_TS = NOW.timestamp()


def _iso(seconds_ago: float) -> str:
    return (NOW - timedelta(seconds=seconds_ago)).isoformat().replace("+00:00", "Z")


def _user(text: str, ago: float) -> dict:
    return {"type": "user", "timestamp": _iso(ago),
            "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def _tool_result(ago: float) -> dict:
    return {"type": "user", "timestamp": _iso(ago),
            "message": {"role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": "t1"}]}}


def _assistant(ago: float, text: str | None = None, tools: list[dict] | None = None) -> dict:
    content: list = []
    if text is not None:
        content.append({"type": "text", "text": text})
    for t in tools or []:
        content.append({"type": "tool_use", "id": "t1", "name": t["name"],
                        "input": t.get("input", {})})
    return {"type": "assistant", "timestamp": _iso(ago),
            "message": {"role": "assistant", "content": content}}


def _write_transcript(tmp: Path, records: list[dict], name: str = "s.jsonl") -> Path:
    p = tmp / name
    p.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    # pin the file mtime to the newest record so the classifier's
    # freshness signal matches the fixture's injected clock
    ts = [datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).timestamp()
          for r in records if r.get("timestamp")]
    if ts:
        os.utime(p, (max(ts), max(ts)))
    return p


def _agent(tmp: Path, records: list[dict], trigger: str | None = None,
           sid: str = "sess-1") -> wa.AgentView:
    tp = _write_transcript(tmp, records, f"{sid}.jsonl")
    return wa.AgentView({"session_id": sid, "transcript_path": str(tp)}, trigger, NOW_TS)


def test_states(tmp: Path):
    """Each of the five states + unknown, from scripted transcripts."""
    # working — the user just prompted; the agent holds control
    a = _agent(tmp, [_user("do the thing", 5)], trigger="prompt:submit")
    assert a.state == "working", a.state
    # working (R3, no trigger) — last record ends on a running tool_use
    a = _agent(tmp, [_user("go", 60),
                     _assistant(30, "on it", [{"name": "Bash", "input": {"command": "ls"}}])])
    assert a.state == "working", a.state
    # asking (T1) — the AskUserQuestion dialog is up, unanswered
    a = _agent(tmp, [_user("go", 60),
                     _assistant(5, None, [{"name": "AskUserQuestion",
                                           "input": {"questions": []}}])],
               trigger="prompt:stop")
    assert a.state == "asking" and a.is_asking, a.state
    # asking (T2) — the closing text asks; sticky (no decay even hours later)
    a = _agent(tmp, [_user("go", 7300),
                     _assistant(7200, "Done reading.\n\nShould I also migrate the tests?")],
               trigger="prompt:stop")
    assert a.state == "asking", a.state
    # asking (T2 options pattern)
    a = _agent(tmp, [_user("go", 60),
                     _assistant(5, "Two ways:\n\n**(A)** keep both\n**(B)** merge them")],
               trigger="prompt:stop")
    assert a.state == "asking", a.state
    # paused — clean text but the harness task list still holds open items
    a = _agent(tmp, [_user("go", 60),
                     _assistant(40, "Starting.", [{"name": "TaskCreate",
                                                   "input": {"subject": "port the tests"}}]),
                     _tool_result(39),
                     _assistant(5, "Stopping here for today.")],
               trigger="prompt:stop")
    assert a.state == "paused", a.state
    assert a.open_tasks == 1, a.open_tasks
    # landed — clean end, tasks all closed
    a = _agent(tmp, [_user("go", 60),
                     _assistant(40, "Starting.", [{"name": "TaskCreate",
                                                   "input": {"subject": "port"}}]),
                     _tool_result(39),
                     _assistant(20, "Closing.", [{"name": "TaskUpdate",
                                                  "input": {"taskId": "1", "status": "completed"}}]),
                     _tool_result(19),
                     _assistant(5, "All done, committed as abc123.")],
               trigger="prompt:stop")
    assert a.state == "landed", a.state
    assert a.open_tasks == 0, a.open_tasks
    # idle — landed decays after T_idle of quiet
    a = _agent(tmp, [_user("go", 1000), _assistant(700, "All done.")])
    assert a.state == "idle", a.state
    # unknown — crash ambiguity: mid-turn but silent past T_dead
    a = _agent(tmp, [_user("go", 2000)])
    assert a.state == "unknown", a.state
    # unknown — the honest floor: no session mapping at all
    assert wa.unbound().state == "unknown"
    assert wa.unbound().skill is None
    assert wa.unbound().is_asking is False
    assert wa.unbound().open_tasks is None
    print("PASS  states")


def test_state_seconds_and_skill(tmp: Path):
    """state_seconds tracks the quiet window; agent.skill from the transcript
    sniff (Skill tool_use / <command-name> tag), current turn only."""
    a = _agent(tmp, [_user("go", 7300),
                     _assistant(7200, "Need a decision — proceed with the rename?")],
               trigger="prompt:stop")
    assert a.state == "asking"
    assert a.state_seconds is not None and 7100 <= a.state_seconds <= 7300, a.state_seconds
    # skill via Skill tool_use in the current turn
    a = _agent(tmp, [_user("run it", 60),
                     _assistant(30, None, [{"name": "Skill", "input": {"skill": "audit-q"}}])],
               trigger="tool:post:Skill")
    assert a.state == "working" and a.skill == "audit-q", (a.state, a.skill)
    # skill via <command-name> tag in the invoking prompt
    a = _agent(tmp, [_user("<command-name>/crank</command-name>", 60),
                     _assistant(5, "Cranking.")], trigger="prompt:stop")
    assert a.skill == "crank", a.skill
    # a PREVIOUS turn's skill does not leak into the current turn
    a = _agent(tmp, [_user("<command-name>/crank</command-name>", 300),
                     _assistant(200, "Done."),
                     _user("thanks, now just tell me the time", 60),
                     _assistant(5, "It is noon.")], trigger="prompt:stop")
    assert a.skill is None, a.skill
    print("PASS  state_seconds_and_skill")


def test_ledger_and_registry(tmp: Path):
    """The daemon-side registry/ledger: observe() accumulates moments; a
    skill:pre in the ledger (rank 1) answers agent.skill; classification is
    cached per AgentView (one read per pass)."""
    wa.REGISTRY.clear()
    tp = _write_transcript(tmp, [_user("go", 10)], "ledger.jsonl")
    sess = {"session_id": "sess-L", "transcript_path": str(tp)}
    wa.observe(sess, "prompt:submit", NOW_TS - 9)
    wa.observe(sess, "skill:pre:groom", NOW_TS - 5)
    a = wa.AgentView(sess, "skill:pre:groom", NOW_TS)
    assert a.state == "working" and a.skill == "groom", (a.state, a.skill)
    # ledger ring is bounded; registry maps the session
    assert wa.REGISTRY["sess-L"].transcript_path == str(tp)
    assert wa.REGISTRY["sess-L"].ledger.maxlen == 256
    # per-pass cache: mutate the transcript after the first read — answer holds
    first = a.state
    _write_transcript(tmp, [_user("go", 10), _assistant(1, "Question for you?")], "ledger.jsonl")
    assert a.state == first, "classification not cached per pass"
    wa.REGISTRY.clear()
    print("PASS  ledger_and_registry")


def test_fixture_rule_fires_only_when_asking(tmp: Path):
    """The Success-Criteria fixture: a rule whose body reads ctx.agent fires
    its tell only in the `asking` state, through the reference fire path."""
    ir = {"rules": {"R-ex-10": {"moment": "prompt:stop", "phase": "stop",
                                "where": None, "guards": [], "guard_py": None,
                                "action": None, "body_py": "body_R_ex_10"}},
          "moments": {"prompt:stop": ["R-ex-10"]},
          "traits": {"_base": ["R-ex-10"]}, "doc_rules": []}
    module = types.SimpleNamespace(
        body_R_ex_10=lambda ctx: (["[warden] a question is pending — surface it in the queue"]
                                  if ctx.agent.state == "asking" else []))
    asking = _agent(tmp, [_user("go", 60), _assistant(5, "Proceed with the rename?")],
                    trigger="prompt:stop", sid="fx-ask")
    landed = _agent(tmp, [_user("go", 60), _assistant(5, "All done.")],
                    trigger="prompt:stop", sid="fx-land")
    root = tmp / "anchor"
    root.mkdir(exist_ok=True)
    (root / ".anchor").write_text("slug: FX\n", encoding="utf-8")
    out = wf.fire(ir, module, "prompt:stop",
                  wf.build_ctx(root, "prompt:stop", agent=asking), ["_base"])
    assert out and "question is pending" in out[0], out
    out = wf.fire(ir, module, "prompt:stop",
                  wf.build_ctx(root, "prompt:stop", agent=landed), ["_base"])
    assert out == [], out
    # and build_ctx's default agent is the unbound error-value view
    ctx = wf.build_ctx(root, "prompt:stop")
    assert ctx.agent.state == "unknown" and ctx.agent.skill is None
    print("PASS  fixture_rule_fires_only_when_asking")


def test_tail_robustness(tmp: Path):
    """Fail-safe plumbing: missing transcript, garbage lines, huge tails."""
    a = wa.AgentView({"session_id": "gone", "transcript_path": str(tmp / "nope.jsonl")},
                     None, NOW_TS)
    assert a.state == "unknown", a.state   # mapping given but nothing readable
    p = tmp / "garbage.jsonl"
    p.write_text("not json\n" + json.dumps(_assistant(5, "All done.")) + "\n",
                 encoding="utf-8")
    a = wa.AgentView({"session_id": "g", "transcript_path": str(p)}, "prompt:stop", NOW_TS)
    assert a.state == "landed", a.state
    # oversized tail: only the window is read, classification still lands
    big = [_user("x" * 2000, 5000 - i) for i in range(400)] + [_assistant(5, "All done.")]
    a = _agent(tmp, big, trigger="prompt:stop", sid="big")
    assert a.state == "landed", a.state
    print("PASS  tail_robustness")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_states(tmp)
        test_state_seconds_and_skill(tmp)
        test_ledger_and_registry(tmp)
        test_fixture_rule_fires_only_when_asking(tmp)
        test_tail_robustness(tmp)
    print("\nall warden_agent tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
