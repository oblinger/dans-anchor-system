#!/usr/bin/env python3
"""T064 — the read verb, and the echo that backs it up.

`state` had no read verb at all. define / set / resolve / remove are every one
of them writes, so an agent could create and mutate a row but never ask what
one currently says. That is what made a malformed row unrecoverable: `state`
refuses to edit a row its parser cannot read and tells you to fix it by hand,
R-pathguard refuses the hand edit, and the only way through was `remove` — a
HARD delete of the row AND its sub-bullets — followed by `define`, with nothing
letting you look first.

Two pieces, both agreed with Dan 2026-08-01:

  1. `show <anchor> <doc> <label>` prints the item's full markdown, sub-bullet
     span included, and does nothing else — no audit-q, no Q.md refresh, no
     Messages entry. Reading is not an event.
  2. `remove` echoes what it deleted, as a backstop for the caller who does NOT
     look first. This is why `remove --dry-run` was dropped rather than built:
     a dry run only helps someone who already suspected they needed one.

Named `show`, not `get` — `get` reads as `set`'s inverse and the symmetry fails
twice over: `set` is rows-only while `show` reads Q/V on any doc, and `set`
writes a FIELD whose true inverse returns one value, not the whole item. `get`
is left unspent for that future scriptable field read.

Run: python3 test-t064-show-verb.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STATE = Path(__file__).parent / "state"

PASS = 0
FAIL = 0


def ok(name):
    global PASS
    PASS += 1
    print(f"  PASS: {name}")


def no(name, detail=""):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


def check(name, cond, detail=""):
    ok(name) if cond else no(name, detail)


BACKLOG = """# ZZS Backlog

## Now

- **T001 — A row with sub-bullets** [Ready] — body text ^T001
  - **Next:** the concrete step with zero user involvement
  - a second sub-bullet worth keeping

- **T002 — A neighbouring row** [Ready] — must not bleed into T001's span ^T002
  - **Next:** stay out of the way

## Done
"""

DOC = """# [[ZZS]] · F001 — Fixture

Orientation.

## Open Questions
<!-- state:q zz -->

- **Q1 — a pending bullet-form question** — context.
    - **(A)** first
    - **(B)** second
    - **Recommendation:** Lean (A).

### Resolved

### Q2 — an archived question (resolved 2026-08-01)
the question text ^F001-Q2

**Resolved:** (B) — second

## Verifications

- **V1 — did the render link the doc first?** — check the queue file.

## Summary

Body.
"""


def run(home, *argv):
    env = dict(os.environ, HOME=str(home))
    p = subprocess.run([sys.executable, str(STATE), *argv],
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


with tempfile.TemporaryDirectory() as td:
    home = Path(td)
    anchor = home / "ob" / "kmr" / "ZZS"
    (anchor / "ZZS Track").mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: ZZS\n", encoding="utf-8")
    backlog = anchor / "ZZS Track" / "ZZS Backlog.md"
    backlog.write_text(BACKLOG, encoding="utf-8")
    doc = anchor / "F001 — Fixture.md"
    doc.write_text(DOC, encoding="utf-8")

    print("1. show prints a row's whole span, and stops at the next row")
    rc, out, err = run(home, "show", "ZZS", "Backlog", "T001")
    check("exits 0", rc == 0, err)
    check("row line present", "- **T001 — A row with sub-bullets**" in out)
    check("first sub-bullet present", "- **Next:** the concrete step" in out)
    check("second sub-bullet present", "a second sub-bullet worth keeping" in out)
    check("the neighbouring row does NOT bleed in", "T002" not in out, out)
    check("the locator goes to stderr, not stdout",
          "ZZS Backlog.md" in err and "ZZS Backlog.md" not in out)

    print("2. show is a READ — it changes nothing")
    before = backlog.read_text(encoding="utf-8")
    run(home, "show", "ZZS", "Backlog", "T001")
    check("backlog byte-identical after two shows",
          backlog.read_text(encoding="utf-8") == before)
    check("no integrity stamp was added by reading",
          "state:backlog" not in backlog.read_text(encoding="utf-8"))

    print("3. show reads Q and V items on any doc, in any zone")
    rc, out, _ = run(home, "show", "ZZS", "F001 — Fixture", "Q1")
    check("pending bullet-form Q1", rc == 0 and "a pending bullet-form question" in out)
    check("Q1 carries its option bullets", "**(A)** first" in out and "**(B)** second" in out)
    check("Q1 stops before the Resolved zone", "Q2" not in out and "### Resolved" not in out)
    rc, out, _ = run(home, "show", "ZZS", "F001 — Fixture", "Q2")
    # The point of reading a resolved item is not having to know it resolved.
    check("archived H3-form Q2 is reachable", rc == 0 and "an archived question" in out)
    check("Q2 carries its resolution", "**Resolved:** (B) — second" in out)
    # F305 D5 — the V<n> item namespace is retired: a verification is the
    # doc's final QUESTION, so `show <doc> V1` is an unknown kind now.
    rc, out, err = run(home, "show", "ZZS", "F001 — Fixture", "V1")
    check("V1 is an unknown kind (namespace retired, F305 D5)",
          rc != 0 and "unknown label kind" in err)

    print("4. show refuses what it cannot read")
    rc, out, err = run(home, "show", "ZZS", "Backlog", "T404")
    check("a missing label errors", rc != 0 and "T404" in err, err)
    rc, out, err = run(home, "show", "ZZS", "Backlog", "F+")
    check("a mint label is refused, and says why",
          rc != 0 and "nothing to show" in err, err)

    print("5. show declares no write flags")
    rc, _, err = run(home, "show", "ZZS", "Backlog", "T001", "--status", "Done")
    check("show REFUSES --status", rc != 0 and "unrecognized" in err, err)

    print("6. remove echoes what it deleted")
    rc, out, err = run(home, "remove", "ZZS", "Backlog", "T001", "--reason", "test")
    check("exits 0", rc == 0, err)
    check("the row line is echoed", "- **T001 — A row with sub-bullets**" in err, err)
    check("the sub-bullets are echoed too — the part a hard delete loses",
          "a second sub-bullet worth keeping" in err, err)
    check("stdout stays the status line",
          "deleted T001" in out and "sub-bullet" not in out, out)
    # T002's body mentions T001 by name, so the assertion is on the ROW header
    # — the thing remove deletes — not on the string appearing anywhere.
    check("the row really is gone",
          "- **T001 —" not in backlog.read_text(encoding="utf-8"))
    check("the neighbour survived", "T002" in backlog.read_text(encoding="utf-8"))

print(f"\ntest-t064-show-verb: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
