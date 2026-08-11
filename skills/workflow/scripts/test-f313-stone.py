#!/usr/bin/env python3
"""test-f313-stone.py — TINK F313: `stone`, one script for every kind of
stone, its control file, and the feeds between them.

Exercises the whole design end to end over a fixture DAG A → B → C
("A feeds into B, B feeds into C" — B's `.anchor` carries `feeds: A`, C's
carries `feeds: B`), built fresh in a tempdir per run. Never touches the real
vault: every call passes `--root <tempdir>` explicitly.

  A. mint            — `stone rock new` creates the numbered stone file and
                        inserts its line at the top of the anchor's own
                        control file, unpublished (above any self-section).
  B. publish + one    — moving a line below the self-section and running
     hop                `update` propagates it into the ONE anchor
                        immediately downstream.
  C. two hops          — a single `update` pass reaches a second hop when the
                        first hop's import site already sits below ITS OWN
                        self-section.
  D. reorder survives — hand-swapping two already-propagated lines in a
                        downstream file and re-running `update` leaves the
                        swap exactly as the human left it.
  E. unpublish        — moving a line back above the self-section retracts it
                        from every downstream file, but it stays present
                        (just repositioned) in its own file — not archived.
  F. own-file delete  — deleting a stone's line from ITS OWN control file
     → archive           archives the stone file (moved, not rewritten).
  G. downstream delete — deleting the SAME kind of line from a DOWNSTREAM
     → restored           (non-owning) file is undone on the next pass.
  H. three-way edit   — the same stone's rendered line, hand-edited in THREE
     → convergence        control files in one pass, converges on the LAST
                        one touched (read-back order is anchor-slug order);
                        every projection equals the stone afterward.
  I. cycle → path,    — a deliberately introduced cycle in feeds: is reported
     no writes            as an arrow path and the pass writes nothing.

Each behaviour above was red-checked by hand during development (broken,
confirmed the corresponding section fails, restored, confirmed green again);
see the implementation report for the specific breaks used.
"""
import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
_loader = importlib.machinery.SourceFileLoader("stone_mod", str(HERE / "stone"))
_spec = importlib.util.spec_from_loader("stone_mod", _loader)
st = importlib.util.module_from_spec(_spec)
sys.modules["stone_mod"] = st
_loader.exec_module(st)

CFG = st.load_kind_config()["rock"]

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


# ============================================================
# Fixture
# ============================================================

def mkanchor(root, slug, feeds):
    d = root / slug
    d.mkdir(parents=True, exist_ok=True)
    feeds_line = f"feeds: {', '.join(feeds)}" if feeds else "feeds:"
    (d / ".anchor").write_text(f"slug: {slug}\n{feeds_line}\n", encoding="utf-8")
    return d


def control_path(root, slug):
    return root / slug / f"{slug} Track" / f"{slug} Rock.md"


def stone_path(root, slug, sid):
    return root / slug / f"{slug} Track" / f"{slug} Rocks" / f"{slug} {sid}.md"


def archived_stone_path(root, slug, sid):
    return root / slug / f"{slug} Track" / f"{slug} Rocks" / "archive" / f"{slug} {sid}.md"


