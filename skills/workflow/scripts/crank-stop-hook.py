#!/usr/bin/env python3
"""crank-stop-hook.py — the Stop-moment groom gate (F239 → generalized by F244).

Registered as a Claude Code `Stop` hook; fires on every turn end. The gate
enforces the F244 *never-strand-the-user* invariant:

  > On a WORK-ARMED stop, the anchor's grooming worklist must be EMPTY.

"Work-armed" = the ending turn used at least one tool (an edit / write / bash /
state mutation) — a pure Q&A or design turn is never gated. "Worklist empty"
= `state groom-list --count` returns 0 (the same `_triage_gate_findings` the
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
BLOCK_CAP re-prompts). Cost in the common case (pure-chat turn, or empty
worklist): one transcript scan + at most one `state` call, well under a second.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CRANK_DIR = Path.home() / ".config" / "anchor-system" / "crank"
GATE_DIR = Path.home() / ".config" / "anchor-system" / "stopgate"
STATE_CLI = Path.home() / ".claude" / "skills" / "workflow" / "scripts" / "state"
TTL_SECONDS = 24 * 3600
BLOCK_CAP = 3


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
    """The grooming-worklist size via `state groom-list --count`, or None on
    any failure (→ fail open)."""
    try:
        r = subprocess.run(
            [sys.executable, str(STATE_CLI), "--anchor", anchor_path,
             "groom-list", "--count"],
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
    return 0


def _block(gate_path, reason):
    try:
        blocks = json.loads(gate_path.read_text()).get("blocks", 0)
    except (ValueError, OSError):
        blocks = 0
    blocks += 1
    if blocks > BLOCK_CAP:
        gate_path.unlink(missing_ok=True)
        print(f"stop-gate: block cap ({BLOCK_CAP}) reached — disarmed, stop "
              "allowed", file=sys.stderr)
        return 0
    try:
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        gate_path.write_text(json.dumps({"blocks": blocks}))
    except OSError:
        pass
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
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
            return 0  # not inside an anchor — nothing to gate
        slug, anchor_path = found

    # Arming: an explicit crank session, OR the ending turn used tools.
    armed = crank is not None or _turn_used_tools(payload.get("transcript_path", ""))
    if not armed:
        return 0  # pure-chat / no-work turn — never gated

    gate_path = GATE_DIR / f"{slug or Path(anchor_path).name}.json"

    count = _worklist_count(anchor_path)
    if count is None or count == 0:
        return _allow(crank_sp, gate_path)  # empty (or unreadable → fail open)

    reason = (
        f"stop-gate (F244): {slug or anchor_path} has {count} item(s) on the "
        "grooming worklist — the frontier is not fully groomed, so stopping "
        "would strand the user (they can neither cleanly crank nor answer). "
        "Run `state --anchor . groom-list` to see them, groom every item to a "
        "known state (Ready+Next / Questions / Blocked / Waiting / Verify) — "
        "record any question via `state ... Q+ define`, never only in chat — "
        "until the worklist is empty, then stop. (No context escape; emptying "
        "the list costs only a little.)"
    )
    return _block(gate_path, reason)


if __name__ == "__main__":
    sys.exit(main())
