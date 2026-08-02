#!/usr/bin/env python3
"""T090 — a linkless row of bolded prose is a section label, and it stays.

The mirror of T088: that defect kept rows it should drop, this one dropped a
row it should keep. `design/DAS Design.md` separates its per-group rows from
the profiles block below with

    |  | **SKILL GROUPS** |

and the empty-row test read that as content-free, so `--fix` would have
deleted it and collapsed two visually distinct zones into one undifferentiated
block. Found 2026-08-01 repairing T077, on a table the tool otherwise called
clean — which is what made it invisible: the only report line was "dropped 1
empty row", indistinguishable from removing a stub.

Bold is the whole signal, and section 2 is why it has to stay that narrow: an
unbolded linkless row IS the stub the empty-row drop exists to remove, so
widening this to "any prose" would retire that drop entirely. The vault-wide
sweep that accepted this change spared 127 rows and still dropped 389.

Run: python3 test-t090-label-rows.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
loader = importlib.machinery.SourceFileLoader("ad_mod", str(HERE / "audit-dispatch.py"))
spec = importlib.util.spec_from_loader("ad_mod", loader)
ad = importlib.util.module_from_spec(spec)
sys.modules["ad_mod"] = ad
loader.exec_module(ad)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


ad._BASENAME_INDEX = {"ZZA Docs"}
ad._HA_COMMANDS = set()

BREADCRUMB = "| -[[ZZA]]- | → [[kmr]] → [[ZZA]](hook://p/ZZA)<br>: fixture |"
SEP = "| --- | --- |"
LIVE = "| Skill | [[ZZA Docs\\|User Docs]] |"
LABEL = "|  | **SKILL GROUPS** |"            # the exact row T077 hit
LABEL_L = "| **Code trees** | _grows over time_ |"
STUB = "| Examples |  |"
STUB2 = "| Design | see below |"


def build(rows):
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td) / "ZZA"
        folder.mkdir()
        (folder / ".anchor").write_text("slug: ZZA\n", encoding="utf-8")
        page = folder / "ZZA.md"
        page.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return ad.rebuild([ad.Row(r) for r in rows], folder, page, "ZZA")


print("1. The label row survives the rebuild")
new, rep = build([BREADCRUMB, SEP, LIVE, LABEL])
check("it is classified as a label", ad.Row(LABEL).is_label)
check("it is still in the rebuilt table", LABEL in new, new)
check("and nothing was reported dropped", rep["dropped_empty_rows"] == [],
      rep["dropped_empty_rows"])
check("a bolded FIRST cell counts too", ad.Row(LABEL_L).is_label)

print("2. Bold is the whole signal — unbolded stubs still go")
check("a wholly empty row is not a label", not ad.Row(STUB).is_label)
check("nor is unbolded prose", not ad.Row(STUB2).is_label)
new, rep = build([BREADCRUMB, SEP, LIVE, STUB, STUB2])
check("both are still dropped", len(rep["dropped_empty_rows"]) == 2,
      rep["dropped_empty_rows"])
check("neither reached the table",
      STUB not in new and STUB2 not in new, new)

print("3. A row with links is never a label, however bold")
bold_linked = "| **Design** | [[ZZA Docs]] |"
check("bolded and linked is a normal row", not ad.Row(bold_linked).is_label)
check("but it is kept anyway, on its link", bold_linked in build(
    [BREADCRUMB, SEP, bold_linked])[0])
# The label exemption must not become a back door around the T088 drop.
bold_dead = "| **Design** | [[ZZA Gone]] |"
check("a bolded row whose only link is dead is still dead",
      ad.Row(bold_dead).is_dead and not ad.Row(bold_dead).is_label)
check("and it is still dropped",
      len(build([BREADCRUMB, SEP, LIVE, bold_dead])[1]["dropped_dead_rows"]) == 1)

print(f"\ntest-t090-label-rows: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
