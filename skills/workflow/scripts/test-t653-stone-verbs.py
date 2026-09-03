#!/usr/bin/env python3
"""T653 — stone verbs: move --dest relocates with a new number, links
following and the old number retired by a tombstone; share/--recall replace
push/recall and take a dotted list; archive is a verb refusing on a shared
stone unless --force; --root is off the figure and $ANCHOR_VAULT_ROOT drives
every call here. Run: python3 test-t653-stone-verbs.py"""
import os, re, subprocess, sys, tempfile
from pathlib import Path

STONE = Path(__file__).resolve().parent / "stone"
PASS = FAIL = 0


def check(label, ok, extra=""):
    global PASS, FAIL
    PASS += bool(ok); FAIL += not ok
    print(("  ok:   " if ok else "  FAIL: ") + label + (f"  [{extra}]" if extra and not ok else ""))


def run(root, *argv):
    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(STONE), *argv], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def one(root, pattern):
    hits = [p for p in root.rglob(pattern) if "archive" not in p.parts]
    assert len(hits) == 1, (pattern, hits)
    return hits[0]


with tempfile.TemporaryDirectory(prefix="t653-") as td:
    root = Path(td)
    for s in ("A", "B"):
        (root / s).mkdir()
        (root / s / ".anchor").write_text(f"slug: {s}\nstones:\n  pebbles:\n  rocks:\n")
        (root / s / f"{s}.md").write_text(f"# {s}\n")
    print("mint")
    rc, out, err = run(root, "new", "A", "--line", "first — [[A P0001|First]]")
    check("new A -> A P0001", rc == 0 and "A P0001" in out, err)
    rc, out, err = run(root, "new", "A", "--line", "second — [[A P0002|Second]]")
    check("new A -> A P0002", rc == 0 and "A P0002" in out, err)
    note = root / "A" / "note.md"; note.write_text("see [[A P0002]] and [[A P0002|alias]]\n")
    a_ctl = one(root, "A Pebble*.md"); a_ctl = [p for p in root.rglob("A Pebble*.md") if p.stem in ("A Pebble", "A Pebbles")][0]

    print("share")
    rc, out, err = run(root, "share", "A", "P0001", "--with", "B")
    b_ctl = [p for p in root.rglob("B Pebble*.md") if p.stem in ("B Pebble", "B Pebbles")]
    check("share --with B lands a line", rc == 0 and b_ctl and "A P0001" in b_ctl[0].read_text(), err)
    p1 = one(root, "A P0001.md")
    check("enrolled:: B recorded", "enrolled:: B" in p1.read_text())
    rc, out, err = run(root, "share", "A", "P0001", "--with", "B.rocks")
    b_rocks = [p for p in root.rglob("B Rock*.md") if p.stem in ("B Rock", "B Rocks")]
    check("share --with B.rocks lands on the named list", rc == 0 and b_rocks and "A P0001" in b_rocks[0].read_text(), err)
    check("enrolled:: carries B.rocks", "B.rocks" in p1.read_text())
    rc, out, err = run(root, "update")
    check("update keeps the dotted appearance", rc == 0 and "A P0001" in b_rocks[0].read_text(), err)
    rc, out, err = run(root, "share", "A", "P0001", "--recall", "B.rocks")
    check("share --recall B.rocks removes it", rc == 0 and "A P0001" not in b_rocks[0].read_text(), err)
    rc, out, err = run(root, "push", "A", "P0001", "--to", "B")
    check("push is no longer a verb", rc != 0)

    print("archive")
    rc, out, err = run(root, "archive", "A", "P0001")
    check("archive refuses a shared stone, naming share --recall", rc != 0 and "share" in err, err)
    rc, out, err = run(root, "archive", "A", "P0001", "--force")
    arch1 = root / "A" / "A Track" / "A Pebbles" / "archive" / "A P0001.md"
    check("archive --force withdraws and archives", rc == 0 and arch1.is_file() and "withdrawn from B" in out, err)
    check("own control line gone", "A P0001" not in a_ctl.read_text())
    check("B's line gone", "A P0001" not in b_ctl[0].read_text())

    print("move --dest")
    rc, out, err = run(root, "move", "A", "P0002", "--dest", "B", "--to-bottom")
    check("move --dest B succeeds", rc == 0 and "A P0002 -> B P0001" in out, err + out)
    newp = root / "B" / "B Track" / "B Pebbles" / "B P0001.md"
    check("file lives under B as B P0001", newp.is_file())
    check("links followed", note.read_text() == "see [[B P0001]] and [[B P0001|alias]]\n", note.read_text())
    tomb = root / "A" / "A Track" / "A Pebbles" / "archive" / "A P0002.md"
    check("tombstone retires A P0002", tomb.is_file() and "[[B P0001]]" in tomb.read_text())
    check("A control no longer names P0002", "A P0002" not in a_ctl.read_text())
    check("B control names B P0001", "B P0001" in b_ctl[0].read_text())
    check("new stone appears:: B only", "appears:: B" in newp.read_text() and "enrolled" not in newp.read_text())
    rc, out, err = run(root, "new", "A", "--line", "third")
    check("A's next number skips both retired ones -> P0003", rc == 0 and "A P0003" in out, out + err)
    rc, out, err = run(root, "update")
    check("update after relocation is clean", rc == 0, err)
    rc, out, err = run(root, "move", "B", "P0001", "--dest", "B")
    check("--dest onto the same list is refused", rc != 0 and "already lives" in err, err)
    rc, out, err = run(root, "move", "B", "P0001")
    check("move without place or --dest is refused", rc != 0)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
