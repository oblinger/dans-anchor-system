#!/usr/bin/env python3
"""test-f277-disclosure.py — R-spine-03/05 (F277 progressive-disclosure review).

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
# Descriptive by default — the drift cases are about summaries that make a claim
# about each unit. Name-only summaries get their own section further down.
TOC = ("| Table of Contents |  |\n|---|---|\n"
       "| **[[#S0]]** | what the first section covers |\n\n")

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
# These two look again with NO intervening write, so they pin only the
# no-change case. The case that matters in production — looking again after
# the document has been edited somewhere unrelated — is T564's, in
# test-t564-summary-fresh-names-the-toc.py §3, and it was failing here
# undetected until 2026-08-20 precisely because this file never writes between
# checks. Same shape as the ad-hoc fixtures this file's docstring indicts.
check("same drift does NOT re-fire", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
check("still quiet on a third look", ap.chk_summary_fresh(f, tmp, "")[0], "pass")
bump(f, 4)
check("further drift fires again", ap.chk_summary_fresh(f, tmp, "")[0], "fail")
f.write_text(f.read_text().replace("what the first section covers", "rewritten gloss"))
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

print("summary_fresh — name-only summaries are content-invariant")
NAME_ONLY = "| Table of Contents |  |\n|---|---|\n| **[[#S0]]** |  |\n| **[[#S1]]** |  |\n\n"
DESCRIPTIVE = ("| Table of Contents |  |\n|---|---|\n"
               "| **[[#S0]]** | what the first section covers |\n"
               "| **[[#S1]]** | what the second section covers |\n\n")

tmp = fresh_env()
bare = doc(tmp / "Bare.md", toc=NAME_ONLY)
check("name-only summary is not descriptive", ap._disclosure_descriptive(bare), False)
check("name-only first sight blesses", ap.chk_summary_fresh(bare, tmp, "")[0], "pass")
for i in (1, 2, 3):
    bump(bare, i)
check("name-only stays quiet on content drift", ap.chk_summary_fresh(bare, tmp, "")[0], "pass")
bare.write_text(bare.read_text() + "\n## NewSection\n\n" + FILLER)
check("...but an ADDED unit still fires", ap.chk_summary_fresh(bare, tmp, "")[0], "fail")

tmp = fresh_env()
desc = doc(tmp / "Desc.md", toc=DESCRIPTIVE)
check("glossed summary is descriptive", ap._disclosure_descriptive(desc), True)
check("descriptive first sight blesses", ap.chk_summary_fresh(desc, tmp, "")[0], "pass")
for i in (1, 2, 3):
    bump(desc, i)
check("descriptive summary DOES fire on content drift",
      ap.chk_summary_fresh(desc, tmp, "")[0], "fail")

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
