#!/usr/bin/env python3
"""Warden agent-state model (F216) — sensing what the agent is doing.

Implements the `agent` object in the interpretation environment: `agent.state`
(`working` / `asking` / `landed` / `paused` / `idle` / `unknown`), `agent.skill`,
`agent.is_asking`, `agent.state_seconds`, `agent.open_tasks`. The classifier is
**fully mechanical — no LLM at any rung** (F216 § The classifier): events and
cheap text checks only.

Signals, per the F216 fallback ladder:

- **R1 — in-band**: at live rule-fire time the triggering moment itself is the
  boundary signal (a `prompt:stop` IS a turn end; a tool moment IS mid-turn),
  plus the daemon's per-session moment ledger for recent history.
- **R3 — transcript-mapped**: the session's transcript JSONL tail — the last
  assistant/user records give the turn boundary, the pending-question predicate
  (T1 dialog signal / T2 text heuristic), the open-task count, and the skill
  sniff. The ledger is *rebuilt* from this on daemon restart, so a restart
  costs recency of the ring, not correctness (F216 § Signal inventory).
- **R4 — residual**: no per-session mapping → the honest floor: `state` is
  `unknown`, `skill` is `None`. Turn-grade states need a per-session signal.

(The R2 tmux-pane rung — permission-dialog visibility — is a later addition;
the ladder degrades past it by design.)

Environment contract (F216 § The environment contract): reads **never raise**
— `unknown` / `None` / `False` are the error channel; one lazy classification
per pass, cached on the `AgentView` and shared by every rule in the pass.
"""
from __future__ import annotations

import json
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

# Engine-config constants (F216 § Debounce) — not per-rule surface.
T_IDLE = 600.0    # landed → idle after this quiet window
T_DEAD = 1800.0   # working + quiet past this = crash ambiguity → unknown

_TAIL_BYTES = 512 * 1024   # transcript tail window
_LEDGER_CAP = 256          # per-session moment ring
_REGISTRY_CAP = 64         # bounded session registry

_ERROR_VALUES = {"state": "unknown", "skill": None, "is_asking": False,
                 "state_seconds": None, "open_tasks": None}


# ── session registry + moment ledger (lives in the daemon process) ───────────

