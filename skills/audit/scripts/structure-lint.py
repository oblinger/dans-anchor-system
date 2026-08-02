#!/usr/bin/env python3
"""Ratchet lint — a checker may not re-spell what a structure IS (T099).

`audit-plan.py` is ~5,000 lines in which checkers kept re-deciding what a heading
is, what a fence is, what a table row is. An AST census found **129 private
spellings across 67 defs**, and nearly every finding of the F296 scan was a
checker that did not call the shared helper. Three classes have since been
converted to primitives — fence (`_FENCE_RE` / `_fenced_mask`), heading
(`_H1_RE` / `_head_h1` / `_H2_RE`), table (`_TABLE_ROW_RE` / `_table_blocks`) —
each opened by a defect, each measured.

67 defs is too diffuse to convert in one refactor, so the durable close is not
finishing the conversion — it is making the **130th spelling impossible to add
silently**. This is that guard.

**It is a ratchet, not a gate.** A hard "no private spellings" rule would fail on
the ~46 sites that legitimately remain (wiki-link and rule-declaration, both
measured and neither yet opened by a defect — and per the discipline this work
has run on, a helper is speculation until a defect names it). So the baseline
freezes what exists today, and the lint fails on anything ABOVE it. When a class
is converted the baseline shrinks and the ratchet tightens; it can never loosen
without an explicit, reviewable edit to the baseline file.

Read off the AST rather than grepped, for the reason the fence assertion in
`test-t099-fenced-mask.py` gives: review is what missed the second and third copies
of the fence toggle, and a text scan cannot tell a live recogniser from the
docstrings that now explain why the recognisers are gone. The census's own first
cut made exactly that mistake, reporting heading at 55 by counting docstrings,
`#` comments, and f-string EMITTERS — `f"# {name}"` writes a heading, it does not
recognise one.

    python3 structure-lint.py                # check against the baseline
    python3 structure-lint.py --report       # show every site, grouped
    python3 structure-lint.py --write-baseline
"""
import ast
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "audit-plan.py"
BASELINE = HERE / "structure-lint-baseline.json"

# The calls that make a string literal a RECOGNISER rather than a value. An
# emitter (`f"# {name}"`, `"| " + cell`) never reaches one of these.
#
# `split` is deliberately ABSENT. `re.split` with an anchored pattern would be a
# recogniser, but `cells = line.split("|")` is by far the commoner spelling and is
# not one — it takes a row already known to be a row and divides it. Counting it
# put six cell-splitters in the table class, which is the same mistake the census's
# first cut made with f-string emitters: parsing a structure is not recognising it.
_RE_FUNCS = {"match", "search", "compile", "fullmatch", "finditer", "findall", "sub"}
_STR_FUNCS = {"startswith", "endswith"}

# What each class looks like when spelled by hand. Deliberately keyed on the
# ANCHORED forms: `^#`, `^|`, a fence marker, `[[`, a RULE declaration. A literal
# mentioning `#` in passing (an SVG `url(#id)` fragment — the one census false
# positive, `chk_svg_no_orphan_defs`) does not anchor and is not counted.
CLASSES = {
    "fence": re.compile(r"(?:```|~~~)"),
    "heading": re.compile(r"\^(?:\\s\*|\s|\[ \]\{0,3\}| \{0,3\})*#|\A#+ "),
    "table": re.compile(r"\^(?:\\s\*|\s|\[ \]\{0,3\}| \{0,3\})*\\?\||\A\|"),
    "wiki-link": re.compile(r"\\?\[\\?\["),
    "rule-decl": re.compile(r"RULE\s+R-|\^#+\\s\*RULESET|RULESET\s+R-"),
}

# The defs that are ALLOWED to spell a structure — they are the primitive, or the
# module-level constant that is. A site here is the single definition the rest of
# the file is supposed to route through.
PRIMITIVES = {
    "<module>",          # _FENCE_RE, _H1_RE, _H2_RE, _TABLE_ROW_RE, _TABLE_SEP_RE, _SUMMARY_ROW_RE …
    "_fenced_mask", "_strip_fenced", "_mask_code", "_code_masked_lines",
    "_head_h1", "_first_h1", "_h2_titles", "_h2_headings", "_section_body",
    "_is_table_row", "_table_blocks", "_table_data_rows", "_row_cells",
}


def _enclosing_defs(tree):
    """node -> nearest enclosing FunctionDef name (or '<module>')."""
    owner = {}
    def walk(node, name):
        for child in ast.iter_child_nodes(node):
            nxt = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else name
            owner[child] = nxt
            walk(child, nxt)
    owner[tree] = "<module>"
    walk(tree, "<module>")
    return owner


