#!/usr/bin/env python3
"""M5 perf hardening — cache invalidation under a stress workload, plus the
advisory ms-budget policy (PRD Q3, resolved advisory-first 2026-07-05).

Three caches keep the hot path fast; each must invalidate correctly under
churn or Warden silently fires stale rules:

  1. the recompile cache (`source_hash` over the scan index) — a changed
     ruleset must MISS, an unchanged corpus must HIT, across many rounds;
  2. the daemon's warm Corpus — artifact rewrites on disk must be picked up
     by the mtime freshness check on the next request;
  3. the reval store (F215) — an external reset/truncation must win over the
     warm in-process copy.

Runnable standalone — no test framework.
"""
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_compile as wc  # noqa: E402
import warden_hook as wh  # noqa: E402
import warden_reval as wr  # noqa: E402
import warden_scan  # noqa: E402

RULESET_TMPL = """\
# RULESET R-stress-{n}

where:: file:{{ANCHOR}}/**/*.md
description:: stress fixture ruleset {n}

### RULE R-stress-{n}-01 — rule v{rev} (checked)

check:: frontmatter_has description
"""


def _write_corpus(root: Path, nsets: int, revs: dict[int, int]) -> None:
    for n in range(nsets):
        (root / f"stress-{n}.md").write_text(
            RULESET_TMPL.format(n=n, rev=revs.get(n, 0)), encoding="utf-8")


def test_recompile_cache_under_churn(tmp: Path):
    """30 rounds of mutate-or-hold: the cache key must miss exactly when a
    ruleset changed and hit exactly when nothing did — no false hits (stale
    rules) and no false misses (wasted recompiles)."""
    root = tmp / "corpus"
    root.mkdir()
    revs: dict[int, int] = {}
    _write_corpus(root, 4, revs)

    def index_hash():
        files, _seen, _ = warden_scan.build_index(str(root), {}, {}, rescan=True)
        return warden_scan.index_hash(files), files

    h_prev, files = index_hash()
    out = tmp / "artifacts"
    ir, module_src, _ = wc.compile_corpus(
        root, {"root": str(root), "files": files, "seen": {}}, "all", h_prev)
    wc._write_artifacts(out, "all", ir, module_src)
    assert wc.cached_source_hash(out) == h_prev

    misses = hits = 0
    for round_ in range(30):
        mutate = round_ % 3 != 2          # two mutating rounds, then a hold
        if mutate:
            n = round_ % 4
            revs[n] = revs.get(n, 0) + 1
            _write_corpus(root, 4, revs)
        h_now, files = index_hash()
        cached = wc.cached_source_hash(out)
        if mutate:
            assert cached != h_now, f"round {round_}: FALSE HIT — stale rules would fire"
            ir, module_src, _ = wc.compile_corpus(
                root, {"root": str(root), "files": files, "seen": {}}, "all", h_now)
            wc._write_artifacts(out, "all", ir, module_src)
            misses += 1
        else:
            assert cached == h_now, f"round {round_}: FALSE MISS — wasted recompile"
            hits += 1
    assert misses == 20 and hits == 10, (misses, hits)
    print(f"PASS  recompile_cache_under_churn ({misses} misses / {hits} hits, all correct)")


def test_daemon_corpus_freshness(tmp: Path):
    """The daemon's warm Corpus reloads on artifact rewrite (mtime check) —
    exercised directly against the class, 10 rewrite rounds."""
    import warden_daemon as wd
    home = tmp / "daemon-home"
    home.mkdir()
    corpus = None
    for round_ in range(10):
        (home / "rules-ir.json").write_text(
            '{"schema": 1, "moments": {}, "rules": {}, "traits": {}, '
            f'"round": {round_}}}', encoding="utf-8")
        # mtime_ns granularity is fine, but keep rounds distinguishable
        os.utime(home / "rules-ir.json", ns=(time.time_ns(), time.time_ns() + round_ + 1))
        if round_ == 0:
            corpus = wd.Corpus(home)
        else:
            corpus.fresh()
        assert corpus.ir.get("round") == round_, \
            f"round {round_}: warm corpus served stale IR {corpus.ir.get('round')}"
    print("PASS  daemon_corpus_freshness (10 rewrite rounds picked up)")


def test_reval_external_reset(tmp: Path):
    """An external reset of reval.json must win over the warm store instance
    (the daemon holds one for its lifetime); rapid alternating writers must
    never corrupt the file."""
    home = tmp / "reval-home"
    st = wr.RevalStore(home)
    f = tmp / "doc.md"
    st.mark_evaluated("R-s-01", f, "v1", verdict=["v1"])
    assert st.verdict("R-s-01", f) == ["v1"]
    # external reset (e.g. a manual wipe) — the warm instance must notice
    time.sleep(0.02)  # ensure a distinct mtime_ns on coarse filesystems
    st.path.unlink()
    assert st.record("R-s-01", f) is None, "warm store served a wiped record"
    # two writers alternating 40 rounds: last-writer-wins, file stays valid JSON
    a, b = wr.RevalStore(home), wr.RevalStore(home)
    for i in range(40):
        (a if i % 2 == 0 else b).mark_evaluated("R-s-01", f, f"v{i}", verdict=[i])
    fresh = wr.RevalStore(home)
    rec = fresh.record("R-s-01", f)
    assert rec is not None and rec["verdict"] == [39], rec
    print("PASS  reval_external_reset (reset + 40 alternating writes, no corruption)")


def test_budget_advisory():
    """The advisory ms-budget policy: correct per-class budgets, warn only
    when exceeded, never any drop/demote side effect."""
    assert wh.budget_ms("tool:pre:Bash") == 2.0
    assert wh.budget_ms("tool:post:Write") == 10.0
    assert wh.budget_ms("write:markdown") == 10.0
    assert wh.budget_ms("session:start") == 100.0
    assert wh.over_budget("write:markdown", 9.9) is None
    warn = wh.over_budget("write:markdown", 25.0)
    assert warn and "OVER-BUDGET write:markdown" in warn and "budget 10 ms" in warn, warn
    assert wh.over_budget("tool:pre:Bash", 2.5) and wh.over_budget("session:start", 99.0) is None
    print("PASS  budget_advisory")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        os.environ["WARDEN_VAULT"] = str(tmp)  # keep declared-trait walks local
        try:
            test_recompile_cache_under_churn(tmp)
            test_daemon_corpus_freshness(tmp)
            test_reval_external_reset(tmp)
            test_budget_advisory()
        finally:
            os.environ.pop("WARDEN_VAULT", None)
    print("\nall warden stress tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
