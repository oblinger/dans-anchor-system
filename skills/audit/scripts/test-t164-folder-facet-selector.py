#!/usr/bin/env python3
"""test-t164-folder-facet-selector.py — T164: a facet that materializes as a
FOLDER must have its rules actually fire on its own instances.

The defect this guards: a folder facet's instance carries its own `.anchor`, so
`sub_anchor_roots` drops it from the parent's scope and it is only ever audited
scoped on ITSELF. But its selector is authored from the parent's point of view
(`{anchor}/**/* Rocks/**`), which is then unsatisfiable from both ends — out of
scope from the parent, and from the folder itself `{anchor}` IS the Rocks folder,
so the pattern demands a nested `* Rocks/` inside itself. Every `R-rocks-*` rule
read `(checked)` while firing on nothing, on both live instances, at every scope.

Two independent halves, and BOTH are required — fixing either alone changes
nothing, which is how the diagnosis was confirmed on 2026-08-08:

  1. `_match_file_glob` matches each file against a candidate path prefixed with
     the anchor's own directory name, so the parent's-eye selector is satisfiable
     from the folder's own scope.
  2. `R-anchor`'s `include::` names R-rocks / R-wp / R-fct-outputs directly.
     Being listed in `R-facet` is NOT adoption — there is no per-anchor adoption
     mechanism, so a ruleset reachable only through `R-facet` never loads.

Guards the vacuous-zero shape specifically: asserts the rules FIRE, because
"the audit reported no failures" is what the broken state also looked like.

Self-contained: builds a fixture tree in tmp, no vault I/O."""
import importlib.machinery
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("audit_plan_t164", HERE / "audit-plan.py")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL {label}\n       got  {got!r}\n       want {want!r}")


# ── half 1: the selector is satisfiable from the folder's own scope ──────────

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    rocks = root / "MED Track" / "MED Rocks"
    rocks.mkdir(parents=True)
    (rocks / ".anchor").write_text("description: rocks\n", encoding="utf-8")
    members = []
    for n in ("MED Rocks.md", "MED HR.md", "MED TX.md"):
        p = rocks / n
        p.write_text("# x\n", encoding="utf-8")
        members.append(p)

    SEL = "{anchor}/**/* Rocks/**, !**/DAS *.md"

    # Scoped ON the Rocks folder — the only scope where these files are ever
    # audited, since the parent excludes them as a sub-anchor.
    hits = ap._match_file_glob(SEL, members, rocks)
    check("selector matches all members when scoped on the folder itself",
          sorted(p.name for p in hits),
          ["MED HR.md", "MED Rocks.md", "MED TX.md"])

    # The negation still bites through the self-prefixed candidate.
    spec = rocks / "DAS Rocks.md"
    spec.write_text("# spec\n", encoding="utf-8")
    hits = ap._match_file_glob(SEL, members + [spec], rocks)
    check("`!**/DAS *.md` still excludes the facet spec",
          "DAS Rocks.md" in [p.name for p in hits], False)

    # A file-shaped facet is unaffected — its primary relative path already
    # matched, and the extra candidate must not broaden it onto a sibling.
    backlog = root / "MED Backlog.md"
    backlog.write_text("# b\n", encoding="utf-8")
    hits = ap._match_file_glob("{anchor}/* Backlog.md", [backlog], root)
    check("file-shaped selector unchanged", [p.name for p in hits],
          ["MED Backlog.md"])

    # The self-prefix must not make an unrelated folder pattern match.
    hits = ap._match_file_glob("{anchor}/**/* Pebbles/**", members, rocks)
    check("a DIFFERENT folder facet's selector still misses", hits, [])


# ── half 2: the folder facets are inside the umbrella closure ────────────────

REPO = Path("/Users/oblinger/ob/kmr/SYS/Bespoke/Skill Agent/dans-anchor-system")
r_anchor = REPO / "rulesets" / "R-anchor.md"
if r_anchor.is_file():
    inc = ""
    for ln in r_anchor.read_text(encoding="utf-8").splitlines():
        if ln.startswith("include::"):
            inc = ln
            break
    for name in ("R-rocks", "R-wp", "R-fct-outputs"):
        check(f"{name} is in R-anchor's include:: (being in R-facet is not adoption)",
              bool(re.search(r"\[\[" + name + r"\]\]", inc)), True)
else:
    print("  SKIP closure half — repo not at the expected path; NOT counted as passing")

print(f"test-t164-folder-facet-selector: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