def write_control(path, slug, body_lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["---", f"description: {slug} Rock — control file", "---", "", f"# {slug} Rock", ""]
    path.write_text("\n".join(header + body_lines) + "\n", encoding="utf-8")


def header_line(slug):
    return st._render_header(slug, CFG)


def stone_line(slug, sid, text):
    return st.render_stone_line(slug, sid, text, CFG)


def run(root, *argv):
    return st.main(["stone", *argv, "--root", str(root)])


def move_line(path, needle, before_needle):
    """Move the (single) line containing `needle` to sit immediately before
    the (single) line that equals `before_needle` exactly. Test-fixture
    helper simulating a human hand-editing a control file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = next(i for i, l in enumerate(lines) if needle in l)
    moving = lines.pop(i)
    j = next(i for i, l in enumerate(lines) if l.strip() == before_needle)
    lines.insert(j, moving)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def insert_self_section(path, slug):
    """Add SLUG's own self-section marker at the top of its content — the
    human act of first-ever publishing anything: everything currently there
    (already at the top) ends up below it, hence published."""
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = st._content_start(lines)
    lines.insert(idx, header_line(slug))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def publish_after(path, needle, after_needle):
    """Move the (single) line containing `needle` to sit immediately AFTER
    the (single) line that equals `after_needle` exactly — publishing it,
    when `after_needle` is the self-section header."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = next(i for i, l in enumerate(lines) if needle in l)
    moving = lines.pop(i)
    j = next(i for i, l in enumerate(lines) if l.strip() == after_needle)
    lines.insert(j + 1, moving)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def drop_line(path, needle):
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [l for l in lines if needle not in l]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rewrite_line_text(path, needle, new_text):
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(lines):
        if needle in l:
            prefix = l.split("]]", 1)[0] + "]]"
            lines[i] = f"{prefix} {new_text}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


TMP = Path(tempfile.mkdtemp())
try:
    root = TMP
    mkanchor(root, "A", [])
    mkanchor(root, "B", ["A"])
    mkanchor(root, "C", ["B"])

    apath = control_path(root, "A")
    bpath = control_path(root, "B")
    cpath = control_path(root, "C")

    # ---- A: mint ------------------------------------------------------
    print("== A: mint ==")
    rc = run(root, "rock", "new", "A", "--line", "decide Aria")
    a_r0001 = stone_path(root, "A", "R0001")
    if rc == 0 and a_r0001.is_file():
        ok("`stone rock new` returns 0 and creates the numbered stone file")
    else:
        no(f"mint failed: rc={rc}, exists={a_r0001.is_file()}")

    stone_text = a_r0001.read_text(encoding="utf-8")
    if "line:: decide Aria" in stone_text:
        ok("stone file carries line:: exactly as minted")
    else:
        no(f"stone file missing line:: — {stone_text!r}")

    a_text = apath.read_text(encoding="utf-8")
    if stone_line("A", "R0001", "decide Aria") in a_text:
        ok("minted line inserted into A's own control file")
    else:
        no(f"minted line missing from A Rock.md:\n{a_text}")
    if "appears:: A" in a_r0001.read_text(encoding="utf-8"):
        ok("stone's propagation index (appears::) includes its own anchor after mint")
    else:
        no("appears:: missing own anchor after mint")

    # ---- B/C fixture wiring: self-section + import headers ------------
    write_control(bpath, "B", [header_line("B"), header_line("A")])
    write_control(cpath, "C", [header_line("C"), header_line("B")])

    # ---- B: publish (below self-section) + one hop ---------------------
    print("== B: publish + one-hop propagation ==")
    insert_self_section(apath, "A")  # first publish ever: self-section lands above the stone
    rc = run(root, "rock", "update")
    b_text = bpath.read_text(encoding="utf-8")
    if rc == 0 and stone_line("A", "R0001", "decide Aria") in b_text:
        ok("published stone propagated one hop into B, under B's header for A")
    else:
        no(f"one-hop propagation failed, rc={rc}:\n{b_text}")

    # ---- C: two hops in a single update pass ---------------------------
    print("== C: two hops in one update pass ==")
    c_text = cpath.read_text(encoding="utf-8")
    if stone_line("A", "R0001", "decide Aria") in c_text:
        ok("same pass already reached C — two-hop propagation in one call")
    else:
        no(f"stone did not reach C on the same pass:\n{c_text}")

    # ---- D: reorder survives update -------------------------------------
    print("== D: hand-reorder survives update ==")
    rc = run(root, "rock", "new", "A", "--line", "gather stats")
    publish_after(apath, "R0002", header_line("A"))  # publish the 2nd rock too
    run(root, "rock", "update")
    b_lines_before = [l for l in bpath.read_text(encoding="utf-8").splitlines()
                       if "R0001" in l or "R0002" in l]
    if b_lines_before == [stone_line("A", "R0001", "decide Aria"),
                           stone_line("A", "R0002", "gather stats")]:
        ok("second published rock appended after the first, in B")
    else:
        no(f"unexpected order after first propagation: {b_lines_before}")

    move_line(bpath, "R0002", stone_line("A", "R0001", "decide Aria"))  # swap by hand
    b_swapped = [l for l in bpath.read_text(encoding="utf-8").splitlines()
                 if "R0001" in l or "R0002" in l]
    rc = run(root, "rock", "update")
    b_after = [l for l in bpath.read_text(encoding="utf-8").splitlines()
               if "R0001" in l or "R0002" in l]
    if b_after == b_swapped:
        ok("hand-swapped order in B survives `update` unchanged")
    else:
        no(f"update reshuffled a hand-edited order: before={b_swapped} after={b_after}")

    # ---- E: unpublish retracts downstream, stays local ------------------
    print("== E: unpublish retracts downstream, stays in owner ==")
    move_line(apath, "R0001", stone_line("A", "R0002", "gather stats"))
    # then hop it above the header entirely
    a_lines = apath.read_text(encoding="utf-8").splitlines()
    i = next(i for i, l in enumerate(a_lines) if "R0001" in l)
    moving = a_lines.pop(i)
    j = next(i for i, l in enumerate(a_lines) if l.strip() == header_line("A"))
    a_lines.insert(j, moving)
    apath.write_text("\n".join(a_lines) + "\n", encoding="utf-8")
    rc = run(root, "rock", "update")
    b_text = bpath.read_text(encoding="utf-8")
    c_text = cpath.read_text(encoding="utf-8")
    a_text = apath.read_text(encoding="utf-8")
    if "R0001" not in b_text and "R0001" not in c_text:
        ok("unpublished stone retracted from both downstream files")
    else:
        no(f"unpublished stone still present downstream:\nB={b_text}\nC={c_text}")
    if "R0001" in a_text:
        ok("unpublished stone still present in its own control file (not archived)")
    else:
        no("unpublished stone vanished from its own file — should only be repositioned")
    if archived_stone_path(root, "A", "R0001").is_file():
        no("unpublish incorrectly archived the stone")
    else:
        ok("unpublish did not archive the stone")

    # ---- F: delete from OWN control file → archive ----------------------
    print("== F: delete from own control file archives the stone ==")
    drop_line(apath, "R0001")
    rc = run(root, "rock", "update")
    live_path = stone_path(root, "A", "R0001")
    arch_path = archived_stone_path(root, "A", "R0001")
    if rc == 0 and not live_path.is_file() and arch_path.is_file():
        ok("stone moved to archive/ after being deleted from its own control file")
    else:
        no(f"archive did not happen as expected: live={live_path.is_file()} arch={arch_path.is_file()}")
    if "appears:: " in arch_path.read_text(encoding="utf-8") and \
       "appears:: A" not in arch_path.read_text(encoding="utf-8"):
        ok("archived stone's propagation index cleared")
    else:
        no("archived stone's appears:: not cleared")

    # ---- G: delete from a DOWNSTREAM control file → restored ------------
    print("== G: delete from a downstream (non-owning) file is restored ==")
    drop_line(cpath, "R0002")
    c_after_drop = cpath.read_text(encoding="utf-8")
    if "R0002" not in c_after_drop:
        ok("fixture setup: R0002 hand-deleted from C")
    else:
        no("fixture setup failed to delete R0002 from C")
    rc = run(root, "rock", "update")
    c_text = cpath.read_text(encoding="utf-8")
    if stone_line("A", "R0002", "gather stats") in c_text:
        ok("stone deleted from a downstream file is restored on the next pass")
    else:
        no(f"downstream deletion was NOT restored:\n{c_text}")

    # ---- H: three-way edit converges on the last one ---------------------
    print("== H: same stone edited in three files converges on the last ==")
    rewrite_line_text(apath, "R0002", "text-from-A")
    rewrite_line_text(bpath, "R0002", "text-from-B")
    rewrite_line_text(cpath, "R0002", "text-from-C")
    rc = run(root, "rock", "update")
    final_stone_text = stone_path(root, "A", "R0002").read_text(encoding="utf-8")
    if "line:: text-from-C" in final_stone_text:
        ok("stone's master line:: converged on the last-touched copy (C, alphabetically last)")
    else:
        no(f"stone did not converge on the expected winner:\n{final_stone_text}")
    a_final = apath.read_text(encoding="utf-8")
    b_final = bpath.read_text(encoding="utf-8")
    c_final = cpath.read_text(encoding="utf-8")
    want = stone_line("A", "R0002", "text-from-C")
    if want in a_final and want in b_final and want in c_final:
        ok("every projection equals the stone after the pass (convergence)")
    else:
        no(f"convergence failed:\nA={a_final}\nB={b_final}\nC={c_final}")

    # ---- I: cycle reported as a path, no writes --------------------------
    print("== I: a cycle in feeds: is reported as a path, and nothing is written ==")
    snapshot = {}
    watched = [apath, bpath, cpath,
               stone_path(root, "A", "R0002"),
               archived_stone_path(root, "A", "R0001")]
    for p in watched:
        snapshot[p] = p.read_bytes() if p.is_file() else None

    (root / "A" / ".anchor").write_text("slug: A\nfeeds: C\n", encoding="utf-8")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(root, "rock", "update")  # main() catches StoneError, returns 1 — never raises out
    err_text = err.getvalue()

    if rc != 0:
        ok(f"cycle update returns non-zero (rc={rc})")
    else:
        no("cycle update returned 0 — should have refused")

    if "cycle" in err_text and "A → B → C → A" in err_text:
        ok(f"cycle reported as an arrow path: {err_text.strip()!r}")
    else:
        no(f"cycle not reported as the expected path: {err_text!r}")

    unchanged = all(
        (p.read_bytes() if p.is_file() else None) == snapshot[p]
        for p in watched
    )
    if unchanged:
        ok("no file was written when the pass aborted on a cycle")
    else:
        no("a cycle abort still left some file(s) modified")

    (root / "A" / ".anchor").write_text("slug: A\nfeeds:\n", encoding="utf-8")  # undo for cleanliness

    # ============================================================
    # J. a duplicate slug elsewhere in the tree is fatal only when REFERENCED
    # ============================================================
    # The real vault has 8 slug collisions across 1,377 anchors, three of them
    # Warden's own fixtures reusing `FX1` on purpose. Failing at discovery made
    # every stone operation impossible in the vault the tool ships inside.
    print("== J: a duplicate slug is fatal only where it is referenced ==")
    jroot = TMP / "j"
    mkanchor(jroot, "SOLO", [])
    for nest in ("one", "two"):
        d = jroot / "dupes" / nest / "DUP"
        d.mkdir(parents=True, exist_ok=True)
        (d / ".anchor").write_text("feeds:\n", encoding="utf-8")  # slug from folder name

    anchors, ambiguous = st.discover_anchors(jroot)
    if "SOLO" in anchors and list(ambiguous) == ["DUP"] and len(ambiguous["DUP"]) == 2:
        ok("discovery separates the ambiguous slug out instead of raising")
    else:
        no(f"discovery mis-split: anchors={sorted(anchors)} ambiguous={ambiguous}")

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(jroot, "rock", "new", "SOLO", "--line", "unblocked by the collision")
    if rc == 0 and stone_path(jroot, "SOLO", "R0001").is_file():
        ok("mint into an unrelated anchor succeeds despite the collision")
    else:
        no(f"mint blocked by an unrelated collision (rc={rc}) {err.getvalue()!r}")

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = run(jroot, "rock", "update")
    if rc == 0 and "ambiguous slug(s) skipped: DUP" in out.getvalue():
        ok("update runs and NAMES the skipped ambiguous slug (no silent skip)")
    else:
        no(f"update did not report the skip: rc={rc} {out.getvalue()!r}")

    # Referenced as a feed endpoint → loud.
    (jroot / "SOLO" / ".anchor").write_text("slug: SOLO\nfeeds: DUP\n", encoding="utf-8")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(jroot, "rock", "update")
    if rc != 0 and "ambiguous" in err.getvalue() and "SOLO's feeds:" in err.getvalue():
        ok("a feeds: edge naming an ambiguous slug fails loudly, naming both paths")
    else:
        no(f"ambiguous feed endpoint not caught: rc={rc} {err.getvalue()!r}")
    (jroot / "SOLO" / ".anchor").write_text("slug: SOLO\nfeeds:\n", encoding="utf-8")

    # Carrying real stone data → loud, because skipping it would lose work.
    write_control(control_path(jroot / "dupes" / "one", "DUP"), "DUP", [])
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(jroot, "rock", "update")
    if rc != 0 and "carries stone data" in err.getvalue():
        ok("an ambiguous anchor holding stone data fails rather than being skipped")
    else:
        no(f"ambiguous anchor with stone data was skipped silently: rc={rc} {err.getvalue()!r}")
    shutil.rmtree(jroot / "dupes" / "one" / "DUP" / "DUP Track")

    # Named as the mint target → loud.
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(jroot, "rock", "new", "DUP", "--line", "which one?")
    if rc != 0 and "ambiguous" in err.getvalue() and "mint target" in err.getvalue():
        ok("minting INTO an ambiguous slug is refused, naming every candidate")
    else:
        no(f"mint into an ambiguous slug was not refused: rc={rc} {err.getvalue()!r}")

    # ============================================================
    # K. the group's own anchor page is not a stone
    # ============================================================
    # `{slug} Rocks.md` lives inside `{slug} Rocks/` and begins `{slug} R`, so a
    # `{slug} {PREFIX}*` glob matches it in EVERY rock group that exists. Loading
    # it as a stone prepends a key block to the anchor page and mints a control
    # line pointing at it — which is what happened to MED, AIS and HBR at once
    # on 2026-08-10, in the vault, before this test existed.
    print("== K: the stone group's own anchor page is never loaded as a stone ==")
    kroot = TMP / "k"
    mkanchor(kroot, "GRP", [])
    run(kroot, "rock", "new", "GRP", "--line", "a real stone")
    page = kroot / "GRP" / "GRP Track" / "GRP Rocks" / "GRP Rocks.md"
    page_text = "---\ndescription: GRP's rocks\n---\n\n# GRP Rocks\nThe folder's own anchor page.\n"
    page.write_text(page_text, encoding="utf-8")

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = run(kroot, "rock", "update")

    if page.read_text(encoding="utf-8") == page_text:
        ok("the group's anchor page is left byte-identical by an update pass")
    else:
        no(f"the group's anchor page was rewritten as a stone:\n{page.read_text(encoding='utf-8')!r}")

    ctrl = control_path(kroot, "GRP").read_text(encoding="utf-8")
    if "[[GRP Rocks" not in ctrl:
        ok("no control line was minted pointing at the anchor page")
    else:
        no(f"control file references the anchor page as a stone:\n{ctrl!r}")

    # And the mint must count the same set, or the next number collides.
    run(kroot, "rock", "new", "GRP", "--line", "the next one")
    if stone_path(kroot, "GRP", "R0002").is_file():
        ok("numbering ignores the anchor page and mints R0002, not a collision")
    else:
        no("mint mis-numbered after the anchor page was present")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
