#!/usr/bin/env python3
"""Differential test — Warden doc-fire ≡ audit-plan verdicts (F212 / F214).

For every golden-corpus fixture, fire the doc-rules two ways — through the Warden
reference engine (`warden_docfire.fire_audit`, IR-driven, in-process) and through
the shipped `audit-plan --run` engine (subprocess) — and assert the canonical
verdict sets `(rule, target, status)` are identical. This is the differential
layer F214 specifies: the two engines cannot drift silently because a divergence
fails here regardless of what `expected.json` is blessed against. Runnable
standalone (no pytest).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CASES = REPO / "warden" / "Warden Corpus" / "cases"
AUDIT_PLAN = REPO / "skills" / "audit" / "scripts" / "audit-plan.py"
sys.path.insert(0, str(HERE))

import warden_docfire as wd  # noqa: E402


def _read_case_yaml(path: Path) -> dict:
    meta: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def _materialize(fixture: Path) -> Path:
    sandbox = Path(tempfile.mkdtemp(prefix="warden-docfire-test-"))
    dst = sandbox / "fixture"
    shutil.copytree(fixture, dst)
    marker = dst / "_anchor.yaml"
    if marker.is_file():
        marker.rename(dst / ".anchor")
    return dst


def _canonical(verdicts: list[dict]) -> list[tuple]:
    return sorted((v["rule"], v["target"], v["status"]) for v in verdicts)


def _audit_plan_verdicts(target: Path, mode: str) -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(AUDIT_PLAN), str(target),
         "--mode", mode, "--run", "--json", "--no-cache"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["results"]


def test_docfire_matches_audit_plan_on_every_case():
    case_dirs = sorted(d for d in CASES.iterdir()
                       if d.is_dir() and (d / "case.yaml").is_file())
    assert case_dirs, "no corpus cases found"
    for case_dir in case_dirs:
        meta = _read_case_yaml(case_dir / "case.yaml")
        mode = meta["mode"]
        if mode not in ("doc", "anchor"):
            continue  # moment cases are the live-fire path, not the doc-audit surface
        sandbox = _materialize(case_dir / "fixture")
        try:
            target = sandbox if meta["target"] == "." else sandbox / meta["target"]
            warden = _canonical(wd.fire_audit(target, mode))
            audit = _canonical(_audit_plan_verdicts(target, mode))
        finally:
            shutil.rmtree(sandbox.parent, ignore_errors=True)
        assert warden == audit, (
            f"{meta['id']}: verdict divergence\n"
            f"  warden-only:    {[v for v in warden if v not in audit]}\n"
            f"  audit-plan-only: {[v for v in audit if v not in warden]}")
        print(f"PASS  {meta['id']}  ({len(warden)} verdicts, warden ≡ audit-plan)")


def test_signature_matches_audit_plan():
    # the warden doc-fire pins to the same content signature audit-plan does
    out = subprocess.run(
        [sys.executable, str(REPO / "warden" / "Warden Corpus" / "harness" / "run-corpus.py"),
         "--engine", "audit-plan", "--json"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    audit_sig = json.loads(out.stdout)["rule_corpus_sigs"]["audit-plan"]
    assert wd.corpus_signature() == audit_sig, (wd.corpus_signature(), audit_sig)
    print(f"PASS  signature ≡ audit-plan  ({audit_sig})")


def main():
    test_docfire_matches_audit_plan_on_every_case()
    test_signature_matches_audit_plan()
    print("\nall warden_docfire tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
