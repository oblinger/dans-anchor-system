#!/usr/bin/env python3
"""test-t144-qfix-lifecycle.py — TINK T144: the B-QFix row's full lifecycle.

T144 was filed against `audit-q --fix` on the claim that it "mints B-QFix when
findings appear but never retires it when they clear." Measured 2026-08-06, that
diagnosis is wrong: `route_findings_to_qfix` seeds its per-anchor groups from
`anchor_backlogs` (not from the findings), so an anchor with zero residuals takes
the `clear_qfix_row` branch and the row is deleted. Confirmed against two live
anchors — PROS and ABIO each carried a `[Ready]` B-QFix row with zero findings,
and a single `--fix` pass cleared both.

The real gap is a TRIGGER gap, not a reconcile gap: nothing re-runs `--fix` when
findings are cleared by editing the offending docs, which is how most findings
get fixed. The row is reconciled only on the next `state` mutation of that anchor
(`backlog-edit.refresh_q_md`), so between those two moments the anchor's banner
reports Runnable work that no longer exists.

These tests pin the reconcile behavior so the wrong diagnosis cannot be re-filed,
and so a future trigger fix has a green baseline to build on:

  A. residual present            → row is created, carrying that residual
  B. residual persists, re-run   → row is updated in place, still a singleton
  C. residual cleared, re-run    → row is DELETED (the behavior T144 denied)
  D. no row, no residual, re-run → nothing is created

Self-contained: imports audit-q.py, builds fixtures in a tmpdir, cleans up.
Never touches the real vault (warden self-fire disabled)."""
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

AQ = Path(__file__).parent / "audit-q.py"
spec = importlib.util.spec_from_file_location("audit_q", AQ)
aq = importlib.util.module_from_spec(spec)
sys.modules["audit_q"] = aq
spec.loader.exec_module(aq)
aq._warden_selffire = None  # disable warden self-fire for fixture writes

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


def qfix_rows(path: Path) -> list[str]:
    return [ln for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.lstrip().startswith("- **B-QFix")]


def make_finding(surface: Path, code="C41"):
    """A non-mechanically-fixable finding — the kind that routes to B-QFix."""
    return aq.Finding(
        code=code,
        severity="warning",
        surface_file=surface,
        surface_line=1,
        message="row 'T001' [Ready] has no `- **Next:**` sub-bullet",
        mechanically_fixable=False,
    )


TMP = Path(tempfile.mkdtemp())
try:
    bl = TMP / "ZZT Track" / "ZZT Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text(
        "# ZZT Backlog\n\n"
        "## Now\n\n"
        "- **T001 — Real work** [Ready] — do the thing. ^T001\n"
        "  - **Next:** run step one.\n",
        encoding="utf-8",
    )
    backlogs = {"ZZT": bl}

    # ---- A: a residual mints the row ---------------------------------------
    print("== A: a non-mechanically-fixable residual creates B-QFix ==")
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)
    rows = qfix_rows(bl)
    if len(rows) == 1:
        ok("B-QFix row created")
    else:
        no(f"expected exactly 1 B-QFix row, found {len(rows)}")
    if "[Ready]" in (rows[0] if rows else ""):
        ok("row is bracketed [Ready]")
    else:
        no("row is not [Ready]")
    if "C41" in bl.read_text(encoding="utf-8"):
        ok("residual is carried as a sub-bullet")
    else:
        no("residual sub-bullet missing")

    # ---- B: the residual persists — row is updated, not duplicated ---------
    print("== B: a second pass with the same residual keeps a singleton ==")
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)
    rows = qfix_rows(bl)
    if len(rows) == 1:
        ok("still exactly 1 B-QFix row (updated in place)")
    else:
        no(f"expected 1 B-QFix row after re-run, found {len(rows)}")

    # ---- C: the residual clears — row is DELETED ---------------------------
    # This is the case T144 claimed was broken. It is not.
    print("== C: zero residuals deletes the row (T144's denied behavior) ==")
    aq.route_findings_to_qfix([], backlogs)
    rows = qfix_rows(bl)
    if not rows:
        ok("B-QFix row deleted when residuals drop to zero")
    else:
        no(f"stale B-QFix row survived a zero-residual pass: {rows[0][:70]}")
    if "- **T001" in bl.read_text(encoding="utf-8"):
        ok("real rows are untouched by the clear")
    else:
        no("the clear removed a real row")

    # ---- D: nothing to clear is a no-op ------------------------------------
    print("== D: zero residuals with no existing row creates nothing ==")
    before = bl.read_text(encoding="utf-8")
    aq.route_findings_to_qfix([], backlogs)
    if bl.read_text(encoding="utf-8") == before:
        ok("no-op when there is no row and no residual")
    else:
        no("a zero-residual pass mutated a backlog with no B-QFix row")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\ntest-t144-qfix-lifecycle: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
