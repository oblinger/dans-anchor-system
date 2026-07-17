#!/usr/bin/env python3
"""test-f251-residuals.py — F253 Step 3: the non-CRITICAL F251 Fable-scan
residual fixes in audit-q.py's --fix path.

  #4  (HIGH) apply_c36_fix selected lines by the findings' stale `surface_line`
      (computed BEFORE apply_placement_fixes shifts rows) and lacked check_c36's
      residual-row guard → it could turn an inert backtick in a `- **C36**`
      residual into a live link. Now it self-scans the current file with the
      same guards (fence + residual skip), immune to line shifts.
  #5  (MED)  C18 auto-moves an expired [Verify-by] row to ## Done without
      rebracketing; C15 then flagged it "belongs in ## Verify" forever while the
      fixer refused. Now check_c15 yields to C18 (skips an expired Verify-by in
      ## Done).
  #6  (MED)  apply_c23_fix / apply_c24_fix recomputed the head region on the RAW
      line, so a ` — ` inside a leading wiki-link truncated the head before the
      status bracket → the replace no-op'd and the finding flapped. Now the head
      span comes from the shared cleaned-line computation _detect_status uses.
  #8  (LOW)  apply_c4_fix inserted every moved row at a fixed offset → multiple
      stale rows landed in ## Done reversed. Now insert_at advances per block.
  #9  (LOW)  apply_c6_fix stranded a FOREIGN trailing block-id (`^F077-note`)
      mid-line when appending `^F077-Q1`. Now it skips + reports foreign ids.
  #10 (LOW)  check_c37's docstring claimed a phantom "C41" (owned by the
      soak-question check). Removed.

Self-contained: imports audit-q.py, builds fixtures in a tmpdir, cleans up.
Never touches the real vault (warden self-fire disabled)."""
import datetime
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

TODAY = datetime.date(2026, 7, 16)
PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

