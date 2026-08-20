#!/usr/bin/env python3
"""T561 — a method-3 facet folder is decided by the facet registry, not by a plural name.

`chk_file_association_folder_structure` recognised a method-3 folder with
`re.search(r"\\s+\\w+s$", folder)` and nothing else. Reported by [[Eli]], found
while driving that anchor from 50 mechanical findings to 5; the vault-wide count
is what made it a bug rather than a nuisance:

    name-only          372 folders in scope, 271 fail   (73% wrong)
    registered facet   100 folders in scope,  48 fail

The 223 that go away are not judgment calls — `NJDB Databricks`,
`@Buck Shlegeris`, `My Dates`, `Cap tables`, `SV Wings` — company names, a
person, and ordinary topic folders whose last letter is `s`.

**§2 is the assertion that matters.** A narrowing rule is trivially made green by
narrowing too far, so §2 pins that the failures which SHOULD survive still do: a
registered-facet folder missing its index still fails, and the reference method-3
instance still passes. §4 pins the two residuals in the ruleset text, so the
narrowing cannot quietly become the whole story.

Run: python3 test-t561-facet-folder-by-registry.py
"""
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

RULESET = _HERE.parent.parent.parent / "rulesets" / "R-file-association.md"

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


INDEX = """| -[[{name}]]- | : index |
| --- | --- |
| ... | [[{item}]] |

# {name}
The index.
"""


def folder(root, name, *, index=True, items=("F001 - A thing",)):
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    for it in items:
        (d / f"{it}.md").write_text(f"# {it}\nbody\n")
    if index:
        (d / f"{name}.md").write_text(
            INDEX.format(name=name, item=items[0] if items else "none"))
    return d


def verdict(name, **kw):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".anchor").write_text("slug: ZZ\n")
        return ap.chk_file_association_folder_structure(
            folder(root, name, **kw), root, [])


print("1. A plural name that names no facet is out of scope")
# Real vault folders, all previously failing, none of them a facet folder.
for name in ("NJDB Databricks", "My Dates", "Cap tables", "SV Wings",
             "Moms Files", "@Buck Shlegeris"):
    st, msg = verdict(name, index=False)
    check(f"{name!r} passes", st, "pass")
check("...and says why, naming the suffix",
      "registered facet" in verdict("NJDB Databricks", index=False)[1], True)

print("2. A registered facet still gets the full check — the narrowing is not a mute")
# `Features` is a registered facet and [[DAS Features]] requires the index, so
# this must still fail. Without this assertion §1 is satisfied by a checker that
# passes everything.
st, msg = verdict("ZZ Features", index=False)
check("a Features folder with no index still FAILS", st, "fail")
check("...for the right reason", "missing anchor file" in msg, True)
check("a Features folder WITH a linking index passes",
      verdict("ZZ Features")[0], "pass")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    d = folder(root, "ZZ Features")
    (d / "ZZ Features.md").write_text("# ZZ Features\nno dispatch here at all.\n")
    st, msg = ap.chk_file_association_folder_structure(d, root, [])
    check("...and an index with no dispatch links still fails", st, "fail")

print("3. The registry is read from disk, not hardcoded")
names = ap._registered_facet_names()
check("it found the facet corpus", len(names) > 50, True)
check("`Features` is in it", "Features" in names, True)
check("`Pebble` is NOT — which is why 19 pebble stores need no exemption",
      "Pebble" in names, False)
check("a pebble store is out of scope",
      verdict("ZZ Pebbles", index=False)[0], "pass")
# The registry is a set of files; an empty one would silently pass everything.
check("the corpus path resolves", (ap.REPO_ROOT / "facets").is_dir(), True)

print("4. The ruleset text carries the narrowing AND its residuals")
text = RULESET.read_text(encoding="utf-8")
m = re.search(r"### RULE R-file-association-07\b.*?(?=\n### RULE |\Z)", text, re.S)
check("R-file-association-07 is present", bool(m), True)
if m:
    body = m.group(0)
    check("...says the suffix must name a registered facet",
          "registered facet" in body, True)
    check("...carries the before/after count", "271" in body and "48" in body, True)
    check("...names residual (a), the unchecked {Parent} half",
          "R-file-association-03" in body and "75" in body, True)
    check("...names residual (b), the singular/plural coincidence",
          "Derm Docs" in body, True)
    # The pebble store's OTHER failure is real and fleet-wide; it is fixed in
    # its own ruleset, and this rule must route there rather than restate it.
    check("...routes the pebble store's other failure to R-anchor-page",
          "R-anchor-page" in body, True)
    check("...and does not claim the pebble stores are fully handled here",
          "dead code" in body, True)

