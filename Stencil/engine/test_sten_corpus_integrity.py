#!/usr/bin/env python3
"""Corpus integrity check (T177) — a specimen's bytes must never move silently.

`design/Template Examples.md`'s own discipline is "cases are quoted from real
files, never invented," and every scored pair in `test_sten_match.py` /
`test_sten_generate.py` carries a human verdict alongside the specimen that
verdict was given to.  Nothing re-checks that the specimen a verdict names is
still the specimen sitting there: a link-rewrite tool (`anchor rename
--rewrite-links`), an agent, or a person can edit inside a
`<!-- begin example ... -->` block and both test suites stay green, because
they read whatever bytes are there NOW rather than the bytes the verdict was
actually written against. That happened once already — `[[DKT Backlog]]`
became `[[DKT Backlog Archive]]` inside T6.b with no verdict flipping, purely
by luck.

This suite hashes every delimited block `sten_corpus.blocks()` extracts (the
SAME region extraction `test_sten_match.py` / `test_sten_generate.py` already
use — no second parser for the `<!-- begin/end -->` grammar) and compares each
hash against `Template Examples.manifest.json`, sitting next to the corpus
itself. A hash mismatch, a missing label, or a new unrecorded label all fail
the run and name exactly which specimen changed.

Standalone: `python3 test_sten_corpus_integrity.py`.  Exit 0 iff every block's
hash matches the manifest.

To **legitimately** re-quote a specimen — the source file it quotes really did
change, and the case should track the new bytes — this must be a deliberate,
one-command act, never a side effect of fixing the red run:

    python3 test_sten_corpus_integrity.py --update

Before running `--update`, update every verdict/prose in `Template
Examples.md` that depended on the old bytes; the manifest only records that a
change was deliberate, it does not check the verdict still holds.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sten_corpus as C          # noqa: E402

MANIFEST = C.CORPUS.with_name("Template Examples.manifest.json")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_manifest() -> dict[str, str]:
    """Label -> sha256 of every block `sten_corpus.blocks()` extracts, as of
    the corpus's current on-disk bytes."""
    return {label: _hash(body) for label, body in C.blocks().items()}


def write_manifest() -> dict[str, str]:
    manifest = compute_manifest()
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def check() -> tuple[bool, list[str]]:
    """Compare the corpus's current blocks against the recorded manifest.
    Returns `(ok, problems)` — `problems` names every changed, new, or
    missing label, never a bare count."""
    recorded = load_manifest()
    current = compute_manifest()
    problems = []
    for label in sorted(set(recorded) | set(current)):
        if label not in current:
            problems.append(f"{label}: in the manifest but MISSING from the corpus now")
        elif label not in recorded:
            problems.append(f"{label}: NEW block, not yet recorded in the manifest")
        elif recorded[label] != current[label]:
            problems.append(f"{label}: bytes changed — hash no longer matches the manifest")
    return not problems, problems


UPDATE_HELP = (
    "\n  A specimen's bytes no longer match the recorded manifest.  This is the "
    "failure T177 exists to catch: a rewriter (or an agent, or a person) edited "
    "a quoted specimen, and the verdict scored against it in test_sten_match.py "
    "/ test_sten_generate.py silently kept pointing at the OLD bytes.\n\n"
    "  If this is an unintended edit (e.g. a vault-wide link rewrite that "
    "reached inside a `<!-- begin example ... -->` block): restore the "
    "specimen's original bytes and re-run.\n\n"
    "  If the specimen genuinely SHOULD change (the source file it quotes was "
    "legitimately re-quoted): first update every verdict/prose in `Template "
    "Examples.md` that depends on the old bytes, THEN run:\n"
    "      python3 test_sten_corpus_integrity.py --update\n"
    "  to deliberately record the new hash. Never run --update just to make a "
    "red run pass."
)


def main() -> int:
    if "--update" in sys.argv:
        manifest = write_manifest()
        print(f"wrote {MANIFEST.name}: {len(manifest)} block(s) recorded.")
        return 0

    print("=== corpus integrity: every delimited block vs its recorded hash ===")
    if not MANIFEST.exists():
        print(f"  no manifest at {MANIFEST.name} — run with --update to create one.")
        print("\nSUITE RED")
        return 1

    ok, problems = check()
    print(f"  {len(compute_manifest())} block(s) checked against {MANIFEST.name}")
    if problems:
        print("\n=== unattributed change(s) to the evidence corpus ===")
        for p in problems:
            print(f"  XX  {p}")
        print(UPDATE_HELP)
        print("\nSUITE RED")
        return 1
    print("\nSUITE GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
