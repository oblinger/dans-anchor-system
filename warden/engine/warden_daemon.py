#!/usr/bin/env python3
"""Warden resident interpreter (F213 phase 2) — the warm Python half of the hot
path.

The Rust hook binary (`warden-rs hook`) owns selection; a rule whose guard or
body is *Python* (`guard_py`/`body_py`) is owed a round-trip to this daemon,
which holds the compiled IR + rules module **preloaded in memory** — so a
Python body pays a socket round-trip, never an interpreter startup (the cost
that blows the per-moment ms budget).

Protocol: one JSON request per connection on the Unix socket
`$WARDEN_HOME/daemon.sock`, newline-terminated; one JSON response back.

  {"op": "ping"}                                   → {"ok": true, "pid": N}
  {"op": "fire_rules", "moment": m,
   "anchor_root": path, "rule_ids": [...],
   "session": {session_id, transcript_path, cwd}}  → {"ok": true, "steers_by_rule": {id: [..]}}
                                                      (session optional — feeds the F216
                                                       registry/ledger + binds ctx.agent)
  {"op": "audit", "file_path": p}                  → {"ok": true, "steers": [...]}
  {"op": "reload"}                                 → {"ok": true}
  {"op": "shutdown"}                               → {"ok": true}

`fire_rules` runs each requested rule through the *reference* fire path
(`warden_fire.fire` with a single-rule moment bucket) so the semantics —
active-set gating, declarative guards, `guard_py`, `body_py`/action — are the
Python reference's by construction, per-rule so the caller can interleave the
steers back into bucket order. `audit` is the warm doc-fire
(`warden_hook.audit_on_write`) — the expensive audit-plan import happens once
per daemon lifetime instead of once per markdown write.

Fail-safe like every Warden surface: a request that raises returns
{"ok": false, "error": ...} and the daemon keeps serving. The compiled
artifacts auto-reload when `rules-ir.json` / `rules_all.py` change on disk
(`warden compile` refreshes them; the daemon notices on the next request).
The daemon exits after `--idle-exit` seconds without a request (default 30
min) — the Rust hook respawns it on demand, so a stale process never lingers.
It **also** exits when the engine's own `*.py` change under it and go quiet
(`engine_stale`), because idle-exit alone only collects engine edits during a
30-minute lull — which never happens while someone is working, the exact
window in which engine edits are made. Two staleness paths, two mechanisms:
`audit-plan.py` reloads in place (it is a leaf); the engine restarts.

Concurrency (F232 B1, T013): the server is THREAD-PER-CONNECTION — one slow
request (an `audit` op, a rule body calling `ask_oracle` with its 60 s
subprocess ceiling) must never block every other session's hooks behind a
serial accept-handle loop. The slow paths are I/O- and subprocess-bound, so
Python threads give real concurrency here. Shared state is lock-guarded:
`TURN_FIRED` (the F217 dedup ring), the F216 session registry (its own lock
in warden_agent), and the Corpus reload. Idle-exit counts only quiet time
with zero requests in flight.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_agent as wa  # noqa: E402
import warden_fire as wf  # noqa: E402
import warden_hook as wh  # noqa: E402


def warden_home() -> Path:
    return Path(os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))


def socket_path() -> Path:
    return warden_home() / "daemon.sock"


def pid_path() -> Path:
    return warden_home() / "daemon.pid"


# ── the preloaded corpus ─────────────────────────────────────────────────────

class Corpus:
    """The compiled IR + rules module, held warm; reloads when the artifacts
    change on disk (cheap mtime stat per request). Reload is lock-guarded
    (T013 — concurrent handler threads must not reload twice); readers grab
    the `(ir, module)` pair via `snapshot()` — ONE reference read (Audit
    2026-07-12 W7: `self.ir, self.module = …` was two attribute stores, so a
    reader could pair a new IR with an old module across a concurrent reload)."""

    def __init__(self, home: Path):
        self.home = home
        self._pair: tuple = ({}, None)
        self._stamp: tuple = ()
        self._lock = threading.Lock()
        self.reload()

    @property
    def ir(self) -> dict:
        return self._pair[0]

    @property
    def module(self):
        return self._pair[1]

    def snapshot(self) -> tuple:
        """The (ir, module) pair as one atomic reference grab (Audit
        2026-07-12 W7) — always internally consistent, even mid-reload."""
        return self._pair

    def _artifact_stamp(self) -> tuple:
        stamp = []
        for name in ("rules-ir.json", "rules_all.py"):
            p = self.home / name
            stamp.append(p.stat().st_mtime_ns if p.is_file() else 0)
        return tuple(stamp)

    def reload(self) -> None:
        with self._lock:
            self._pair = tuple(wf.load_compiled(self.home, "all"))
            self._stamp = self._artifact_stamp()

    def fresh(self) -> None:
        if self._artifact_stamp() != self._stamp:
            self.reload()


# ── the compile sweep: dirty + quiet → recompile ─────────────────────────────
#
# A ruleset edited and never compiled leaves `rules-ir.json` behind its sources.
# The doc-fire path does not care (it flattens the rulesets from SOURCE on every
# write), but two surfaces do: the **moment** rules — the `tool:pre` deny rules
# that fire before a Bash or an Edit — and `warden mend <rule-id>`, both of which
# read only the compiled IR. So a rule can be authored, be live on writes, and
# still be invisible at the moment it was written for.
#
# Dan's design, 2026-08-10, and the debounce is the load-bearing half: scan on a
# slow interval, but only recompile once the newest edit has gone QUIET. Without
# the quiet window an agent mid-edit would trigger a compile per save; with it, a
# burst of edits costs exactly one compile after the burst ends. Same shape as
# HookAnchor's ~30 s settle, for the same reason.
#
# Both knobs are config, in ~/.config/anchor-system/warden/config.yaml:
#     compile_scan_minutes: 10     # how often to look; 0 disables the sweep
#     compile_quiet_minutes: 2     # how long the newest edit must have been still
_SWEEP_DEFAULTS = {"compile_scan_minutes": 10.0, "compile_quiet_minutes": 2.0}


def _sweep_config() -> dict:
    cfg = dict(_SWEEP_DEFAULTS)
    p = Path.home() / ".config/anchor-system/warden/config.yaml"
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            for k in _SWEEP_DEFAULTS:
                if line.startswith(k + ":"):
                    try:
                        cfg[k] = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
    except OSError:
        pass
    return cfg


def _rulesets_newest_ns() -> int:
    """Newest mtime across the rule sources. ~0.3 ms for 117 files, and it only
    runs once per scan interval, so the sweep's cost is not worth measuring."""
    try:
        import warden_root
        root = warden_root.corpus_root() / "rulesets"
        return max((p.stat().st_mtime_ns for p in root.rglob("*.md")), default=0)
    except Exception:
        return 0


