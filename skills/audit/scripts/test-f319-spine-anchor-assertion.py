#!/usr/bin/env python3
"""F319 M5 — `spine fix` must not silently rewrite the `.anchor` beside a page.

Touching an entry page makes HookAnchor harvest its identity-cell description
into the sibling `.anchor`, and that is NOT revertible while the two disagree:
restoring `.anchor` from git and waiting for the rebuild reproduces the
overwrite, because the page still says something different. The mover's other
five assertions all read only the page, so a second file changes while every
one of them passes.

**What this file really guards is the checker, not the corpus.** The first
draft refused 107 files where 52 is right, because it compared raw cell text
instead of what HookAnchor would actually store. Each case below is pinned to
the real page that exposed it, so a future edit to `anchor_would_change` cannot
quietly re-widen it. Ground truth is `sections.rs`
(`extract_dispatch_descriptions` + `strip_own_name_prefixes`) — not this file's
model of it.

Run: python3 test-f319-spine-anchor-assertion.py
"""
from __future__ import annotations

import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import spine as sp                                                # noqa: E402
import spine_fix as sf                                            # noqa: E402

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  PASS: {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {m}")


def chk(m, cond):
    ok(m) if cond else no(m)


V = sf.VAULT

# ---- A: the `.anchor` reader is a YAML scalar reader -------------------------
print("== A: reading `description:` — .strip('\"') is wrong in BOTH directions ==")
# An UNQUOTED value that merely ends in a quotation mark. `.strip('\"')` ate it,
# and `Artifact Template Rule Sets` then read as a divergence that is not there.
chk("an unquoted value ending in a quotation mark keeps it",
    sf._unquote('document-template corpora — each defines "…in order"')
    == 'document-template corpora — each defines "…in order"')
# A genuinely quoted value, with escapes inside it — `prj/PQ/.anchor`.
chk("a fully double-quoted value unquotes and unescapes",
    sf._unquote(r'"Personal \"Quick\" Projects — dated one-off"')
    == 'Personal "Quick" Projects — dated one-off')
chk("a fully single-quoted value unquotes",
    sf._unquote("'a plain value'") == "a plain value")
chk("a bare value is untouched",
    sf._unquote("  Warm-storage of X  ") == "Warm-storage of X")
chk("a backslash escape survives", sf._unquote(r'"a \\ b"') == r'a \ b')

# ...and `anchor_desc` must actually USE it. Testing `_unquote` alone leaves the
# call site free to go back to `.strip('"')` with every assertion above still
# green — a mutation run caught exactly that hole in the first version of this
# file, which is the whole reason these two cases read a real `.anchor`.
_q = Path(tempfile.mkdtemp())
(_q / ".anchor").write_text(
    'description: "Personal \\"Quick\\" Projects — dated one-off"\n')
chk("anchor_desc unquotes through _unquote, not by stripping",
    sf.anchor_desc(_q) == 'Personal "Quick" Projects — dated one-off')
_u = Path(tempfile.mkdtemp())
(_u / ".anchor").write_text(
    'description: document-template corpora — each defines "…in order"\n')
chk("anchor_desc keeps the closing mark of an unquoted value",
    sf.anchor_desc(_u) == 'document-template corpora — each defines "…in order"')

# ---- B: what the harvest would actually store -------------------------------
print("== B: mirroring the harvest, not modelling it ==")
mux = V / "prj/ClaudiMux/MuxUX/MUX.md"
div = (V / "prj/ClaudiMux/Skill Docket App/Docket Item Viewer"
         / "DIV Dev Docs/DIV Dev Docs.md")
if not mux.is_file() or not div.is_file():
    no("the pinned vault pages are gone — re-pin this test before trusting it")
else:
    # `build_desc_with_name` prepends the display name and the harvest strips it
    # symmetrically, so this is a round-trip and not drift.
    chk("MUX: the `MuxUX — ` own-name prefix is stripped, so no divergence",
        sf.anchor_would_change(
            mux, "MuxUX — Tauri GUI overlay for tmux session management, "
                 "layout control, and agent placement.") is None)
    # `if !text.is_empty()` — a bare `: ` overwrites nothing at all.
    chk("DIV Dev Docs: an empty `: ` harvests nothing, so no divergence",
        sf.anchor_would_change(div, "") is None)
    chk("an empty description is None, not ''",
        sf.harvested_desc("", mux.parent, "MUX") is None)

    # ...and it must still fire, or it guards nothing.
    chk("a genuinely different description still refuses",
        sf.anchor_would_change(mux, "something else entirely") is not None)
    chk("a prefix that is NOT one of the anchor's own names is kept, and refuses",
        sf.anchor_would_change(
            mux, "Something Else — Tauri GUI overlay for tmux session "
                 "management, layout control, and agent placement.") is not None)

    # The two refusal classes are labelled, because they are different problems:
    # a fossil heals, a divergence loses text.
    why = sf.anchor_would_change(mux, "MUX — a completely different description")
    chk("a genuine divergence is labelled as a rewrite",
        why is not None and "would be rewritten" in why)

# ---- C: the prefix strip is iterative and bounded ----------------------------
print("== C: `strip_own_name_prefixes` — iterative, and it stops ==")
d = Path(tempfile.mkdtemp()) / "MuxUX"
d.mkdir()
(d / ".anchor").write_text("slug: MUX\ntitle: MuxUX\n")
chk("own-name prefixes strip iteratively",
    sf._strip_own_name_prefixes("MuxUX — MUX — real desc", d, "MUX") == "real desc")
chk("an em-dash inside a real description survives",
    sf._strip_own_name_prefixes("Espresso — example collection — notes", d, "MUX")
    == "Espresso — example collection — notes")
chk("an escaped pipe is unescaped before comparing",
    sf._unescape_pipes(r"a \| b") == "a | b")

# ---- D: end to end, on a page the mover would otherwise fix ------------------
print("== D: end to end — the gate refuses the WRITE, not just the comparison ==")
h = Path(tempfile.mkdtemp()) / "HBR"
h.mkdir()
page = h / "HBR.md"


def build(anchor_desc: str, cell_desc: str):
    (h / ".anchor").write_text(f"slug: HBR\ndescription: {anchor_desc}\n")
    # S03 shape: the H1 sits ABOVE the masthead, so the mover has work to do.
    page.write_text(textwrap.dedent(f"""\
        # HBR
        Orientation.

        | -[[HBR]]- | : {cell_desc}<br>→ [[kmr]] → [HBR](hook://p/HBR) |
        | --- | --- |
        | [[HBR Log]] | a child |
        """))


build("the worked example", "the worked example")
a, n, _ = sf.plan_file(page)
chk("agreeing descriptions let the S03 fix through", (a, n) == ("fixed", "S03"))

build("a META description nobody harvested", "the worked example")
before = page.read_text()
a, n, new = sf.plan_file(page)
chk("a diverging `.anchor` refuses the file", a == "refused")
chk("and the page is left byte-identical",
    new is None and page.read_text() == before)

build("the   worked\texample", "the worked example")
a, n, _ = sf.plan_file(page)
chk("a whitespace-only difference is not a divergence", a == "fixed")

# The three norm() folds, each pinned separately — and the two cases that must
# still refuse, because a fold is only safe if it hides exactly what it claims.
# Measured 2026-08-12: 4 of 30 reported divergences differed by nothing but a
# trailing period or a first-letter capital, which is a fifth of the list the
# operator had to read and dismiss by hand.
build("the worked example.", "the worked example")
a, n, _ = sf.plan_file(page)
chk("a trailing full stop is not a divergence", a == "fixed")

build("The worked example", "the worked example")
a, n, _ = sf.plan_file(page)
chk("the case of the FIRST character is not a divergence", a == "fixed")

build("The worked example.", "the worked example")
a, n, _ = sf.plan_file(page)
chk("both folds at once still agree", a == "fixed")

build("the worked Example", "the worked example")
a, n, _ = sf.plan_file(page)
chk("case AFTER the first character still refuses — a slug's case is meaning",
    a == "refused")

build("the worked example. it does two things", "the worked example")
a, n, _ = sf.plan_file(page)
chk("an INTERIOR full stop is not stripped — only a trailing one",
    a == "refused")

(h / ".anchor").write_text("slug: HBR\n")
a, n, _ = sf.plan_file(page)
chk("an `.anchor` declaring no description has nothing to lose", a == "fixed")

# A page that does NOT front its folder is not the harvest authority, so the
# gate must not apply to it — otherwise it refuses on its neighbour's `.anchor`.
(h / ".anchor").write_text("slug: HBR\ndescription: something quite different\n")
other = h / "HBR Log.md"
other.write_text(page.read_text().replace("[[HBR]]", "[[HBR Log]]"))
a, n, _ = sf.plan_file(other)
chk("a non-fronting page is not gated on its folder's `.anchor`", a == "fixed")

# ---- E: the two-page anchor — only ONE page can rewrite the `.anchor` -------
# A folder whose slug differs from its name holds two pages that BOTH front it:
# the slug-named anchor page and a folder-named marker stub pointing at it.
# HookAnchor routes the harvest on the slug-keyed question (T051), so the stub
# cannot touch the `.anchor` — and a guard that refuses it is protecting a write
# that will not happen. Measured 2026-08-12: three of the vault's 30 reported
# divergences were exactly this (`Atticus.md`, `Munger.md`, `Areas of Thought.md`).
print("== E: two pages front the folder; only the slug-named one owns .anchor ==")
g = Path(tempfile.mkdtemp()) / "Atticus"
g.mkdir()
(g / ".anchor").write_text(
    "slug: ATT\ndescription: the Quartermaster's identity home\n")


def two_page(stem: str, cell_desc: str) -> Path:
    p = g / f"{stem}.md"
    p.write_text(textwrap.dedent(f"""\
        # {stem}
        Orientation.

        | -[[{stem}]]- | : {cell_desc}<br>→ [[kmr]] → [{stem}](hook://p/{stem}) |
        | --- | --- |
        | [[ATT Log]] | a child |
        """))
    return p


stub = two_page("Atticus", "Character/persona name for the agent at [[ATT]]")
real = two_page("ATT", "a description that disagrees too")

chk("the slug-named page IS the description home", sp.is_description_home(real))
chk("the folder-named marker stub is NOT", not sp.is_description_home(stub))
chk("but BOTH still front the folder — the union is a different question",
    sp.Spine(real).fronts_folder and sp.Spine(stub).fronts_folder)

a, n, _ = sf.plan_file(stub)
chk("so the stub is fixed despite disagreeing with the `.anchor`", a == "fixed")
a, n, _ = sf.plan_file(real)
chk("while the real anchor page still refuses on the same disagreement",
    a == "refused")

# No slug declared → the folder namesake is the home, exactly as before T051.
(g / ".anchor").write_text("description: the Quartermaster's identity home\n")
chk("with no slug, the folder namesake is the description home",
    sp.is_description_home(stub) and not sp.is_description_home(real))

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
