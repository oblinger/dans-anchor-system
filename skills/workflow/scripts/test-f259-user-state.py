#!/usr/bin/env python3
"""test-f259-user-state.py — F259: the [User] workflow state (the F240 sibling
for a user ACTION). A row entering [User] needs a `- **User:**` action AND a
--why-user-action justification; a well-formed [User] row is a groomed,
honestly-parked state (a crank stops cleanly on it); its count folds into the
Questions banner bucket, count-only.

Layers:
  1. user_action_gate + _status_needs_user (backlog-edit.py) — the pure gate.
  2. _delegate_row_edit / perform_edit end-to-end on a temp backlog — [User]
     set refuses without --user / --why-user-action, succeeds with both, and
     the `- **User:**` sub-bullet + annotation land on disk.
  3. _triage_gate_findings (state) — a well-formed [User] row is NOT a worklist
     finding (crank may stop); a [User] row missing `- **User:**` IS.

Self-contained: imports the modules in-process; the post-write refresh_q_md /
stamp side effects are stubbed so no real vault / audit-q is touched. Touches
only a tmp backlog file."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
be = st.be  # one class identity so `except be.BacklogEditError` matches

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

# ---- 1. the pure gate -------------------------------------------------------
print("== 1. user_action_gate + _status_needs_user ==")

ok("User is a valid status") if "User" in be.VALID_STATUS_BASE else no("User missing from VALID_STATUS_BASE")
ok("validate_status accepts [User]") if (be.validate_status("User") is None) else no("validate_status rejected User")
ok("_status_needs_user(User)") if be._status_needs_user("User") else no("_status_needs_user false")
ok("_status_needs_user(Ready) false") if not be._status_needs_user("Ready") else no("_status_needs_user(Ready) true")

try:
    be.user_action_gate("User", "F9", "Log into Hoare", None)
    no("missing --why-user-action should refuse")
except be.BacklogEditError as ex:
    ok("refuses missing --why-user-action") if "why-user-action" in str(ex) else no(f"wrong msg: {ex}")

out = be.user_action_gate("User", "F9", "Log into Hoare", "only you hold the Hoare login")
ok("annotates with why-user-action") if "*why-user-action: only you hold" in out else no(f"no annotation: {out}")

out2 = be.user_action_gate("User", "F9", "x · *why-user-action: prior*", None)
ok("grandfathered re-touch") if out2 == "x · *why-user-action: prior*" else no(f"re-touch mutated: {out2}")

# ---- 2. perform_edit end-to-end on a temp backlog ---------------------------
print("== 2. state set --status User: guard + gate + sub-bullet on disk ==")

# Stub the post-write side effects (refresh_q_md / stamp / selffire).
st.be.refresh_q_md = lambda *a, **k: None
st.be.restamp_backlog = lambda lines: lines
st.be.heal_backlog_if_stale = lambda *a, **k: None
st.be._selffire = lambda *a, **k: None
st.be.append_messages = lambda *a, **k: None
st.be.write_state = lambda *a, **k: None

BACKLOG = ("# ZZR Backlog\n\n## Now\n\n"
           "- **F1 — Needs your login** [Designing] — seeded ^F1\n\n## Done\n")


def fresh_backlog():
    d = Path(tempfile.mkdtemp())
    f = d / "ZZR Backlog.md"
    f.write_text(BACKLOG, encoding="utf-8")
    return f


def run_set(backlog, **over):
    """Drive perform_edit directly against a temp backlog (skips find_backlog)."""
    kw = dict(verify_text=None, next_text=None, pending_subs=None,
              why_user=None, user_text=None, why_user_action=None)
    kw.update(over)
    return be.perform_edit(backlog, "same", "F1", "User", "", "",
                           False, False, **kw)


# [User] with no --user action → refused, nothing written.
f = fresh_backlog()
before = f.read_text()
try:
    run_set(f, why_user_action="only you hold the login")
    no("[User] without --user should refuse")
except be.BacklogEditError as ex:
    good = "User:" in str(ex) and f.read_text() == before
    ok("[User] without a `- **User:**` action refused, file unchanged") if good \
        else no(f"refused but wrote, or wrong msg: {ex}")

# [User] with --user but no --why-user-action → refused.
f = fresh_backlog()
try:
    run_set(f, user_text="Log into Hoare so the token refreshes")
    no("[User] without --why-user-action should refuse")
except be.BacklogEditError as ex:
    ok("[User] without --why-user-action refused") if "why-user-action" in str(ex) \
        else no(f"wrong msg: {ex}")

# [User] with both → written; sub-bullet + annotation on disk.
f = fresh_backlog()
try:
    run_set(f, user_text="Log into Hoare at https://hoare.example",
            why_user_action="the Hoare session cookie is yours alone")
    txt = f.read_text()
    good = ("- **User:** Log into Hoare at https://hoare.example" in txt
            and "*why-user-action: the Hoare session cookie is yours alone*" in txt
            and "[User]" in txt)
    ok("[User] with --user + --why-user-action writes the action + annotation") if good \
        else no(f"missing sub-bullet/annotation:\n{txt}")
except be.BacklogEditError as ex:
    no(f"[User] with both wrongly refused: {ex}")

# Optional queued Next rides on a [User] row.
f = fresh_backlog()
run_set(f, user_text="Approve the OAuth consent screen",
        why_user_action="only you can click the Google consent dialog",
        next_text="Re-run the sync and confirm the token propagated")
txt = f.read_text()
ok("[User] row carries an optional queued `- **Next:**`") \
    if ("- **Next:** Re-run the sync" in txt and "- **User:** Approve" in txt) \
    else no(f"queued Next missing:\n{txt}")

# ---- 3. _triage_gate_findings — groomed vs finding ---------------------------
print("== 3. _triage_gate_findings: well-formed [User] groomed; bare [User] flagged ==")

# The well-formed [User] row from above → no finding (crank may stop on it).
findings = st._triage_gate_findings(f)
user_findings = [x for x in findings if "F1" in x]
ok("well-formed [User] row is not a worklist finding") if not user_findings \
    else no(f"unexpected finding: {user_findings}")

# A [User] row with no `- **User:**` (hand-authored) → a finding.
bare = fresh_backlog()
bare.write_text("# ZZR Backlog\n\n## Now\n\n"
                "- **F2 — Bare user row** [User] — seeded ^F2\n\n## Done\n",
                encoding="utf-8")
findings = st._triage_gate_findings(bare)
ok("bare [User] row (no action) is a finding") \
    if any("F2" in x and "User" in x for x in findings) \
    else no(f"expected a finding for bare [User]: {findings}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
