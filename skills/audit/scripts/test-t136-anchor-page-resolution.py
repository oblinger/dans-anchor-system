#!/usr/bin/env python3
"""T136 — the repair tool and the on-write gate contradicted each other.

`SYS/CLAUDE.md` mandates `/audit dispatch` to build or repair any masthead. On
`SYS/Staff/Scout/`, running it rewrote the title cell from `-[[SCOUT]]-` to
`-[[Scout]]-`; `R-doc-structure-02` then failed the same page with *"anchor page
(.anchor slug) carries no dispatch-masthead table"*. Run the tool, fail the
gate; satisfy the gate, the tool reports the page dirty forever. Scout burned
three edit cycles getting back to the slug form every sibling already uses.

**The cause is not a naming disagreement — it is case-insensitive-filesystem
aliasing.** `find_anchor_page` looked up `folder / f"{folder.name}.md"` and
trusted `.exists()`. On APFS `Path("Scout/Scout.md").exists()` is True when the
file is really `SCOUT.md`, and the Path that answered reports the *asked-for*
casing in `.stem` — so the tool rebuilt the title from a stem no file has ever
had, while Warden's `_has_self_masthead` reads the stem from a real directory
walk and matches case-sensitively.

**The title cell is authoritative from the PAGE STEM, not the slug.** A sweep of
1353 vault anchors found 8 whose page is deliberately the long human name behind
a short slug (`Espresso.md`/ESP, `Warden.md`/WARDEN, `Vector.md`/VEC), each
correctly titled for its page. Keying the title on the slug would have rewritten
all of them. What the slug *is* good for is finding the right page in the first
place, which is the fix.

    python3 test-t136-anchor-page-resolution.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).parent


def _load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(_HERE / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ad = _load("ad", "audit-dispatch.py")
ap = _load("ap", "audit-plan.py")

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def masthead(title, extra=""):
    return (f"# {title}\n\n"
            f"| -[[{title}]]- | → [[kmr]] → [[SYS]] |\n"
            f"| --- | --- |\n{extra}")


def anchor(folder_name, slug, pages, dirs=()):
    """Build an anchor folder; `pages` maps filename → text."""
    d = ROOT / folder_name
    d.mkdir(parents=True, exist_ok=True)
    (d / ".anchor").write_text(f"slug: {slug}\n", encoding="utf-8")
    for fn, text in pages.items():
        (d / fn).write_text(text, encoding="utf-8")
    for sub in dirs:
        (d / sub).mkdir(exist_ok=True)
    return d


# ------------------------------------------- named_exactly — the case gate

print("named_on_disk — never fabricate a stem the filesystem does not have")

scout = anchor("Scout", "SCOUT", {"SCOUT.md": masthead("SCOUT"),
                                  "SCOUT Persona.md": "# SCOUT Persona\n"})

check("the real name resolves",
      ad.named_on_disk(scout, "SCOUT.md").name, "SCOUT.md")
# The load-bearing one. On APFS the plain `.exists()` this replaced answers True
# for `Scout.md` and hands back a Path whose stem is `Scout` — a stem no file
# has. The lookup must still SUCCEED (the folder legitimately differs in case
# from its page) but must report the name that is actually there.
check("a case-variant query still resolves...",
      ad.named_on_disk(scout, "Scout.md") is not None, True)
check("...but reports the TRUE on-disk name",
      ad.named_on_disk(scout, "Scout.md").name, "SCOUT.md")
check("...whereas the OS would have handed back the fabricated stem",
      (scout / "Scout.md").stem, "Scout")
check("an absent name resolves to nothing",
      ad.named_on_disk(scout, "Nope.md"), None)
# A directory named like the page must not be mistaken for it.
(scout / "SCOUT Track").mkdir(exist_ok=True)
check("a directory is not a page", ad.named_on_disk(scout, "SCOUT Track"), None)


# ------------------------------------------------------- anchor_slug

print("\nanchor_slug — the declaration of record")

check("the slug is read from .anchor", ad.anchor_slug(scout), "SCOUT")
plain = ROOT / "Plain"
plain.mkdir(exist_ok=True)
check("no .anchor → no slug", ad.anchor_slug(plain), None)
noslug = anchor("NoSlug", "X", {"NoSlug.md": masthead("NoSlug")})
(noslug / ".anchor").write_text("code: /some/path\n", encoding="utf-8")
check("an .anchor without a slug key → no slug", ad.anchor_slug(noslug), None)


# --------------------------------------------- find_anchor_page + the title

print("\nfind_anchor_page — the slug page wins, and the title follows the page")

check("the slug page is found, with its true casing",
      ad.find_anchor_page(scout).name, "SCOUT.md")
# The bug in one assertion: the title is rebuilt from this stem, so an aliased
# stem is what wrote `-[[Scout]]-` onto a file named SCOUT.md.
check("...so the title cell rebuilds as the slug form",
      ad.find_anchor_page(scout).stem, "SCOUT")

# The persona-marker case (Staff/Boone/): folder `Boone`, slug `PROS`. Both
# `Boone.md` and `PROS.md` genuinely exist, so this is NOT case aliasing — the
# tool simply preferred the folder namesake, and repaired the marker stub while
# leaving the identity page untouched.
boone = anchor("Boone", "PROS", {
    "PROS.md": masthead("PROS"),
    "Boone.md": "# Boone\n\n| -[[Boone]]- | → [[kmr]] → [[SYS]] |\n| --- | --- |\n",
})
check("a persona stub does not win over the identity page",
      ad.find_anchor_page(boone).name, "PROS.md")

# Mid-migration (Staff/Munger/ on 2026-08-05): slug `CFO` declared, but `CFO.md`
# does not exist yet. Falling back to the folder namesake keeps the tool working
# rather than crashing on a half-landed rename.
munger = anchor("Munger", "CFO", {"Munger.md": masthead("Munger")})
check("a declared-but-absent slug page falls back to the namesake",
      ad.find_anchor_page(munger).name, "Munger.md")

# An anchor whose page is deliberately the long human name behind a short slug
# — 8 of these exist vault-wide, and the slug must not be imposed on them.
esp = anchor("Espresso", "ESP", {"Espresso.md": masthead("Espresso")})
check("a long-name page behind a short slug keeps its own name",
      ad.find_anchor_page(esp).stem, "Espresso")

# `.anchor` files without a `slug:` key are common, and their page is often a
# case-variant of the folder (`Log/NOTE/` holds `Note.md`). An exact-match
# namesake lookup skips the real page and the fallback scan then picks an
# unrelated file — this test exists because a first cut at the fix did exactly
# that, resolving `Log/NOTE` to `DATED.md` and `Topic/Misc/BOOK` to
# `001_ideas.md` on the vault sweep that caught it.
note = ROOT / "NOTE"
note.mkdir(exist_ok=True)
(note / ".anchor").write_text("code: /somewhere\n", encoding="utf-8")
(note / "Note.md").write_text(masthead("Note"), encoding="utf-8")
(note / "DATED.md").write_text(masthead("DATED"), encoding="utf-8")
check("a slugless anchor still finds its case-variant namesake",
      ad.find_anchor_page(note).name, "Note.md")
check("...and not the alphabetically-first sibling with a masthead",
      ad.find_anchor_page(note).name != "DATED.md", True)


# ------------------------------------- the two sides now agree on the title

print("\nThe tool and the gate agree — which is the whole point of T136")

for folder in (scout, boone, esp):
    page = ad.find_anchor_page(folder)
    text = page.read_text(encoding="utf-8")
    # What the gate demands ...
    gate_ok = ap._has_self_masthead(text, page.stem)
    # ... and what the tool would write, given the same page.
    tool_wants = f"-[[{page.stem}]]-"
    check(f"{folder.name}: gate accepts the page's existing title", gate_ok, True)
    check(f"{folder.name}: tool would write that same title",
          tool_wants in text, True)


# ------------------------------- R-dispatch-table-10 — the message, reworded

print("\nchk_dispatch_area_row — the message names the CELL, not a missing link")

# Scout's real masthead: the Track link IS present, in the right-hand cell,
# behind a bolded `**Track**` label. The old message said the link was absent,
# which sent Scout hunting for a break that never existed.
wrong_cell = anchor("Wc", "WC", {
    "WC.md": masthead("WC", "| **Track** | [[WC Track\\|Track]],  [[WC Backlog\\|Backlog]] |\n"),
}, dirs=["WC Track"])
verdict, msg = ap.chk_dispatch_area_row(wrong_cell / "WC.md", wrong_cell, ["Track"])
check("a bolded label in the left cell fails", verdict, "fail")
check("...and the message names the left cell, not a missing link",
      "LEFT cell" in msg and "no `[[" not in msg, True)
# The bolded form is what every real offender uses; the original pattern only
# admitted the bare word, so these fell through to the missing-link branch.
check("...the bold markers did not hide the label from the check",
      "leads with a text label" in msg, True)

# A genuinely absent row still reports as absent.
absent = anchor("Ab", "AB", {"AB.md": masthead("AB")}, dirs=["AB Track"])
verdict, msg = ap.chk_dispatch_area_row(absent / "AB.md", absent, ["Track"])
check("a truly missing row still fails", verdict, "fail")
check("...and says the masthead has no such row", "has no" in msg, True)

# Link present somewhere, but not leading any row → the third, distinct message.
buried = anchor("Bu", "BU", {
    "BU.md": masthead("BU", "| Related | [[BU Track\\|Track]] |\n"),
}, dirs=["BU Track"])
verdict, msg = ap.chk_dispatch_area_row(buried / "BU.md", buried, ["Track"])
check("a link that leads no row fails", verdict, "fail")
check("...and the message says it is present but mis-placed",
      "but not from the LEFT cell" in msg, True)

# The correct form passes.
right = anchor("Ok", "OK", {
    "OK.md": masthead("OK", "| [[OK Track\\|Track]] | [[OK Backlog\\|Backlog]] |\n"),
}, dirs=["OK Track"])
check("the left-cell-link form passes",
      ap.chk_dispatch_area_row(right / "OK.md", right, ["Track"])[0], "pass")

# No folder, no requirement.
none = anchor("Nn", "NN", {"NN.md": masthead("NN")})
check("no Track folder → nothing required",
      ap.chk_dispatch_area_row(none / "NN.md", none, ["Track"])[0], "pass")


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