class SessionRecord:
    """One session's registry entry: identity mapping + bounded moment ring."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.transcript_path: str | None = None
        self.cwd: str | None = None
        self.pane_id: str | None = None
        self.ledger: deque[tuple[str, float]] = deque(maxlen=_LEDGER_CAP)


REGISTRY: dict[str, SessionRecord] = {}
# T013: the daemon serves connections on threads — the evict-then-insert
# below must not interleave across handler threads.
_REGISTRY_LOCK = threading.Lock()


def observe(session: dict | None, moment: str | None, ts: float | None = None) -> SessionRecord | None:
    """Record a moment for a session (registry + ledger). Every field is
    optional — a payload with no session_id is simply not registered."""
    if not session:
        return None
    sid = session.get("session_id") or ""
    if not sid:
        return None
    with _REGISTRY_LOCK:
        rec = REGISTRY.get(sid)
        if rec is None:
            while len(REGISTRY) >= _REGISTRY_CAP:
                REGISTRY.pop(next(iter(REGISTRY)))
            rec = REGISTRY[sid] = SessionRecord(sid)
    for key in ("transcript_path", "cwd", "pane_id"):
        val = session.get(key)
        if val:
            setattr(rec, key, val)
    if moment:
        rec.ledger.append((moment, ts if ts is not None else time.time()))
    return rec


# ── transcript tail reading ──────────────────────────────────────────────────

def transcript_tail(path: str | Path, max_bytes: int = _TAIL_BYTES) -> list[dict]:
    """Parse the last `max_bytes` of a transcript JSONL into records
    (chronological). Unreadable file / bad lines → skipped (fail-safe)."""
    records: list[dict] = []
    try:
        p = Path(path)
        size = p.stat().st_size
        with p.open("rb") as fh:
            if size > max_bytes:
                fh.seek(size - max_bytes)
                fh.readline()  # drop the partial first line
            for raw in fh:
                try:
                    rec = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(rec, dict) and rec.get("type") in ("user", "assistant"):
                    records.append(rec)
    except OSError:
        pass
    return records


def _rec_ts(rec: dict) -> float | None:
    ts = rec.get("timestamp")
    if not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _content_blocks(rec: dict) -> list:
    msg = rec.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def _is_real_user_prompt(rec: dict) -> bool:
    """A user record that is an actual prompt (not a tool_result envelope)."""
    if rec.get("type") != "user":
        return False
    blocks = _content_blocks(rec)
    return any(b.get("type") == "text" for b in blocks if isinstance(b, dict))


def _last_text(rec: dict) -> str:
    parts = [b.get("text", "") for b in _content_blocks(rec)
             if isinstance(b, dict) and b.get("type") == "text"]
    return "\n\n".join(p for p in parts if p)


def _tool_uses(rec: dict) -> list[dict]:
    return [b for b in _content_blocks(rec)
            if isinstance(b, dict) and b.get("type") == "tool_use"]


# ── the pending-question predicate Q (F216 § The classifier) ─────────────────

_OPTIONS_RE = re.compile(r"(?m)^\s*(?:[-*]\s*)?\*{0,2}\(?[A-D]\)|\bQ\d+\s*:")


def question_pending(records: list[dict]) -> bool:
    """Did the turn end addressing a question to the user? T1 (dialog moment
    with no answer after it) checked first, then T2 (text heuristic)."""
    if not records:
        return False
    last = records[-1]
    if last.get("type") != "assistant":
        return False
    # T1 — the harness multi-choice dialog is literally up: the final record
    # carries an AskUserQuestion tool_use with nothing answering it after.
    if any(t.get("name") == "AskUserQuestion" for t in _tool_uses(last)):
        return True
    # T2 — chat-question heuristic on the final agent text: last non-code
    # paragraph ends in `?`, or carries an options pattern ((A)/(B), Q<n>:).
    # Mechanical by design — occasional rhetorical-question misses accepted.
    text = _last_text(last)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paragraphs = [p for p in paragraphs if not p.startswith("```")]
    if not paragraphs:
        return False
    final = paragraphs[-1]
    return final.rstrip().endswith("?") or bool(_OPTIONS_RE.search(final))


# ── the open-work test W — harness task list from transcript records ─────────

_TASK_DONE = ("completed", "cancelled", "done")


def open_tasks(records: list[dict]) -> int:
    """Open harness-task count: TaskCreate tool_uses open, TaskUpdate with a
    terminal status closes (distinct taskIds). Mechanical, floor 0."""
    created = 0
    closed_ids: set = set()
    for rec in records:
        if rec.get("type") != "assistant":
            continue
        for tu in _tool_uses(rec):
            name = tu.get("name")
            inp = tu.get("input") or {}
            if name == "TaskCreate":
                created += len(inp.get("tasks", [])) if isinstance(inp.get("tasks"), list) else 1
            elif name == "TaskUpdate":
                if str(inp.get("status", "")).lower() in _TASK_DONE:
                    closed_ids.add(inp.get("taskId") or inp.get("task_id") or len(closed_ids))
    return max(0, created - len(closed_ids))


# ── agent.skill — ranked derivation ──────────────────────────────────────────

_CMD_TAG_RE = re.compile(r"<command-name>/?([\w:-]+)</command-name>")


def current_skill(records: list[dict], ledger=None) -> str | None:
    """Rank 1: last `skill:pre:<name>` ledger moment since the last
    prompt:submit. Rank 2: transcript sniff — the current turn's Skill
    tool_use or the invoking prompt's <command-name> tag. Else None."""
    if ledger:
        skill = None
        for moment, _ in ledger:
            if moment == "prompt:submit":
                skill = None
            elif moment.startswith("skill:pre:"):
                skill = moment.split(":", 2)[2] or None
            elif moment == "prompt:stop":
                skill = None
        if skill:
            return skill
    # transcript sniff: records of the current turn = after the last real prompt
    turn_start = 0
    for i, rec in enumerate(records):
        if _is_real_user_prompt(rec):
            turn_start = i
    skill = None
    for rec in records[turn_start:]:
        if rec.get("type") == "assistant":
            for tu in _tool_uses(rec):
                if tu.get("name") == "Skill":
                    inp = tu.get("input") or {}
                    skill = (inp.get("skill") or inp.get("command") or "").strip() or skill
        elif _is_real_user_prompt(rec):
            m = _CMD_TAG_RE.search(_last_text(rec))
            if m:
                skill = m.group(1)
    return skill or None


