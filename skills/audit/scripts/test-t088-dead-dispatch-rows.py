#!/usr/bin/env python3
"""T088 — a dispatch row whose every link points at nothing is dead, and goes.

The runbook lists "remove rows pointing at deleted children" among the fixes
`/audit dispatch` applies mechanically without asking. It never applied that
one: the keep/drop test asked whether a row contained link *syntax*, never
whether the link had a *target*. Found 2026-08-01 finishing T087 — after
`SKA Audit Design/` was archived to Yore, `SKA audit.md` kept

    | [[SKA Audit Design|Design]]  | [[SKA Audit PRD|PRD]],   |

whose two links both resolved to nothing, and the tool reported the table
"already in good form" on two consecutive runs. Removing the row by hand is
exactly what the never-hand-author-a-dispatch-table rule exists to prevent.

Two decisions read links, and BOTH had to learn about resolution — fixing only
the keep/drop test would have let the carry-forward safety net rescue the dead
link into a Related row and undo the drop in the same pass. That interaction is
what section 3 exists to pin.

Section 5 pins the conservative half, which matters more than the drop: this
tool WRITES to anchor pages, so a row it cannot judge is a row it must not
delete. Markdown hrefs (`file://`, `https://`) are unresolvable from here, so
their presence keeps a row alive.

Run: python3 test-t088-dead-dispatch-rows.py
"""
import contextlib
import importlib.machinery
import importlib.util
import io
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


def ok(name):
    global PASS
    PASS += 1
    print(f"  PASS: {name}")


def no(name, detail=""):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


def check(name, cond, detail=""):
    ok(name) if cond else no(name, detail)


# Both resolvers are stubbed rather than consulted, so the fixtures state their
# own ground truth instead of depending on what happens to sit in the vault or
# in the HookAnchor command table.
ad._BASENAME_INDEX = {"ZZA Docs", "ZZA Log", "ZZA Alive", "DAS Audit",
                      "ZZA Folder"}
ad._HA_COMMANDS = {"zza command"}

BREADCRUMB = "| -[[ZZA]]- | → [[kmr]] → [[ZZA]](hook://p/ZZA)<br>: fixture |"
SEP = "| --- | --- |"
LIVE = "| Skill | [[ZZA Docs\\|User Docs]], [[ZZA Log\\|Log]] |"
# The exact shape T087 hit: two plain, unstruck links to archived docs.
DEAD = "| [[ZZA Audit Design\\|Design]]  | [[ZZA Audit PRD\\|PRD]],   |"
MIXED = "| Related | [[ZZA Alive]], [[ZZA Gone]] |"
STRUCK = "| Design | ~~[[ZZA Docs\\|Design]]~~ |"
HREF_ONLY = "| Skill | [SKILL](file:///Users/x/.claude/skills/zza/SKILL.md) |"
HREF_PLUS_DEAD = "| Skill | [[ZZA Gone]], [SKILL](file:///Users/x/SKILL.md) |"
EMPTY = "| Examples |  |"


def build(rows):
    """Run the rebuild over a table and return (new_lines, report)."""
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td) / "ZZA"
        folder.mkdir()
        (folder / ".anchor").write_text("slug: ZZA\n", encoding="utf-8")
        page = folder / "ZZA.md"
        page.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return ad.rebuild([ad.Row(r) for r in rows], folder, page, "ZZA")


print("1. The T087 row — plain links to archived docs — is dropped")
new, rep = build([BREADCRUMB, SEP, LIVE, DEAD])
check("the dead row is gone from the rebuilt table",
      not any("ZZA Audit Design" in l for l in new), new)
check("it is reported under dropped_dead_rows",
      len(rep["dropped_dead_rows"]) == 1, rep["dropped_dead_rows"])
check("NOT miscounted as an empty row — the two say different things",
      rep["dropped_empty_rows"] == [], rep["dropped_empty_rows"])
check("the live row survives untouched", LIVE in new, new)
check("the breadcrumb is still preserved verbatim", new[0] == BREADCRUMB)

print("2. A row mixing live and dead links keeps its curated status")
new, rep = build([BREADCRUMB, SEP, MIXED])
check("the mixed row is kept", MIXED in new, new)
check("nothing is reported dead", rep["dropped_dead_rows"] == [])
check("the resolving link is what kept it",
      "wiki:ZZA Alive" in ad.Row(MIXED).live_links)
check("the unresolvable one is invisible to the link universe",
      "wiki:ZZA Gone" not in ad.Row(MIXED).live_links,
      ad.Row(MIXED).live_links)

print("3. The safety net does not rescue the dead link back in")
new, rep = build([BREADCRUMB, SEP, LIVE, DEAD])
check("carried_forward is empty", rep["carried_forward"] == [],
      rep["carried_forward"])
