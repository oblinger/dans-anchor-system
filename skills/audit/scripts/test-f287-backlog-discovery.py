#!/usr/bin/env python3
"""F287 — backlog discovery is an opt-in, and its residue is asserted.

The property under test: creating `{slug} Track/{slug} Backlog.md` IS the act
of opting into queue tracking (Q1, Dan 2026-07-30). Discovery therefore keys on
that exact structure, and anything that neither opts in nor carries a named
reason becomes a C52 finding instead of a silent `continue` — the bare skip
that let Disk's twelve rows disappear.

The tests weight two things over raw coverage:

  1. **What must NOT fire.** A rule this broad dies by false positives. An empty
     freshly-scaffolded backlog, a corpus fixture, and the backlog facet spec
     must all stay silent, or C52 becomes noise people skim past.
  2. **Slug agreement.** The whole point of tightening `endswith("Track")` to
     `== f"{slug} Track"` is that a folder merely ending in "Track" is not a
     declaration by the anchor that names the file.

Run: python3 test-f287-backlog-discovery.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "aq", Path(__file__).resolve().parent / "audit-q.py")
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


BACKLOG = "# {slug} Backlog\n\n## Now\n- **F001 — a thing** [Ready] — body ^F001\n"
EMPTY = "# {slug} Backlog\n"
NO_H1 = "## Now\n- **F001 — a thing** [Ready] — body ^F001\n"
ORPHAN_ROWS = "# {slug} Backlog\n\n## Notes on process\n- **F001 — a thing** [Ready] — body ^F001\n"


def write(root, rel, text, slug="ZZ"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.format(slug=slug), encoding="utf-8")
    return p


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # --- the opt-in itself -------------------------------------------
        p = write(root, "ZZ/ZZ Track/ZZ Backlog.md", BACKLOG)
        check("opted in + well-formed renders", aq.classify_backlog(p)[0], "render")

        p = write(root, "YY/YY Plan/YY Backlog.md", BACKLOG, slug="YY")
        check("legacy `{slug} Plan/` still renders", aq.classify_backlog(p)[0], "render")

        # --- slug must agree: the reason for tightening endswith() ---------
        # These two are deliberately unclassified, so they are removed straight
        # after: later cases assert on vault-WIDE C52 counts, and a leftover
        # unclassified file would silently inflate every one of them.
        p = write(root, "ZZ/Some Other Track/ZZ Backlog.md", BACKLOG)
        check("folder merely ENDING in 'Track' is not an opt-in",
              aq.classify_backlog(p)[0], "unclassified")
        p.unlink()

        p = write(root, "ZZ/QQ Track/ZZ Backlog.md", BACKLOG)
        check("a different slug's Track folder is not ZZ's opt-in",
              aq.classify_backlog(p)[0], "unclassified")
        p.unlink()

        # --- the Disk failure, which used to be silent ---------------------
        p = write(root, "Disk/Disk Docs/Disk Backlog.md", BACKLOG, slug="Disk")
        check("misplaced real queue is unclassified, not dropped",
              aq.classify_backlog(p)[0], "unclassified")
        f = aq.check_c52_unclassified_backlog(root)
        check("...and C52 reports it", len(f), 1)
        check("...naming the file", "Disk Backlog.md" in f[0].message, True)
        check("...and the remedy", "Disk Track/Disk Backlog.md" in f[0].message, True)
        check("...not auto-fixable (the remedy is a judgement call)",
              f[0].mechanically_fixable, False)
        p.unlink()

        # --- structural verification of an opted-in file -------------------
        p = write(root, "NN/NN Track/NN Backlog.md", NO_H1, slug="NN")
        v, reason = aq.classify_backlog(p)
        check("opted in with no H1 is malformed", v, "malformed")
        check("...and says why", reason, "no H1")
        p.unlink()

        p = write(root, "OO/OO Track/OO Backlog.md", ORPHAN_ROWS, slug="OO")
        v, reason = aq.classify_backlog(p)
        check("rows under no recognised horizon are malformed", v, "malformed")
        check("...and counts them", "1 row(s)" in (reason or ""), True)
        p.unlink()

        # --- what must NOT fire --------------------------------------------
        p = write(root, "SS/SS Track/SS Backlog.md", EMPTY, slug="SS")
        check("empty freshly-scaffolded backlog renders, silently",
              aq.classify_backlog(p)[0], "render")
        check("...and produces no C52 noise",
              len(aq.check_c52_unclassified_backlog(root)), 0)

        p = write(root, "warden/Warden Corpus/cases/c1/fixture/FX9 Backlog.md",
                  BACKLOG, slug="FX9")
        check("corpus fixture is a named non-queue",
              aq.classify_backlog(p), ("not-a-queue", "fixture"))

        p = write(root, "dans-anchor-system/facets/DAS Backlog.md", BACKLOG, slug="DAS")
        check("backlog facet spec is a named non-queue",
              aq.classify_backlog(p), ("not-a-queue", "facet-spec"))

        # No suppression list on the render path (Dan 2026-07-30): "it is
        # documentation" is not a basis for hiding a queue. Staleness is a
        # separate, general masking concern.
        p = write(root, "dans-anchor-system/examples/HH/HH Track/HH Backlog.md",
                  BACKLOG, slug="HH")
        check("an example anchor that opted in renders like any other",
              aq.classify_backlog(p)[0], "render")

        check("no C52 findings from any named non-queue",
              len(aq.check_c52_unclassified_backlog(root)), 0)

        # --- retired machinery stays retired --------------------------------
        check("SUBPROJECT_QUEUES allowlist is gone",
              hasattr(aq, "SUBPROJECT_QUEUES"), False)
        check("F107 depth rule is gone",
              hasattr(aq, "_is_ska_subskill"), False)

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: {', '.join(FAILURES)}")
        return 1
    print("all F287 assertions pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
