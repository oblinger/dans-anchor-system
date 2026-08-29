#!/usr/bin/env python3
"""test-t197-group-selector.py — a spec declares its own group; the selector reads it.

`R-facet-spec` used to reach its target set by SUBTRACTION: a `DAS *.md` glob minus
a hand-listed complement that had grown to **48 clauses** — a 21-name brace
expression plus 27 separate `!DAS <name>.md` terms. Every clause was appended by an
agent after a finding fired on a document the list had not yet heard of, so a new
discipline was born *failing* the facet rules and the fix was always to grow the
negative. The positive definition ("a discipline facet selects nothing of its own")
existed in prose in each spec's opening line and nothing mechanical read it.

T197 Q1 (A), Dan 2026-08-11: give the group a machine-readable declaration. The
declaration is a frontmatter `group:` key on the spec itself — [[DAS Facet]] §
Facet groups is explicit that *"the group is declared in the spec, never encoded in
which folder the spec lives in"*, because a facet can legitimately change groups
(Brief is a slot inline and a file as a sidecar).

What this file protects:

- the four group values, and only those, are selectable;
- comma lists work, because a real spec spans two groups (`DAS Template`);
- a document with no `group:` key is selected by NOTHING — that is what keeps the
  selector positive, and it is also the residual under-inclusion risk;
- a MISSPELLED value raises rather than silently dropping the spec out of scope.
  Under-inclusion reads as a clean green, which is the worse half of the trade, so
  the one case that can be distinguished from "not a spec" is refused loudly;
- `group:` is a distinct selector kind and does not disturb the four that existed.

Usage: python3 test-t197-group-selector.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ap"] = m
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


def build(files: dict) -> tuple[Path, list[Path]]:
    root = Path(tempfile.mkdtemp()) / "Demo"
    root.mkdir(parents=True)
    (root / ".anchor").write_text("slug: Demo\n", encoding="utf-8")
    out = []
    for name, body in files.items():
        p = root / name
        p.write_text(body, encoding="utf-8")
        out.append(p)
    return root, out


FM = "---\ndescription: d\ngroup: {g}\n---\n\n# {n}\nline.\n"
NOFM = "# {n}\nline.\n"


def main():
    m = _load()

    # 0 — parse_selector recognises the kind at all, and leaves the others alone.
    check(m.parse_selector("group: file") == ("group", "file", None),
          "`group:` parses as its own selector kind")
    check(m.parse_selector("always") == ("always", "", None),
          "`always` still parses as always (control)")
    check(m.parse_selector("sentinel: ^# X") == ("sentinel", "^# X", None),
          "`sentinel:` still parses as sentinel (control)")
    check(m.parse_selector("file: *.md") == ("file", "*.md", None),
          "`file:` still parses as file (control)")
    check(m.parse_selector("**/*.md") == ("file", "**/*.md", None),
          "a bare glob is still a file glob (control)")

    root, files = build({
        "DAS Backlog.md": FM.format(g="file", n="DAS Backlog"),
        "DAS Rocks.md": FM.format(g="folder", n="DAS Rocks"),
        "DAS Brief.md": FM.format(g="slot", n="DAS Brief"),
        "DAS markdown.md": FM.format(g="discipline", n="DAS markdown"),
        "DAS Template.md": FM.format(g="file, folder", n="DAS Template"),
        "DAS Facets.md": "---\ndescription: the index\n---\n\n# DAS Facets\nline.\n",
        "DAS Legacy.md": NOFM.format(n="DAS Legacy"),
    })
    by = {p.name: p for p in files}

    def sel(arg):
        return {p.name for p in m.match_targets("group", arg, files, root)}

    # 1 — each value selects exactly its own members.
    check(sel("file") == {"DAS Backlog.md", "DAS Template.md"},
          "`group: file` selects the file specs, including the two-group spec")
    check(sel("folder") == {"DAS Rocks.md", "DAS Template.md"},
          "`group: folder` selects the folder specs, including the two-group spec")
    check(sel("slot") == {"DAS Brief.md"}, "`group: slot` selects the slot spec")
    check(sel("discipline") == {"DAS markdown.md"},
          "`group: discipline` selects the discipline")

    # 2 — THE CHANGE. The union of the three non-discipline groups is R-facet-spec's
    #     new target set, and the discipline is out by declaring what it is.
    got = sel("file, folder, slot")
    check(got == {"DAS Backlog.md", "DAS Rocks.md", "DAS Brief.md", "DAS Template.md"},
          "`group: file, folder, slot` is the facet-spec target set")
    check("DAS markdown.md" not in got,
          "a discipline is excluded by its own declaration, not by a name list")

    # 3 — no declaration means no membership, in EITHER direction. This is what
    #     makes the selector positive; it is also the residual under-inclusion risk,
    #     and it is asserted so the risk is a tested property rather than a surprise.
    check(m.declared_groups(by["DAS Facets.md"]) == set(),
          "an index page with frontmatter but no `group:` declares nothing")
    check(m.declared_groups(by["DAS Legacy.md"]) == set(),
          "a page with no frontmatter at all declares nothing")
    for v in m.GROUP_VALUES:
        if by["DAS Facets.md"].name in sel(v) or by["DAS Legacy.md"].name in sel(v):
            check(False, f"an undeclared page leaked into `group: {v}`")
            break
    else:
        check(True, "an undeclared page is selected by NO group value")

    # 4 — a typo raises. Silently dropping the spec would be a green that means
    #     nothing, which is the failure mode this whole change trades into.
    #     `File` is NOT a typo — case is normalised on the read side (§5) — so the
    #     fixture has to be a value the vocabulary genuinely does not contain.
    root2, files2 = build({"DAS Typo.md": FM.format(g="files", n="DAS Typo")})
    try:
        m.match_targets("group", "file", files2, root2)
        check(False, "a misspelled group value raises")
    except ValueError as e:
        check("files" in str(e) and "DAS Typo" in str(e),
              "a misspelled group value raises, naming the file and the bad value")
    root2b, files2b = build({"DAS Case.md": FM.format(g="File", n="DAS Case")})
    check({p.name for p in m.match_targets("group", "file", files2b, root2b)}
          == {"DAS Case.md"},
          "a merely mis-CASED value is normalised, not refused (control)")

    # 5 — case and quoting tolerance on the READ side, so a spec is not silently
    #     unselected for cosmetic reasons the author cannot see.
    root3, files3 = build({"DAS Q.md": "---\ngroup: \"file\"\n---\n\n# DAS Q\nx.\n",
                           "DAS U.md": "---\ngroup: FILE\n---\n\n# DAS U\nx.\n",
                           "DAS L.md": "---\ngroup: [file, slot]\n---\n\n# DAS L\nx.\n"})
    names = {p.name for p in m.match_targets("group", "file", files3, root3)}
    check(names == {"DAS Q.md", "DAS U.md", "DAS L.md"},
          "quoted, upper-cased and YAML-list spellings all read as `file`")

    # 6 — the vocabulary is a named constant, so widening it is a deliberate edit.
    check(m.GROUP_VALUES == ("file", "folder", "slot", "discipline"),
          "GROUP_VALUES is exactly the four groups DAS Facet defines")

    print("-" * 40)
    print(f"T197 group selector: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