check("no Related row was synthesized to hold the corpse",
      not any("ZZA Audit PRD" in l for l in new), new)

print("4. A struck link is dead by declaration, resolvable target or not")
# `~~[[X]]~~` is the maintenance pass saying the target is gone by hand; the
# fixture's target DOES resolve, so only the strikethrough can be deciding.
check("the struck link is not counted live", ad.Row(STRUCK).live_links == [],
      ad.Row(STRUCK).live_links)
check("so a wholly-struck row is dead", ad.Row(STRUCK).is_dead)
new, rep = build([BREADCRUMB, SEP, LIVE, STRUCK])
check("and it is dropped", not any("~~" in l for l in new), new)

print("5. A row this tool cannot judge is a row it must not delete")
# Every assertion here came from the vault-wide dry sweep run before this
# check was allowed to write. The first pass condemned 417 rows across 121
# anchors; all but a handful were false positives from a resolver that only
# knew `.md` files. The drop is destructive, so the resolver's blind spots ARE
# the damage — each class it could not see is pinned below.
check("an href-only row has a live link key",
      ad.Row(HREF_ONLY).live_links != [], ad.Row(HREF_ONLY).live_links)
check("so it is never dead", not ad.Row(HREF_ONLY).is_dead)
check("an href keeps a row alive even beside a dead wiki-link",
      not ad.Row(HREF_PLUS_DEAD).is_dead, ad.Row(HREF_PLUS_DEAD).live_links)
new, rep = build([BREADCRUMB, SEP, HREF_PLUS_DEAD])
check("and the rebuild keeps it", HREF_PLUS_DEAD in new, new)
check("a heading link lives or dies with its file",
      ad.wiki_target_resolves("ZZA Alive#Section")
      and not ad.wiki_target_resolves("ZZA Gone#Section"))
check("a folder target resolves — the repair is an index page, not a delete",
      ad.wiki_target_resolves("ZZA Folder"))
check("a HookAnchor command resolves — catalog rows name commands, not files",
      ad.wiki_target_resolves("ZZA Command"))
check("so a catalog row of command names is not dead",
      not ad.Row("| **Code trees** | [[ZZA Command]] |").is_dead)
check("a non-breadcrumb `hook://` row is unjudgeable, so it stays",
      not ad.Row("| docs | [d](hook://p/docs), [[ZZA Gone]] |").is_dead)

print("5b. If the HookAnchor resolver did not load, nothing is dropped")
# Absence of evidence from a resolver that failed to start is not evidence of
# absence, and this check deletes rows.
saved_cmds, saved_avail = ad._HA_COMMANDS, ad._HA_AVAILABLE
try:
    ad._HA_COMMANDS, ad._HA_AVAILABLE = set(), False
    check("a would-be dead row survives", not ad.Row(DEAD).is_dead)
    _, rep = build([BREADCRUMB, SEP, LIVE, DEAD])
    check("and the rebuild drops nothing", rep["dropped_dead_rows"] == [],
          rep["dropped_dead_rows"])
finally:
    ad._HA_COMMANDS, ad._HA_AVAILABLE = saved_cmds, saved_avail
check("the fail-safe is restored for the rest of the run", ad._HA_AVAILABLE)

print("6. Dead links are still links — a dead row is not an empty one")
r = ad.Row(DEAD)
check("Row.links sees both", len(r.links) == 2, r.links)
check("Row.live_links sees neither", r.live_links == [], r.live_links)
check("Row.is_dead is true", r.is_dead)
check("has_links is false — dead rows never reach the keep branch",
      not r.has_links)
check("an empty row is not 'dead' — it never had a target",
      not ad.Row(EMPTY).is_dead)
check("a fully live row is not dead", not ad.Row(LIVE).is_dead)

print("7. The tool now says something instead of 'already in good form'")
new, rep = build([BREADCRUMB, SEP, LIVE, DEAD])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ad.print_report("ZZA", Path("/tmp/ZZA.md"),
                    [ad.Row(x) for x in [BREADCRUMB, SEP, LIVE, DEAD]],
                    new, rep, False)
out = buf.getvalue()
check("the report names the dead row", "dead row(s)" in out, out)
check("it quotes the row it dropped", "ZZA Audit Design" in out, out)
check("and no longer claims the table was already in good form",
      "already in good form" not in out, out)
new2, rep2 = build([BREADCRUMB, SEP, LIVE])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ad.print_report("ZZA", Path("/tmp/ZZA.md"),
                    [ad.Row(x) for x in [BREADCRUMB, SEP, LIVE]],
                    new2, rep2, False)
check("a genuinely clean table still reports clean",
      "already in good form" in buf.getvalue(), buf.getvalue())

print(f"\ntest-t088-dead-dispatch-rows: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
