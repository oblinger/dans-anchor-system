#!/usr/bin/env python3
"""T657 — R-spine-02 (doc_head_orientation_line) exempts T655 stone archive
month files: `archive/YYYY-MM <list> archive.md` opens with frontmatter aliases
then `# <stone>` sections with `key:: value` fields and no title line (Dan
2026-09-03). The same bytes outside an `archive/` folder still fail.
Run: python3 test-t657-archive-month-file-head.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

PLAN = Path(__file__).resolve().parent / "audit-plan.py"
BODY = ("---\naliases:\n  - A P0002\n---\n\n# A P0002\nline:: second [[A]] \nretired:: 2026-09-03\n\n"
        "## Re-census\n\n| a | b |\n| - | - |\n\nprose\n")
fails = 0


def verdict(path: Path) -> str:
    r = subprocess.run([sys.executable, str(PLAN), str(path), "--mode", "doc", "--run"], capture_output=True, text=True)
    for line in (r.stdout + r.stderr).splitlines():
        if "R-spine-02" in line:
            return line
    return "R-spine-02 not reported\n" + r.stdout[-400:] + r.stderr[-400:]


def check(label, ok, extra=""):
    global fails
    print(("  ok:   " if ok else "  FAIL: ") + label + ("" if ok else f"\n        {extra[:500]}"))
    fails += 0 if ok else 1


with tempfile.TemporaryDirectory(prefix="t657-") as td:
    root = Path(td)
    arch = root / "A Pebbles" / "archive"; arch.mkdir(parents=True)
    month = arch / "2026-09 A archive.md"; month.write_text(BODY)
    v = verdict(month)
    check("month file passes R-spine-02", v.startswith("✓") and "stone archive month file" in v, v)
    other = root / "A Pebbles" / "2026-09 A archive.md"; other.write_text(BODY)
    v = verdict(other)
    check("same bytes outside archive/ still fail", v.startswith("✗") and "no orientation line" in v, v)
    legacy = arch / "A P0002.md"; legacy.write_text(BODY)
    v = verdict(legacy)
    check("a non-month-named file in archive/ is not exempt", v.startswith("✗"), v)

print(f"\n{'PASS' if not fails else 'FAIL'} — {fails} failing")
sys.exit(1 if fails else 0)
