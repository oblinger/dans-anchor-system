#!/usr/bin/env python3
"""test-f628-lists.py — F628 migration step 1: named stone lists.

Registry parse, dotted addressing, dotless resolution, the transition
fallback to the kind table, and placement overrides honored by every verb
INCLUDING the update walk (a walk reading a relocated list's old path would
see every stone missing from its own control file and archive the lot).

Fixtures only; never touches the real vault (`--root <tempdir>`), and the
user's global `stones:` config section is neutralized up front so results do
not depend on this machine.

  A. parse_address     — bare / dotted / spaced-slug / non-list-tail forms.
  B. registry parse    — `_` designation, empty entry, field entry; malformed
                          names and non-string `_` refused.
  C. bare mint         — no registry anywhere: bare `Anchor` resolves to the
                          system dotless type (pebble), legacy paths.
  D. `_` designation   — a registry `_: rock` makes bare `Anchor` mint rocks.
  E. dotted mint       — `Anchor.rock` reaches the kind-table type with no
                          registry (transition fallback).
  F. novel list        — a declared `traffic:` entry with a folder override
                          mints `T0001` into the anchor-root folder with the
                          control file inside as the folder note (Q3 shape).
  G. unknown list      — `Anchor.bogus` is refused, naming the registry.
  H. legacy CLI        — `stone pebble new` still works and continues the
                          same number sequence as the addressed form.
  I. relocated list    — a `rock: {folder: ...}` override is honored by the
                          addressed mint, by legacy `rock update` (stone NOT
                          archived, control found), and by push/recall
                          landing on the relocated target control.
  J. update, no kind   — bare `stone update` walks every kind in the table.
  K. dotted push tgt   — refused until the list-level walk (step 3).
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
_loader = importlib.machinery.SourceFileLoader("stone_mod_f628", str(HERE / "stone"))
_spec = importlib.util.spec_from_loader("stone_mod_f628", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["stone_mod_f628"] = st
_loader.exec_module(st)

st._GLOBAL_STONES_CACHE = {}   # hermetic: ignore any user-level `stones:` config

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


def check(cond, msg):
    ok(msg) if cond else no(msg)


def mkanchor(root, slug, extra=""):
    d = root / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(f"slug: {slug}\n{extra}", encoding="utf-8")
    return d


def run(root, *argv):
    return st.main(["stone", *argv, "--root", str(root)])


def quiet(root, *argv):
    """run, swallowing stdout+stderr, returning (rc, out, err)."""
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        rc = run(root, *argv)
    return rc, o.getvalue(), e.getvalue()


# ============================================================
print("A. parse_address")
# ============================================================
check(st.parse_address("Lumen") == ("Lumen", None), "bare anchor")
check(st.parse_address("Lumen.rocks") == ("Lumen", "rocks"), "dotted")
check(st.parse_address("HUD 1.rocks") == ("HUD 1", "rocks"), "spaced slug + list")
check(st.parse_address("No.TaList") == ("No.TaList", None),
      "a tail that is not a list name stays part of the slug")

# ============================================================
print("B. registry parse")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    L = mkanchor(root, "L",
                 "stones:\n"
                 "  _: pebble\n"
                 "  pebble:\n"
                 "  traffic:\n"
                 "    folder: Traffic\n"
                 "    prefix: T\n"
                 "traits: [x]\n")
    reg = st._anchor_stones(L)
    check(reg is not None and reg.get("_") == "pebble", "`_` designation read")
    check(reg.get("pebble") == {}, "empty entry -> all defaults")
    check(reg.get("traffic") == {"folder": "Traffic", "prefix": "T"},
          "field entry read")
    check("traits" not in reg, "parse stops at the first unindented line")

    M = mkanchor(root, "M")
    check(st._anchor_stones(M) is None, "no `stones:` -> None (undeclared)")

    bad = mkanchor(root, "Bad", "stones:\n  _:\n    x: 1\n")
    try:
        st._anchor_stones(bad)
        no("non-string `_` accepted")
    except SystemExit:
        ok("non-string `_` refused")

    bad2 = mkanchor(root, "Bad2", "stones:\n  BadName:\n")
    try:
        st._anchor_stones(bad2)
        no("malformed list name accepted")
    except SystemExit:
        ok("malformed list name refused")

# ============================================================
print("C. bare mint, no registry -> system dotless type (pebble), legacy paths")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "M")
    rc, out, err = quiet(root, "new", "M", "--line", "[[M]] first")
    check(rc == 0, f"rc 0 (got {rc}; err={err.strip()})")
    spath = root / "M" / "M Track" / "M Pebbles" / "M P0001.md"
    cpath = root / "M" / "M Track" / "M Pebble.md"
    check(spath.is_file(), "stone at legacy pebble path")
    check(cpath.is_file() and "M P0001" in cpath.read_text(encoding="utf-8"),
          "control file carries the line")

    # E. dotted mint reaches a kind-table type with no registry
    rc, out, err = quiet(root, "new", "M.rock", "--line", "[[M]] a rock")
    check(rc == 0, "E: `M.rock` mints via transition fallback")
    check((root / "M" / "M Track" / "M Rocks" / "M R0001.md").is_file(),
          "E: rock at legacy path")

    # H. legacy CLI continues the same sequence
    rc, out, err = quiet(root, "pebble", "new", "M", "--line", "[[M]] second")
    check(rc == 0 and (root / "M" / "M Track" / "M Pebbles" / "M P0002.md").is_file(),
          "H: legacy `stone pebble new` mints P0002 in the same list")

# ============================================================
print("D. `_: rock` makes bare mint a rock")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "Q", "stones:\n  _: rock\n  rock:\n")
    rc, out, err = quiet(root, "new", "Q", "--line", "[[Q]] r")
    check(rc == 0 and (root / "Q" / "Q Track" / "Q Rocks" / "Q R0001.md").is_file(),
          "bare `Q` minted a rock per its registry `_`")

# ============================================================
print("F. novel declared list with folder override -> folder-note control")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "L",
             "stones:\n  _: pebble\n  traffic:\n    folder: Traffic\n    prefix: T\n")
    rc, out, err = quiet(root, "new", "L.traffic", "--line", "[[L]] watch this")
    check(rc == 0, f"rc 0 (err={err.strip()})")
    check((root / "L" / "Traffic" / "L T0001.md").is_file(),
          "stone in the anchor-root Traffic/ folder, prefix T")
    note = root / "L" / "Traffic" / "L Traffic.md"
    check(note.is_file() and "L T0001" in note.read_text(encoding="utf-8"),
          "control file is the folder note inside Traffic/ (Q3 shape)")

    # G. unknown list on an anchor WITH a registry
    rc, out, err = quiet(root, "new", "L.bogus", "--line", "[[L]] x")
    check(rc == 1 and "bogus" in err, "G: `L.bogus` refused, naming the list")

# ============================================================
print("I. relocated kind list — override honored by mint, update, push, recall")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "N", "stones:\n  rock:\n    folder: N Rocks\n")
    mkanchor(root, "M")
    rc, out, err = quiet(root, "new", "N.rock", "--line", "[[N]] moved rock")
    check(rc == 0 and (root / "N" / "N Rocks" / "N R0001.md").is_file(),
          "mint lands in the anchor-root folder")
    ncontrol = root / "N" / "N Rock.md"
    check(ncontrol.is_file(), "control sits BESIDE the relocated folder")

    rc, out, err = quiet(root, "rock", "update")
    check(rc == 0, f"legacy `rock update` passes (err={err.strip()})")
    check((root / "N" / "N Rocks" / "N R0001.md").is_file()
          and not (root / "N" / "N Rocks" / "archive" / "N R0001.md").exists(),
          "relocated stone NOT archived by the walk")

    rc, out, err = quiet(root, "push", "N.rock", "R0001", "--to", "M")
    check(rc == 0, f"push from relocated list (err={err.strip()})")
    mcontrol = root / "M" / "M Track" / "M Rock.md"
    check(mcontrol.is_file() and "N R0001" in mcontrol.read_text(encoding="utf-8"),
          "line landed on the target's rock control")
    check("enrolled:: M" in (root / "N" / "N Rocks" / "N R0001.md").read_text(encoding="utf-8"),
          "enrollment recorded on the stone")

    rc, out, err = quiet(root, "recall", "N.rock", "R0001", "--from", "M")
    check(rc == 0 and "N R0001" not in mcontrol.read_text(encoding="utf-8"),
          "recall removes the line again")

    # K. dotted push target refused until step 3
    rc, out, err = quiet(root, "push", "N.rock", "R0001", "--to", "M.rock")
    check(rc == 1 and "step 3" in err, "K: dotted push target refused, naming step 3")

# ============================================================
print("J. bare `stone update` is ONE unified list-level pass (step 3)")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "M")
    rc, out, err = quiet(root, "update")
    check(rc == 0 and "stone: update" in out and "list(s)" in out,
          f"one summary line for the whole pass, naming the list count")

# ============================================================
print("L/M/N. unified propagation: two kinds at once, per-list feeds, bare target")
# ============================================================
CFG_ALL = st.load_kind_config()


def publish_all(root, slug, kind):
    """Insert SLUG's self-section header at the top of its KIND control —
    existing lines end up below it, hence published (f313's fixture move)."""
    cfg, _ = st._effective_cfg(root / slug, slug, kind, CFG_ALL)
    cpath = st._control_path(root / slug, slug, cfg)
    lines = cpath.read_text(encoding="utf-8").splitlines()
    idx = st._content_start(lines)
    lines.insert(idx, st._render_header(slug, cfg))
    cpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "A")
    mkanchor(root, "B", "feeds: A\n")
    mkanchor(root, "C", "stones:\n  traffic:\n    feeds: [A.rock]\n")
    mkanchor(root, "D", "stones:\n  traffic:\n    feeds: [A]\n")
    quiet(root, "new", "A", "--line", "[[A]] a pebble")
    quiet(root, "new", "A.rock", "--line", "[[A]] a rock")
    publish_all(root, "A", "pebble")
    publish_all(root, "A", "rock")

    rc, out, err = quiet(root, "update")
    check(rc == 0, f"L: unified pass rc 0 (err={err.strip()})")
    bp = (root / "B" / "B Track" / "B Pebble.md")
    br = (root / "B" / "B Track" / "B Rock.md")
    check(bp.is_file() and "A P0001" in bp.read_text(encoding="utf-8"),
          "L: pebble propagated along the anchor-level edge")
    check(br.is_file() and "A R0001" in br.read_text(encoding="utf-8"),
          "L: rock propagated along the SAME anchor-level edge, one pass")
    ct = root / "C" / "C Track" / "C Traffic" / "C Traffic.md"
    check(ct.is_file() and "A R0001" in ct.read_text(encoding="utf-8"),
          "M: per-list feed put a ROCK line on the traffic list (cross-type)")
    dt = root / "D" / "D Track" / "D Traffic" / "D Traffic.md"
    check(dt.is_file() and "A P0001" in dt.read_text(encoding="utf-8")
          and "A R0001" not in dt.read_text(encoding="utf-8"),
          "N: bare feed target `A` drew A's DEFAULT list (pebbles), not rocks")

    # P. restricted walk parity: a per-kind pass neither sees nor disturbs
    # what only the unified walk manages.
    before = ct.read_text(encoding="utf-8")
    rc, out, err = quiet(root, "pebble", "update")
    check(rc == 0 and ct.read_text(encoding="utf-8") == before,
          "P: legacy `pebble update` leaves the traffic list untouched")
    rc, out, err = quiet(root, "rock", "update")
    check(rc == 0 and ct.read_text(encoding="utf-8") == before,
          "P: legacy `rock update` too — the rock line there is not its business")

    # idempotence: a second unified pass writes nothing
    rc, out, err = quiet(root, "update", "--dry-run")
    check(rc == 0 and "0 control file(s) would be written" in out
          and "0 stone file(s) would be written" in out,
          "L: the unified pass is idempotent (second dry-run writes nothing)")

