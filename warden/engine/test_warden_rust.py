#!/usr/bin/env python3
"""Differential test: the Rust performance engine (F213) ≡ the Python reference.

The Rust `warden-rs fire` binary and the Python `warden_fire` primitives are run
over the **same IR** and their fire plans are diffed byte-for-byte — this is the
F214 differential gate for M3. The Python side of the diff reuses the *real*
reference functions (`warden_fire.is_active` / `eval_guard`) rather than a
re-implementation, so a divergence means Rust drifted from the oracle, not that a
parallel oracle drifted from itself.

Coverage:
  • the live corpus IR (`~/.warden/rules-ir.json`) — indexed dispatch + active-set
    gating across every registered moment and a range of anchor trait sets;
  • synthetic fixtures exercising the declarative residual (`eval_guard`:
    git-aspect/mode/trait/facet × eq/in/has, including `in`-scalar and `has`
    substring) and the `tell`/`deny`/`judge` + `guard_py` dispatch arms.

Skips (does not fail) when the Rust binary is unavailable — CI builds it first;
the local unit loop can run without cargo. Mirrors the live-e2e skip discipline.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import warden_fire as wf  # noqa: E402

RS_DIR = HERE.parent / "rs"
BIN = os.environ.get("WARDEN_RS_BIN") or str(RS_DIR / "target" / "release" / "warden-rs")
LIVE_IR = Path(os.path.expanduser("~/.warden/rules-ir.json"))


def _have_bin() -> bool:
    return Path(BIN).is_file() or shutil.which(BIN) is not None


# ── the Python oracle: fire plan from the reference primitives ────────────────

def fire_plan_py(ir: dict, moment: str, ctx, anchor_traits) -> list[dict]:
    """Mirror of the Rust `fire_plan` selection, built on the real `warden_fire`
    reference functions. Stops short of running Python bodies (the resident-
    interpreter path) — exactly what the Rust engine decides on its own."""
    plan: list[dict] = []
    for rid in ir.get("moments", {}).get(moment, []):
        row = ir["rules"][rid]
        if not wf.is_active(ir, rid, anchor_traits):
            continue
        if not all(wf.eval_guard(g, ctx) for g in row.get("guards", [])):
            continue
        if row.get("guard_py"):
            plan.append({"rule_id": rid, "kind": "python-guard", "steer": None})
            continue
        if row.get("body_py"):
            plan.append({"rule_id": rid, "kind": "python-body", "steer": None})
        elif row.get("action"):
            act = row["action"]
            if act.get("kind") in ("tell", "deny"):
                steer = act.get("text") or act.get("reason") or ""
                if act["kind"] == "deny":
                    steer = f"DENY: {steer}"  # F131 — mirror of warden_fire.fire
                plan.append({"rule_id": rid, "kind": "declarative", "steer": steer})
            else:
                plan.append({"rule_id": rid, "kind": "action-other", "steer": None})
    return plan


def _mk_ctx(traits, git_aspect="", mode=None, facets=None):
    return types.SimpleNamespace(
        git_aspect=git_aspect, mode=mode, traits=traits, facets=facets or [])


def run_rust(ir_path: str, moment: str, traits, git_aspect="", mode=None, facets=None):
    cmd = [BIN, "fire", "--ir", ir_path, "--moment", moment]
    if traits:
        cmd += ["--traits", ",".join(traits)]
    if git_aspect:
        cmd += ["--git-aspect", git_aspect]
    if mode is not None:
        cmd += ["--mode", mode]
    if facets:
        cmd += ["--facets", ",".join(facets)]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ── synthetic IR: guards + declarative actions + guard_py ─────────────────────

SYN = {
    "schema": 1, "root": "/x", "source_hash": "h", "active_set_hash": "a",
    "moments": {"tool:pre:Bash": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]},
    "rules": {
        "S1": {"id": "S1", "action": {"kind": "tell", "text": "beware bash"},
               "body_py": None, "guard_py": None,
               "guards": [{"key": "git-aspect", "op": "eq", "value": "commit"}]},
        "S2": {"id": "S2", "action": {"kind": "deny", "reason": "no force push"},
               "body_py": None, "guard_py": None,
               "guards": [{"key": "trait", "op": "has", "value": "push"}]},
        "S3": {"id": "S3", "action": {"kind": "judge"},
               "body_py": None, "guard_py": None, "guards": []},
        "S4": {"id": "S4", "action": None, "body_py": None,
               "guard_py": "guard_S4", "guards": []},
        "S5": {"id": "S5", "action": {"kind": "tell", "text": "drive+facet"},
               "body_py": None, "guard_py": None,
               "guards": [{"key": "mode", "op": "eq", "value": "drive"},
                          {"key": "facet", "op": "in", "value": ["a", "b"]}]},
        # `in` with a scalar value → equality; `has` substring on the git-aspect string.
        "S6": {"id": "S6", "action": {"kind": "tell", "text": "in-scalar"},
               "body_py": None, "guard_py": None,
               "guards": [{"key": "mode", "op": "in", "value": "drive"}]},
        "S7": {"id": "S7", "action": {"kind": "tell", "text": "substr"},
               "body_py": None, "guard_py": None,
               "guards": [{"key": "git-aspect", "op": "has", "value": "omm"}]},
    },
    "traits": {"syn": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]},
}


class RustDifferential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not _have_bin():
            raise unittest.SkipTest(f"warden-rs not built at {BIN} (CI builds it first)")

    def _diff(self, ir: dict, moment: str, traits, **ctx_kw):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(ir, f)
            path = f.name
        try:
            anchor_traits = list(traits) + ["anchor-base"]
            ctx = _mk_ctx(anchor_traits, **ctx_kw)
            want = fire_plan_py(ir, moment, ctx, anchor_traits)
            got = run_rust(path, moment, traits, **ctx_kw)
            self.assertEqual(got, want, f"moment={moment} traits={traits} ctx={ctx_kw}")
        finally:
            os.unlink(path)

    # ── synthetic: guards + action arms ──────────────────────────────────────

    def test_syn_commit_no_push(self):
        # git-aspect commit, no push trait, mode null → S1 tell, S3 judge, S4 python-guard, S7 substr
        self._diff(SYN, "tool:pre:Bash", ["syn"], git_aspect="commit")

    def test_syn_all_fire(self):
        self._diff(SYN, "tool:pre:Bash", ["syn", "push"],
                   git_aspect="commit", mode="drive", facets=["a"])

    def test_syn_nothing_matches(self):
        # no git-aspect, no push, mode not drive → only S3 judge + S4 python-guard survive
        self._diff(SYN, "tool:pre:Bash", ["syn"])

    def test_syn_inactive_trait(self):
        # trait not adopted → whole ruleset silent
        self._diff(SYN, "tool:pre:Bash", ["other"], git_aspect="commit")

    def test_syn_facet_miss(self):
        self._diff(SYN, "tool:pre:Bash", ["syn"], mode="drive", facets=["z"])

    def test_syn_substr_only(self):
        # git-aspect "rebase" → S7 "omm" not a substring; S1 eq commit false
        self._diff(SYN, "tool:pre:Bash", ["syn"], git_aspect="rebase")

    # ── live corpus: indexed dispatch + active-set ───────────────────────────

    def test_live_corpus_all_moments(self):
        if not LIVE_IR.is_file():
            self.skipTest(f"no live IR at {LIVE_IR} (run `warden compile`)")
        ir = json.loads(LIVE_IR.read_text())
        trait_sets = [[], ["warden-selftest"], ["query"], ["backlog"],
                      ["warden-selftest", "query"], ["anchor-page"]]
        for moment in list(ir.get("moments", {})) + ["nope:moment"]:
            for traits in trait_sets:
                self._diff(ir, moment, traits)


if __name__ == "__main__":
    unittest.main()
