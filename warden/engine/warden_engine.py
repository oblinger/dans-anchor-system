#!/usr/bin/env python3
"""Warden reference engine — the unified compile→install→fire loop (F212 / M2).

Ties the three engine stages into one lazy entry point:

  scan (warden_scan)  →  compile (warden_compile, cached)  →  fire (warden_fire)

`WardenEngine(root)` is the warm, in-process reference implementation the Rust
performance engine ([[F213]]) is differential-tested against — the **behavioral
oracle**. It compiles the rule corpus **lazily** on first fire (M1 Q1: compile
on entry, never for a session that never fires) and memoizes it for the process
lifetime; `fire(anchor_root, moment)` then assembles the moment `ctx`, resolves
the anchor's active-set from its `.anchor` traits, and runs the moment's rules.

This is a thin composition — the parse/split/emit lives in `warden_compile`, the
dispatch in `warden_fire` — so there is exactly one implementation of each stage
(no parallel engine). Installing the compiled modules into the *live* Claude
Code hook surface is the M4 productionisation layer above this reference loop.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import warden_compile as wc     # noqa: E402
import warden_docfire as wdf     # noqa: E402
import warden_fire as wf        # noqa: E402
import warden_scan as ws        # noqa: E402


class WardenEngine:
    """The warm reference engine for one rule-corpus `root` (the vault root)."""

    def __init__(self, root: str | Path, anchor_module: str = "all"):
        self.root = Path(root).expanduser().resolve()
        self.anchor_module = anchor_module
        self._ir: dict | None = None
        self._module = None
        self._module_src: str | None = None
        self._source_hash: str | None = None

    # ── lazy compile (warm-start) ────────────────────────────────────────────

    def ensure_compiled(self, force: bool = False):
        """Compile the corpus on first fire and memoize it for the process (the
        M1 lazy warm-start: compile on entry, reuse for the session). `force`
        re-scans + recompiles — used when the corpus is known to have changed
        mid-session; the cross-process recompile cache lives on disk in
        `warden_compile`."""
        if self._ir is not None and not force:
            return
        files, seen, _ = ws.build_index(str(self.root), {}, {}, rescan=True)
        source_hash = ws.index_hash(files)
        index = {"root": str(self.root), "files": files, "seen": seen}
        ir, module_src, _ = wc.compile_corpus(self.root, index, self.anchor_module, source_hash)
        self._ir = ir
        self._source_hash = source_hash
        self._module_src = module_src
        # materialise the emitted module in-process
        ns: dict = {}
        exec(compile(module_src, f"<rules_{self.anchor_module}>", "exec"), ns)
        self._module = _NS(ns)

    # ── fire ─────────────────────────────────────────────────────────────────

    def fire(self, anchor_root: str | Path, moment: str, **ctx_overrides) -> list[str]:
        """Run the rules keyed at `moment` and active for the anchor at
        `anchor_root`; return their steers."""
        self.ensure_compiled()
        assert self._ir is not None
        anchor_root = Path(anchor_root).expanduser().resolve()
        ctx = wf.build_ctx(anchor_root, moment, **ctx_overrides)
        traits = wf.read_anchor_traits(anchor_root)
        return wf.fire(self._ir, self._module, moment, ctx, traits)

    def run_moments(self, anchor_root, moments: list[str]) -> dict:
        """Fire a stream of moments against one anchor → {moment: [steers]}
        (the simulated moment stream the F212 loop is specified over)."""
        return {m: self.fire(anchor_root, m) for m in moments}

    # ── doc-audit fire (the where-major tier doc-rules) ──────────────────────

    def fire_audit(self, target, mode: str) -> list[dict]:
        """Fire the tier **doc-rules** for `mode` (`doc`/`anchor`) against
        `target`, returning `{rule, target, status, detail}` verdicts. This is
        the authoring-time `/audit` pass of the same rule corpus — IR-driven and
        verdict-identical to `audit-plan --run` (the golden corpus proves it), so
        the reference engine owns both fire paths: the live moment stream and the
        doc-audit surface."""
        return wdf.fire_audit(Path(target).expanduser().resolve(), mode)

    # ── moment-fire signature (the golden-corpus moment-case pin) ─────────────

    def moment_signature(self) -> str:
        """Content signature of the moment-fire surface — the analogue of the
        doc-fire `corpus_signature` for the live moment stream. It hashes the
        moment dispatch table plus the emitted rule-body source, so it moves iff
        a moment rule's dispatch *or* its body could change a steer, and stays
        stable under unrelated corpus churn. Pins a moment-golden bless (the
        `warden-moment` engine's `blessed_against`)."""
        import hashlib
        import json
        self.ensure_compiled()
        assert self._ir is not None
        payload = (json.dumps(self._ir["moments"], sort_keys=True)
                   + "\x00" + (self._module_src or ""))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @property
    def ir(self) -> dict:
        self.ensure_compiled()
        assert self._ir is not None
        return self._ir


class _NS:
    """Adapt an exec namespace to attribute access (what warden_fire expects of
    the emitted module)."""
    def __init__(self, ns: dict):
        self.__dict__.update(ns)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-engine",
        description="Fire a moment against an anchor through the reference engine.")
    ap.add_argument("--root", required=True, help="the rule-corpus root (vault root)")
    ap.add_argument("--anchor-root", required=True, help="the anchor to fire against")
    ap.add_argument("--moment", required=True, help="moment to fire, e.g. skill:post:audit-q")
    args = ap.parse_args(argv)
    engine = WardenEngine(args.root)
    for steer in engine.fire(args.anchor_root, args.moment):
        print(steer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
