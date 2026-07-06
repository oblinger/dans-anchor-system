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

This is the productionisation layer above `warden_fire`. Steers land as
`additionalContext`; a `DENY: `-sentinel steer at a PreToolUse event lands as a
real `permissionDecision: deny` (F131 — the veto path, un-deferring Integration
Strategy D5). Outside PreToolUse the sentinel degrades to a plain steer —
deny is `tool:pre`-only per [[Warden Semantics]] § deny, fail-open elsewhere.
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
    # F217 loop prevention (wall 1): an oracle session is moment-silent — its
    # own tool uses and turn boundaries must never reach the ledger or fire
    # rules. The judge is not an observed agent.
    if os.environ.get("WARDEN_ORACLE", "").strip():
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


# ── per-moment ms budget (M5 — advisory policy, PRD Q3 resolved 2026-07-05) ──
# Over-budget fires are LOGGED, never dropped/demoted: demote-to-audit stays a
# future escalation to take only if advisory data shows a persistent offender.

def budget_ms(moment: str) -> float:
    """The PRD § Performance per-moment budget (p99, fire-time)."""
    if moment.startswith("tool:pre"):
        return 2.0
    if moment.startswith(("tool:post", "write:", "read:")):
        return 10.0
    return 100.0  # session:* / prompt:* / git:* / timer: — rare, cost amortized


def over_budget(moment: str, elapsed_ms: float) -> str | None:
    """The advisory log line for an over-budget fire, or None when inside it."""
    b = budget_ms(moment)
    if elapsed_ms <= b:
        return None
    return f"OVER-BUDGET {moment} fired in {elapsed_ms:.1f} ms (budget {b:g} ms)"


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
    """Fire the moment(s) this event maps to; return steers. Assumes the kill
    switch has already been checked.

    Anchor resolution (F229 A′): any moment whose event carries an anchored
    file — `write:`/`read:`, file-bearing tool moments like `tool:pre:Edit`,
    and the audit-on-write doc-fire — is governed by the **file's anchor**:
    the file's anchor owns the file, wherever the session sits. Everything
    else (Bash, session, prompt moments) is governed by the session's cwd
    anchor, which is also the fallback when the file is un-anchored; the
    doc-fire is strictly file-anchored (no anchor, no audit). File-governance
    for tool moments closed the 2026-07-06 adoption-audit gap: a cwd outside
    the guarded anchor let `tool:pre:Edit` deny rules (R-pathguard) be
    side-stepped entirely."""
    import warden_fire as wf

    moments = event_to_moments(data)
    if not moments:
        return []
    cwd = Path(data.get("cwd") or os.getcwd())
    anchor_cwd = find_anchor(cwd)
    tool_input = data.get("tool_input") or {}
    event_fp = tool_input.get("file_path") or None
    anchor_file = find_anchor(Path(event_fp).parent) if event_fp else None
    if anchor_cwd is None and anchor_file is None:
        return []

    wdir = warden_home()
    ir_path = wdir / "rules-ir.json"
    if not ir_path.is_file():
        _log(f"no compiled IR at {ir_path} — run `warden compile` (event={data.get('hook_event_name')})")
        return []
    ir, module = wf.load_compiled(wdir, "all")

    # F131: the pending tool call as an injected object — veto-path rules test
    # `event.tool` / `event.target` / `event.input` before the call lands.
    import types
    event_view = types.SimpleNamespace(
        tool=data.get("tool_name") or "", target=event_fp, input=tool_input)
    steers: list[str] = []
    for moment in moments:
        anchor_root = anchor_file or anchor_cwd
        if anchor_root is None:
            continue
        traits = wf.effective_traits(ir, anchor_root)
        # F216: bind the agent-state view to the session that produced this
        # event (lazy — costs nothing unless a rule reads agent.*).
        # F215: the event's file path lets fire() bind ctx.file per rule.
        import warden_agent as wa
        ctx = wf.build_ctx(anchor_root, moment, agent=wa.make_agent(data, moment),
                           file_path=event_fp, event=event_view, traits=traits,
                           git_aspect=wf.git_aspect_of(traits))
        t0 = time.perf_counter()
        fired = wf.fire(ir, module, moment, ctx, traits)
        warn = over_budget(moment, (time.perf_counter() - t0) * 1000.0)
        if warn:
            _log(warn)
        if fired:
            _log(f"FIRED {moment} @ {anchor_root.name} traits={traits} → {len(fired)} steer(s)")
            steers.extend(fired)

    # Doc-fire on write (F222 / F229 A′): governed by the FILE's anchor — the
    # `audit-on-write` trait now rides `anchor-base` (ir.base_traits), so every
    # anchored markdown file is audited on write; an un-anchored file is not
    # (no anchor, no audit).
    if anchor_file is not None and any(m.startswith("write:markdown") for m in moments):
        if "audit-on-write" in wf.effective_traits(ir, anchor_file):
            aow = audit_on_write(Path(event_fp)) if event_fp else []
            if aow:
                _log(f"AUDIT-ON-WRITE {Path(event_fp).name} @ {anchor_file.name} → {len(aow)} issue steer(s)")
                steers.extend(aow)
    return steers