TMP = Path(tempfile.mkdtemp())
try:
    # ---- #4: apply_c36_fix residual guard + line-shift immunity -------------
    print("== #4 apply_c36_fix skips residual rows + ignores stale surface_line ==")
    bl = TMP / "ZZA Track" / "ZZA Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text(
        "# ZZA Backlog\n\n"
        "## Now\n\n"
        "- **F001 — Real** [Ready] — see `foo.md` for context.\n"
        "  - **Next:** do it.\n"
        "- **C36** residual quoting `foo.md` — must stay backticked.\n\n"
        "## Done\n",
        encoding="utf-8",
    )
    vindex = {"foo": [Path("/somewhere/foo.md")]}  # makes `foo.md` → [[foo]]
    # Deliberately stale surface_line (999) — the old code gated on it and would
    # fix nothing; the fixed code self-scans and still linkifies the real row.
    findings = [aq.Finding(
        severity="warning", surface_file=bl, surface_line=999,
        code="C36", message="x", mechanically_fixable=True,
    )]
    n = aq.apply_c36_fix(bl, findings, vindex)
    out = bl.read_text(encoding="utf-8")
    if "[[foo]]" in out and "- **F001" in out.split("[[foo]]")[0].splitlines()[-1]:
        ok("real F001 row linkified despite a stale surface_line (self-scan)")
    else:
        no(f"F001 not linkified via self-scan (n={n})\n{out}")
    if "- **C36** residual quoting `foo.md`" in out:
        ok("`- **C36**` residual row's backtick left intact (guard held)")
    else:
        no(f"C36 residual row was wrongly linkified\n{out}")

    # ---- #5: C18/C15 no longer flag each other forever ----------------------
    print("== #5 check_c15 yields to C18 for an expired Verify-by in ## Done ==")
    bl5 = TMP / "ZZB Track" / "ZZB Backlog.md"
    bl5.parent.mkdir(parents=True, exist_ok=True)
    bl5.write_text(
        "# ZZB Backlog\n\n"
        "## Now\n\n"
        "- **F010 — Live verify** [Verify] — check it.\n\n"
        "## Done\n\n"
        "- **F011 — Retired** [Verify-by 2020-01-01] — window long past.\n",
        encoding="utf-8",
    )
    entries = aq.backlog_entries(bl5, {})
    c15 = aq.check_c15_watching_waiting_in_later(entries, TODAY)
    ids = {f.surface_line for f in c15}
    flagged_ids = {e.identifier for e in entries
                   if e.source_line in {f.surface_line for f in c15}}
    if "F011" not in flagged_ids:
        ok("expired [Verify-by] row in ## Done is NOT flagged by C15")
    else:
        no(f"C15 still flags the retired Verify-by row: {flagged_ids}")
    if "F010" in flagged_ids:
        ok("a live [Verify] row misfiled in ## Now IS still flagged by C15")
    else:
        no(f"C15 stopped flagging a genuinely-misfiled Verify row: {flagged_ids}")

    # ---- #6: apply_c23_fix head-region past a leading wiki-link ` — ` --------
    print("== #6 apply_c23_fix rewrites [Designing] past a leading wiki-link — ==")
    bl6 = TMP / "ZZC Track" / "ZZC Backlog.md"
    bl6.parent.mkdir(parents=True, exist_ok=True)
    bl6.write_text(
        "# ZZC Backlog\n\n"
        "## Now\n\n"
        "- **T900** [[Ref — Doc]] [Designing] — plain body, no arrow link.\n"
        "  - **Next:** proceed.\n\n"
        "## Done\n",
        encoding="utf-8",
    )
    entries6 = aq.backlog_entries(bl6, {})
    t900 = [e for e in entries6 if e.identifier == "T900"]
    pre_ok = bool(t900) and t900[0].status == "Designing"
    changed, log = aq.apply_c23_fix(bl6, entries6)
    out6 = bl6.read_text(encoding="utf-8")
    if pre_ok and changed and "[Ready]" in out6 and "[Designing]" not in out6:
        ok("[Designing] → [Ready] even with a leading `[[Ref — Doc]]` before it")
    else:
        no(f"C23 head-region fix failed — pre_ok={pre_ok} changed={changed}\n{out6}")
    # The pre-existing wiki-link must be preserved verbatim.
    if "[[Ref — Doc]]" in out6:
        ok("leading wiki-link preserved verbatim through the splice")
    else:
        no(f"wiki-link mangled by the splice\n{out6}")

    # ---- #8: apply_c4_fix preserves source order ----------------------------
    print("== #8 apply_c4_fix moves multiple stale rows in source order ==")
    bl8 = TMP / "ZZD Track" / "ZZD Backlog.md"
    bl8.parent.mkdir(parents=True, exist_ok=True)
    bl8.write_text(
        "# ZZD Backlog\n\n"
        "## Now\n\n"
        "- **F020 — First done** [Done 2026-01-01] — a.\n"
        "- **F021 — Second done** [Done 2026-01-02] — b.\n\n"
        "## Done\n",
        encoding="utf-8",
    )
    entries8 = aq.backlog_entries(bl8, {})
    changed8, _ = aq.apply_c4_fix(bl8, entries8)
    out8 = bl8.read_text(encoding="utf-8")
    done_body = out8.split("## Done", 1)[1]
    if changed8 and done_body.find("F020") < done_body.find("F021") \
            and "F020" in done_body and "F021" in done_body:
        ok("F020 precedes F021 in ## Done (source order preserved)")
    else:
        no(f"C4 row order wrong in ## Done\n{out8}")

    # ---- #9: apply_c6_fix skips a foreign trailing block-id -----------------
    print("== #9 apply_c6_fix skips + reports a foreign trailing block-id ==")
    doc = TMP / "F077 — Example.md"
    doc.write_text(
        "---\ndescription: x\n---\n\n"
        "# [[ZZE]] · F077 — Example\n\n"
        "## Open Questions\n"
        "<!-- state:q 00 -->\n\n"
        "- **Q1 — Something** — pick one. ^F077-note\n"
        "  - **(A)** first.\n"
        "  - **(B)** second.\n"
        "  - **Recommendation:** None.\n",
        encoding="utf-8",
    )
    qs = aq.extract_q_entries(doc, "F077")
    before = doc.read_text(encoding="utf-8")
    log9 = aq.apply_c6_fix(qs)
    after = doc.read_text(encoding="utf-8")
    if "^F077-note" in after and after == before:
        ok("foreign `^F077-note` left intact — Q line not clobbered")
    else:
        no(f"foreign block-id line was mutated\n{after}")
    if any("SKIPPED" in m and "foreign" in m for m in log9):
        ok("skip is reported for manual attention")
    else:
        no(f"skip not reported in log: {log9}")

    # ---- #10: check_c37 docstring no longer claims a phantom C41 ------------
    print("== #10 check_c37 docstring drops the phantom C41 ==")
    if "C41" not in (aq.check_c37_queries_item_format.__doc__ or ""):
        ok("check_c37 docstring no longer documents a phantom C41")
    else:
        no("check_c37 docstring still claims C41")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
