#!/usr/bin/env python3
# warden-hook: Stop
"""crank-stop-hook.py — the Stop-moment groom gate (F239 → generalized by F244).

Registered as a Claude Code `Stop` hook; fires on every turn end. The gate
enforces the F244 *never-strand-the-user* invariant:

  > On a WORK-ARMED stop, the anchor's grooming worklist must be EMPTY.

"Work-armed" = the ending turn used at least one tool (an edit / write / bash /
state mutation) — a pure Q&A or design turn is never gated. "Worklist empty"
= `state groom-list <anchor> --count` returns 0 (the same `_triage_gate_findings` the
groom cascade and F242/C49 use — one source of truth). Recording a question in
state grooms that item off the worklist, so a chat-only question can't clear
the gate (the anti-rolloff guarantee). There is NO context-<40% escape and NO
"CRANK READY" ceremony (both dropped 2026-07-15 — worklist-empty is the whole
gate; it subsumes F239's crank-exit handshake).

Arming sources (either): the ending turn used tools, OR a fresh `state crank
start` sentinel covers the cwd (back-compat). Anchor is resolved from the cwd
(nearest `.anchor`) or the crank sentinel.

Fail-open everywhere — enforcement must never trap a session: unresolvable
anchor, unreadable state, or a `state` error all ALLOW the stop; after
BLOCK_CAP consecutive blocks the gate disarms and allows (bounded worst case:
BLOCK_CAP re-prompts) — each disarm is recorded to `stopgate/disarms.jsonl`
(the firing is otherwise stderr-only and invisible: observability + BLOCK_CAP
tuning data). Cost in the common case (pure-chat turn, or empty
worklist): one transcript scan + at most one `state` call, well under a second.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CRANK_DIR = Path.home() / ".config" / "anchor-system" / "crank"
GATE_DIR = Path.home() / ".config" / "anchor-system" / "stopgate"
STATE_CLI = Path.home() / ".claude" / "skills" / "workflow" / "scripts" / "state"
TTL_SECONDS = 24 * 3600
BLOCK_CAP = 3
DISARM_LOG = GATE_DIR / "disarms.jsonl"
# F267 — LLM stop-check (stage 2): catch a chat-only question the worklist gate
# (stage 1) is structurally blind to. INERT for now — logs a verdict, blocks
# nothing. Runs only on a work-armed, clean-worklist stop (the sole gap).
LLM_CHECK_LOG = GATE_DIR / "llm-check.jsonl"
LLM_CONF = GATE_DIR / "llm-check.conf"   # {mode, budget, fired} — absent → inert
LLM_MODEL = "haiku"
LLM_TIMEOUT = 30
LLM_RECURSION_ENV = "STOPGATE_LLM_CHECK"


def _iter_entries(transcript_path):
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except (OSError, TypeError):
        return


def _turn_used_tools(transcript_path):
    """True iff, since the last genuine user prompt, any assistant message used
    a tool. A user message carrying only tool_result blocks is NOT a genuine
    prompt (it's the harness returning tool output) — so a multi-step tool turn
    still counts as one work-armed turn."""
    entries = list(_iter_entries(transcript_path))
    last_user = -1
    for i, e in enumerate(entries):
        if e.get("type") != "user":
            continue
        msg = e.get("message") or {}
        content = msg.get("content")
        if isinstance(content, str):
            last_user = i
            continue
        blocks = content or []
        only_tool_results = bool(blocks) and all(
            isinstance(b, dict) and b.get("type") == "tool_result" for b in blocks)
        if not only_tool_results:
            last_user = i
    for e in entries[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        msg = e.get("message") or {}
        for b in (msg.get("content") or []):
            if isinstance(b, dict) and b.get("type") == "tool_use":
                return True
    return False


def _sentinel_fresh(sentinel):
    try:
        started = datetime.fromisoformat(sentinel.get("started", ""))
        return 0 <= (datetime.now(timezone.utc) - started).total_seconds() < TTL_SECONDS
    except (ValueError, TypeError):
        return False


def _crank_sentinel_for(cwd):
    """(path, sentinel) of a fresh crank sentinel covering cwd, or None."""
    if not CRANK_DIR.is_dir():
        return None
    for sp in sorted(CRANK_DIR.glob("*.json")):
        try:
            s = json.loads(sp.read_text())
        except (ValueError, OSError):
            sp.unlink(missing_ok=True)
            continue
        if not _sentinel_fresh(s):
            sp.unlink(missing_ok=True)
            continue
        anchor = (s.get("anchor_path") or "").rstrip("/")
        if anchor and (cwd == anchor or cwd.startswith(anchor + "/")):
            return sp, s
    return None


def _anchor_from_cwd(cwd):
    """(slug, anchor_path) of the nearest `.anchor` at/above cwd, or None."""
    try:
        d = Path(cwd).resolve()
    except (OSError, ValueError):
        return None
    for cand in [d, *d.parents]:
        marker = cand / ".anchor"
        if not marker.is_file():
            continue
        slug = None
        try:
            for ln in marker.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("slug:"):
                    slug = ln.split(":", 1)[1].strip()
                    break
        except (OSError, UnicodeDecodeError):
            return None
        return (slug, str(cand)) if slug else None
    return None


def _worklist_count(anchor_path):
    """The grooming-worklist size via `state groom-list <anchor> --count`, or None on
    any failure (→ fail open)."""
    try:
        r = subprocess.run(
            [sys.executable, str(STATE_CLI), "groom-list", anchor_path,
             "--count"],
            capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    try:
        return int((r.stdout or "").strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None


def _allow(crank_sp, gate_path):
    if crank_sp is not None:
        crank_sp.unlink(missing_ok=True)
    gate_path.unlink(missing_ok=True)
    return None


def _record_disarm(anchor, blocks, count):
    """Append a durable record when the gate gives up (BLOCK_CAP exceeded).
    A disarm is otherwise invisible — stderr only — so a gate being routinely
    escaped would leave no trace; this makes the safety-valve firing observable
    (detection) and gives the data to tune BLOCK_CAP. Fail-safe: logging must
    never break the hook (a disarm that fails to log still allows the stop)."""
    try:
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "anchor": anchor,
               "blocks": blocks, "cap": BLOCK_CAP, "worklist_count": count}
        with open(DISARM_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception:  # noqa: BLE001 — logging is never allowed to break the gate
        pass


def _block(gate_path, reason, anchor=None, count=None):
    try:
        blocks = json.loads(gate_path.read_text()).get("blocks", 0)
    except (ValueError, OSError):
        blocks = 0
    blocks += 1
    if blocks > BLOCK_CAP:
        gate_path.unlink(missing_ok=True)
        _record_disarm(anchor or gate_path.stem, blocks, count)
        print(f"stop-gate: block cap ({BLOCK_CAP}) reached — disarmed, stop "
              "allowed", file=sys.stderr)
        return None
    try:
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        gate_path.write_text(json.dumps({"blocks": blocks}))
    except OSError:
        pass
    return {"decision": "block", "reason": reason}


def _llm_config():
    """`{mode: 'inert'|'enforce', budget: int, fired: int}`. Absent/unreadable →
    inert (fail-safe). `budget` is the GLOBAL cap on how many times stage-2 may
    BLOCK before it auto-reverts to allowing — the confidence dial (debut = 1).
    Turn it up as trust in the rule grows; drop to inert to disarm."""
    try:
        c = json.loads(LLM_CONF.read_text(encoding="utf-8"))
        return {"mode": c.get("mode", "inert"),
                "budget": int(c.get("budget", 0)),
                "fired": int(c.get("fired", 0))}
    except (OSError, ValueError, TypeError):
        return {"mode": "inert", "budget": 0, "fired": 0}


def _llm_spend_fire(cfg):
    """Persist one spent fire against the global budget. Fail-safe (a write
    error just means the budget isn't decremented — bounded the other way by the
    per-stop nature of the check)."""
    try:
        cfg = dict(cfg)
        cfg["fired"] = int(cfg.get("fired", 0)) + 1
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        LLM_CONF.write_text(json.dumps(cfg), encoding="utf-8")
    except OSError:
        pass


_OPEN_Q_ROW_RE = re.compile(
    r"^\s*-\s+\*\*([A-Za-z][\w.-]*)\s+—\s+(.+?)\*\*\s+\[([^\]]+)\]")


def _queue_open_questions(anchor_path):
    """F275 M1 — the anchor's open questions as a structured
    `[(handle, header)]` list: every backlog row bracketed `[Questions]` /
    `[N Questions]` / `[User]`, by its id + title. This is the pending-Q set the
    cover-check matches the agent's ask against (upgrade from the coarse
    exists-check). Includes F275 standalone `Q<n>` rows and feature/task rows
    alike (the row's own handle + title). Bounded to 3 dir levels for latency;
    each file read is guarded so one unreadable backlog never sinks the list."""
    out = []
    try:
        base = Path(anchor_path)
        for pat in ("* Backlog.md", "*/* Backlog.md", "*/*/* Backlog.md"):
            for bl in base.glob(pat):
                try:
                    lines = bl.read_text(encoding="utf-8").splitlines()
                except OSError:
                    continue
                for line in lines:
                    m = _OPEN_Q_ROW_RE.match(line)
                    if not m:
                        continue
                    bracket = m.group(3).strip()
                    if bracket == "User" or bracket.endswith(("Questions", "Question")):
                        out.append((m.group(1), m.group(2).strip()))
    except (OSError, ValueError):
        return out
    return out


def _last_assistant_text(transcript_path):
    """Concatenated text of the FINAL assistant message — the words the agent is
    about to end its turn on (what the LLM stage-2 check reads)."""
    text = ""
    for e in _iter_entries(transcript_path):
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str):
            text = content
            continue
        parts = [b.get("text") or "" for b in (content or [])
                 if isinstance(b, dict) and b.get("type") == "text"]
        if parts:
            text = "\n".join(parts)
    return text.strip()


def _normalize_cover(raw):
    """T063 — one shape for `covered_by`: a bare handle, or None.

    The classifier answers this field four different ways, and until 2026-07-30
    every one of them was written to the log verbatim: JSON `null` (which
    `str()` turned into the string `"None"`, 341 records), the literal string
    `"none"` (324), a bare handle (`F235`), and the whole row title
    (`F235 — Activity CLI — grain downsampling …`). Nothing parsed the field
    yet, which is exactly why this was cheap to fix — the enforcement path had
    always compared case-insensitively and was never wrong.

    Note for anyone reading the log: records before 2026-07-30 keep the old
    mixed encodings. The change is at the write site only; back-log records are
    left alone rather than rewritten.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.lower() in ("none", "null", "n/a", "-"):
        return None
    # Keep only the handle when the classifier echoes the full row title.
    # Split on a SPACED dash so hyphenated handles (`B-QFix`) survive intact.
    return re.split(r"\s+[—–-]\s+", s, maxsplit=1)[0].strip()[:80] or None


def _llm_ask_check(payload, anchor, anchor_path):
    """Stage-2 (F267 + F275 M1 cover-check): on a work-armed, clean-worklist
    stop, ask an LLM whether the agent's final message is WAITING ON THE USER
    (a question / go / decision) AND — if so — whether an open question already
    recorded in the queue COVERS that ask. ALWAYS logs a verdict to
    llm-check.jsonl (so the cover-check's accuracy can be observed before it is
    armed). Returns a block-reason (str) only in ENFORCE mode when the agent is
    asking AND no open queue question covers it AND the global fire budget is
    not spent (and spends one fire); otherwise None. INERT mode always returns
    None. Recursion-guarded + fully fail-open — never breaks the stop.

    F275 M1 upgrades the predicate from *exists* (any open [Questions] row gave
    a free pass) to *covers* (the specific ask must be captured by a specific
    open Q) — closing the loophole where one unrelated open Q silenced the gate.
    Arming is unchanged: the cover-check ships behind the same conservative
    mode/budget dial, dormant until the user re-arms it (F267 two-dial rollout)."""
    if os.environ.get(LLM_RECURSION_ENV):
        return None
    asking = False
    summary = ""
    covered_by = None
    got_verdict = False
    try:
        msg = _last_assistant_text(payload.get("transcript_path", ""))
        if len(msg) < 15:
            return None
        open_qs = _queue_open_questions(anchor_path)
        if open_qs:
            q_list = "\n".join(f"  {h} — {t[:120]}" for h, t in open_qs[:40])
        else:
            q_list = "  (none)"
        prompt = (
            "You are a strict classifier. An AI agent just wrote its FINAL "
            "message before ending its turn, in a workspace that already has "
            "these OPEN QUESTIONS recorded in its queue (handle — summary):\n"
            + q_list + "\n\n"
            "Decide two things about the agent's FINAL MESSAGE:\n"
            "1. asking — is it WAITING ON THE USER? true if it asks a question, "
            "requests approval / a decision / a go-ahead, presents options for "
            "the user to pick, or says it is holding / deferring / standing by "
            "on an action pending the user. false if it only reports completed "
            "work, states next steps it will take itself, or offers optional "
            "help without blocking on it.\n"
            "2. covered_by — if asking, does one of the OPEN QUESTIONS above "
            "already capture that SAME ask? Return that question's exact handle "
            "if so; otherwise \"none\". If not asking, return \"none\".\n"
            "Respond with ONLY JSON: {\"asking\": true|false, \"summary\": "
            "\"<the specific ask in <=15 words, or ''>\", \"covered_by\": "
            "\"<handle or none>\"}.\n\n"
            "AGENT FINAL MESSAGE:\n" + msg[:6000])
        env = {**os.environ, LLM_RECURSION_ENV: "1"}
        r = subprocess.run(["claude", "-p", prompt, "--model", LLM_MODEL],
                           capture_output=True, text=True, timeout=LLM_TIMEOUT,
                           env=env)
        out = (r.stdout or "").strip()
        if "```" in out or not out.startswith("{"):
            mm = re.search(r"\{.*\}", out, re.S)
            if mm:
                out = mm.group(0)
        verdict = json.loads(out)
        asking = bool(verdict.get("asking"))
        summary = str(verdict.get("summary", ""))[:200]
        covered_by = _normalize_cover(verdict.get("covered_by"))
        got_verdict = True
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "anchor": anchor,
               "asking": asking, "summary": summary, "covered_by": covered_by,
               "open_q_count": len(open_qs), "msg_excerpt": msg[:200]}
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LLM_CHECK_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception:  # noqa: BLE001 — the check must never break the stop
        return None
    # Enforce decision — block only when the agent is asking AND no open queue
    # question covers it. Fail-safe = allow (a `covered_by` naming any handle,
    # or a non-asking verdict, never blocks).
    try:
        if not (got_verdict and asking):
            return None
        if covered_by is not None:
            return None  # an open Q already captures this ask — surfaced, don't block
        cfg = _llm_config()
        if cfg["mode"] != "enforce" or cfg["fired"] >= cfg["budget"]:
            return None
        _llm_spend_fire(cfg)
        q = summary or "a question"
        return ("stop-gate (F267/F275): your final message asks the user "
                "something — \"" + q + "\" — that NO open question in the queue "
                "covers. A chat-only ask strands the user. There are TWO exits; "
                "pick by whether you already have an answer.\n"
                "  (1) You have a lean — DECIDE IT YOURSELF and announce the "
                "choice (F068 assume-and-announce). Ordering, batching, "
                "rollback, cosmetic renames, and anything low-stakes and "
                "reversible are yours; so is any ask whose answer is already in "
                "your own analysis. This is the common case, and the mint below "
                "will REFUSE a Lean/Strong question without `--why-ask` "
                "precisely to send you here.\n"
                "  (2) It is genuinely the user's call — irreversible, "
                "interface-sticky, an architecture lock-in, or a taste only "
                "they hold. Mint it: `state define <anchor> Backlog Q+` with "
                "`- **(A)**`/`- **(B)**` options, a `- **Recommendation:**`, a "
                "`- **Damage:**`, and a `- **On answer:**` line (add "
                "`--why-ask \"<sentence>\"` if you carry a lean; or record it in "
                "the relevant feature doc via `state ... Q+ define`) — then "
                "re-state the ask in ONE dispatch line pointing at the queue.\n"
                "(Bounded fires, then allows — do not loop; if you cannot act, "
                "say why.)")
    except Exception:  # noqa: BLE001 — enforce must never break the stop
        return None