def _engine_newest_ns() -> int:
    """Newest mtime across the engine's OWN Python — the modules this process
    imported at start and holds for its whole life.

    Tests are excluded deliberately: the daemon never imports them, so saving a
    test file must not bounce a live daemon. ~14 stats, once per scan interval.
    """
    try:
        return max((p.stat().st_mtime_ns for p in HERE.glob("*.py")
                    if not p.name.startswith("test_") and p.name != "conftest.py"),
                   default=0)
    except OSError:
        return 0


def engine_stale(loaded_ns: int) -> str | None:
    """Has the engine's own code changed under the running process?

    `audit-plan.py` reloads in place (warden_docfire.refresh_audit_plan) because
    it is a leaf: a dict of checkers and fixers with no threads, no sockets and
    no module-level state anyone holds a reference to. **The engine modules are
    the opposite** — `warden_daemon` holds the accept loop, `warden_fire` the
    dedup ring, `warden_agent` the session registry, each behind its own lock,
    and handler threads are running against all of them. Re-exec'ing those in
    place would leave live threads split across two copies of the same module.

    So the engine's answer to staleness is to **exit** and let the Rust hook
    respawn — a genuinely fresh interpreter, which is what `--idle-exit` already
    relied on. The only thing that changes here is *when*: idle-exit needs 30
    quiet minutes, which never arrive during a working session, so engine edits
    could sit unloaded indefinitely for exactly as long as someone was using
    the system. That is how F319's spine checkers were live on disk and dead in
    the daemon. Dan, 2026-08-10: *"the Python should also be reloaded by the
    daemon — both should be checked."*

    The quiet window is shared with the compile sweep and is load-bearing for a
    second reason here: restarting into a half-written `.py` would fail to boot,
    and the hook would respawn into the same broken file every time.
    """
    try:
        newest = _engine_newest_ns()
        if not newest or newest <= loaded_ns:
            return None
        quiet_ns = _sweep_config()["compile_quiet_minutes"] * 60 * 1e9
        if (time.time_ns() - newest) < quiet_ns:
            return None                              # still being edited
        return (f"engine code changed {(newest - loaded_ns) / 1e9:.0f}s after this "
                f"process loaded it — exiting so the next hook respawns fresh")
    except Exception as e:                           # noqa: BLE001 — accept loop
        # A non-None return EXITS the daemon, so a broken check must answer
        # None — never bounce the process on its own bug. Loud, but not fatal.
        wh._log(f"DAEMON ENGINE-STALE CHECK ERROR ({type(e).__name__}: {e})")
        return None


