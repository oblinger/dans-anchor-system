#!/usr/bin/env python3
"""Tests for warden_hook.py — the live hook dispatcher (F220).

Covers the event→moment mapping, the kill switch (checked before any work), the
dispatch→fire→log path (the selftest rule writes its marker), and active-set
gating (an anchor without the funky trait fires nothing). Hermetic: a scratch
`WARDEN_HOME` holds both the compiled corpus and the selftest log, so nothing
touches the real `~/.warden`. Runnable standalone.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
from warden_root import corpus_root
REPO = corpus_root()
sys.path.insert(0, str(HERE))

import warden_hook as wh  # noqa: E402

_HOME = None  # a compiled scratch WARDEN_HOME shared across the dispatch tests


def _compiled_home() -> Path:
    """Compile the corpus once into a scratch home; reuse for the process."""
    global _HOME
    if _HOME is None:
        _HOME = Path(tempfile.mkdtemp(prefix="warden-hook-test-")) / "home"
        env = {**os.environ, "WARDEN_HOME": str(_HOME)}
        out = subprocess.run([str(HERE / "warden"), "compile"],
                             capture_output=True, text=True, env=env)
        assert out.returncode == 0, out.stderr
        assert (_HOME / "rules-ir.json").is_file(), "compile produced no IR"
    return _HOME


def _anchor(tmp: Path, traits: str) -> Path:
    a = tmp / "FX"
    a.mkdir(parents=True)
    (a / ".anchor").write_text(f"slug: FX\ntraits: [{traits}]\n", encoding="utf-8")
    return a


def test_event_to_moments():
    e = wh.event_to_moments
    assert e({"hook_event_name": "PostToolUse", "tool_name": "Write",
              "tool_input": {"file_path": "x.md"}}) == ["tool:post:Write", "write:markdown"]
    assert e({"hook_event_name": "PostToolUse", "tool_name": "Bash"}) == ["tool:post:Bash"]
    assert e({"hook_event_name": "PreToolUse", "tool_name": "Bash"}) == ["tool:pre:Bash"]
    assert e({"hook_event_name": "PreToolUse", "tool_name": "Skill",
              "tool_input": {"skill": "audit-q"}}) == ["skill:pre:audit-q"]
    assert e({"hook_event_name": "UserPromptSubmit"}) == ["prompt:submit"]
    assert e({"hook_event_name": "SessionStart"}) == ["session:start"]
    assert e({"hook_event_name": "PreCompact"}) == ["session:compact"]
    assert e({"hook_event_name": "Nonsense"}) == []
    print("PASS  event_to_moments")


def test_kill_switch():
    with tempfile.TemporaryDirectory() as td:
        os.environ.pop("WARDEN_DISABLED", None)
        old = os.environ.get("WARDEN_HOME")
        os.environ["WARDEN_HOME"] = td
        try:
            assert wh.disabled() is False, "enabled by default"
            (Path(td) / "DISABLED").write_text("x", encoding="utf-8")
            assert wh.disabled() is True, "sentinel file disables"
            (Path(td) / "DISABLED").unlink()
            assert wh.disabled() is False
            os.environ["WARDEN_DISABLED"] = "1"
            assert wh.disabled() is True, "env var disables"
            os.environ.pop("WARDEN_DISABLED")
        finally:
            if old is None:
                os.environ.pop("WARDEN_HOME", None)
            else:
                os.environ["WARDEN_HOME"] = old
    print("PASS  kill_switch")


def _read_markers(home: Path) -> list[dict]:
    fp = home / "selftest.log"
    if not fp.is_file():
        return []
    return [json.loads(ln) for ln in fp.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_dispatch_fires_and_logs():
    home = _compiled_home()
    (home / "selftest.log").unlink(missing_ok=True)
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "warden-selftest, Commit")
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(anchor / "note.md")}, "cwd": str(anchor)}
            steers = wh.dispatch(event)
            # a markdown Write fires BOTH tool:post:Write and write:markdown
            assert len(steers) == 2, steers
            markers = _read_markers(home)
            rules = {m["rule"] for m in markers}
            assert rules == {"R-warden-selftest-01", "R-warden-selftest-02"}, markers
            assert all(m["anchor"] == "FX" for m in markers), markers
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  dispatch_fires_and_logs")


def test_trait_gating():
    home = _compiled_home()
    (home / "selftest.log").unlink(missing_ok=True)
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")  # no warden-selftest trait
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(anchor / "note.md")}, "cwd": str(anchor)}
            assert wh.dispatch(event) == [], "fired without the funky trait"
            assert _read_markers(home) == [], "logged without the funky trait"
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  trait_gating")


def test_audit_on_write():
    """F222 + F229 A′: the doc-fire audits a written markdown file governed by
    the FILE's anchor — `audit-on-write` rides `anchor-base` (ir.base_traits),
    so EVERY anchored file is audited regardless of declared traits; an
    un-anchored file is not (no anchor, no audit). The file's anchor governs
    even when the session's cwd sits elsewhere."""
    home = _compiled_home()
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            # a Messages file with a prose H1 fails R-messages-01 ("no H1")
            anchor = _anchor(Path(td), "audit-on-write")
            bad = anchor / "FX Messages.md"
            bad.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(bad)}, "cwd": str(anchor)}
            steers = wh.dispatch(event)
            aow = [s for s in steers if s.startswith("[warden audit-on-write]")]
            assert len(aow) == 1, steers
            assert "R-messages-01" in aow[0], aow
            assert "FX Messages.md" in aow[0], aow

            # a clean file → no audit-on-write steer
            good = anchor / "FX Messages.md"
            good.write_text("# FX Messages\n\nbody\n", encoding="utf-8")
            clean = wh.dispatch({**event, "tool_input": {"file_path": str(good)}})
            assert not [s for s in clean if s.startswith("[warden audit-on-write]")], clean

        # base-implied (F229 A′): an anchor WITHOUT the declared trait still
        # audits — audit-on-write rides anchor-base for every anchor.
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")  # no audit-on-write declared
            bad = anchor / "FX Messages.md"
            bad.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(bad)}, "cwd": str(anchor)}
            steers = wh.dispatch(event)
            aow = [s for s in steers if s.startswith("[warden audit-on-write]")]
            assert len(aow) == 1, steers

        # file-anchor governance: cwd un-anchored, file inside an anchor →
        # still audited (the file's anchor owns the file).
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")
            bad = anchor / "FX Messages.md"
            bad.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")
            outside = Path(td) / "elsewhere"
            outside.mkdir()
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(bad)}, "cwd": str(outside)}
            steers = wh.dispatch(event)
            aow = [s for s in steers if s.startswith("[warden audit-on-write]")]
            assert len(aow) == 1, steers

        # un-anchored file: no anchor anywhere up its tree → no audit.
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")
            loose_dir = Path(td) / "loose"       # sibling of FX/, outside it
            loose_dir.mkdir()
            loose = loose_dir / "note.md"
            loose.write_text("just prose, not an H1\n\nbody\n", encoding="utf-8")
            event = {"hook_event_name": "PostToolUse", "tool_name": "Write",
                     "tool_input": {"file_path": str(loose)}, "cwd": str(anchor)}
            steers = wh.dispatch(event)
            assert not [s for s in steers if s.startswith("[warden audit-on-write]")], steers
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  audit_on_write (F229 A′ — base-implied, file-anchored)")