# ── the classifier — signals → state (F216 evaluation order) ─────────────────

def classify(session: dict | None, trigger_moment: str | None = None,
             now: float | None = None, records: list[dict] | None = None) -> dict:
    """One mechanical classification: the F216 ladder (liveness → in flight →
    turn end → decay). Returns the full value dict; never raises upward —
    callers wrap, and R4 (no per-session mapping) returns the error values.
    `records` lets the caller share its transcript-tail read (one per pass)."""
    now = now if now is not None else time.time()
    if not session:
        return dict(_ERROR_VALUES)
    sid = session.get("session_id") or ""
    rec = REGISTRY.get(sid) if sid else None
    ledger = list(rec.ledger) if rec else []
    tp = session.get("transcript_path") or (rec.transcript_path if rec else None)
    if records is None:
        records = transcript_tail(tp) if tp else []
    if not records and not ledger and not trigger_moment:
        return dict(_ERROR_VALUES)   # R4 — the honest floor

    # last-activity timestamp: newest of ledger / records / transcript mtime
    last_ts = 0.0
    if ledger:
        last_ts = max(last_ts, ledger[-1][1])
    for r in reversed(records):
        t = _rec_ts(r)
        if t:
            last_ts = max(last_ts, t)
            break
    if tp:
        try:
            last_ts = max(last_ts, Path(tp).stat().st_mtime)
        except OSError:
            pass
    quiet = max(0.0, now - last_ts) if last_ts else None

    n_open = open_tasks(records)
    skill = current_skill(records, ledger)
    values = {"skill": skill, "open_tasks": n_open,
              "state_seconds": round(quiet, 3) if quiet is not None else None}

    def done(state: str) -> dict:
        values["state"] = state
        values["is_asking"] = state == "asking"
        return values

    def turn_end() -> dict:
        if question_pending(records):
            return done("asking")     # sticky — no timer (F216 § transitions)
        state = "paused" if n_open > 0 else "landed"
        if state == "landed" and quiet is not None and quiet >= T_IDLE:
            return done("idle")       # the one decay edge
        return done(state)

    def working() -> dict:
        # crash ambiguity: alive but silent past T_DEAD → unknown, not a guess
        if quiet is not None and quiet >= T_DEAD:
            return done("unknown")
        return done("working")

    # 1. liveness — a session whose newest signal is a stop, read out-of-band
    # with no transcript to consult, is over → idle. (Claude Code's Stop fires
    # per *turn*, so when a transcript exists the turn-end branch reads the
    # real ending instead.)
    if not records and ledger and trigger_moment is None \
            and ledger[-1][0] in ("session:stop", "prompt:stop"):
        return done("idle")

    # 2/3. R1 — the triggering moment IS the boundary
    if trigger_moment:
        if trigger_moment in ("prompt:stop", "session:stop"):
            return turn_end()
        if trigger_moment == "prompt:submit" or trigger_moment.split(":", 1)[0] in (
                "tool", "skill", "write", "read", "git"):
            return working()
        # session:start / session:compact / unknown moments → fall through

    # R3 — classify from the transcript tail
    if records:
        last = records[-1]
        if last.get("type") == "user":
            return working()          # prompt or tool_result in — agent has control
        uses = _tool_uses(last)
        if uses and not any(t.get("name") == "AskUserQuestion" for t in uses):
            return working()          # ended on a tool_use — a tool is running
        return turn_end()
    return dict(_ERROR_VALUES)


# ── agent.turn — the conversation-content view (F217) ───────────────────────

