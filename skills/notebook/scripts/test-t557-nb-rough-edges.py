#!/usr/bin/env python3
"""T557 — the two `nb` rough edges A2X found in use, and the trades each fix made.

Both came from [[A2X]] 2026-08-16, a use report rather than a review: A2X013 was
at 16 cells when they were written up.

  1. **`nb mint` failed on the notebook's own `.anchor` and pointed the wrong
     way.** *".anchor at <path> declares no slug: — declare one, or pass a path
     in an anchor that does"* — advice that turns a notebook into an anchor,
     which [[DAS Notebook]] says a notebook folder must not be. HookAnchor's
     scanner mints a 0-byte `.anchor` in every namesake folder on its rescan,
     so a notebook acquires one whether or not anyone wanted it; A2X's came
     back after the first removal.

  2. **`--data` attachments landed where `.gitignore` ate them.** `.gitignore`
     line 62 is a blanket `*.csv`, so `nb append --data results.csv` reported
     success, wrote the file, and left it untracked — three true statements
     adding up to a false impression, against a facet that promises the file is
     *"stored"*.

**The trades are what this file mostly pins**, because both fixes bought
something with something:

  - Climbing past a slugless `.anchor` means an anchor relying on [[DAS Dot
    Anchor]]'s basename fallback now mints in its PARENT's namespace. §1c
    asserts that behaviour explicitly rather than leaving it to be discovered —
    for the folder that raised this, the fallback would have minted
    `A2X013 - Game Break Overview001`.
  - A warning rather than a `.gitignore` exception leaves the file untracked.
    §2d asserts the warning cannot break an append: no git, no repo, no crash.

Run: python3 test-t557-nb-rough-edges.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NB = Path(__file__).resolve().parent / "nb"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def run(*args, cwd=None):
    r = subprocess.run([sys.executable, str(NB), *args],
                       capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def anchor(root, slug=None):
    (root / ".anchor").write_text(f"slug: {slug}\n" if slug else "")


print("1. `nb mint` walks past a slugless `.anchor`")
with tempfile.TemporaryDirectory() as td:
    root = Path(td) / "anchor"
    nbdir = root / "ZZ Notebook" / "ZZ013 - A Test"
    nbdir.mkdir(parents=True)
    anchor(root, "ZZ")
    anchor(nbdir)                      # the 0-byte one the scanner mints
    rc, out, err = run("mint", str(nbdir))
    check("1a. it succeeds where it used to die", rc, 0)
    check("...and mints in the ENCLOSING anchor's namespace", out, "ZZ014")
    # 1b — the same folder with no stray `.anchor` must give the same answer,
    # or the fix would be reading the stray file rather than ignoring it.
    (nbdir / ".anchor").unlink()
    rc2, out2, _ = run("mint", str(nbdir))
    check("1b. the stray file changes nothing", (rc2, out2), (0, "ZZ014"))

print("1c. The trade: the basename fallback is refused, not honoured")
with tempfile.TemporaryDirectory() as td:
    # [[DAS Dot Anchor]] lets a slug fall back to the folder basename. `nb`
    # deliberately does NOT: for this folder the fallback would mint
    # `A2X013 - Game Break Overview001`. Asserted so the choice is visible.
    root = Path(td) / "outer"
    inner = root / "A2X013 - Game Break Overview"
    inner.mkdir(parents=True)
    anchor(root, "A2X")
    anchor(inner)
    rc, out, _ = run("mint", str(inner))
    check("the basename is NOT used as a slug", out.startswith("A2X"), True)
    check("...and the answer is the parent anchor's", out, "A2X014")

print("1d. A walk that finds no slug at all names what it passed")
with tempfile.TemporaryDirectory() as td:
    inner = Path(td) / "orphan" / "inner"
    inner.mkdir(parents=True)
    anchor(inner.parent)
    anchor(inner)
    rc, out, err = run("mint", str(inner))
    check("it still fails", rc, 1)
    check("...naming the slugless anchors it passed", "passed" in err, True)
    check("...and the remedy is deleting a stray file, NOT declaring a slug "
          "on the notebook", "delete a stray" in err, True)
    check("...the old misdirecting advice is gone",
          "declare one, or pass a path in an anchor that does" in err, False)

print("2. `nb append` warns when a stored file is gitignored")
if shutil.which("git") is None:
    print("  -- git not available; §2 skipped")
else:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "anchor"
        (root / "ZZ Notebook").mkdir(parents=True)
        anchor(root, "ZZ")
        subprocess.run(["git", "init", "-q", "."], cwd=root, check=True)
        (root / ".gitignore").write_text("*.csv\n")
        data = Path(td) / "results.csv"
        data.write_text("a,b\n1,2\n")
        keep = Path(td) / "notes.txt"
        keep.write_text("x\n")
        nbdir = root / "ZZ Notebook" / "ZZ013 - A Test"
        rc, out, err = run("append", str(nbdir), "--title", "First",
                           "--data", str(data), "--data", str(keep))
        check("2a. the append still succeeds", rc, 0)
        check("...and the cell was really written",
              (nbdir / "ZZ013-001 First.md").is_file(), True)
        check("2b. the ignored file is named", "results.csv" in err, True)
        check("...and the tracked one is NOT — this is not a blanket warning",
              "notes.txt" in err, False)
        check("2c. it says what the silence would have cost",
              "never versioned" in err, True)
        # Both files are on disk either way — the warning is about tracking,
        # so the assertion has to be that nothing was withheld.
        check("...and BOTH files were stored regardless",
              ((nbdir / "ZZ013-001 results.csv").is_file(),
               (nbdir / "ZZ013-001 notes.txt").is_file()), (True, True))

    with tempfile.TemporaryDirectory() as td:
        # 2d — outside a repo `git check-ignore` fails. A missing warning must
        # never cost someone their append.
        root = Path(td) / "anchor"
        (root / "ZZ Notebook").mkdir(parents=True)
        anchor(root, "ZZ")
        data = Path(td) / "d.csv"
        data.write_text("a\n")
        nbdir = root / "ZZ Notebook" / "ZZ013 - A Test"
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(td))
        r = subprocess.run([sys.executable, str(NB), "append", str(nbdir),
                            "--title", "First", "--data", str(data)],
                           capture_output=True, text=True, env=env)
        check("2d. outside a git repo the append succeeds", r.returncode, 0)
        check("...and the file is stored",
              (nbdir / "ZZ013-001 d.csv").is_file(), True)

print()
if FAILURES:
    print(f"test-t557-nb-rough-edges: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t557-nb-rough-edges: all checks pass")
