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


def test_turn_view(tmp: Path):
    """F217: the six agent.turn members + the agent.response alias, from a
    scripted turn; unbound view reads error values; TURN_CAP truncation."""
    a = _agent(tmp, [
        _user("old turn", 300), _assistant(290, "old reply"),
        _user("Fix the flaky test?", 60),
        _assistant(50, "Looking.", [{"name": "Bash", "input": {"command": "pytest -k flaky"}}]),
        _tool_result(49),
        _assistant(5, "All tests pass — done.")], trigger="prompt:stop", sid="turn-1")
    t = a.turn
    assert t.user_said == "Fix the flaky test?", t.user_said
    assert "Looking." in t.agent_said and "All tests pass" in t.agent_said
    assert "old reply" not in t.agent_said, "prior turn leaked into agent_said"
    assert a.response == t.agent_said, "agent.response is the agent_said alias"
    assert ("Bash", "pytest -k flaky") in t.tools, t.tools
    assert t.commands == ["pytest -k flaky"], t.commands
    assert "USER: Fix the flaky test?" in t.text and "TOOL Bash:" in t.text
    assert len(t.messages) == 4, len(t.messages)
    # unbound → error values, reads never raise
    u = wa.unbound()
    assert u.turn.user_said == "" and u.turn.tools == [] and u.response == ""
    # TURN_CAP: head + tail survive an oversized member
    big = "CLAIM-AT-HEAD " + "x" * (wa.TURN_CAP * 2) + " QUESTION-AT-TAIL?"
    a2 = _agent(tmp, [_user("go", 60), _assistant(5, big)], trigger="prompt:stop", sid="turn-2")
    said = a2.turn.agent_said
    assert len(said) <= wa.TURN_CAP + 40, len(said)
    assert said.startswith("CLAIM-AT-HEAD") and said.rstrip().endswith("QUESTION-AT-TAIL?")
    print("PASS  turn_view")


def test_content_rules(tmp: Path):
    """F217 Success-Criteria fixtures: the question-kind rule (R-ex-11) and the
    done-claim-without-test rule (R-ex-12) fire on their turns and stay silent
    on a normal turn; a turn-bearing rule is skipped for an unbound agent."""
    import re as _re
    ir = {"rules": {
            "R-ex-11": {"moment": "prompt:stop", "phase": "stop", "where": None,
                        "guards": [], "guard_py": None, "action": None,
                        "body_py": "body_R_ex_11", "turn_bearing": True},
            "R-ex-12": {"moment": "prompt:stop", "phase": "stop", "where": None,
                        "guards": [], "guard_py": None, "action": None,
                        "body_py": "body_R_ex_12", "turn_bearing": True}},
          "moments": {"prompt:stop": ["R-ex-11", "R-ex-12"]},
          "traits": {"_base": ["R-ex-11", "R-ex-12"]}, "doc_rules": []}
    module = types.SimpleNamespace(
        body_R_ex_11=lambda ctx: (
            ["Low-stakes ordering choices are yours — pick an order and proceed."]
            if ctx.agent.is_asking and _re.search(r"(?i)\b(should i|which order|do you want me to)\b",
                                                  ctx.agent.response) else []),
        body_R_ex_12=lambda ctx: (
            ["You claimed completion but ran no test command — run the suite first."]
            if _re.search(r"(?i)\b(all tests pass|task (is )?done|completed?)\b", ctx.agent.response)
            and not any(c.startswith(("pytest", "just test", "cargo test"))
                        for c in ctx.agent.turn.commands) else []))
    root = tmp / "anchor17"
    root.mkdir(exist_ok=True)
    (root / ".anchor").write_text("slug: FX\n", encoding="utf-8")

    def fire_with(agent):
        return wf.fire(ir, module, "prompt:stop",
                       wf.build_ctx(root, "prompt:stop", agent=agent), ["_base"])

    # R-ex-11 fires: turn ends asking a low-stakes ordering question
    ask = _agent(tmp, [_user("go", 60),
                       _assistant(5, "Should I do the rename first or the tests first?")],
                 trigger="prompt:stop", sid="c-ask")
    out = fire_with(ask)
    assert any("yours" in s for s in out), out
    # R-ex-12 fires: done-claim, no test command in the turn's ledger
    claim = _agent(tmp, [_user("go", 60), _assistant(5, "Task done, everything works.")],
                   trigger="prompt:stop", sid="c-claim")
    out = fire_with(claim)
    assert any("no test command" in s for s in out), out
    # silent: done-claim WITH a test run, and no question
    clean = _agent(tmp, [_user("go", 60),
                         _assistant(30, "Running.", [{"name": "Bash",
                                                      "input": {"command": "pytest -q"}}]),
                         _tool_result(29),
                         _assistant(5, "All tests pass — landed.")],
                   trigger="prompt:stop", sid="c-clean")
    assert fire_with(clean) == [], fire_with(clean)
    # unbound agent → turn-bearing rules skipped wholesale (R4)
    assert fire_with(wa.unbound()) == []
    print("PASS  content_rules")


