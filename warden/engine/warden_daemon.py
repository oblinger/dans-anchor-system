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
min) — the Rust hook respawns it on demand, so a stale process never lingers
and engine-code changes are picked up within one idle window.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
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
    change on disk (cheap mtime stat per request)."""

    def __init__(self, home: Path):
        self.home = home
        self.ir: dict = {}
        self.module = None
        self._stamp: tuple = ()
        self.reload()

    def _artifact_stamp(self) -> tuple:
        stamp = []
        for name in ("rules-ir.json", "rules_all.py"):
            p = self.home / name
            stamp.append(p.stat().st_mtime_ns if p.is_file() else 0)
        return tuple(stamp)

    def reload(self) -> None:
        self.ir, self.module = wf.load_compiled(self.home, "all")
        self._stamp = self._artifact_stamp()

    def fresh(self) -> None:
        if self._artifact_stamp() != self._stamp:
            self.reload()


# ── request handlers ─────────────────────────────────────────────────────────

# F217 wall 2: (rule_id, session_id, turn_key) triples already fired — bounded
# ring; membership checks are O(n) over ≤512 entries, well inside the budget.
from collections import deque  # noqa: E402

TURN_FIRED: deque = deque(maxlen=512)

def _fire_rules(corpus: Corpus, req: dict) -> dict:
    """Run the requested rules through the reference fire path, one rule per
    single-rule bucket so steers stay per-rule (the caller re-interleaves)."""
    moment = req["moment"]
    anchor_root = Path(req["anchor_root"])
    rule_ids = req.get("rule_ids", [])
    # F216: record the moment in the session registry/ledger and bind the
    # agent-state view. The ledger holds the moments this daemon sees (owed
    # round-trips); full history comes from the transcript tail, which the
    # classifier reads — so a sparse ledger degrades recency, not correctness.
    session = wa.session_of(req.get("session"))
    wa.observe(session, moment)
    agent = wa.AgentView(session, moment)
    ctx = wf.build_ctx(anchor_root, moment, agent=agent)
    traits = wf.read_anchor_traits(anchor_root)
    # F217 loop prevention (wall 2): a turn-bearing rule fires once per
    # (rule, session, turn) — a Stop-steer continuation extends the SAME turn
    # (no new prompt:submit), so the extended turn cannot re-trigger the rule
    # that steered it. A genuinely new turn resets the key.
    tkey = wa.turn_key(agent._records()) if session else None
    by_rule: dict[str, list[str]] = {}
    for rid in rule_ids:
        row = corpus.ir.get("rules", {}).get(rid)
        if row is None:
            by_rule[rid] = []
            continue
        dedup = None
        if row.get("turn_bearing") and session and tkey:
            dedup = (rid, session.get("session_id", ""), tkey)
            if dedup in TURN_FIRED:
                by_rule[rid] = []
                continue
        one = dict(corpus.ir)
        one["moments"] = {moment: [rid]}
        by_rule[rid] = wf.fire(one, corpus.module, moment, ctx, traits)
        if by_rule[rid] and dedup:
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


# ── server loop ──────────────────────────────────────────────────────────────

def _recv_line(conn: socket.socket, limit: int = 4 * 1024 * 1024) -> bytes:
    buf = b""
    while b"\n" not in buf and len(buf) < limit:
        chunk = conn.recv(65536)
        if not chunk:
            break
        buf += chunk
    return buf.split(b"\n", 1)[0]


def serve(idle_exit: float) -> int:
    home = warden_home()
    home.mkdir(parents=True, exist_ok=True)
    sock_p = socket_path()
    # A stale socket file from a dead daemon blocks bind; probe before unlinking
    # so we never steal a live daemon's socket.
    if sock_p.exists():
        try:
            probe = socket.socket(socket.AF_UNIX)
            probe.settimeout(0.2)
            probe.connect(str(sock_p))
            probe.close()
            return 0  # a live daemon already owns the socket — nothing to do
        except OSError:
            sock_p.unlink(missing_ok=True)

    srv = socket.socket(socket.AF_UNIX)
    srv.bind(str(sock_p))
    srv.listen(8)
    srv.settimeout(min(idle_exit, 60.0) if idle_exit > 0 else 60.0)
    pid_path().write_text(str(os.getpid()), encoding="utf-8")
    corpus = Corpus(home)
    wh._log(f"DAEMON up pid={os.getpid()} ({len(corpus.ir.get('rules', {}))} rules preloaded)")

    last = time.monotonic()
    try:
        while True:
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                if idle_exit > 0 and time.monotonic() - last > idle_exit:
                    wh._log("DAEMON idle-exit")
                    return 0
                continue
            last = time.monotonic()
            try:
                conn.settimeout(30.0)
                line = _recv_line(conn)
                try:
                    req = json.loads(line) if line.strip() else {}
                except ValueError:
                    req = {}
                try:
                    resp = handle(corpus, req)
                except Exception as e:  # noqa: BLE001 — keep serving, fail-safe
                    resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
                    wh._log(f"DAEMON ERROR op={req.get('op')}: {resp['error']}")
                conn.sendall(json.dumps(resp).encode("utf-8") + b"\n")
                if resp.get("_shutdown"):
                    return 0
            except OSError:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass
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
