#!/usr/bin/env python3
"""run-corpus.py — the golden-corpus runner (Warden F214, golden layer).

Runs every corpus case through an engine adapter, canonicalizes the verdicts,
and diffs them against the case's blessed `expected.json`.

    run-corpus.py                 # run all cases against the default engine
    run-corpus.py --case ID ...   # run selected case(s)
    run-corpus.py --bless         # re-record expected.json (review the git diff!)
    run-corpus.py --json          # machine-readable report

Per-case outcome (the PASS/FAIL/STALE trichotomy):

    PASS        verdicts match expected.json
    PASS*       verdicts match, but the live rule corpus has changed since the
                case was blessed (stale signature — informational; re-bless to
                re-pin)
    FAIL        rule corpus unchanged since blessing, verdicts differ
                → an engine or fixture regression
    STALE-DIFF  rule corpus changed AND verdicts differ — expected churn from a
                rule edit; requires a conscious `--bless`, reviewed as the
                expected.json diff in the commit

Exit 0 iff no FAIL and no STALE-DIFF.

Engines are adapters. Doc/anchor cases run through `audit-plan` (the shipped
mechanical audit engine) or the `warden` reference doc-fire engine (F212) — the
same `(rule, target, status)` verdict contract; `--engine <name>` overrides the
per-case default so `--engine warden` genuinely runs the reference engine (not
just a signature re-pin). Moment cases (`family: moment`) run through the
`warden-moment` engine: fire a live moment against the fixture anchor and lock
the emitted **steers** — the moment-fire analogue of a doc verdict. Each case
pins to the signature of the surface its engine actually reads (doc-rule content
hash vs. moment dispatch+body hash).

Fixtures run from a temp-dir sandbox, never in place: `fixture/` is copied out
and `_anchor.yaml` (if present) materializes as `.anchor` in the copy — so the
stored corpus never carries a live `.anchor` (no anchor-scan pollution) and the
engine never mistakes corpus internals for scope.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
CORPUS_DIR = HARNESS_DIR.parent
CASES_DIR = CORPUS_DIR / "cases"
import sys as _sys
_sys.path.insert(0, str(CORPUS_DIR.parents[0] / "engine"))
from warden_root import corpus_root as _corpus_root
REPO_ROOT = _corpus_root()                 # …/dans-anchor-system
AUDIT_PLAN = REPO_ROOT / "skills" / "audit" / "scripts" / "audit-plan.py"
WARDEN_ENGINE_DIR = CORPUS_DIR.parent / "engine"   # …/warden/engine


# ── case.yaml (flat key: value — no YAML dependency) ────────────────────────

def read_case_yaml(path: Path) -> dict:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def write_case_yaml(path: Path, meta: dict) -> None:
    order = ["id", "family", "mode", "target", "moment", "provenance", "engine",
             "blessed_against", "note"]
    keys = [k for k in order if k in meta] + [k for k in meta if k not in order]
    path.write_text("".join(f"{k}: {meta[k]}\n" for k in keys), encoding="utf-8")


# ── engine adapters ──────────────────────────────────────────────────────────

def _audit_plan_module():
    spec = importlib.util.spec_from_file_location("audit_plan", AUDIT_PLAN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load engine module from {AUDIT_PLAN}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _warden_docfire_module():
    if str(WARDEN_ENGINE_DIR) not in sys.path:
        sys.path.insert(0, str(WARDEN_ENGINE_DIR))
    import warden_docfire  # noqa: E402
    return warden_docfire


_MOMENT_ENGINE = None


def _moment_engine():
    """The warm `WardenEngine` used for `warden-moment` cases — built once and
    reused (its compile is memoized), so N moment cases pay one corpus compile."""
    global _MOMENT_ENGINE
    if _MOMENT_ENGINE is None:
        if str(WARDEN_ENGINE_DIR) not in sys.path:
            sys.path.insert(0, str(WARDEN_ENGINE_DIR))
        import warden_engine  # noqa: E402
        _MOMENT_ENGINE = warden_engine.WardenEngine(REPO_ROOT)
    return _MOMENT_ENGINE


def run_moment(anchor_root: Path, moment: str) -> list[str]:
    """Fire a live moment against the sandbox anchor and return its steers. The
    selftest bodies append to `$WARDEN_HOME/selftest.log`; point WARDEN_HOME at a
    throwaway dir so a corpus run never writes the real `~/.warden/selftest.log`."""
    import os
    home = tempfile.mkdtemp(prefix="warden-moment-home-")
    prev = os.environ.get("WARDEN_HOME")
    os.environ["WARDEN_HOME"] = home
    try:
        return _moment_engine().fire(anchor_root, moment)
    finally:
        if prev is None:
            os.environ.pop("WARDEN_HOME", None)
        else:
            os.environ["WARDEN_HOME"] = prev
        shutil.rmtree(home, ignore_errors=True)


def rule_corpus_signature(engine: str) -> str:
    """The live rule corpus' CONTENT signature — pins what a bless was against.
    Hashes the flattened rules' verdict-bearing fields (id/tier/where/check/fix)
    across both umbrellas, so it moves only when a rule change could move a
    verdict — message-wording and unrelated-file churn leave it stable. The
    `warden` reference engine reads the very same rulesets, so it pins to the
    same signature (a `warden` bless and an `audit-plan` bless are comparable)."""
    if engine == "audit-plan":
        mod = _audit_plan_module()
        warnings: list[str] = []
        return "-".join(mod._plan_rules_hash(mod.flatten_umbrella(u, warnings))
                        for u in ("R-doc", "R-anchor"))
    if engine == "warden":
        return _warden_docfire_module().corpus_signature()
    if engine == "warden-moment":
        return _moment_engine().moment_signature()
    raise SystemExit(f"run-corpus: unknown engine {engine!r}")


_SIG_CACHE: dict[str, str] = {}


def signature_for(engine: str) -> str:
    """Memoized live signature per engine — a mixed run (doc + moment cases) pins
    each case against the signature of the surface its engine actually reads."""
    if engine not in _SIG_CACHE:
        _SIG_CACHE[engine] = rule_corpus_signature(engine)
    return _SIG_CACHE[engine]


def run_engine(engine: str, target: Path, mode: str) -> list[dict]:
    """Adapter contract: run the engine on a sandboxed target, return raw verdicts
    as a list of {rule, target, status, detail}."""
    if engine == "audit-plan":
        out = subprocess.run(
            [sys.executable, str(AUDIT_PLAN), str(target),
             "--mode", mode, "--run", "--json", "--no-cache"],
            capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(f"audit-plan failed: {out.stderr.strip()}")
        return json.loads(out.stdout)["results"]
    if engine == "warden":
        # The Warden reference engine (F212): fire the compiled doc-rule IR
        # through the shared checker registry — in-process, no subprocess.
        return _warden_docfire_module().fire_audit(target, mode)
    raise SystemExit(f"run-corpus: unknown engine {engine!r}")


# ── canonicalization ─────────────────────────────────────────────────────────

def canonical(verdicts: list[dict]) -> list[dict]:
    """The golden equality view: (rule, target, status), sorted. `detail` is
    informational (message wording may churn freely) and excluded."""
    rows = [{"rule": v["rule"], "target": v["target"], "status": v["status"]}
            for v in verdicts]
    return sorted(rows, key=lambda r: (r["rule"], r["target"], r["status"]))


def canonical_moment(steers: list[str]) -> list[dict]:
    """The golden equality view for a moment case: the emitted steers, sorted.
    Locks the exact steer text a moment produces for the fixture anchor — the
    moment-fire analogue of the doc `(rule, target, status)` verdict."""
    return [{"steer": s} for s in sorted(steers)]


# ── the per-case run ─────────────────────────────────────────────────────────

def materialize(fixture: Path) -> Path:
    sandbox = Path(tempfile.mkdtemp(prefix="warden-corpus-"))
    dst = sandbox / "fixture"
    shutil.copytree(fixture, dst)
    marker = dst / "_anchor.yaml"
    if marker.is_file():
        marker.rename(dst / ".anchor")
    return dst


def engine_for(meta: dict, override: str | None) -> str:
    """Pick the engine to run a case through. Moment cases are engine-fixed
    (`warden-moment`); doc/anchor cases honour the `--engine` override (so
    `--engine warden` really runs the reference engine, not just re-pins the
    signature), else the case's declared engine, else audit-plan."""
    if meta.get("family") == "moment":
        return "warden-moment"
    return override or meta.get("engine", "audit-plan")