def compile_sweep(home: Path) -> str | None:
    """One tick. Returns a log line when it recompiled, else None.

    Deliberately reports NOTHING when clean — a sweep that narrates every quiet
    tick is a sweep people turn off. **Total by construction**: this runs on the
    daemon's accept loop, so anything it raised would take the whole hook
    surface down with it. A housekeeping task must never be able to do that.
    """
    try:
        return _compile_sweep(home)
    except Exception as e:                       # noqa: BLE001 — see the docstring
        return f"COMPILE-SWEEP ERROR ({type(e).__name__}: {e})"


def _compile_sweep(home: Path) -> str | None:
    cfg = _sweep_config()
    if cfg["compile_scan_minutes"] <= 0:
        return None
    newest = _rulesets_newest_ns()
    if not newest:
        return None
    try:
        compiled = (home / "rules-ir.json").stat().st_mtime_ns
    except OSError:
        compiled = 0
    if newest <= compiled:
        return None                                  # not dirty
    quiet_ns = cfg["compile_quiet_minutes"] * 60 * 1e9
    if (time.time_ns() - newest) < quiet_ns:
        return None                                  # dirty, but still being edited
    try:
        import warden_compile as wc
        import warden_scan as ws
        import warden_root
        root = warden_root.corpus_root()
        files, seen, _ = ws.build_index(str(root), {}, {}, rescan=True)
        index = {"root": str(root), "files": files, "seen": seen}
        ir, module_src, _ = wc.compile_corpus(root, index, "all", ws.index_hash(files))
        wc._write_artifacts(home, "all", ir, module_src)
    except Exception as e:
        # Fail OPEN and say so. A sweep that cannot compile must not take the
        # daemon down with it — the artifacts on disk still serve, just stale,
        # which is exactly the state this whole mechanism exists to make loud.
        return f"COMPILE-SWEEP FAILED ({type(e).__name__}: {e}) — IR left stale"
    return (f"COMPILE-SWEEP recompiled {len(ir.get('rules') or {})} rules — sources were "
            f"{(newest - compiled) / 1e9:.0f}s ahead of the compiled IR")


# ── request handlers ─────────────────────────────────────────────────────────

# F217 wall 2: (rule_id, session_id, turn_key) triples already fired — bounded
# ring; membership checks are O(n) over ≤512 entries, well inside the budget.
# Lock-guarded (T013): handler threads race the check-then-append otherwise.
from collections import deque  # noqa: E402

TURN_FIRED: deque = deque(maxlen=512)
_TURN_LOCK = threading.Lock()

