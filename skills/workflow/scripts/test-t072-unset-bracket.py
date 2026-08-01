#!/usr/bin/env python3
"""test-t072-unset-bracket.py — T072: an unset `[ ]` row survives the guards.

`[ ]` is a legal bracket (DAS Backlog § Status brackets — the "candidate for
promotion" state), and its status string is a single space. That string is
truthy, so guards written as `if not status: return` fell through and then did
`status.split()[0]`, which raises IndexError on whitespace and took the whole
edit down. Found on the HBR reference anchor: `state … T002 set` on a `[ ]` row
crashed in verify_no_implementation_in_verify.

Pins the invariant at all three sites that split the status into tokens:
guards must SKIP a token-less status, and must still fire on real ones.

Self-contained: imports backlog-edit.py in-process, touches no vault file."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0


def ok(m):
    globals().__setitem__("PASS", PASS + 1)
    print(f"  PASS: {m}")


def no(m):
    globals().__setitem__("FAIL", FAIL + 1)
    print(f"  FAIL: {m}")


# The bodies below deliberately carry the language each guard hunts for, so a
# guard that DOESN'T skip has something to trip on.
PENDING_WORK = "Phase 2 sweeps every remaining anchor; will migrate the rest later."

print("1. Token-less status (`[ ]`) skips every status-splitting guard")

for label, call in [
    ("verify_no_implementation_in_verify",
     lambda: be.verify_no_implementation_in_verify(" ", PENDING_WORK)),
    ("verify_completion_block",
     lambda: be.verify_completion_block(" ", "→ [[F001 — Something]]", " ")),
    ("warn_verify_watching_horizon",
     lambda: be.warn_verify_watching_horizon(" ", "Now")),
]:
    try:
        call()
        ok(f"{label} skips a whitespace status")
    except IndexError as e:
        no(f"{label} raised IndexError on a whitespace status: {e}")
    except be.BacklogEditError as e:
        no(f"{label} refused a whitespace status (should skip): {e}")

print("2. The guards still fire on a real status")

try:
    be.verify_no_implementation_in_verify("Verify", PENDING_WORK)
    no("verify_no_implementation_in_verify let pending-work language through [Verify]")
except be.BacklogEditError:
    ok("verify_no_implementation_in_verify still refuses [Verify] + pending work")
except IndexError as e:
    no(f"verify_no_implementation_in_verify raised IndexError: {e}")

try:
    be.verify_no_implementation_in_verify("Ready", PENDING_WORK)
    ok("verify_no_implementation_in_verify ignores non-Verify statuses")
except Exception as e:
    no(f"verify_no_implementation_in_verify fired outside Verify: {e}")

# An empty string is the other token-less shape — the pre-existing guard
# covered it, and the fix must not regress it.
print("3. Empty and None statuses stay skipped")

for label, status in [("empty string", ""), ("None", None)]:
    try:
        be.verify_no_implementation_in_verify(status, PENDING_WORK)
        be.verify_completion_block(status, "body", None)
        be.warn_verify_watching_horizon(status, "Now")
        ok(f"{label} status skips cleanly")
    except Exception as e:
        no(f"{label} status raised {type(e).__name__}: {e}")

print(f"\ntest-t072-unset-bracket: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
