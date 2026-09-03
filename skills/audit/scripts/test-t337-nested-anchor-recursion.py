#!/usr/bin/env python3
"""T337 — `/audit anchor X` audits X's WHOLE tree, nested anchors included.

`sub_anchor_roots` drops every nested `.anchor` from a target's scope, and a
facet folder (`{slug} Track/`, `{slug} Design/`) carries one exactly like a
real nested project — so a single-anchor audit saw 26% of its own tree (361
files seen, 1,049 omitted, across 57 anchors, measured 2026-08-12). Dan's
ruling 2026-09-03: until a peer relationship can be declared, assume nested
anchors are not peers and scan the whole tree.

`plan_anchor_tree` keeps the deepest-owner invariant: each nested root is
planned under ITS OWN root (its own slug, selectors, Exceptions) and only the
result is merged, labelled by owner. `--batch` keeps the old per-anchor plan.

    python3 test-t337-nested-anchor-recursion.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-plan.py").resolve()
_spec = importlib.util.spec_from_file_location("ap337", _S)
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap337"] = ap
_spec.loader.exec_module(ap)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


td = tempfile.TemporaryDirectory()
# resolve(): sub_anchor_roots resolves, and /var is a symlink on macOS
ROOT = Path(td.name).resolve() / "Zq"
ROOT.mkdir()
(ROOT / ".anchor").write_text("slug: Zq\n", encoding="utf-8")
(ROOT / "Zq.md").write_text("# Zq\nOrientation.\n", encoding="utf-8")
# The shape that motivated the row: a facet Track/ carrying its own .anchor,
# holding the anchor's working surface.
TRK = ROOT / "Zq Track"
TRK.mkdir()
(TRK / ".anchor").write_text("description: track\n", encoding="utf-8")
# Vault convention: the facet folder's page lives INSIDE it.
(TRK / "Zq Track.md").write_text("# Zq Track\n\n| a | b |\n|---|---|\n| [[Zq Status]] | x |\n",
                                encoding="utf-8")
(TRK / "Zq Backlog.md").write_text("# Zq Backlog\n\n## Now\n", encoding="utf-8")
(TRK / "Zq Status.md").write_text("# Zq Status\ndescription:: s\n", encoding="utf-8")
# A genuinely separate nested project, with a facet sub-anchor of its own.
SUB = ROOT / "Sub"
SUB.mkdir()
(SUB / ".anchor").write_text("slug: Sub\n", encoding="utf-8")
(SUB / "Sub.md").write_text("# Sub\nOrientation.\n", encoding="utf-8")
STRK = SUB / "Sub Track"
STRK.mkdir()
(STRK / ".anchor").write_text("description: track\n", encoding="utf-8")
(STRK / "Sub Track.md").write_text("# Sub Track\nOrientation.\n", encoding="utf-8")
(STRK / "Sub Backlog.md").write_text("# Sub Backlog\n\n## Now\n", encoding="utf-8")

print("The old shape — what --batch still does per anchor")
_, seen = ap.enumerate_scope(ROOT, "anchor", ap.sub_anchor_roots(ROOT))
check("the parent's own plan sees only its top-level files",
      sorted(p.name for p in seen), ["Zq.md"])
check("every nested .anchor at any depth is a root",
      sorted(str(r.relative_to(ROOT.resolve())) for r in ap.sub_anchor_roots(ROOT)),
      ["Sub", "Sub/Sub Track", "Zq Track"])

print("\nThe merged plan")
warnings = []
plan = ap.plan_anchor_tree(ROOT, None, warnings)
check("scope counts every markdown file in the tree", plan["scope_file_count"], 7)
check("nothing is reported as excluded", plan["excluded_subanchors"], [])
check("three nested anchors are included, in path order",
      [n["path"] for n in plan["nested_anchors"]],
      ["Sub", "Sub/Sub Track", "Zq Track"])
check("each nested entry names its owner slug",
      [n["slug"] for n in plan["nested_anchors"]], ["Sub", "Sub Track", "Zq Track"])
check("the top-level plan's own root is unchanged", plan["anchor_root"], str(ROOT))

by_root = {}
for g in plan["groupings"]:
    by_root.setdefault(g.get("anchor_root", "<top>"), set())
    for r in g["rules"]:
        by_root[g.get("anchor_root", "<top>")].update(r["targets"])
check("the parent's groupings carry no anchor_root (they ARE the plan's)",
      "<top>" in by_root, True)
check("groupings from the facet sub-anchor are planned under ITS root",
      str(TRK) in by_root, True)
check("groupings from the nested project are planned under ITS root",
      str(SUB) in by_root, True)
check("a nested target is labelled by its path from the top target",
      any(t.startswith("Zq Track/") for t in by_root.get(str(TRK), ())), True)
check("a nested anchor's own root is labelled by its path, not `{anchor}`",
      "{anchor}" in by_root.get(str(SUB), set()), False)
check("no target of any grouping still reads `{anchor}` for a nested root",
      any(t == "{anchor}" for root, ts in by_root.items() if root != "<top>" for t in ts),
      False)
all_targets = {t for ts in by_root.values() for t in ts}
check("the backlog under the facet Track/ is now a target",
      "Zq Track/Zq Backlog.md" in all_targets, True)
check("the nested project's own page is a target, under Sub's own root",
      "Sub/Sub.md" in by_root.get(str(SUB), set()), True)
check("the nested project's facet backlog is a target",
      "Sub/Sub Track/Sub Backlog.md" in all_targets, True)

print("\nExecution honors the owning root")
rep = ap.execute_plan(plan, None)
res = {(v["rule"], v["target"]): v for v in rep["results"]}
check("verdicts exist for a file under the facet Track/",
      any(t.startswith("Zq Track/") for _, t in res), True)
v = res.get(("R-status-09", "Zq Track/Zq Status.md"))
check("R-status-09 fires on the Status file under the facet Track/", v is not None, True)
check("...and finds the parent's Track page rather than erroring",
      (v or {}).get("status"), "pass")
check("no checker crashed on a nested-root target",
      [k for k, v in res.items() if v["status"] == "error"], [])

print("\nRecipe and report wording")
rec = ap.render_recipe(plan, "file", None)
check("recipe says how many nested anchors it includes",
      "includes 3 nested anchor(s)" in rec, True)
check("recipe no longer speaks of exclusion", "excluded" in rec, False)
man = ap.judge_manifest(plan, None, "m")
check("judgment tasks carry their owning root",
      all("anchor_root" in t for t in man["tasks"]) and bool(man["tasks"]), True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