# ============================================================
print("R. digit-named lists (HUD.1)")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "A")
    mkanchor(root, "H", "stones:\n  '1':\n    feeds: [A, A.rock]\n")
    check(st.parse_address("H.1") == ("H", "1"), "H.1 parses as (H, 1)")
    quiet(root, "new", "A", "--line", "[[A]] p")
    quiet(root, "new", "A.rock", "--line", "[[A]] r")
    CFG_ALL2 = st.load_kind_config()
    for kind in ("pebble", "rock"):
        cfg, _ = st._effective_cfg(root / "A", "A", kind, CFG_ALL2)
        cp = st._control_path(root / "A", "A", cfg)
        lines = cp.read_text(encoding="utf-8").splitlines()
        lines.insert(st._content_start(lines), st._render_header("A", cfg))
        cp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rc, out, err = quiet(root, "update")
    hc = root / "H" / "H Track" / "H 1" / "H 1.md"
    check(rc == 0 and hc.is_file()
          and "A P0001" in hc.read_text(encoding="utf-8")
          and "A R0001" in hc.read_text(encoding="utf-8"),
          "list `1` receives both the pebble and the rock in one merged list")

# ============================================================
print("O. unified cycle names dotted lists")
# ============================================================
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    mkanchor(root, "A", "feeds: B\n")
    mkanchor(root, "B", "feeds: A\n")
    rc, out, err = quiet(root, "update")
    check(rc == 1 and "cycle in feeds: DAG" in err
          and "A." in err and "B." in err,
          "cycle reported as a dotted-list path, nothing written")

