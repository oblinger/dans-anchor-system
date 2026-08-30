#!/usr/bin/env python3
"""test-t112-naming-prefix-optional.py — R-naming-01 recast (2026-08-02).

An anchor has ONE slug. A file prefix is OPTIONAL — folder membership is what
makes a file a child of an anchor, not its name — but IF a prefix is present it
must be that slug.

The rule previously REQUIRED a prefix, which put 3,047 of 7,799 vault files
(39%) in violation, and the R-naming-03 allowlist had grown into a workaround
for the over-reach. Recast, it finds 0 violations vault-wide — which is exactly
why this suite exists: a rule that reports nothing is indistinguishable from a
rule that checks nothing until you make it fire on purpose.

The defect it must still catch: a file leading with the anchor's folder NAME
where a distinct slug exists (`Tink Backlog.md` under slug `TINK`). That is the
shape that makes `{slug}` interpolation in a `where::` selector resolve to a
token no file matches — silently. T111 is that failure in the wild, where an
index-page term reached 0 of 22 pages.

    python3 test-t112-naming-prefix-optional.py
"""
import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
AUDIT = HERE.parent / "skills" / "audit" / "scripts"

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


spec = importlib.util.spec_from_file_location("audit_plan", AUDIT / "audit-plan.py")
assert spec and spec.loader
ap = importlib.util.module_from_spec(spec)
sys.modules["audit_plan"] = ap
spec.loader.exec_module(ap)


def verdict(anchor, filename):
    p = anchor / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# x\n", encoding="utf-8")
    return ap.chk_name_slug_prefixed(p, anchor, [])[0]


# An anchor whose folder NAME and SLUG differ — the case the rule is about.
d = pathlib.Path(tempfile.mkdtemp())
atticus = d / "Atticus"
atticus.mkdir()
(atticus / ".anchor").write_text("slug: ATT\n", encoding="utf-8")

print("The prefix is OPTIONAL — folder membership is what scopes a file")
for name in ("Notes on the redesign.md", "CLAUDE.md", "Lumens.md", "scratch.md"):
    check(f"unprefixed {name!r} passes", verdict(atticus, name), "pass")

print("\nA prefix, when present, must be the SLUG")
check("'Atticus Backlog.md' passes", verdict(atticus, "Atticus Backlog.md"), "pass")
check("'ATT.md' passes (anchor page)", verdict(atticus, "ATT.md"), "pass")
check("'Atticus Persona.md' passes", verdict(atticus, "Atticus Persona.md"), "pass")

print("\n...and the folder NAME is refused as a prefix — the T111 defect")
check("'Atticus Backlog.md' FAILS", verdict(atticus, "Atticus Backlog.md"), "fail")
check("'Atticus Persona.md' FAILS", verdict(atticus, "Atticus Persona.md"), "fail")
# The message must name the fix, not just the fault.
p = atticus / "Atticus Backlog.md"
_, msg = ap.chk_name_slug_prefixed(p, atticus, [])
check("the refusal names the slug to use instead", "'ATT'" in msg, True)

print("\nCase alone is a defect — this is what T111 turned on")
tink = d / "Tink"
tink.mkdir()
(tink / ".anchor").write_text("slug: TINK\n", encoding="utf-8")
check("'Tink Backlog.md' passes", verdict(tink, "Tink Backlog.md"), "pass")
check("'Tink Backlog.md' FAILS (folder-name casing)",
      verdict(tink, "Tink Backlog.md"), "fail")

print("\nA nested anchor carries the ROOT slug, not its own folder name")
sub = tink / "TINK Track"
sub.mkdir()
(sub / ".anchor").write_text("", encoding="utf-8")   # no slug: → falls back to folder
check("'Tink Backlog.md' inside 'Tink Track/' passes",
      verdict(sub, "Tink Backlog.md"), "pass")
check("...and an unprefixed file there passes too",
      verdict(sub, "scratch.md"), "pass")

print("\nR-naming-03 sanctioned shapes still pass")
for name in ("SKILL.md", "README.md", "F007 — Some feature.md",
             "ATT042 - Some feature.md", "2026-08-02 A log entry.md"):
    check(f"{name!r} passes", verdict(atticus, name), "pass")

print(f"\nR-naming-01 prefix-optional: {sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