def _fire_rules(corpus: Corpus, req: dict) -> dict:
    """Run the requested rules through the reference fire path, one rule per
    single-rule bucket so steers stay per-rule (the caller re-interleaves)."""
    moment = req["moment"]
    anchor_root = Path(req["anchor_root"])
    rule_ids = req.get("rule_ids", [])
    # Audit 2026-07-12 W7: one snapshot for the whole request — reading
    # corpus.ir / corpus.module separately could straddle a concurrent reload.
    ir, module = corpus.snapshot()
    # F216: record the moment in the session registry/ledger and bind the
    # agent-state view. The ledger holds the moments this daemon sees (owed
    # round-trips); full history comes from the transcript tail, which the
    # classifier reads — so a sparse ledger degrades recency, not correctness.
    session = wa.session_of(req.get("session"))
    wa.observe(session, moment)
    agent = wa.AgentView(session, moment)
    # F215: the event's file path (write:/read: moments) — fire() binds
    # ctx.file per file-bearing rule from it.
    # F131: the pending tool call (tool:pre veto path) — rules test
    # event.tool / event.target / event.input.
    import types
    event_view = types.SimpleNamespace(
        tool=req.get("tool_name") or "",
        target=req.get("file_path") or None,
        input=req.get("tool_input") or {})
    ctx = wf.build_ctx(anchor_root, moment, agent=agent,
                       file_path=req.get("file_path") or None,
                       event=event_view)
    traits = wf.effective_traits(ir, anchor_root)
    # F217 loop prevention (wall 2): a turn-bearing rule fires once per
    # (rule, session, turn) — a Stop-steer continuation extends the SAME turn
    # (no new prompt:submit), so the extended turn cannot re-trigger the rule
    # that steered it. A genuinely new turn resets the key.
    tkey = wa.turn_key(agent._records()) if session else None
    by_rule: dict[str, list[str]] = {}
    for rid in rule_ids:
        row = ir.get("rules", {}).get(rid)
        if row is None:
            by_rule[rid] = []
            continue
        dedup = None
        if row.get("turn_bearing") and session and tkey:
            dedup = (rid, session.get("session_id", ""), tkey)
            with _TURN_LOCK:
                if dedup in TURN_FIRED:
                    by_rule[rid] = []
                    continue
        one = dict(ir)
        one["moments"] = {moment: [rid]}
        by_rule[rid] = wf.fire(one, module, moment, ctx, traits)
        if by_rule[rid] and dedup:
            with _TURN_LOCK:
                if dedup not in TURN_FIRED:
                    TURN_FIRED.append(dedup)
    return {"ok": True, "steers_by_rule": by_rule}


def handle(corpus: Corpus, req: dict) -> dict:
    op = req.get("op", "")
    if op == "ping":
        return {"ok": True, "pid": os.getpid()}
    if op == "reload":
        corpus.reload()
        return {"ok": True}
    if op == "fire_rules":
        corpus.fresh()
        return _fire_rules(corpus, req)
    if op == "audit":
        corpus.fresh()
        return {"ok": True, "steers": wh.audit_on_write(Path(req["file_path"]))}
    if op == "shutdown":
        return {"ok": True, "_shutdown": True}
    return {"ok": False, "error": f"unknown op {op!r}"}


def _safe_handle(corpus: Corpus, req: dict) -> dict:
    """One request, fail-safe. Catches BaseException, not Exception (F232 B4):
    a rule body calling sys.exit() raises SystemExit, which must degrade to a
    failed request — never kill the shared daemon. KeyboardInterrupt (the
    operator's own Ctrl-C) still terminates."""
    try:
        return handle(corpus, req)
    except KeyboardInterrupt:
        raise
    except BaseException as e:  # noqa: BLE001 — keep serving, fail-safe
        resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        wh._log(f"DAEMON ERROR op={req.get('op')}: {resp['error']}")
        return resp


# ── server loop ──────────────────────────────────────────────────────────────

class RequestTooLarge(OSError):
    """A request line past the read cap with no newline — truncated mid-JSON
    (Audit 2026-07-12 W4). Distinct so the server can answer with an explicit
    error instead of parsing the truncation to `{}` (which used to silently
    skip an owed tool:pre veto)."""


