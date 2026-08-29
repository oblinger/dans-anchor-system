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
import threading
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

# ── keeping `ap` fresh in a resident daemon ──────────────────────────────────
#
# The IR reloads on mtime (`Corpus.fresh`) and the audit rulesets are read from
# SOURCE on every fire (`compile_audit_ir`), so both of those self-heal. The
# checker *code* did not: `ap` was bound once at import, and the daemon holds
# this module warm for hours. So editing `audit-plan.py` — adding a checker,
# registering a fixer — changed nothing until someone happened to restart the
# daemon, and the rules that needed the new code reported `error`, which the
# write path deliberately never surfaces. It fails silent and it fails clean.
#
# That is exactly how R-spine-04..08 sat dead: the rules were live, the
# checkers were registered, and the daemon was executing a copy of the file
# from before they existed (F319, 2026-08-10).
#
# The stamp covers the whole scripts directory, not just `audit-plan.py`,
# because the checkers import siblings (`spine.py`, `spine_check.py`,
# `spine_fix.py`) — a fix landing in one of those must reload too. ~40 stats,
# measured at 0.1 ms, against a per-fire budget in the tens of ms.
_AP_STAMP: dict = {"ns": None}
_AP_LOCK = threading.Lock()


def _scripts_stamp() -> int:
    try:
        return max((p.stat().st_mtime_ns for p in _AUDIT_PLAN.parent.glob("*.py")),
                   default=0)
    except OSError:
        return 0


def refresh_audit_plan() -> bool:
    """Re-exec audit-plan IN PLACE when it or a sibling changed. True if reloaded.

    In place matters: `exec_module` into the *existing* module object rebinds
    its globals, so every `ap.<name>` reference already written in this file
    picks up the new value without a single call site changing. Rebinding a new
    module object instead would leave any `from ap import x` alias stale — the
    same class of bug this exists to fix.
    """
    ns = _scripts_stamp()
    if ns == _AP_STAMP["ns"]:
        return False
    with _AP_LOCK:
        if ns == _AP_STAMP["ns"]:           # another thread won the race
            return False
        spec = importlib.util.spec_from_file_location("audit_plan", _AUDIT_PLAN)
        if spec is not None and spec.loader is not None:
            try:
                spec.loader.exec_module(ap)
            except Exception:               # a half-saved file must not kill the write
                return False
        _AP_STAMP["ns"] = ns
    return True


_AP_STAMP["ns"] = _scripts_stamp()


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


# ── rule selection by file kind (F297) ───────────────────────────────────────
#
# The markdown doc-fire flattens one fixed umbrella (`R-doc`). That is what made
# a non-markdown document rule unreachable: `R-svg-jiggle` is a correct,
# compiled, registered ruleset that no umbrella includes, so no selector it
# carries was ever evaluated (T106 — a deliberately-bad `.svg` fired the write
# hook with the svg rules not even *considered*).
#
# For any other kind the selector is the anchor's own declared traits: the
# compiled IR already maps trait → rule ids and records which of those are
# where-major doc-rules, so an anchor that declares `svg-jiggle` is asking for
# exactly those rules on exactly the files their `where` names. The IR row is
# used only to decide WHICH rulesets are in play; the rows themselves come back
# through the same `compile_audit_ir` flatten the markdown path uses, so a
# non-markdown fire carries the full `why` / `fix` / `check_pattern` an audit-
# plan rule dict has and behaves identically from there down.

_MD_SUFFIXES = (".md", ".markdown")
_IR_CACHE: dict = {}


