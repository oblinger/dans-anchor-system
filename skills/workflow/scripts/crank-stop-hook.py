#!/usr/bin/env python3
"""crank-stop-hook.py — F239 crank exit handshake: the Stop-moment gate.

Registered as a Claude Code `Stop` hook. Fires on every turn end; gates ONLY
when a crank-session sentinel (written by `state crank start`) covers the
session's cwd. The turn may end iff the anchor's backlog is in exactly one of
three mechanically-checkable states (ruled by the user 2026-07-14):

  1. Empty frontier — `## Now` + `## Next` hold no live rows.
  2. Something Ready — >=1 [Ready]/[Active]/[Agreed] row AND the final
     assistant message contains `CRANK READY`.
  3. Groomed — a fresh `state triage` stamp (backlog sha unchanged since the
     stamp) AND the stamp's canonical TRIAGE line echoed in the final message.

Otherwise the hook blocks with a re-prompt. Safety valves: sentinels expire
after 24 h; after BLOCK_CAP consecutive blocks the gate disarms and allows
the stop (fail-open — enforcement must never trap a session). An accepted
stop clears the sentinel.

Cost in the common case (no sentinel): one directory check, <5 ms.
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CRANK_DIR = Path.home() / ".config" / "anchor-system" / "crank"
TRIAGE_DIR = Path.home() / ".config" / "anchor-system" / "triage"
TTL_SECONDS = 24 * 3600
BLOCK_CAP = 3

H2_RE = re.compile(r"^##\s+(.+?)\s*$")
ROW_RE = re.compile(r"^-\s+\*\*.+?\*\*\s+\[([^\]]+)\]")
READY_BRACKETS = ("Ready", "Active", "Agreed")
READY_HORIZONS = ("Active", "Ready", "Now", "Next", "Legwork")


def _final_assistant_text(transcript_path):
    """Concatenated text blocks of the LAST assistant message in the
    transcript JSONL. Empty string when unavailable."""
    last = ""
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                msg = entry.get("message") or {}
                parts = [b.get("text", "") for b in (msg.get("content") or [])
                         if isinstance(b, dict) and b.get("type") == "text"]
                if parts:
                    last = "\n".join(parts)
    except (OSError, TypeError):
        return ""
    return last


def _backlog_counts(backlog_path):
    """(now_next_rows, ready_rows) for the backlog, or (None, None) if the
    file is unreadable. Done-bracketed rows never count."""
    try:
        lines = Path(backlog_path).read_text(encoding="utf-8").splitlines()
    except (OSError, TypeError):
        return None, None
    now_next = ready = 0
    h2 = None
    for line in lines:
        m = H2_RE.match(line)
        if m:
            h2 = m.group(1).strip()
            continue
        r = ROW_RE.match(line)
        if not r or h2 is None:
            continue
        bracket = r.group(1).strip()
        if bracket.startswith("Done"):
            continue
        if h2 in ("Now", "Next"):
            now_next += 1
        if bracket in READY_BRACKETS and h2 in READY_HORIZONS:
            ready += 1
    return now_next, ready


def _sentinel_fresh(sentinel):
    try:
        started = datetime.fromisoformat(sentinel.get("started", ""))
        age = (datetime.now(timezone.utc) - started).total_seconds()
        return 0 <= age < TTL_SECONDS
    except (ValueError, TypeError):
        return False


def _allow(sentinel_path):
    sentinel_path.unlink(missing_ok=True)
    return 0


def _block(sentinel_path, sentinel, reason):
    sentinel["blocks"] = int(sentinel.get("blocks", 0)) + 1
    if sentinel["blocks"] > BLOCK_CAP:
        sentinel_path.unlink(missing_ok=True)
        print(f"crank-stop-hook: block cap ({BLOCK_CAP}) reached — "
              "gate disarmed, stop allowed", file=sys.stderr)
        return 0
    try:
        sentinel_path.write_text(json.dumps(sentinel, indent=2))
    except OSError:
        pass
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not CRANK_DIR.is_dir():
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    match = None
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
            match = (sp, s)
            break
    if match is None:
        return 0

    sp, s = match
    backlog = s.get("backlog_path", "")
    now_next, ready = _backlog_counts(backlog)
    if now_next is None or ready is None:
        return _allow(sp)  # backlog unreadable — fail open, disarm

    # State 1 — empty frontier: nothing to groom, stop is legal, no ritual.
    if now_next == 0:
        return _allow(sp)

    final_text = _final_assistant_text(payload.get("transcript_path", ""))

    # State 2 — something Ready, declared: the scannable CRANK READY tail.
    if ready > 0 and "CRANK READY" in final_text:
        return _allow(sp)

    # State 3 — groomed: fresh gated stamp + canonical line echoed.
    stamp_path = TRIAGE_DIR / f"{s.get('slug', '')}.json"
    if stamp_path.is_file():
        try:
            stamp = json.loads(stamp_path.read_text())
        except (ValueError, OSError):
            stamp = {}
        try:
            cur_sha = hashlib.sha256(Path(backlog).read_bytes()).hexdigest()
        except OSError:
            cur_sha = None
        if (stamp.get("backlog_sha256") == cur_sha
                and stamp.get("line") and stamp["line"] in final_text):
            return _allow(sp)

    reason = (
        f"crank stop gate (F239): no legal stop state — {s.get('slug', '?')} "
        f"backlog has {now_next} row(s) in Now/Next and Ready={ready}. Legal "
        "exits: (1) Now+Next empty; (2) Ready > 0 and the final message "
        "contains CRANK READY; (3) a fresh `state triage` stamp with its "
        "canonical TRIAGE line echoed in the final message. Run the grooming "
        "cascade (/groom then /ask) until something is Ready or every "
        "question is parked, run `state triage`, and end with its printed "
        "line — or declare CRANK READY if Ready work remains. "
        "(`state crank stop` disarms this gate.)"
    )
    return _block(sp, s, reason)


if __name__ == "__main__":
    sys.exit(main())