TURN_CAP = 16 * 1024   # per text member; head+tail-preserving truncation


def _cap(text: str) -> str:
    if len(text) <= TURN_CAP:
        return text
    half = (TURN_CAP - 20) // 2
    return text[:half] + "\n…[elided]…\n" + text[-half:]


def turn_slice(records: list[dict]) -> list[dict]:
    """The current turn's records: from the last real user prompt onward
    (a Stop-steer continuation extends the same turn — no new prompt)."""
    start = 0
    for i, rec in enumerate(records):
        if _is_real_user_prompt(rec):
            start = i
    return records[start:]


def turn_key(records: list[dict]) -> str | None:
    """The turn's identity: the opening user-prompt record's uuid (falling
    back to its timestamp). None when no turn is identifiable."""
    sl = turn_slice(records)
    if not sl or not _is_real_user_prompt(sl[0]):
        return None
    return sl[0].get("uuid") or sl[0].get("timestamp") or None


_TOOL_KEY_INPUT = ("command", "file_path", "skill", "prompt", "pattern")


def _tool_key_input(inp: dict) -> str:
    for k in _TOOL_KEY_INPUT:
        v = inp.get(k)
        if isinstance(v, str) and v:
            return v
    return ""


class TurnView:
    """`agent.turn` — the six content members (F217 § The `agent.turn` view).
    `agent`'s members are interpreted state; these are raw content. Lazy —
    built on the first member read, cached for the pass. Reads never raise;
    at R4 (unbound) every member is its error value ('' / [])."""

    def __init__(self, records: list[dict] | None):
        self._records = records
        self._built: dict | None = None

    def _b(self) -> dict:
        if self._built is None:
            try:
                self._built = self._build()
            except Exception:  # noqa: BLE001 — reads never raise (contract)
                self._built = {"user_said": "", "agent_said": "", "text": "",
                               "messages": [], "tools": [], "commands": []}
        return self._built

    def _build(self) -> dict:
        sl = turn_slice(self._records or [])
        user_said = ""
        agent_parts: list[str] = []
        flat: list[str] = []
        tools: list[tuple[str, str]] = []
        for rec in sl:
            if _is_real_user_prompt(rec):
                user_said = _last_text(rec)
                flat.append(f"USER: {user_said}")
            elif rec.get("type") == "assistant":
                t = _last_text(rec)
                if t:
                    agent_parts.append(t)
                    flat.append(f"AGENT: {t}")
                for tu in _tool_uses(rec):
                    key = _tool_key_input(tu.get("input") or {})
                    tools.append((tu.get("name") or "", key))
                    flat.append(f"TOOL {tu.get('name')}: {key[:120]}")
        return {
            "user_said": _cap(user_said),
            "agent_said": _cap("\n\n".join(agent_parts)),
            "text": _cap("\n".join(flat)),
            "messages": sl,
            "tools": tools,
            "commands": [k for n, k in tools if n == "Bash" and k],
        }

    @property
    def user_said(self) -> str:
        return self._b()["user_said"]

    @property
    def agent_said(self) -> str:
        return self._b()["agent_said"]

    @property
    def text(self) -> str:
        return self._b()["text"]

    @property
    def messages(self) -> list:
        return self._b()["messages"]

    @property
    def tools(self) -> list:
        return self._b()["tools"]

    @property
    def commands(self) -> list:
        return self._b()["commands"]


# ── ask_oracle — the judgment verb (F217 § Judgment gating) ──────────────────

