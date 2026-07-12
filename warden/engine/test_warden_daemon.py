#!/usr/bin/env python3
"""Tests for warden_daemon.py — the resident interpreter (F213 phase 2).

Covers the protocol ops (ping / fire_rules / audit / reload / shutdown), the
per-rule fire parity against the direct reference path (`warden_fire.fire`
with a single-rule bucket — the same construction the daemon uses, so this
pins the contract), and the fail-safe unknown-op response. Hermetic: a scratch
`WARDEN_HOME` holds the compiled corpus + the socket; the daemon is started
and shut down by the test. Runnable standalone.
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

_HOME = None
_PROC = None


def _env(home: Path) -> dict:
    return {**os.environ, "WARDEN_HOME": str(home)}


def _compiled_home() -> Path:
    global _HOME
    if _HOME is None:
        _HOME = Path(tempfile.mkdtemp(prefix="warden-daemon-test-")) / "home"
        out = subprocess.run([str(HERE / "warden"), "compile"],
                             capture_output=True, text=True, env=_env(_HOME))
        assert out.returncode == 0, out.stderr
        assert (_HOME / "rules-ir.json").is_file()
        assert (_HOME / "daemon.cmd").is_file(), "compile must write daemon.cmd"
    return _HOME


def _start_daemon(home: Path):
    global _PROC
    _PROC = subprocess.Popen(
        [sys.executable, str(HERE / "warden_daemon.py"), "--serve", "--idle-exit", "120"],
        env=_env(home), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        time.sleep(0.1)
        if (home / "daemon.sock").exists():
            return
    raise AssertionError("daemon did not come up")


def _request(home: Path, req: dict) -> dict:
    os.environ["WARDEN_HOME"] = str(home)
    import warden_daemon as wd
    return wd.request(req, timeout=15.0)


def _anchor(tmp: Path, traits: str) -> Path:
    a = tmp / "FX"
    a.mkdir(parents=True)
    (a / ".anchor").write_text(f"slug: FX\ntraits: [{traits}]\n", encoding="utf-8")
    return a


def test_ping():
    home = _compiled_home()
    resp = _request(home, {"op": "ping"})
    assert resp["ok"] and resp["pid"] == _PROC.pid, resp
    print("PASS  ping")


def test_fire_rules_parity():
    """The daemon's per-rule fire == the reference fire with the same
    single-rule bucket (identical ctx/traits sensing on both sides)."""
    home = _compiled_home()
    import warden_fire as wf
    with tempfile.TemporaryDirectory() as td:
        anchor = _anchor(Path(td), "warden-selftest, Commit")
        moment = "write:markdown"
        rids = ["R-warden-selftest-02"]
        resp = _request(home, {"op": "fire_rules", "moment": moment,
                               "anchor_root": str(anchor), "rule_ids": rids})
        assert resp["ok"], resp
        ir, module = wf.load_compiled(home, "all")
        ctx = wf.build_ctx(anchor, moment)
        traits = wf.read_anchor_traits(anchor)
        for rid in rids:
            one = dict(ir)
            one["moments"] = {moment: [rid]}
            ref = wf.fire(one, module, moment, ctx, traits)
            assert resp["steers_by_rule"][rid] == ref, (rid, resp["steers_by_rule"][rid], ref)
        assert resp["steers_by_rule"][rids[0]], "selftest rule should steer"
        # an unknown rule id returns an empty list, not an error
        resp2 = _request(home, {"op": "fire_rules", "moment": moment,
                                "anchor_root": str(anchor), "rule_ids": ["nope"]})
        assert resp2["ok"] and resp2["steers_by_rule"]["nope"] == [], resp2
        # F216: a session-carrying request is accepted (registry/ledger fed,
        # ctx.agent bound) and fires identically
        resp3 = _request(home, {"op": "fire_rules", "moment": moment,
                                "anchor_root": str(anchor), "rule_ids": rids,
                                "session": {"session_id": "sess-t",
                                            "transcript_path": str(Path(td) / "none.jsonl"),
                                            "cwd": str(anchor)}})
        assert resp3["ok"], resp3
        assert resp3["steers_by_rule"] == resp["steers_by_rule"], resp3
    print("PASS  fire_rules_parity")


def test_audit_parity():
    """The daemon's audit op == warden_hook.audit_on_write for the same file."""
    home = _compiled_home()
    import warden_hook as wh
    with tempfile.TemporaryDirectory() as td:
        anchor = _anchor(Path(td), "audit-on-write")
        bad = anchor / "FX Messages.md"
        bad.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")
        resp = _request(home, {"op": "audit", "file_path": str(bad)})
        assert resp["ok"], resp
        ref = wh.audit_on_write(bad)
        assert resp["steers"] == ref, (resp["steers"], ref)
        assert resp["steers"] and "R-messages-01" in resp["steers"][0], resp
    print("PASS  audit_parity")


def test_unknown_op_and_reload():
    home = _compiled_home()
    resp = _request(home, {"op": "bogus"})
    assert resp["ok"] is False and "unknown op" in resp["error"], resp
    assert _request(home, {"op": "reload"})["ok"]
    print("PASS  unknown_op_and_reload")


