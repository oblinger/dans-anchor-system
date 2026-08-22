#!/usr/bin/env python3
"""test-t581-arrow-link-picking.py — TINK T581.

`queries-render.py::_pick_arrow_link` decides which `→ [[…]]` on a backlog row
is the row's OWN doc. That choice becomes the LINK the user clicks on
`{slug} queries.md`, so getting it wrong puts a wrong or dead link on the one
surface Dan reads.

TWO INDEPENDENT DEFECTS, fixed together and pinned separately here.

1. IT SCANNED THE RAW LINE, so an arrow-link written inside backticks counted
   as a pointer. Found live: T578's body explains that `--body` is discarded
   "when the row carries a `→ [[doc]]` pointer", and the render turned that
   illustration into the row's link — `- [[doc]] — **[Verify]** Nothing to
   check by hand…`. Rows about the backlog machinery talk about pointer syntax
   constantly, so this is not an exotic shape.

2. ITS OWN-DOC TEST WAS `basename.startswith(f"{identifier} ")`, written
   against the legacy `F332 — Title` filename — the only one of the vault's
   THREE permanent naming conventions that puts the row identifier at the head
   of the name. Under F298 (`TINK F332 - Title`) and F300 (`TINK332 - Title`)
   it matches nothing, so every row minted since 2026-08-02 failed the test and
   fell through to `matches[0]`.

   Defect 2 is the wider one BECAUSE IT IS SILENT: on most rows the first arrow
   IS the own-doc arrow, so the fallback and the right answer agree and nothing
   looks wrong. It only surfaces when a row mentions another doc first — and
   then it surfaces as a wrong link rather than an error. audit-q hit the same
   stale test and fixed it 2026-08-19 (after C24/C48/C50 had been silently
   passing on eight rows); the fix was never propagated to the render.

The two defects interact, which is why a fix for either alone is not enough:
with the own-doc test broken, EVERY row is on the `matches[0]` fallback, so a
prose arrow anywhere before the real one wins. That is asserted below.
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qr", HERE / "queries-render.py")
qr = importlib.util.module_from_spec(spec)
sys.modules["qr"] = qr
spec.loader.exec_module(qr)

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


pick = qr._pick_arrow_link

# ============================================================
print("== A: a code-span arrow is prose, not a pointer (defect 1) ==")
# ============================================================

# THE EXACT SHAPE FOUND LIVE, reduced. T578 has no doc of its own and its body
# describes the pointer syntax inside a code span.
t578 = ("- **T578 — `state set --body` is silently discarded on a doc-backed "
        "row** [Verify] — reports `updated <row>` and writes nothing when the "
        "row carries a `→ [[doc]]` pointer. ^T578")
if pick(t578, "T578") is None:
    ok("a row whose ONLY arrow is inside backticks has no pointer at all")
else:
    no(f"the code-span arrow was picked as the pointer: {pick(t578, 'T578')!r}")

# The same illustration must not outrank a real pointer that follows it.
mixed = ("- **T578 — x** [Verify] — a row carrying a `→ [[doc]]` pointer "
         "behaves differently — → [[TINK578 - The real doc|T578]] ^T578")
if pick(mixed, "T578") == "TINK578 - The real doc|T578":
    ok("a real pointer wins over a code-span illustration that precedes it")
else:
    no(f"the illustration beat the real pointer: {pick(mixed, 'T578')!r}")

# Backticks must not eat a legitimate pointer that merely sits near code.
near = ("- **T900 — x** [Ready] — → [[TINK900 - Title|T900]] — the fix is in "
        "`_pick_arrow_link`, which scans `line`. ^T900")
if pick(near, "T900") == "TINK900 - Title|T900":
    ok("stripping spans does not disturb a pointer outside them")
else:
    no(f"a legitimate pointer was lost to span-stripping: {pick(near, 'T900')!r}")

# A CODE SPAN INSIDE THE LINK'S OWN DISPLAY ALIAS MUST SURVIVE INTACT. This is
# a regression the first cut of the T581 fix introduced and a vault-wide diff
# of old-picker vs new-picker caught: deciding on the stripped line is right,
# but the returned text must be sliced from the ORIGINAL. ATT's F054 alias is
# exactly this shape and came back with spaces where `bridge run` belongs.
alias = ("- **F054 — x** [Ready] — → [[ATT054 - bridge run|F054 — `bridge run`: "
         "unattended remote work proves it is alive]] ^F054")
got = pick(alias, "F054")
if got == "ATT054 - bridge run|F054 — `bridge run`: unattended remote work proves it is alive":
    ok("a code span inside the link's display alias is returned intact")
else:
    no(f"span-stripping leaked into the returned text: {got!r}")

# The property the slice relies on, asserted directly rather than assumed:
# stripping must PRESERVE LENGTH, or the offsets mean different things in the
# two strings and the slice silently returns the wrong characters.
for probe in ("a `b` c", "`x`", "no spans", "`a``b`", "trailing `unclosed"):
    if len(qr._strip_code_spans(probe)) != len(probe):
        no(f"_strip_code_spans changed length on {probe!r} — the slice is unsafe")
        break
else:
    ok("_strip_code_spans preserves length, which is what makes the slice valid")

# ============================================================
print("== B: all three naming conventions are recognised (defect 2) ==")
#
# These coexist in the vault permanently and are never migrated, so the test
# is over all three rather than over the current one.
# ============================================================

CONVENTIONS = [
    ("legacy F300-era", "F332 — Programmable Permissions", "F332"),
    ("F298 slug-prefixed", "TINK F332 - Programmable Permissions", "F332"),
    ("F300 fused", "TINK332 - Programmable Permissions", "F332"),
]
for label, basename, ident in CONVENTIONS:
    line = (f"- **{ident} — x** [Ready] — see → [[Some Other Doc]] first, "
            f"then → [[{basename}|{ident}]] ^{ident}")
    got = pick(line, ident)
    if got == f"{basename}|{ident}":
        ok(f"{label}: the own doc is found even behind a prose arrow")
    else:
        no(f"{label}: picked {got!r}, not the own doc")

# The T-row form under the fused convention — the shape every row minted today
# takes, and the one the old `startswith` test could never match.
trow = ("- **T575 — Build YOKE** [Verify] — spec is → [[ASR013 - A remote-worker "
        "paradigm|ASR013]] — → [[TINK575 - YOKE, one researcher|T575]] ^T575")
if pick(trow, "T575") == "TINK575 - YOKE, one researcher|T575":
    ok("a T-row's fused-form doc outranks another anchor's doc mentioned first")
else:
    no(f"the T-row picked {pick(trow, 'T575')!r} — the foreign doc won")

# THE INTERACTION, stated as its own case. This is what the live bug actually
# was: with the own-doc test broken every row rides `matches[0]`, so the FIRST
# arrow wins regardless of what it points at. If defect 2 regresses, this is
# the assertion that catches it while the others still pass.
if pick(trow, "T575") != "ASR013 - A remote-worker paradigm|ASR013":
    ok("and it is NOT the `matches[0]` fallback — the own-doc test really ran")
else:
    no("the fallback answered; the own-doc test is matching nothing again")

# ============================================================
print("== C: the fallback and the negative cases still behave ==")
# ============================================================

if pick("- **T001 — x** [Ready] — no arrows here at all. ^T001", "T001") is None:
    ok("a row with no arrow link has no pointer")
else:
    no("an arrow was invented from a row that has none")

# A row with only foreign arrows still gets the first one — the fallback is
# deliberate (it is better to link something than nothing) and stays.
foreign = "- **T002 — x** [Ready] — → [[Some Doc]] and → [[Other Doc]] ^T002"
if pick(foreign, "T002") == "Some Doc":
    ok("with no own doc, the FIRST arrow is still the fallback")
else:
    no(f"the fallback changed: {pick(foreign, 'T002')!r}")

# Last-wins among several own-doc arrows (the original T012 rule).
dup = ("- **F230 — x** [Ready] — → [[F230 — Old Title]] superseded by "
       "→ [[F230 — New Title]] ^F230")
if pick(dup, "F230") == "F230 — New Title":
    ok("among several own-doc arrows the LAST wins, as T012 ruled")
else:
    no(f"T012's last-wins rule broke: {pick(dup, 'F230')!r}")

# A number that merely shares a prefix is not the same row.
prefix = "- **T57 — x** [Ready] — → [[TINK575 - Something|T575]] ^T57"
if pick(prefix, "T57") == "TINK575 - Something|T575":
    ok("T575 is not T57's doc — it falls back rather than false-matching")
else:
    no("a prefix number was mistaken for the row's own doc")

# The letter still discriminates in the two forms that carry it: F332's doc is
# not T332's. (Under the fused form it cannot, by construction — see the
# docstring — and slug+number is unique within an anchor anyway.)
lettered = "- **T332 — x** [Ready] — → [[F332 — Feature Title]] ^T332"
if not qr._row_basename_is_own_doc("F332 — Feature Title", "T332"):
    ok("in a lettered filename the KIND letter still discriminates F from T")
else:
    no("F332's doc was accepted as T332's own")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
