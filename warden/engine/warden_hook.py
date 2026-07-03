#!/usr/bin/env python3
"""Warden live hook dispatcher (F220) — the seam onto the real Claude Code hook
surface.

Registered in `settings.json` as the command for the piloted hook events, this
is invoked once per event with the event JSON on **stdin**. It:

  1. checks the **kill switch FIRST** — `~/.warden/DISABLED` or `WARDEN_DISABLED`
     env — and no-ops instantly if disabled (no scan, no compile, no fire), so a
     disabled Warden costs ~nothing and can never break a session;
  2. maps the hook event → Warden moment(s) ([[Warden Events]]);
  3. resolves the anchor from `cwd` (walk up to `.anchor`) — its traits gate the
     active-set;
  4. loads the **pre-compiled** IR + module from `~/.warden/` (fast cold start —
     no per-hook recompile; `warden compile` refreshes them) and fires;
  5. emits steers as hook output and **always exits 0**. Any exception is caught
     and swallowed to a no-op (logged to `~/.warden/hook.log`) — a Warden bug
     must never break the user's actual tool call (fail-safe, never fail-closed).

This is the productionisation layer above `warden_fire` — steer-only in the
pilot (no `tool:pre` veto). Blocking (`deny`/`block` via JSON per Integration
Strategy D5) is deferred past the pilot.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def warden_home() -> Path:
    return Path(os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))


# ── kill switch (checked before any work) ────────────────────────────────────

def disabled() -> bool:
    """True if Warden is globally (sentinel file) or per-session (env) disabled.
    The very first thing the dispatcher checks — an instant, global, no-restart
    off switch so a broken rule pulls out of every environment in one move."""
    if os.environ.get("WARDEN_DISABLED", "").strip().lower() in ("1", "true", "yes", "on"):
        return True
    return (warden_home() / "DISABLED").exists()


# ── event → moment mapping ([[Warden Events]]) ───────────────────────────────

_CONTENT_KIND = {
    ".md": "markdown", ".markdown": "markdown", ".rs": "rust",
    ".py": "python", ".json": "json", ".svg": "svg",
}


def content_kind(file_path: str) -> str | None:
    return _CONTENT_KIND.get(Path(file_path).suffix.lower())


def event_to_moments(data: dict) -> list[str]:
    """Map a Claude Code hook event payload to the Warden moment(s) it fires.
    Mirrors the [[Warden Events]] catalog; unknown/unmapped events → []."""
    event = data.get("hook_event_name", "")
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""

    if event == "PreToolUse":
        if tool == "Skill":
            skill = (tool_input.get("skill") or tool_input.get("command") or "").strip()
            return [f"skill:pre:{skill}"] if skill else ["skill:pre"]
        return [f"tool:pre:{tool}"] if tool else ["tool:pre"]
    if event == "PostToolUse":
        moments = [f"tool:post:{tool}"] if tool else ["tool:post"]
        if tool in ("Write", "Edit") and file_path:
            kind = content_kind(file_path)
            if kind:
                moments.append(f"write:{kind}")
        return moments
    if event == "SessionStart":
        return ["session:start"]
    if event == "Stop":
        return ["session:stop", "prompt:stop"]
    if event == "PreCompact":
        return ["session:compact"]
    if event == "UserPromptSubmit":
        return ["prompt:submit"]
    return []


# ── anchor resolution ────────────────────────────────────────────────────────

def find_anchor(start: Path) -> Path | None:
    """Walk up from `start` to the nearest directory holding `.anchor`."""
    cur = start.resolve()
    for d in [cur, *cur.parents]:
        if (d / ".anchor").is_file():
            return d
    return None


# ── operational log ──────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    try:
        home = warden_home()
        home.mkdir(parents=True, exist_ok=True)
        with (home / "hook.log").open("a", encoding="utf-8") as fh:
            fh.write(f"{time.time():.3f}\t{msg}\n")
    except OSError:
        pass


# ── dispatch ─────────────────────────────────────────────────────────────────

def dispatch(data: dict) -> list[str]:
    """Fire the moment(s) this event maps to against the cwd anchor; return
    steers. Assumes the kill switch has already been checked."""
    import warden_fire as wf

    moments = event_to_moments(data)
    if not moments:
        return []
    cwd = Path(data.get("cwd") or os.getcwd())
    anchor_root = find_anchor(cwd)
    if anchor_root is None:
        return []

    wdir = warden_home()
    ir_path = wdir / "rules-ir.json"
    if not ir_path.is_file():
        _log(f"no compiled IR at {ir_path} — run `warden compile` (event={data.get('hook_event_name')})")
        return []
    ir, module = wf.load_compiled(wdir, "all")
    traits = wf.read_anchor_traits(anchor_root)

    steers: list[str] = []
    for moment in moments:
        ctx = wf.build_ctx(anchor_root, moment)
        fired = wf.fire(ir, module, moment, ctx, traits)
        if fired:
            _log(f"FIRED {moment} @ {anchor_root.name} traits={traits} → {len(fired)} steer(s)")
            steers.extend(fired)

    # Doc-fire on write (F222): an anchor that opts in via the `audit-on-write`
    # trait runs its doc-audit rules on the freshly-written markdown file and
    # steers on failures — the /audit doc pass, triggered live by the edit.
    if "audit-on-write" in traits and any(m.startswith("write:markdown") for m in moments):
        fp = (data.get("tool_input") or {}).get("file_path") or ""
        aow = audit_on_write(Path(fp)) if fp else []
        if aow:
            _log(f"AUDIT-ON-WRITE {Path(fp).name} @ {anchor_root.name} → {len(aow)} issue steer(s)")
            steers.extend(aow)
    return steers


def audit_on_write(file_path: Path) -> list[str]:
    """Run the doc-audit rules on a written markdown file; return a steer naming
    each failing rule (empty when the file is clean, or on any error — fail-safe).
    Reuses `warden_docfire.fire_audit` (verdict-identical to `audit-plan`)."""
    try:
        import warden_docfire as wdf
        if not file_path.is_file():
            return []
        # Steer only on `fail` (a real content violation) — never on `error`
        # (an unimplemented/broken checker is a rule-infra gap, not the writer's
        # problem; surfacing it here is noise) nor `pass`.
        fails = [v for v in wdf.fire_audit(file_path.resolve(), "doc")
                 if v.get("status") == "fail"]
    except Exception as e:  # noqa: BLE001 — a doc-fire bug must never break the write
        _log(f"AUDIT-ON-WRITE ERROR {type(e).__name__}: {e}")
        return []
    if not fails:
        return []
    lines = "\n".join(f"  · {v['rule']}: {v.get('detail') or v.get('status')}" for v in fails)
    return [f"[warden audit-on-write] {file_path.name} has {len(fails)} issue(s) to fix:\n{lines}"]


def emit(event: str, steers: list[str]) -> None:
    """Write hook output that injects the steers as agent-visible context."""
    if not steers:
        return
    text = "\n\n".join(s for s in steers if s)
    if not text:
        return
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
    print(json.dumps(out))


def main(argv=None) -> int:
    # 1. kill switch — before ANY work.
    if disabled():
        return 0
    # 2. read the event; a malformed payload is a no-op, never an error.
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (ValueError, OSError):
        return 0
    # 3. dispatch — fail-safe: a Warden bug must never break the tool call.
    try:
        steers = dispatch(data)
        emit(data.get("hook_event_name", ""), steers)
    except Exception as e:  # noqa: BLE001 — deliberate catch-all fail-safe
        _log(f"ERROR {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
