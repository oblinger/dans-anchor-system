#!/usr/bin/env python3
"""test-f258-stopgate-auditq.py — F258: the crank stop-gate worklist counts
audit-q backlog findings too, so a crank cannot cleanly stop while any audit-q
warning remains (matching what `state triage` already requires).

Covers the two pieces that carry the logic:
  1. `_audit_q_backlog_findings` — parses `audit-q: N finding(s)`; returns None
     (caller's fail-open/closed choice) on unparseable output or a subprocess
     error.
  2. `cmd_groom_list --count` — prints `len(_triage_gate_findings) + aq`, and
     fails OPEN (aq None → 0) so an audit-q infra failure never permanently
     blocks a stop.

Self-contained: imports the `state` module in-process, stubs the audit-q
subprocess + helpers so the real vault / audit-q is never touched."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import sys
from pathlib import Path

STATE = Path(__file__).parent / "state"
loader = importlib.machinery.SourceFileLoader("state_mod", str(STATE))
spec = importlib.util.spec_from_loader("state_mod", loader)
st = importlib.util.module_from_spec(spec)
sys.modules["state_mod"] = st
loader.exec_module(st)

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


class FakeProc:
    def __init__(self, stdout="", stderr="", rc=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, rc


_real_run = st.subprocess.run

# ---- 1. _audit_q_backlog_findings parse + polarity --------------------------
print("== 1. _audit_q_backlog_findings parses the count; None on failure ==")

st.subprocess.run = lambda *a, **k: FakeProc(stdout="audit-q: 4 findings (2 errors, 2 warnings)\n")
n, _out = st._audit_q_backlog_findings("SKA")
ok("parses '4 findings' → 4") if n == 4 else no(f"got {n!r}, want 4")

st.subprocess.run = lambda *a, **k: FakeProc(stdout="audit-q: 0 findings (0 errors, 0 warnings)\n")
n, _out = st._audit_q_backlog_findings("SKA")
ok("parses '0 findings' → 0") if n == 0 else no(f"got {n!r}, want 0")

st.subprocess.run = lambda *a, **k: FakeProc(stdout="garbage with no count line\n")
n, _out = st._audit_q_backlog_findings("SKA")
ok("unparseable output → None (caller decides polarity)") if n is None else no(f"got {n!r}, want None")

def _boom(*a, **k):
    raise OSError("simulated audit-q failure")
st.subprocess.run = _boom
n, _out = st._audit_q_backlog_findings("SKA")
ok("subprocess error → None") if n is None else no(f"got {n!r}, want None")

st.subprocess.run = _real_run

# ---- 2. cmd_groom_list --count = light + audit-q (fail-open) ----------------
print("== 2. cmd_groom_list --count adds the audit-q count; fails open ==")

st._triage_gate_findings = lambda bp: ["row1: no Next", "row2: bracket/H2"]  # 2 light
st.be.find_backlog = lambda slug: Path("/fake/ZZR Backlog.md")


class Args:
    count = True


def _count_output():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        st.cmd_groom_list("ZZR", "/fake", Args())
    return buf.getvalue().strip()


st._audit_q_backlog_findings = lambda slug: (3, "out")
got = _count_output()
ok("2 light + 3 audit-q → 5") if got == "5" else no(f"got {got!r}, want 5")

st._audit_q_backlog_findings = lambda slug: (0, "out")
got = _count_output()
ok("2 light + 0 audit-q → 2") if got == "2" else no(f"got {got!r}, want 2")

# Fail-open: audit-q undeterminable (None) → counted as 0, never a spurious block.
st._audit_q_backlog_findings = lambda slug: (None, "")
got = _count_output()
ok("audit-q None (fail-open) → light count only (2)") if got == "2" else no(f"got {got!r}, want 2")

# All clear → worklist 0 (stop allowed).
st._triage_gate_findings = lambda bp: []
st._audit_q_backlog_findings = lambda slug: (0, "")
got = _count_output()
ok("no light + 0 audit-q → 0 (stop allowed)") if got == "0" else no(f"got {got!r}, want 0")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