def test_pathguard_veto():
    """F131: the veto path — R-pathguard denies the agent's Edit/Write on
    script-owned surfaces (backlog, queries, feature-doc Q regions, Atlas) in
    an anchor declaring `pathguard`, and stays inert without the trait."""
    home = _compiled_home()
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "pathguard")

            def pre(tool, **ti):
                return wh.dispatch({"hook_event_name": "PreToolUse", "tool_name": tool,
                                    "tool_input": ti, "cwd": str(anchor)})

            # 01 — backlog Edit denied with the state-task redirect
            denies = [s for s in pre("Edit", file_path=str(anchor / "FX Backlog.md"),
                                     old_string="a", new_string="b")
                      if s.startswith(wh.DENY_SENTINEL)]
            assert len(denies) == 1 and "state Backlog" in denies[0], denies
            # 01 — queries page Edit denied with the renderer redirect
            denies = [s for s in pre("Edit", file_path=str(anchor / "FX queries.md"),
                                     old_string="a", new_string="b")
                      if s.startswith(wh.DENY_SENTINEL)]
            assert len(denies) == 1 and "queries-render.py" in denies[0], denies
            # 02 — feature-doc edit INSIDE ## Open Questions denied...
            fdoc = anchor / "F001 — Fixture feature.md"
            fdoc.write_text("# F001 — Fixture feature\n\nbody\n\n## Open Questions\n\n"
                            "- **Q1 — pick one?** ^F001-Q1\n\n## Design\n\nprose\n",
                            encoding="utf-8")
            denies = [s for s in pre("Edit", file_path=str(fdoc),
                                     old_string="- **Q1 — pick one?** ^F001-Q1",
                                     new_string="- answered")
                      if s.startswith(wh.DENY_SENTINEL)]
            assert len(denies) == 1 and "state <doc>" in denies[0], denies
            # ...but an edit elsewhere in the same doc passes
            clean = pre("Edit", file_path=str(fdoc), old_string="prose", new_string="better prose")
            assert not [s for s in clean if s.startswith(wh.DENY_SENTINEL)], clean
            # 03 — wholesale Write of the backlog denied too (the bypass)
            denies = [s for s in pre("Write", file_path=str(anchor / "FX Backlog.md"),
                                     content="# rewritten")
                      if s.startswith(wh.DENY_SENTINEL)]
            assert len(denies) == 1 and "script-owned" in denies[0], denies
            # 04 — Atlas
            atlas = anchor / "Atlas" / "Atlas.md"
            denies = [s for s in pre("Edit", file_path=str(atlas), old_string="x", new_string="y")
                      if s.startswith(wh.DENY_SENTINEL)]
            assert len(denies) == 1 and "/atlas" in denies[0], denies
            # file-anchor governance (2026-07-06): the SAME guarded Edit from a
            # session cwd'd OUTSIDE the anchor is still denied — the file's
            # anchor owns the file; cwd must not side-step tool:pre guards.
            with tempfile.TemporaryDirectory() as elsewhere:
                denies = [s for s in wh.dispatch(
                    {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                     "tool_input": {"file_path": str(anchor / "FX Backlog.md"),
                                    "old_string": "a", "new_string": "b"},
                     "cwd": elsewhere})
                    if s.startswith(wh.DENY_SENTINEL)]
                assert len(denies) == 1 and "state Backlog" in denies[0], denies

        # trait OFF → the same event fires nothing
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")
            steers = wh.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                                  "tool_input": {"file_path": str(anchor / "FX Backlog.md"),
                                                 "old_string": "a", "new_string": "b"},
                                  "cwd": str(anchor)})
            assert not [s for s in steers if s.startswith(wh.DENY_SENTINEL)], steers
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  pathguard_veto (F131)")


