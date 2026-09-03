#!/usr/bin/env python3
"""T204 — audit-dispatch is REPORT ONLY (Dan 2026-09-03: "let's make it report
only"). The retired `--fix` joined unlisted children with the cell delimiter
(N children -> N+1 cells) and at N=1 put the child in the name cell. Now: the
page's bytes are identical after every invocation, `--fix` is not an argument,
unlisted children are reported and never injected, and every proposed row has
the header's column count. Run: python3 test-t204-dispatch-report-only.py"""
import io, contextlib, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
AD = HERE / "audit-dispatch.py"
PASS = FAIL = 0


def check(label, ok, extra=""):
    global PASS, FAIL
    PASS += bool(ok); FAIL += not ok
    print(("  ok   " if ok else "  FAIL ") + label + (f"\n         {extra!r}" if extra and not ok else ""))


def run(*argv):
    r = subprocess.run([sys.executable, str(AD), *argv], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


with tempfile.TemporaryDirectory(prefix="t204-") as td:
    root = Path(td) / "ZZQ"
    root.mkdir()
    (root / ".anchor").write_text("slug: ZZQ\n")
    # children are sibling .md files (what on_disk_children lists); link
    # liveness is judged against the VAULT, so the listed row targets a real page
    for child in ("ZZQ Beta", "ZZQ Gamma"):
        (root / f"{child}.md").write_text(f"# {child}\n")
    page = root / "ZZQ.md"
    page.write_text(
        "# ZZQ\n\n"
        "| -[[Old Name]]- | [[kmr]] → [[ZZQ]] |\n"
        "| --- | --- |\n"
        "| [[Tink Backlog]] | the listed one |\n"
        "| nothing here |  |\n"
        "| ... |  |\n\n"
        "Prose below the table.\n")
    before = page.read_bytes()

    rc, out, err = run(str(root))
    check("plain run exits 0", rc == 0, err)
    check("page bytes unchanged after a plain run", page.read_bytes() == before)
    check("report says it never writes", "REPORT ONLY" in out and "never writes" in out, out)
    check("unlisted children are REPORTED, named", "ZZQ Beta" in out and "ZZQ Gamma" in out, out)
    check("...and not injected as a row", "| [[ZZQ Beta]]" not in out and "[[ZZQ Beta]] | [[ZZQ Gamma]]" not in out, out)
    check("breadcrumb drift is proposed, not written",
          "-[[ZZQ]]-" in out and b"-[[Old Name]]-" in page.read_bytes(), out)

    rc, out, err = run(str(root), "dry")
    check("explicit `dry` still accepted", rc == 0 and page.read_bytes() == before, err)

    rc, out, err = run(str(root), "--fix")
    check("--fix is no longer an argument", rc != 0 and "unrecognized arguments: --fix" in err, err)
    check("...and wrote nothing", page.read_bytes() == before)

    rc, out, err = run(str(root), "--json")
    rep = json.loads(out)
    check("json report has no `applied` key", "applied" not in rep, list(rep))
    check("json report names the unlisted children", rep["report"]["unlisted_children"] == ["ZZQ Beta", "ZZQ Gamma"], rep["report"])
    cols = [row.count("|") - 1 for row in rep["proposed"] if row.strip().startswith("|")]
    check("every proposed row has the header's column count (no N+1-cell row)", cols and len(set(cols)) == 1, (cols, rep["proposed"]))
    check("page bytes unchanged after --json", page.read_bytes() == before)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
