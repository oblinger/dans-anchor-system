#!/usr/bin/env python3
"""Warden doc-rule fire path — the audit-surface executor (F212 / M4 seam).

The moment dispatcher (`warden_fire`) runs *when-rules* at a live moment. Tier
**doc-rules** — the where-major `checked`/`sampled`/`stated`/`tracked` rules the
compiler records under `doc_rules` — fire on the authoring-time `/audit doc` (and
`/audit anchor`) pass instead: match each rule's `where` glob against the target
scope, run its `check::` action, emit a verdict per target.

This module is the reference executor for that path, and it is the concrete M4
seam: instead of re-deriving the resolve/match/check machinery, it **reuses
`audit-plan.py`'s** flatten + selector + checker primitives (the shipped Python
Resolve→Run→Judge engine, F001) — but it drives them from the **Warden IR**. Each
rule is round-tripped through `warden_compile.compile_rule` into a doc-rule row,
and execution reads that row's declarative `action`. So this proves the compiled
IR is a faithful executable representation of the doc-rules: firing from the IR
reproduces `audit-plan --run` verdict-for-verdict (the golden corpus, run through
the `warden` engine adapter, matches the `expected.json` blessed against
audit-plan). The checker *implementations* stay audit-plan's — Warden references
them by name through `run_checker`, staying adapter-isolated from the impl.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_compile as wc  # noqa: E402

# audit-plan lives in the corpus repo's skills tree; load it by path (it is
# not a package). …/dans-anchor-system/skills/audit/scripts/audit-plan.py —
# resolved via warden_root since the T008 engine extraction.
from warden_root import corpus_root  # noqa: E402
_REPO_ROOT = corpus_root()
_AUDIT_PLAN = _REPO_ROOT / "skills" / "audit" / "scripts" / "audit-plan.py"


def _load_audit_plan():
    spec = importlib.util.spec_from_file_location("audit_plan", _AUDIT_PLAN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load audit-plan from {_AUDIT_PLAN}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ap = _load_audit_plan()


# ── compile: audit-plan rulesets → Warden doc-rule IR rows ───────────────────

def _adapt_rule(r: dict) -> dict:
    """Shape an audit-plan rule dict into the shape `warden_compile.compile_rule`
    parses (a doc-rule has no `when::`/`if::`/python body — tier + `where` +
    optional `check::`)."""
    return {
        "id": r["id"], "when": None, "where": r.get("where"), "ifs": [],
        "tier": r.get("tier"), "check": r.get("check"), "fix": r.get("fix"),
        "py_kind": None,
    }


# F232 B3: the umbrella flatten re-reads ~50 ruleset files (~90 ms warm per
# markdown write when this module stays resident in the daemon). Cache the
# compiled rows keyed on the source files' mtimes — a rule edit invalidates
# via its file's mtime; a new ruleset joins the umbrella only through an
# include:: edit in an already-tracked file, so the stamp always notices.
_AUDIT_IR_CACHE: dict = {}


def _sources_stamp(sources: tuple) -> tuple:
    out = []
    for s in sources:
        try:
            out.append((ap.REPO_ROOT / s).stat().st_mtime_ns)
        except OSError:
            out.append(0)
    return tuple(out)


def compile_audit_ir(umbrella: str) -> list[tuple[dict, dict]]:
    """Flatten an audit umbrella (`R-doc` / `R-anchor`) and compile every rule to
    its Warden IR doc-rule row. Returns [(row, ruleset)] in flatten order — the
    ruleset is retained for its `source` (drop-own-source) + `where` precedence
    (already folded into the row by `compile_rule`). Mtime-cached (F232 B3)."""
    ent = _AUDIT_IR_CACHE.get(umbrella)
    if ent is not None and _sources_stamp(ent["sources"]) == ent["stamp"]:
        return ent["rows"]
    rulesets = ap.flatten_umbrella(umbrella, [])
    rows: list[tuple[dict, dict]] = []
    for rs in rulesets:
        for r in rs["rules"]:
            row = wc.compile_rule(_adapt_rule(r), rs)
            rows.append((row, rs))
    sources = tuple(sorted({rs["source"] for _, rs in rows if rs.get("source")}))
    _AUDIT_IR_CACHE[umbrella] = {
        "sources": sources, "stamp": _sources_stamp(sources), "rows": rows}
    return rows


# ── fire: execute the check-action rows over a target scope ──────────────────

def _check_str(action: dict) -> str:
    """Reconstruct the `run_checker` argument from an IR check action."""
    return action["ref"] + (" " + " ".join(action["args"]) if action["args"] else "")


def fire_audit(target: Path, mode: str) -> list[dict]:
    """Fire the doc-rules for `mode` against `target`, returning verdicts as
    `{rule, target, status, detail}` — the same shape (and, for check-bearing
    rules, the same values) `audit-plan --run --json` emits under `results`.

    Mirrors `audit-plan.plan_one` + `execute_plan`: pick the umbrella by mode,
    enumerate scope, match each rule's selector, drop the ruleset's own source
    file, and run the checker per target. Only rows whose `action` is a `check`
    produce a verdict — `judge`/`track` rows are the agent-judgment residue
    (`audit-plan --judge`), never mechanical verdicts."""
    umbrella = "R-doc" if mode == "doc" else "R-anchor"
    rows = compile_audit_ir(umbrella)
    exclude = ap.sub_anchor_roots(target) if mode == "anchor" else None
    anchor_root, scope_files = ap.enumerate_scope(target, mode, exclude)

    results: list[dict] = []
    for row, rs in rows:
        action = row.get("action")
        if not action or action.get("kind") != "check":
            continue
        where = row["where"] or "always"
        kind, arg = ap.parse_selector(where)
        if mode == "doc" and kind == "anchor":
            continue  # anchor-structure rules are N/A at the doc level
        tgts = ap.match_targets(kind, arg, scope_files, anchor_root)
        if tgts and rs.get("source"):
            src_abs = (ap.REPO_ROOT / rs["source"]).resolve()
            tgts = [t for t in tgts if t.resolve() != src_abs]
        if not tgts:
            continue
        check = _check_str(action)
        for t in tgts:
            # `{anchor}` — the lowercase where-token vocabulary (F229 MS-1);
            # audit-plan displays it lowercase and the parity test diffs verbatim.
            disp = str(t.relative_to(anchor_root)) if t != anchor_root else "{anchor}"
            status, detail = ap.run_checker(check, t, anchor_root)
            results.append({"rule": row["id"], "target": disp,
                            "status": status, "detail": detail})
    return results


def fire_on_write(target: Path, rows: list[tuple[dict, dict]] | None = None) -> dict:
    """The on-write fire path (M4a — fixer parity with `audit-on-write.sh`).

    Warden owns resolve/match (the compiled doc-rule rows, their `where`
    selectors); check + fix execution is delegated to **`audit-plan`'s own
    `execute_on_write`** — the same fixer registry, the same never-delete
    alnum-subsequence floor, the same fix→re-check→message fallthrough — so
    behavior parity with the bespoke F177 hook holds by construction. Returns
    audit-plan's report shape: {fixed: [...], messages: [...]}.

    `rows` overrides the umbrella compile for tests (inject fixture rules)."""
    if rows is None:
        rows = compile_audit_ir("R-doc")
    anchor_root, scope_files = ap.enumerate_scope(target, "doc", None)

    plan_rules = []
    for row, rs in rows:
        action = row.get("action")
        if not action or action.get("kind") != "check":
            continue
        where = row["where"] or "always"
        kind, arg = ap.parse_selector(where)
        if kind == "anchor":
            continue
        tgts = ap.match_targets(kind, arg, scope_files, anchor_root)
        if tgts and rs.get("source"):
            src_abs = (ap.REPO_ROOT / rs["source"]).resolve()
            tgts = [t for t in tgts if t.resolve() != src_abs]
        if not tgts:
            continue
        src = next((r for r in rs["rules"] if r["id"] == row["id"]), {})
        plan_rules.append({
            "id": row["id"], "check": _check_str(action), "fix": row.get("fix"),
            "why": src.get("why"), "check_pattern": src.get("check_pattern"),
            "targets": [str(t.relative_to(anchor_root)) for t in tgts],
            "_target_paths": [str(t) for t in tgts],
        })
    plan = {"anchor_root": str(anchor_root), "groupings": [{"rules": plan_rules}]}
    return ap.execute_on_write(plan, None)


def corpus_signature() -> str:
    """The live rule-corpus signature — reuses audit-plan's (the doc-fire path
    reads the very same rulesets), so a `warden`-engine bless pins to the same
    content hash the `audit-plan` engine does."""
    return "-".join(ap._plan_rules_hash(ap.flatten_umbrella(u, []))
                    for u in ("R-doc", "R-anchor"))


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(
        prog="warden-docfire",
        description="Fire Warden doc-rules against an anchor/doc; emit verdicts.")
    p.add_argument("target")
    p.add_argument("--mode", choices=("doc", "anchor"), default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    tgt = Path(args.target).expanduser().resolve()
    mode = args.mode or ("doc" if tgt.is_file() else "anchor")
    results = fire_audit(tgt, mode)
    if args.json:
        import json
        print(json.dumps({"results": results}, indent=2))
    else:
        for v in results:
            mark = {"pass": "✓", "fail": "✗", "error": "!"}.get(v["status"], "?")
            print(f"{mark} {v['rule']:20s} {v['target']:24s} {v['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
