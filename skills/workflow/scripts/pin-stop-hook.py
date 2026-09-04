#!/usr/bin/env python3
# warden-hook: Stop
"""pin-stop-hook — a turn that wrote vault files and pinned nothing is told so,
once, with the exact `pin` invocation (TINK T669; Dan's go 2026-09-04).

Why it exists. `pin` (F660) was documented in one place, ~12,300 tokens into a
skill body that loads only on invoke, and was not on PATH — the weakest rung on
the Agent Recall ladder for a tool wanted in every agent's inner loop. This hook
moves the knowledge to the moment it is needed: an agent that has never heard
of pin reads the full command in the reason text and complies on first
encounter, with nothing to remember.

Why Stop and not write. Writes happen dozens of times a turn; a write-time rule
fires ~30x and is tuned out by turn three (how the osascript rules died).
Turn-ends happen once.

Self-silencing. A turn that wrote nothing hears nothing; a turn that pinned
hears nothing; and the nudge blocks the stop AT MOST ONCE per turn —
`stop_hook_active` is the harness's own "you already continued from a stop
hook" flag, so the second stop passes even if the agent decided nothing here
was for Dan. Every examined turn is logged to `stopgate/pin-nudge.jsonl`
(verdicts `pinned` / `nudged` / `passed-after-nudge`), which is the point:
the miss rate becomes a number instead of a feeling.

What counts as a write: a Write / Edit / NotebookEdit tool_use whose
`file_path` is under `vault_root` (global.yaml, default ~/ob/kmr). Bash
heredocs that write vault files are NOT seen — a known blind spot, kept rather
than guessed at, because a false nudge is what trains agents to ignore this.
What counts as a pin: any Bash tool_use whose command invokes `pin` as a
command token (`…/scripts/pin SLUG …`).

Mode: `stopgate/pin-nudge.conf` `{"mode": "nudge"|"log"}`; absent → nudge.
Fail-open everywhere: any error → {} (the stop proceeds, nothing logged).
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(os.path.expanduser("~/.config/anchor-system"))
GATE_DIR = STATE_DIR / "stopgate"
LOG = GATE_DIR / "pin-nudge.jsonl"
CONF = GATE_DIR / "pin-nudge.conf"
PIN = Path(__file__).resolve().parent / "pin"
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
_PIN_CALL_RE = re.compile(r"(?<![\w.-])pin[\"']?\s+[^\s-]")   # `…/scripts/pin Tink …`, never `spin`/`pin-…`


def _vault_root():
    try:
        for line in (STATE_DIR / "global.yaml").read_text(encoding="utf-8").splitlines():
            m = re.match(r"^vault_root:\s*(\S+)", line)
            if m:
                return os.path.realpath(os.path.expanduser(m.group(1).strip("'\"")))
    except OSError:
        pass
    return os.path.realpath(os.path.expanduser("~/ob/kmr"))


def _mode():
    try:
        return json.loads(CONF.read_text(encoding="utf-8")).get("mode", "nudge")
    except (OSError, ValueError, TypeError):
        return "nudge"


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


def _turn_tool_uses(transcript_path):
    """tool_use blocks since the last genuine user prompt (a user entry made
    only of tool_result blocks is the harness, not the user)."""
    entries = list(_iter_entries(transcript_path))
    last_user = -1
    for i, e in enumerate(entries):
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str):
            last_user = i
            continue
        blocks = content or []
        if not (blocks and all(isinstance(b, dict) and b.get("type") == "tool_result"
                               for b in blocks)):
            last_user = i
    out = []
    for e in entries[last_user + 1:]:
        if e.get("type") != "assistant":
            continue
        for b in ((e.get("message") or {}).get("content") or []):
            if isinstance(b, dict) and b.get("type") == "tool_use":
                out.append(b)
    return out


def turn_writes_and_pins(transcript_path, vault_root):
    """(vault files written this turn, in order, deduped; whether pin ran)."""
    written, pinned = [], False
    for b in _turn_tool_uses(transcript_path):
        name, inp = b.get("name"), b.get("input") or {}
        if name in WRITE_TOOLS:
            fp = inp.get("file_path") or inp.get("notebook_path") or ""
            if not fp:
                continue
            rp = os.path.realpath(os.path.expanduser(fp))
            if (rp == vault_root or rp.startswith(vault_root + "/")) and rp not in written:
                written.append(rp)
        elif name == "Bash" and _PIN_CALL_RE.search(inp.get("command") or ""):
            pinned = True
    return written, pinned


def _anchor_slug(cwd):
    d = Path(cwd or os.getcwd())
    for p in [d, *d.parents]:
        a = p / ".anchor"
        if a.is_file():
            try:
                m = re.search(r"^slug:\s*(\S+)", a.read_text(encoding="utf-8"), re.M)
            except OSError:
                m = None
            return (m.group(1) if m else p.name), str(p)
    return None, None


def _log(rec):
    try:
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **rec}
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except OSError:
        pass


def _reason(slug, written):
    shown = [Path(w).stem for w in written[:3]]
    links = " ".join(f'"[[{s}]]"' for s in shown)
    more = f" (+{len(written) - 3} more)" if len(written) > 3 else ""
    return (
        f"pin (T669): this turn wrote {len(written)} vault file(s){more} and pinned nothing — "
        f"Dan sees only what is pinned into your spine. Show the work with ONE call, then stop again:\n"
        f"  \"{PIN}\" {slug} {links}\n"
        f"Pass the file(s) he should open (the ones just written, or the one that matters); a bare "
        f"`pin {slug}` clears the row. pin refuses if the anchor page has no dispatch table or a link "
        f"does not resolve — then there is nothing to pin here: stop again and this stays silent."
    )


def hook(event):
    tp = event.get("transcript_path", "")
    if not tp:
        return {}
    vault = _vault_root()
    written, pinned = turn_writes_and_pins(tp, vault)
    if not written:
        return {}
    slug, anchor_path = _anchor_slug(event.get("cwd") or "")
    base = {"anchor": slug, "writes": len(written), "session": event.get("session_id")}
    if pinned:
        _log({**base, "verdict": "pinned"})
        return {}
    if event.get("stop_hook_active"):
        _log({**base, "verdict": "passed-after-nudge"})
        return {}
    mode = _mode()
    _log({**base, "verdict": "nudged", "mode": mode})
    if mode != "nudge" or not slug:
        return {}
    return {"decision": "block", "reason": _reason(slug, written)}


def warden_hook(event: dict) -> dict:
    """F299 fan-in entrypoint (`warden compile` reads the header declaration)."""
    try:
        return hook(event or {})
    except Exception:
        return {}


if __name__ == "__main__":
    import sys
    try:
        out = warden_hook(json.loads(sys.stdin.read() or "{}"))
    except Exception:
        out = {}
    if out:
        print(json.dumps(out))