def _recv_line(conn: socket.socket, limit: int = 64 * 1024 * 1024) -> bytes:
    buf = b""
    while b"\n" not in buf and len(buf) < limit:
        chunk = conn.recv(65536)
        if not chunk:
            break
        buf += chunk
    # Audit 2026-07-12 W4: hitting the cap without a newline means the payload
    # was cut mid-string — never hand truncated bytes to json.loads. (The cap
    # itself was raised 4 MB → 64 MB: a large Write/Edit tool_input must reach
    # the veto rules whole.)
    if b"\n" not in buf and len(buf) >= limit:
        raise RequestTooLarge(f"request exceeds {limit} bytes with no newline")
    return buf.split(b"\n", 1)[0]


def _serve_conn(corpus: Corpus, conn: socket.socket,
                stop_evt: threading.Event, in_flight) -> None:
    """One connection, on its own thread (T013): read one request, answer it,
    close. A shutdown request answers first, then signals the accept loop."""
    try:
        conn.settimeout(30.0)
        try:
            line = _recv_line(conn)
        except RequestTooLarge as e:
            # Audit 2026-07-12 W4: answer loudly (the Rust client logs a non-ok
            # response); fail-open — the caller skips the owed steers.
            wh._log(f"DAEMON ERROR request truncated: {e}")
            conn.sendall(json.dumps(
                {"ok": False, "error": f"request truncated: {e}"}).encode("utf-8") + b"\n")
            return
        try:
            req = json.loads(line) if line.strip() else {}
        except ValueError:
            req = {}
        resp = _safe_handle(corpus, req)
        conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
        if resp.get("_shutdown"):
            stop_evt.set()
    except OSError:
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass
        with in_flight["lock"]:
            in_flight["n"] -= 1