def test_turn_bearing_mark_and_key(tmp: Path):
    """The compiler marks turn-bearing rules; turn_key identifies the turn and
    survives a Stop-steer continuation (same key — no new prompt)."""
    import warden_compile as wc
    rs = {"source": "T.md", "name": "R-t", "where": None}
    base = {"tier": "checked", "when": "prompt:stop", "where": None, "check": None,
            "py_kind": "trigger"}
    row = wc.compile_rule({**base, "id": "R-t-01", "ifs": [],
                           "py_src": "def trigger(ctx):\n    return [] if not ctx.agent.turn.commands else ['x']"}, rs)
    assert row.get("turn_bearing") is True, row
    row = wc.compile_rule({**base, "id": "R-t-02", "ifs": ["agent.response != ''"],
                           "py_src": "def trigger(ctx):\n    return []"}, rs)
    assert row.get("turn_bearing") is True, row
    row = wc.compile_rule({**base, "id": "R-t-03", "ifs": [],
                           "py_src": "def trigger(ctx):\n    return []"}, rs)
    assert row.get("turn_bearing") is None, row
    # turn identity
    turn = [_user("go", 60), _assistant(5, "done")]
    k1 = wa.turn_key(turn)
    assert k1, "turn key missing"
    continuation = turn + [_assistant(2, "continuing after a steer")]
    assert wa.turn_key(continuation) == k1, "steer continuation changed the turn key"
    new_turn = continuation + [_user("next", 1), _assistant(0, "ok")]
    assert wa.turn_key(new_turn) != k1, "new prompt did not reset the turn key"
    print("PASS  turn_bearing_mark_and_key")


def test_daemon_turn_dedup(tmp: Path):
    """F217 loop fixture (wall 2): a turn-bearing rule fires once per
    (rule, session, turn) — the Stop-steer continuation (same turn, no new
    prompt) is suppressed; a genuinely new turn fires again."""
    import re as _re
    import warden_daemon as wd
    wd.TURN_FIRED.clear()
    wa.REGISTRY.clear()
    ir = {"rules": {"R-ex-11": {"moment": "prompt:stop", "phase": "stop",
                                "where": None, "guards": [], "guard_py": None,
                                "action": None, "body_py": "body_R_ex_11",
                                "turn_bearing": True}},
          "moments": {"prompt:stop": ["R-ex-11"]},
          "traits": {"_base": ["R-ex-11"]}, "doc_rules": []}
    module = types.SimpleNamespace(
        body_R_ex_11=lambda ctx: (["decide the order yourself"]
                                  if _re.search(r"(?i)\bshould i\b", ctx.agent.response) else []))
    corpus = types.SimpleNamespace(ir=ir, module=module)
    root = tmp / "anchor-dedup"
    root.mkdir(exist_ok=True)
    (root / ".anchor").write_text("slug: FX\n", encoding="utf-8")
    turn = [_user("go", 60), _assistant(5, "Should I rename first or test first?")]
    tp = _write_transcript(tmp, turn, "dedup.jsonl")
    req = {"moment": "prompt:stop", "anchor_root": str(root), "rule_ids": ["R-ex-11"],
           "session": {"session_id": "d-1", "transcript_path": str(tp)}}
    r1 = wd._fire_rules(corpus, req)
    assert r1["steers_by_rule"]["R-ex-11"], r1
    # the steer re-invokes the agent; the continuation ends on the SAME turn
    _write_transcript(tmp, turn + [_assistant(2, "Okay — should I rename first?")],
                      "dedup.jsonl")
    r2 = wd._fire_rules(corpus, req)
    assert r2["steers_by_rule"]["R-ex-11"] == [], "rule re-fired on its own steer continuation"
    # a genuinely new turn resets the key
    _write_transcript(tmp, turn + [_user("continue", 1),
                                   _assistant(0, "Should I batch these commits?")],
                      "dedup.jsonl")
    r3 = wd._fire_rules(corpus, req)
    assert r3["steers_by_rule"]["R-ex-11"], "new turn did not reset the dedup key"
    wd.TURN_FIRED.clear()
    wa.REGISTRY.clear()
    print("PASS  daemon_turn_dedup")


def test_oracle_seam_and_wall(tmp: Path):
    """ask_oracle: cached by prompt hash, fail-silent on a missing command,
    spawns with WARDEN_ORACLE=1; and wall 1 — the hook no-ops for a session
    carrying the oracle marker."""
    home = tmp / "whome"
    os.environ["WARDEN_HOME"] = str(home)
    try:
        # the prompt lands as $0 of the -c script — output is exactly "yes"
        os.environ["WARDEN_ORACLE_CMD"] = '/bin/sh -c "echo yes"'
        assert wa.ask_oracle("is this a question? reply yes or no") == "yes"
        # cached: even with a broken command the cached verdict answers
        os.environ["WARDEN_ORACLE_CMD"] = "/nonexistent-oracle"
        assert wa.ask_oracle("is this a question? reply yes or no") == "yes"
        # uncached + broken command → fail-silent empty
        assert wa.ask_oracle("a different prompt") == ""
    finally:
        os.environ.pop("WARDEN_ORACLE_CMD", None)
        os.environ.pop("WARDEN_HOME", None)
    import warden_hook as wh
    os.environ["WARDEN_ORACLE"] = "1"
    try:
        assert wh.disabled() is True, "oracle session not moment-silent"
    finally:
        os.environ.pop("WARDEN_ORACLE", None)
    assert wh.disabled() is False or (Path.home() / ".warden" / "DISABLED").exists()
    print("PASS  oracle_seam_and_wall")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_states(tmp)
        test_state_seconds_and_skill(tmp)
        test_ledger_and_registry(tmp)
        test_fixture_rule_fires_only_when_asking(tmp)
        test_tail_robustness(tmp)
        test_turn_view(tmp)
        test_content_rules(tmp)
        test_turn_bearing_mark_and_key(tmp)
        test_daemon_turn_dedup(tmp)
        test_oracle_seam_and_wall(tmp)
    print("\nall warden_agent tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
