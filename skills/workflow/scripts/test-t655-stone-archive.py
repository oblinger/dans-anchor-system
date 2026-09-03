#!/usr/bin/env python3
"""T655 — the stone archive is one markdown file per list per MONTH
(`archive/YYYY-MM <list> archive.md`), each retired stone an `## <name>` section
and an alias; numbering comes from a `next:` counter in the control file's
frontmatter, seeded once from a scan; relocation records the old name in the
month file (no tombstone); `stone archive <list> --convert` folds the legacy
one-file-per-stone archive. Run: python3 test-t655-stone-archive.py"""
import datetime as _dt, os, re, subprocess, sys, tempfile, time
from pathlib import Path

STONE = Path(__file__).resolve().parent / "stone"
PASS = FAIL = 0
MONTH = _dt.date.today().strftime("%Y-%m")
TODAY = _dt.date.today().isoformat()


def check(label, ok, extra=""):
    global PASS, FAIL
    PASS += bool(ok); FAIL += not ok
    print(("  ok:   " if ok else "  FAIL: ") + label + (f"  [{extra}]" if extra and not ok else ""))


def run(root, *argv):
    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(STONE), *argv], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def fm_next(ctl: Path):
    m = re.search(r"^next: (\d+)$", ctl.read_text(), re.M)
    return int(m.group(1)) if m else None


def strip_next(ctl: Path):
    ctl.write_text("\n".join(l for l in ctl.read_text().splitlines() if not l.startswith("next:")) + "\n")