def serve(idle_exit: float) -> int:
    home = warden_home()
    home.mkdir(parents=True, exist_ok=True)
    sock_p = socket_path()
    # A stale socket file from a dead daemon blocks bind; probe before unlinking
    # so we never steal a live daemon's socket. Retry with backoff (F232 B6):
    # a BUSY daemon (serial loop mid-request with a full backlog) can miss one
    # 0.2 s probe — one failed connect is not proof of death.
    if sock_p.exists():
        alive = False
        for delay in (0.0, 0.5, 1.5):
            if delay:
                time.sleep(delay)
            try:
                probe = socket.socket(socket.AF_UNIX)
                probe.settimeout(1.0)
                probe.connect(str(sock_p))
                probe.close()
                alive = True
                break
            except OSError:
                continue
        if alive:
            return 0  # a live daemon already owns the socket — nothing to do
        sock_p.unlink(missing_ok=True)

    srv = socket.socket(socket.AF_UNIX)
    try:
        srv.bind(str(sock_p))
    except OSError:
        # Cold-start race (F232 B6): another daemon bound between our probe
        # and this bind. If it answers, yield cleanly; else surface the error.
        try:
            probe = socket.socket(socket.AF_UNIX)
            probe.settimeout(1.0)
            probe.connect(str(sock_p))
            probe.close()
            return 0
        except OSError:
            raise
    srv.listen(8)
    # Short accept timeout: the loop wakes ~1×/s to notice a shutdown request
    # (handled on a worker thread now) and to apply the idle-exit policy.
    srv.settimeout(1.0)

    # T013 thread-per-connection: workers are daemon threads (a hung rule body
    # can't pin the process past shutdown); idle-exit counts only quiet time
    # with nothing in flight.
    stop_evt = threading.Event()
    in_flight = {"n": 0, "lock": threading.Lock()}
    last = time.monotonic()
    # First sweep one full interval after start, not at start: a daemon that
    # compiles the moment it comes up would fire on every hook-triggered spawn.
    last_sweep = time.monotonic()
    # What the engine's code looked like when THIS process imported it. Taken
    # here rather than at module scope so it reflects the running interpreter,
    # not whenever the module happened to be first read.
    engine_loaded_ns = _engine_newest_ns()
    # Audit 2026-07-12 W3: the socket is bound (and about to be pid-stamped) before this
    # point — everything that can fail from here on (the pid-file write, the
    # corpus load, the accept loop) must run INSIDE this try so the `finally`
    # always unlinks `daemon.sock` / `daemon.pid`. A Corpus() failure (e.g. a
    # SyntaxError in the emitted rules module) used to escape BEFORE the try,
    # stranding a bound socket + pid file that every later hook would spawn a
    # daemon against — and crash against — again, stalling every hook call.
    try:
        pid_path().write_text(str(os.getpid()), encoding="utf-8")
        try:
            corpus = Corpus(home)
        except Exception as e:
            wh._log(f"DAEMON ERROR corpus load failed pid={os.getpid()}: "
                     f"{type(e).__name__}: {e}")
            raise
        # Audit 2026-07-12 W2: a repo move/rename leaves the compiled state
        # pointing at dead paths and the whole surface silently no-ops. Stay
        # up (fail-open — the ~/.warden artifacts still serve) but say so
        # loudly on every start.
        root = corpus.ir.get("root") or ""
        if root and not Path(root).is_dir():
            msg = (f"STALE — compiled IR root missing: {root} "
                   "(repo moved? run `warden install`)")
            wh._log(f"DAEMON {msg}")
            print(f"warden: {msg}", file=sys.stderr)
        wh._log(f"DAEMON up pid={os.getpid()} ({len(corpus.ir.get('rules', {}))} rules preloaded)")

        while not stop_evt.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                with in_flight["lock"]:
                    busy = in_flight["n"] > 0
                if busy:
                    last = time.monotonic()
                elif idle_exit > 0 and time.monotonic() - last > idle_exit:
                    wh._log("DAEMON idle-exit")
                    return 0
                # The compile sweep rides the loop that was already waking once
                # a second, so it costs one float compare per tick until the
                # interval is up. Only then does it stat the rulesets.
                scan_s = _sweep_config()["compile_scan_minutes"] * 60
                if scan_s > 0 and time.monotonic() - last_sweep >= scan_s:
                    last_sweep = time.monotonic()
                    note = compile_sweep(home)
                    if note:
                        wh._log(f"DAEMON {note}")
                        corpus.fresh()          # adopt what we just wrote
                    # Second staleness path, same tick: the engine's own code.
                    # `busy` is already false in this branch — exiting with a
                    # request in flight would drop it on the floor.
                    note = engine_stale(engine_loaded_ns)
                    if note:
                        wh._log(f"DAEMON {note}")
                        return 0
                continue
            last = time.monotonic()
            with in_flight["lock"]:
                in_flight["n"] += 1
            threading.Thread(
                target=_serve_conn, args=(corpus, conn, stop_evt, in_flight),
                daemon=True).start()
        return 0
    finally:
        sock_p.unlink(missing_ok=True)
        pid_path().unlink(missing_ok=True)


# ── client (also used by tests + the `warden` CLI) ──────────────────────────

def request(req: dict, timeout: float = 10.0) -> dict:
    """Send one request to the running daemon; raises OSError if unreachable."""
    conn = socket.socket(socket.AF_UNIX)
    conn.settimeout(timeout)
    conn.connect(str(socket_path()))
    try:
        conn.sendall(json.dumps(req).encode("utf-8") + b"\n")
        resp = _recv_line(conn)
        return json.loads(resp) if resp.strip() else {"ok": False, "error": "empty response"}
    finally:
        conn.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="warden-daemon",
        description="Warden resident interpreter — warm body_py/guard_py execution over IPC.")
    ap.add_argument("--serve", action="store_true", help="run the server loop")
    ap.add_argument("--idle-exit", type=float, default=1800.0,
                    help="exit after this many idle seconds (0 = never; default 1800)")
    args = ap.parse_args(argv)
    if not args.serve:
        ap.error("nothing to do — pass --serve")
    return serve(args.idle_exit)


if __name__ == "__main__":
    sys.exit(main())