def sites(path=TARGET):
    """[(def_name, class, lineno, literal)] — every private structure spelling."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    owner = _enclosing_defs(tree)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not isinstance(fn, ast.Attribute):
            continue
        if fn.attr in _RE_FUNCS:
            # `re.match(PAT, s)` — the pattern is arg 0; `PAT.match(s)` carries no
            # literal here and is attributed to wherever PAT was defined.
            args = node.args[:1]
        elif fn.attr in _STR_FUNCS:
            args = node.args[:1]
        else:
            continue
        for a in args:
            for lit in ([a] if isinstance(a, ast.Constant) else
                        getattr(a, "elts", []) if isinstance(a, ast.Tuple) else []):
                if not isinstance(lit, ast.Constant) or not isinstance(lit.value, str):
                    continue
                for cls, pat in CLASSES.items():
                    if pat.search(lit.value):
                        found.append((owner.get(node, "<module>"), cls, lit.lineno, lit.value))
    return found


def tally(found):
    out = {}
    for d, cls, _, _ in found:
        if d in PRIMITIVES:
            continue
        out.setdefault(d, {}).setdefault(cls, 0)
        out[d][cls] += 1
    return out


def main():
    found = sites()
    current = tally(found)

    if "--report" in sys.argv:
        by_class = {}
        for d, cls, ln, lit in found:
            if d in PRIMITIVES:
                continue
            by_class.setdefault(cls, []).append((d, ln, lit))
        total = sum(len(v) for v in by_class.values())
        print(f"{total} private spellings across {len(current)} defs "
              f"(primitives excluded)\n")
        for cls in sorted(by_class, key=lambda c: -len(by_class[c])):
            rows = by_class[cls]
            print(f"  {cls:12s} {len(rows):3d} sites / {len({d for d, _, _ in rows})} defs")
            for d, ln, lit in sorted(rows)[:60]:
                print(f"      {d}:{ln}  {lit[:64]!r}")
            print()
        return 0

    if "--write-baseline" in sys.argv:
        BASELINE.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        n = sum(sum(c.values()) for c in current.values())
        print(f"baseline written: {n} spellings across {len(current)} defs")
        return 0

    if not BASELINE.is_file():
        print("structure-lint: no baseline — run --write-baseline", file=sys.stderr)
        return 2
    base = json.loads(BASELINE.read_text(encoding="utf-8"))

    grew, shrank = [], []
    for d, classes in sorted(current.items()):
        for cls, n in sorted(classes.items()):
            was = base.get(d, {}).get(cls, 0)
            if n > was:
                where = [f"line {ln}" for dd, cc, ln, _ in found if dd == d and cc == cls]
                grew.append(f"  {d} — {cls}: {was} -> {n}  ({', '.join(where[:4])})")
    for d, classes in sorted(base.items()):
        for cls, n in sorted(classes.items()):
            now = current.get(d, {}).get(cls, 0)
            if now < n:
                shrank.append(f"  {d} — {cls}: {n} -> {now}")

    if grew:
        print("structure-lint: a new private structure spelling was added.\n")
        print("\n".join(grew))
        print("\nA checker that re-implements what a heading / a fence / a table row IS "
              "is itself\nthe defect — that is what T099's census of 129 spellings across "
              "67 defs measured,\nand what every F296 finding turned out to be. Route it "
              "through the primitive:\n"
              "  fence    _FENCE_RE / _fenced_mask / _strip_fenced / _mask_code\n"
              "  heading  _H1_RE / _head_h1 / _H2_RE / _h2_titles / _section_body\n"
              "  table    _TABLE_ROW_RE / _is_table_row / _table_blocks / _table_data_rows\n"
              "\nIf no primitive fits yet, add one — and MEASURE it (the before/after "
              "verdict diff\nat each rule's own `where::`, run back-to-back). Only if the "
              "spelling is genuinely\nsingular does the baseline get edited, deliberately, "
              "in the same commit.")
        return 1

    n = sum(sum(c.values()) for c in current.values())
    if shrank:
        print("structure-lint: the ratchet can tighten — sites were converted:\n")
        print("\n".join(shrank))
        print(f"\nRun --write-baseline to freeze the smaller set ({n} spellings "
              f"across {len(current)} defs).")
        return 1

    print(f"structure-lint: clean — {n} private spellings across {len(current)} defs, "
          f"none new.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