def audit_on_write(file_path: Path) -> list[str]:
    """Run the doc-audit rules on a written markdown file: mechanical fails
    WITH a `fix::` are repaired in place (audit-plan's fixer registry +
    never-delete floor — M4a fixer parity with the bespoke F177 hook);
    fails without one are steered. Empty when clean or on any error
    (fail-safe). Reuses `warden_docfire.fire_on_write`."""
    try:
        import warden_docfire as wdf
        if not file_path.is_file():
            return []
        # `error` verdicts never surface (an unimplemented/broken checker is a
        # rule-infra gap, not the writer's problem) — execute_on_write only
        # reports genuine `fail`s.
        report = wdf.fire_on_write(file_path.resolve())
    except Exception as e:  # noqa: BLE001 — a doc-fire bug must never break the write
        _log(f"AUDIT-ON-WRITE ERROR {type(e).__name__}: {e}")
        return []
    fixed, messages = report.get("fixed", []), report.get("messages", [])
    if not fixed and not messages:
        return []
    lines = [f"  ✓ fixed {f['rule']} — {f.get('detail') or ''}".rstrip() for f in fixed]
    for m in messages:
        line = f"  · {m['rule']}: {m.get('detail') or 'fail'}"
        if m.get("why"):
            line += f"  [why: {m['why']}]"
        lines.append(line)
    head = f"[warden audit-on-write] {file_path.name}: " \
           f"{len(fixed)} auto-fixed, {len(messages)} issue(s) to fix by hand:" \
        if fixed else \
        f"[warden audit-on-write] {file_path.name} has {len(messages)} issue(s) to fix:"
    return [head + "\n" + "\n".join(lines)]


DENY_SENTINEL = "DENY: "


def emit(event: str, steers: list[str]) -> None:
    """Write hook output that injects the steers as agent-visible context.

    F131 veto path: at a PreToolUse event, `DENY: `-sentinel steers become a
    real `permissionDecision: deny` whose reason is the deny text(s) — the tool
    call is refused and the agent sees the redirect. At any other event the
    sentinel is stripped and the steer lands as plain context (deny is
    `tool:pre`-only; fail-open, never fail-closed)."""
    if not steers:
        return
    denies = [s[len(DENY_SENTINEL):] for s in steers if s.startswith(DENY_SENTINEL)]
    tells = [s for s in steers if s and not s.startswith(DENY_SENTINEL)]
    hso: dict = {"hookEventName": event}
    if denies and event == "PreToolUse":
        hso["permissionDecision"] = "deny"
        hso["permissionDecisionReason"] = "\n\n".join(denies)
    else:
        tells = tells + denies  # non-pre deny degrades to a plain steer
    text = "\n\n".join(tells)
    if text:
        hso["additionalContext"] = text
    if len(hso) == 1:
        return
    print(json.dumps({"hookSpecificOutput": hso}))


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
