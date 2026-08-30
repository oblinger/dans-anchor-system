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
import re
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

# ~25 MB x 3 generations (~75 MB). At the observed ~5.2 MB per 3 days that is
# roughly six weeks, against the 3.7 days the old 5 MB x 2 held -- which is why
# two of three counts on a nine-day soak came back ungradeable (T607). The log's
# job is explaining a recent surprise, and 75 MB is nothing against the
# questions it newly answers. Decided rather than asked (F068): the change is
# one constant and reversing it costs the same edit.
FIRES_ROTATE_BYTES = 25 * 1024 * 1024
FIRES_GENERATIONS = 3          # fires.jsonl + .1 + .2


# F613 Q2 (Dan, 2026-08-28): capture the command on EVERY Bash fire record.
# "Why wouldn't we capture everything?" — because a command line sometimes
# carries a credential. But every Claude session transcript already records
# every Bash command verbatim on the same disk, so this is a second copy of
# text that is already there, and the size is a few MB a week. The mask below
# is belt-and-braces for the two obvious shapes, not the reason the answer is
# yes; a value it misses is one the transcript holds anyway.
_SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*\s*=\s*)"
    r"(?:'[^']*'|\"[^\"]*\"|\S+)")
_BEARER_RE = re.compile(r"(?i)(bearer\s+)\S+")


def mask_secrets(cmd: str) -> str:
    """Blank the value of a `*KEY=`/`*TOKEN=`-style assignment and a bearer
    token, keeping the name so the shape of the command survives."""
    cmd = _SECRET_ASSIGN_RE.sub(lambda m: m.group(1) + "***", cmd)
    return _BEARER_RE.sub(lambda m: m.group(1) + "***", cmd)


def _fire_record(rec: dict) -> None:
    """Append one JSONL record to ~/.warden/fires.jsonl — the explainability
    log: which rules were considered at a moment, which fired, and the steer
    text VERBATIM as the agent received it. `warden log` is the viewer.
    Rotates past FIRES_ROTATE_BYTES across FIRES_GENERATIONS files."""
    try:
        home = warden_home()
        home.mkdir(parents=True, exist_ok=True)
        path = home / "fires.jsonl"
        if path.is_file() and path.stat().st_size > FIRES_ROTATE_BYTES:
            # Cascade oldest-first so no generation is skipped: .1 -> .2, then
            # live -> .1. Walking the other way would overwrite .1 with the live
            # file before .2 had been taken from it, silently losing a whole
            # generation on every rotation.
            for n in range(FIRES_GENERATIONS - 1, 1, -1):
                older = home / f"fires.jsonl.{n}"
                newer = home / f"fires.jsonl.{n - 1}"
                if newer.is_file():
                    newer.replace(older)
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
                "command": mask_secrets(_str(tool_input.get("command"))),
                "considered": [rid for rid, _ in records],
                "fires": [{"rule": rid, "steer": s}
                          for rid, produced in records for s in produced],
                # F601: rules whose steer an exception row quieted.
                "excepted": list(getattr(ctx, "excepted", None) or []),
                "ms": round(elapsed_ms, 1),
            })
        if fired:
            _log(f"FIRED {moment} @ {anchor_root.name} traits={traits} → {len(fired)} steer(s)"
                 + _indent_steers(fired))
            steers.extend(fired)

    # Doc-fire on write (F222 / F229 A′): governed by the FILE's anchor — the
    # `audit-on-write` trait now rides `anchor-base` (ir.base_traits), so every
    # anchored file is audited on write; an un-anchored file is not
    # (no anchor, no audit).
    #
    # F297: ANY typed write kind, not just `write:markdown` — the narrow
    # condition was what made a non-markdown document rule unreachable. Rule
    # selection per kind happens in `warden_docfire.rows_for`.
    write_moment = next((m for m in moments if m.startswith("write:")), None)
    if anchor_file is not None and write_moment and event_fp:
        if "audit-on-write" in wf.effective_traits(ir, anchor_file):
            steers.extend(_doc_fire(Path(event_fp), anchor_file,
                                    _str(data.get("tool_name")), write_moment))

    # F297 leg 2 — a file a SCRIPT wrote. A Bash event carries the command
    # string and nothing about what it touched, so `python3 make_diagram.py` is
    # invisible to every file-keyed moment. After the call, stat the governed
    # paths the compile resolved and doc-fire whatever moved (mirror of
    # `hook.rs`'s sweep).
    if ir.get("governed_paths") and "tool:post:Bash" in moments:
        for moved in _governed_moved(ir):
            owner = find_anchor(moved.parent)
            if owner is None or "audit-on-write" not in wf.effective_traits(ir, owner):
                continue
            steers.extend(_doc_fire(moved, owner, "Bash", "tool:post:Bash"))

    # F297 leg 3 — MARKDOWN a script wrote (mirror of `hook.rs`). Leg 2 fires on
    # `governed_paths`, which excludes markdown by construction: "markdown needs
    # no entry, since the write hook has always seen markdown". False — the
    # write hook sees the Write and Edit TOOLS, never `cat > x.md`, `sed -i`, or
    # a python heredoc. Widening `governed_paths` is the wrong repair, since
    # `_governed_moved` stats every entry per Bash call against ~8k vault
    # markdown files; the command string is already in hand, so read the
    # candidates out of it and stat only those.
    if "tool:post:Bash" in moments:
        cmd = _str((data.get("tool_input") or {}).get("command"))
        floor = _bash_pre_floor(_str(data.get("session_id")))
        for moved in _md_paths_in_command(cmd, cwd, floor):
            owner = find_anchor(moved.parent)
            if owner is None or "audit-on-write" not in wf.effective_traits(ir, owner):
                continue
            steers.extend(_doc_fire(moved, owner, "Bash", "tool:post:Bash"))
    # The floor stamp for the NEXT tool:post:Bash (mirror of hook.rs): a call
    # whose write lands more than FRESH_SECS before the call RETURNS has a
    # stale mtime at post time, and recency alone drops it silently (measured
    # 2026-08-22: `sed -i … x.md && sleep 25` took zero doc-fires).
    if "tool:pre:Bash" in moments:
        _stamp_bash_pre(_str(data.get("session_id")))
    return steers