def run_case(case_dir: Path, bless: bool, override: str | None = None) -> dict:
    meta = read_case_yaml(case_dir / "case.yaml")
    engine = engine_for(meta, override)
    live_sig = signature_for(engine)
    fixture = case_dir / "fixture"
    sandbox = materialize(fixture)
    try:
        target = sandbox if meta["target"] == "." else sandbox / meta["target"]
        if engine == "warden-moment":
            got = canonical_moment(run_moment(sandbox, meta["moment"]))
        else:
            got = canonical(run_engine(engine, target, meta["mode"]))
    finally:
        shutil.rmtree(sandbox.parent, ignore_errors=True)

    expected_fp = case_dir / "expected.json"
    if bless:
        expected_fp.write_text(json.dumps(got, indent=1) + "\n", encoding="utf-8")
        meta["blessed_against"] = live_sig
        write_case_yaml(case_dir / "case.yaml", meta)
        return {"case": meta["id"], "outcome": "BLESSED", "verdicts": len(got)}

    if not expected_fp.is_file():
        return {"case": meta["id"], "outcome": "UNBLESSED",
                "diff": ["no expected.json — run with --bless"]}
    expected = json.loads(expected_fp.read_text(encoding="utf-8"))
    stale = meta.get("blessed_against") != live_sig
    if got == expected:
        return {"case": meta["id"], "outcome": "PASS*" if stale else "PASS",
                "verdicts": len(got)}
    diff = ([f"- {json.dumps(r)}" for r in expected if r not in got]
            + [f"+ {json.dumps(r)}" for r in got if r not in expected])
    return {"case": meta["id"], "outcome": "STALE-DIFF" if stale else "FAIL",
            "diff": diff}


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv):
    ap = argparse.ArgumentParser(prog="run-corpus")
    ap.add_argument("--case", action="append", help="case id(s) to run (default: all)")
    ap.add_argument("--engine", default=None,
                    help="run doc/anchor cases through this engine "
                         "(audit-plan | warden); default: the case's own engine")
    ap.add_argument("--bless", action="store_true",
                    help="re-record expected.json + re-pin blessed_against")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    case_dirs = sorted(d for d in CASES_DIR.iterdir()
                       if d.is_dir() and (d / "case.yaml").is_file())
    if args.case:
        case_dirs = [d for d in case_dirs
                     if read_case_yaml(d / "case.yaml").get("id") in args.case
                     or d.name in args.case]
        if not case_dirs:
            raise SystemExit(f"run-corpus: no case matches {args.case}")

    results = [run_case(d, args.bless, args.engine) for d in case_dirs]
    bad = [r for r in results if r["outcome"] in ("FAIL", "STALE-DIFF", "UNBLESSED")]
    sigs = "  ·  ".join(f"{e} {s}" for e, s in sorted(_SIG_CACHE.items()))

    if args.json:
        print(json.dumps({"rule_corpus_sigs": _SIG_CACHE, "results": results,
                          "ok": not bad}, indent=1))
    else:
        for r in results:
            line = f"{r['outcome']:10s} {r['case']}"
            if "verdicts" in r:
                line += f"  ({r['verdicts']} verdicts)"
            print(line)
            for d in r.get("diff", []):
                print(f"    {d}")
        print(f"\n{len(results) - len(bad)}/{len(results)} ok  ·  {sigs}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
