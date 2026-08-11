#!/usr/bin/env python3
"""test-f312-rocks-tier-control-file.py — R-rocks-06 judges the CONTROL file.

[[DAS Stone]] moved a rock group's ranking off the folder-note and into the
control file `{slug} Rock.md`, because an anchor page's top is machine-maintained
and the ranking is the one thing that must stay hand-arranged. `R-rocks-05`'s
checker was migrated in that pass. `R-rocks-06`'s was not, and nothing noticed —
it kept opening the folder-note, found no tier lines there, and reported **pass**
on every group in the vault.

Measured 2026-08-11, before the fix: **0 tier links judged, 12 present.** All four
live groups (`MED` 1, `AIS` 3, `VEC` 1, `HBR` 3) had migrated. The rule was green
because it was looking at the wrong file, which is indistinguishable from green
because the links resolve — see [[project_a_threshold_detector_proves_a_vacuous_zero]].

This is the **third** silent stop in this one ruleset: `R-rocks-04`'s note records
two earlier parser folds that disabled `R-rocks-03` and `R-rocks-05`. The first two
were caused by a malformed tier annotation; this one by a migration that moved a
file out from under a checker. Different cause, identical signature — a rule that
reads as coverage while evaluating nothing.

Case 3 is the one to keep, and it caught a landmine the fix had just armed. A
migrated control file carries two shapes that are NOT this group's tier lines: the
self-section header, and — because propagation under [[DAS feed]] is line-copying —
lines naming stones **owned by another anchor**. `_resolve_doc` searches at most
four ancestor anchor roots, so it cannot see either. Judging them would trade a
vacuous pass for a false failure on any anchor that imports rocks, which is the
whole purpose of the feed DAG. No live group imports rocks today, so this test is
the only thing standing between that and a rule that breaks on first real use.

Usage: python3 test-f312-rocks-tier-control-file.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load(name, fname):
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(name, HERE / fname)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


ap = _load("ap", "audit-plan.py")

NOTE = ("| -[[WGT Rocks]]- | → [[WGT]] → [WGT Rocks](hook://p/WGT%20Rocks) |\n"
        "| --- | --- |\n"
        "| ... | [[WGT R0001]],  [[WGT R0002]],   |\n")


def group(control=None, note=NOTE, rocks=("WGT R0001", "WGT R0002")):
    """A minimal rock group: `<tmp>/WGT/WGT Track/WGT Rocks/`, plus a control
    file one directory up when `control` is given."""
    td = Path(tempfile.mkdtemp())
    folder = td / "WGT" / "WGT Track" / "WGT Rocks"
    folder.mkdir(parents=True)
    (td / "WGT" / ".anchor").write_text("slug: WGT\n", encoding="utf-8")
    (folder / "WGT Rocks.md").write_text(note, encoding="utf-8")
    for r in rocks:
        (folder / f"{r}.md").write_text(f"# {r}\nA rock.\n", encoding="utf-8")
    if control is not None:
        (folder.parent / "WGT Rock.md").write_text(control, encoding="utf-8")
    return folder


def verdict(folder):
    return ap.chk_rocks_tier_links_resolve(ap._rocks_note(folder), folder, None)


LIVE = ("# WGT Rock\n\n[[WGT Rock|-WGT-]] \n\nACTIVE\n"
        "[[WGT R0001|WGT:]] the first chunk\n"
        "[[WGT R0002|WGT:]] the second chunk\n")

# 1 — the migrated shape: a dead link in the CONTROL file must fail. Before the
#     fix this passed, because the rule never opened the file.
dead = LIVE.replace("WGT R0002|", "WGT R9999|")
v = verdict(group(control=dead))
check(v[0] == "fail", "a dead link in the control file FAILS")
check("WGT R9999" in v[1], "...and the message names the missing rock")
check("WGT Rock.md" in v[1], "...and says which file it was reading")

# 2 — the same group with every link live passes, so case 1 is not just noise.
check(verdict(group(control=LIVE))[0] == "pass", "a control file with live links passes")

# 3 — an import site. Neither its header (R-stone-04) nor the foreign stones
#     copied in below it belong to this group, and no local resolver can see
#     either. This is the case that caught the landmine.
imported = LIVE + "\n[[VEC Rock|-VEC-]] \n[[VEC R0001|VEC:]] someone else's rock\n"
v = verdict(group(control=imported))
check(v[0] == "pass", "an import site — foreign header AND foreign stones — is skipped")
check(ap._stone_control_suffixes() >= {" Rock", " Pebble"},
      "...headers found via the kind config, so a third kind needs no code")

# 3b — the skip must not be a blanket amnesty: this group's OWN dead stone still
#      fails when it sits in the same file as an import.
v = verdict(group(control=imported.replace("WGT R0002|", "WGT R9999|")))
check(v[0] == "fail" and "WGT R9999" in v[1],
      "...but this group's own dead stone beside an import still fails")

# 4 — the fallback survives. A group that has NOT migrated is still judged on its
#     folder-note; dropping that would trade this bug for its mirror image.
unmigrated = NOTE + "\nACTIVE\n[[WGT R9999|WGT:]] a rock that does not exist\n"
v = verdict(group(control=None, note=unmigrated))
check(v[0] == "fail", "an unmigrated group is still judged on its folder-note")
check("WGT Rocks.md" in v[1], "...and the message names the folder-note")

# 5 — the control file WINS when both exist. A group mid-migration whose stale
#     folder-note still lists a since-deleted rock must not fail for it.
v = verdict(group(control=LIVE, note=NOTE + "\nOLD\n[[WGT R9999|WGT:]] deleted\n"))
check(v[0] == "pass", "a stale folder-note is ignored once a control file exists")

print(f"\nF312 R-rocks-06 control file: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
