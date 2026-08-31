#!/usr/bin/env python3
"""test-t276-dated.py — ATT T276: the stone engine reads DATE-NAMED members.

`stone-kinds.py` has accepted `member: dated` since the kind table was written,
and `book` declares it — but the engine implemented only the numbered shape, so
`classify_line` returned ('other',) for every book line, `_is_stone_target`
matched a pattern an empty prefix and zero digits can never satisfy, and
`stone book new` had no dated path at all. Tool and rule contradicted each
other and `stone update` walked past all 14 live book members in silence.

The load-bearing design call this file pins down is IDENTITY. A numbered stone
carries its owner in the link target (`[[A R0001]]`); a dated one cannot,
because its name is a date and a title and nothing else. The owner therefore
comes from the rendered ALIAS (`[[2026-07-26 Fellows|A:]]`), never from
"whichever file the line sits in" — case D is the reason: a published stone
propagates into OTHER anchors' control files, where the file-based rule would
silently reattribute it to the consumer on the first pass.

Fixture is a two-anchor DAG B ← A ("B feeds from A"), built fresh per run in a
tempdir; every call passes --root explicitly, so the real vault is never read.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("stone_mod", str(HERE / "stone"))
_spec = importlib.util.spec_from_loader("stone_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["stone_mod"] = st
_loader.exec_module(st)
st._LINE_MAX_CACHE = 0  # hermetic: no line budget in fixtures
st._GLOBAL_STONES_CACHE = {}  # hermetic: kind-table mode regardless of user config (F628 step 4)

CFG = st.load_kind_config()["book"]
NUM = st.load_kind_config()["rock"]

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"  PASS: {msg}")


def no(msg):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {msg}")


def mkanchor(root, slug, feeds):
    d = root / slug
    d.mkdir(parents=True, exist_ok=True)
    feeds_line = f"feeds: {', '.join(feeds)}" if feeds else "feeds:"
    (d / ".anchor").write_text(f"slug: {slug}\n{feeds_line}\n", encoding="utf-8")
    return d


def control_path(root, slug):
    return st._control_path(root / slug, slug, CFG)


def folder(root, slug):
    return st._stone_folder(root / slug, slug, CFG)


def run(root, *argv):
    return st.main(["stone", *argv, "--root", str(root)])


def capture(root, *argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run(root, *argv)
    return buf.getvalue()


def fails(root, *argv):
    """(rc, stderr) — a refusal must SAY why, so both halves are asserted."""
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        rc = run(root, *argv)
    return rc, buf.getvalue()


SID = "2026-07-26 Fellows application"


def build(tmp):
    root = Path(tmp)
    mkanchor(root, "A", [])
    mkanchor(root, "B", ["A"])
    return root


# ============================================================
# A. the mint writes a date-named file and a control line that names its owner
# ============================================================
def case_a():
    print("\nA. dated mint")
    with tempfile.TemporaryDirectory() as tmp:
        root = build(tmp)
        run(root, "book", "new", "A", "--line", "Fellows application — all stages complete",
            "--title", "Fellows application", "--date", "2026-07-26")

        f = folder(root, "A") / f"{SID}.md"
        if f.is_file():
            ok("the member file is named `YYYY-MM-DD {Title}` with no slug in it")
        else:
            no(f"expected {f}, folder holds {[p.name for p in folder(root, 'A').glob('*.md')]}")

        body = control_path(root, "A").read_text(encoding="utf-8")
        want = f"[[{SID}|-]]"
        if want in body:
            ok("the control line targets the bare dated name; on the owner's own page "
               "the alias is the dash (the owner IS the page — 2026-08-30)")
        else:
            no(f"{want!r} not in control file:\n{body}")
        # The dash reads back to the owner only when the reader says whose
        # page it is — without a host it is nobody's, never a guess.
        line = next(l for l in body.splitlines() if want in l)
        with_host = st.classify_line(line, CFG, "A")
        without = st.classify_line(line, CFG)
        if with_host[:3] == ("stone", "A", SID) and without[0] == "other":
            ok("a dashed dated line is A's when read as A's page, and unowned when read blind")
        else:
            no(f"dash read-back: with host {with_host!r}, without {without!r}")


# ============================================================
# B. the line reads back — target alone is not enough, the alias supplies identity
# ============================================================
def case_b():
    print("\nB. read-back")
    line = st.render_stone_line("A", SID, "some text", CFG)
    cls = st.classify_line(line, CFG)
    if cls == ("stone", "A", SID, "some text"):
        ok("classify_line round-trips a dated line to (owner, sid, text)")
    else:
        no(f"classify_line returned {cls!r}")

    bare = f"[[{SID}]] some text"
    if st.classify_line(bare, CFG)[0] == "other":
        ok("a dated link with NO alias is not a stone — identity is required, never guessed")
    else:
        no("a dated link without an alias was classified as a stone")

    if st.classify_line(f"[[{SID}|A:]] x", NUM)[0] == "other":
        ok("a numbered kind still refuses a dated target — the widening is per-kind")
    else:
        no("the dated shape leaked into the numbered kind")


# ============================================================
# C. the folder note is not a member (the dated echo of the `HBR Rocks.md` bug)
# ============================================================
def case_c():
    print("\nC. the control file is not one of its own members")
    with tempfile.TemporaryDirectory() as tmp:
        root = build(tmp)
        run(root, "book", "new", "A", "--line", "x", "--title", "Fellows application",
            "--date", "2026-07-26")
        # `book` is container-named, so the control file sits INSIDE the folder.
        cp = control_path(root, "A")
        if cp.parent == folder(root, "A"):
            ok("the control file is the folder note, as the container-named kind requires")
        else:
            no(f"control {cp} is not inside {folder(root, 'A')}")
        names = {f.stem for f in st._stone_files(folder(root, "A"), "A", CFG)}
        if names == {SID}:
            ok("_stone_files sees the member and never the folder note")
        else:
            no(f"_stone_files returned {names!r}")


# ============================================================
# D. one hop — the owner survives propagation into a file it does not own
# ============================================================
def case_d():
    print("\nD. propagation keeps the owner")
    with tempfile.TemporaryDirectory() as tmp:
        root = build(tmp)
        run(root, "book", "new", "A", "--line", "Fellows application", "--title",
            "Fellows application", "--date", "2026-07-26")
        # Publish: put A's own self-section header above the line.
        cp = control_path(root, "A")
        lines = cp.read_text(encoding="utf-8").splitlines()
        idx = st._content_start(lines)
        lines.insert(idx, st._render_header("A", CFG))
        cp.write_text("\n".join(lines) + "\n", encoding="utf-8")

        run(root, "book", "update")
        downstream = control_path(root, "B").read_text(encoding="utf-8")
        if f"[[{SID}|A:]]" in downstream:
            ok("the stone reached B's control file still attributed to A")
        else:
            no(f"not propagated, or reattributed:\n{downstream}")

        # The identity claim, stated as a test: re-reading B's copy must still
        # say A. This is what a file-based owner rule would get wrong.
        for l in downstream.splitlines():
            c = st.classify_line(l, CFG)
            if c[0] == "stone" and c[2] == SID:
                if c[1] == "A":
                    ok("re-reading the downstream copy still names A as owner")
                else:
                    no(f"downstream copy reads owner {c[1]!r}, not 'A'")
                break
        else:
            no("no stone line found in B's control file")


# ============================================================
# E. refusals — a dated mint needs a title, and the date must be a date
# ============================================================
def case_e():
    print("\nE. refusals")
    with tempfile.TemporaryDirectory() as tmp:
        root = build(tmp)
        rc, err = fails(root, "book", "new", "A", "--line", "x")
        if rc != 0 and "--title" in err:
            ok("a dated mint with no --title is refused, naming --title")
        else:
            no(f"rc={rc} err={err!r}")

        rc, err = fails(root, "book", "new", "A", "--line", "x", "--title", "T",
                        "--date", "26-07-2026")
        if rc != 0 and "YYYY-MM-DD" in err:
            ok("a malformed --date is refused, naming the shape")
        else:
            no(f"rc={rc} err={err!r}")

        rc, err = fails(root, "book", "new", "A", "--line", "x", "--title", "a/b")
        if rc != 0 and "filename" in err:
            ok("a title carrying a path separator is refused — the title IS the filename")
        else:
            no(f"rc={rc} err={err!r}")


# ============================================================
# F. a slug with a space can own a DATED stone, though never a numbered one
# ============================================================
def case_f():
    print("\nF. owner round-trip is per-kind")
    try:
        st._reject_unroundtrippable_owner("HUD 1", CFG)
        ok("a spaced slug may own a dated stone — its alias round-trips")
    except st.StoneError as e:
        no(f"dated owner refused: {e}")
    try:
        st._reject_unroundtrippable_owner("HUD 1", NUM)
        no("a spaced slug was allowed to own a NUMBERED stone")
    except st.StoneError:
        ok("a spaced slug still cannot own a numbered stone — target parsing needs it")


def main():
    for c in (case_a, case_b, case_c, case_d, case_e, case_f):
        c()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
