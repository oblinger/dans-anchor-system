#!/usr/bin/env python3
"""T071 — the eleven checkers that had `check::` refs but no implementation.

An unimplemented `check::` ref does not fail loudly: the checker lookup misses,
and `audit_on_write` suppresses `error` verdicts, so nine Agenda rules plus
two others were silently inert for their whole lifetime. This pins each one
firing on a violation AND staying silent on a conforming file — the second half
matters more, because a checker that fires on good input gets disabled within a
day and is then inert again, this time on purpose.

Run: python3 test-t071-wired-checkers.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "ap", Path(__file__).resolve().parent / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def verdict(checker, target, root, args=()):
    return ap.CHECKERS[checker](target, root, list(args))[0]


GOOD_AGENDA = """---
description: how ZZT wins
---
# ZZT Agenda
What ZZT is trying to achieve and how it will know.

## Purpose

Why this activity exists.

## Success — what "won" looks like

The falsifiable end-state.

## Approach

The theory of victory.

## Constraints

What bounds us.

## Cadence

Revisited monthly by the ZZT pilot.
"""


def build(root, agenda_text=GOOD_AGENDA, rel="ZZT Track/ZZT Agenda.md",
          track=True, anchor_extra=""):
    (root / ".anchor").write_text("slug: ZZT\n" + anchor_extra)
    (root / "ZZT.md").write_text("# ZZT\nAn anchor.\n")
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(agenda_text)
    if track:
        t = root / "ZZT Track" / "ZZT Track.md"
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text("# ZZT Track\nTracking.\n\n| x | [[ZZT Agenda\\|Agenda]] |\n")
    return p


print("1. A conforming Agenda passes every one of the nine")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root)
    for c in ["agenda_filename_valid", "agenda_in_track_folder", "agenda_required_h2s",
              "agenda_h2_order", "agenda_cadence_stated", "agenda_no_work_rows",
              "agenda_header_shape"]:
        check(c, verdict(c, f, root), "pass")
    for c in ["agenda_single_per_anchor", "agenda_track_dispatch_linked"]:
        check(c, verdict(c, root, root), "pass")

print("2. Each rule fires on its own violation")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, rel="ZZT Track/ZZT Agenda 2026.md")
    check("R-agenda-01 qualifier suffix", verdict("agenda_filename_valid", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, rel="ZZT Design/ZZT Agenda.md")
    check("R-agenda-02 in Design", verdict("agenda_in_track_folder", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, rel="ZZT Track/ZZT Agenda/ZZT Agenda.md")
    check("R-agenda-02 folder-doc form is legal",
          verdict("agenda_in_track_folder", f, root), "pass")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    build(root)
    (root / "Side").mkdir()
    (root / "Side" / "Side Agenda.md").write_text(GOOD_AGENDA)
    check("R-agenda-03 second agenda", verdict("agenda_single_per_anchor", root, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    build(root)
    nested = root / "Sub"
    nested.mkdir()
    (nested / ".anchor").write_text("slug: SUB\n")
    (nested / "SUB Agenda.md").write_text(GOOD_AGENDA)
    check("R-agenda-03 nested anchor's agenda does not count",
          verdict("agenda_single_per_anchor", root, root), "pass")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, GOOD_AGENDA.replace("## Constraints\n\nWhat bounds us.\n\n", ""))
    check("R-agenda-04 missing H2", verdict("agenda_required_h2s", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    swapped = GOOD_AGENDA.replace("## Approach", "## TMP").replace(
        "## Constraints", "## Approach").replace("## TMP", "## Constraints")
    f = build(root, swapped)
    check("R-agenda-05 shuffled order", verdict("agenda_h2_order", f, root), "fail")
    check("R-agenda-04 still sees all five", verdict("agenda_required_h2s", f, root), "pass")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, GOOD_AGENDA.replace("Revisited monthly by the ZZT pilot.",
                                        "We will revisit this when it feels stale."))
    check("R-agenda-06 no interval", verdict("agenda_cadence_stated", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, GOOD_AGENDA + "\n- **F001 — a task** [Ready] — work. ^F001\n")
    check("R-agenda-07 work row", verdict("agenda_no_work_rows", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    fenced = GOOD_AGENDA + "\n```\n- **F001 — shown, not declared** [Ready] ^F001\n```\n"
    f = build(root, fenced)
    check("R-agenda-07 fenced example is not a work row",
          verdict("agenda_no_work_rows", f, root), "pass")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, GOOD_AGENDA.replace("# ZZT Agenda", "# Agenda"))
    check("R-agenda-08 wrong H1", verdict("agenda_header_shape", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    f = build(root, GOOD_AGENDA.split("---\n", 2)[2])
    check("R-agenda-08 no frontmatter", verdict("agenda_header_shape", f, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    build(root, track=False)
    (root / "ZZT Track" / "ZZT Track.md").write_text("# ZZT Track\nTracking.\n")
    check("R-agenda-09 unlinked agenda",
          verdict("agenda_track_dispatch_linked", root, root), "fail")

print("3. The two other non-Agenda refs")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZT\ntraits: [code, doc]\n")
    check("R-code-repository-02 code trait, no key",
          verdict("no_git_probe_fallback", root, root), "fail")
    (root / ".anchor").write_text("slug: ZZT\ntraits: [code]\ncode: ~/ob/proj/zzt\n")
    check("R-code-repository-02 key present",
          verdict("no_git_probe_fallback", root, root), "pass")
    (root / ".anchor").write_text("slug: ZZT\ntraits: [doc]\n")
    check("R-code-repository-02 not a code anchor",
          verdict("no_git_probe_fallback", root, root), "pass")
    (root / ".anchor").write_text("slug: ZZT\ntraits:\n  - code\n")
    check("R-code-repository-02 block-list traits",
          verdict("no_git_probe_fallback", root, root), "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZT\n")
    pat = r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)? .+\.dmg$"
    good = root / "1.2.3 MuxUX.dmg"
    good.write_text("")
    bad = root / "MuxUX 1.2.3.dmg"
    bad.write_text("")
    check("regex_basename version-first passes", verdict("regex_basename", good, root, [pat]), "pass")
    check("regex_basename name-first fails", verdict("regex_basename", bad, root, [pat]), "fail")
    check("regex_basename with no pattern errors", verdict("regex_basename", good, root), "error")

print()
if FAILURES:
    print(f"test-t071-wired-checkers: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t071-wired-checkers: all checks pass")