# ============================================================
print("Q. config-mode types (kind table retired): plural names, folder-note control")
# ============================================================
SECTION = {
    "_": "pebbles",
    "pebbles": None,
    "rocks": None,
    "sleepers": None,
    "book": {"member": "dated"},
}
st._GLOBAL_STONES_CACHE = SECTION
try:
    types = st.load_types()
    check(sorted(types) == ["book", "pebbles", "rocks", "sleepers"],
          "config section IS the type set (kind table not consulted)")
    check(types["pebbles"]["prefix"] == "P" and types["rocks"]["prefix"] == "R"
          and types["sleepers"]["prefix"] == "S",
          "prefixes derive from the names")
    check(types["book"]["member"] == "dated", "book declares dated members")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        mkanchor(root, "L", "stones:\n  pebbles:\n  rocks:\n")
        rc, out, err = quiet(root, "new", "L", "--line", "[[L]] plural world")
        check(rc == 0, f"bare mint rc 0 (err={err.strip()})")
        check((root / "L" / "L Track" / "L Pebbles" / "L P0001.md").is_file(),
              "stone in the plural folder")
        note = root / "L" / "L Track" / "L Pebbles" / "L Pebbles.md"
        check(note.is_file() and "L P0001" in note.read_text(encoding="utf-8"),
              "control is the folder note INSIDE (Q5) with the plural name (Q6)")
        rc, out, err = quiet(root, "new", "L.rocks", "--line", "[[L]] r")
        check(rc == 0 and (root / "L" / "L Track" / "L Rocks" / "L R0001.md").is_file()
              and (root / "L" / "L Track" / "L Rocks" / "L Rocks.md").is_file(),
              "dotted plural address mints into the folder-note shape")
        rc, out, err = quiet(root, "pebbles", "update")
        check(rc == 0, "legacy-form CLI accepts the config-mode type name (stone pebbles update)")
        rc, out, err = quiet(root, "update", "--dry-run")
        check(rc == 0 and "0 control file(s) would be written" in out,
              "unified pass reconciles the plural world cleanly")
        # dated member in config mode
        mkanchor(root, "H", "stones:\n  book:\n")
        rc, out, err = quiet(root, "new", "H.book", "--line", "[[x]]", "--title", "Trip")
        check(rc == 0 and any((root / "H" / "H Track" / "H Book").glob("*Trip.md")),
              "config-mode dated mint works (H.book --title)")
finally:
    st._GLOBAL_STONES_CACHE = {}

# ============================================================
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
