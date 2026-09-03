#!/usr/bin/env python3
"""T654 — `move --after|--before` and `new --after` accept a LABEL line's exact
text as well as a stone id; a label reference may cross a blank line; zero or
several matches refuse. Presti-shaped fixture: blank-separated stones, empty
group labels at the bottom. Run: python3 test-t654-stone-labels.py"""
import os, subprocess, sys, tempfile
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


with tempfile.TemporaryDirectory(prefix="t654-") as td:
    root = Path(td); (root / "P").mkdir()
    (root / "P" / ".anchor").write_text("slug: P\nstones:\n  pebbles:\n")
    (root / "P" / "P.md").write_text("# P\n")
    for i in range(1, 4):
        rc, out, err = run(root, "new", "P", "--line", f"stone {i}")
        assert rc == 0, err
    ctl = [p for p in root.rglob("P Pebble*.md") if p.stem in ("P Pebble", "P Pebbles")][0]
    text = ctl.read_text().rstrip("\n") + "\n\nCV NEXT:\n\nCYCLE 27:\n\nCYCLE 21:\n"
    ctl.write_text(text)
    lines = lambda: ctl.read_text().split("\n")

    print("move to a label")
    rc, out, err = run(root, "move", "P", "P0001", "--after", "CYCLE 27:")
    L = lines()
    check("move --after LABEL succeeds", rc == 0, err)
    check("stone sits directly below the label", L[L.index("CYCLE 27:") + 1].startswith("[[P P0001|-]]"), "\n".join(L))
    rc, out, err = run(root, "move", "P", "P0002", "--before", "CYCLE 27:")
    L = lines()
    check("move --before LABEL puts it directly above", rc == 0 and L[L.index("CYCLE 27:") - 1].startswith("[[P P0002|-]]"), err)
    check("no stone lost or duplicated", sum(l.startswith("[[P P000") for l in L) == 3)

    print("new into a group")
    rc, out, err = run(root, "new", "P", "--line", "stone 4", "--after", "CV NEXT:")
    L = lines()
    check("new --after LABEL lands below it", rc == 0 and L[L.index("CV NEXT:") + 1].startswith("[[P P0004|-]]"), err + out)
    check("receipt names the placement", "below 'CV NEXT:'" in out, out)
    rc, out, err = run(root, "new", "P", "--line", "stone 5", "--after", "P0004")
    L = lines()
    check("new --after ID lands below that stone", rc == 0 and L[L.index("CV NEXT:") + 2].startswith("[[P P0005|-]]"), err + out)

    print("refusals")
    n_before = len(list((root / "P").rglob("P P00*.md")))
    rc, out, err = run(root, "new", "P", "--line", "stone 6", "--after", "NOPE:")
    check("unknown label refused, candidates listed", rc != 0 and "CYCLE 27:" in err, err)
    check("nothing half-minted", len(list((root / "P").rglob("P P00*.md"))) == n_before)
    ctl.write_text(ctl.read_text() + "\nCYCLE 21:\n")
    rc, out, err = run(root, "move", "P", "P0003", "--after", "CYCLE 21:")
    check("duplicate label refused", rc != 0 and "appears 2 times" in err, err)

    print("update keeps the grouping")
    rc, out, err = run(root, "update")
    L = lines()
    check("update ran", rc == 0, err)
    check("P0001 still under CYCLE 27:", L[L.index("CYCLE 27:") + 1].startswith("[[P P0001|-]]"), "\n".join(L))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