def test_bridge_guard():
    """F183: one-shot SSH remote-control is denied at tool:pre:Bash with the
    bridge redirect (rides anchor-base — fires in ANY anchor); the no-match
    table passes untouched: bare attach, scp/rsync, in-bridge tmux, and
    ssh-as-argument."""
    home = _compiled_home()
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        with tempfile.TemporaryDirectory() as td:
            anchor = _anchor(Path(td), "Commit")  # no special trait — base-implied

            def bash(cmd):
                return wh.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                    "tool_input": {"command": cmd}, "cwd": str(anchor)})

            def denied(cmd):
                return [s for s in bash(cmd) if s.startswith(wh.DENY_SENTINEL)]

            # match — command-executing SSH, flags tolerated, chained too
            assert denied("ssh haorui.local 'make test'"), "plain one-shot not denied"
            assert denied("ssh -p 2222 -i ~/.ssh/k haorui.local ls /tmp"), "flagged form not denied"
            assert denied("cd /x && ssh haorui.local 'nohup ./run &'"), "chained form not denied"
            assert "bridge" in denied("ssh haorui.local w")[0], "redirect must name the bridge skill"
            # no match — the legitimate forms
            assert not denied("ssh haorui.local"), "bare interactive attach wrongly denied"
            assert not denied("scp build.tgz haorui.local:/tmp/"), "scp wrongly denied"
            assert not denied("rsync -e ssh -av x/ haorui.local:x/"), "rsync -e ssh wrongly denied"
            assert not denied("ssh haorui.local tmux send-keys -t bridge 'ls' Enter"), \
                "in-bridge tmux control wrongly denied"
            assert not denied("which ssh"), "ssh-as-argument wrongly denied"
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  bridge_guard (F183)")