def warden_hook(payload):
    """The gate's decision for one turn: a Claude Code hook-output dict, or
    None to allow the stop.

    This is the F299 fan-in entrypoint — `warden compile` reads the
    `# warden-hook: Stop` declaration in this file's header and calls this
    function from the generated `Stop` entrypoint, so the gate shares one
    interpreter with the other Python hooks on the moment instead of starting
    its own. It returns the decision rather than printing it; `main()` below is
    the same logic reached as a standalone process, and both paths run this
    function, so there is only one gate.
    """
    cwd = (payload.get("cwd") or os.getcwd()).rstrip("/")

    crank = _crank_sentinel_for(cwd)
    crank_sp = crank[0] if crank else None

    # Resolve the anchor: crank sentinel wins (it carries the exact anchor),
    # else walk up from cwd.
    if crank:
        slug = crank[1].get("slug", "")
        anchor_path = (crank[1].get("anchor_path") or "").rstrip("/")
    else:
        found = _anchor_from_cwd(cwd)
        if found is None:
            return None  # not inside an anchor — nothing to gate
        slug, anchor_path = found

    # Arming: an explicit crank session, OR the ending turn used tools.
    armed = crank is not None or _turn_used_tools(payload.get("transcript_path", ""))
    if not armed:
        return None  # pure-chat / no-work turn — never gated

    gate_path = GATE_DIR / f"{slug or Path(anchor_path).name}.json"

    count = _worklist_count(anchor_path)
    if count is None:
        return _allow(crank_sp, gate_path)  # unreadable worklist → fail open
    if count == 0:
        # F267 stage 2: always logs a verdict; returns a block-reason only in
        # enforce mode (asking + unsurfaced + budget left), else None.
        reason = _llm_ask_check(payload, slug or Path(anchor_path).name, anchor_path)
        if reason:
            return {"decision": "block", "reason": reason}
        return _allow(crank_sp, gate_path)  # clean worklist → stage-1 allow

    reason = (
        f"stop-gate (F244): {slug or anchor_path} has {count} item(s) on the "
        "grooming worklist — the frontier is not fully groomed, so stopping "
        "would strand the user (they can neither cleanly crank nor answer). "
        "Run `state groom-list <anchor>` to see them, groom every item to a "
        "known state (Ready+Next / Questions / Blocked / Waiting / Verify) — "
        "record any question via `state ... Q+ define`, never only in chat — "
        "and clear any audit-q findings the worklist lists with `/audit q --fix` "
        "(the worklist counts them too, per F258) — until it is empty, then "
        "stop. (No context escape; emptying the list costs only a little.)"
    )
    return _block(gate_path, reason, slug or Path(anchor_path).name, count)


def main():
    """Standalone-process form — the same gate, reached through stdin/stdout.
    Kept so the hook still runs as its own `settings.json` command and so the
    F239/F244/F267 suites can drive it as a subprocess."""
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    out = warden_hook(payload)
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
