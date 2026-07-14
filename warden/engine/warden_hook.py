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


def _str(v) -> str:
    """A payload field coerced to str — a malformed (non-string) field must
    degrade to 'absent', never abort the whole dispatch (F232 C3; the Rust
    engine already degrades per-field)."""
    return v if isinstance(v, str) else ""


def _dict(v) -> dict:
    return v if isinstance(v, dict) else {}


def event_to_moments(data: dict) -> list[str]:
    """Map a Claude Code hook event payload to the Warden moment(s) it fires.
    Mirrors the [[Warden Events]] catalog; unknown/unmapped events → []."""
    event = _str(data.get("hook_event_name"))
    tool = _str(data.get("tool_name"))
    tool_input = _dict(data.get("tool_input"))
    file_path = _str(tool_input.get("file_path"))

    if event == "PreToolUse":
        if tool == "Skill":
            skill = (_str(tool_input.get("skill")) or _str(tool_input.get("command"))).strip()
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


# ── stale-path self-check (Audit 2026-07-12 W2) ─────────────────────────────

def _stale_paths(ir: dict) -> list[str]:
    """Dead absolute paths in the compiled state — the IR `root` and the
    `daemon.cmd` script are snapshots taken at `warden compile` time; after a
    repo move/rename they dangle and the whole veto + doc-fire surface
    silently no-ops (Audit 2026-07-12 W2 — the exact ob-skills→dans-anchor-system
    incident). One line per dead path; empty = healthy. Detection only —
    callers warn loudly but stay fail-open."""
    out: list[str] = []
    root = ir.get("root") or ""
    if root and not Path(root).is_dir():
        out.append(f"compiled IR root missing: {root}")
    cmd_p = warden_home() / "daemon.cmd"
    if cmd_p.is_file():
        try:
            import shlex
            toks = shlex.split(cmd_p.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            toks = []
        # daemon.cmd is `python3 <script> --serve` — the script is token 2.
        for t in toks[1:2]:
            if t and not Path(t).is_file():
                out.append(f"daemon.cmd target missing: {t}")
    return out


# ── anchor resolution ────────────────────────────────────────────────────────

def find_anchor(start: Path) -> Path | None:
    """Walk up from `start` to the nearest directory holding `.anchor`."""
    cur = start.resolve()
    for d in [cur, *cur.parents]:
        if (d / ".anchor").is_file():
            return d
    return None


_MIRROR_ROUTES = Path.home() / ".config/anchor-system/mirror-routes.json"


def mirror_route_anchor(file_path: str, routes_file: Path = _MIRROR_ROUTES) -> Path | None:
    """Resolve a repo-side mirror-route file to its declaring vault anchor.

    Two-Way Doc Mirror routes (F188) live in code repos outside any anchor
    tree, so `find_anchor` sees nothing there — exactly where R-code-mirror
    must fire. The routes index (written by every `code sync`) maps each
    repo-side route back to the `.anchor` that declared it; per F229 A'
    (the file's anchor owns the file) that vault anchor governs the copies.
    """
    try:
        routes = json.loads(routes_file.read_text()).get("routes", [])
    except (OSError, ValueError):
        return None
    try:
        fp = Path(file_path).resolve()
    except OSError:
        fp = Path(file_path)
    for e in routes:
        there, anchor = e.get("there"), e.get("anchor")
        if not there or not anchor:
            continue
        try:
            t = Path(there).resolve()
        except OSError:
            t = Path(there)
        if fp == t or t in fp.parents:
            d = Path(anchor).parent
            if (d / ".anchor").is_file():
                return d
    return None


# ── per-moment ms budget (M5 — advisory policy, PRD Q3 resolved 2026-07-05) ──
# Over-budget fires are LOGGED, never dropped/demoted: demote-to-audit stays a
# future escalation to take only if advisory data shows a persistent offender.

def budget_ms(moment: str, owed_python: bool = False) -> float:
    """The PRD § Performance per-moment budget (p99, fire-time).

    A moment that owes a Python body/guard round-trip is budgeted at the
    post-hoc 10 ms rate even at tool:pre — the F213 phase-2 design accepts
    ~4 ms of resident-daemon IPC whenever rule-authored Python must run, so
    holding such fires to the 2 ms pure-selection budget just logs the same
    known design cost on every call (the 2026-07-06 hook.log flood: 806 of
    861 lines were tool:pre:Bash breaching 2 ms by the IPC floor)."""
    if moment.startswith("tool:pre"):
        return 10.0 if owed_python else 2.0
    if moment.startswith(("tool:post", "write:", "read:")):
        return 10.0
    return 100.0  # session:* / prompt:* / git:* / timer: — rare, cost amortized


def over_budget(moment: str, elapsed_ms: float, owed_python: bool = False) -> str | None:
    """The advisory log line for an over-budget fire, or None when inside it."""
    b = budget_ms(moment, owed_python)
    if elapsed_ms <= b:
        return None
    return f"OVER-BUDGET {moment} fired in {elapsed_ms:.1f} ms (budget {b:g} ms)"


# ── operational log ──────────────────────────────────────────────────────────

def _append(name: str, line: str) -> None:
    try:
        home = warden_home()
        home.mkdir(parents=True, exist_ok=True)
        with (home / name).open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def _stamp() -> str:
    """Human-readable local timestamp, ms precision (per user direction
    2026-07-06 — epoch floats told the reader nothing)."""
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"


def _log(msg: str) -> None:
    _append("hook.log", f"{_stamp()}  {msg}\n")


def _log_perf(msg: str) -> None:
    """Advisory perf lines (OVER-BUDGET) go to their own file — at one line per
    breaching call they drown hook.log's operational signal otherwise."""
    _append("perf.log", f"{_stamp()}  {msg}\n")


def _indent_steers(steers: list[str]) -> str:
    """The steer text itself, indented under the log line — the part the reader
    actually wants ('1 issue steer(s)' alone says nothing)."""
    return "".join("\n        " + ln for s in steers for ln in s.splitlines())


# ── fire record (F231 — the why-did-that-happen log) ────────────────────────

FIRES_ROTATE_BYTES = 5 * 1024 * 1024


def _fire_record(rec: dict) -> None:
    """Append one JSONL record to ~/.warden/fires.jsonl — the explainability
    log: which rules were considered at a moment, which fired, and the steer
    text VERBATIM as the agent received it. `warden log` is the viewer.
    Rotates once past ~5 MB (single .1 generation)."""
    try:
        home = warden_home()
        home.mkdir(parents=True, exist_ok=True)
        path = home / "fires.jsonl"
        if path.is_file() and path.stat().st_size > FIRES_ROTATE_BYTES:
            path.replace(home / "fires.jsonl.1")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
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
    cwd = Path(_str(data.get("cwd")) or os.getcwd())
    anchor_cwd = find_anchor(cwd)
    tool_input = _dict(data.get("tool_input"))
    event_fp = _str(tool_input.get("file_path")) or None
    anchor_file = find_anchor(Path(event_fp).parent) if event_fp else None
    if anchor_file is None and event_fp:
        anchor_file = mirror_route_anchor(event_fp)
    if anchor_cwd is None and anchor_file is None:
        return []

    wdir = warden_home()
    ir_path = wdir / "rules-ir.json"
    if not ir_path.is_file():
        _log(f"no compiled IR at {ir_path} — run `warden compile` (event={data.get('hook_event_name')})")
        return []
    ir, module = wf.load_compiled(wdir, "all")

    # Audit 2026-07-12 W2: loudly surface compiled-state paths that no longer
    # resolve (repo moved/renamed) — fail-open, so dispatch continues on
    # whatever still works, but the staleness is never symptom-free again.
    stale = _stale_paths(ir)
    if stale:
        detail = "; ".join(stale)
        _log(f"STALE — {detail} (repo moved? run `warden install`)")
        print(f"warden: STALE — {detail} (repo moved? run `warden install`)",
              file=sys.stderr)

    # F131: the pending tool call as an injected object — veto-path rules test
    # `event.tool` / `event.target` / `event.input` before the call lands.
    import types
    event_view = types.SimpleNamespace(
        tool=_str(data.get("tool_name")), target=event_fp, input=tool_input)
    steers: list[str] = []
    if stale and "session:start" in moments:
        steers.append(f"[warden] STALE compiled state — {detail}; "
                      "run `warden install` (rules are NOT enforcing until then)")
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
        records = wf.fire_records(ir, module, moment, ctx, traits)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        owed = any(ir["rules"][rid].get("body_py") or ir["rules"][rid].get("guard_py")
                   for rid, _ in records)
        warn = over_budget(moment, elapsed_ms, owed)
        if warn:
            _log_perf(warn)
        fired = [s for _, produced in records for s in produced]
        if records:
            _fire_record({
                "ts": round(time.time(), 3), "engine": "py", "moment": moment,
                "anchor": anchor_root.name, "traits": traits,
                "tool": data.get("tool_name") or "", "file": event_fp or "",
                "considered": [rid for rid, _ in records],
                "fires": [{"rule": rid, "steer": s}
                          for rid, produced in records for s in produced],
                "ms": round(elapsed_ms, 1),
            })
        if fired:
            _log(f"FIRED {moment} @ {anchor_root.name} traits={traits} → {len(fired)} steer(s)"
                 + _indent_steers(fired))
            steers.extend(fired)

    # Doc-fire on write (F222 / F229 A′): governed by the FILE's anchor — the
    # `audit-on-write` trait now rides `anchor-base` (ir.base_traits), so every
    # anchored markdown file is audited on write; an un-anchored file is not
    # (no anchor, no audit).
    if anchor_file is not None and any(m.startswith("write:markdown") for m in moments):
        if "audit-on-write" in wf.effective_traits(ir, anchor_file):
            aow_started = time.perf_counter()
            aow = audit_on_write(Path(event_fp)) if event_fp else []
            aow_ms = (time.perf_counter() - aow_started) * 1000.0
            # F232 B3: the doc-fire is timed into the budget advisory like any
            # moment fire (it owes Python by construction — the audit import).
            warn = over_budget("write:markdown", aow_ms, owed_python=True)
            if warn:
                _log_perf("doc-fire " + warn)
            if aow:
                _log(f"AUDIT-ON-WRITE {Path(event_fp).name} @ {anchor_file.name} → {len(aow)} issue steer(s)"
                     + _indent_steers(aow))
                _fire_record({
                    "ts": round(time.time(), 3), "engine": "py", "moment": "doc-fire",
                    "anchor": anchor_file.name, "traits": [],
                    "tool": data.get("tool_name") or "", "file": event_fp or "",
                    "considered": ["audit-on-write"],
                    "fires": [{"rule": "audit-on-write", "steer": s} for s in aow],
                    "ms": round(aow_ms, 1),
                })
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