print("5. R-anchor-page-02 exempts a stone store — the OTHER half of T561")
STONE = _HERE.parent.parent.parent / "rulesets" / "R-anchor-page.md"


def store(root, folder_name, control_name, *, control=True, namesake=False):
    d = root / "ZZ Track" / folder_name
    d.mkdir(parents=True, exist_ok=True)
    (d / "ZZ P0001.md").write_text("# ZZ P0001\nbody\n")
    if namesake:
        (d / f"{folder_name}.md").write_text(f"# {folder_name}\nthe index.\n")
    if control:
        (d.parent / f"{control_name}.md").write_text(f"# {control_name}\ncontrol.\n")
    return d


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    d = store(root, "ZZ Pebbles", "ZZ Pebble")
    check("a pebble store with its control file one level up is exempt",
          ap.chk_entry_page_matches_slug(d, d, [])[0], "pass")
    check("...and says why",
          "stone store" in ap.chk_entry_page_matches_slug(d, d, [])[1], True)
    # The positive half is the control file. Remove it and the folder is just a
    # folder with no entry page — the rule must come back.
    (d.parent / "ZZ Pebble.md").unlink()
    check("without the control file it is NOT exempt",
          ap.chk_entry_page_matches_slug(d, d, [])[0], "fail")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    # Sleepers, not pebbles: the suffix and control name come from the stone-kind
    # registry, so a kind the code never mentions works for free.
    d = store(root, "ZZ Sleepers", "ZZ Sleeper")
    check("a sleeper store is exempt too — the kinds are read, not hardcoded",
          ap.chk_entry_page_matches_slug(d, d, [])[0], "pass")
    check("...and `_is_stone_store` derives both from the JSON",
          set(ap._stone_kind_suffixes()) >= {" Pebbles", " Sleepers", " Rocks"}, True)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    # A rock group IS an anchor by design (4 of 4 carry a namesake and .anchor),
    # so the exemption must not be what makes it pass.
    d = store(root, "ZZ Rocks", "ZZ Rock", namesake=True)
    (d / ".anchor").write_text("slug: ZZ Rocks\n")
    st, msg = ap.chk_entry_page_matches_slug(d, d, [])
    check("a rock group passes on its own namesake", st, "pass")
    check("...NOT via the stone-store exemption — a true verdict for the "
          "right reason", "stone store" in msg, False)

with tempfile.TemporaryDirectory() as td:
    # The rule still has to do its job on an ordinary folder, or the exemption
    # has been widened into a mute.
    root = Path(td)
    (root / ".anchor").write_text("slug: ZZ\n")
    plain = root / "ZZ Widgets"
    plain.mkdir()
    (plain / "a.md").write_text("# a\n")
    check("an ordinary folder with no entry page still fails",
          ap.chk_entry_page_matches_slug(plain, plain, [])[0], "fail")

stone_text = STONE.read_text(encoding="utf-8")
m2 = re.search(r"### RULE R-anchor-page-02\b.*?(?=\n### RULE |\Z)", stone_text, re.S)
check("R-anchor-page-02's text carries the exemption", bool(m2), True)
if m2:
    b = m2.group(0)
    check("...with the measured 19 of 19", "19 of 19" in b, True)
    check("...keyed to the control file, not the missing namesake",
          "circular" in b, True)
    check("...and records that rocks are unaffected", "4 of 4" in b, True)
    check("...and the measurement lesson that produced a wrong 1 of 19",
          "1 of 19" in b and "--no-cache" in b, True)

print("6. The live vault population is what the ruleset claims")
V = Path.home() / "ob/kmr"
if V.is_dir():
    PL = re.compile(r"\s+\w+s$")
    scope = fails = 0
    for d in V.rglob("*"):
        if not d.is_dir():
            continue
        if any(p.startswith(".") for p in d.relative_to(V).parts):
            continue
        if not PL.search(d.name):
            continue
        st, _ = ap.chk_file_association_folder_structure(d, V, [])
        if st == "fail":
            fails += 1
        scope += 1
    print(f"       ({scope} plural-suffix folders walked, {fails} failing)")
    check("failures are far below the 271 the name-only rule produced",
          fails < 100, True)
    check("...and not zero — the rule still has real work",
          fails > 0, True)

print()
if FAILURES:
    print(f"test-t561-facet-folder-by-registry: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t561-facet-folder-by-registry: all checks pass")