def test_systemexit_survival():
    """F232 B4: SystemExit from a handler degrades to a failed request — the
    daemon keeps serving (in-process check of `_safe_handle`, then a live
    probe that the running daemon still answers)."""
    home = _compiled_home()
    os.environ["WARDEN_HOME"] = str(home)
    import warden_daemon as wd
    orig = wd.handle
    try:
        def _boom(_corpus, _req):
            raise SystemExit(3)
        wd.handle = _boom
        resp = wd._safe_handle(None, {"op": "x"})
        assert resp["ok"] is False and "SystemExit" in resp["error"], resp
        # KeyboardInterrupt (operator Ctrl-C) still terminates.
        def _intr(_corpus, _req):
            raise KeyboardInterrupt
        wd.handle = _intr
        try:
            wd._safe_handle(None, {"op": "x"})
            raise AssertionError("KeyboardInterrupt was swallowed")
        except KeyboardInterrupt:
            pass
    finally:
        wd.handle = orig
    assert _request(home, {"op": "ping"})["ok"], "live daemon stopped answering"
    print("PASS  systemexit_survival (F232 B4)")


def test_shutdown():
    home = _compiled_home()
    resp = _request(home, {"op": "shutdown"})
    assert resp["ok"], resp
    _PROC.wait(timeout=10)
    assert not (home / "daemon.sock").exists(), "socket not cleaned up"
    print("PASS  shutdown")


def test_corpus_load_failure_no_stray_socket():
    """Audit 2026-07-12 W3: a `Corpus()` load failure (a corrupted compiled rules module)
    must not strand `daemon.sock` / `daemon.pid` — before the fix, every LATER
    daemon spawn against that home crashed the same way against the same
    stale socket, stalling ~2s per hook call forever."""
    home = Path(tempfile.mkdtemp(prefix="warden-daemon-badcorpus-")) / "home"
    home.mkdir(parents=True)
    (home / "rules-ir.json").write_text("{}", encoding="utf-8")
    (home / "rules_all.py").write_text("def broken(:\n", encoding="utf-8")  # SyntaxError
    proc = subprocess.Popen(
        [sys.executable, str(HERE / "warden_daemon.py"), "--serve", "--idle-exit", "5"],
        env=_env(home), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        rc = proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
        raise AssertionError("daemon did not exit after a corpus load failure")
    out = proc.stdout.read() if proc.stdout else ""
    assert rc != 0, f"daemon exited 0 despite a corpus load failure; output:\n{out}"
    log_path = home / "hook.log"  # wh._log's operational log, not stdout
    log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    assert "DAEMON ERROR corpus load failed" in log, \
        f"corpus load failure was not logged; hook.log:\n{log}\nstdout/stderr:\n{out}"
    assert not (home / "daemon.sock").exists(), "stray daemon.sock left behind"
    assert not (home / "daemon.pid").exists(), "stray daemon.pid left behind"
    print("PASS  corpus_load_failure_no_stray_socket (Audit 2026-07-12 W3)")


def test_concurrent_slow_request():
    """T013 (F232 B1): the daemon is thread-per-connection — one slow request
    (a 60 s oracle body, a long audit) must not block another session's hooks.
    In-process serve on the now-free home; a patched slow op holds one
    connection while a ping answers underneath it."""
    import threading
    home = _compiled_home()
    os.environ["WARDEN_HOME"] = str(home)
    import warden_daemon as wd
    orig = wd.handle

    def _slow_or_orig(corpus, req):
        if req.get("op") == "slow":
            time.sleep(2.0)
            return {"ok": True, "slow": True}
        return orig(corpus, req)

    wd.handle = _slow_or_orig
    srv = threading.Thread(target=wd.serve, args=(30.0,), daemon=True)
    srv.start()
    try:
        for _ in range(50):
            time.sleep(0.1)
            if (home / "daemon.sock").exists():
                break
        else:
            raise AssertionError("in-process daemon did not come up")
        results: dict = {}

        def _slow_call():
            results["slow"] = wd.request({"op": "slow"}, timeout=15.0)

        st = threading.Thread(target=_slow_call)
        st.start()
        time.sleep(0.3)  # the slow request is now in flight
        t0 = time.monotonic()
        ping = wd.request({"op": "ping"}, timeout=5.0)
        dt = time.monotonic() - t0
        assert ping["ok"], ping
        assert dt < 1.0, f"ping took {dt:.2f}s behind a slow request — daemon still serial"
        st.join(timeout=10)
        assert results.get("slow", {}).get("ok"), results
    finally:
        wd.handle = orig
        try:
            wd.request({"op": "shutdown"}, timeout=5.0)
        except OSError:
            pass
        srv.join(timeout=10)
    assert not srv.is_alive(), "in-process daemon did not stop on shutdown"
    print("PASS  concurrent_slow_request (T013 / F232 B1)")


def main():
    home = _compiled_home()
    _start_daemon(home)
    try:
        test_ping()
        test_fire_rules_parity()
        test_audit_parity()
        test_unknown_op_and_reload()
        test_systemexit_survival()
        test_shutdown()
        test_concurrent_slow_request()
        test_corpus_load_failure_no_stray_socket()
    finally:
        if _PROC and _PROC.poll() is None:
            _PROC.kill()
    print("\nall warden_daemon tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