def _bash_pre_dir() -> Path:
    return warden_home() / "bash-pre"


def _safe_sid(session_id: str) -> str:
    return "".join(c for c in session_id if c.isalnum() or c in "-_")


def _stamp_bash_pre(session_id: str) -> None:
    """Record "a Bash call started now" for this session (F297 leg 3 floor)."""
    sid = _safe_sid(session_id)
    if not sid:
        return
    try:
        d = _bash_pre_dir()
        d.mkdir(parents=True, exist_ok=True)
        (d / sid).write_text(str(time.time()))
    except OSError:
        pass


def _bash_pre_floor(session_id: str) -> float | None:
    """The mtime floor for this session's current Bash call, if a pre-stamp
    exists. Consumers OR this with the recency window, so a missing stamp
    degrades to today's behavior, never below it. One second of slack for the
    stamp-write/file-write race."""
    sid = _safe_sid(session_id)
    if not sid:
        return None
    try:
        return max(float((_bash_pre_dir() / sid).read_text().strip()) - 1.0, 0.0)
    except (OSError, ValueError):
        return None


def _md_paths_in_command(cmd: str, cwd: Path,
                         floor: float | None = None) -> list[Path]:
    """Markdown paths a Bash command names that were written by it.

    Two filters, and both matter. **Existence** keeps a false token cheap: a
    non-path ending `.md` costs one stat and never a steer. **Recency** is what
    separates a write from a read — `grep foo x.md` leaves mtime alone, so only
    a file touched during this call survives. Recency rather than an mtime
    snapshot on purpose: a snapshot cannot fire on a path's FIRST write, which
    is exactly the case that produced a bad dispatch table to begin with.
    """
    FRESH_SECS = 20
    now = time.time()
    out: list[Path] = []
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        # A quoted run is ONE token, spaces included — vault paths have spaces
        # ("Tink Track/Tink Backlog.md"), so splitting on whitespace alone would
        # shred exactly the paths this needs to see.
        if c in "'\"":
            j = cmd.find(c, i + 1)
            j = n if j < 0 else j
            tok, i = cmd[i + 1:j], j + 1
        elif c.isspace():
            i += 1
            continue
        else:
            j = i
            while j < n and not cmd[j].isspace() and cmd[j] not in "'\"":
                j += 1
            tok, i = cmd[i:j], j
        tok = tok.strip("<>|;&()`,:=")
        if not tok.endswith((".md", ".markdown")):
            continue
        path = Path(tok).expanduser() if tok.startswith(("/", "~")) else cwd / tok
        try:
            st = path.stat()
        except OSError:
            continue
        recent = (now - st.st_mtime) <= FRESH_SECS
        since_start = floor is not None and st.st_mtime >= floor
        if not path.is_file() or not (recent or since_start):
            continue
        if path not in out:
            out.append(path)
    return out