def _compiled_ir() -> dict:
    """The live compiled IR, mtime-cached (this module stays resident in the
    daemon across writes; a `warden compile` moves the file's mtime)."""
    import json
    import warden_hook as wh  # lazy — warden_hook imports this module back
    p = wh.warden_home() / "rules-ir.json"
    try:
        # Key on the PATH as well as the mtime. `warden_home()` is read from
        # $WARDEN_HOME, so it can point somewhere else between two calls in one
        # process; an mtime-only key would then serve one home's IR under
        # another home's name whenever the two files' mtimes happened to match.
        stamp = (str(p), p.stat().st_mtime_ns)
    except OSError:
        return {}
    if _IR_CACHE.get("stamp") != stamp:
        try:
            _IR_CACHE.update(stamp=stamp, ir=json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return {}
    return _IR_CACHE.get("ir") or {}


def _ruleset_of(source: str) -> str:
    """The ruleset name from an IR row's `source` (`rulesets/R-x.md#RULESET R-x`)."""
    return wc._include_target(source) if "#" in source else ""


def trait_rows(target: Path) -> list[tuple[dict, dict]]:
    """The doc-rule rows a non-markdown write puts in play — the anchor's
    effective traits, narrowed to the rules whose `where` actually names this
    file. Narrowing first is what keeps the fire cheap: a file no declared glob
    names flattens nothing at all and costs one selector match per candidate."""
    import warden_fire as wf
    ir = _compiled_ir()
    if not ir:
        return []
    anchor_root, scope_files = ap.enumerate_scope(target, "doc", None)
    doc_ids = set(ir.get("doc_rules") or [])
    index = ir.get("traits") or {}
    eligible = {rid for t in wf.effective_traits(ir, anchor_root)
                for rid in index.get(t, []) if rid in doc_ids}
    rules = ir.get("rules") or {}
    names: set[str] = set()
    for rid in eligible:
        row = rules.get(rid) or {}
        kind, arg, mir = ap.parse_selector(row.get("where") or "always")
        if kind == "anchor":
            continue
        if ap.match_targets(kind, arg, scope_files, anchor_root, mir):
            names.add(_ruleset_of(row.get("source") or ""))
    rows: list[tuple[dict, dict]] = []
    for name in sorted(n for n in names if n):
        rows.extend((row, rs) for row, rs in compile_audit_ir(name)
                    if row["id"] in eligible)
    return rows


def rows_for(target: Path) -> list[tuple[dict, dict]]:
    """The rows a write of `target` fires — umbrella for markdown, declared
    traits for every other kind."""
    if target.suffix.lower() in _MD_SUFFIXES:
        return compile_audit_ir("R-doc")
    return trait_rows(target)


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
    # F601 — the same table `audit-plan --run` reads. Before this, the same
    # doc-rule on the same file returned `except` under `/audit` and `fail`
    # under Warden (measured 2026-08-27 on SV EX001), because the lookup lived
    # in `execute_plan`, which only audit-plan's own CLI ever called.
    excs, _declined, _problems = ap.load_exceptions(anchor_root)
    for row, rs in rows:
        action = row.get("action")
        if not action or action.get("kind") != "check":
            continue
        where = row["where"] or "always"
        kind, arg, mir = ap.parse_selector(where)
        if mode == "doc" and kind == "anchor":
            continue  # anchor-structure rules are N/A at the doc level
        tgts = ap.match_targets(kind, arg, scope_files, anchor_root, mir)
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
            if status in ap._EXC_SUPPRESSIBLE and excs:
                e = ap._exception_for(excs, row["id"], t, anchor_root)
                if e:
                    status = "except"
                    detail = (f"{e['handle']} (grade {e['grade']}) — {e['why']}"
                              + (f"  [was: {detail}]" if detail else ""))
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

    Which rules are in play is chosen by the file's kind (F297 — `rows_for`):
    markdown fires the `R-doc` umbrella; every other kind fires the doc-rules
    the file's anchor declares by trait.

    `rows` overrides the umbrella compile for tests (inject fixture rules)."""
    refresh_audit_plan()
    if rows is None:
        rows = rows_for(target)
    if not rows:
        return {"fixed": [], "messages": []}
    anchor_root, scope_files = ap.enumerate_scope(target, "doc", None)

    plan_rules = []
    for row, rs in rows:
        action = row.get("action")
        if not action or action.get("kind") != "check":
            continue
        where = row["where"] or "always"
        kind, arg, mir = ap.parse_selector(where)
        if kind == "anchor":
            continue
        tgts = ap.match_targets(kind, arg, scope_files, anchor_root, mir)
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
