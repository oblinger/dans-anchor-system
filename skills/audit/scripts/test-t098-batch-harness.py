#!/usr/bin/env python3
"""T098 — one undecodable byte must not take down the whole audit.

`audit-plan.py --batch ~/ob/kmr --run --json` had never once completed. It died
at the FIRST non-UTF-8 byte in the vault — a single 0xbb in one doc — with
`UnicodeDecodeError`, which is a `ValueError` and so walked straight through
every `except OSError` guard in the file. The failure is at PLAN time, inside
`match_targets`, which sits OUTSIDE `run_checker`'s per-checker `except
Exception`, so it aborted the run rather than costing one verdict.

The consequence was not one missing verdict either. It meant the audit had no
vault-wide harness at all, so every measurement of a checker change had to be
hand-scoped against each rule's `where::` — which is how F296 published two
verdict counts (52, then 56) that were wrong before they were right.

The second half is a directory named `*.md`: the vault has one (`SV/ww/2025
bzz.md`), and reading it raises `IsADirectoryError` at the same plan-time site.

    python3 test-t098-batch-harness.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    # A doc whose bytes are not valid UTF-8. 0xbb is the real byte that stopped
    # the real run (a Windows-1252 right guillemet).
    bad = root / "bad.md"
    bad.write_bytes("# Head\nOrientation » here.\n".encode("cp1252"))
    good = root / "good.md"
    good.write_text("# Head\nOrientation line.\n", encoding="utf-8")

    check("a non-UTF-8 doc decodes instead of raising",
          ap._read(bad).startswith("# Head"), True)
    check("the undecodable byte becomes U+FFFD, not a structural character",
          "�" in ap._read(bad), True)
    # The point of REPLACE over ignore/strict: structure must be unchanged, so a
    # checker reaches the same verdict it would on a clean file.
    check("...and structure is untouched — the H1 is still found at line 0",
          ap._first_h1(ap._read(bad)), (0, "Head"))
    check("a clean doc is byte-identical through the same path",
          ap._read(good), "# Head\nOrientation line.\n")

    # A DIRECTORY whose name ends `.md` — the vault has one.
    dirmd = root / "notes.md"
    dirmd.mkdir()

    scope = [good, bad, dirmd]
    hit = ap.match_targets("sentinel", r"^# Head", scope, root)
    check("a sentinel scan skips a directory named `*.md` rather than dying",
          sorted(p.name for p in hit), ["bad.md", "good.md"])
    check("...and the non-UTF-8 doc still MATCHES — skipping is not suppression",
          bad in hit, True)

    # A sentinel that matches nothing still returns cleanly over the same scope.
    check("a non-matching sentinel returns empty, not an exception",
          ap.match_targets("sentinel", r"^ZZZ-no-such", scope, root), [])

    # OSError is still allowed through: a MISSING file is a fault to surface,
    # not a fault to swallow. This is the line between a guard and a fallback.
    missing = root / "nope.md"
    try:
        ap._read(missing)
        check("a missing file still raises (guard, not fallback)", "no raise", "FileNotFoundError")
    except FileNotFoundError:
        check("a missing file still raises (guard, not fallback)", True, True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