def _doc_fire(file: Path, owner: Path, tool: str, budget_moment: str) -> list[str]:
    """One doc-fire — the audit pass over `file`, owned by anchor `owner`.
    Shared by the on-write path and the F297 post-Bash sweep so a script's write
    and a direct write produce the same steers and the same fire record."""
    started = time.perf_counter()
    aow = audit_on_write(file)
    aow_ms = (time.perf_counter() - started) * 1000.0
    # F232 B3: the doc-fire is timed into the budget advisory like any moment
    # fire (it owes Python by construction — the audit import).
    warn = over_budget(budget_moment, aow_ms, owed_python=True)
    if warn:
        _log_perf("doc-fire " + warn)
    if not aow:
        return []
    _log(f"AUDIT-ON-WRITE {file.name} @ {owner.name} → {len(aow)} issue steer(s)"
         + _indent_steers(aow))
    _fire_record({
        "ts": round(time.time(), 3), "engine": "py", "moment": "doc-fire",
        "anchor": owner.name, "traits": [], "tool": tool, "file": str(file),
        "considered": ["audit-on-write"],
        "fires": [{"rule": "audit-on-write", "steer": s} for s in aow],
        "ms": round(aow_ms, 1),
    })
    return aow


def _governed_moved(ir: dict) -> list[Path]:
    """The governed paths whose mtime moved since the last sweep (F297 leg 2).

    The snapshot lives beside the compiled state and is keyed on the IR's
    `source_hash`: a recompile re-baselines rather than reporting the entire
    list as changed, and a path stat-able but absent from the previous snapshot
    is adopted silently for the same reason. Both directions fail quiet — a
    sweep that cannot read or write its snapshot reports nothing rather than
    firing on everything."""
    snap_path = warden_home() / "governed.json"
    stamp = ir.get("source_hash") or ""
    try:
        prev = json.loads(snap_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev = {}
    rebased = prev.get("source_hash") != stamp
    prev_m = prev.get("mtimes") or {}
    now_m: dict[str, int] = {}
    moved: list[Path] = []
    for p in ir["governed_paths"]:
        try:
            ns = os.stat(p).st_mtime_ns
        except OSError:
            continue
        was = prev_m.get(p)
        if was is not None and not rebased and was != ns:
            moved.append(Path(p))
        now_m[p] = ns
    if rebased or now_m != prev_m:
        try:
            snap_path.write_text(
                json.dumps({"source_hash": stamp, "mtimes": now_m}), encoding="utf-8")
        except OSError:
            pass
    return moved


def _mendable_rules() -> set[str]:
    """Rule ids the compiled corpus can teach a remediation for (F280).

    Derived from the IR, never hand-declared on the rule: a marker that is
    computed cannot promise a lesson the corpus does not have, and adding a
    mend block never requires touching the rules it teaches."""
    try:
        ir = json.loads((warden_home() / "rules-ir.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    have = ir.get("mend") or {}
    return {rid for rid, row in (ir.get("rules") or {}).items()
            if isinstance(row, dict) and row.get("mend") in have}


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
    mendable = _mendable_rules()
    lines = [f"  ✓ fixed {f['rule']} — {f.get('detail') or ''}".rstrip() for f in fixed]
    for m in messages:
        line = f"  · {m['rule']}: {m.get('detail') or 'fail'}"
        if m.get("why"):
            line += f"  [why: {m['why']}]"
        # F280: a bare marker, never a topic. The rule id is already on the
        # line, so a confused agent runs `warden mend <rule-id>`; one that
        # knows the convention reads past five characters.
        if m.get("rule") in mendable:
            line += "  mend"
        lines.append(line)
    head = f"[warden audit-on-write] {file_path.name}: " \
           f"{len(fixed)} auto-fixed, {len(messages)} issue(s) to fix by hand:" \
        if fixed else \
        f"[warden audit-on-write] {file_path.name} has {len(messages)} issue(s) to fix:"
    return [head + "\n" + "\n".join(lines)]


# ── F328: the DAS hook registry — Warden executes it for free ────────────────
#
# One file (~/.config/anchor-system/hooks/registry): each line is a moment,
# whitespace, one executable path — no inline arguments (grammar owned by DAS's
# hook-install / hook-run). Warden is already spawned at the moment, so fanning
# out from here costs zero additional processes; on Warden-less machines the
# `hook-run` fallback does the same job over the same file. Both executors log
# to the same file in the same line format, so "what fired when" reads uniform
# regardless of which executor fired it. A failing child is logged with its
# exit status and never suppresses its neighbours or the hook itself.
#
# A child's stdout is returned as a tell: it joins the steers on the same
# `additionalContext` surface its output would have landed on as a separate
# settings.json entry. (Structured hook-decision JSON from a registry child is
# not interpreted — a hook that needs `permissionDecision` keeps its own
# settings.json entry rather than a registry line.)

def _registry_path() -> Path:
    p = os.environ.get("DAS_HOOK_REGISTRY", "")
    return Path(p) if p else Path.home() / ".config/anchor-system/hooks/registry"


def _registry_log(line: str) -> None:
    p = os.environ.get("DAS_HOOK_LOG", "")
    path = Path(p) if p else Path.home() / ".config/anchor-system/hooks/hook-run.log"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def run_registry(data: dict, raw: str) -> list[str]:
    """Run every registry line matching this event's moments, in file order.

    Returns the children's non-empty stdouts as tells. Never raises."""
    import subprocess
    try:
        text = _registry_path().read_text()
    except OSError:
        return []
    moments = event_to_moments(data)
    tells: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(None, 1)
        if len(parts) != 2 or parts[0] not in moments:
            continue
        moment, cmd = parts[0], parts[1].rstrip()
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            res = subprocess.run([cmd], input=raw, capture_output=True, text=True)
        except OSError as e:
            _registry_log(f"{ts}  {moment}  error={e}  {cmd}")
            continue
        if res.returncode == 0:
            _registry_log(f"{ts}  {moment}  ok  {cmd}")
        else:
            _registry_log(f"{ts}  {moment}  exit={res.returncode}  {cmd}")
        if res.stdout.strip():
            tells.append(res.stdout.strip())
    return tells


# ── settings-registration staleness (2026-08-22; mirror of hook.rs) ─────────
#
# A session's hook registration is frozen at session start: editing
# ~/.claude/settings.json changes nothing for any LIVE session, and nothing
# says so (measured cost 45 min, 2026-08-22). Warden fires at SessionStart
# (matcher `*`), so it records what settings.json looked like when the session
# registered and says, once, on a later fire that the file has moved. Advisory
# only; every path is fail-quiet.

def _file_stamp(p: Path) -> str | None:
    """`mtime_ns:len` — engine-agnostic (hook.rs computes the identical string,
    and the two engines share the stamp dir; a content hash would need the
    same algorithm on both sides forever)."""
    try:
        st = p.stat()
        return f"{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        return None


def _settings_staleness_at(data: dict, settings_path: Path,
                           stamp_dir: Path) -> str | None:
    sid = "".join(c for c in _str(data.get("session_id"))
                  if c.isalnum() or c in "-_")
    if not sid:
        return None
    cur = _file_stamp(settings_path)
    if cur is None:
        return None
    try:
        stamp_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    f = stamp_dir / sid
    if _str(data.get("hook_event_name")) == "SessionStart":
        try:
            cutoff = time.time() - 7 * 24 * 3600
            for e in stamp_dir.iterdir():
                if e.stat().st_mtime < cutoff:
                    e.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            f.write_text(cur)
        except OSError:
            pass
        return None
    try:
        prev = f.read_text().strip()
    except OSError:
        try:
            f.write_text(cur)  # pre-feature session: adopt silently
        except OSError:
            pass
        return None
    if prev == cur:
        return None
    try:
        f.write_text(cur)  # one steer per change, not per call
    except OSError:
        pass
    return (f"[warden] {settings_path} changed after this session started. "
            "A session's hook registration is frozen at session start, so if "
            "the change touched `hooks`, THIS session is still running the old "
            "registration — restart (exit and relaunch/resume) to pick it up. "
            "Rule content (rulesets, compiled IR) is NOT affected: it reloads "
            "live.")


def _settings_staleness(data: dict) -> str | None:
    try:
        return _settings_staleness_at(
            data, Path.home() / ".claude/settings.json",
            warden_home() / "settings-stamp")
    except Exception:  # noqa: BLE001 — advisory only, never in the way
        return None


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
        # F328: fan out to the DAS hook registry at this event's moments —
        # children's stdout joins the steers as agent-visible context.
        steers = steers + run_registry(data, raw)
        # Settings-registration staleness — one advisory line when
        # settings.json moved under a live session (mirror of hook.rs).
        stale = _settings_staleness(data)
        if stale:
            _log(f"SETTINGS-STALE steer issued (session {_str(data.get('session_id'))})")
            steers = steers + [stale]
        emit(data.get("hook_event_name", ""), steers)
    except Exception as e:  # noqa: BLE001 — deliberate catch-all fail-safe
        _log(f"ERROR {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
