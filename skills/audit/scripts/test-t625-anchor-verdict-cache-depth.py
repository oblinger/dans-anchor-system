#!/usr/bin/env python3
"""T625 — an anchor-scope verdict must go stale when the anchor's FACET FOLDERS
change, not only when its root listing does.

`execute_plan` caches every verdict under (rule, rule-body, target-content
hash). For an anchor-dir target that hash was the sorted list of the root's
child NAMES — so `R-design-02`, which inspects `{slug} Design/` one level down,
kept serving its cached `fail` after `SPARKS PRD.md` was written inside that
folder. Atticus touched every file, waited out the watcher and ran `ha
--rescan` with no change, which is the signature: nothing at the root had a
new name. A `fail` that survives the fix it demands is the defect; this pins
the hash rather than the checker, because every `anchor`-scope checker that
reads into Track/ or Design/ shares it.
"""
import importlib.util, pathlib, sys, tempfile, time

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ap", _HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(_spec)
sys.modules["ap"] = ap
_spec.loader.exec_module(ap)

PASSED = FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    print(f"  {'ok  ' if cond else 'FAIL'}    {name}")
    PASSED += bool(cond)
    FAILED += not cond


root = pathlib.Path(tempfile.mkdtemp()) / "Sparks"
design = root / "SPARKS Design"
track = root / "SPARKS Track"
for d in (design, track):
    d.mkdir(parents=True)
(root / ".anchor").write_text("slug: SPARKS\n", encoding="utf-8")
(root / "SPARKS.md").write_text("# SPARKS\n", encoding="utf-8")
(design / "SPARKS Design.md").write_text("# SPARKS Design\n", encoding="utf-8")
(track / "SPARKS Status.md").write_text("prd:: none\n", encoding="utf-8")

h0 = ap._content_hash(root)
check("the hash of an anchor dir is stable across two reads", h0 == ap._content_hash(root))

# --- the live case: a PRD written one level down -----------------------------
status, detail = ap.chk_design_folder_children(root, root, ["PRD"])
check("before the PRD exists R-design-02 fails on it", status == "fail" and "PRD" in detail)
(design / "SPARKS PRD.md").write_text("# SPARKS PRD\n", encoding="utf-8")
h1 = ap._content_hash(root)
check("adding a file INSIDE {slug} Design/ changes the anchor's hash", h1 != h0)
status, _ = ap.chk_design_folder_children(root, root, ["PRD"])
check("and the checker itself now passes", status == "pass")

# --- an edit with no new name: Status.md's content -----------------------------
time.sleep(0.01)
(track / "SPARKS Status.md").write_text("prd:: none\nux:: none\n", encoding="utf-8")
h2 = ap._content_hash(root)
check("editing a file inside {slug} Track/ (same name) changes the hash", h2 != h1)

# --- the root case still works -------------------------------------------------
(root / "SPARKS Discussion.md").write_text("x\n", encoding="utf-8")
check("a new root child still changes the hash", ap._content_hash(root) != h2)

# --- a file target is unchanged: bytes only -----------------------------------
f = root / "SPARKS.md"
hf = ap._content_hash(f)
check("a file target hashes its bytes, not its mtime",
      hf == ap._content_hash(f) and len(hf) == 12)

print(f"\n{PASSED} passed, {FAILED} failed")
sys.exit(1 if FAILED else 0)
