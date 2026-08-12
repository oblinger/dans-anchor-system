#!/usr/bin/env python3
"""test-t231-vault-requires-write.py — the wide invocation reports; the narrow one writes.

`spine fix --vault` used to WRITE unless given `--dry-run`, and [[TINK319 - Spine
Agenda|F319]] calls the vault measurement "the dry run" in half a dozen places. On
2026-08-11 an agent read that prose, ran the command it names, and wrote **1,296
files** across the vault with no user go — the single action M5 is gated on. The
only signal that it had written rather than reported was one word in the summary
line, `fixed` versus `would fix`.

The second-order damage was worse than the writes: HookAnchor's daemon wakes on
every touched page and re-harvests descriptions, so a mass touch of entry pages
became a mass rewrite of **16 `.anchor` files** — content this script's own guard
explicitly refuses to touch. A guard the tool honours can still be defeated by a
second actor one cycle later.

T231's fix inverts the default at vault scale only: `--vault` reports unless
`--write`, a path writes unless `--dry-run`. The asymmetry is deliberate — one
file's diff is inspectable and 1,296 are not — and this file asserts both halves,
because making everything report-only would have been the easy over-correction and
would have broken the on-write hook path.

Usage: python3 test-t231-vault-requires-write.py
"""
import importlib.util
import io
import sys
import contextlib
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0

# S05: a blank line between the H1 and its orientation line. The masthead is NOT
# decoration here — without one the classifier reads the page as spine-less and
# returns `ok, already conforming`, which is how the first cut of this file got a
# green control assertion on a fixture that could not be fixed.
DIRTY = ("---\ndescription: d\n---\n\n"
         "| -[[Page]]- | : d<br>\u2192 [[X]] \u2192 [Page](hook://p/Page)  |\n"
         "| --- | --- |\n| ... |  |\n\n"
         "# Page\n\nThe orientation line.\n\nBody.\n")


def _load():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("spine_fix", HERE / "spine_fix.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["spine_fix"] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


def run(m, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main(argv)
    return rc, buf.getvalue()


def fixture():
    d = Path(tempfile.mkdtemp())
    p = d / "Page.md"
    p.write_text(DIRTY, encoding="utf-8")
    return p


def main():
    m = _load()

    # 0 — the fixture is genuinely fixable, or every assertion below is vacuous.
    p = fixture()
    action, note, new = m.plan_file(p)
    check(action == "fixed" and new != DIRTY,
          "fixture is genuinely fixable (control) — plan_file returns a rewrite")

    # 1 — a PATH argument still writes by default. The on-write hook path depends
    #     on this; making everything report-only is the easy over-correction.
    p = fixture()
    run(m, [str(p)])
    check(p.read_text() != DIRTY, "a path argument still WRITES by default")

    # 2 — a path with --dry-run still does not write (control, unchanged).
    p = fixture()
    _, out = run(m, [str(p), "--dry-run"])
    check(p.read_text() == DIRTY, "a path with --dry-run does not write")
    check("would fix" in out, "the dry-run summary says `would fix`")

    # 3 — THE T231 CHANGE. `--vault` alone must not write. Asserted through the
    #     summary verb and the explicit banner, since running the real vault sweep
    #     inside a test is precisely the thing that must never happen by accident.
    src = (HERE / "spine_fix.py").read_text()
    check("if a.vault and not write:" in src and "REPORTS ONLY" in src,
          "`--vault` without --write prints the REPORTS-ONLY banner")
    check('write = a.write and not a.dry_run if a.vault else not a.dry_run' in src,
          "the write decision is one expression: vault opts IN, a path opts OUT")
    check("if write:" in src and "if not a.dry_run:\n                f.write_text" not in src,
          "the write site is gated on `write`, not on `not dry_run`")

    # 4 — the contradiction is refused rather than silently resolved. Whichever way
    #     it resolved, half the users would be surprised.
    try:
        run(m, ["--vault", "--write", "--dry-run"])
        check(False, "--write with --dry-run is refused")
    except SystemExit as e:
        check(e.code == 2, "--write with --dry-run exits 2 (argparse error)")

    # 5 — `--write` is documented as vault-only, so nobody reads it as a general
    #     force flag they should be adding everywhere.
    check("ignored for" in src and "which write by default" in src,
          "--write's help says it is meaningless for path arguments")

    # 6 — the module docstring names the new grammar. The old one said
    #     `spine fix <paths|--vault> [--dry-run]`, which is exactly the sentence
    #     that made the destructive invocation the short one.
    check("--vault [--write]" in (m.__doc__ or ""),
          "the docstring states the two-default grammar")
    check("REPORTS" in (m.__doc__ or "").upper(),
          "the docstring says --vault reports")

    print("-" * 40)
    print(f"T231 vault requires --write: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