with tempfile.TemporaryDirectory(prefix="t655-") as td:
    root = Path(td)
    for s in ("A", "B"):
        (root / s).mkdir()
        (root / s / ".anchor").write_text(f"slug: {s}\nstones:\n  pebbles:\n  rocks:\n")
        (root / s / f"{s}.md").write_text(f"# {s}\n")
    folder = root / "A" / "A Track" / "A Pebbles"
    arch = folder / "archive"
    month_file = arch / f"{MONTH} A archive.md"

    print("counter")
    rc, out, err = run(root, "new", "A", "--line", "first")
    check("new A -> A P0001", rc == 0 and "A P0001" in out, err)
    a_ctl = folder / "A Pebbles.md"
    check("control frontmatter carries next: 2", fm_next(a_ctl) == 2, a_ctl.read_text())
    rc, out, err = run(root, "new", "A", "--line", "second", "--body", "prose of two\n\nmore prose")
    rc, out, err = run(root, "new", "A", "--line", "third")
    check("counter advances -> P0003, next: 4", "A P0003" in out and fm_next(a_ctl) == 4, out)

    print("archive verb appends to the month file")
    rc, out, err = run(root, "archive", "A", "P0002")
    check("archive P0002 exits 0 and names the month file", rc == 0 and f"{MONTH} A archive.md" in out, out + err)
    check("stone file deleted", not (folder / "A P0002.md").exists())
    check("no per-stone archive file", not (arch / "A P0002.md").exists())
    t = month_file.read_text() if month_file.is_file() else ""
    check("month file exists with H1", t.startswith("---") and f"# {MONTH} A archive" in t, t)
    check("section ## A P0002 with line::, retired::, body verbatim",
          "## A P0002\nline:: second\nretired:: " + TODAY + "\n\nprose of two\n\nmore prose" in t, t)
    check("alias registered", "aliases:\n  - A P0002\n" in t, t)
    check("no projection state in the section", "appears::" not in t and "enrolled::" not in t)
    check("own control line gone", "A P0002" not in a_ctl.read_text())
    rc, out, err = run(root, "archive", "A", "P0002")
    check("archiving again: 'already archived' (found via the month file)", rc != 0 and "already archived" in err, err)

    print("update's archive path uses the same file")
    a_ctl.write_text("\n".join(l for l in a_ctl.read_text().splitlines() if "A P0003" not in l) + "\n")
    rc, out, err = run(root, "update", "--dry-run")
    check("dry run announces the archive and writes nothing",
          rc == 0 and "would archive" in out and (folder / "A P0003.md").is_file()
          and "A P0003" not in month_file.read_text(), out)
    rc, out, err = run(root, "update")
    t = month_file.read_text()
    check("wet run appends ## A P0003 to the SAME month file (1 archived)",
          rc == 0 and "## A P0003" in t and "(1 archived)" in out and not (folder / "A P0003.md").exists(), out)
    check("aliases grow: both names", "  - A P0002\n  - A P0003\n" in t, t)
    check("exactly one archive file this month", sorted(p.name for p in arch.iterdir()) == [month_file.name])
    rc, out, err = run(root, "update")
    check("a second update recreates nothing", rc == 0 and not (folder / "A P0003.md").exists()
          and "(0 archived)" in out, out)

    print("counter never reuses a retired number")
    rc, out, err = run(root, "new", "A", "--line", "fourth")
    check("next mint is P0004", "A P0004" in out, out)
    strip_next(a_ctl)
    rc, out, err = run(root, "new", "A", "--line", "fifth")
    check("counter absent -> seeded from live files + month-file headings -> P0005",
          rc == 0 and "A P0005" in out and fm_next(a_ctl) == 6, out + err)

    print("relocation records the old name, no tombstone")
    rc, out, err = run(root, "move", "A", "P0004", "--dest", "B")
    check("move --dest B -> B P0001", rc == 0 and "A P0004 -> B P0001" in out and "recorded in archive/" in out, out + err)
    t = month_file.read_text()
    check("## A P0004 with moved:: → [[B P0001]] in A's month file",
          "## A P0004\nline:: fourth\nmoved:: " + TODAY + " → [[B P0001]]" in t and "  - A P0004\n" in t, t)
    check("no tombstone file", not (arch / "A P0004.md").exists())
    b_ctl = root / "B" / "B Track" / "B Pebbles" / "B Pebbles.md"
    check("B's counter advanced to 2", fm_next(b_ctl) == 2, b_ctl.read_text())
    rc, out, err = run(root, "new", "A", "--line", "sixth")
    check("A's numbering continues past the moved one -> P0006", "A P0006" in out, out)

    print("month rollover")
    sys.path.insert(0, str(STONE.parent))
    import importlib.machinery, importlib.util
    ld = importlib.machinery.SourceFileLoader("stone_mod", str(STONE))
    sp = importlib.util.spec_from_loader("stone_mod", ld); sm = importlib.util.module_from_spec(sp); ld.exec_module(sm)
    sm._archive_append(folder, "A", "A P0099", [("line", "old"), ("retired", "2026-01-15")], "", month="2026-01")
    check("a different month is a different file", (arch / "2026-01 A archive.md").is_file()
          and "## A P0099" in (arch / "2026-01 A archive.md").read_text())
    check("this month's file untouched by it", "A P0099" not in month_file.read_text())
    check("_is_archived sees every month file", sm._is_archived(folder, "A", "P0099") and not sm._is_archived(folder, "A", "P0042"))
    strip_next(a_ctl)
    rc, out, err = run(root, "new", "A", "--line", "seventh")
    check("seed scans every month file -> P0100", "A P0100" in out, out + err)

    print("--convert folds the legacy one-file archive")
    legacy = arch / "A P0050.md"
    legacy.write_text("line:: legacy fifty\nappears:: \n\nOld body.\n")
    when = time.mktime(_dt.datetime(2026, 7, 15, 12, 0).timetuple()); os.utime(legacy, (when, when))
    tomb = arch / "A P0051.md"
    tomb.write_text("line:: moved 2026-07-20 → [[B P0009]]\nappears:: \n\nRelocated.\n")
    when2 = time.mktime(_dt.datetime(2026, 7, 20, 12, 0).timetuple()); os.utime(tomb, (when2, when2))
    rc, out, err = run(root, "archive", "A", "--convert")
    july = arch / "2026-07 A archive.md"
    check("convert exits 0, names the month file and count", rc == 0 and "2 archived stone(s) -> archive/2026-07 A archive.md" in out, out + err)
    jt = july.read_text() if july.is_file() else ""
    check("legacy stone folded by mtime with retired:: from mtime",
          "## A P0050\nline:: legacy fifty\nretired:: 2026-07-15\n\nOld body." in jt, jt)
    check("tombstone folded too", "## A P0051" in jt and "[[B P0009]]" in jt, jt)
    check("aliases for both", "  - A P0050\n  - A P0051\n" in jt, jt)
    check("legacy files deleted", not legacy.exists() and not tomb.exists())
    rc, out, err = run(root, "archive", "A", "--convert")
    check("convert is idempotent", rc == 0 and "nothing to convert" in out, out)
    rc, out, err = run(root, "archive", "A")
    check("archive without <id> or --convert is refused", rc != 0 and "--convert" in err, err)
    rc, out, err = run(root, "update")
    check("update after everything is clean and loads no archive", rc == 0 and "(0 archived)" in out, out + err)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
