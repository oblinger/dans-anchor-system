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
  J. duplicate slugs  — a colliding slug is fatal only where it is REFERENCED
                        (mint target, feed endpoint, carrier of stone data);
                        elsewhere the walk skips it and says so.
  K. the group's own  — `{slug} Rocks.md` sits inside `{slug} Rocks/` and
     page is not a       begins `{slug} R`, so a prefix glob matched it in
     stone               every group; it must never load as a stone.
  L. un-round-trippable — an owner slug needs letters and digits with no
     slug → mint          spaces, since a control line is parsed back into
     refused              (owner, number) from its link target. Refused at the
                        mint; still allowed to CONSUME via feeds:.
  M. --dry-run        — reports every write AND every archive (a file MOVE),
                        performs none of them, and the wet pass still does.
  N. unresolvable     — a `feeds:` name matching no anchor refuses the pass,
     feed edge            quotes the offending name, and writes nothing.
  O. zero-work pass   — a run with nothing to do still prints its counts.

Each behaviour above was red-checked by hand during development (broken,
confirmed the corresponding section fails, restored, confirmed green again);
see the implementation report for the specific breaks used.

**N and O were added 2026-08-11, with F312 M1.** They are the two of that
feature's three feed-graph invariants that shipped implemented and unasserted —
only acyclicity (case I) had a guard. Both untested ones fail *quietly* by
nature: an unresolvable source supplies zero stones and looks exactly like an
empty one, and a silent pass looks exactly like a pass that never ran. A
ruleset was about to claim all three, so they were measured before it did.
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

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

    # ---- H: conflicting edits abort the pass; agreeing edits converge -----
    # F312 Q6 answered (C) 2026-08-13. This case USED to assert the opposite —
    # that three files editing one stone to three different values converged on
    # the alphabetically-last one. That was the shipped behaviour and it
    # silently discarded two edits per pass: the projections converge, every
    # file looks right afterwards, and nothing anywhere records that the other
    # two edits existed. (C) keeps every-file-is-a-write-surface and removes
    # only the silence.
    print("== H: conflicting edits abort the pass and discard nothing ==")
    h_watch = [apath, bpath, cpath, stone_path(root, "A", "R0002")]
    h_before = {p: p.read_bytes() for p in h_watch}
    rewrite_line_text(apath, "R0002", "text-from-A")
    rewrite_line_text(bpath, "R0002", "text-from-B")
    rewrite_line_text(cpath, "R0002", "text-from-C")
    h_edited = {p: p.read_bytes() for p in h_watch}

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(root, "rock", "update")
    err_text = err.getvalue()

    if rc != 0:
        ok(f"three-way conflicting edit refuses the pass (rc={rc})")
    else:
        no("conflicting edits returned 0 — the loss is still silent")

    if "conflicting values" in err_text and "A:R0002" in err_text:
        ok("...and the report names the stone")
    else:
        no(f"collision not reported against the stone: {err_text!r}")

    if all(f"text-from-{s}" in err_text for s in ("A", "B", "C")):
        ok("...and quotes every value in conflict, so nothing is lost to the log")
    else:
        no(f"report did not carry all three values: {err_text!r}")

    if all(p.read_bytes() == h_edited[p] for p in h_watch):
        ok("...and NOTHING was written — no half-reconciled tree, as with a cycle")
    else:
        no("a colliding pass still wrote — abort is not before-writes")

    # Agreement is not conflict: two projections edited to the SAME new text
    # discard nothing when one is taken, so this must still converge. Without
    # this the check could pass by simply refusing every multi-file edit.
    rewrite_line_text(apath, "R0002", "agreed-text")
    rewrite_line_text(bpath, "R0002", "agreed-text")
    rewrite_line_text(cpath, "R0002", "agreed-text")
    rc = run(root, "rock", "update")
    want = stone_line("A", "R0002", "agreed-text")
    if rc == 0 and "line:: agreed-text" in stone_path(root, "A", "R0002").read_text(encoding="utf-8"):
        ok("three projections edited to the SAME text still converge (rc=0)")
    else:
        no(f"agreeing edits were treated as a conflict (rc={rc})")
    if all(want in p.read_text(encoding="utf-8") for p in (apath, bpath, cpath)):
        ok("...and every projection equals the stone afterwards (convergence)")
    else:
        no("convergence failed after an agreeing three-way edit")
    del h_before

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

    # ============================================================
    # L. a slug that cannot round-trip is refused AT THE MINT, not at discovery
    # ============================================================
    # A control line is parsed back into (owner, number) from its link target
    # alone, so an owner slug needs letters and digits with no spaces. `HUD 1`
    # mints fine and writes a line that LOOKS right, then classifies as 'other'
    # forever — no propagation, no read-back, and no pass says a word. But a
    # consuming-only node may legitimately carry such a slug, which is why the
    # check lives at the mint and not in discover_anchors.
    print("== L: a slug that cannot round-trip is refused at the mint only ==")
    lroot = TMP / "l"
    mkanchor(lroot, "POOL", [])
    (lroot / "SCREEN").mkdir(parents=True, exist_ok=True)
    (lroot / "SCREEN" / ".anchor").write_text("slug: HUD 1\nfeeds: POOL\n", encoding="utf-8")
    run(lroot, "rock", "new", "POOL", "--line", "a real stone")
    # below POOL's own self-section marker, so it publishes downstream
    write_control(control_path(lroot, "POOL"), "POOL",
                  [header_line("POOL"), stone_line("POOL", "R0001", "a real stone")])

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(lroot, "rock", "new", "HUD 1", "--line", "would never propagate")
    if rc != 0 and "cannot own a stone" in err.getvalue():
        ok("minting into a spaced slug is refused loudly instead of failing silently")
    else:
        no(f"spaced-slug mint was not refused: rc={rc} {err.getvalue()!r}")

    if not list((lroot / "SCREEN").rglob("HUD 1 R*.md")):
        ok("the refused mint left no orphan stone file behind")
    else:
        no("a stone file was written for a slug that can never be read back")

    # The same slug must still CONSUME — that is the whole reason for the seam.
    screen_ctrl = lroot / "SCREEN" / "HUD 1 Track" / "HUD 1 Rock.md"
    screen_ctrl.parent.mkdir(parents=True, exist_ok=True)
    screen_ctrl.write_text("# HUD 1 Rock\n\n[[HUD 1 Rock|-HUD 1-]]\n\n[[POOL Rock|-POOL-]]\n", encoding="utf-8")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        run(lroot, "rock", "update")
    if "[[POOL R0001|POOL:]] a real stone" in screen_ctrl.read_text(encoding="utf-8"):
        ok("a spaced slug still receives stones along feeds: — only minting is barred")
    else:
        no(f"spaced slug failed to consume:\n{screen_ctrl.read_text(encoding='utf-8')!r}")

    # ============================================================
    # M. --dry-run reports every write and archive, and performs none
    # ============================================================
    # `update` has no confirmation and `--root` defaults to the whole vault, so
    # its first invocation anywhere is a vault-wide write. The dry run is how
    # you look first — which means it must be inert including the ARCHIVE path,
    # where the mutation is a file MOVE rather than a write.
    print("== M: --dry-run reports, and changes nothing ==")
    mroot = TMP / "m"
    mkanchor(mroot, "UP", [])
    mkanchor(mroot, "DOWN", ["UP"])
    run(mroot, "rock", "new", "UP", "--line", "original text")
    write_control(control_path(mroot, "UP"), "UP",
                  [header_line("UP"), stone_line("UP", "R0001", "original text")])
    write_control(control_path(mroot, "DOWN"), "DOWN", [header_line("UP")])
    run(mroot, "rock", "update")

    def _tree_bytes(root):
        return {str(p): p.read_bytes() for p in sorted(root.rglob("*.md"))}

    before = _tree_bytes(mroot)
    # an edit downstream (propagates back + out) AND a deletion from the owner's
    # own file (archives) — both mutation kinds in one pass
    rewrite_line_text(control_path(mroot, "DOWN"), "UP R0001", "edited downstream")
    drop_line(control_path(mroot, "UP"), "UP R0001")
    staged = _tree_bytes(mroot)

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = run(mroot, "rock", "update", "--dry-run")
    report = out.getvalue()

    if rc == 0 and "DRY RUN" in report:
        ok("--dry-run exits 0 and says so in its summary line")
    else:
        no(f"dry run summary missing: rc={rc} {report!r}")

    if "would write" in report or "would archive" in report:
        ok("--dry-run names the writes it is declining to make")
    else:
        no(f"dry run reported no intended work: {report!r}")

    if _tree_bytes(mroot) == staged:
        ok("--dry-run left every file byte-identical, including the archive move")
    else:
        changed = [k for k, v in _tree_bytes(mroot).items() if staged.get(k) != v]
        no(f"dry run mutated the tree: {changed}")

    if stone_path(mroot, "UP", "R0001").is_file() and not archived_stone_path(mroot, "UP", "R0001").is_file():
        ok("--dry-run did not move the stone into archive/")
    else:
        no("dry run archived a stone — a file MOVE performed by a run that promised not to")

    # and the real pass still does all of it, so the dry run is not just a no-op verb
    run(mroot, "rock", "update")
    if _tree_bytes(mroot) != staged and archived_stone_path(mroot, "UP", "R0001").is_file():
        ok("the same pass without --dry-run performs the writes and the archive")
    else:
        no("the wet run did not do what the dry run promised")

    # ============================================================
    # N. an unresolvable name in `feeds:` is named, not ignored
    #    ([[DAS feed]] invariant 2, R-feed-03)
    #
    # Case I covers acyclicity and case J covers a DUPLICATE slug; a name that
    # matches NO anchor was implemented and never asserted. It is the invariant
    # whose failure is the least visible of the three: an unresolvable source
    # supplies zero stones and is indistinguishable from a source that happens
    # to be empty, so a typo'd feed edge stays invisible forever.
    # ============================================================
    print("== N: a feeds: name matching no anchor is reported by name ==")
    nroot = TMP / "n"
    mkanchor(nroot, "SRC", [])
    mkanchor(nroot, "DST", ["SRC", "TYPPO"])
    run(nroot, "rock", "new", "SRC", "--line", "a real stone")
    write_control(control_path(nroot, "DST"), "DST", [header_line("SRC")])
    before_n = _tree_bytes(nroot)

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = run(nroot, "rock", "update")
    msg = err.getvalue()

    if rc != 0:
        ok(f"an unresolvable feed edge refuses the pass (rc={rc})")
    else:
        no("an unresolvable feed edge was tolerated — a typo'd source is a silent zero")

    if "TYPPO" in msg:
        ok(f"...and the offending name is quoted: {msg.strip()!r}")
    else:
        no(f"...but the message does not name TYPPO: {msg!r}")

    if _tree_bytes(nroot) == before_n:
        ok("...and nothing was written, as with a cycle")
    else:
        no("an unresolvable edge aborted the pass but still wrote files")

    # ============================================================
    # O. a pass with nothing to do SAYS so ([[DAS feed]] invariant 3, R-feed-04)
    #
    # "No silent empty" is the vault's most repeated defect shape, and the one
    # place it is least detectable is a run that legitimately has no work: a
    # pass that printed nothing would be indistinguishable from a pass that
    # never looked. The counts are the evidence, so they are asserted.
    # ============================================================
    print("== O: a zero-work pass still reports its counts ==")
    oroot = TMP / "o"
    mkanchor(oroot, "QUIET", [])
    write_control(control_path(oroot, "QUIET"), "QUIET", [header_line("QUIET")])
    (oroot / "QUIET" / "QUIET Track" / "QUIET Rocks").mkdir(parents=True, exist_ok=True)

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = run(oroot, "rock", "update")
    report = out.getvalue()

    if rc == 0 and report.strip():
        ok(f"a no-op pass exits 0 and still prints: {report.strip()!r}")
    else:
        no(f"a no-op pass said nothing — a zero nobody can distinguish from not looking: {report!r}")

    if "0 control file(s) written" in report and "anchor(s)" in report:
        ok("...naming both the zero it wrote and the scope it covered")
    else:
        no(f"...but the report carries no count of what it looked at: {report!r}")

finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
