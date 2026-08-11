#!/usr/bin/env python3
"""Two staleness paths, two mechanisms — and the debounce both of them share.

Why this exists (F319, 2026-08-10). A ruleset can be authored, be live on every
markdown write, and still be invisible where it was meant to fire — because the
doc-fire path flattens rulesets from SOURCE, while the **moment** rules
(`tool:pre` deny) and `warden mend <rule-id>` read only the compiled IR. Nothing
closed that gap but remembering to type `warden compile`, and R-spine-04..08 sat
dead for a day because nobody did.

That is the *compile* path (`compile_sweep`). The *code* path is a separate
failure with the same shape: the daemon imports the engine once and holds it for
its whole life, and idle-exit only collects engine edits after 30 quiet minutes
— which never arrive while someone is working, i.e. exactly when engine edits
are made. `engine_stale` closes that one by exiting so the hook respawns fresh.

The debounce is the half worth testing on both. Acting the instant a file
changes would fire once per save while someone is editing; both sweeps only act
once the newest edit has been still for `compile_quiet_minutes`. Both branches
are asserted for both paths, because a debounce that never releases and a
debounce that never holds look identical from the outside on any single run.

Run: pytest test_warden_compile_sweep.py    (or python3 -m pytest)
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_daemon as wd     # noqa: E402

HOME = Path(os.environ.get("WARDEN_HOME", str(Path.home() / ".warden")))
IR = HOME / "rules-ir.json"

needs_ir = pytest.mark.skipif(
    not IR.is_file(), reason="no compiled IR — run `warden compile` first")


def set_mtime(p: Path, secs_ago: float) -> None:
    t = time.time() - secs_ago
    os.utime(p, (t, t))


@pytest.fixture
def quiet_s() -> float:
    return wd._sweep_config()["compile_quiet_minutes"] * 60


@pytest.fixture
def newest_is():
    """Drive the sweep's view of the newest ruleset directly.

    The first version of this file moved ONE ruleset's mtime and let the real
    `_rulesets_newest_ns` run — which takes the max over ~117 files. It passed
    until someone edited a different ruleset minutes before the run, and then
    the dirty-and-quiet case failed for a reason that had nothing to do with the
    sweep. A debounce test whose result depends on when the corpus was last
    touched is not testing the debounce.
    """
    real = wd._rulesets_newest_ns

    def drive(secs_ago: float):
        wd._rulesets_newest_ns = lambda: time.time_ns() - int(secs_ago * 1e9)

    yield drive
    wd._rulesets_newest_ns = real


@pytest.fixture
def ir_mtime():
    """Restore the IR's timestamps unless the test legitimately recompiled it."""
    orig = (IR.stat().st_atime, IR.stat().st_mtime) if IR.is_file() else None
    yield
    if orig and IR.is_file() and IR.stat().st_mtime < time.time() - 120:
        os.utime(IR, orig)


@pytest.fixture
def engine_is():
    real = wd._engine_newest_ns

    def drive(secs_ago: float):
        wd._engine_newest_ns = lambda: time.time_ns() - int(secs_ago * 1e9)

    yield drive
    wd._engine_newest_ns = real


# ── the compile sweep ────────────────────────────────────────────────────────

def test_both_knobs_are_configurable_and_defaulted():
    cfg = wd._sweep_config()
    assert cfg["compile_scan_minutes"] > 0
    assert cfg["compile_quiet_minutes"] > 0


@needs_ir
def test_clean_corpus_is_silent(newest_is, ir_mtime):
    """A sweep that narrates every quiet tick is a sweep people turn off."""
    newest_is(3600)
    set_mtime(IR, 0)
    assert wd.compile_sweep(HOME) is None


@needs_ir
def test_dirty_but_still_being_edited_holds(newest_is, ir_mtime, quiet_s):
    newest_is(quiet_s / 4)
    set_mtime(IR, 3600)
    assert wd.compile_sweep(HOME) is None
    assert IR.stat().st_mtime < time.time() - 1000     # left untouched


@needs_ir
def test_dirty_and_quiet_recompiles_once(newest_is, ir_mtime, quiet_s):
    set_mtime(IR, 3600)
    newest_is(quiet_s * 2)
    note = wd.compile_sweep(HOME)
    assert note is not None
    assert "recompiled" in note and "ahead of the compiled IR" in note
    assert IR.stat().st_mtime > time.time() - 60
    # and it does not then recompile in a loop
    assert wd.compile_sweep(HOME) is None


@needs_ir
def test_scan_minutes_zero_disables_the_sweep(newest_is, ir_mtime, quiet_s):
    real = wd._sweep_config
    wd._sweep_config = lambda: {"compile_scan_minutes": 0.0,
                                "compile_quiet_minutes": 2.0}
    try:
        set_mtime(IR, 3600)
        newest_is(quiet_s * 2)
        assert wd.compile_sweep(HOME) is None
    finally:
        wd._sweep_config = real


def test_real_ruleset_scan_works_on_the_live_corpus():
    """The fixtures above prove the debounce; this proves the thing they stub."""
    n = wd._rulesets_newest_ns()
    assert 0 < n <= time.time_ns()


def test_compile_sweep_fails_open():
    """It runs on the accept loop — anything it raised would take the whole
    hook surface down with it."""
    real = wd._rulesets_newest_ns
    wd._rulesets_newest_ns = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        wd.compile_sweep(HOME)          # must not raise
    finally:
        wd._rulesets_newest_ns = real


# ── the engine's own code ────────────────────────────────────────────────────

def test_unchanged_engine_does_not_bounce_the_daemon(engine_is):
    engine_is(3600)
    assert wd.engine_stale(time.time_ns()) is None


def test_engine_saved_seconds_ago_holds(engine_is, quiet_s):
    """Same debounce, and load-bearing for a second reason here: restarting into
    a half-written `.py` would fail to boot, and the hook would respawn into the
    same broken file every time."""
    engine_is(quiet_s / 4)
    assert wd.engine_stale(time.time_ns() - int(10 * quiet_s * 1e9)) is None


def test_settled_engine_edit_asks_for_the_exit(engine_is, quiet_s):
    engine_is(quiet_s * 2)
    note = wd.engine_stale(time.time_ns() - int(10 * quiet_s * 1e9))
    assert note is not None
    assert "engine code changed" in note and "respawn" in note


def test_engine_check_never_bounces_on_its_own_bug(engine_is):   # fixture restores
    """A non-None return is what EXITS the daemon, so the error path must
    answer None — loud in the log, but never fatal."""
    wd._engine_newest_ns = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    assert wd.engine_stale(0) is None


def test_engine_scan_reads_the_daemons_own_module():
    base = wd._engine_newest_ns()
    assert 0 < base <= time.time_ns()
    assert base >= Path(str(wd.__file__)).stat().st_mtime_ns


@pytest.mark.parametrize("name", ["test_warden_compile_sweep.py", "conftest.py"])
def test_test_files_are_excluded_from_the_engine_scan(name):
    """The daemon never imports these. If they counted, every run of this very
    suite would restart the live daemon."""
    p = HERE / name
    if not p.is_file():
        pytest.skip(f"{name} not present")
    base = wd._engine_newest_ns()
    keep = (p.stat().st_atime, p.stat().st_mtime)
    try:
        os.utime(p, None)                     # touch to now
        assert wd._engine_newest_ns() == base
    finally:
        os.utime(p, keep)
