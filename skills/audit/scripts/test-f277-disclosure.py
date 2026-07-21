#!/usr/bin/env python3
"""test-f277-disclosure.py — R-progressive-04/05 (F277 progressive-disclosure review).

Covers the two checkers behind the "Warden detects staleness, the agent judges"
mechanism: `summary_present_iff_complex` (a complex folder-index must carry a
dispatch table) and `summary_fresh` (re-ask once the covered content has moved).

The anti-nag cases are the reason this file exists. F277's design named four
dampers; the once-per-drift one shipped missing, and the gap only surfaced when
the rule fired twice on one file in one session during the advisory soak. Ad-hoc
fixtures had passed — they never re-ran a checker against unchanged drift.

    python3 test-f277-disclosure.py
"""
import importlib.util
import pathlib
import tempfile

SCRIPT = pathlib.Path(__file__).parent / "audit-plan.py"
_spec = importlib.util.spec_from_file_location("audit_plan", SCRIPT)
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)

FILLER = "filler line\n" * 40
TOC = "| Table of Contents |  |\n|---|---|\n| **[[#S0]]** |  |\n\n"

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def fresh_env():
    """A temp anchor root with its own registry — checkers must not share state."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    ap.DISCLOSURE_REGISTRY = tmp / "disclosure.json"
    return tmp


def doc(path, n_sections=8, toc=TOC):
    body = "".join(f"## S{i}\n\n{FILLER}" for i in range(n_sections))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {path.stem}\n\n{toc}{body}")
    return path


def bump(path, section):
    """Rewrite one section's body wholesale — drift under an unchanged heading."""
    path.write_text(path.read_text().replace(
        f"## S{section}\n\n{FILLER}", f"## S{section}\n\n" + "CHANGED\n" * 40))


print("summary_fresh — blessing and drift")
tmp = fresh_env()
f = doc(tmp / "Doc.md")
check("first sight blesses silently", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("prose-identical rewrite stays quiet", ap.chk_summary_fresh(f, tmp, "")[0], "pass")

for i in (1, 2, 3):
    bump(f, i)
check("quarter-drift fires", ap.chk_summary_fresh(f, tmp, "")[0], "fail")

print("summary_fresh — anti-nag (F277 § Not nagging)")
check("same drift does NOT re-fire", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("still quiet on a third look", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
bump(f, 4)
check("further drift fires again", ap.chk_summary_fresh(f, tmp, "")[0], "fail")
f.write_text(f.read_text().replace("| **[[#S0]]** |  |", "| **[[#S0]]** | rewritten |"))
check("summary rewrite re-blesses", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("quiet after re-blessing", ap.chk_summary_fresh(f, tmp, "")[0], "pass")

print("summary_fresh — exemptions")
tmp = fresh_env()
short = tmp / "Short.md"
short.write_text("# Short\n\n## A\n\nbody\n\n## B\n\nbody\n")
check("below the complexity floor is exempt", ap.chk_summary_fresh(short, tmp, "")[0], "pass")

tmp = fresh_env()
nosum = doc(tmp / "NoSummary.md", toc="")
check("missing summary is 04's business, not 05's",
      ap.chk_summary_fresh(nosum, tmp, "")[0], "pass")

print("summary_present_iff_complex")
tmp = fresh_env()
plain = doc(tmp / "Plain.md", toc="")
check("a plain file is not 04's business", ap.chk_summary_present_iff_complex(plain, tmp, "")[0], "pass")

tmp = fresh_env()
idx = doc(tmp / "Folder" / "Folder.md", toc="")
for i in range(4):
    (idx.parent / f"member{i}.md").write_text("# m\n\nbody\n")
check("complex folder index without a dispatch table fires",
      ap.chk_summary_present_iff_complex(idx, tmp, "")[0], "fail")
idx.write_text(idx.read_text().replace("# Folder\n\n", "# Folder\n\n" + TOC))
check("...and passes once it has one",
      ap.chk_summary_present_iff_complex(idx, tmp, "")[0], "pass")

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
