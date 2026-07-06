#!/usr/bin/env python3
"""Regression test for warden_fire.py (F211 fire path — Success Criteria).

Pins the two properties the F211 Success Criteria name:
  1. The real `R-query-14` fires end-to-end at `skill:pre:audit-q` against a
     fixture anchor whose queries file carries a commit/push question — the
     compile → install → fire loop, module-emitted body and all.
  2. Indexed dispatch + active-set gating, via a synthesized two-rule fixture on
     different moments: firing one moment runs ONLY its rule; a rule whose trait
     the anchor has not adopted does not fire.

Runnable standalone (`python3 test_warden_fire.py`) — no test framework.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import warden_compile as wc   # noqa: E402
import warden_fire as wf      # noqa: E402

FCT_QUERY = REPO / "facets" / "FCT Track" / "FCT Query.md"

# A synthesized ruleset with two when-rules on DIFFERENT moments; each body
# records a distinct marker so we can prove only one executes per moment.
FIXTURE_RULESET = '''# RULESET R-fix
include::

### RULE R-fix-01 — audit-q marker (when:: skill:post:audit-q)
when:: skill:post:audit-q

```python
def trigger(ctx):
    return ["A-fired"]
```

### RULE R-fix-02 — write marker (when:: tool:post:Write)
when:: tool:post:Write

```python
def body(ctx):
    return ["B-fired"]
```
'''


def _compile_into(warden_dir: Path, text: str, name: str, anchor: str):
    rs = wc.parse_ruleset(text, name, "fixture.md")
    assert rs is not None, f"ruleset {name} not parsed"
    ir, module_src, _ = wc.compile_ruleset(rs, anchor)
    warden_dir.mkdir(parents=True, exist_ok=True)
    import json
    (warden_dir / "rules-ir.json").write_text(json.dumps(ir), encoding="utf-8")
    (warden_dir / f"rules_{anchor}.py").write_text(module_src, encoding="utf-8")
    return ir


def test_real_r_query_14_fires(tmp: Path):
    """Build a fixture anchor that adopted the `query` trait + Commit aspect, with
    a commit/push question in its queries file; fire audit-q → the steer."""
    anchor = tmp / "FX"
    (anchor / "FX Track").mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: FX\ntraits: [query, Commit]\n", encoding="utf-8")
    (anchor / "FX Track" / "FX queries.md").write_text(
        "## Immediate Questions\n\n- **Q1** Should I commit and push this branch now?\n",
        encoding="utf-8")

    wdir = anchor / ".warden"
    _compile_into(wdir, FCT_QUERY.read_text(encoding="utf-8"), "R-query", "query")
    ir, module = wf.load_compiled(wdir, "query")
    traits = wf.read_anchor_traits(anchor)
    ctx = wf.build_ctx(anchor, "skill:pre:audit-q")

    assert ctx.git_aspect == "commit", ctx.git_aspect
    assert "commit and push" in ctx.queries_text
    steers = wf.fire(ir, module, "skill:pre:audit-q", ctx, traits)
    assert steers and "Do NOT ask" in steers[0], steers
    assert "commit now" in steers[0], steers[0]
    print("PASS  real_r_query_14_fires")


def test_indexed_dispatch_and_gating(tmp: Path):
    wdir = tmp / "fixwarden"
    _compile_into(wdir, FIXTURE_RULESET, "R-fix", "fix")
    ir, module = wf.load_compiled(wdir, "fix")

    # sanity: two rules, on two different moments
    assert set(ir["moments"]) == {"skill:pre:audit-q", "tool:post:Write"}, ir["moments"]

    adopted = ["fix", "anchor-base"]
    ctx = wf.build_ctx(tmp, "skill:pre:audit-q")  # tmp has no .anchor → bare ctx

    # firing audit-q runs ONLY R-fix-01
    a = wf.fire(ir, module, "skill:pre:audit-q", ctx, adopted)
    assert a == ["A-fired"], a
    # firing Write runs ONLY R-fix-02
    b = wf.fire(ir, module, "tool:post:Write", ctx, adopted)
    assert b == ["B-fired"], b

    # active-set gating: an anchor that has NOT adopted the `fix` trait fires nothing
    none = wf.fire(ir, module, "skill:pre:audit-q", ctx, ["other", "anchor-base"])
    assert none == [], none
    print("PASS  indexed_dispatch_and_gating")


def main():
    with tempfile.TemporaryDirectory() as td:
        test_real_r_query_14_fires(Path(td) / "a")
        test_indexed_dispatch_and_gating(Path(td) / "b")
    print("\nall warden_fire tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
