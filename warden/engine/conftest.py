"""Shared pytest fixtures for the Warden engine tests.

Restored 2026-08-01 (Tink T094). Thirty-three of the engine's seventy-four tests
request a fixture named `tmp` and had been erroring at setup — never running —
since the T008 extraction moved the engine into its own repo and left whatever
defined `tmp` behind. The gap was invisible in the usual way: an ERROR at setup
reads like infrastructure noise, not like coverage loss, on the one component
holding a DENY veto over every file write in the vault.
"""
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _warden_home_isolation():
    """Restore `$WARDEN_HOME` after every test, whatever the test did to it.

    Roughly twenty call sites point `WARDEN_HOME` at a scratch compiled corpus;
    most restore it, three in `test_warden_daemon.py` never did. Because pytest
    runs modules alphabetically, `daemon` left the variable aimed at a corpus
    with no `svg-jiggle` and `docfire`'s T106 regression pin then failed —
    reporting a product regression that did not exist, and only in the full run.

    A per-test fixture is the fix rather than "remember to restore it": there is
    no way for a new call site to forget, and a test that leaks is contained to
    itself. The doc-fire IR caches are cleared alongside it, since they are keyed
    off that same home and would otherwise outlive the variable they describe.
    """
    saved = os.environ.get("WARDEN_HOME")
    yield
    if saved is None:
        os.environ.pop("WARDEN_HOME", None)
    else:
        os.environ["WARDEN_HOME"] = saved
    try:
        import warden_docfire as wdf
        wdf._IR_CACHE.clear()
        wdf._AUDIT_IR_CACHE.clear()
    except Exception:                      # module not imported by this test
        pass


@pytest.fixture
def tmp(tmp_path: Path) -> Path:
    """A fresh, empty, writable directory for one test.

    Every call site treats it as scratch space it owns outright — writing
    transcripts, corpora and registries straight into it and reading them back —
    so per-test isolation is the whole contract. `tmp_path` supplies exactly
    that; `tmp` is the name the tests were written against.
    """
    return tmp_path
