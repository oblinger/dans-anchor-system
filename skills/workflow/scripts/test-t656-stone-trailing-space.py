#!/usr/bin/env python3
"""T656 — a trailing space is not a diff. R-markdown-16 pads a terminal link
with one trailing space on whichever file it last touched; stone compared
byte-for-byte and reported the stone UNADJUDICATED on every pass (ATT drop
2026-09-03). Run: python3 test-t656-stone-trailing-space.py"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STONE = Path(__file__).resolve().parent / "stone"
fails = 0


def check(label, ok, extra=""):
    global fails
    print(("  ok:   " if ok else "  FAIL: ") + label + ("" if ok else f"\n        {extra[:600]}"))
    fails += 0 if ok else 1


def run(root, *argv):
    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(STONE), *argv], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


with tempfile.TemporaryDirectory(prefix="t656-") as td:
    root = Path(td)
    (root / "A").mkdir()
    (root / "A" / ".anchor").write_text("slug: A\nstones:\n  pebbles:\n  rocks:\n")
    (root / "A" / "A.md").write_text("# A\n")
    folder = root / "A" / "A Track" / "A Pebbles"
    rc, out, err = run(root, "new", "A", "--line", "chase the link [[A]]")
    check("new stone whose line ends in a link", rc == 0 and "A P0001" in out, err)
    rc, out, err = run(root, "update")
    check("first update is clean", rc == 0 and "UNADJUDICATED" not in out + err, out + err)
    ctl = folder / "A Pebbles.md"
    stone = folder / "A P0001.md"

    print("pad the projection (what R-markdown-16 does to the control file)")
    lines = ctl.read_text().splitlines()
    idx = next(i for i, l in enumerate(lines) if "A P0001" in l and "[[A]]" in l)
    lines[idx] = lines[idx].rstrip() + " "
    ctl.write_text("\n".join(lines) + "\n")
    before = stone.read_text()
    rc, out, err = run(root, "update")
    check("no UNADJUDICATED, no replaced, no conflict", rc == 0 and not any(w in out + err for w in ("UNADJUDICATED", "replaced", "CONFLICT")), out + err)
    check("stone file untouched", stone.read_text() == before)
    check("padded projection left alone (resync does not fight the pad)", ctl.read_text().splitlines()[idx].endswith("[[A]] "), ctl.read_text())

    print("pad the stone's own line:: instead")
    ctl.write_text("\n".join(l.rstrip() for l in ctl.read_text().splitlines()) + "\n")
    s = stone.read_text().replace("line:: chase the link [[A]]", "line:: chase the link [[A]] ", 1)
    check("fixture: stone line:: padded", s != stone.read_text()); stone.write_text(s)
    rc, out, err = run(root, "update")
    check("still no UNADJUDICATED / replaced / conflict", rc == 0 and not any(w in out + err for w in ("UNADJUDICATED", "replaced", "CONFLICT")), out + err)

    print("a real edit still propagates")
    lines = ctl.read_text().splitlines()
    idx = next(i for i, l in enumerate(lines) if "A P0001" in l)
    lines[idx] = lines[idx].replace("chase the link", "follow the link")
    ctl.write_text("\n".join(lines) + "\n")
    os.utime(ctl, None)
    rc, out, err = run(root, "update")
    check("edited projection reaches the stone", "follow the link" in stone.read_text(), out + err + stone.read_text())

print(f"\n{'PASS' if not fails else 'FAIL'} — {fails} failing")
sys.exit(1 if fails else 0)
