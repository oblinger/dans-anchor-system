#!/usr/bin/env python3
"""test-f254-audit-fix.py — F254 Step B: audit-q.py --fix corruption fixes.

Regression tests for the two F251 Fable-scan CRITICALs in the doc-mutating
`--fix` path:
  B1 (#3) fence-blindness — `backlog_entries` used to parse a ```-fenced example
     row/heading as real, so `apply_c4_fix`/`apply_placement_fixes` extracted it
     out of its code block (splitting the fence) and a fenced `## H2` flipped the
     live horizon for real rows below it;
  B2 (#2) arrow-target fallback — `_arrow_target` fell back to the FIRST arrow
     link (an unrelated prose mention) when no arrow was the row's own doc, so
     C23/C24 counted Qs from the wrong file and rewrote a live [Questions] row.

Self-contained: imports audit-q.py, builds fixtures in a tmpdir, cleans up.
Never touches the real vault (warden self-fire disabled)."""
import importlib.util
import re
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

TMP = Path(tempfile.mkdtemp())
try:
    # ---- B1: fence-blindness ------------------------------------------------
    print("== B1 (#3) fenced example row/heading is not parsed as real ==")
    bl = TMP / "ZZT Track" / "ZZT Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text(
        "# ZZT Backlog\n\n"
        "## Ready\n\n"
        "- **F001 — Real work** [Ready] — do the thing.\n"
        "  - **Next:** run step one.\n\n"
        "Example of the old row format (illustration only):\n\n"
        "```\n"
        "## Now\n"
        "- **F999 — Example row** [Done 2026-01-01] — how rows used to look.\n"
        "```\n\n"
        "- **F002 — More work** [Ready] — second thing.\n"
        "  - **Next:** run step two.\n\n"
        "## Done\n",
        encoding="utf-8",
    )
    entries = aq.backlog_entries(bl, {})
    ids = {e.identifier for e in entries}
    if "F999" not in ids:
        ok("fenced F999 row not parsed as a backlog entry")
    else:
        no("fenced F999 row wrongly parsed as real")
    f002 = next((e for e in entries if e.identifier == "F002"), None)
    if f002 and f002.horizon == "Ready":
        ok("fenced `## Now` did NOT flip horizon (F002 still under Ready)")
    else:
        no(f"fenced heading flipped horizon: F002 horizon={getattr(f002,'horizon',None)!r}")
    changed, log = aq.apply_c4_fix(bl, entries)
    after = bl.read_text(encoding="utf-8")
    # The fence must stay intact and F999 must remain inside it (not moved to ## Done).
    fence_intact = "```\n## Now\n- **F999 — Example row**" in after
    done_idx = after.index("## Done")
    f999_idx = after.index("F999")
    if fence_intact and f999_idx < done_idx:
        ok("apply_c4_fix left the fenced example row untouched (fence not split)")
    else:
        no("apply_c4_fix corrupted the fenced example block")

    # ---- B2: arrow-target own-doc-only --------------------------------------
    print("== B2 (#2) _arrow_target returns None when no arrow is the row's own doc ==")
    bl2 = TMP / "R2 Track" / "R2 Backlog.md"
    bl2.parent.mkdir(parents=True, exist_ok=True)
    bl2.write_text(
        "# R2 Backlog\n\n"
        "## Later\n\n"
        "- **F077 — Seven** [Questions] — context → [[F100 — Nine]] ^F077\n"
        "- **F088 — Eight** [Questions] — see → [[F088 — Eight]] ^F088\n",
        encoding="utf-8",
    )
    entries2 = aq.backlog_entries(bl2, {})
    e077 = next(e for e in entries2 if e.identifier == "F077")
    e088 = next(e for e in entries2 if e.identifier == "F088")
    if aq._arrow_target(e077) is None:
        ok("F077 (arrow to unrelated F100) -> _arrow_target None (falls to inline count)")
    else:
        no("F077 wrongly resolved an unrelated arrow as its own doc")
    at088 = aq._arrow_target(e088)
    if at088 is not None and (at088.target_basename or "").startswith("F088 "):
        ok("F088 (own-doc arrow) -> _arrow_target resolves correctly")
    else:
        no(f"F088 own-doc arrow not resolved: {at088!r}")
    # check_c24 must NOT emit a wrongful finding on F077 (arrow present but not own).
    c24 = aq.check_c24_questions_count_match(entries2)
    if not any(f.surface_line == e077.source_line for f in c24):
        ok("check_c24 emits no wrongful rebracket finding for F077")
    else:
        no("check_c24 still fires on F077 from the wrong doc")

    # ---- D1: C24 fixer [Designing] fallback when no Next: (F250 #10) --------
    print("== D1 (#10) C24 fixer promotes to [Ready] ONLY with a Next: sub-bullet ==")
    bl3 = TMP / "R3 Track" / "R3 Backlog.md"
    bl3.parent.mkdir(parents=True, exist_ok=True)
    bl3.write_text(
        "# R3 Backlog\n\n"
        "## Later\n\n"
        "- **T001 — No next** [Questions] — body only ^T001\n"
        "- **T002 — Has next** [Questions] — body ^T002\n"
        "  - **Next:** run the thing.\n",
        encoding="utf-8",
    )
    entries3 = aq.backlog_entries(bl3, {})
    aq.apply_c24_fix(bl3, entries3)
    after3 = bl3.read_text(encoding="utf-8")
    before_t002 = after3.split("T002")[0]
    if "**T001 — No next** [Designing]" in after3 and "[Ready]" not in before_t002:
        ok("0-Q row with NO Next -> [Designing] (not F171-forbidden [Ready])")
    else:
        no(f"T001 fallback wrong:\n{after3}")
    if "**T002 — Has next** [Ready]" in after3:
        ok("0-Q row WITH Next -> [Ready]")
    else:
        no(f"T002 promotion wrong:\n{after3}")

    # ---- C2: audit-q banner Questions counts pending only (F251 #7) ---------
    print("== C2 (#7) derive_anchor_banner Questions = pending only (no Resolved/fenced) ==")
    anc = TMP / "vault" / "ZZC"
    (anc / "ZZC Track").mkdir(parents=True, exist_ok=True)
    (anc / "ZZC Design" / "ZZC Features").mkdir(parents=True, exist_ok=True)
    (anc / ".anchor").write_text("slug: ZZC\n", encoding="utf-8")
    (anc / "ZZC Design" / "ZZC Features" / "F010 — Thing.md").write_text(
        "# F010 — Thing\n\n## Open Questions\n\n"
        "- **Q1 — First** — pick A or B\n"
        "- **Q2 — Second** — pick C or D\n\n"
        "```\n- **Q9 — Fenced example** — not real\n```\n\n"
        "## Resolved\n\n"
        "- **Q3 — Old** — resolved\n- **Q4 — Older** — resolved\n- **Q5 — Oldest** — resolved\n",
        encoding="utf-8",
    )
    blc = anc / "ZZC Track" / "ZZC Backlog.md"
    blc.write_text(
        "# ZZC Backlog\n\n## Now\n\n"
        "- **F010 — Thing** [2 Questions] — see → [[F010 — Thing]] ^F010\n",
        encoding="utf-8",
    )
    vidx = aq.build_vault_index(TMP / "vault")
    banner = aq.derive_anchor_banner("ZZC", blc, vidx) or ""
    # F260 renamed the user-facing plate: pending Questions now report as `User`.
    qm = re.search(r"User\s+(\d+)", banner)
    if qm and qm.group(1) == "2":
        ok("banner User = 2 (pending only; 3 Resolved + 1 fenced excluded)")
    else:
        no(f"banner User wrong: {banner!r}")

    # ---- C1: queries-render banner "Ready" = [Ready] only, not [Active] (F250 #9)
    print("== C1 (#9) queries-render banner Ready counts [Ready] only (excludes [Active]) ==")
    QR = Path(__file__).parent / "queries-render.py"
    qr_spec = importlib.util.spec_from_file_location("queries_render", QR)
    qr_mod = importlib.util.module_from_spec(qr_spec)
    sys.modules["queries_render"] = qr_mod
    qr_spec.loader.exec_module(qr_mod)  # imports audit_q from real HOME — fine in-process
    blr = TMP / "ZZR Track" / "ZZR Backlog.md"
    blr.parent.mkdir(parents=True, exist_ok=True)
    blr.write_text(
        "# ZZR Backlog\n\n## Now\n\n"
        "- **F001 — Active one** [Active] — doing it ^F001\n"
        "  - **Next:** finish it.\n"
        "- **F002 — Ready one** [Ready] — queued ^F002\n"
        "  - **Next:** start it.\n",
        encoding="utf-8",
    )
    rows = qr_mod.parse_backlog(blr)
    banner_r = qr_mod.derive_banner("ZZR", rows, blr, {}) or ""
    # F260 replaced the `Ready` plate with `Runnable` and DID fold [Active] in —
    # a mid-implementation row carrying a `- **Next:**` is runnable work. This
    # assertion previously encoded the opposite and had been red ever since.
    rm = re.search(r"Runnable\s+(\d+)", banner_r)
    if rm and rm.group(1) == "2":
        ok("banner Runnable = 2 ([Ready] + [Active], per F260)")
    else:
        no(f"banner Runnable wrong (expected 2): {banner_r!r}")

    print()
    print(f"==== RESULT: {PASS} passed, {FAIL} failed ====")
    sys.exit(1 if FAIL else 0)
finally:
    shutil.rmtree(TMP, ignore_errors=True)