def test_emit_deny_shape():
    """F131: emit() converts DENY steers to a PreToolUse permissionDecision;
    at any other event the sentinel degrades to plain context (fail-open)."""
    import contextlib
    import io

    def capture(event, steers):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            wh.emit(event, steers)
        out = buf.getvalue().strip()
        return json.loads(out)["hookSpecificOutput"] if out else None

    hso = capture("PreToolUse", ["DENY: use state q", "also beware"])
    assert hso["permissionDecision"] == "deny", hso
    assert hso["permissionDecisionReason"] == "use state q", hso
    assert hso["additionalContext"] == "also beware", hso
    # non-pre: deny degrades to a plain steer, no permission fields
    hso = capture("PostToolUse", ["DENY: too late to block"])
    assert "permissionDecision" not in hso, hso
    assert hso["additionalContext"] == "too late to block", hso
    # steer-less call emits nothing
    assert capture("PreToolUse", []) is None
    print("PASS  emit_deny_shape (F131)")


def test_stale_paths_surfaced():
    """Audit 2026-07-12 W2: compiled state whose absolute-path snapshots dangle
    (repo moved/renamed) is detected, logged, and steered at session:start —
    while dispatch stays fail-open (no exception, no block)."""
    # healthy compiled home → no stale findings
    home = _compiled_home()
    healthy = json.loads((home / "rules-ir.json").read_text(encoding="utf-8"))
    old = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = str(home)
    try:
        assert wh._stale_paths(healthy) == [], wh._stale_paths(healthy)
    finally:
        os.environ["WARDEN_HOME"] = old if old else str(home)
    # a moved-repo home: dead IR root + dead daemon.cmd target
    with tempfile.TemporaryDirectory() as td:
        stale_home = Path(td) / "home"
        stale_home.mkdir()
        (stale_home / "rules-ir.json").write_text(json.dumps(
            {"root": "/nonexistent/w2-moved", "rules": {}, "moments": {},
             "traits": {}}), encoding="utf-8")
        (stale_home / "daemon.cmd").write_text(
            "python3 '/nonexistent/w2 moved/warden_daemon.py' --serve\n",
            encoding="utf-8")
        os.environ["WARDEN_HOME"] = str(stale_home)
        try:
            anchor = _anchor(Path(td), "Commit")
            found = wh._stale_paths(json.loads(
                (stale_home / "rules-ir.json").read_text(encoding="utf-8")))
            assert len(found) == 2, found
            assert "compiled IR root missing: /nonexistent/w2-moved" in found[0], found
            assert "/nonexistent/w2 moved/warden_daemon.py" in found[1], found
            # session:start → a loud agent-visible steer, still fail-open
            steers = wh.dispatch({"hook_event_name": "SessionStart",
                                  "cwd": str(anchor)})
            assert len(steers) == 1 and steers[0].startswith(
                "[warden] STALE compiled state"), steers
            assert "run `warden install`" in steers[0], steers
            # other moments: logged but not steered (no per-call spam)
            assert wh.dispatch({"hook_event_name": "PostToolUse",
                                "tool_name": "Bash", "cwd": str(anchor)}) == []
            log = (stale_home / "hook.log").read_text(encoding="utf-8")
            assert "STALE" in log and "w2-moved" in log, log
        finally:
            os.environ["WARDEN_HOME"] = old if old else str(home)
    print("PASS  stale_paths_surfaced (Audit 2026-07-12 W2)")


def main():
    test_event_to_moments()
    test_kill_switch()
    test_dispatch_fires_and_logs()
    test_trait_gating()
    test_audit_on_write()
    test_pathguard_veto()
    test_bridge_guard()
    test_emit_deny_shape()
    test_stale_paths_surfaced()
    print("\nall warden_hook tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
