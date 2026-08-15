#!/usr/bin/env python3
"""test-t144-qfix-lifecycle.py — the audit-residual lifecycle, POST-F332.

T144 pinned the B-QFix `[Ready]` row's reconcile behavior. F332 Q2 (Dan,
2026-08-15) retired that row: mechanical audit debris is sub-surface work
the user is neither aware of nor interested in, so `--fix` now routes it to
`{slug} Chores.md` ([[DAS Chores]]) beside the backlog, and clears/deletes
that file's audit-owned bullets when residuals drop to zero. A legacy
B-QFix row found on a touched anchor is removed in the same pass.

  A. residual present            → chores file created carrying it; no B-QFix
                                   row is minted; a legacy row is removed
  B. residual persists, re-run   → idempotent (hand-added chores survive)
  C. residual cleared, re-run    → audit bullets cleared; file deleted when
                                   nothing hand-added remains
  E. read-only pass              → reports stale audit chores, mutates nothing
  D. no residue, re-run          → no-op

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
    """A non-mechanically-fixable finding — the kind that routes to chores."""
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
    # Seed a LEGACY B-QFix row so test A also covers its removal on touch.
    bl.write_text(
        "# ZZT Backlog\n\n"
        "## Now\n\n"
        "- **T001 — Real work** [Ready] — do the thing. ^T001\n"
        "  - **Next:** run step one.\n"
        "- **B-QFix — QFix** [Ready] — legacy machinery row. ^B-QFix\n"
        "  - **C99** old/residual.md:1 — stale capture from before F332.\n",
        encoding="utf-8",
    )
    backlogs = {"ZZT": bl}
    chores = bl.parent / "ZZT Chores.md"

    # ---- A: a residual routes to chores; the legacy row is removed ---------
    print("== A: a residual routes to Chores.md; no B-QFix row survives ==")
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)
    if chores.exists() and "C41" in chores.read_text(encoding="utf-8"):
        ok("chores file created carrying the residual")
    else:
        no(f"chores file missing or empty: {chores}")
    if not qfix_rows(bl):
        ok("legacy B-QFix row removed on touch; none minted")
    else:
        no("a B-QFix row survives in the backlog")

    # ---- B: idempotent re-run; hand-added chores survive -------------------
    print("== B: re-run is idempotent and preserves hand-added chores ==")
    with chores.open("a", encoding="utf-8") as f:
        f.write("- hand-added chore: rewrap the widget cable.\n")
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)
    ctext = chores.read_text(encoding="utf-8")
    if ctext.count("C41") == 1:
        ok("audit bullet not duplicated on re-run")
    else:
        no(f"audit bullet duplicated:\n{ctext}")
    if "hand-added chore" in ctext:
        ok("hand-added chore survives the rewrite")
    else:
        no("hand-added chore was destroyed")

    # ---- C: zero residuals clears audit bullets; file kept for hand chores -
    print("== C: zero residuals clears audit bullets ==")
    aq.route_findings_to_qfix([], backlogs)
    ctext = chores.read_text(encoding="utf-8")
    if "C41" not in ctext and "hand-added chore" in ctext:
        ok("audit bullets cleared; hand chores kept, file retained")
    else:
        no(f"clear pass wrong:\n{ctext}")
    # Now with no hand chores, the file itself goes.
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)
    lines = [l for l in chores.read_text(encoding="utf-8").splitlines()
             if l.startswith("- ") and "hand-added" in l]
    chores.write_text(
        "\n".join(l for l in chores.read_text(encoding="utf-8").splitlines()
                  if "hand-added" not in l) + "\n", encoding="utf-8")
    aq.route_findings_to_qfix([], backlogs)
    if not chores.exists():
        ok("chores file deleted when nothing hand-added remains")
    else:
        no(f"empty chores file survived:\n{chores.read_text(encoding='utf-8')}")
    if "- **T001" in bl.read_text(encoding="utf-8"):
        ok("real rows are untouched throughout")
    else:
        no("a real row was damaged")

    # ---- E: the read-only path REPORTS staleness without mutating ----------
    print("== E: read-only pass reports stale chores and does not touch them ==")
    aq.route_findings_to_qfix([make_finding(bl)], backlogs)   # re-mint chores
    before_bl = bl.read_text(encoding="utf-8")
    before_ch = chores.read_text(encoding="utf-8")
    log = aq.report_stale_qfix_rows([make_finding(bl)], backlogs)
    if not log:
        ok("silent while the residual still reproduces")
    else:
        no(f"reported staleness on a live residual: {log}")
    log = aq.report_stale_qfix_rows([], backlogs)
    if log and "stale audit chores" in log[0]:
        ok("reports stale audit chores once residuals stop reproducing")
    else:
        no(f"failed to report stale chores: {log}")
    if (bl.read_text(encoding="utf-8") == before_bl
            and chores.read_text(encoding="utf-8") == before_ch):
        ok("read-only pass left both files byte-identical")
    else:
        no("read-only pass mutated a file")
    aq.route_findings_to_qfix([], backlogs)   # tidy up for D

    # ---- D: nothing to clear is a no-op ------------------------------------
    print("== D: zero residuals with no residue creates nothing ==")
    before_bl = bl.read_text(encoding="utf-8")
    aq.route_findings_to_qfix([], backlogs)
    if bl.read_text(encoding="utf-8") == before_bl and not chores.exists():
        ok("no-op when there is no residue and no residual")
    else:
        no("a zero-residual pass created or mutated something")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\ntest-t144-qfix-lifecycle: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