def ask_oracle(prompt: str, timeout: float = 60.0) -> str:
    """One blocking oracle judgment → its reply text. Audit-path machinery:
    fail-silent ('' on any failure — a rule gating on a `yes` sentinel then
    stays quiet), cached by prompt hash in `$WARDEN_HOME/oracle-cache.json`,
    and the spawned session carries `WARDEN_ORACLE=1` so its own moments are
    invisible to Warden (loop-prevention wall 1). The command is `claude -p`
    (override: `WARDEN_ORACLE_CMD`, the test seam)."""
    import hashlib
    import os as _os
    import shlex
    import subprocess
    try:
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        home = Path(_os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))
        cache_p = home / "oracle-cache.json"
        cache: dict = {}
        if cache_p.is_file():
            try:
                cache = json.loads(cache_p.read_text(encoding="utf-8"))
            except ValueError:
                cache = {}
        if key in cache:
            return cache[key]
        cmd = shlex.split(_os.environ.get("WARDEN_ORACLE_CMD") or "claude -p")
        out = subprocess.run(cmd + [prompt], capture_output=True, text=True,
                             timeout=timeout,
                             env={**_os.environ, "WARDEN_ORACLE": "1"})
        reply = out.stdout.strip() if out.returncode == 0 else ""
        if reply:
            home.mkdir(parents=True, exist_ok=True)
            cache[key] = reply
            cache_p.write_text(json.dumps(cache), encoding="utf-8")
        return reply
    except Exception:  # noqa: BLE001 — fail-silent (conservative: rule stays quiet)
        return ""


# ── AgentView — the lazy `agent` object rules read ───────────────────────────

class AgentView:
    """The `agent` in the interpretation environment. Lazy: classification
    runs on the first property read and is cached for the pass (F216
    § Laziness + cost). Reads never raise — error values are the channel."""

    def __init__(self, session: dict | None = None, trigger_moment: str | None = None,
                 now: float | None = None):
        self._session = session
        self._trigger = trigger_moment
        self._now = now
        self._values: dict | None = None
        self._tail: list[dict] | None = None
        self._turn: TurnView | None = None

    @property
    def is_bound(self) -> bool:
        """True when a per-session mapping exists (rungs R1–R3); False is R4 —
        turn-bearing rules are skipped wholesale for an unbound agent."""
        return bool(self._session)

    def _records(self) -> list[dict]:
        """The one transcript-tail read of the pass, shared by the classifier
        and the turn view."""
        if self._tail is None:
            tp = (self._session or {}).get("transcript_path")
            try:
                self._tail = transcript_tail(tp) if tp else []
            except Exception:  # noqa: BLE001
                self._tail = []
        return self._tail

    def _classified(self) -> dict:
        if self._values is None:
            try:
                self._values = classify(self._session, self._trigger, self._now,
                                        records=self._records() if self._session else None)
            except Exception:  # noqa: BLE001 — reads never raise (contract)
                self._values = dict(_ERROR_VALUES)
        return self._values

    @property
    def turn(self) -> TurnView:
        """`agent.turn` — the conversation-content view (F217), lazy + cached."""
        if self._turn is None:
            self._turn = TurnView(self._records() if self.is_bound else None)
        return self._turn

    @property
    def response(self) -> str:
        """The everyday alias of `agent.turn.agent_said` (F217)."""
        return self.turn.agent_said

    @property
    def state(self) -> str:
        return self._classified().get("state", "unknown")

    @property
    def skill(self) -> str | None:
        return self._classified().get("skill")

    @property
    def is_asking(self) -> bool:
        return bool(self._classified().get("is_asking", False))

    @property
    def state_seconds(self) -> float | None:
        return self._classified().get("state_seconds")

    @property
    def open_tasks(self) -> int | None:
        return self._classified().get("open_tasks")


def unbound() -> AgentView:
    """The headless/audit-path agent: every read returns the error values."""
    return AgentView(None)


def session_of(payload: dict | None) -> dict | None:
    """Extract the session mapping from a hook event payload (or a daemon
    request's `session` field — same shape)."""
    if not payload or not isinstance(payload, dict):
        return None
    sid = payload.get("session_id") or ""
    tp = payload.get("transcript_path") or ""
    if not sid and not tp:
        return None
    return {"session_id": sid, "transcript_path": tp,
            "cwd": payload.get("cwd") or "", "pane_id": payload.get("pane_id") or ""}


def make_agent(payload: dict | None, trigger_moment: str | None = None,
               now: float | None = None) -> AgentView:
    """Bind an AgentView from a hook payload; unmappable payload → unbound."""
    return AgentView(session_of(payload), trigger_moment, now)
