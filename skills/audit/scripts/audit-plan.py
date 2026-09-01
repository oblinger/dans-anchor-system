#!/usr/bin/env python3
"""audit-plan — the resolver/planner for the rule-driven audit engine (F161).

Stage 1 (RESOLVE) of the Resolve → Run → Judge pipeline:

  1. Flatten an umbrella ruleset (R-anchor / R-doc) by resolving its include:: DAG
     down to the leaf `# RULESET` blocks (standalone stubs OR embedded in facet /
     discipline / skill specs).
  2. Glob/sentinel-match each rule's `where::` selector against the target set
     (an anchor tree, or a single document) to build the (rule × target) match set.
     A selector that matches nothing => the rule is N/A (skipped, never failed).
  3. Materialize each leaf ruleset as a cached flat rule file (hashed → reused).
  4. Emit a query-plan recipe: per leaf ruleset, the cached flat file + each rule's
     tier + the targets it matched. The agent then follows the recipe — read a flat
     rule file, judge its listed targets — with no rule-selection thinking.

Stage 2 (RUN) executes the mechanical `checked`/`sampled` rules via `--run`: a
`check::` ref on a rule names a primitive in CHECKERS; verdicts are cached by
(rule-id, rule-body-hash, target-content-hash). Caches built here: the flattened
-rules cache (per-ruleset flat files + the shared flattened-umbrella cache, keyed
by a corpus signature) and the verdict cache.

Deferred to later F161 slices (announced, not silently dropped):
  - Stage 3 agent-judge of the `stated` / unscriptable `sampled` residue, cached
    by the full Q3 key (adds model-id). `checked` rules without a `check::` ref are
    still routed to the agent like `stated` rules.
  - The whole-plan cache (anchor-tree-hash + rules-hash) and anchor-manifest cache
    that would let an unchanged re-audit skip resolution entirely.

Usage:
  audit-plan <path-or-slug> [--mode anchor|doc] [--order file|rule]
                            [--json] [--cache-dir DIR] [--no-cache]
  audit-plan <path-or-slug> --run            # execute mechanical (check::) rules
  audit-plan <path-or-slug> --judge --model M  # emit agent-judgment manifest
  audit-plan --record-verdict --key K --status pass|fail [--detail D]
  audit-plan --batch <dir>  [--order rule] [--json] ...

  <path-or-slug>  An anchor folder, an anchor slug (resolved under the repo's
                  examples/ or cwd), or a single .md document.
  --mode          Force anchor- vs doc-level. Default: auto (dir/slug → anchor,
                  .md file → doc).
  --order         Recipe iteration order. Default: file-major for a single
                  anchor/doc, rule-major for --batch.
  --batch DIR     Rule-major sweep over every anchor (dir containing `.anchor`)
                  under DIR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

HOME = Path.home()

# ── repo discovery ──────────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    """Walk up from the script to the dans-anchor-system repo root (has facets/ + skills/)."""
    for p in [start, *start.parents]:
        if (p / "facets").is_dir() and (p / "skills").is_dir():
            return p
    # Fallback: the script lives at skills/audit/scripts/ → repo is 3 up.
    return start.parents[2]


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root(SCRIPT_DIR)


# ── markdown / wiki-link index ──────────────────────────────────────────────

_MD_INDEX: dict[str, list[Path]] | None = None


def md_index() -> dict[str, list[Path]]:
    """basename (no extension) → [paths]. Built once, lazily, over the repo."""
    global _MD_INDEX
    if _MD_INDEX is None:
        idx: dict[str, list[Path]] = {}
        for p in REPO_ROOT.rglob("*.md"):
            if "/.git/" in str(p):
                continue
            idx.setdefault(p.stem, []).append(p)
        _MD_INDEX = idx
    return _MD_INDEX


def resolve_file(name: str) -> Path | None:
    """Resolve a wiki-link target (a basename, no #fragment) to a file path."""
    hits = md_index().get(name)
    if not hits:
        return None
    # Prefer a hit under facets/ or the Rulesets catalog when ambiguous.
    hits = sorted(hits, key=lambda p: (("facets" not in p.parts), len(p.parts)))
    return hits[0]


# ── ruleset parsing ────────────────────────────────────────────────────────

_RULESET_RE = re.compile(r"^(#+)\s+RULESET\s+(R-[\w-]+)\s*$")
# Six tiers, not four. `retired` and `governing` were admitted 2026-08-11 because
# both are live in the corpus and neither parsed: a heading this regex rejects is
# SKIPPED, and a skipped heading does not end the rule above it, so the `check::`
# beneath it folds onto its predecessor. That is not hypothetical — it silently
# disabled `R-rocks-03`, which ran `R-rocks-04`'s checker and reported that
# verdict as its own, passing green on every rock group without ever being
# evaluated. It was the SECOND occurrence in the same ruleset (T156 records
# `(checked, warn)` folding rule 05 onto rule 04), and it recurs because a
# malformed tier makes a rule invisible to the very checks that would catch it —
# every other consumer reads PARSED rules, where the offending heading is gone.
# Admitting a tier is only half: `_needs_judgment` is a membership test, so both
# new tiers are excluded there too, or every retired rule starts billing agent
# judgment on every audit. `R-ruleset-06` is now wired as the standing guard.
_RULE_RE = re.compile(
    r"^#+\s+RULE\s+(R-[\w-]+-\d+)\s+[—-]\s+(.*?)\s*"
    r"\((checked|sampled|stated|tracked|retired|governing)\)\s*$"
)
_FIELD_RE = re.compile(r"^([a-z][a-z_-]*)::\s*(.*)$")
# One wiki-link span, for the whole file. `group(0)` is the span, `group(1)` its
# inner text. The class excludes `[` as well as `]`, and that is the point: the
# earlier `[^\]]+` let an UNCLOSED `[[` run forward to the next `]]` anywhere on
# the line, so in a table row `| [[broken | [[Good]] |` it matched from `[[broken`
# across the real cell delimiter. `fix_md_table_pipe_escape` escaped that
# delimiter, merging two cells, and the paired check went fail → pass — so the
# on-write driver reported the row FIXED. Forbidding a nested `[[` stops the span
# at the typo instead of swallowing the row. Alias / heading / block-id pipes stay
# INSIDE the span deliberately: they are link content, and escaping them is what
# the table-pipe caller exists to do.
#
# A second definition of this name was briefly added near the structure primitives
# and SHADOWED this one at module level — silently, since both answered `group(0)`.
# One name, one definition; that is the whole T099 thesis and it applies to the
# fix as much as to the defect.
_WIKILINK_RE = re.compile(r"\[\[([^\[\]]*?)\]\]")

# The OTHER link spelling — a markdown inline link, `[text](target)`. Extracted
# 2026-08-20 from the one non-primitive site that spelled it by hand
# (`chk_dispatch_cell_narrative`, which already routed its wiki-links through
# `_WIKILINK_RE` and then inlined this one beneath it), on `structure-lint`'s
# ratchet. Byte-identical to the literal it replaces, so the extraction cannot
# move a verdict — which is why it needs no population measurement, unlike a
# primitive that generalizes.
#
# The lint files it under `wiki-link`, which is the wrong CLASS for the right
# FINDING: `CLASSES["wiki-link"]` matches `\[\[` and this pattern opens `\[[`,
# a `\[` beside a character class. Worth knowing before the next such report is
# read as a stray wiki-link matcher.
_MDLINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")


def _strip_link_target(raw: str) -> str:
    """`[[DAS Brief#RULESET R-brief|embedded body]]` → `DAS Brief#RULESET R-brief`."""
    inner = raw.strip()
    if inner.startswith("[[") and inner.endswith("]]"):
        inner = inner[2:-2]
    # Split at the alias pipe whether or not it carries the in-table escape, then
    # drop the escape. This is the OPPOSITE of `_row_cells`, deliberately: there a
    # `\|` is NOT a cell boundary; here it IS the alias separator, merely written
    # for a table. Splitting on unescaped pipes only was tried and is wrong — it
    # hands back the whole `Target\|Label` as the target. Without the `rstrip` the
    # target keeps a trailing backslash, and the sole caller feeds `include::`
    # targets to `load_ruleset`, where a residue resolves to no file and the
    # included ruleset silently never loads — the zero-output failure mode again.
    # Latent today (no live `include::` uses the escape), and cheap to close.
    return inner.split("|", 1)[0].rstrip("\\").strip()


def _strip_ticks(val: str) -> str:
    """Strip a single surrounding backtick pair from a field value (F172 —
    `` where:: `file:{anchor}/**/*.md` `` is the canonical authored form).
    Values whose interior contains further backticks (prose with inline code
    spans) pass through untouched, as does the bare legacy form."""
    if len(val) >= 2 and val[0] == "`" and val[-1] == "`" and "`" not in val[1:-1]:
        return val[1:-1].strip()
    return val


def extract_ruleset_block(text: str, name: str | None = None) -> tuple[list[str], int] | None:
    """Return (block_lines, heading_level) for `# RULESET <name>` (or first RULESET
    block when name is None). Block spans until the next heading of level <= its own."""
    lines = text.splitlines()
    # Structural decisions read the code-MASKED lines; the block returned is the
    # real ones (F296 finding 3). Without this, a shell `# comment` inside a
    # fenced example parses as a level-1 heading, and `<= level` is true of every
    # level — so the block ends at the fence and every RULE after it silently
    # leaves the engine: never planned, never judged, never reported N/A. That is
    # the one failure here with NO output at all, so nothing would ever show it.
    masked = _code_masked_lines(text)
    start = None
    level = None
    for i, ln in enumerate(masked):
        m = _RULESET_RE.match(ln)
        if m and (name is None or m.group(2) == name):
            start = i
            level = len(m.group(1))
            break
    if start is None or level is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(masked)):
        hm = re.match(r"^(#+)\s+\S", masked[j])
        if hm and len(hm.group(1)) <= level:
            end = j
            break
    return lines[start:end], level


def parse_ruleset_block(block: list[str], source: Path) -> dict:
    """Parse a RULESET block's header fields + RULE entries into a dict."""
    header = _RULESET_RE.match(block[0])
    assert header is not None  # block[0] is always the RULESET heading line
    rs = {
        "name": header.group(2),
        "where": None,
        "confirm": None,
        "description": None,
        "includes": [],
        "imports": [],
        "rules": [],
        "source": str(source.relative_to(REPO_ROOT)),
    }
    # Header fields: contiguous `field::` lines after the RULESET line, before body.
    i = 1
    while i < len(block):
        ln = block[i].strip()
        if not ln:
            i += 1
            continue
        fm = _FIELD_RE.match(ln)
        if not fm:
            break
        key, val = fm.group(1), fm.group(2).strip()
        if key == "include":
            rs["includes"] = [_strip_link_target(m.group(0)) for m in _WIKILINK_RE.finditer(val)]
        elif key == "import":
            # Corpus-root-relative paths to the Python providing this ruleset's
            # `check::` implementations (F289). Accumulated across repeated
            # `import::` lines; whitespace- or comma-separated within one.
            rs["imports"].extend(_strip_ticks(p) for p in re.split(r"[,\s]+", val) if p.strip())
        elif key == "where":
            rs["where"] = _strip_ticks(val) or None
        elif key == "confirm":
            # `confirm:: user` (F314) — this ruleset's rules may not be excepted
            # on the agent's own say-so. Inherited by every rule in the set
            # unless a rule overrides it, exactly like `where::`.
            rs["confirm"] = _strip_ticks(val) or None
        elif key == "description":
            rs["description"] = val or None
        i += 1
    # RULE entries. A fenced example of a RULE heading or a `check::` field is a
    # picture of the form, not the form (F296 finding 3) — a phantom rule, or a
    # real rule's action overwritten by an illustration. Structure is decided on
    # the masked block; VALUES are still read from the real line, because
    # `_mask_code` blanks inline spans and `where:: `file:…`` is authored with
    # them (F172). A line the mask emptied but the source did not is code.
    masked_block = _code_masked_lines("\n".join(block))
    cur = None
    for idx in range(i, len(block)):
        ln = block[idx]
        mln = masked_block[idx] if idx < len(masked_block) else ln
        if ln.strip() and not mln.strip():
            continue
        rm = _RULE_RE.match(ln)
        if rm:
            cur = {
                "id": rm.group(1),
                "title": rm.group(2).strip(),
                "tier": rm.group(3),
                "where": None,
                "confirm": None,
                "check": None,
                "fix": None,
                "check_pattern": None,
                "why": None,
            }
            rs["rules"].append(cur)
            continue
        if cur is None:
            continue
        s = ln.strip()
        wm = _FIELD_RE.match(s)
        if wm and wm.group(1) in ("where", "check", "fix", "confirm"):
            fv = wm.group(2).strip()
            if wm.group(1) in ("where", "confirm"):
                fv = _strip_ticks(fv)
            cur[wm.group(1)] = fv or None
        elif s.startswith("**Check pattern:**"):
            cur["check_pattern"] = s.split("**Check pattern:**", 1)[1].strip()
        elif s.startswith("**Why:**"):
            cur["why"] = s.split("**Why:**", 1)[1].strip()
    return rs


def load_ruleset(target: str, visited: set[str], warnings: list[str]) -> list[dict]:
    """Resolve a link target to leaf rulesets (those with RULE entries),
    following include:: recursively. Returns a flat list of ruleset dicts."""
    filepart, _, fragment = target.partition("#")
    filepart = filepart.strip()
    fragment = fragment.strip()
    name = None
    if fragment:
        fm = re.match(r"RULESET\s+(R-[\w-]+)", fragment)
        if fm:
            name = fm.group(1)
    path = resolve_file(filepart)
    if path is None:
        # No file by that basename — fall back to a repo-wide search for an
        # embedded `# RULESET <filepart>` block (covers stub-less rulesets like
        # R-ruleset / R-file-association that live only inside a facet/discipline).
        if filepart.startswith("R-"):
            found = _search_embedded(filepart)
            if found:
                return found
        warnings.append(f"unresolved include target: {target!r}")
        return []

    key = f"{path}#{name or ''}"
    if key in visited:
        return []
    visited.add(key)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        warnings.append(f"cannot read {path}: {e}")
        return []

    blk = extract_ruleset_block(text, name)
    if blk is None:
        warnings.append(f"no RULESET block {name or ''} in {path.name}")
        return []
    rs = parse_ruleset_block(blk[0], path)

    result: list[dict] = []
    if rs["rules"]:
        result.append(rs)
    # Recurse into includes (umbrellas + stubs that point at embedded bodies).
    for inc in rs["includes"]:
        result.extend(load_ruleset(inc, visited, warnings))
    return result


def _search_embedded(name: str) -> list[dict]:
    """Find an embedded `# RULESET <name>` block anywhere in the repo."""
    for p in REPO_ROOT.rglob("*.md"):
        if "/.git/" in str(p):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if f"RULESET {name}" not in text:
            continue
        blk = extract_ruleset_block(text, name)
        if blk:
            rs = parse_ruleset_block(blk[0], p)
            if rs["rules"]:
                return [rs]
    return []


def flatten_umbrella(umbrella: str, warnings: list[str]) -> list[dict]:
    """Flatten an umbrella (R-anchor / R-doc / any ruleset link) to leaf rulesets,
    de-duplicated by ruleset name (first occurrence wins)."""
    leaves = load_ruleset(umbrella, set(), warnings)
    seen, out = set(), []
    for rs in leaves:
        if rs["name"] in seen:
            continue
        seen.add(rs["name"])
        out.append(rs)
    register_imports(out)
    return out


# ── checker registration — `import::` on the ruleset (F289) ─────────────────
#
# Where a `check::` ref finds its implementation used to be engine policy: the
# fire path loaded exactly one file, at a path assembled from a hardcoded string
# inside dans-anchor-system, and that file's `CHECKERS` dict was the entire
# vocabulary a ref could name. A consumer handed the engine could write
# `check:: my_thing` and had nowhere on disk to put `my_thing`.
#
# A ruleset now declares the Python its refs need, beside the `include::` it
# already carries, corpus-root-relative:
#
#     import:: skills/audit/scripts/audit-plan.py
#
# Execution uses ONE merged environment — `check::` refs are global names against
# a flat registry, and per-ruleset environments would misdescribe that. But a
# purely global model lets a ruleset's refs resolve BY ACCIDENT, satisfied by an
# import some neighbouring ruleset declared: harmless inside one corpus, and
# precisely the failure when that ruleset is extracted into a new one, where it
# breaks because its dependency was covered by a file it never named. So
# `verify_registrations` checks each ruleset's refs against its OWN declared
# imports and warns when a ref resolves only globally. Runtime is unchanged; the
# declaration merely loses the ability to lie.

class CorpusError(RuntimeError):
    """A corpus declares something the engine cannot honour — a missing import
    file, an unloadable module. Raised rather than warned: an import that does
    not resolve silently empties a ruleset's whole vocabulary, and every rule in
    it then reads as agent-judgment work with nothing to say it was demoted."""


# `check::` and `fix::` are TWO registries, not one. Conflating them is not a
# hypothetical: the first cut of this verification checked both against
# `CHECKERS` and reported `R-doc-structure-01 — fix:: breadcrumb_position` as a
# ghost, when `breadcrumb_position` is a perfectly good registered FIXER. F289's
# own "11 ghosts" measurement carried the same conflation and is corrected to 10
# here. A ref is a ghost only against the registry its FIELD resolves through.
_IMPORTED: dict[str, tuple[dict, dict]] = {}  # corpus-relative path -> (CHECKERS, FIXERS)
_REGISTRY: dict | None = None          # merged checker name -> fn
_FIX_REGISTRY: dict | None = None      # merged fixer name -> fn
_REGISTRY_OWNER: dict[str, str] = {}   # name -> the import that first defined it


def _load_checker_module(rel: str) -> tuple[dict, dict]:
    """Load one corpus-root-relative Python file; return its (CHECKERS, FIXERS).

    `CHECKERS` is required — a module named by `import::` that registers nothing
    is a corpus mistake worth saying out loud. `FIXERS` is optional: plenty of
    rulesets check without repairing, and requiring an empty dict would be
    ceremony.

    Loading THIS file is the common case (dans-anchor-system's own rulesets name
    it), and it is short-circuited to the live module: re-executing audit-plan
    from disk would duplicate 5,000 lines of definitions and hand back checker
    functions that are not the ones the rest of the process holds."""
    if rel in _IMPORTED:
        return _IMPORTED[rel]
    path = (REPO_ROOT / rel).resolve()
    if path == Path(__file__).resolve():
        _IMPORTED[rel] = (CHECKERS, FIXERS)
        return _IMPORTED[rel]
    if not path.is_file():
        raise CorpusError(f"import:: {rel!r} — no such file under {REPO_ROOT}")
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"_das_checkers_{abs(hash(rel))}", path)
    if spec is None or spec.loader is None:
        raise CorpusError(f"import:: {rel!r} — not loadable as a Python module")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        raise CorpusError(f"import:: {rel!r} — {type(e).__name__}: {e}") from e
    reg = getattr(mod, "CHECKERS", None)
    if not isinstance(reg, dict):
        raise CorpusError(f"import:: {rel!r} — module defines no CHECKERS dict")
    fixers = getattr(mod, "FIXERS", None)
    _IMPORTED[rel] = (reg, fixers if isinstance(fixers, dict) else {})
    return _IMPORTED[rel]


def register_imports(rulesets: list[dict]) -> None:
    """Load every module any of these rulesets names, merging into the registry.

    Idempotent and cheap on repeat — a batch run flattens once per umbrella and
    calls this on every return path, including the cached ones."""
    for rs in rulesets:
        for rel in rs.get("imports") or ():
            if rel in _IMPORTED:
                continue
            reg, fixers = _load_checker_module(rel)
            for src, dst in ((reg, registry()), (fixers, fixer_registry())):
                for name, fn in src.items():
                    if name in _REGISTRY_OWNER and _REGISTRY_OWNER[name] != rel:
                        continue  # first wins; verify_registrations reports the clash
                    _REGISTRY_OWNER.setdefault(name, rel)
                    dst[name] = fn


def fixer_registry() -> dict:
    """The merged fixer environment every `fix::` ref resolves against.

    Separate from `registry()` because the two vocabularies are separate: 127
    checkers and 7 fixers today, overlapping by name wherever a check and its
    repair share one (`md_table_pipe_escape`), and disjoint where they do not
    (`breadcrumb_position` is a fixer with no checker of that name)."""
    global _FIX_REGISTRY
    if _FIX_REGISTRY is None:
        _FIX_REGISTRY = dict(FIXERS)
        for n in FIXERS:
            _REGISTRY_OWNER.setdefault(n, "skills/audit/scripts/audit-plan.py")
    return _FIX_REGISTRY


def registry() -> dict:
    """The merged checker environment every `check::` ref resolves against.

    Seeded with this module's own `CHECKERS` because audit-plan is both the
    driver and dans-anchor-system's checker library — the two are the same file
    today, so its definitions are ambiently in scope no matter what any ruleset
    declares. That is why the declaration is VERIFIED rather than enforced
    (`verify_registrations`): splitting the checker library out of the driver is
    what would make the seam exclusive, and it is a separate change."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = dict(CHECKERS)
        for n in CHECKERS:
            _REGISTRY_OWNER.setdefault(n, "skills/audit/scripts/audit-plan.py")
    return _REGISTRY


def all_corpus_rulesets() -> list[dict]:
    """Every RULESET block in the corpus, reachable from an umbrella or not.

    The distinction is load-bearing and was not obvious: flattening `R-doc` +
    `R-anchor` reaches **24** rulesets, and the corpus holds far more. A ruleset
    outside that closure never runs, so a ghost ref inside it costs nothing
    today — but it is exactly the ref that will be wrong on the day something
    does include it, and it is what `import::` declarations exist to keep
    honest. `--verify-registry` checks the whole population; `plan_one` warns
    only about the closure, because that is what is executing for that plan."""
    out: list[dict] = []
    seen: set[str] = set()
    for p in sorted(REPO_ROOT.rglob("*.md")):
        if "/.git/" in str(p):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "RULESET " not in text:
            continue
        for ln in _code_masked_lines(text):
            m = _RULESET_RE.match(ln)
            if not m or m.group(2) in seen:
                continue
            blk = extract_ruleset_block(text, m.group(2))
            if blk is None:
                continue
            rs = parse_ruleset_block(blk[0], p)
            if rs["rules"]:
                seen.add(rs["name"])
                out.append(rs)
    return out


def inert_umbrellas(reachable: set[str], roots: tuple[str, ...]) -> list[str]:
    """Umbrellas that aggregate rulesets but are themselves outside the closure.

    T208. `audit-plan.py` resolves a FIXED umbrella — `R-doc` in doc mode,
    `R-anchor` in anchor mode — and nothing reads a per-anchor ruleset
    declaration, so an `include::` in any other umbrella arms nothing. `R-facet`
    spent its whole life documenting itself as the thing an anchor "adopts";
    three separate defects each began with an agent following that and
    concluding, reasonably, that a facet was covered. The tell is invisible from
    every surface that would normally show it: the recipe lists the rules, the
    tier reads `(checked)`, and the sweep runs green because no rule ran.

    The number that matters is not "is this umbrella reachable" — a pure catalog
    whose members are all armed elsewhere is harmless and should not nag. It is
    **how many rulesets this umbrella is the SOLE route to**, since those are
    armed by nothing at all. That count falls to zero as the sets get named in
    `R-doc`/`R-anchor`, so the report converges instead of becoming furniture.
    """
    out: list[str] = []
    seen: set[str] = set()
    warns: list[str] = []
    for p in sorted(REPO_ROOT.rglob("*.md")):
        if "/.git/" in str(p):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "RULESET " not in text:
            continue
        for ln in _code_masked_lines(text):
            m = _RULESET_RE.match(ln)
            if not m or m.group(2) in seen:
                continue
            name = m.group(2)
            seen.add(name)
            if name in roots or name in reachable:
                continue
            blk = extract_ruleset_block(text, name)
            if blk is None:
                continue
            rs = parse_ruleset_block(blk[0], p)
            if not rs["includes"]:
                continue
            members = {r["name"] for r in flatten_umbrella(name, warns)}
            orphaned = sorted(members - reachable)
            if not members:
                out.append(f"{name} — outside the closure, and its include:: reaches "
                           f"nothing that carries rules; an empty umbrella")
                continue
            if not orphaned:
                out.append(f"{name} — outside the closure, but every one of its "
                           f"{len(members)} rulesets is armed by another route; "
                           f"a catalog, costing nothing")
                continue
            out.append(f"{name} — outside the closure and the SOLE route to "
                       f"{len(orphaned)} ruleset(s), which are therefore armed by "
                       f"nothing: {', '.join(orphaned)}")
    return out


def verify_registrations(rulesets: list[dict]) -> dict:
    """Check the `check::`↔registry mapping in both directions.

    Neither direction is checked today and both were found broken (F289): 11
    refs named a checker nothing registers, and 23 registered checkers were
    invoked by no rule. The ghost direction is the expensive one and it fails
    QUIETLY BY DESIGN — `_needs_judgment` decides mechanical-vs-agent with a
    membership test, so a name that is not there misses, the rule is promoted to
    agent judgment, and `run_checker`'s `unknown checker` error never runs
    because the rule never reaches it. One typo turns a free deterministic check
    into a billed non-deterministic one that reports nothing.

    Returns {ghosts, undeclared, clashes, orphans}. `ghosts` is the corpus
    error; `undeclared` and `clashes` are warnings; `orphans` wants a human —
    an uninvoked checker is either a rule waiting to be written or dead code,
    and only reading each one tells you which."""
    register_imports(rulesets)
    # Each field resolves against its OWN registry — see the note on `_IMPORTED`.
    REG = {"check": registry(), "fix": fixer_registry()}
    ghosts, undeclared, clashes = [], [], []
    used: set[str] = set()

    seen_owner: dict[str, str] = {}
    for rs in rulesets:
        own: dict[str, set] = {"check": set(), "fix": set()}
        for rel in rs.get("imports") or ():
            checkers, fixers = _IMPORTED.get(rel) or ({}, {})
            for n in set(checkers) | set(fixers):
                if n in seen_owner and seen_owner[n] != rel:
                    clashes.append(f"{n!r} defined by both "
                                   f"{seen_owner[n]} and {rel} — first wins")
                seen_owner.setdefault(n, rel)
            own["check"] |= set(checkers)
            own["fix"] |= set(fixers)
        for r in rs["rules"]:
            for field in ("check", "fix"):
                ref = r.get(field)
                if not ref:
                    continue
                name = ref.split()[0]
                if field == "check":
                    used.add(name)
                if name not in REG[field]:
                    ghosts.append(f"{r['id']} — {field}:: {name!r} is registered nowhere; "
                                  f"the rule silently becomes agent judgment")
                elif name not in own[field]:
                    undeclared.append(f"{r['id']} — {field}:: {name!r} resolves only "
                                      f"globally; {rs['name']} declares no import:: "
                                      f"that defines it")
    orphans = sorted(n for n in REG["check"] if n not in used)
    return {"ghosts": ghosts, "undeclared": undeclared,
            "clashes": clashes, "orphans": orphans}


# ── flattened-umbrella cache (shared across all anchors in a batch / re-audit) ─
#
# flatten_umbrella() does a repo-wide rglob + parse to resolve the include:: DAG.
# That work is identical for every anchor in a batch and stable across re-audits
# until a rule source file changes. Cache it twice: an in-process memo (one batch
# run touches many anchors) and a disk cache keyed by a signature over every md
# file's (relpath, mtime, size) — any rule edit bumps an mtime and invalidates it.

_FLATTEN_MEM: dict[str, tuple[list[dict], list[str]]] = {}


def _rule_corpus_sig() -> str:
    h = hashlib.sha256()
    for p in sorted(REPO_ROOT.rglob("*.md")):
        if "/.git/" in str(p):
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        h.update(str(p.relative_to(REPO_ROOT)).encode())
        h.update(f"|{st.st_mtime_ns}|{st.st_size}".encode())
    return h.hexdigest()[:16]


def flatten_umbrella_cached(umbrella: str, cdir: Path | None, warnings: list[str],
                            stats: dict | None = None) -> list[dict]:
    def bump(k):
        if stats is not None:
            stats[k] = stats.get(k, 0) + 1

    # Both cache hits below bypass flatten_umbrella, so each re-registers: the
    # rulesets round-trip through JSON with their `imports` intact, but the
    # loaded modules do not survive a new process.
    if umbrella in _FLATTEN_MEM:
        rs, warns = _FLATTEN_MEM[umbrella]
        warnings.extend(warns)
        register_imports(rs)
        bump("flatten_mem_hit")
        return rs

    if cdir is None:
        rs = flatten_umbrella(umbrella, warnings)
        _FLATTEN_MEM[umbrella] = (rs, [])
        bump("flatten_miss")
        return rs

    sig = _rule_corpus_sig()
    fp = cdir / "umbrella" / f"{umbrella}-{sig}.json"
    if fp.is_file():
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            rs, warns = data["rulesets"], data.get("warnings", [])
            _FLATTEN_MEM[umbrella] = (rs, warns)
            warnings.extend(warns)
            register_imports(rs)
            bump("flatten_disk_hit")
            return rs
        except (OSError, json.JSONDecodeError):
            pass

    local: list[str] = []
    rs = flatten_umbrella(umbrella, local)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps({"umbrella": umbrella, "rulesets": rs, "warnings": local}),
                  encoding="utf-8")
    _FLATTEN_MEM[umbrella] = (rs, local)
    warnings.extend(local)
    bump("flatten_miss")
    return rs


# ── selector resolution ─────────────────────────────────────────────────────

def effective_where(rule: dict, ruleset: dict) -> str:
    """Precedence: rule.where > ruleset.where > 'always'."""
    return rule.get("where") or ruleset.get("where") or "always"


def effective_confirm(rule: dict, ruleset: dict) -> str | None:
    """Precedence: rule.confirm > ruleset.confirm > None. Same shape as
    `effective_where`, because the question it answers is the same kind: a
    property a ruleset sets for all its rules and any one rule may override."""
    return rule.get("confirm") or ruleset.get("confirm") or None


# A trailing `, !mirror` on ANY selector kind, and the bare kind `mirror`.
_MIRROR_SUFFIX_RE = re.compile(r",\s*!mirror\s*$")


def parse_selector(where: str) -> tuple[str, str, str | None]:
    """(kind, arg, mirror). kind ∈ always|file|anchor|sentinel|group|mirror.
    Bare glob → ('file', glob, None). `mirror` ∈ None | 'only' | 'exclude'.

    F600. Mirror-ness is a MODIFIER on the line, not a word in the glob
    vocabulary, and the positive rule is what settles that. `!`-negation is
    implemented in exactly one of the five kinds — inside `_match_file_glob` —
    so only a `file:` glob can exclude anything, and `R-spine` says `always`,
    which cannot exclude at all. Making `mirror` a glob term would have forced
    `R-spine` to restate its scope as a path pattern, and worse, would have left
    the positive direction with no honest spelling: `R-spine-11` must SELECT
    mirrored docs, and `file:mirror` is a lie about what the term is.

    As a suffix it reads the same in both directions and composes with every
    kind: `where:: always, !mirror` excludes them, `where:: mirror` selects
    them, and `group:` / `sentinel:` inherit the modifier for free.

    A spine is a vault convention — a `:>>` breadcrumb and a dispatch masthead
    built from wiki-links and `hook://` URIs — and both render as literal noise
    on GitHub. Dan, 2026-08-28: *"the rule should be mirrored docs cannot have a
    spine, because it just doesn't mean anything in the receiver's
    environment."*
    """
    w = where.strip()
    mirror = None
    if _MIRROR_SUFFIX_RE.search(w):
        mirror = "exclude"
        w = _MIRROR_SUFFIX_RE.sub("", w).strip()
    if w == "mirror":
        return "mirror", "", "only"
    if w == "always":
        return "always", "", mirror
    if w == "anchor":
        return "anchor", "", mirror
    if w.startswith("file:"):
        return "file", w[len("file:"):].strip(), mirror
    if w.startswith("sentinel:"):
        return "sentinel", w[len("sentinel:"):].strip(), mirror
    if w.startswith("group:"):
        return "group", w[len("group:"):].strip(), mirror
    return "file", w, mirror  # bare glob


def _glob_to_relpattern(glob: str) -> str:
    g = glob.strip()
    if g.startswith("{anchor}/"):
        g = g[len("{anchor}/"):]
    elif g == "{anchor}":
        g = ""
    return g


def _anchor_name(anchor_root: Path) -> str:
    """{slug} token → the anchor's slug (from .anchor), else its folder name."""
    dot = anchor_root / ".anchor"
    if dot.is_file():
        try:
            for line in dot.read_text(encoding="utf-8").splitlines():
                m = re.match(r"\s*(?:slug|name)\s*:\s*(.+?)\s*$", line)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
        except OSError:
            pass
    return anchor_root.name


def _expand_braces(pat: str) -> list[str]:
    """Expand glob brace-alternation {a,b,c} (cartesian over groups). Predefined
    {ALL-CAPS} tokens must already be substituted out before this runs."""
    m = re.search(r"\{([^{}]*,[^{}]*)\}", pat)
    if not m:
        return [pat]
    pre, post = pat[:m.start()], pat[m.end():]
    out = []
    for alt in m.group(1).split(","):
        out.extend(_expand_braces(pre + alt.strip() + post))
    return out


def _split_terms(glob: str) -> list[str]:
    """Split a where:: file value on TOP-LEVEL commas. Commas inside {} are
    brace-alternation, not list separators."""
    terms, depth, cur = [], 0, ""
    for ch in glob:
        if ch == "{":
            depth += 1; cur += ch
        elif ch == "}":
            depth = max(0, depth - 1); cur += ch
        elif ch == "," and depth == 0:
            terms.append(cur); cur = ""
        else:
            cur += ch
    terms.append(cur)
    return [t.strip() for t in terms if t.strip()]


@lru_cache(maxsize=4096)
def _glob_rx(pat: str):
    """Compile one (brace-expanded) relative glob to a regex with pathlib.glob
    semantics: `**/` spans zero-or-more directories, `*`/`?` stay within one
    segment. Matching scope files against this — instead of walking the anchor
    tree per rule via `Path.glob` — keeps the on-write doc-fire O(scope)
    rather than O(anchor tree) (F232 B3: 54 file-selector rules × a full tree
    walk was ~390 ms per markdown write)."""
    out = []
    i = 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("**", i):
            out.append(".*")
            i += 2
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _match_file_glob(arg: str, scope_files: list[Path], anchor_root: Path) -> list[Path]:
    """Resolve a `file:` where-glob to scope files, honoring the full spec
    ([[DAS Ruleset]] § Where clause): {anchor}/{slug} tokens, brace-alternation,
    comma-union, and gitignore-style !-negation. Matches patterns against the
    scope files' anchor-relative paths — no filesystem walk (F232 B3)."""
    name = _anchor_name(anchor_root)
    root = anchor_root.resolve()
    # T164 — a facet that materializes as a FOLDER carries its own `.anchor`, so
    # `sub_anchor_roots` drops it from the parent's scope and it is only ever audited
    # scoped on itself. But its selector is authored from the parent's point of view
    # (`{anchor}/**/* Rocks/**`), which is then unsatisfiable from BOTH ends: out of
    # scope from the parent, and from the folder itself `{anchor}` IS the Rocks folder,
    # so the pattern demands a nested `* Rocks/` inside itself. Every rule read
    # `(checked)` and fired on nothing. So each file also gets a candidate path
    # prefixed with the anchor's own directory name, which is exactly the path the
    # selector was written against. File-shaped facets are unaffected — their primary
    # relative path already matched, and this only ever adds candidates.
    own = anchor_root.name
    rel_of: dict = {}
    for p in scope_files:
        if p == anchor_root or p.resolve() == root:
            rel_of[p] = ""          # the anchor itself (anchor-mode synthetic)
            continue
        try:                        # literal path first (symlink-tolerant)
            rel_of[p] = p.relative_to(anchor_root).as_posix()
            continue
        except ValueError:
            pass
        try:
            rel_of[p] = p.resolve().relative_to(root).as_posix()
        except ValueError:
            rel_of[p] = None        # outside the anchor — matches nothing
    include: set[Path] = set()
    exclude: set[Path] = set()
    for term in _split_terms(arg):
        neg = term.startswith("!")
        if neg:
            term = term[1:].strip()
        rel = _glob_to_relpattern(term).replace("{slug}", name)
        if not rel:
            paths = {p for p, r in rel_of.items() if r == ""}
        else:
            rxs = [_glob_rx(pat) for pat in _expand_braces(rel)]
            paths = {p for p, r in rel_of.items()
                     if r and any(rx.match(c) for rx in rxs
                                  for c in (r, f"{own}/{r}"))}
        (exclude if neg else include).update(paths)
    hits = include - exclude
    return [p for p in scope_files if p in hits]


# ── `group:` selector (T197) — a document declares what it is ────────────────
#
# The facet-group vocabulary is [[DAS Facet]] § Facet groups: a spec attaches to
# a `file`, a `folder`, a `slot`, or to nothing of its own (`discipline`). That
# page also settles WHERE the answer lives — *"the group is declared in the spec,
# never encoded in which folder the spec lives in"* — because a facet can change
# groups (Brief is a slot inline and a file as a sidecar) and a folder forces one
# answer permanently.
#
# This selector is what finally READS that declaration. Before it, `R-facet-spec`
# reached its target set by SUBTRACTION: a `DAS *.md` glob minus a hand-listed
# complement that had grown to 48 clauses, every one appended by an agent after a
# finding fired on a document the list had not yet heard of. A new discipline was
# born failing the facet rules and the fix was always to grow the negative.
#
# The declaration is a frontmatter key, not a body `group::` field, for two
# reasons: frontmatter is the metadata surface these specs already carry (the
# `status::` dataview field is likewise specified as living there), and a body
# line inside a spec is one dispatch-table rebuild away from being an electric
# zone. Multiple groups are comma-separable — a spec whose realization genuinely
# spans two (`DAS Template`, whose instances are files AND folders) says so
# rather than picking a lie.
_GROUP_KEY_RE = re.compile(r"^group\s*:\s*(.+?)\s*$", re.M)
GROUP_VALUES = ("file", "folder", "slot", "discipline")


def declared_groups(path: Path) -> set[str]:
    """The facet groups a spec doc declares in frontmatter — empty if none.

    Empty is the honest answer for every document that is not a spec (an index,
    a gallery, a group profile), which is what keeps the selector positive.
    """
    try:
        fm = _frontmatter(_read(path))
    except OSError:
        return set()
    if not fm:
        return set()
    m = _GROUP_KEY_RE.search(fm)
    if not m:
        return set()
    raw = m.group(1).strip().strip("[]")
    return {v.strip().strip("\"'").lower() for v in raw.split(",") if v.strip()}


def match_targets(kind: str, arg: str, scope_files: list[Path], anchor_root: Path,
                  mirror: str | None = None) -> list[Path]:
    """Files in scope this selector governs. `mirror` post-filters the result:
    'exclude' drops docs inside a declared mirror route, 'only' keeps just them
    (F600). The filter runs LAST, after the kind has chosen, so it composes with
    every kind rather than being re-implemented inside each."""
    out = _match_targets_kind(kind, arg, scope_files, anchor_root)
    if mirror is None and kind != "mirror":
        return out
    try:
        # `_spine_sibling`, not a bare import: it is the one loader that finds
        # these modules however audit-plan was entered (script, or imported by
        # warden_docfire), and it is what keeps the audit and the `spine` CLI
        # from drifting into two notions of what a mirror route is.
        spine = _spine_sibling("spine")
        roots = spine.mirror_roots()
    except Exception:
        # An unreadable route index yields no exemptions: fail toward MORE
        # checking, never less -- the same direction `spine.mirror_roots` takes.
        return out if mirror != "only" else []
    if mirror == "only" or kind == "mirror":
        return [p for p in out if p.is_file() and spine.in_mirror_route(p, roots)]
    return [p for p in out if not (p.is_file() and spine.in_mirror_route(p, roots))]


def _match_targets_kind(kind: str, arg: str, scope_files: list[Path],
                        anchor_root: Path) -> list[Path]:
    if kind in ("always", "mirror"):
        return list(scope_files)
    if kind == "group":
        want = {g.strip().lower() for g in arg.split(",") if g.strip()}
        out = []
        for p in scope_files:
            if not p.is_file():
                continue
            got = declared_groups(p)
            # A typo is the one failure this selector cannot survive quietly:
            # `group: File` or `group: files` declares nothing the selector
            # knows, so the spec drops out of the target set and every rule
            # that governed it reports nothing — a silent green, which is the
            # worse half of the over/under-inclusion trade. Refuse to let an
            # unknown value pass as if it were a considered choice.
            bad = got - set(GROUP_VALUES)
            if bad:
                raise ValueError(
                    f"{p}: frontmatter `group:` names {sorted(bad)}, which is not "
                    f"one of {list(GROUP_VALUES)} — see [[DAS Facet]] § Facet groups")
            if got & want:
                out.append(p)
        return out
    if kind == "anchor":
        return [anchor_root]  # synthetic: one structural check per anchor
    if kind == "file":
        return _match_file_glob(arg, scope_files, anchor_root)
    if kind == "sentinel":
        try:
            rx = re.compile(arg, re.MULTILINE)
        except re.error:
            return []
        out = []
        for p in scope_files:
            # `is_file()` first: the vault contains directories whose name ends
            # `.md` (`SV/ww/2025 bzz.md`), and reading one raises IsADirectoryError
            # here at PLAN time — outside `run_checker`'s per-checker guard, so it
            # takes the whole run down rather than one verdict (T098).
            if not p.is_file():
                continue
            try:
                if rx.search(_read(p)):
                    out.append(p)
            except OSError:
                pass
        return out
    return []


# ── target enumeration ──────────────────────────────────────────────────────

def sub_anchor_roots(target: Path) -> set[Path]:
    """Nested anchor roots strictly inside target (target's own .anchor excluded).
    A file is owned by its *deepest* enclosing anchor; target's scope drops any
    file under a nested sub-anchor so it isn't double-audited (the sub-anchor's
    own plan covers it). Applied uniformly — a single audit is a batch-of-one."""
    t = target.resolve()
    roots = set()
    for dot in target.rglob(".anchor"):
        if _under_dot_dir(dot, target):
            continue  # T100 — a `.anchor` inside `.trash` is not a live sub-anchor
        if _is_folder_doc_marker(dot):
            continue  # F329 — scanner-minted marker beside a folder-form backlog
        parent = dot.parent.resolve()
        if parent != t:
            roots.add(parent)
    return roots


def _is_state_backlog_namesake(f: Path) -> bool:
    """True when `f` IS a folder-form backlog's namesake page — `X/X.md`
    carrying the machine `<!-- state:backlog -->` stamp (F329).

    The sibling of `_is_folder_doc_marker`, which asks the same question from
    the `.anchor` side. Both read the stamp rather than the folder shape,
    because the stamp is written by `state` and cannot be acquired by accident.
    """
    if f.parent.name != f.stem:
        return False
    try:
        head = f.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return False
    return re.search(r"<!--\s*state:backlog\b", head) is not None


def _is_notebook_namesake(f: Path) -> bool:
    """True when `f` IS a notebook's narrative page — `X/X.md` carrying the
    machine `<!-- notebook -->` marker (F334).

    The third member of the family with `_is_state_backlog_namesake` and
    `_is_folder_doc_marker`, and keyed the same way and for the same reason:
    on a marker a script writes, never on the folder's shape or its name. The
    folder shape is what a page LOOKS like; the marker is what a tool DECLARED,
    and only the second cannot be acquired by accident.
    """
    if f.parent.name != f.stem:
        return False
    try:
        head = f.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return False
    return re.search(r"<!--\s*notebook\b", head) is not None


def _is_folder_doc_marker(dot: Path) -> bool:
    """True when this `.anchor` sits beside a folder-form backlog namesake
    (F329) — a `<!-- state:backlog -->`-stamped `X/X.md`. HookAnchor's scanner
    auto-mints `.anchor` in every namesake folder on its 10-minute rescan, so
    the marker's mere presence cannot demote the queue folder to a sub-anchor:
    that would eject the anchor's own backlog (and its T-docs) from every
    anchor-scoped audit — the T232 failure, self-inflicted. Same discriminator
    `_anchorness` uses: the namesake's own machine stamp outranks the marker."""
    namesake = dot.parent / f"{dot.parent.name}.md"
    if not namesake.is_file():
        return False
    try:
        head = namesake.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return False
    return re.search(r"<!--\s*state:backlog\b", head) is not None


def _under_dot_dir(p: Path, root: Path) -> bool:
    """True when any directory between `root` and `p` is dot-prefixed.

    T100. This replaces a hardcoded `"/.git/" in str(p)` — one name, chosen because
    it was the one that hurt first. The vault-wide batch ([[T098]]) exposed the rest:
    of 376,166 planned rule-target pairs, **4,377 sat under a dot-directory** —
    `.trash` (3,579 pairs), `.anchor.d`, `.pytest_cache`, `.trash-hud` — so the audit
    reported findings against documents the user had DELETED, and fix-by-default
    would have cheerfully repaired them.

    `.anchor.d` was the one the row flagged as needing a decision rather than a rule,
    since it is anchor metadata rather than junk. The contents settle it: 222 of its
    238 files are `.json` machine state, 3 are `.yaml` config, and the 13 `.md` are
    machine-written stat log entries (`stat/A03241200.md`) — no authored document
    among them, so nothing there wants a doc-structure verdict. A dot-prefix rule is
    right, and no named exception list is needed.

    Measured RELATIVE to the walk root, not absolutely: auditing a target that itself
    lives under a dot-directory (`~/.claude/skills/...` is a real case) must still
    enumerate its own files. Only dot-directories the walk DESCENDS INTO are skipped.
    """
    try:
        rel = p.relative_to(root)
    except ValueError:
        return False
    return any(part.startswith(".") for part in rel.parts[:-1])


def enumerate_scope(target: Path, mode: str,
                    exclude_roots: set[Path] | None = None) -> tuple[Path, list[Path]]:
    """Return (anchor_root, scope_files). For doc mode the scope is the one file.
    Files under any path in exclude_roots (nested sub-anchors) are dropped."""
    if mode == "doc":
        # Anchor-relative matching (T018, 2026-07-14): resolve the file's real
        # anchor root (walk-up to .anchor) so on-write doc-fires share the same
        # `where::` semantics as anchor-mode audits — dir-scoped globs and the
        # {slug} token match identically on both paths. Parent-dir fallback
        # keeps out-of-anchor files matchable by basename, as before.
        for cand in (target.parent, *target.parent.parents):
            if (cand / ".anchor").is_file():
                return cand, [target]
        return target.parent, [target]
    exclude_roots = exclude_roots or set()
    files = []
    for p in target.rglob("*.md"):
        if _under_dot_dir(p, target):
            continue
        if any(r == p.parent or r in p.parents for r in exclude_roots):
            continue
        files.append(p)
    return target, files


# ── flattened-rules cache ───────────────────────────────────────────────────

_CACHE_BASE = HOME / ".cache"
_CACHE_DEFAULT = _CACHE_BASE / "dans-anchor-system-audit"


def cache_dir(opt: str | None) -> Path:
    """Resolve the cache root — never against the process cwd.

    T608. `~/ob/kmr/umbrella/R-anchor-450377da353065e3.json` was found sitting
    at the VAULT ROOT and git-tracked, so the hourly sweep had committed a
    regenerable cache into the commons. The default here was always absolute;
    the escape is a RELATIVE `--cache-dir`, which `Path(opt).expanduser()`
    leaves relative, so `cdir / "umbrella"` landed wherever the run happened to
    start. That is why the file's directory was literally named `umbrella` and
    its first key was the umbrella's own name — the path was assembled correctly
    and rooted nowhere.

    Two changes, because either alone leaves the hole open:

    - A relative option resolves against `~/.cache/`, a stable base, so the same
      invocation from two directories writes to one place instead of two.
    - A cache dir inside a git working tree is REFUSED outright. That is the
      actual damage — not that the cache existed, but that it was committed —
      and it is the half that would still bite someone who passed an absolute
      path into a repo. Refused rather than relocated: a silent move would leave
      the caller believing a directory it named is in use.

    Deleting the stray file without fixing this was the worst of the available
    outcomes, and it is what happened: re-measured 2026-08-28, the file and its
    directory are gone, so the next escape lands somewhere less obvious.
    """
    if opt:
        d = Path(opt).expanduser()
        if not d.is_absolute():
            d = _CACHE_BASE / d
    else:
        d = _CACHE_DEFAULT
    for a in (d, *d.parents):
        if (a / ".git").exists():
            raise SystemExit(
                f"audit-plan: refusing a cache dir inside a git working tree — {d}\n"
                f"  (tracked at {a})\n"
                f"  A regenerable cache committed into a repo is what T608 found at the\n"
                f"  vault root. Pass an absolute --cache-dir outside any repo, or omit it\n"
                f"  to use {_CACHE_DEFAULT}.")
    (d / "flat").mkdir(parents=True, exist_ok=True)
    return d


def ruleset_hash(rs: dict) -> str:
    h = hashlib.sha256()
    for r in rs["rules"]:
        h.update(f"{r['id']}|{r['tier']}|{r['title']}|{r.get('check_pattern')}".encode())
    return h.hexdigest()[:12]


def write_flat_file(rs: dict, cdir: Path) -> Path:
    digest = ruleset_hash(rs)
    fp = cdir / "flat" / f"{rs['name']}-{digest}.md"
    if not fp.exists():
        lines = [f"# {rs['name']} (flattened)", ""]
        if rs.get("description"):
            lines += [f"_{rs['description']}_", ""]
        for r in rs["rules"]:
            lines.append(f"## {r['id']} — {r['title']} ({r['tier']})")
            if r.get("check_pattern"):
                lines.append(f"**Check pattern:** {r['check_pattern']}")
            if r.get("why"):
                lines.append(f"**Why:** {r['why']}")
            lines.append("")
        fp.write_text("\n".join(lines), encoding="utf-8")
    return fp


# ── planning ────────────────────────────────────────────────────────────────

def _plan_tree_hash(anchor_root: Path, scope_files: list[Path]) -> str:
    """Content+structure hash of the audited tree — relpath + bytes of every scope
    file (+ the .anchor). Any edit / add / remove invalidates the cached plan."""
    h = hashlib.sha256()
    dot = anchor_root / ".anchor"
    if dot.is_file():
        try:
            h.update(b"A")
            h.update(dot.read_bytes())
        except OSError:
            pass
    for p in sorted(scope_files):
        try:
            h.update(b"F")
            h.update(str(p.relative_to(anchor_root)).encode())
            h.update(b"C")
            h.update(p.read_bytes())
        except (OSError, ValueError):
            pass
    return h.hexdigest()[:16]


def _plan_rules_hash(rulesets: list[dict]) -> str:
    """Hash of the plan-relevant rule fields (selector + tier + checker), so a
    `where::`/`check::`/tier edit invalidates the plan even if titles are stable."""
    h = hashlib.sha256()
    for rs in rulesets:
        h.update(f"RS|{rs['name']}|{rs.get('where')}".encode())
        for r in rs["rules"]:
            h.update(f"R|{r['id']}|{r['tier']}|{r.get('where')}|{r.get('check')}|{r.get('fix')}".encode())
    return h.hexdigest()[:12]


def plan_one(target: Path, mode: str, cdir: Path | None, warnings: list[str],
             exclude_roots: set[Path] | None = None, stats: dict | None = None) -> dict:
    umbrella = "R-doc" if mode == "doc" else "R-anchor"
    rulesets = flatten_umbrella_cached(umbrella, cdir, warnings, stats)
    # One line, not one per ref: a ghost ref is a corpus fault, not a finding
    # about this target, and it must not scale with how many documents were
    # audited. `--verify-registry` prints the full report.
    ghosts = verify_registrations(rulesets)["ghosts"]
    if ghosts:
        warnings.append(
            f"{len(ghosts)} check::/fix:: ref(s) resolve to no registered checker — "
            f"those rules are silently agent-judgment; run "
            f"`audit-plan.py --verify-registry` for the list")
    anchor_root, scope_files = enumerate_scope(target, mode, exclude_roots)

    # Whole-plan (anchor-manifest) cache — skip selector resolution when the tree
    # and the rules are both unchanged. Keyed by (abs anchor + mode + tree + rules).
    plan_fp = None
    if cdir is not None:
        key = hashlib.sha256(
            f"{anchor_root.resolve()}|{mode}|"
            f"{_plan_tree_hash(anchor_root, scope_files)}|{_plan_rules_hash(rulesets)}".encode()
        ).hexdigest()[:20]
        plan_fp = cdir / "plans" / f"{key}.json"
        if plan_fp.is_file():
            try:
                plan = json.loads(plan_fp.read_text(encoding="utf-8"))
                plan["warnings"] = warnings
                if stats is not None:
                    stats["plan_hit"] = stats.get("plan_hit", 0) + 1
                return plan
            except (OSError, json.JSONDecodeError):
                pass

    groupings = []
    for rs in rulesets:
        flat = str(write_flat_file(rs, cdir).relative_to(cdir)) if cdir else None
        matched_rules = []
        for r in rs["rules"]:
            kind, arg, mir = parse_selector(effective_where(r, rs))
            if mode == "doc" and kind == "anchor":
                continue  # anchor-structure rules are N/A at the doc level
            tgts = match_targets(kind, arg, scope_files, anchor_root, mir)
            # A facet spec is the SOURCE of its embedded ruleset, never an instance
            # of it — e.g. DAS Decisions.md (spec of R-decisions) matches the
            # `* Decisions.md` selector but must not be audited as a Decisions
            # instance. Drop a ruleset's own source file from its rule targets.
            #
            # NAME-matched only (T212, 2026-08-11). The case above is a *glob*
            # catching the spec by filename — `DAS Decisions.md` looks like a
            # Decisions doc and is not one. A `sentinel:` selector matches by
            # CONTENT, and content does not lie about kind: a file carrying
            # `# RULESET R-` is a ruleset whichever ruleset it is. Applying the
            # exclusion there silently exempted `R-ruleset.md` from `R-ruleset`
            # — the one set whose subject is the file kind it is itself written
            # as, and whose header claims in so many words *"Self-applying:
            # this set obeys its own rules."* It was not, and had never been.
            # Measured before the narrowing: of the four sentinel-scoped sets
            # (R-brief, R-discussion, R-ruleset, R-stream) only R-ruleset
            # matches its own sentinel, and it passes all six of its mechanical
            # rules — so this closes the hole without moving a verdict.
            if tgts and rs.get("source") and kind != "sentinel":
                src_abs = (REPO_ROOT / rs["source"]).resolve()
                tgts = [t for t in tgts if t.resolve() != src_abs]
            if not tgts:
                continue  # selector miss → N/A
            matched_rules.append({
                "id": r["id"], "tier": r["tier"], "title": r["title"],
                "selector": effective_where(r, rs), "check": r.get("check"),
                "fix": r.get("fix"),
                "check_pattern": r.get("check_pattern"), "why": r.get("why"),
                "targets": [str(p.relative_to(anchor_root)) if p != anchor_root else "{anchor}"
                            for p in tgts],
                "_target_paths": [str(p) for p in tgts],
            })
        if matched_rules:
            groupings.append({"ruleset": rs["name"], "flat_file": flat,
                              "source": rs["source"], "rules": matched_rules})

    plan = {
        "umbrella": umbrella, "mode": mode,
        "target": str(target), "anchor_root": str(anchor_root),
        "scope_file_count": len(scope_files),
        "excluded_subanchors": sorted(str(r) for r in (exclude_roots or set())),
        "groupings": groupings, "warnings": warnings,
    }
    if plan_fp is not None:
        try:
            plan_fp.parent.mkdir(parents=True, exist_ok=True)
            plan_fp.write_text(json.dumps(plan), encoding="utf-8")
            if stats is not None:
                stats["plan_miss"] = stats.get("plan_miss", 0) + 1
        except OSError:
            pass
    return plan


# ── rendering ───────────────────────────────────────────────────────────────

def render_recipe(plan: dict, order: str, cdir: Path | None) -> str:
    out = []
    out.append(f"# audit-plan recipe — {plan['umbrella']} on {Path(plan['target']).name}")
    out.append("")
    out.append(f"- mode: **{plan['mode']}**  ·  order: **{order}-major**  ·  "
               f"scope files: {plan['scope_file_count']}  ·  "
               f"rulesets matched: {len(plan['groupings'])}")
    if plan.get("excluded_subanchors"):
        out.append(f"- excluded {len(plan['excluded_subanchors'])} nested sub-anchor(s): "
                   + ", ".join(Path(r).name for r in plan["excluded_subanchors"]))
    if cdir:
        out.append(f"- flat-rule cache: `{cdir / 'flat'}`")
    out.append("")

    def tier_tag(t):
        return "judge (mechanical — checker pending)" if t == "checked" else f"judge ({t})"

    def fmt_targets(r):
        if r["selector"].strip() == "always":
            return f"(all {len(r['targets'])} scope files)"
        return ", ".join(r["targets"])

    if order == "rule":
        out.append("Load one flat rule file at a time; judge its listed targets.\n")
        for g in plan["groupings"]:
            out.append(f"## {g['ruleset']}  — flat: `{g['flat_file']}`  (src: {g['source']})")
            for r in g["rules"]:
                out.append(f"- **{r['id']}** [{tier_tag(r['tier'])}] — {r['title']}")
                out.append(f"    - selector `{r['selector']}` → {fmt_targets(r)}")
            out.append("")
    else:  # file-major
        by_file: dict[str, list[tuple[str, dict]]] = {}
        for g in plan["groupings"]:
            for r in g["rules"]:
                for t in r["targets"]:
                    by_file.setdefault(t, []).append((g["ruleset"], r))
        out.append("Walk each target; run its matched rules.\n")
        for f in sorted(by_file):
            out.append(f"## {f}")
            for rsname, r in by_file[f]:
                out.append(f"- **{r['id']}** [{tier_tag(r['tier'])}] — {r['title']}  ({rsname})")
            out.append("")

    if plan["warnings"]:
        out.append("## warnings")
        for w in plan["warnings"]:
            out.append(f"- {w}")
    return "\n".join(out)


# ── Stage 2: checker primitives + verdict-cached executor (F161) ─────────────
#
# Each `checked`/`sampled` rule may carry a machine-readable `check::` ref naming
# one of these primitives (the prose **Check pattern:** stays the human spec).
# A primitive takes (target_path, anchor_root, args) and returns (status, detail)
# where status ∈ {pass, fail, error}. For `anchor`-scope rules the target is the
# anchor root dir; helpers resolve the entry page from it.

def _read(path: Path) -> str:
    """Decode a doc, replacing bytes that are not UTF-8 rather than raising.

    T098. `UnicodeDecodeError` is a `ValueError`, not an `OSError`, so it slipped
    past every `except OSError` guard in this file and aborted the whole run at
    the FIRST bad byte — `--batch ~/ob/kmr` died on one 0xbb in one doc and audited
    nothing. That is why the audit has had no vault-wide harness, and why the
    F296 measurements had to be hand-scoped (and were published wrong twice).

    Replacement is the right call for a STRUCTURAL audit rather than a fallback
    that hides a fault: an undecodable byte becomes U+FFFD, which is not a `#`, a
    backtick or a pipe, so every heading/fence/table judgement is unchanged. What
    would be a fallback is swallowing a missing or unreadable file — so OSError is
    still allowed to propagate, and callers that ENUMERATE files skip non-files
    before getting here."""
    return path.read_text(encoding="utf-8", errors="replace")


def _anchor_slug(anchor_root: Path) -> str:
    dot = anchor_root / ".anchor"
    if dot.is_file():
        m = re.search(r"^slug:\s*(\S+)", _read(dot), re.MULTILINE)
        if m:
            return m.group(1).strip().strip('"\'')
    return anchor_root.name


def _entry_page(anchor_root: Path) -> Path | None:
    cand = anchor_root / f"{_anchor_slug(anchor_root)}.md"
    if cand.is_file():
        return cand
    cand = anchor_root / f"{anchor_root.name}.md"
    return cand if cand.is_file() else None


def _as_file(target: Path, anchor_root: Path) -> Path | None:
    return _entry_page(anchor_root) if target.is_dir() else target


def _frontmatter(text: str) -> str | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else None


# An ATX H1 per CommonMark: up to THREE leading spaces (four makes it an indented
# code block), then `#`, then AT LEAST ONE space or tab, then content. The three
# spellings this replaced — `^# \S`, `^# `, `.startswith("# ")` — each demanded
# column zero and exactly one space, and the single-space half is the one that bit
# hardest: `SYS/Atlas/Atlas.md` opens `#  Atlas  — glossary …` with TWO spaces, so
# every `^# \S` site walked past the real head and blamed the file's `# BRIEF` at
# line 374. That is T092's damage signature exactly, and T092 read it as an
# indentation problem — the `^ {0,3}` relaxation it shipped does not fix Atlas.md
# and never did. The trailing group strips an ATX closing sequence (`# Title #`),
# which is not part of the heading content and which `ln[2:].strip()` used to keep.
_H1_RE = re.compile(r"^ {0,3}#[ \t]+(\S.*?)(?:[ \t]+#+)?[ \t]*$")
_H2_RE = re.compile(r"^ {0,3}##[ \t]+(\S.*?)(?:[ \t]+#+)?[ \t]*$")
# Any ATX heading, level unconstrained — the "something already started" test
# `_head_h1` uses to decide a document has no head. Looser than `_H1_RE`/`_H2_RE`
# on purpose: it must not require a non-blank title, because a bare `##` divider
# still means the head is over. Hence `([ \t]|$)` rather than `[ \t]` — CommonMark
# admits `##` alone as an empty heading, and requiring the space silently let one
# through. `#tag` is correctly NOT a heading under either spelling.
_ANY_HEADING_RE = re.compile(r"^ {0,3}#{1,6}([ \t]|$)")

# A TABLE ROW, spelled once. Five sites disagreed about what one is (T103 class b),
# and the disagreement was not academic in either direction. `chk_breadcrumb_row` and
# `_row_cells` anchored on `lstrip()`/`strip()`, so a four-space INDENTED CODE BLOCK
# showing a sample table read as the document's first table row — `DKT Standard.md`
# opens `### kv-table` with exactly that, and the checker failed the page for a
# malformed masthead while the real breadcrumb table sat untouched below. The other
# three anchored at column zero (`^\|`), so a table legitimately indented as the
# continuation of a list item was invisible: `ATT F004` carries a two-space symlink
# table, `chk_breadcrumb_row` sees it and `chk_design_row_iff_folder` does not, and
# the same document gets both verdicts about the same table.
#
# `{0,3}` is CommonMark's bound and it separates exactly those two cases. It is
# deliberately NOT the `[ \t]*` that `_FENCE_RE` settled on, and the asymmetry is
# measured rather than sloppy: CommonMark counts those three spaces from the
# containing block's content column, so both bounds are approximations of a block
# parser this file does not have. For fences the permissive one won because a fence's
# contents are literal either way, so over-recognising costs nothing and
# under-recognising exposes markup samples to the fixers. For table rows the trade is
# reversed — over-recognising a code sample turns it into live structure that
# checkers then demand the author repair.
_TABLE_ROW_RE = re.compile(r"^ {0,3}\|")
# A GFM delimiter row: `|---|---|`, `| :-- | --: |`. Interior is dashes, colons,
# pipes and space, and it must carry at least one dash — without that requirement
# `| | |` (an empty row) reads as a separator.
_TABLE_SEP_RE = re.compile(r"^ {0,3}\|[\s:|-]*-[\s:|-]*\|\s*$")


def _is_table_row(line: str) -> bool:
    """Is this line the start of a GFM table row? The one definition."""
    return bool(_TABLE_ROW_RE.match(line))


def _table_blocks(lines) -> list[list[str]]:
    """Contiguous runs of table rows, in order — one entry per table.

    Named by two defects at once. `chk_tests_table_present` took `rows[2:]` over
    EVERY row in its section, so a second small table's header and separator were
    judged as coverage data rows and reported as "kind row(s) without a wiki-link
    first cell" — a finding about a table that is not the coverage table. And
    `_proposed_tests_rows` identified the separator LEXICALLY, so an all-placeholder
    data row `| - | - | - |` matched the separator pattern, was dropped, and took
    the real row above it out with it (the row a separator follows is a header) —
    silent suppression, the worse half. Both stop being possible once a table is a
    block with a header, an optional separator, and data, instead of a flat list of
    pipe-lines with an index arithmetic guess on top.
    """
    blocks, cur = [], []
    for ln in lines:
        if _is_table_row(ln):
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def _table_data_rows(block: list[str]) -> list[str]:
    """Data rows of ONE table block — header dropped, separator dropped if present.

    Positional, not lexical: the separator can only be the second line of a block,
    so a data row that happens to look like one (`| - | - | - |`) stays data.
    """
    if len(block) >= 2 and _TABLE_SEP_RE.match(block[1]):
        return block[2:]
    return block[1:]


def _unescaped_pipe_positions(s: str) -> list[int]:
    """Indices of every `|` in `s` that markdown reads as a LIVE character — i.e.
    one preceded by an EVEN number of backslashes (zero included).

    The one place this file answers "is this pipe escaped?". Three call sites each
    spelled it `(?<!\\\\)\\|` — a lookbehind that asks only whether *some* backslash
    precedes the pipe — and all three were wrong on the same form: `[[A\\\\|b]]`.
    There `\\\\` is an ESCAPED BACKSLASH that renders as one literal backslash, which
    leaves the pipe bare, so the cell terminates and the row's tail is discarded.
    The lookbehind saw a backslash and called it escaped. Escaping is a parity
    property, not a presence one; only an ODD run escapes.

    Measured on the real checker before the fix (T224): `[[A\\|b]]` pass / 2 cells
    (correct), `[[A\\\\|b]]` **pass / 3 cells (WRONG)**, `[[A|b]]` fail / 3 cells
    (correct). The wrong one is exactly the shape a repair pass produces when it
    escapes an already-escaped pipe, so the fixer could manufacture the defect its
    own checker was blind to. Found by Lumen 2026-08-10 on six [[Lumen Nudge]] rows
    that had lost their tails.

    Written as a shared primitive under the T099 rule that a helper is speculation
    until a defect names it: `_row_cells`, `chk_md_table_pipe_escape` and
    `fix_md_table_pipe_escape` are three independent defects naming it.
    """
    out = []
    for m in re.finditer(r"\|", s):
        i, n = m.start(), 0
        while i - 1 - n >= 0 and s[i - 1 - n] == "\\":
            n += 1
        if n % 2 == 0:
            out.append(m.start())
    return out


def _split_unescaped_pipes(s: str) -> list[str]:
    """`s` split on live pipes only; escaping backslashes stay with their cell."""
    out, prev = [], 0
    for p in _unescaped_pipe_positions(s):
        out.append(s[prev:p])
        prev = p + 1
    out.append(s[prev:])
    return out


def _escape_unescaped_pipes(s: str) -> str:
    """Escape every live pipe in `s`. Right-to-left so earlier indices stay valid."""
    for p in reversed(_unescaped_pipe_positions(s)):
        s = s[:p] + "\\" + s[p:]
    return s


def _row_cells(line: str) -> list[str]:
    """Interior cells of a GFM table row, split on UNESCAPED pipes only.

    Five callers each spelled this as `ln.split("|")`, and every one of them was
    wrong on the form THIS FILE'S OWN RULE mandates: `chk_md_table_pipe_escape`
    requires a wiki-link in a cell to be written `[[Target\\|Label]]`, so a naive
    split cuts the link in half and hands the caller `spec]]` as a "cell". Measured
    consequences were a false finding on the mandated form
    (`chk_spec_cells_format_valid`), a cell read as empty when it was not
    (`chk_proposed_tests_rows_have_spec`), and — the quiet one — an aliased row
    dropped entirely by `_subsystem_names`, so kebab-naming and link-resolution
    silently stopped checking any subsystem that used an alias.

    Written as a shared primitive rather than five patches under the T099 rule that
    a helper is speculation until a defect names it. Four independent defects name
    it, so it is no longer speculation.

    A trailing pipe is optional in GFM: only an empty final field is dropped, so
    `| a | b` keeps `b` — the `[1:-1]` idiom this replaces silently lost it.
    """
    if not _is_table_row(line):
        return []
    s = line.strip()
    parts = _split_unescaped_pipes(s)[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [c.strip() for c in parts]

# SETEXT H1s (`Title` underlined by `===`) are deliberately NOT recognized, and the
# reason is measurement rather than laziness. They are real CommonMark H1s, and the
# omission is genuinely inconsistent — `chk_h1_present` fails such a doc "no H1"
# while `chk_doc_top_order` exempts it "no H1 — out of scope". But implementing it
# was tried here and reverted: of the FOUR vault docs whose only candidate head is a
# `===` underline, not one is a heading. One is a git merge-conflict marker
# (`<<<<<<< HEAD` over `=======` in `House Crime.md`), one is a console banner in
# captured tool output, and two are `=====` used as an ASCII divider in pasted prose
# and in a math scratchpad. Supporting setext scored zero true positives, four false
# heads, and — worse — moved four docs from silently-exempt to failing
# `chk_doc_head_orientation_line` and `chk_doc_top_order` with findings pointing
# hundreds of lines into a body. In this vault `===` is a divider, not an underline.


def _split_frontmatter(text: str) -> tuple[int, str]:
    """`(lines consumed, remaining body)` for a leading YAML frontmatter block.

    ONE definition, because two spellings of it disagreed: `_head_h1` accepted an
    empty `---\\n---\\n` block while `chk_h1_after_frontmatter`'s `.*?` required at
    least one interior line, so the same doc could pass `chk_h1_present` and fail
    `chk_h1_after_frontmatter` on the literal `---`. No vault doc has empty
    frontmatter today; the disagreement is the defect, not its current blast radius.
    """
    m = re.match(r"\A---\n(?:.*?\n)??---\n", text, re.DOTALL)
    if not m:
        return 0, text
    return text[:m.end()].count("\n"), text[m.end():]


def _head_h1(text: str) -> tuple[int | None, str | None]:
    """The document's HEAD H1 as `(line index, heading text)`, or `(None, None)`.

    Skips YAML frontmatter and fenced code, so neither a `# comment:` line inside
    frontmatter nor a `# comment` inside a ```python block can impersonate the
    head. Both were live vault-wide: `skills/bridge/templates/brief-template.md`
    reported its frontmatter's `# status_doc:` comment as the H1, and fourteen
    docs (research notes, `CLAUDE.md` files, `F035 — Tiered Runtime.md`) reported
    a shell or Python comment from inside a fence. Fence pairing is delegated to
    `_strip_fenced`/`_FENCE_RE` (F296) rather than re-hand-rolled — the two
    toggles this replaced knew only ``` and flipped parity on an info-string line.

    HEAD, not merely first — the distinction is T093, and it is why this was
    renamed off `_first_h1`. "The first H1 anywhere" and "the H1 that heads this
    document" are different questions, and under the old name all twelve callers
    silently asked the first while meaning the second. They diverge on **220 vault
    docs** that open a body section with a `# LOG` / `# BRIEF` / `# TODO` marker
    below an earlier `##` — a deliberate and widespread user convention, not a
    defect. Those docs have no head H1 at all, so a scan that returns the marker
    hands every caller a "head" hundreds of lines into the body, and the findings
    that follow blame a real line number for a defect that is not there: an
    orientation line demanded under a section divider, a slug mismatch against
    `# LOG`. `R-spine-02` produced 177 of those and `R-doc-structure`'s
    top-order check another 58, both on rules scoped `where:: always`.

    So a heading of ANY level appearing before the first H1 means there is no head
    H1 — return `(None, None)` and let each caller decide what that means. The one
    exemption is the parked `## Open Questions` block, which /query places above
    the H1 by design (F241); `chk_h1_after_frontmatter` sanctions the same element
    and is the authority for what may legally precede a head.

    The returned index is in WHOLE-FILE coordinates (frontmatter re-added), because
    every caller that reports a line number reports it to a human who will open the
    file at that line.
    """
    off, body = _split_frontmatter(text)
    parked_q = False
    for i, ln in enumerate(_strip_fenced(body).splitlines()):
        hit = _H1_RE.match(ln)
        if hit:
            return off + i, hit.group(1)
        if re.match(r"^ {0,3}## Open (?:Items|Questions)\b", ln):
            parked_q = True
            continue
        if _ANY_HEADING_RE.match(ln):
            if parked_q and re.match(r"^ {0,3}#{3,6}[ \t]", ln):
                continue  # H3+ nested inside the parked block, still pre-head
            return None, None
    return None, None


def chk_at_entity_person_opening(target, anchor_root, args):
    """R-at-entity-11 — a flat person page opens breadcrumb → identity H1 →
    card with Contact + Rolodex, and carries no `#pp`. Warn while the register
    migrates (465 person pages, 441 in the old head-line form on 2026-08-29)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not f.name.startswith("@"):
        return "pass", "not an at entity"
    if f.parent.name.startswith("@") and f.parent.name == f.stem:
        return "pass", "a namesake page — not in scope"
    if "Corp" in f.parts and not f.parent.name.startswith("@"):
        return "pass", "an org page under Corp/ — not in scope"
    text = _read(f)
    lines = text.split("\n")
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
    head = lines[body_start:]
    h1 = next((i for i, l in enumerate(head) if l.startswith("# ")), None)
    problems = []
    pre = "\n".join(head[:h1] if h1 is not None else head[:20])
    if ":>>" not in pre:
        problems.append("no `:>>` breadcrumb above the H1")
    if "| -[[" in pre:
        problems.append("carries a dispatch masthead — a person page is a leaf")
    if h1 is None:
        problems.append("no H1")
    else:
        if not re.match(rf"^# @{re.escape(f.stem[1:])}(\s+—\s+\S|\s*$)", head[h1]):
            problems.append("H1 is not `# @{Name} — **[title](…) at [[@Org]]**` (or a bare `# @{Name}` when nothing is known)")
        j = h1 + 1
        while j < len(head) and not head[j].strip():
            j += 1
        if j >= len(head) or not re.match(r"^\|\s*Card\s*\|", head[j]):
            problems.append("no `| Card |` table directly under the H1")
        else:
            k = j
            rows = []
            while k < len(head) and head[k].strip().startswith("|"):
                rows.append(head[k]); k += 1
            for need in ("Contact", "Rolodex"):
                if not any(re.match(rf"^\|\s*\*\*{need}\*\*", r) for r in rows):
                    problems.append(f"card has no **{need}** row (always present, even empty)")
    if re.search(r"(^|\s)#pp\b", pre + ("\n" + head[h1] if h1 is not None else "")):
        problems.append("`#pp` tag — retired; every @ person page is a person")
    if problems:
        return "warn", "; ".join(problems) + " (R-at-entity-11)"
    return "pass", "breadcrumb → identity H1 → card"


def chk_anchor_has(target, anchor_root, args):
    """`.anchor` declares every field named in args.

    Registered, called by no rule, and that is the correct state rather than a
    gap (T212). `R-dot-anchor-01` reads *".anchor is valid YAML; **every field
    is optional**"*, so there is no field any anchor is required to declare and
    nothing for this primitive to assert. It stays registered because the
    optionality is a property of the *base* grammar: a rule scoped to one kind
    of anchor may well require `slug:` or `traits:` of that kind, and this is
    what it would call. Do not wire it against all anchors.
    """
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return "fail", "no .anchor file"
    text = _read(dot)
    missing = [k for k in args if not re.search(rf"(^|\b){re.escape(k)}\s*[:=]", text, re.MULTILINE)]
    return ("pass", "") if not missing else ("fail", f"missing in .anchor: {', '.join(missing)}")


def _is_stone_store(folder: Path) -> bool:
    """True when this folder is a `stone` STORE — `{slug} Pebbles/` beside its
    control file `{slug} Pebble.md`, and the same for any other stone kind.

    A store is not an anchor: `stone` writes `{slug} P####.md` into the folder
    and keeps the control file **one level up**, so the folder has no namesake
    by design. That is not an omission to repair — 19 of 19 `*Pebbles/` folders
    vault-wide are in exactly this shape, which makes it the convention rather
    than a deviation (T561, from [[Eli]]).

    **The positive half is the control file, not the missing namesake.** Keying
    on "this folder has no namesake" would be circular — that is the very thing
    `R-anchor-page-02` reports. `{slug} Pebble.md` sitting beside the folder is
    a fact `stone` wrote, and nothing acquires it by accident, which is the same
    property the T363 and T556 exemptions are keyed on.

    Suffix and control name are both **derived from `facets/DAS Stone
    Kinds.json`**, whose own comment promises a third kind needs no code change.
    Hardcoding `" Pebbles"` here would quietly break that promise.

    Rocks are matched by this predicate too and are unaffected in practice:
    4 of 4 rock folders carry a namesake AND an `.anchor`, so they pass
    `R-anchor-page-02` on their own. The residual is worth stating — a rock
    folder that LOST its namesake would now be silent here — and it is small
    because a rock group is an anchor by design and `R-dot-anchor` still reads
    it.
    """
    try:
        kinds = _stone_kind_suffixes()
    except Exception:
        return False
    for suffix, (_kind, cfg) in kinds.items():
        if not suffix or not folder.name.endswith(suffix):
            continue
        slug = folder.name[: -len(suffix)]
        control = cfg.get("control")
        if not isinstance(control, str):
            continue
        if (folder.parent / f"{control.replace('{slug}', slug)}.md").is_file():
            return True
    return False


def _is_stone_group(folder: Path) -> bool:
    """True when this folder is a stone GROUP whose namesake is the kind's
    CONTROL FILE — `{owner} Book/` holding `{owner} Book.md`, and the same for
    every kind in `DAS Stone Kinds.json`.

    Exists for the T290 arm of `chk_entry_page_matches_slug`: a stone group's
    note is named by the kind template (`R-stone-01`), never by a declared
    slug, so the slug-names-the-note rule must not fire on one (ATT T289 Q1,
    Dan 2026-08-31 — renaming Hermes Book's note to its slug broke `R-stone-01`,
    `-02` and `-07` at once). Both control positions are accepted — inside the
    folder (the current namesake layout) and one level up (the pre-2026-08
    layout `_is_stone_store` keys on) — because the carve-out must hold across
    the layout migration, not just after it.
    """
    try:
        kinds = _stone_kind_suffixes()
    except Exception:
        return False
    for suffix, (_kind, cfg) in kinds.items():
        if not suffix or not folder.name.endswith(suffix):
            continue
        owner = folder.name[: -len(suffix)]
        control = cfg.get("control")
        if not isinstance(control, str):
            continue
        name = control.replace("{slug}", owner) + ".md"
        if (folder / name).is_file() or (folder.parent / name).is_file():
            return True
    return False


def chk_entry_page_matches_slug(target, anchor_root, args):
    ep = _entry_page(anchor_root)
    if ep is None:
        if _is_stone_store(anchor_root):
            # T561, 2026-08-20. Fired on 19 of 19 pebble stores, measured
            # through the real `--mode anchor --run` plan rather than by calling
            # this checker directly (which passes the vault as anchor_root and
            # answers a different question — the first cut of this measurement
            # got "1 of 19" that way and was wrong).
            return "pass", "a stone store, not an anchor — control file is one level up"
        return "fail", f"no entry page {_anchor_slug(anchor_root)}.md"
    # T290 (Dan 2026-08-30): a DECLARED slug names the folder note. _entry_page
    # falls back to {folder}.md — correct resolution, but under a declared slug
    # the fallback hit IS the violation, not a pass. Byte-exact via the
    # directory listing, because the filesystem is case-insensitive and
    # is_file() would bless `muse.md` as `MUSE.md`. A missing note entirely is
    # the ep-is-None branch above — a different finding, deliberately not this
    # arm's (three empty placeholder anchors would otherwise fail it).
    dot = anchor_root / ".anchor"
    declared = None
    if dot.is_file():
        m = re.search(r"^\s*slug\s*:\s*(.+?)\s*$", _read(dot), re.M)
        if m:
            declared = m.group(1).strip().strip("\"'")
    if declared and declared != anchor_root.name:
        try:
            names = {p.name for p in anchor_root.iterdir()}
        except OSError:
            return "error", "unreadable anchor root"
        if f"{declared}.md" not in names:
            if _is_stone_group(anchor_root):
                return "pass", (f"a stone group — {ep.name} is the kind's control file, "
                                f"named by the kind template, never by the slug")
            if "Warden Corpus/cases/" in str(anchor_root):
                return "pass", ("a Warden corpus fixture — deliberately minimal, "
                                "slugs reused across cases")
            return "fail", (f"slug {declared!r} is declared but the folder note is {ep.name} "
                            f"— rename it to {declared}.md (a declared slug names the "
                            f"folder note, Dan 2026-08-30 / ATT T290)")
    return "pass", ep.name


def chk_frontmatter_has(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    fm = _frontmatter(_read(f))
    if fm is None:
        return "fail", "no YAML frontmatter"
    key = args[0] if args else "description"
    return ("pass", "") if re.search(rf"^{re.escape(key)}\s*:", fm, re.MULTILINE) else ("fail", f"frontmatter missing {key}:")


def chk_h1_present(target, anchor_root, args):
    """A head H1 exists. Reports WHICH failure it is, because they want opposite fixes.

    "No head H1" covers two populations that a bare `no H1` message conflates, and
    T101 measured the split on the 23 in-scope feature docs that fail: only 6 have
    no `# ` line at all, while **17 carry the correct title H1 further down**, below
    an earlier `##` — `# F035 — Tiered Runtime` at line 145, `# F043 — Controllable
    Named Views` at line 24, each under a `## Resolved Decisions` block written in
    the pre-F241 above-the-H1 style. Told `no H1`, an author adds a second one; told
    where the existing one sits, they move it. Reporting a true fault with a message
    that implies the wrong remediation is the same damage signature as T092/T093,
    one layer in — the line number is right and the instruction is not.

    The message states the observation and stops short of prescribing, deliberately.
    Whether a displaced H1 should MOVE depends on the doc class: in a feature doc it
    is a misplaced title, but in the 124 loose notes T101 excluded from scope the
    same shape is a deliberate `# LOG` / `# BRIEF` body marker that must stay put.
    One checker cannot tell those apart; the `where::` glob can, so the checker
    reports what it sees and the rule's scope decides what it means.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    if _head_h1(text)[0] is not None:
        return "pass", ""
    off, body = _split_frontmatter(text)
    for i, ln in enumerate(_strip_fenced(body).splitlines()):
        if _H1_RE.match(ln):
            return "fail", f"no head H1 (an H1 sits at line {off + i + 1}, below an earlier heading)"
    return "fail", "no H1"


def chk_no_blank_after_h1(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    lines = text.splitlines()
    i, _ = _head_h1(text)
    if i is None:
        return "fail", "no H1"
    # `lines` is the ORIGINAL text, so the line after an H1 that opens a fenced
    # block is the fence marker (non-blank) rather than the blanked-out interior.
    if i + 1 >= len(lines):
        # 165 vault docs are an H1 and nothing else. Reporting "blank line directly
        # after H1" on them describes a defect that is not there, and sends the
        # reader hunting for a blank line to delete; the file simply ends.
        return "fail", "the H1 is the last line — no orientation line follows it"
    if lines[i + 1].strip() == "":
        return "fail", "blank line directly after H1"
    return "pass", ""


def chk_regex_present(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    pat = args[0] if args else ""
    return ("pass", "") if re.search(pat, _read(f), re.MULTILINE) else ("fail", f"pattern absent: {pat}")


def chk_regex_absent(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    pat = args[0] if args else ""
    return ("fail", f"pattern present: {pat}") if re.search(pat, _read(f), re.MULTILINE) else ("pass", "")


# Sanctioned non-slug-prefixed name patterns (R-naming-03 allowlist). Matched
# against the file stem (basename without .md).
_NAME_ALLOWLIST = (
    r"^F\d+ [—-] ",              # F<NNN> — title  (Features, legacy + F298)
    r"^[A-Za-z]+\d{3} - ",       # {SLUG}<NNN> - title  (Features, F300)
    r"^US-[A-Za-z]+-\d+ [—-] ",  # US-<SLUG>-<N> — title  (Stories)
    r"^\d{4}-\d{2}-\d{2}\b",     # YYYY-MM-DD topic  (Log)
    r"^\d{4}-\d{2}\b",           # YYYY-MM topic
    r"^\d{4}\b",                 # YYYY topic
    r"^SKILL$",                  # SKILL.md  (Claude Code skill entry convention)
    r"^R-[a-z]",                 # R-<x>.md  (ruleset / rule files, F133)
)


def _ancestor_anchor_slugs(anchor_root: Path) -> list[str]:
    """Slugs of this anchor AND every ancestor anchor up to the repo root. Nested
    anchors (`{ROOT} Design/`, `{ROOT} Track/`) prefix their files with the ROOT
    anchor's slug, not their own folder name — so a file is correctly named if it
    carries any ancestor anchor's slug (per DAS Naming §Folder-anchor files)."""
    out: list[str] = []
    try:
        cur = anchor_root.resolve()
        root = REPO_ROOT.resolve()
    except OSError:
        return [_anchor_slug(anchor_root), anchor_root.name]
    while True:
        if (cur / ".anchor").is_file():
            out.append(_anchor_slug(cur))
            out.append(cur.name)
        if cur == root or cur.parent == cur:
            break
        cur = cur.parent
    return out or [_anchor_slug(anchor_root), anchor_root.name]


_SLUG_GRAMMAR = re.compile(r"^[A-Z0-9]+$")


def _anchor_display_name(anchor_root):
    """The anchor's NAME as a reader sees it — the anchor page's stem when the
    folder has one, else the folder basename.

    The two differ in case more often than they look like they would: the
    Warden anchor is folder `warden/` (a repo-path convention, sibling to
    `rs/` and `engine/`) but page `Warden.md`, and every prose reference is
    `[[Warden]]`. R-dot-anchor-03's name-as-slug form is decided against the
    name a reader knows, which is the page title.
    """
    base = anchor_root.name
    try:
        for md in anchor_root.glob("*.md"):
            if md.stem.lower() == base.lower():
                return md.stem
    except OSError:
        pass
    return base


def chk_slug_is_a_handle(target, anchor_root, args):
    """R-dot-anchor-03: a declared slug is all capitals unless it IS the name,
    and is never a restatement of the basename (TINK F301, amended by T150).

    GRAMMAR — two legal forms, ruled by Dan 2026-08-13. A slug is `^[A-Z0-9]+$`
    (one uppercase alphanumeric token) when it is a genuine SHORTENING, which is
    the ordinary case; or it is THE NAME ITSELF, carried in the name's own case
    (`Warden`). The one thing forbidden is two casings of the same word in
    circulation, so a name used as its own slug is never upcased. A leading
    digit is deliberate in the first form, because ANC Standard retires a slug
    in place by prefixing its two-digit creation year (`SKD` -> `25SKD`);
    `^[A-Z][A-Z0-9]*$` would condemn every retired slug.

    RESTATEMENT — a value BYTE-IDENTICAL to the FOLDER BASENAME says nothing the
    basename did not already say, and deleting it is provably safe: the implied
    slug computes to the same handle with the declaration gone. That test is
    against the folder specifically, because the folder is what the implied slug
    is computed from. A slug equal to the anchor PAGE's name but not the folder's
    (`Warden` over `warden/`) is doing real work and stays.

    A slug differing from the basename only in CASE is likewise NOT a
    restatement, and the distinction is load-bearing. `MUSE` for folder `muse`
    supplies an uppercase prefix form (`MUSE F018.md`) that the lowercase
    basename cannot; deleting it would drop the implied slug to `muse` and put
    every prefixed file in that anchor in violation. The Staff roster
    (`TINK`/`Tink`) is the same shape, so it needs no exemption — it was never
    an exception, only a case the first draft of this rule mis-classified.

    Silent on an anchor that declares no slug — that is the common and correct
    case (86% of the corpus), not a defect.
    """
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return "pass", "no .anchor"
    try:
        text = dot.read_text(encoding="utf-8")
    except OSError:
        return "error", "unreadable .anchor"
    m = re.search(r"^\s*slug\s*:\s*(.+?)\s*$", text, re.M)
    if not m:
        return "pass", "no slug declared — the basename serves"
    slug = m.group(1).strip().strip('"').strip("'")
    name = _anchor_display_name(anchor_root)
    # Restatement is tested FIRST because it is the more specific diagnosis and
    # the only one carrying a provably-safe fix. A multi-word restatement fails
    # both tests, and reporting the grammar violation would send the reader off
    # to invent a shortening when deleting the line is correct and lossless.
    # Measured 2026-08-18 (T241): all 19 vault failures are restatements, and
    # grammar-first mislabelled the 11 multi-word ones.
    if slug == anchor_root.name:
        return "fail", (f"slug {slug!r} restates the basename {anchor_root.name!r} "
                        f"— delete it; the implied slug is already that value")
    is_the_name = slug == name and slug != anchor_root.name
    if not is_the_name and not _SLUG_GRAMMAR.match(slug):
        return "fail", (f"slug {slug!r} is neither one uppercase alphanumeric token "
                        f"(^[A-Z0-9]+$) nor the anchor's own name {name!r} — a slug "
                        f"is a prefix and must be visually separable from the name "
                        f"it sits in front of, unless it IS that name")
    return "pass", ""


def chk_name_slug_prefixed(target, anchor_root, args):
    """Per-file (R-naming-01, recast 2026-08-02): a prefix is OPTIONAL, but if
    one is present it must be the anchor's slug.

    The rule used to REQUIRE a prefix, which put 3,047 of 7,799 vault files
    (39%) in violation — folder membership is what makes a file a child of an
    anchor, not its name, and `Lumens.md` / `Notes on X.md` are well-named. The
    R-naming-03 allowlist had grown into a workaround for that over-reach.

    What IS a defect is a file leading with the anchor's folder NAME where a
    distinct slug exists (`Tink Backlog.md` under slug `TINK`), because then
    `{slug}` interpolation in a `where::` selector resolves to a token no file
    matches — silently. T111 is that failure: an index-page term reached 0 of
    22 pages. Nested anchors legitimately carry the ROOT slug, so `MUX Track/
    MUX Paths.md` is correct and only the folder-name form is refused.

    The uniqueness property this protects is audit-q C53's (F281); this rule is
    only the mechanism that keeps it true for the repeated structural names.
    """
    if not target.is_file():
        return "pass", "not a file"
    stem = target.stem
    # The refusal is tested FIRST and deliberately. `_ancestor_anchor_slugs`
    # returns each ancestor's slug AND its folder name, so a pass-check run
    # ahead of this would accept `Atticus Backlog.md` on the folder name and
    # the rule would never fire at all — which is the exact defect T112 caught.
    for wrong in _ancestor_folder_names(anchor_root):
        if stem == wrong or stem.startswith(f"{wrong} "):
            return ("fail", f"{target.name!r} leads with the folder name "
                            f"{wrong!r}; the prefix must be the slug "
                            f"({_anchor_slug(anchor_root)!r})")
    if any(stem == s or stem.startswith(f"{s} ")
           for s in _ancestor_anchor_slugs(anchor_root)):
        return "pass", ""
    for pat in _NAME_ALLOWLIST:
        if re.match(pat, stem):
            return "pass", "allowlisted pattern"
    return "pass", "no prefix — legal (folder membership is what scopes a file)"


def _ancestor_folder_names(anchor_root: Path) -> list[str]:
    """Ancestor anchor FOLDER names that differ from their own declared slug —
    the spellings R-naming-01 refuses as a prefix.

    Uses `_anchor_name` (the slug exactly as `.anchor` declares it), NOT
    `_anchor_slug` (which reduces a multi-token slug to its first token). An
    anchor may legitimately declare `slug: SKA ctrl`, and there the folder name
    IS the slug — reducing it to `SKA` would refuse `SKA ctrl/SKA ctrl.md`,
    which is correctly named. That mistake falsely condemned 130 files.
    """
    out: list[str] = []
    try:
        cur, root = anchor_root.resolve(), REPO_ROOT.resolve()
    except OSError:
        return out
    while True:
        if (cur / ".anchor").is_file():
            if cur.name != _anchor_name(cur):
                out.append(cur.name)
        if cur == root or cur.parent == cur:
            break
        cur = cur.parent
    return out


def chk_h1_after_frontmatter(target, anchor_root, args):
    """The H1 opens the body after the YAML frontmatter, allowing only the two
    sanctioned pre-H1 elements: a `:>>` breadcrumb line (canonical DIRECTLY above
    the H1 per R-doc-structure-01 — its exact position is `doc_top_order`'s job,
    not re-judged here) and a parked `## Open Questions` block (placed between
    frontmatter and H1 per /query parented mode). Anything else before the H1
    fails. (2026-07-06: previously this checker failed the breadcrumb-above-H1
    form its own rule's prose mandates — the contradiction that pushed at least
    one PRD's breadcrumb below its H1.)"""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    _, body = _split_frontmatter(text)
    in_questions = False
    # DELIBERATELY NOT fence-stripped, and the T099 sweep that converted its twelve
    # siblings stopped here on purpose. The loop below accepts only three things
    # before the H1 — blank, `:>>`, `## Open Questions` — and rejects everything
    # else, so it trips on the fence OPENER itself, which is correct: a code block
    # above the H1 is precisely the "anything else" this rule forbids. Stripping
    # would blank that opener, the loop would skip it as empty, and the checker
    # would pass a file it exists to fail. Its neighbour `chk_architecture_h1_present`
    # reads the opposite way — it matches only HEADING lines, steps over the opener,
    # and does need stripping. Same class, opposite fix; the discriminator is
    # whether the scan rejects unknown lines or ignores them.
    for ln in body.splitlines():
        if not ln.strip():
            continue
        if _H1_RE.match(ln):
            return "pass", ""
        if ln.lstrip().startswith(":>>"):
            in_questions = False
            continue
        if re.match(r"^## Open (?:Items|Questions)\b", ln):
            in_questions = True
            continue
        if in_questions:
            continue
        return "fail", f"first line after frontmatter is not an H1: {ln!r}"
    return "fail", "no body after frontmatter"


def chk_h1_matches_slug(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    slug = _anchor_slug(anchor_root)
    _, h1 = _head_h1(_read(f))
    if h1 is None:
        return "fail", "no H1"
    if re.match(rf"^{re.escape(slug)}\s*[-–—]\s+\S", h1):
        return "pass", h1
    if h1 == slug or h1 == anchor_root.name:
        return "pass", f"bare-name: {h1}"
    return "fail", f"H1 {h1!r} is not '{slug} - <name>'"


def chk_breadcrumb_row(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Fence-stripped (T103a): a masthead shown as a fenced EXAMPLE is exactly what
    # the docs teaching mastheads carry, and reading one as the doc's first table
    # row fails the page for a malformed breadcrumb it does not have.
    for ln in _strip_fenced(_read(f)).splitlines():
        if _is_table_row(ln):
            if re.search(r"\|\s*-\[\[.+?\]\]-\s*\|.*hook://", ln.strip()):
                return "pass", ""
            return "fail", "first table row is not a breadcrumb (-[[…]]- … hook://)"
    return "pass", "no dispatch table (tableless anchor)"


def chk_design_row_iff_folder(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    name = _anchor_slug(anchor_root)
    has_folder = (anchor_root / f"{name} Design").is_dir()
    text = _strip_fenced(_read(f))   # T103a — a fenced sample row is not a Design row
    # A *Design row*'s first cell is the design-folder link aliased exactly "Design"
    # (or a bare "Design" cell) — NOT a member doc like "UX Design"/"API Design".
    has_row = (bool(re.search(r"^ {0,3}\|\s*\[\[[^\]|]*\|Design\]\]", text, re.MULTILINE))
               or bool(re.search(r"^ {0,3}\|\s*Design\s*\|", text, re.MULTILINE)))
    if has_folder == has_row:
        return "pass", "both present" if has_folder else "neither (no design facet)"
    if has_folder and not has_row:
        return "fail", f"{name} Design/ exists but no Design row in the table"
    return "fail", f"Design row present but no {name} Design/ folder"


# ── F161 batch-2 primitives (consolidated from multi-agent proposals) ────────
#
# Shared header/field, facet-page, ruleset, status, testing, prd, roadmap, log,
# brief, design, dated-stream, naming, and SVG-geometry/hygiene checkers. Where
# several proposals overlapped they were merged to one general primitive (see the
# `renames` report). Python 3.11 target: no nested same-quote f-strings.


# -- shared header / field helpers --------------------------------------------

def _header_block(lines, h1_idx):
    """Lines after H1 up to (not including) the first blank line."""
    out = []
    for i in range(h1_idx + 1, len(lines)):
        if lines[i].strip() == "":
            break
        out.append(lines[i])
    return out


def _head_h1_idx(lines):
    """Index-only view of `_head_h1`, for the callers that already hold `lines`.
    Rejoining is cheap next to the `_read` these callers just did, and it keeps ONE
    definition of what an H1 is — the whole point of the primitive."""
    return _head_h1("\n".join(lines))[0]


def chk_header_has_field(target, anchor_root, args):
    """Header (lines after H1, before first blank) carries `<field>::`. Arg: field.

    Two failures live under this one verdict and they want opposite fixes, so it
    names which one it found (T212, wiring it to R-ruleset-02). Of the 16 files
    carrying the RULESET sentinel that fail on `include`, **9 have no such line
    at all** and **7 have one sitting below a blank line** — a header detached
    from its H1, which `parse_ruleset_block` tolerates and this rule's Check
    pattern does not. Told only *"header missing include:: line"*, the author of
    one of those 7 goes looking for a line that is already there, two rows down.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    field = args[0] if args else "include"
    h1_idx = _head_h1_idx(lines)
    if h1_idx is None:
        return "fail", "no H1"
    pat = re.compile(rf"^{re.escape(field)}::")
    for ln in _header_block(lines, h1_idx):
        if pat.match(ln):
            return "pass", ""
    # Look past the gap before concluding it is absent. Bounded to the leading
    # field zone so a `field::` mentioned anywhere in the body cannot satisfy it.
    for ln in lines[h1_idx + 1:h1_idx + 14]:
        if pat.match(ln):
            return "fail", (f"{field}:: sits below a blank line — the header "
                            f"block runs from the line after the H1")
    return "fail", f"header missing {field}:: line"


def chk_description_field_line(target, anchor_root, args):
    """`description::` present (2nd non-blank line preferred) with no `::` in value.
    Consolidates description_field_valid / status_description_line /
    description_field_second_line."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    nonblank = [ln for ln in _read(f).splitlines() if ln.strip()]
    if len(nonblank) < 2:
        return "fail", "fewer than 2 non-blank lines"
    if not _H1_RE.match(nonblank[0]):
        return "fail", "first non-blank line is not H1"
    for ln in nonblank[1:]:
        m = re.match(r"^description::\s*(.*)$", ln)
        if m:
            value = m.group(1)
            if not value:
                return "fail", "description:: value is empty"
            if "::" in value:
                return "fail", "description:: value contains :: token"
            return "pass", ""
        # only consider the 2nd non-blank line as the required slot
        break
    return "fail", "second non-blank line is not 'description:: ...'"


# -- R-facet-spec --------------------------------------------------------------

def chk_facet_dispatch_top(target, anchor_root, args):
    """H1 -> a one-line summary (a single blank line after the H1 is tolerated) -> a
    breadcrumb dispatch table. The substantive requirement is the breadcrumb table —
    the masthead is what makes a facet spec navigable."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    h1_idx = _head_h1_idx(lines)
    if h1_idx is None:
        return "fail", "no H1"
    # summary line: first non-blank, non-table line within 2 lines of the H1
    summary_idx = None
    for i in range(h1_idx + 1, min(h1_idx + 3, len(lines))):
        if lines[i].strip() and not _is_table_row(lines[i]):
            summary_idx = i
            break
    if summary_idx is None:
        return "fail", "no one-line summary after H1"
    # The masthead sits ABOVE the H1 — that is the convention every facet spec in
    # the corpus follows, and the one DAS Anchor Page specifies. Searching only
    # BELOW the summary meant the table was always behind the cursor, so this
    # `(checked)` rule failed 100% of the corpus while reading as real coverage.
    bc = re.compile(r"^ {0,3}\|\s*-\[\[.+?\]\]-\s*\|")
    if any(bc.search(l) for l in lines[:h1_idx]):
        return "pass", "breadcrumb table above the H1 (masthead convention)"
    # ...and still accept it below, for any doc laid out the other way round.
    for i in range(summary_idx + 1, min(summary_idx + 12, len(lines))):
        if bc.search(lines[i]):
            return "pass", "H1 -> summary -> breadcrumb table"
    return "fail", "no breadcrumb dispatch table (missing masthead)"


def chk_triggers_section_iff_declared(target, anchor_root, args):
    """## Triggers present IFF triggers declared (has typed ### H3 entries)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Boundaries on the fence-stripped copy (T099). This rule is scoped to
    # `DAS *.md` — facet specs, the doc class whose whole job is to SHOW markup —
    # so a fenced `## ` sample closing the section early is not a hypothetical
    # here; twelve of the vault's `DAS *.md` docs carry a fenced H2 with a real H2
    # opening above it. A truncated section reads as having no `### ` entries and
    # the doc is failed for a Triggers block that is fully populated.
    text = _strip_fenced(_read(f))
    m = re.search(r"^## Triggers\s*$", text, re.MULTILINE)
    if not m:
        return "pass", "no Triggers section (implies no triggers declared)"
    start = m.start()
    nxt = re.search(r"^## ", text[start + 1:], re.MULTILINE)
    end = start + 1 + nxt.start() if nxt else len(text)
    section = text[start:end]
    if re.search(r"^### \S+", section, re.MULTILINE):
        return "pass", "Triggers section has typed H3 triggers"
    return "fail", "Triggers section present but has no typed H3 entries"


# A retired location token and the words that turn a mention of it into history.
# `\{slug\}` is the placeholder as facet specs write it; the trailing `\b` catches
# `{slug} Docs`, `{slug} Docs/`, and `{slug} Docs/{slug} Plan/` alike.
_RETIRED_LOCATION_RE = re.compile(r"\{slug\}\s+Docs\b")
_PROVENANCE_WORDS = (
    "previously", "legacy", "superseded", "deprecated", "retired",
    "pre-f094", "no longer", "used to", "formerly", "migrat",
)


def chk_no_retired_location(target, anchor_root, args):
    """R-facet-spec-28: a facet spec must not state `{slug} Docs/` as a LIVE location.

    The `{slug} Docs/` tree was retired 2026-08-05 (T118). Its three subfolders did
    not land in one place — `Docs/{slug} Plan/` and `Docs/{slug} Design/` collapsed
    into `{slug} Design/`, `Docs/{slug} Dev/` became `{slug} Dev Docs/`, and Outputs
    moved to `{slug} Track/` — so a corpus that half-remembers the old tree files
    documents in three different wrong places, which is exactly the split this rule
    exists to prevent recurring.

    Provenance survives. A note telling a reader who finds a legacy tree that the
    path is superseded is the *reason* the retirement is legible; four such notes
    stand in the corpus by design. So the unit of judgement is the containing
    PARAGRAPH, not the line: a mention accompanied by a history word passes, a bare
    location claim fails. Paragraph rather than line because a provenance sentence
    is often the lead-in to a bulleted path, and failing that shape would push
    authors toward cramming history into every bullet."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    # Paragraph = a run of consecutive non-blank lines. Cheap, and it is the unit a
    # reader actually judges "is this history or an instruction?" against.
    para_start, offenders = 0, []
    for i in range(len(lines) + 1):
        if i < len(lines) and lines[i].strip():
            continue
        para = lines[para_start:i]
        if para and any(_RETIRED_LOCATION_RE.search(ln) for ln in para):
            blob = " ".join(para).lower()
            if not any(w in blob for w in _PROVENANCE_WORDS):
                hit = next(j for j, ln in enumerate(para)
                           if _RETIRED_LOCATION_RE.search(ln))
                offenders.append(para_start + hit + 1)
        para_start = i + 1
    if offenders:
        where = ", ".join(f"line {n}" for n in offenders[:3])
        return "fail", (f"`{{slug}} Docs/` stated as a live location ({where}) — "
                        f"retired 2026-08-05; use `{{slug}} Design/`, "
                        f"`{{slug}} Dev Docs/`, or `{{slug}} Track/`. A historical "
                        f"note is fine if the paragraph says so (previously / "
                        f"legacy / superseded)")
    return "pass", ""


# -- R-ruleset -----------------------------------------------------------------

def chk_all_rules_have_id(target, anchor_root, args):
    """Every RULE heading matches R-<slug>-NN."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Same stripping, same reason, as the sibling `chk_rule_numbers_unique` below:
    # a ruleset showing an example RULE heading is documenting the form, not
    # declaring a rule. No rule invokes this checker today (T099 census: one of six
    # such orphans), so the conversion moves nothing — it is here so that wiring it
    # later does not re-import the defect its wired siblings already shed.
    headings = [ln for ln in _strip_fenced(_read(f)).splitlines()
                if re.match(r"^#+\s+RULE\s+", ln)]
    if not headings:
        return "pass", "no rules found"
    for h in headings:
        if not re.search(r"R-[a-z0-9-]+-\d{2}\b", h):
            return "fail", f"invalid rule heading: {h[:60]}"
    return "pass", ""


def chk_rule_numbers_unique(target, anchor_root, args):
    """Rule ids (R-<slug>-NN) are unique within the file."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    seen = set()
    # A rule is DECLARED by a heading, the same anchoring its sibling
    # `chk_all_rules_have_tier` already uses. The unanchored `re.search` this
    # replaced counted any line MENTIONING an id — so a ruleset whose prose cites
    # its own `RULE R-x-01` (to explain why rule 03 exists, say) reported that id
    # as a duplicate declaration, and the remediation on offer is to delete one of
    # the two — either the real rule or the sentence explaining it. Fences are
    # stripped for the same reason: a ruleset that shows an example RULE heading
    # is documenting the form, not declaring a second rule.
    for ln in _strip_fenced(_read(f)).splitlines():
        m = re.match(r"^ {0,3}#+\s+RULE\s+(R-[a-z0-9-]+-\d{2})\b", ln)
        if m:
            if m.group(1) in seen:
                return "fail", f"duplicate rule id: {m.group(1)}"
            seen.add(m.group(1))
    return "pass", "" if seen else "no rules found"


def chk_all_rules_have_tier(target, anchor_root, args):
    """Every RULE heading carries a tier `_RULE_RE` admits, or is a hook rule.

    Wired to `R-ruleset-06` on 2026-08-11, having sat registered-and-invoked-by-
    nothing since T099. It is the standing guard against the fold: a heading
    `_RULE_RE` rejects is skipped, and a skipped heading does not terminate the
    rule above it, so the `check::` beneath folds onto its predecessor and that
    rule silently runs someone else's checker. `R-rocks-03` did exactly this,
    twice. Every other consumer reads PARSED rules and therefore cannot see the
    heading at all — which is why the guard has to read raw lines.

    **Two families share the `RULE` sentinel and only one is ours.** An audit
    rule runs a `check::` and must declare a tier; a **Warden rule** is
    declarative — `when::` / `if::` / `mend::` — and has no tier by design,
    because tiers describe *this* engine's execution model and Warden has its
    own. 37 Warden rules live in the corpus and flagging them would be this
    checker going red for the wrong reason. They also cannot fold: the field
    beneath them is not `check::`.

    **A Warden rule is spelled two ways and both must count**, which took two
    passes to get right. `R-pathguard` / `R-ios` / `R-ob-remote-ops` /
    `R-code-mirror` put the moment in the heading parenthetical
    (`… (when:: tool:pre:Bash)`); `R-fct-claude` and the `FEX Repo` example
    rulesets put `when::` / `if::` on a body line instead. Keying on the
    heading alone flagged 11 headings that were all Warden rules; keying on the
    body alone flagged 8 of the other spelling. Neither number was a defect
    count — each was a measure of which spelling the checker had not learned.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _strip_fenced(_read(f)).splitlines()
    idx = [i for i, ln in enumerate(lines) if re.match(r"^#+\s+RULE\s+", ln)]
    if not idx:
        return "pass", "no rules found"
    bad = []
    for n, i in enumerate(idx):
        if _RULE_RE.match(lines[i]):
            continue
        end = idx[n + 1] if n + 1 < len(idx) else len(lines)
        body = lines[i:end]
        warden = (bool(re.search(r"\(when::[^)]*\)\s*$", lines[i]))
                  or any(re.match(r"^(when|if|mend)::", b) for b in body))
        declares_check = any(b.startswith("check::") for b in body)
        if warden and not declares_check:
            continue                      # a Warden rule — not this engine's
        bad.append(lines[i])
    if bad:
        return "fail", (f"{len(bad)} rule heading(s) carry no tier "
                        f"`_RULE_RE` admits, so the parser skips them and the "
                        f"next `check::` folds onto the rule above: "
                        f"{bad[0].strip()[:70]}")
    return "pass", ""


def chk_checked_rules_have_pattern(target, anchor_root, args):
    """Every (checked)/(sampled) rule body carries a **Check pattern:** field."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Structure comes off the fence-stripped copy. Every rule body in a ruleset
    # ends in a ```python block, and a `# comment` at column 0 inside it matched
    # the `^#+\s+` body terminator — so the body ended AT the code, and a
    # `**Check pattern:**` written below it was never seen. The finding that
    # produces ("missing Check pattern") points at a rule that has one.
    lines = _strip_fenced(_read(f)).splitlines()
    missing = []
    i = 0
    while i < len(lines):
        m = re.match(r"^ {0,3}#+\s+RULE\s+(R-[a-z0-9-]+-\d{2})", lines[i])
        if m and re.search(r"\((checked|sampled)\)\s*$", lines[i]):
            rule_id = m.group(1)
            body = ""
            i += 1
            while i < len(lines) and not re.match(r"^ {0,3}#+\s+", lines[i]):
                body += lines[i] + "\n"
                i += 1
            # A QUALIFIED heading counts. `**Check pattern (queries-specific,
            # C39):**` and `**Check pattern (Rust):**` are the same field naming
            # which half of the rule the pattern covers — a distinction worth
            # writing when a rule inherits some checks and adds others. The
            # literal-substring test rejected both, and the remediation it
            # offered was to delete the qualifier from a rule that has a pattern
            # (T212, 2026-08-11: 2 of the 17 findings on first wiring were this).
            if not re.search(r"\*\*Check pattern[^*\n]*:\*\*", body):
                missing.append(rule_id)
        else:
            i += 1
    if missing:
        # Say what the cap hid. Three names with no count reads as "three
        # findings", so an author fixes three, re-runs, and meets three more —
        # with no way to tell at any point how far from done they are (T212).
        more = f" (+{len(missing) - 3} more)" if len(missing) > 3 else ""
        return "fail", "missing Check pattern: " + ", ".join(missing[:3]) + more
    return "pass", ""


def chk_ruleset_no_frontmatter(target, anchor_root, args):
    """Standalone ruleset file (# RULESET first non-blank BELOW any frontmatter)
    has no YAML frontmatter.

    Decide kind on the body, not on line 1 (T217, 2026-08-11). The previous form
    asked whether the file's *first non-blank line* was `# RULESET` and, if not,
    answered `('pass', 'not a standalone ruleset file')`. On a file that opens
    with frontmatter that line is the frontmatter's own `---`, so **every file
    this rule exists to catch exempted itself for carrying the very thing being
    forbidden** — the violation was its own defense. `R-dispatch-table.md` sat
    that way long enough for its `where:` to go unread by both engines and all
    15 of its rules to run at `always`.

    Frontmatter is leading by definition, so the presence question is answered by
    the strip and nothing else. The old code instead scanned the WHOLE file for a
    line starting `---` once it judged the file standalone, which can only add
    false positives (a `---` thematic break in the body) and cannot add a true
    one. Measured before replacing it: across all 122 vault files carrying a
    `# RULESET R-` block, exactly one verdict changes — `examples/FEX Repo/
    R-fex-manifest.md`, a real violation in the file whose stated job is to be
    the worked example of the ruleset format.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _strip_fenced(_read(f)).splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    had_frontmatter = False
    if i < len(lines) and lines[i].strip() == "---":
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == "---":
                lines = lines[j + 1:]
                had_frontmatter = True
                break
    first = next((ln for ln in lines if ln.strip()), None)
    if first is None:
        return "pass", "empty file"
    if re.match(r"^#+\s+RULESET\s+R-", first):
        if had_frontmatter:
            return "fail", "standalone ruleset file has YAML frontmatter"
        return "pass", ""
    return "pass", "not a standalone ruleset file"


# -- R-status ------------------------------------------------------------------

def chk_status_filename_valid(target, anchor_root, args):
    """Filename is exactly '{slug} Status.md'."""
    slug = _anchor_slug(anchor_root)
    expected = f"{slug} Status.md"
    if target.name == expected:
        return "pass", ""
    return "fail", f"expected {expected!r}, got {target.name!r}"


def chk_status_in_track_folder(target, anchor_root, args):
    """File lives in {slug} Track/."""
    slug = _anchor_slug(anchor_root)
    expected_parent = anchor_root / f"{slug} Track"
    if target.parent == expected_parent:
        return "pass", ""
    return "fail", f"not in {expected_parent.name}/ folder; found in {target.parent.name}/"


def chk_doc_in_design_folder(target, anchor_root, args):
    """R-fct-system-design-01: the doc sits in a `* Design/` folder.

    Matched on the folder SUFFIX rather than on `{slug} Design` exactly, because a
    sub-anchor's design folder is named for the sub-anchor and the slug lookup at
    the anchor root would reject perfectly well-placed files. The rule being
    enforced is "filed with the design docs", not "filed under this precise slug".

    Walks ANCESTORS rather than testing the immediate parent only: a subsystem's
    design doc nests one level deeper (`MUX Design/DMUX Subsystem/DMUX System
    Design.md`) and is correctly filed — the parent-only form failed it, which was
    the rule inventing a defect rather than finding one.
    """
    for part in reversed(target.parent.parts):
        if part.endswith(" Design") or part == "Design":
            return "pass", ""
    return "fail", (f"not under a `* Design/` folder; found in `{target.parent.name}/` "
                    f"— a System Design is a design artifact and files with its "
                    f"siblings (PRD, Roadmap, Architecture)")


def chk_no_decisions_section(target, anchor_root, args):
    """R-fct-system-design-05: no `## Decisions` H2 — decisions live in their own file.

    Ruled by Dan 2026-08-05 (Q004) as the general model: specialized content like
    decisions goes in its own file rather than becoming a section of a design doc.
    A decision inlined here is invisible to anything reading `{slug} Decisions.md`,
    and it makes the design doc a second place a reader has to check.

    Routed through `_h2_titles` rather than a local `^##\\s+Decisions$` regex — the
    primitive already strips fences (so a doc quoting the heading as an EXAMPLE of
    what not to do does not fail on its own advice) and already allows the six
    genuinely indented H2s in the vault. Re-spelling "what an H2 is" inside a checker
    is the T099 defect class, and structure-lint catches it.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    for idx, title in _h2_titles(_read(f).splitlines()):
        if title.rstrip(":").strip().lower() == "decisions":
            return "fail", (f"`## {title}` at line {idx + 1} — durable rulings belong "
                            f"in the anchor's own Decisions doc, not inlined here "
                            f"(R-fct-system-design-05)")
    return "pass", ""


def _status_facet_lines(text):
    """`name:: value` lines excluding description::."""
    out = []
    for ln in text.splitlines():
        if re.match(r"^[a-z_]+:: ", ln) and not ln.startswith("description::"):
            out.append(ln)
    return out


def chk_status_facets_ordered(target, anchor_root, args):
    """Exactly 5 facet lines in order: prd, ux, architecture, testing, roadmap."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    facet_lines = _status_facet_lines(_read(f))
    expected = ["prd", "ux", "architecture", "testing", "roadmap"]
    if len(facet_lines) != 5:
        return "fail", f"expected 5 facets, found {len(facet_lines)}"
    names = [ln.split("::")[0].strip() for ln in facet_lines]
    if names != expected:
        return "fail", f"expected order {expected}, got {names}"
    return "pass", ""


def chk_status_cell_values_valid(target, anchor_root, args):
    """Each facet cell value is in the ladder: none/MVP-agent/MVP-user/Full-agent/Full-user."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    valid = {"none", "MVP-agent", "MVP-user", "Full-agent", "Full-user"}
    bad = []
    for ln in _status_facet_lines(_read(f)):
        parts = ln.split("::", 1)[1].strip().split()
        if parts and parts[0] not in valid:
            bad.append((ln.split("::")[0].strip(), parts[0]))
    if bad:
        return "fail", f"invalid cells: {bad}"
    return "pass", ""


def chk_status_nonone_cells_dated(target, anchor_root, args):
    """Every non-'none' facet cell includes a (YYYY-MM-DD) date."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    missing = []
    for ln in _status_facet_lines(_read(f)):
        parts = ln.split("::", 1)[1].strip().split()
        if parts and parts[0] != "none" and not re.search(r"\(\d{4}-\d{2}-\d{2}\)", ln):
            missing.append(ln.split("::")[0].strip())
    if missing:
        return "fail", f"non-none cells missing dates: {missing}"
    return "pass", ""


def chk_status_user_cells_noted(target, anchor_root, args):
    """Every *-user cell includes ' — <note>'."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    missing = []
    for ln in _status_facet_lines(_read(f)):
        parts = ln.split("::", 1)[1].strip().split()
        if parts and parts[0].endswith("-user") and not re.search(r" — .+", ln):
            missing.append(ln.split("::")[0].strip())
    if missing:
        return "fail", f"*-user cells missing notes: {missing}"
    return "pass", ""


def chk_status_track_dispatch_linked(target, anchor_root, args):
    """{slug} Track.md contains a [[{slug} Status]] link."""
    slug = _anchor_slug(anchor_root)
    track = anchor_root / f"{slug} Track.md"
    if not track.is_file():
        return "error", f"no {track.name}"
    pattern = rf"\[\[{re.escape(slug)} Status(?:\]\]|\|)"
    if re.search(pattern, _read(track), re.IGNORECASE):
        return "pass", ""
    return "fail", f"no [[{slug} Status]] link found"


# -- R-testing -----------------------------------------------------------------

def chk_testing_filename_correct(target, anchor_root, args):
    """File named {slug} Testing.md for this anchor's slug (or an ancestor's —
    doc-mode passes the file's parent as anchor_root); no legacy
    {slug} Testing Strategy.md alongside."""
    if not target.is_file():
        return "error", "target is not a file"
    stem = target.stem
    if not stem.endswith(" Testing"):
        return "fail", f"file should be '<slug> Testing.md' not '{target.name}'"
    slug = stem[: -len(" Testing")]
    slugs = _ancestor_anchor_slugs(anchor_root)
    if slug not in slugs:
        return "fail", f"'{slug}' is not this anchor's slug (expected one of {sorted(set(slugs))})"
    legacy = target.parent / f"{slug} Testing Strategy.md"
    if legacy.is_file():
        return "fail", f"legacy file {legacy.name} exists alongside {target.name}"
    return "pass", ""


def _section_body(lines, header_re, stop_re=r"^ {0,3}## ", structure=False):
    """Lines under the first heading matching header_re, up to next stop_re.

    Boundaries are always found on the FENCE-STRIPPED copy: finding them on raw
    text let a fenced `## Examples` — 110 vault docs carry one — close a section
    early, so the checker judged a fragment.

    `structure` picks which copy comes BACK, and every caller must choose. The
    two halves answer different questions and neither default is safe for the
    other (T103a):

    - `structure=False` — the ORIGINAL lines. For callers asking *is there
      content here* / *what does it say*. A section whose body IS a code block
      (`## Architecture Diagram`, a `## Tests` body) must not read as empty.
    - `structure=True` — the fence-blanked lines. For callers asking *what
      structure does this section declare* — an H3, a table row, a bullet name,
      an image embed. A fenced one of those is a picture of the thing, and the
      docs most likely to show the picture are the docs these rules govern.

    The flag exists because the re-strip it replaces was got wrong three times.
    `_bold_item_names` and `_subsystems_table_rows` (T102) each re-derived the
    stripped copy at the call site, with a paragraph apiece explaining why;
    `chk_tests_table_present` and `chk_architecture_diagram_section_with_embed`
    did not, and a fenced example table / a fenced `![[diagram.svg]]` satisfied
    both rules outright. One seam, decided once per caller.
    """
    marks = _strip_fenced("\n".join(lines)).splitlines()
    # `_strip_fenced` blanks fenced lines, and `"\n".join(...).splitlines()` then
    # DROPS the trailing empties — so on any document whose last lines are inside a
    # fence, `marks` comes back shorter than `lines`. The scan below walks `lines`
    # while indexing `marks`, and raised IndexError on exactly those docs: the
    # checker returned `("error", "IndexError: ...")` instead of a verdict, so every
    # `_section_body` consumer silently stopped evaluating on a doc that ends in a
    # code block — a common shape, and a fail-open one. Padding rather than
    # shortening the loop is deliberate: the dropped lines are real content that a
    # section may legitimately contain, and truncating would end the section early.
    marks += [""] * (len(lines) - len(marks))
    start = None
    for i, ln in enumerate(marks):
        if re.match(header_re, ln):
            start = i
            break
    if start is None:
        return None
    src = marks if structure else lines
    out = []
    for i in range(start + 1, len(lines)):
        if re.match(stop_re, marks[i]):
            break
        out.append(src[i])
    return out


def chk_strategy_subsections_present_ordered(target, anchor_root, args):
    """## Strategy has 4 H3s in order: Test Kinds, Completeness Targets, Responsibilities, Tier Mapping."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    # structure=True: the four H3s are the thing being required, so a fenced
    # sample listing them satisfied the rule on a doc that declares none.
    body = _section_body(lines, r"^## Strategy\b", structure=True)
    if body is None:
        return "fail", "no ## Strategy section"
    required = ["### Test Kinds", "### Completeness Targets", "### Responsibilities", "### Tier Mapping"]
    found = [req for ln in body for req in required if ln.strip().startswith(req)]
    if found != required:
        missing = [r for r in required if r not in found]
        if missing:
            return "fail", "missing: " + ", ".join(missing)
        return "fail", f"subsections out of order: found {found}"
    return "pass", ""


def chk_proposed_tests_structure(target, anchor_root, args):
    """## Proposed Tests has H3 subsections, each with a markdown table."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Every boundary this reads — the section H2, the H3s, the `|` rows — comes off
    # the fence-stripped copy, for the reason `_section_body` already documents: a
    # Testing doc that SHOWS a proposed-tests table in a fence would otherwise have
    # that sample counted as the section's real content, and the H3 it sits under
    # judged complete on a table it doesn't have.
    lines = _strip_fenced(_read(f)).splitlines()
    pt_start = None
    for i, ln in enumerate(lines):
        if re.match(r"^## Proposed Tests\b", ln):
            pt_start = i
            break
    if pt_start is None:
        return "fail", "no ## Proposed Tests section"
    h3s = []
    for i in range(pt_start + 1, len(lines)):
        if re.match(r"^## ", lines[i]):
            break
        if re.match(r"^### ", lines[i]):
            h3s.append((i, lines[i]))
    if not h3s:
        return "fail", "no H3 subsections under ## Proposed Tests"
    for h3_idx, h3_ln in h3s:
        has_table = False
        for j in range(h3_idx + 1, len(lines)):
            if re.match(r"^### ", lines[j]) or re.match(r"^## ", lines[j]):
                break
            if re.match(r"^\|", lines[j]):
                has_table = True
                break
        if not has_table:
            return "fail", f"H3 section {h3_ln.strip()!r} has no markdown table"
    return "pass", ""


def _bold_item_names(lines, header_re):
    """**Name** at start of bullets under a section heading.

    structure=True: a bullet name is never code, so a `- **Sample Kind**` shown
    inside a fence would be harvested as a declared kind.
    """
    body = _section_body(lines, header_re, stop_re=r"^### ", structure=True)
    names = set()
    if body:
        for ln in body:
            m = re.match(r"^-\s*\*\*([^*]+)\*\*", ln)
            if m:
                names.add(m.group(1).strip())
    return names


def chk_proposed_tests_subset_of_strategy(target, anchor_root, args):
    """Every Proposed Tests H3 kind is declared in Strategy ### Test Kinds."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _strip_fenced(_read(f)).splitlines()
    test_kinds = _bold_item_names(lines, r"^### Test Kinds\b")
    pt_start = None
    proposed = set()
    for i, ln in enumerate(lines):
        if re.match(r"^## Proposed Tests\b", ln):
            pt_start = i
            break
    if pt_start is not None:
        for i in range(pt_start + 1, len(lines)):
            if re.match(r"^## ", lines[i]):
                break
            if re.match(r"^### ", lines[i]):
                proposed.add(lines[i].replace("### ", "").strip())
    unknown = proposed - test_kinds
    if unknown:
        return "fail", "Proposed Tests kinds not in Strategy: " + ", ".join(sorted(unknown))
    return "pass", ""


def chk_all_test_kinds_have_targets(target, anchor_root, args):
    """Every ### Test Kinds entry has a ### Completeness Targets entry."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    kinds = _bold_item_names(lines, r"^### Test Kinds\b")
    targets = _bold_item_names(lines, r"^### Completeness Targets\b")
    missing = kinds - targets
    if missing:
        return "fail", "Test kinds without targets: " + ", ".join(sorted(missing))
    return "pass", ""


def _proposed_tests_rows(lines):
    """Data-row lines under ## Proposed Tests — every table in the section, each
    with its own header and separator dropped.

    Stripped here rather than at the two callsites so neither can be fixed and the
    other left behind — the exact way the fence defect stayed alive across three
    F296 presses (T099). Header/separator identification is POSITIONAL now
    (`_table_blocks` / `_table_data_rows`): the lexical form dropped a legitimate
    all-placeholder row `| - | - | - |` as a separator and took the real row above
    it along, because the row a separator follows is treated as a header.
    """
    lines = _strip_fenced("\n".join(lines)).splitlines()
    pt_start = None
    for i, ln in enumerate(lines):
        if re.match(r"^ {0,3}## Proposed Tests\b", ln):
            pt_start = i
            break
    if pt_start is None:
        return None
    body = []
    for i in range(pt_start + 1, len(lines)):
        if _H2_RE.match(lines[i]):
            break
        body.append(lines[i])
    return [ln for block in _table_blocks(body) for ln in _table_data_rows(block)]


def chk_proposed_tests_rows_have_spec(target, anchor_root, args):
    """Every Proposed Tests table row has a non-empty last (Spec) cell."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _proposed_tests_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Proposed Tests section"
    for ln in rows:
        cells = _row_cells(ln)
        if not cells:
            continue
        # No lexical separator guard here. `_proposed_tests_rows` drops the header
        # and separator POSITIONALLY now, and the guard that used to sit here made
        # the very next line unreachable: a `-` Spec cell matched `^[\s:-]+$` and
        # was skipped as a separator — which is the exact failure this rule exists
        # to catch, silently declared out of scope by its own guard.
        if not cells[-1] or cells[-1] == "-":
            return "fail", f"row has empty Spec cell: {ln[:60]}"
    return "pass", ""


def chk_spec_cells_format_valid(target, anchor_root, args):
    """Proposed Tests Spec cells are [[wiki-link]] or [bracket], not inline prose."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _proposed_tests_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Proposed Tests section"
    for ln in rows:
        cells = _row_cells(ln)
        if not cells:
            continue
        spec = cells[-1]
        # An unfilled placeholder is the SIBLING rule's business
        # (`proposed_tests_rows_have_spec` fails it); separators are already gone
        # positionally, so no lexical test is needed for them here either.
        if not spec or spec == "-":
            continue
        if not re.match(r"^\[\[.+\]\]$", spec) and not re.match(r"^\[[^\]]+\]$", spec):
            return "fail", f"Spec cell invalid (not wiki-link or bracket): {spec}"
    return "pass", ""


def chk_status_field_valid(target, anchor_root, args):
    """Frontmatter status in drafting|in-review|accepted — the spec'd form is the
    `status::` dataview field (R-testing-08); plain `status:` also accepted."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    fm = _frontmatter(_read(f))
    if fm is None:
        return "fail", "no YAML frontmatter"
    m = re.search(r"^status\s*::?\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return "fail", "frontmatter missing status:: field"
    value = m.group(1).strip().strip("\"'")
    if value not in ("drafting", "in-review", "accepted"):
        return "fail", f"status value {value!r} not valid"
    return "pass", ""


# -- R-architecture (T015, 2026-07-13) ------------------------------------------

def _h2_titles(lines):
    """(line_idx, title) for every H2 heading, in document order — fences skipped.

    Indices are into the ORIGINAL `lines`, since callers report them. The vault has
    six genuinely indented H2s (` ## TODO`, `   ## old`) and no multi-space form, so
    the indent allowance is the small half here; the fence is the large one."""
    marks = _strip_fenced("\n".join(lines)).splitlines()
    return [(i, m.group(1).strip()) for i, ln in enumerate(marks)
            for m in [_H2_RE.match(ln)] if m]


def _ancestor_anchor_roots(anchor_root: Path, cap: int = 4) -> list[Path]:
    """Enclosing dirs carrying `.anchor`, nearest first (max `cap`) — nested
    anchors (`{slug} Design/`, `{slug} Architecture/`) sit below the root whose
    tree holds the docs a link resolves to. Bounded at REPO_ROOT when inside
    the repo. Falls back to [anchor_root] when no `.anchor` exists up-tree."""
    out: list[Path] = []
    cur = anchor_root
    try:
        repo = REPO_ROOT.resolve()
    except OSError:
        repo = None
    while len(out) < cap:
        if (cur / ".anchor").is_file():
            out.append(cur)
        if cur.parent == cur or (repo is not None and cur.resolve() == repo):
            break
        cur = cur.parent
    return out or [anchor_root]


def _real_anchor_root(anchor_root: Path) -> Path:
    """Nearest enclosing dir carrying `.anchor` — doc-mode passes the file's
    parent as anchor_root, which for a `{slug} Design/` doc is below the root."""
    return _ancestor_anchor_roots(anchor_root, cap=1)[0]


def _resolve_doc(name: str, anchor_root: Path) -> Path | None:
    """First `{name}.md` found searching the ancestor anchor roots nearest-first
    (wiki-links resolve by basename; a subsystem doc may live in an outer root)."""
    base = name.split("/")[-1]
    for root in _ancestor_anchor_roots(anchor_root):
        try:
            hit = next(iter(root.rglob(f"{base}.md")), None)
        except (OSError, ValueError):
            hit = None
        if hit is not None:
            return hit
    return None


def chk_architecture_filename_correct(target, anchor_root, args):
    """R-architecture-01: entry-point doc is `{slug} Architecture.md` in
    `{slug} Design/` — single file, or folder-doc form `{slug} Architecture/`.
    Slug comes from the basename and must be an (ancestor) anchor slug."""
    if not target.is_file():
        return "error", "target is not a file"
    stem = target.stem
    if not stem.endswith(" Architecture"):
        return "fail", f"file should be '<slug> Architecture.md' not '{target.name}'"
    slug = stem[: -len(" Architecture")]
    if slug not in _ancestor_anchor_slugs(anchor_root):
        return "fail", f"'{slug}' is not this anchor's slug"
    design = f"{slug} Design"
    parent = target.parent
    if parent.name == design:
        return "pass", ""
    if parent.name == f"{slug} Architecture" and parent.parent.name == design:
        return "pass", "folder-doc form"
    if (parent / ".anchor").is_file():
        return "fail", f"anchor-root placement — migrate into {design}/"
    return "fail", f"lives in '{parent.name}/', expected '{design}/'"


def chk_architecture_h1_present(target, anchor_root, args):
    """R-architecture-02: first heading is a single clean `# {basename}` H1 —
    no `[[wiki]] ·` decoration."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    fm = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    body = text[fm.end():] if fm else text
    expected = f"# {f.stem}"
    # Unlike its neighbour `chk_h1_after_frontmatter`, which matches ANY non-blank
    # line and so trips on the fence OPENER before ever reaching its body, this one
    # matches only heading lines — it steps straight over the opener and reads the
    # first heading INSIDE the fence as the document's first heading. An
    # Architecture doc opening with a fenced `# Example` layout sketch fails on a
    # heading that is a sample, and the reported "expected" name is the right one,
    # which makes the finding read as a genuine mismatch.
    for ln in _strip_fenced(body).splitlines():
        if re.match(r"^#{1,6}\s", ln):
            if ln.strip() == expected:
                return "pass", ""
            return "fail", f"first heading is {ln.strip()!r}, expected {expected!r}"
    return "fail", "no markdown heading found"


def chk_overview_section_present(target, anchor_root, args):
    """Shared R-architecture-03 / R-testing-11: `## Overview` H2 present with a
    non-empty body before the next H2."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    body = _section_body(_read(f).splitlines(), r"^## Overview\s*$")
    if body is None:
        return "fail", "no ## Overview H2"
    if not any(ln.strip() for ln in body):
        return "fail", "## Overview section is empty"
    return "pass", ""


_IMG_EMBED_RE = re.compile(r"!\[\[.+?\]\]|!\[[^\]]*\]\([^)]+\)")


def chk_architecture_diagram_section_with_embed(target, anchor_root, args):
    """R-architecture-04: `## Architecture diagram` H2 with >= 1 image embed."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # structure=True: an embed is exactly what this rule requires, so a fenced
    # `![[example.svg]]` showing the reader HOW to embed one satisfied the rule on
    # a page whose diagram is still to be drawn.
    body = _section_body(_read(f).splitlines(), r"^## Architecture [Dd]iagram\s*$",
                         structure=True)
    if body is None:
        return "fail", "no ## Architecture diagram H2"
    if not any(_IMG_EMBED_RE.search(ln) for ln in body):
        return "fail", "## Architecture diagram has no image embed"
    return "pass", ""


_BOX_DRAWING_CHARS = "┌┐└┘├┤┬┴┼│─╔╗╚╝╠╣║═▲▼◄►"


def chk_no_ascii_diagram(target, anchor_root, args):
    """R-architecture-05: no fenced code block draws a box/arrow ASCII diagram
    (>= 3 box-drawing glyphs inside a fence = a diagram, not stray characters)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    fenced = _fenced_mask(text)
    hits, first_line = 0, None
    for i, ln in enumerate(text.splitlines(), 1):
        # Marker lines carry no box-drawing glyphs, so counting them costs nothing
        # and the whole toggle collapses to the shared mask (T099).
        if fenced[i - 1]:
            n = sum(ln.count(c) for c in _BOX_DRAWING_CHARS)
            if n:
                hits += n
                first_line = first_line or i
    if hits >= 3:
        return "fail", f"fenced ASCII diagram (box-drawing glyphs from line {first_line})"
    return "pass", ""


def _subsystems_table_rows(lines):
    """Data rows of the table under `## Subsystems` (header + separator skipped).
    None = no section; [] = section without a usable table."""
    # structure=True: a fenced `| [[No-Such-Doc]] | example |` is an illustration,
    # and harvesting it made `chk_subsystem_link_convention` report a missing
    # subsystem doc against the page's own example.
    body = _section_body(lines, r"^## Subsystems\s*$", structure=True)
    if body is None:
        return None
    # Blocks, not a flat row list (T103b): the subsystems table is the FIRST table
    # in the section, and the blanket `rows[2:]` this replaces skipped the header
    # POSITIONALLY across every table at once — so a second small table below
    # contributed its own header and separator as data rows.
    blocks = _table_blocks(body)
    return _table_data_rows(blocks[0]) if blocks else []


def chk_subsystems_section_present(target, anchor_root, args):
    """R-architecture-06: `## Subsystems` H2 with a table of >= 1 data row."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _subsystems_table_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Subsystems H2"
    if not rows:
        return "fail", "## Subsystems has no table with data rows"
    return "pass", ""


def chk_spine_order_correct(target, anchor_root, args):
    """R-architecture-07: first three H2s are Overview -> Architecture diagram ->
    Subsystems, before any supporting section."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    titles = [t for _, t in _h2_titles(_read(f).splitlines())]
    spine = ["overview", "architecture diagram", "subsystems"]
    got = titles[:3]
    if [t.lower() for t in got] == spine:
        return "pass", ""
    return "fail", f"first H2s are {got}, expected Overview / Architecture diagram / Subsystems"


_SUBSYS_CELL_RE = re.compile(
    r"\[\[([^\]\\|#]+)(?:[\\|#][^\]]*)?\]\]"   # [[target]] / [[target\|alias]] / [[target#sec]]
    r"|(?<!\[)\[([^\[\]]+)\](?!\()")           # [single-bracket placeholder]


def _subsystem_names(rows):
    """(name, is_wikilink) per table data row's first cell, bracketed entries only."""
    out = []
    for ln in rows:
        cells = _row_cells(ln)
        cell = cells[0] if cells else ""
        m = _SUBSYS_CELL_RE.search(cell)
        if m:
            out.append(((m.group(1) or m.group(2)).strip(), bool(m.group(1))))
    return out


def chk_subsystem_kebab_naming(target, anchor_root, args):
    """R-architecture-08: Design-resident subsystem docs use kebab
    `{slug}-{Subsystem}` form. A `[[link]]` resolving to a doc OUTSIDE any
    `* Design/` folder is a project-tree component/group page referenced by its
    true name — exempt. `[single-bracket]` placeholders are exempt (their home,
    and so their naming, is decided at authoring time)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _subsystems_table_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Subsystems H2"
    stem = f.stem
    slug = (stem[: -len(" Architecture")] if stem.endswith(" Architecture")
            else _anchor_slug(_real_anchor_root(anchor_root)))
    bad = []
    for n, is_link in _subsystem_names(rows):
        if re.fullmatch(rf"{re.escape(slug)}-[A-Za-z0-9-]+", n):
            continue
        if not is_link:
            continue  # placeholder — naming decided when the doc is authored
        hit = _resolve_doc(n, anchor_root)
        if hit is not None and not any(p.name.endswith(" Design") for p in hit.parents):
            continue  # real project-tree component/group page — true name is right
        bad.append(n)
    if bad:
        return "fail", "non-kebab Design-resident subsystem names: " + ", ".join(bad[:5])
    return "pass", ""


def chk_subsystem_link_convention(target, anchor_root, args):
    """R-architecture-09: `[[double-bracket]]` subsystem entries resolve to an
    existing doc under the anchor; `[single-bracket]` placeholders are exempt."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _subsystems_table_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Subsystems H2"
    missing = []
    for name, is_link in _subsystem_names(rows):
        if not is_link:
            continue
        if _resolve_doc(name, anchor_root) is None:
            missing.append(name)
    if missing:
        return "fail", "missing subsystem docs: " + ", ".join(missing[:5])
    return "pass", ""


# -- R-testing-12 (T015, 2026-07-13) ---------------------------------------------

def chk_tests_table_present(target, anchor_root, args):
    """R-testing-12: `## Tests` H2 before `## Overview`, holding a coverage table
    whose kind cells are [[wiki-links]]."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    titles = _h2_titles(lines)
    tests_i = next((i for i, t in titles if t == "Tests"), None)
    if tests_i is None:
        return "fail", "no ## Tests H2"
    over_i = next((i for i, t in titles if t == "Overview"), None)
    if over_i is not None and tests_i > over_i:
        return "fail", "## Tests appears after ## Overview (must precede it)"
    # structure=True: a `## Tests` section that SHOWS what a coverage table looks
    # like put that fenced sample first, so `blocks[0]` was the picture and the
    # real table below it was never inspected.
    body = _section_body(lines, r"^ {0,3}## Tests\s*$", structure=True) or []
    # The COVERAGE table is the first table in the section. A second table below it
    # (a legend, a note) is not coverage, and flattening the section into one row
    # list made its header and separator read as kind rows missing a wiki-link.
    blocks = _table_blocks(body)
    data = _table_data_rows(blocks[0]) if blocks else []
    if not data:
        return "fail", "## Tests has no table with data rows"
    nolink = sum(1 for ln in data if "[[" not in (_row_cells(ln) or [""])[0])
    if nolink:
        return "fail", f"{nolink} kind row(s) without a [[wiki-link]] first cell"
    return "pass", ""


# -- R-anchor-page (extras) ----------------------------------------------------

def chk_no_track_row_if_ecosystem_traits(target, anchor_root, args):
    """If .anchor traits include skill/facet/discipline/example, assert no Track row."""
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return "error", "no .anchor file"
    traits = _read(dot)
    if not any(t in traits for t in ("skill", "facet", "discipline", "example")):
        return "pass", "not an ecosystem anchor"
    f = _as_file(target, anchor_root)
    if f is None:
        # No entry page. That IS a fault, and it is R-anchor-page-02's — its
        # checker's first branch reports it by name. Raising it here as an
        # `error` says the CHECKER malfunctioned, on 20 DAS-repo skill and
        # ruleset anchors that have no `{slug}.md` at all (T212). A page that
        # does not exist cannot carry a track row, so the honest verdict for
        # THIS rule is pass, with the real fault left to the rule that owns it.
        return "pass", "no entry page — R-anchor-page-02 reports that"
    # Fence-stripped (T103a): the docs that explain why these anchors carry no Track
    # row are the ones most likely to SHOW a Track row in a fenced example.
    if re.search(r"\|\s*\[?\[?Track\]?\]?\s*\|", _strip_fenced(_read(f))):
        return "fail", "Track row present on ecosystem anchor"
    return "pass", ""


def chk_file_path_matches_prd_locations(target, anchor_root, args):
    """PRD at {slug} Design/{slug} PRD.md or {slug} Design/{slug} PRD/{slug} PRD.md."""
    if not target.is_file():
        return "pass", "not a file"
    proj = target.stem[:-len(" PRD")] if target.stem.endswith(" PRD") else target.stem
    parent, grand = target.parent.name, target.parent.parent.name
    in_design_single = (parent == f"{proj} Design")                            # …/{proj} Design/{proj} PRD.md
    in_design_folder = (parent == f"{proj} PRD" and grand == f"{proj} Design")  # …/{proj} Design/{proj} PRD/…
    if in_design_single or in_design_folder:
        return "pass", ""
    return "fail", f"PRD {target.name!r} not under a '{proj} Design/' folder"


def chk_h1_no_frontmatter(target, anchor_root, args):
    """No YAML frontmatter; H1 is the first non-blank line.
    Consolidates body_only_no_frontmatter (R-prd) + h1_no_frontmatter (R-completed-roadmap)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    if text.lstrip().startswith("---"):
        return "fail", "YAML frontmatter present"
    for ln in text.splitlines():
        if ln.strip():
            if _H1_RE.match(ln):
                return "pass", ""
            return "fail", f"first non-blank line is not H1: {ln!r}"
    return "fail", "file is empty or all blank"


def _h2_headings(text):
    """Titles only — the text view of `_h2_titles`, sharing its one definition."""
    return [t for _, t in _h2_titles(text.splitlines())]


def chk_required_sections_in_order(target, anchor_root, args):
    """Required H2s present and in order. Args override defaults (PRD set)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    required = args if args else ["Overview", "Goals", "Non-Goals", "User Stories"]
    h2s = _h2_headings(_read(f))
    missing = [r for r in required if r not in h2s]
    if missing:
        return "fail", "missing required sections: " + ", ".join(missing)
    indices = [h2s.index(r) for r in required]
    if indices != sorted(indices):
        return "fail", f"required sections not in order: {h2s}"
    return "pass", ""


def chk_queries_location(target, anchor_root, args):
    """R-query-01: `{X} queries.md` lives in `{X} Track/` (or a sub-folder
    rooted there) — the prefix X is taken from the basename itself, so the
    check is sub-anchor-safe (a Track folder carrying its own `.anchor` still
    passes)."""
    if not target.is_file():
        return "pass", "not a file"
    name = target.name
    if not name.endswith(" queries.md"):
        return "pass", "not a queries file"
    x = name[: -len(" queries.md")]
    want = f"{x} Track"
    for parent in target.parents:
        if parent.name == want:
            return "pass", ""
        if (parent / ".anchor").is_file() and parent.name != want:
            break  # left the owning anchor without meeting the Track folder
    return "fail", (f"`{name}` sits in `{target.parent.name}/` — it belongs at "
                    f"`{want}/{name}`")


_QUERIES_BANNER_RE = re.compile(
    r"^# \[(?:U\+A|U|A|G|\?|-)\]  "                    # tag + two spaces
    r"(?:\[\[[^\]]+\]\]|[^\[\]|]+?)  -  "              # wiki-linked or plain label
    r"Ready \d+    User \d+(?:    Inbox \d+)?   \|   "  # zone 1 — classes
                                                       # (Inbox only when N>0)
    r"Now \d+    Next \d+    Later \d+   \|   "         # zone 2 — horizons
    r"Parked \d+    Waiting \d+    Icebox \d+"          # zone 3 — the quiet group
    r"(?:    \{\d+\})?\s*$"                            # optional QFix residual count
)


def chk_queries_banner_form(target, anchor_root, args):
    """R-query-16: the H1 is the status banner in the locked form the renderer
    emits (`queries-render.py derive_banner`) — three zones ordered by
    attention, `Ready`/`User` | `Now`/`Next`/`Later` | `Parked`/`Waiting`/
    `Icebox` — with the exact spacing (two spaces around `-`, four between
    counts, three around each `|`), slug wiki-linked or plain, optional
    trailing `    {N}` residual count. The Q.md section scan keys off this
    exact form.

    THIS CHECK MOVES WITH THE FORMAT STRING, IN THE SAME PASS. It has now
    lagged once: F260 renamed the headline pair to `Runnable`/`User` and this
    check kept enforcing the pre-F260 `Ready`/`Questions` pair for the whole
    interval, so it failed on 26 of 32 live queries files — every page the
    renderer produced — and fired as an on-write warning against correct
    output. A lock that disagrees with the thing it locks is worse than no
    lock, because it trains readers to ignore the warning.

    F305 (2026-08-07) replaced the two zones with three: `Runnable` reverted to
    `Ready`, `Verify` left the horizon group for the new `Parked` class, and
    `Waiting` gained a count it never had. Accepting BOTH forms was rejected
    again, on the same grounds as last time — no legacy accumulation — but the
    resolution differs: rather than let pages self-correct whenever they next
    render, every anchor was re-rendered in the same pass, so no page sits in
    the failing interval at all.

    T131 leg 2 (2026-08-08) added an OPTIONAL `    Inbox N` to zone 1, after
    `User`. Optional is not legacy accumulation here and the distinction is
    load-bearing: the renderer emits the field only when N > 0, so `Inbox` is
    absent and present in exactly the cases the format function makes it absent
    and present. There is one form, with a conditional field — not two forms
    kept alive side by side. That is also why this edit needed no re-render:
    with nothing pending vault-wide, every live banner was already correct."""
    if not target.is_file():
        return "pass", "not a file"
    if not target.name.endswith(" queries.md"):
        return "pass", "not a queries file"
    # The banner is machine-rendered, but this check exists precisely to catch a
    # hand-mangled file — the population where a stray fenced `# ` line above the
    # banner is most likely. Locate the H1 the way every other checker now does,
    # then match the RAW line, since the banner's exact spacing is the thing under
    # test and `_head_h1` returns text with the indent and closing hashes removed.
    text = _read(target)
    idx, _ = _head_h1(text)
    if idx is None:
        return "fail", "no H1 — a queries file opens with the status-banner H1"
    raw = text.splitlines()[idx]
    if _QUERIES_BANNER_RE.match(raw):
        return "pass", ""
    return "fail", (f"H1 (line {idx + 1}) is not the locked status-banner "
                    "form — expected `# [<TAG>]  <slug>  -  Ready N    "
                    "User N   |   Now N    Next N    Later N   |   "
                    "Parked N    Waiting N    Icebox N` "
                    "(re-render via queries-render.py)")


def chk_queries_catchall_links(target, anchor_root, args):
    """R-query-09: each top-level `## Questions` bullet carries a wiki-link
    whose VISIBLE token is a work-item handle — `F<n>` / `T<n>` / `M-…` /
    `R-…` (optionally `… Q<m>`) — clickable to the concrete background, never
    a free-text restatement."""
    if not target.is_file():
        return "pass", "not a file"
    handle = re.compile(r"^(?:[FT]\d+|[MR]-[\w.-]+)(\s+Q\d+)?\b")
    in_q = False
    bad = []
    # Fence-stripped (T103a): a fenced `## Questions` sample opened the section and
    # every fenced bullet under it was judged as a live catch-all entry.
    for ln, raw in enumerate(_strip_fenced(_read(target)).splitlines(), 1):
        if raw.startswith("## "):
            in_q = raw.strip() == "## Questions"
            continue
        if not in_q or not raw.startswith("- "):
            continue
        ok = False
        for m in re.finditer(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", raw):
            visible = (m.group(2) or m.group(1)).strip()
            if handle.match(visible):
                ok = True
                break
        if not ok:
            bad.append(f"line {ln}")
    if bad:
        return "fail", ("Questions bullet(s) without a handle-visible wiki-link "
                        "(`F<n>`/`T<n>`/`M-…`) — " + ", ".join(bad[:5]))
    return "pass", ""


def chk_queries_sections_subsequence(target, anchor_root, args):
    """R-query-03: the queries H2s are a subsequence of the allowed sections, in
    order, with no foreign H2 and no repeats. Empty sections are omitted, so a
    subset is fine — only membership, order, and uniqueness are enforced.

    `Other` (F284) closes the list: it is the catch-all that makes the render
    total over the frontier, so it must be admissible here or this rule would
    forbid the very section that guarantees no row is lost. It sorts last
    because it holds the rows whose state is unclear — never above the work
    whose state IS clear.

    The list itself is F283's order (2026-07-30). `Agent Resolutions` and
    `Immediate Questions` are gone — neither had been rendered since F231, so the
    rule was describing a file that no longer existed. `Blockers` (computed —
    rows some other row is blocked on) and `Blocked` (the ledger of
    `[Blocked <handle>]` + `[Waiting]`) replace them.

    `User` (F259) sits between `Verifications` and `Other` because that is where
    `queries-render.py` has emitted it since F259 landed — this rule simply never
    caught up, so every render of an anchor holding `[User]` rows fired a warden
    R-query-03 warning against a section the renderer is required to write. Six
    anchors were in that state when it was noticed (T141). The placement is not a
    judgment call being made here: the renderer already made it, and a rule that
    contradicts the file's only writer is the side that is wrong."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    allowed = args if args else ["Blockers", "Ready", "Questions", "Blocked",
                                 "Verifications", "User", "Other"]
    h2s = _h2_headings(_read(f))
    foreign = [h for h in h2s if h not in allowed]
    if foreign:
        return "fail", "foreign H2 section(s): " + ", ".join(foreign)
    idx = [allowed.index(h) for h in h2s]
    if any(idx[i] >= idx[i + 1] for i in range(len(idx) - 1)):
        return "fail", f"sections out of order or repeated: {h2s}"
    return "pass", ""


def chk_user_stories_use_rid_numbering(target, anchor_root, args):
    """## User Stories H3s use US-{slug}-N: (inline form; folder form deferred)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Strip ONCE, up front (T103a). The scan below was already fence-aware, but the
    # folder-form escape above it read RAW text — so a fenced `| Stories |
    # [[X Stories]] |` illustrating the extracted form deferred the ENTIRE rule on a
    # PRD carrying its stories inline. A silent escape is the worst shape here: the
    # rule reports `pass` with a reason that sounds deliberate.
    text = _strip_fenced(_read(f))
    if re.search(r"\[\[\s*[^\]]*\s*Stories\s*\]\]", text):
        return "pass", "folder form (deferred to R-stories)"
    slug = _anchor_slug(anchor_root)
    in_stories = False
    ids = []
    # A PRD that documents the US-{slug}-N form by showing one — the likeliest place
    # in the vault for a sample `### US-EXAMPLE-1:` to appear — would otherwise have
    # its own illustration reported as a malformed user story.
    for ln in text.splitlines():
        if re.match(r"^## User Stories", ln):
            in_stories = True
            continue
        if in_stories and re.match(r"^## ", ln):
            break
        if in_stories:
            m = re.match(r"^### (US-[\w-]+): ", ln)
            if m:
                ids.append(m.group(1))
    bad = [s for s in ids if not re.match(rf"^US-{re.escape(slug)}-\d+$", s)]
    if bad:
        return "fail", f"user stories not in US-{slug}-N format: " + ", ".join(bad)
    return "pass", ""


def chk_no_legacy_open_questions_file(target, anchor_root, args):
    """No legacy {slug} Open Questions.md in {slug} Design/."""
    name = _anchor_slug(anchor_root)
    legacy = anchor_root / f"{name} Design" / f"{name} Open Questions.md"
    if legacy.is_file():
        return "fail", f"legacy Open Questions file exists: {legacy.relative_to(anchor_root)}"
    return "pass", ""


def chk_design_workflow_modern_names(target, anchor_root, args):
    """## Design Workflow uses modern phase names, not legacy ones."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # structure=True: this rule's subject is which phase NAMES the section uses, so
    # a doc that quotes the retired names in a fence to say they are retired was
    # failed for its own explanation — remediation: delete the explanation.
    body = _section_body(_read(f).splitlines(), r"^## Design Workflow", structure=True)
    if body is None:
        return "fail", "no ## Design Workflow section"
    workflow = "\n".join(body)
    old = [n for n in ("System Design", "Testing Strategy", "Principles")
           if re.search(re.escape(n), workflow, re.IGNORECASE)]
    if old:
        return "fail", "Design Workflow contains old phase names: " + ", ".join(old)
    if not any(n in workflow for n in ("Architecture", "Testing", "Decisions")):
        return "fail", "Design Workflow references no modern phase names"
    return "pass", ""


def chk_dispatch_table_stories_row(target, anchor_root, args):
    """Dispatch table has a Stories row displaying '{slug} Stories'."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _strip_fenced(_read(f))   # T103a — a fenced table is not THE dispatch table
    # project slug from the PRD's own basename ("HBR PRD.md" -> "HBR"), not the
    # (possibly nested) anchor folder name.
    base = Path(f).stem
    name = base[:-len(" PRD")] if base.endswith(" PRD") else anchor_root.name
    table = []
    in_table = False
    for ln in text.splitlines():
        if ln.lstrip().startswith("|"):
            in_table = True
            table.append(ln)
        elif in_table:
            break
    if not table:
        return "fail", "no dispatch table found"
    joined = "\n".join(table)
    if re.search(rf"\[\[{re.escape(name)} Stories", joined):
        return "pass", ""
    return "fail", f"no Stories row linking [[{name} Stories]]"


# -- R-doc-structure / R-stories ----------------------------------------------

def chk_no_dispatch_table(target, anchor_root, args):
    """Fail if the document carries a breadcrumb-masthead dispatch table.

    Used by R-stories-12: story files and the stories index are non-anchors and
    must not carry a dispatch table (per [[DAS Doc Structure]] R-doc-structure-02).
    Back-links belong in a ## Related / ## See also section, not a masthead."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Fence-stripped (T103a). This rule's remediation is "remove it", so a fenced
    # masthead sample read as live tells the author to delete their own
    # documentation — the most damaging shape a false finding can take here.
    # `_strip_fenced` blanks lines in place, so the reported line number survives.
    for i, ln in enumerate(_strip_fenced(_read(f)).splitlines(), 1):
        if re.search(r"^ {0,3}\|\s*-\[\[.+?\]\]-\s*\|", ln):
            return "fail", (f"non-anchor doc has a dispatch-masthead table (line {i}); "
                            "remove it — back-links go in ## Related")
    return "pass", "no dispatch table"


# -- R-progressive (conditional, multi-check document-layout rules) ------------

def _strip_fenced(text: str) -> str:
    """Blank out lines inside code fences — so a masthead/breadcrumb shown as
    a fenced *example* (in discipline/facet docs, the `md` skill, etc.) is not mistaken for
    a live one. Fence markers and their contents become empty lines.

    Pairing is delegated to `_FENCE_RE` (F296). The hand-rolled toggle this
    replaced knew only ``` — so a `~~~` example of a masthead was read as a LIVE
    masthead, and worse, an opening ``` inside a `~~~` block inverted the toggle
    for the rest of the file, hiding every real structure below it from six
    consumers at once. `_strip_fenced` differs from `_mask_code` in exactly one
    way that must be preserved: it blanks whole LINES to empty rather than to
    spaces, and does not touch inline spans. `_disclosure_units` hashes this
    output, so changing the blanking character would re-hash every fenced doc in
    the registry and fire a false drift re-ask on each one."""
    lines = text.splitlines()
    fenced = set()
    for m in _FENCE_RE.finditer(text):
        for i in range(text.count("\n", 0, m.start()),
                       text.count("\n", 0, m.end()) + 1):
            fenced.add(i)
    return "\n".join("" if i in fenced else ln for i, ln in enumerate(lines))


def _has_self_masthead(text: str, stem: str) -> bool:
    """True if the doc carries its OWN dispatch-masthead — a table row (outside a
    code fence) whose first cell is the self-referential breadcrumb cell
    `-[[<stem>]]-` (optionally aliased `-[[<stem>|alias]]-`), per
    [[DAS Dispatch Table]]. An example masthead shown in the body that links to a
    DIFFERENT page (`-[[Some Other Page]]-`) is not the doc's own masthead, so it
    does not count — this is what keeps facet/discipline docs that *illustrate*
    mastheads from false-positiving.

    Matched case-insensitively (T138 Q1 → A, 2026-08-08). Obsidian resolves a
    wiki-link's FILENAME case-insensitively through its own index, so `-[[Tink]]-`
    on `TINK.md` routes the reader correctly. A case-sensitive match here reads
    the masthead as ABSENT, which does not merely mis-report: every masthead rule
    that opens with `if not _has_self_masthead(...): return "pass"` then passes
    the doc vacuously."""
    pat = r"^\|\s*-\[\[\s*" + re.escape(stem) + r"\s*(\|[^\]]*)?\]\]-\s*\|"
    return bool(re.search(pat, _strip_fenced(text), re.MULTILINE | re.IGNORECASE))


def _has_breadcrumb_line(text: str) -> bool:
    """A `:>>` breadcrumb top-row is present (the non-anchor navigation form),
    outside any code fence."""
    return bool(re.search(r"^\s*:>>", _strip_fenced(text), re.MULTILINE))


def chk_dispatch_table_by_context(target, anchor_root, args):
    """A doc must never carry BOTH its own dispatch-masthead table AND a `:>>`
    breadcrumb — the two are *alternative* navigation forms, never combined: a
    self-masthead marks the page that IS a container (the anchor page); a `:>>`
    breadcrumb is the navigation on every other doc (per
    [[feedback_breadcrumb_vs_dispatch_table]]). The masthead considered is the
    doc's OWN self-referential `-[[<this doc>]]-` first cell — an example masthead
    in the body (linking to another page) is not the doc's masthead and is ignored.

    (The *presence* direction — which anchor pages are required to carry a masthead
    — depends on the anchor kind and is `R-anchor-page`'s kind-aware job, not
    asserted here: a per-file checker cannot reliably classify anchor-page-ness
    across the vault without false-positiving the many anchor pages whose folders
    carry no `.anchor` file.)"""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    if _has_self_masthead(text, f.stem) and _has_breadcrumb_line(text):
        return "fail", (f"{f.name} has BOTH its own dispatch-masthead table and a `:>>` "
                        "breadcrumb — a doc uses one navigation form (masthead = the container's "
                        "own page; `:>>` = every other doc), never both")
    return "pass", "single navigation form"


def _breadcrumb_h1_positions(lines):
    """(breadcrumb_idx, h1_idx) of the first `:>>` line and first H1, fences
    skipped; either may be None.

    The H1 half comes from `_head_h1`; only the breadcrumb scan is still local.
    The hand-rolled `in_fence` toggle this replaced was the F296 finding-1 shape
    verbatim — blind to `~~~`, and flipping parity on any ``` line, so an
    info-string opener INSIDE a block re-exposed the rest of the file."""
    bidx = None
    for i, ln in enumerate(_strip_fenced("\n".join(lines)).splitlines()):
        if ln.lstrip().startswith(":>>"):
            bidx = i
            break
    hidx = _head_h1("\n".join(lines))[0]
    return bidx, hidx


def chk_doc_top_order(target, anchor_root, args):
    """R-doc-structure-01 (top-matter subset): the doc has an H1, and a `:>>`
    breadcrumb — when present — sits DIRECTLY above it, zero blank lines between
    (per the 2026-06-27 breadcrumb-vs-dispatch ruling; live instance of the miss:
    the SKL Query PRD's breadcrumb below its H1, 2026-07-06). The rule's fuller
    ordering constraints (summary line, figure/table placement) are not yet
    mechanically judged — a vault sample showed them too noisy to enforce
    blindly; tighten by data, not ambition."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    bidx, hidx = _breadcrumb_h1_positions(lines)
    if hidx is None:
        # the ruleset's scope is authored docs "identified by a leading # H1";
        # `where:: always` can't express that, so the H1-less file is out of
        # scope here (H1 presence is its own rule where one applies)
        return "pass", "no H1 — out of scope"
    if bidx is None:
        return "pass", "no breadcrumb"
    if bidx > hidx:
        return "fail", f"`:>>` breadcrumb (line {bidx + 1}) sits BELOW the H1 (line {hidx + 1}) — it goes directly above, zero blank lines"
    if hidx - bidx != 1:
        return "fail", f"{hidx - bidx - 1} line(s) between the `:>>` breadcrumb (line {bidx + 1}) and the H1 (line {hidx + 1}) — zero blank lines allowed"
    return "pass", "breadcrumb directly above H1"


def _anchorness(f: Path) -> tuple[bool, str]:
    """(is_anchor_page, evidence) — the file is its folder's namesake page (in
    a folder that IS an anchor root), or a sibling `.anchor` declares its stem
    as the slug.

    F329 (2026-08-15) — a namesake alone no longer proves anchorhood: the
    folder-doc form (`X/X.md` with NO `.anchor` in the folder — folder-form
    backlogs, feature docs grown into folders) is a *document* in folder form,
    and demanding a masthead of it would be wrong. The `.anchor` marker is
    what separates the two, and it is the definition of an anchor root anyway.

    Same day, the marker test alone proved insufficient: HookAnchor's scanner
    auto-mints `.anchor` in EVERY namesake folder on its 10-minute rescan
    (observed re-minting 2 minutes after deletion), so "has `.anchor`" is true
    of every folder-doc within one scan cycle and the F329 exemption would be
    a no-op. The stronger discriminator is the file's own machine stamp: a
    namesake carrying `<!-- state:backlog -->` is a folder-form backlog — a
    state-owned document, never an anchor page — whatever the scanner minted
    beside it. Policy question (should the scanner skip these?) is filed with
    HA; this keeps DAS audits truthful in the meantime.
    """
    if f.stem == f.parent.name:
        if (f.parent / ".anchor").is_file():
            try:
                head = f.read_text(encoding="utf-8", errors="replace")[:2000]
            except OSError:
                head = ""
            if re.search(r"<!--\s*state:backlog\b", head):
                return False, ""
            return True, "folder namesake"
        return False, ""
    dot = f.parent / ".anchor"
    if dot.is_file():
        try:
            m = re.search(r"^slug:\s*(\S+)", dot.read_text(encoding="utf-8"), re.MULTILINE)
            if m and m.group(1) == f.stem:
                return True, ".anchor slug"
        except OSError:
            pass
    return False, ""


def chk_dispatch_table_iff_anchor(target, anchor_root, args):
    """R-doc-structure-02, the mechanically-judgeable subset: (a) a doc never
    carries BOTH its own masthead and a `:>>` breadcrumb line; (b) a provable
    anchor page (folder namesake or `.anchor`-declared slug) never carries a
    bare `:>>` line (its breadcrumb is the masthead's first cell); (c) a
    `.anchor`-declared anchor page carries a masthead. The converse direction —
    "non-anchor must not carry a masthead" — is NOT judged here: a 2026-07-06
    vault sweep false-positived 99 real anchor pages whose folder name differs
    from their stem (SKL.md in skill-docs/, DAS Facets.md in facets/, per-dossier
    sub-anchor pages); only scoped rules like R-stories-12 assert that
    direction, where the file kind is provable. Template files are skipped."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if any("Template" in part for part in f.parts):
        return "pass", "template — skipped"
    text = _read(f)
    is_anchor, evidence = _anchorness(f)
    has_masthead = _has_self_masthead(text, f.stem)
    has_crumb = _has_breadcrumb_line(text)
    if has_masthead and has_crumb:
        return "fail", f"{f.name} has BOTH its own dispatch-masthead and a `:>>` breadcrumb — one navigation form, never both"
    if is_anchor and has_crumb:
        return "fail", f"anchor page ({evidence}) has a bare `:>>` breadcrumb line — an anchor's breadcrumb is the masthead's first cell, never a `:>>` line"
    if is_anchor and evidence == ".anchor slug" and not has_masthead:
        return "fail", f"anchor page ({evidence}) carries no dispatch-masthead table"
    return "pass", "anchor page with masthead" if has_masthead else "single navigation form"


def chk_dispatch_area_row(target, anchor_root, args):
    """R-dispatch-table-09/-10 (arg: the area — Design / Track / …): on a doc
    with its own masthead, the <Area> row's LEFT cell is a link down to the
    `{stem} <Area>` sub-anchor — never a bare text label (the SKL Query miss:
    `| Design | [[Query PRD|PRD]] |`). And when a `{stem} <Area>/` folder exists
    (directly or one level down, e.g. `{stem} Docs/{stem} <Area>/`), the masthead
    must carry that row."""
    if not args:
        return "error", "dispatch_area_row needs an area arg (Design/Track/…)"
    area = args[0]
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    if not _has_self_masthead(text, f.stem):
        return "pass", "no self-masthead"
    stripped = _strip_fenced(text)
    sub = f"{f.stem} {area}"
    # bare text label in the left cell → always wrong (row leads with the link).
    # The label is commonly bolded (`| **Track** |`), which the original pattern
    # did not admit, so that row fell through to the has_row test and was
    # reported as a MISSING link — see the T136 message note below.
    if re.search(r"^\|\s*(?:\*\*|__|\*|_)?\s*" + re.escape(area)
                 + r"\s*(?:\*\*|__|\*|_)?\s*\|", stripped, re.MULTILINE):
        return "fail", (f"masthead row '{area}' leads with a text label — the LEFT cell is "
                        f"the sub-anchor link itself, `[[{sub}\\|{area}]]`, not a label with "
                        f"the link in the right-hand cell")
    # Case-insensitive per T138 Q1 → (A): the link resolves the way Obsidian
    # resolves it, so `[[Tink Track|Track]]` on `TINK.md` is a found row, not a
    # missing one. 98 masthead links vault-wide differ from their target's
    # on-disk case; every one of them routes a reader correctly, and reporting
    # them as absent is the phantom "row is missing" finding T136 half-fixed.
    has_row = bool(re.search(r"^\|\s*\[\[" + re.escape(sub) + r"\s*(\\\||\|)?[^\]]*\]\]",
                             stripped, re.MULTILINE | re.IGNORECASE))
    folder = (f.parent / sub).is_dir() or any(p.is_dir() for p in f.parent.glob(f"*/{sub}"))
    if folder and not has_row:
        # T136 — the message used to say the link was absent. When it is in fact
        # present in a right-hand cell, that sends the reader hunting for a
        # broken link that was never broken (three edit cycles, SCOUT 2026-08-05).
        # The requirement is about the CELL POSITION, so the message must be too.
        if re.search(r"\[\[" + re.escape(sub) + r"(\s*(\\\||\|)[^\]]*)?\]\]",
                     stripped, re.IGNORECASE):
            return "fail", (f"masthead links `[[{sub}]]`, but not from the LEFT cell of its own "
                            f"row — the {area} row leads with `[[{sub}\\|{area}]]` and enumerates "
                            f"the parts on the right")
        return "fail", f"{sub}/ exists but the masthead has no `[[{sub}\\|{area}]]` row"
    return "pass", "row links the sub-anchor" if has_row else f"no {area} facet"


def _masthead_rows(text, stem):
    """The contiguous run of table rows containing the doc's own `-[[stem]]-`
    breadcrumb cell — the masthead table, and nothing else in the doc."""
    lines = _strip_fenced(text).splitlines()
    pat = re.compile(r"^\|\s*-\[\[\s*" + re.escape(stem) + r"\s*(\|[^\]]*)?\]\]-\s*\|",
                     re.IGNORECASE)
    at = next((i for i, ln in enumerate(lines) if pat.match(ln)), None)
    if at is None:
        return []
    lo = at
    while lo > 0 and _is_table_row(lines[lo - 1]):
        lo -= 1
    hi = at + 1
    while hi < len(lines) and _is_table_row(lines[hi]):
        hi += 1
    return lines[lo:hi]


def chk_dispatch_link_case_drift(target, anchor_root, args):
    """R-dispatch-table-15 — a masthead link whose target exists beside the doc
    under a DIFFERENT case. Cosmetic, by ruling (T138 Q1 → A, 2026-08-08).

    98 of these exist vault-wide across ~40 anchors — [[SLUG]] 22, [[TINK]] 9,
    [[ASG]] 7 — and most have no rename anywhere in their history: `[[pp]]`→`PP`,
    `[[SCRatch]]`→`Scratch`, `[[Dir]]`→`DIR` are plain hand-authoring drift.
    **Every one of them resolves**, because Obsidian matches a link's filename
    case-insensitively through its own index, so nothing a reader does is
    broken and this must never be an error.

    It is worth listing rather than dropping because the case-insensitive
    matching that stopped the phantom findings also made the drift invisible,
    and the canonical-spelling argument still has one live constituency: every
    NON-Obsidian consumer — GitHub's renderer, this vault's own checkers, any
    external tool — resolves case-sensitively. Keeping the population
    enumerated is what keeps that sweep available if it is ever wanted.

    Scoped to siblings and children of the doc, which is where a masthead
    points; a vault-wide resolve would cost an index for a cosmetic list.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    rows = _masthead_rows(text, f.stem)
    if not rows:
        return "pass", "no self-masthead"
    nearby = {}
    for p in list(f.parent.iterdir()) + [q for d in f.parent.iterdir()
                                         if d.is_dir()
                                         for q in list(d.iterdir())[:200]]:
        nearby.setdefault((p.stem if p.is_file() else p.name).casefold(),
                          p.stem if p.is_file() else p.name)
    drift = []
    for ln in rows:
        # What a wiki-link IS comes from `_WIKILINK_RE`, the one definition —
        # re-spelling it here is the T099 defect, and this checker committed it
        # (caught by structure-lint 2026-08-08, after the T138 commit shipped).
        # Only the split of the link's INNER text is local business: the name is
        # whatever precedes the first alias pipe or heading anchor, and inside a
        # table cell that pipe is BACKSLASH-escaped, so `\|` must be tried first.
        for m in _WIKILINK_RE.finditer(ln):
            name = re.split(r"\\\||\||#", m.group(1), maxsplit=1)[0].strip()
            real = nearby.get(name.casefold())
            if real and real != name:
                drift.append(f"`[[{name}]]` → `{real}`")
    if drift:
        uniq = sorted(set(drift))
        return "warn", ("masthead link case differs from the target on disk: "
                        + ", ".join(uniq)
                        + " — resolves fine in Obsidian, cosmetic only (T138)")
    return "pass", "masthead link case matches disk"


def masthead_narrative_offenders(text, stem):
    """R-dispatch-table-06's core test over TEXT — no filesystem access. Returns
    the doc's own masthead rows whose RIGHT cell carries more than TWO words
    in a row outside links and code spans, as (left label, right cell) pairs
    (right cell .strip()'d, so a pair is a stable identity for the cell).

    The criterion is Dan's hard cap, restated 2026-08-22 when he declined the
    adaptive-tuning path (F594) in favor of a flat rule: "a hard rule that
    says you can't write a spine that has more than 2 words in a row in it
    … it's just gonna be harsh on that point at this stage." Links and code
    spans are pointers — they carry no word count and they BREAK a run.
    Everything else counts, parenthesized or not: `(two words)` and bare
    `two words` both pass; any fragment of three or more words fails. The
    earlier form allowed a ≤2-word modifier only inside parentheses — strict
    in the wrong dimension (bare two-word tags failed) while stating the same
    cap. Punctuation-only tokens (·, —, commas) neither count nor break a
    run, so `quick, dirty, old` is three words and fails.

    Split out of `chk_dispatch_cell_narrative` (which formats these into its
    verdict) so the `tool:pre` veto path (R-dispatch-guard, 2026-08-22) can run
    the identical test against the PROPOSED content of a Write/Edit before it
    lands on disk — one definition of a violating cell for both the post-write
    audit and the pre-write deny.
    """
    rows = _masthead_rows(text, stem)
    if len(rows) < 3:
        return []
    marker_cells = {"...", "…", "---", "^^^", "+++", "!!!"}
    offenders = []
    for ln in rows[2:]:
        cells = _row_cells(ln)
        if not cells:
            continue
        if cells[0].strip() in marker_cells:
            break
        if len(cells) < 2:
            continue
        # A LEFT cell that is itself a wiki-link is a child pulled above the
        # separator by hand — the special disk, the flagship member — and the
        # right cell is that child's description, exactly as the machine would
        # write it below `---`. A sentence there is expected, not narrative.
        # Ruled by Dan 2026-08-29 on [[Disk]] (10T / 8T / BLACK): "there's a
        # label, there's a wiki-link in the left-hand column, and then as long
        # as there's a bunch of text in the right-hand column, it's the
        # description of that link — it's allowed to be there." The 2-word cap
        # is for the right cell of a LABEL row, where prose explains a link
        # that should explain itself on its own page.
        # A markdown link (`[PRD](hook://…)`, a `file://` asset) in the left
        # cell is the same shape — the ruling was about a link, not its
        # syntax; 25 such rows vault-wide on 2026-08-29.
        if _WIKILINK_RE.search(cells[0]) or _MDLINK_RE.search(cells[0]):
            continue
        right = cells[1]
        # A DESCRIBED GROUP LABEL is exempt too (T623 Q4, Dan 2026-08-29: "if
        # it really is a group label, then it absolutely makes sense to have
        # words on that"). The shape that "really is" one: a non-link,
        # non-empty left cell and a right cell that is ENTIRELY one italic
        # span — `| **Registers** | *entity-keyed: you look it up* |` ([[kmr]],
        # [[AOT]]). Prose outside the italics is still narrative. The
        # single-line preference is guidance in DAS spine, not enforced here.
        if _is_described_group_label(cells[0], right):
            continue
        # Links and code spans are pointers: zero words, and a run-breaker —
        # replaced by a hard separator so text on either side of a link is two
        # runs, not one. The code-span carve-out keeps the `Ground truth` row
        # naming `~/ob/kmr/.obsidian/` legal (Dan blessed that shape
        # 2026-08-22: "spiritually the ground truth section here is good");
        # 22 cells vault-wide are code-span-only.
        stripped = _WIKILINK_RE.sub("\x00", right)
        stripped = _MDLINK_RE.sub("\x00", stripped)
        stripped = re.sub(r"`[^`]*`", "\x00", stripped)
        for frag in stripped.split("\x00"):
            words = [t for t in frag.split() if re.search(r"\w", t)]
            if len(words) > 2:
                offenders.append((cells[0].strip(), right.strip()))
                break
    return offenders


def _is_described_group_label(left: str, right: str) -> bool:
    """`| **Label** | *gloss* |` — a group heading with its gloss (T623 Q4).
    The gloss is ONE italic span covering the whole cell; bold inside it
    (`**kind of entity**`, as on [[kmr]]) is fine, a second italic span or
    any text outside the italics is not."""
    if not left.strip() or _WIKILINK_RE.search(left) or _MDLINK_RE.search(left):
        return False
    r = right.strip()
    if len(r) < 3 or not (r.startswith("*") and r.endswith("*")) or r.startswith("**"):
        return False
    inner = re.sub(r"\*\*[^*]+\*\*", "", r[1:-1])   # drop bold spans
    return "*" not in inner


def chk_dispatch_cell_narrative(target, anchor_root, args):
    """R-dispatch-table-06 — a masthead's RIGHT cell is nearly pure links: at
    most one short (<=2 word) parenthetical tag per link, no other prose.

    Scope: every row of the doc's own masthead after the identity row and the
    GFM header separator, stopping at the first electric-marker row (`...`,
    `---`, `^^^`, `+++`, `!!!`, `…`) — everything from there down is machine-
    owned per R-dispatch-table-13 and never hand-authored narrative. The LEFT
    cell is exempt (R-06: "describing the row itself is fine there").

    Check: replace every wiki-link (`[[Target]]` / `[[Target\\|Display]]`),
    markdown link (`[text](url)`), and code span with a run-breaking
    separator, then count words in each remaining fragment of the right cell.
    Any fragment of three or more words is a violation — Dan's hard cap,
    restated 2026-08-22: "you can't write a spine that has more than 2 words
    in a row." A ≤2-word modifier passes with or without parentheses; a
    sentence, a `**bold**` gloss, or any third consecutive word belongs on
    the destination page's own head (H1 + orientation line) or `## Overview`,
    not the table that points at it.

    Ships `fail` since 2026-08-22, on Dan's direct instruction: "let's just
    change the rule so that you cannot write a table with more than 2 words
    … let's just see what happens when the system is forced to do that."

    It shipped `warn` from 2026-08-14, on the reasoning that a rule with no
    safe automatic repair should stay advisory until the corpus is clean.
    That deadlocked, because `execute_on_write` surfaces only `fail`: the rule
    was invisible at the one moment it could have been obeyed for free, so the
    corpus never cleaned. Measured the day of the flip — 1,374 hand-typed
    prose cells across 370 of the vault's 1,028 masthead docs, and no agent
    had ever been told about one of them. The escape is the exception table
    ([[R-exception-discipline]], grade A–C suppresses); there is still no
    `fix::`, so the on-write path emits the message and leaves the repair to
    the agent, which is what -06's MEND is written for.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    rows = _masthead_rows(text, f.stem)
    if len(rows) < 3:
        return "pass", "no self-masthead" if not rows else "no content rows"
    offenders = [f"'{label}' row: {right[:80]!r}"
                 for label, right in masthead_narrative_offenders(text, f.stem)]
    if offenders:
        # `fail` again since 2026-08-29 evening (TINK T623). It sat at `warn`
        # for one day while the spine→heart migration ran: 434 of 1,604
        # mastheads violated on the morning measurement, 0 of 1,541 after the
        # link-left flips, the group-gloss exemption, and the fact-card moves
        # into `| Card |` hearts ([[DAS heart]] § Fact card). The cap is now
        # satisfiable without loss on every page, which was the condition for
        # re-arming; R-dispatch-guard's denies came back the same evening.
        return "fail", ("dispatch table right cell carries more than 2 words in a "
                        "row — " + "; ".join(offenders[:4])
                        + " — move the page's own facts into its heart ([[DAS heart]]) "
                        "and the explanation of a destination onto that page "
                        "(R-dispatch-table-06)")
    return "pass", "right cells are links + <=2-word tags only"


_HAND_LINK_NAMES: dict[str, frozenset] = {}


def _root_link_names(root: Path) -> frozenset:
    """Every file NAME and .md STEM under `root` — the basename index Obsidian
    resolves a wiki-link against. Memoised per root for the life of the run."""
    key = str(root)
    hit = _HAND_LINK_NAMES.get(key)
    if hit is None:
        names: set[str] = set()
        try:
            for p in root.rglob("*"):
                if "/.git/" in str(p):
                    continue
                # Case-folded: Obsidian resolves a link's filename
                # case-insensitively (R-dispatch-table-15), so `[[WW]]` finds
                # `ww.md` and must not be reported.
                names.add(p.name.lower())
                if p.suffix == ".md":
                    names.add(p.stem.lower())
        except OSError:
            pass
        hit = frozenset(names)
        _HAND_LINK_NAMES[key] = hit
    return hit


_ELECTRIC_MARKERS = {"...", "…", "+++", "^^^", "!!!"}


def chk_dispatch_hand_link_resolves(target, anchor_root, args):
    """R-dispatch-table-16 — every wiki-link in a HAND row of the masthead
    resolves to a file somewhere in the vault, by Obsidian's own rule
    (basename, anywhere).

    Only the rows the author owns are judged: everything after the identity row
    and the GFM separator, stopping at the first electric marker (`...`, `| --- | |`,
    `+++`, `^^^`, `!!!`). Rows below the marker are the machine's and are
    recomputed from the command store, which is exactly why a dead link there
    cannot exist and a dead link ABOVE it cannot be cleared by the machine —
    the confusion T615 was filed on (Dan, 2026-08-28: *"if those are dead links
    and that electric section is computed automatically, why didn't it remove
    them?"*). HBR Components carried six such links to component pages that
    were never written, in hand rows the rebuild never touches.

    Resolution is vault-wide by basename (the ancestor anchor roots plus the
    corpus root), never sibling-only: a masthead routinely links other anchors.
    A link with an extension (`Help.txt`, `Diagram.svg`) resolves against file
    names; a bare name resolves against `.md` stems. Ships `warn` — a dead hand
    link routes a reader nowhere, but the fix is an author's (write the page or
    drop the row), and there is no mechanical repair to apply."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    rows = _masthead_rows(text, f.stem)
    if len(rows) < 3:
        return "pass", "no self-masthead" if not rows else "no content rows"
    # Every enclosing anchor up to the vault root (uncapped — a masthead links
    # other anchors anywhere in the vault), plus the corpus root.
    roots: list[Path] = []
    cur = anchor_root.resolve()
    while True:
        if (cur / ".anchor").is_file():
            roots.append(cur)
        if cur.parent == cur:
            break
        cur = cur.parent
    roots = [roots[-1]] if roots else [anchor_root]
    roots.append(REPO_ROOT)
    dead: list[str] = []
    for ln in rows[1:]:
        cells = _row_cells(ln)
        if not cells:
            continue
        first = cells[0].strip()
        if first in _ELECTRIC_MARKERS or (first == "---" and not any(c.strip() for c in cells[1:])):
            break
        if all(re.fullmatch(r":?-{3,}:?", c.strip() or "---") for c in cells):
            continue                    # the GFM header separator
        for m in re.finditer(r"\[\[([^\]]+)\]\]", ln):
            tgt = _link_file_target(m.group(1))
            if not tgt:
                continue                # `[[#heading]]` — same-page
            name = tgt.split("/")[-1].strip()
            if not name:
                continue
            if any(name.lower() in _root_link_names(r) for r in roots):
                continue
            dead.append(f"[[{tgt}]]")
    if dead:
        uniq = list(dict.fromkeys(dead))
        return "warn", (f"{len(uniq)} hand-row link(s) resolve to no file: "
                        + ", ".join(uniq[:6]) + (" …" if len(uniq) > 6 else "")
                        + " — write the page or drop the row; the rebuild never "
                        "touches rows above the separator (R-dispatch-table-16)")
    return "pass", "every hand-row link resolves"


def chk_toc_table_iff_long(target, anchor_root, args):
    """R-doc-structure-03, the long side only: a doc of 300+ body lines must
    carry a TOC table (≥2 rows whose first cell is an in-document `[[#…]]`
    link). The MUST-NOT direction (short doc with a TOC) is not mechanically
    judged — a 2026-07-06 sweep flagged 18 canonical exemplars whose small
    section-index tables are the rule's own "specialized table" exemption,
    which a regex can't tell from a TOC."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # A mechanically-regenerated projection can't hold a TOC: `queries-render.py`
    # rewrites the whole page on every state change, so any TOC would be erased
    # on the next write and nobody could add one by hand anyway (R-pathguard
    # denies the edit). The rule asks an author to help a reader navigate; these
    # pages have no author. Backlogs are NOT exempt — `state` edits rows in
    # place, so a hand-authored TOC survives there, and long ones carry one.
    if f.name == "Q.md" or f.name.endswith(" queries.md"):
        return "pass", "script-owned projection"
    # T237 — append-only chronological logs are exempt too, on a DIFFERENT
    # ground, which is worth stating because the projection argument does not
    # apply: an Inbox is appended to rather than rewritten, so a hand-authored
    # TOC would in fact survive `state drop` (Atticus was careful to say so
    # rather than overclaim the exemption). The reason these are exempt is that
    # the rule has nothing to bite on. An Inbox's content outline IS its list
    # of dated H2s, in the order they already appear, so a TOC restates the
    # document; a Messages log has no headings at all, so its TOC would be
    # empty. Left unexempted, the advisory fired on every `state` write to
    # every Inbox and Messages file in the fleet — nine times in one drain,
    # measured 2026-08-17 — which is how a warning tier stops being read.
    if f.name.endswith(" Inbox.md") or f.name.endswith(" Messages.md"):
        return "pass", "append-only log — its outline is the entry list itself"
    lines = _strip_fenced(_read(f)).splitlines()
    # LUMEN F034 (2026-08-25) — the append-only exemption above, generalized
    # to the SHAPE it was always about: a dated chronological log. LUMEN Day
    # is eighteen dated `##` sections growing ~23 lines a day; its content
    # outline IS its dated-H2 list in the order they appear, so a TOC restates
    # the document and grows a row every morning without bound (and rotation is
    # no remedy — a fresh day-log re-crosses 300 lines in ~13 days). Gate on
    # the structure, never on a filename suffix: a `" Day.md"` suffix would
    # silently exempt ordinary docs like `ASR Test Day.md`, and a silent wrong
    # exemption is worse than the advisory. Threshold: 4+ H2s, ≥80% opening
    # with an ISO date.
    h2s = [ln for ln in lines if ln.startswith("## ")]
    # An optional weekday prefix is part of the dated shape — LUMEN Day's own
    # headings read `## Tue 2026-08-25 · W35`.
    dated_h2s = sum(1 for ln in h2s if re.match(
        r"##\s+(?:(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+)?\d{4}-\d{2}-\d{2}\b", ln))
    if len(h2s) >= 4 and dated_h2s >= 0.8 * len(h2s):
        return "pass", "dated chronological log — its outline is the entry list itself"
    # First cell may be bold — md-toc.py (the sanctioned TOC generator) emits
    # `| **[[#Section]]** |`, which the bare `\[\[#` pattern missed, making
    # every md-toc-generated TOC read as absent (false R-doc-structure-03 fail,
    # 2026-07-08 MUX Backlog).
    toc_rows = sum(1 for ln in lines if re.match(r"^\|\s*(?:\*\*)?\[\[#", ln))
    # T555 — length was never the whole trigger. The rule's own Check pattern
    # reads *"estimate length by content (**heading count** + body lines as a
    # page proxy)"*, and only the body-lines half was ever implemented. A doc
    # with too few headings cannot benefit from a TOC at any length: the H1 is
    # not a TOC row, so fewer than 4 headings yields a table of 0–2 rows, which
    # is friction with no navigation value and the opposite of this rule's own
    # rationale.
    #
    # Reported from `Log/VOX/`, where a `type: vox-transcript` doc carries an H1
    # and a `## Transcript` and nothing else. **The corpus had already voted**:
    # `2026-08-15 Juan — game break signals and metrics.md` is 1,072 lines with
    # no TOC and `2026-08-10 Lewis on Singapore.md` is 6,631 — the rule had been
    # firing and being ignored, which is how a warning tier stops being read.
    #
    # Measured vault-wide 2026-08-20 before choosing the number: 381 docs fire
    # today; a `< 4` gate silences 40 of them and leaves 341. Both transcripts
    # above carry exactly **3** headings, so 4 is the smallest threshold that
    # answers the report — not a round number picked for looking reasonable.
    headings = sum(1 for ln in lines if _ANY_HEADING_RE.match(ln))
    if len(lines) >= 300 and toc_rows < 2 and headings >= 4:
        return "fail", (f"{len(lines)} lines and {headings} headings with no TOC table "
                        f"— a long doc carries a content-outline table (`[[#…]]` links)")
    return "pass", ""



# ---------------------------------------------------------------------------
# R-spine-03/05 — progressive-disclosure summary (SKA F277, 2026-07-20)
# ---------------------------------------------------------------------------

DISCLOSURE_REGISTRY = Path.home() / ".warden" / "disclosure.json"
DISCLOSURE_DRIFT_FRACTION = 0.25   # a quarter of units changed → re-ask
DISCLOSURE_MIN_LINES = 300         # matches R-doc-structure-03; H2-count was a bad
                                   # proxy — template docs (features, PRDs) always
                                   # carry several sections without being hard to read


def _disclosure_scope(f, anchor_root):
    """file | container | tree — mechanical, from existing structure.

    A doc that is its folder's same-named index summarizes the FOLDER, not
    itself; if a `.anchor` sits beside it, it fronts the whole tree."""
    if f.parent.name == f.stem:
        return "tree" if (f.parent / ".anchor").exists() else "container"
    return "file"


def _disclosure_units(f, scope):
    """The set of things the summary covers, as {name: content-hash}.

    Counting CHANGED UNITS is what "big chunks moved" means mechanically —
    file size fires on typo fixes, and hashing only the heading set misses a
    section rewritten wholesale under an unchanged heading, which is exactly
    when a summary goes stale."""
    import hashlib
    units = {}
    if scope == "file":
        body, cur, buf = _strip_fenced(_read(f)), None, []
        for ln in body.splitlines():
            if re.match(r"^##\s+\S", ln):
                if cur is not None:
                    units[cur] = hashlib.sha1("\n".join(buf).encode()).hexdigest()[:12]
                cur, buf = ln.strip(), []
            elif cur is not None:
                buf.append(ln)
        if cur is not None:
            units[cur] = hashlib.sha1("\n".join(buf).encode()).hexdigest()[:12]
    else:
        it = f.parent.rglob("*.md") if scope == "tree" else f.parent.glob("*.md")
        for m in sorted(it):
            if m == f:
                continue
            try:
                units[str(m.relative_to(f.parent))] = hashlib.sha1(
                    m.read_bytes()).hexdigest()[:12]
            except OSError:
                continue
    return units


# A SUMMARY ROW — a TOC row, an in-doc `[[#…]]` outline row, or a dispatch masthead
# row. Spelled once because the two functions that asked the question disagreed:
# `_disclosure_summary` allowed a bold wrapper only on the `[[#…]]` form, while
# `_disclosure_descriptive` allowed it on all three. A masthead whose first cell is
# `| **[[Alpha]]** |` — the bolded-lead form the dispatch spec itself uses — was
# therefore judged to HAVE no summary and, in the same pass, to have a DESCRIPTIVE
# one. Bold is presentation; it belongs in one place, applied to every form.
_SUMMARY_ROW_RE = re.compile(r"^ {0,3}\|\s*(?:\*\*)?(?:-?\[\[|→)")


def _disclosure_summary(f):
    """(has_summary, hash_of_summary_region). A summary is a TOC table, an
    in-doc `[[#…]]` outline, or a dispatch masthead."""
    import hashlib
    lines = _strip_fenced(_read(f)).splitlines()
    rows = [ln for ln in lines if _SUMMARY_ROW_RE.match(ln)]
    return bool(rows), hashlib.sha1("\n".join(rows).encode()).hexdigest()[:12]


def _summary_is_toc(f):
    """Is the summary region a content-outline TOC rather than a dispatch masthead?

    Both satisfy `_disclosure_summary`, but only a TOC is DERIVED from the
    section set, so only a TOC goes stale the instant a `##` is added or
    removed — and only a TOC has a generator to re-run. A masthead's rows name
    sibling FILES and survive any amount of section churn untouched, so the
    same advice there would send the agent to regenerate something that is not
    wrong. Detected by the `[[#…]]` in-document target, which is what makes a
    row an outline entry rather than a member link.
    """
    lines = _strip_fenced(_read(f)).splitlines()
    return any("[[#" in ln for ln in lines if _SUMMARY_ROW_RE.match(ln))


def _disclosure_descriptive(f):
    """Does the summary say anything ABOUT each unit, or only name it?

    A bare list of names/links (a backlog's `## Ready / ## Now / ## Next` TOC) is
    invariant under content churn beneath it — the names stay right no matter how
    the rows move, so re-asking on drift is pure noise. A summary whose rows carry
    a gloss makes a claim about each unit, and THAT is what goes stale when the
    unit is rewritten. Descriptive summaries answer to content drift; name-only
    ones answer only to units appearing or disappearing.
    """
    lines = _strip_fenced(_read(f)).splitlines()
    for ln in lines:
        if not _SUMMARY_ROW_RE.match(ln):
            continue
        # Strip the link cell, then look for surviving prose in later cells.
        cells = _row_cells(ln)
        for cell in cells[1:]:
            gloss = re.sub(r"\[\[[^\]]*\]\]|\*\*|`[^`]*`|<br>|→|:", " ", cell)
            if len(gloss.split()) >= 3:
                return True
    return False


def _disclosure_complex(f):
    return len(_strip_fenced(_read(f)).splitlines()) >= DISCLOSURE_MIN_LINES


def _disclosure_load():
    try:
        return json.loads(DISCLOSURE_REGISTRY.read_text())
    except Exception:
        return {}


def _disclosure_save(reg):
    try:
        DISCLOSURE_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        DISCLOSURE_REGISTRY.write_text(json.dumps(reg, indent=1, sort_keys=True))
    except OSError:
        pass


def chk_summary_present_iff_complex(target, anchor_root, args):
    """R-spine-03 (F277 M1) — a complex doc opens with a summary entity.

    The primary failure is ABSENCE, not staleness: agents are told to write a
    top summary and largely do not, because nothing ever forces the check.
    `toc_table_iff_long` covers only 300+ line docs, a floor so high almost
    nothing trips it."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    scope = _disclosure_scope(f, anchor_root)
    if scope == "file":
        # Long file-scope docs are already `toc_table_iff_long`
        # (R-doc-structure-03, same 300-line floor). Duplicating it here would
        # be a second rule for one constraint.
        return "pass", ""
    if not any(m.suffix == ".md" and m != f for m in f.parent.iterdir()):
        return "pass", ""      # nothing to summarize yet
    if _is_state_backlog_namesake(f):
        # T363 Q1 = (A), 2026-08-19. A folder-form backlog (F329) IS an index
        # doc fronting a folder, and its members are listed — as derived pointer
        # rows in `## Now` / `## Next` / `## Later`, which carry status and
        # horizon a masthead link-list could not. The rule exists so a reader
        # reaches the members from the index; here they already can.
        #
        # Reported by SONAR after four writes produced four identical warnings,
        # then by LUMEN and again by SONAR — it fires on EVERY `state` mutation
        # to 13 folders across 9 anchors, and three sessions logged it as known
        # noise. A rule that is correct, unactionable and permanent trains
        # agents to skim the whole warning tier, which is the tier carrying the
        # findings that are actionable.
        #
        # Keyed to the machine `state:backlog` stamp, NOT to "the body has
        # links": the narrow key is what stops any future index doc claiming
        # the same exemption for prose that happens to link a sibling.
        #
        # The one thing the horizon body genuinely cannot show is a doc whose
        # row RETIRED — SONAR017, an open question to Dan, unreferenced for
        # three days. That gap is real and is closed separately by audit-q C58,
        # which is what makes this exemption safe to state.
        return "pass", ""
    if _is_notebook_namesake(f):
        # T556, 2026-08-20 — same family, and the facet had already ruled.
        # [[DAS Notebook]]: "A notebook folder is NOT a sub-anchor — it takes
        # no functional `.anchor` and no dispatch table; the `<!-- notebook -->`
        # marker on the namesake is the machine-readable discriminator."
        # The narrative already carries one H2 per cell, each linking that
        # cell's doc, so a masthead would restate every link in the body.
        #
        # Reported by A2X, who declined to fix it locally and was right to:
        # restructuring a notebook index is a facet decision, and guessing
        # would put a table on every notebook in the vault. It fired on EVERY
        # `nb append` — A2X013 is at 16 cells, so 16 identical warnings.
        #
        # Residual, stated because the T363 exemption came with its own: a cell
        # doc sitting in the folder that the narrative does NOT link would be
        # invisible here, exactly as a retired row's doc was. It is a much
        # smaller hole — `nb append` is the facet's only sanctioned write
        # surface and it writes the block and the doc in one act — so an orphan
        # cell can only arrive by hand, which the facet already forbids.
        return "pass", ""
    has, _ = _disclosure_summary(f)
    if has:
        return "pass", ""
    return "fail", ("index doc fronting a folder with no dispatch table — add one linking "
                    "the members so a reader reaches any of them in one click")


def chk_summary_fresh(target, anchor_root, args):
    """R-progressive-05 (F277 M2) — re-ask when the covered content has moved.

    Counts changed/added/removed UNITS since the summary was last blessed.
    Blessing is OBSERVED, never self-reported: when the summary region's own
    hash changes, the agent evidently rewrote it, so the current unit set is
    re-blessed. There is no handshake for an agent to forget or overstate.

    THE SUMMARY REGION IS THE TOC TABLE OR DISPATCH MASTHEAD, not the prose
    under a `## Summary` heading — `_disclosure_summary` hashes exactly the
    rows `_SUMMARY_ROW_RE` matches. Rewriting `## Summary` therefore re-blesses
    NOTHING, which is worth stating loudly here because the message this
    checker used to emit invited precisely that and the flag survived it."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _disclosure_complex(f):
        return "pass", ""
    has, summary_hash = _disclosure_summary(f)
    if not has:
        return "pass", ""      # absence is R-spine-03's business, not ours

    scope = _disclosure_scope(f, anchor_root)
    units = _disclosure_units(f, scope)
    reg = _disclosure_load()
    key = str(f)
    prev = reg.get(key)

    # First sight, or the agent just rewrote the summary → bless silently.
    if prev is None or prev.get("summary") != summary_hash:
        reg[key] = {"summary": summary_hash, "units": units, "scope": scope}
        _disclosure_save(reg)
        return "pass", ""

    old = prev.get("units", {})
    added = [k for k in units if k not in old]
    removed = [k for k in old if k not in units]
    changed = [k for k in units if k in old and units[k] != old[k]]
    total = max(len(old), 1)

    # A name-only summary (a bare TOC of section names) stays correct however
    # much the content beneath it moves — only an appearing or disappearing unit
    # can falsify it. Firing on content drift there is guaranteed noise, and on
    # tracking files it fires on literally every write, which is how a rule
    # trains agents to tune it out.
    if not _disclosure_descriptive(f):
        changed = []

    # An added or removed unit is precisely what a summary most often fails to
    # mention, so it fires on its own rather than waiting for the fraction.
    if added or removed or (changed and (len(changed) / total) >= DISCLOSURE_DRIFT_FRACTION):
        # Anti-nag (F277 § Not nagging): having already prompted on THIS drift,
        # stay quiet until either the agent rewrites the summary (handled above)
        # or the content moves further still. Without this the same unanswered
        # prompt repeats on every subsequent write to the file, which is exactly
        # how the original prose rule died. Keyed on the unit set rather than a
        # session id — a session is not observable here, and "drift grew since I
        # last complained" is the sharper condition anyway.
        # The suppression key must match WHAT FIRED, or it suppresses nothing.
        # Keying on the full {name: content-hash} map means any edit anywhere in
        # the doc mints a new key, so a name-triggered prompt re-fires on every
        # subsequent write — the exact repetition this block exists to prevent,
        # reintroduced by the key being finer than the trigger. Measured on the
        # live registry 2026-08-20: 12 documents standing flagged, several of
        # them re-prompting on every write for weeks. Content-fraction drift
        # still keys on the full map, because there "it moved further" IS the
        # condition to re-prompt on.
        prompted = prev.get("prompted")
        frac_fired = bool(changed) and (len(changed) / total) >= DISCLOSURE_DRIFT_FRACTION
        if prompted is not None:
            if frac_fired and prompted == units:
                return "pass", ""
            if not frac_fired and set(prompted) == set(units):
                return "pass", ""
        reg[key] = {"summary": summary_hash, "units": old,
                    "scope": scope, "prompted": units}
        _disclosure_save(reg)

        bits = []
        if changed:
            bits.append(f"{len(changed)} of {total} changed")
        if added:
            bits.append(f"{len(added)} added")
        if removed:
            bits.append(f"{len(removed)} removed")
        noun = "sections" if scope == "file" else "members"
        # A TOC is derived from the section set, so an added/removed section
        # means the TOC itself is stale — it is still listing a heading that is
        # gone, which is a dead `[[#…]]` link a reader can click. That is the
        # actionable repair, and naming "the summary" instead sends the agent to
        # rewrite prose the checker does not hash, leaving the flag standing.
        # `scope == "file"` is load-bearing, not belt-and-braces. A container
        # page's units are its MEMBER FILES, so its `[[#…]]` outline is not what
        # drifted and regenerating it would repair nothing — every backlog in
        # the vault is exactly this shape (a namesake page over a folder, with a
        # content TOC), and without the gate all six of them got sent to
        # `md-toc.py` for a change in their sibling set. Found by measuring the
        # live registry rather than by reasoning about it.
        if scope == "file" and (added or removed) and _summary_is_toc(f):
            return "fail", (f"{noun}: {', '.join(bits)} since the summary was last written — "
                            f"the TOC table still names the old section set, so it now "
                            f"carries a dead `[[#…]]` row; regenerate it with "
                            f"`python3 ~/.claude/skills/md/md-toc.py <file>` (never hand-edit "
                            f"those rows — they carry figure spaces), then re-read the prose "
                            f"summary and fix it or leave it deliberately")
        return "fail", (f"{noun}: {', '.join(bits)} since the summary was last written — "
                        f"re-read it and decide whether it still serves a reader; "
                        f"fix it or leave it deliberately")
    return "pass", ""


def chk_progressive_disclosure_layout(target, anchor_root, args):
    """Multi-check section spacing in one rule — the section-break conventions that
    let a navigator scan a doc's outline ([[DSC progressive-disclosure]]):

      (1) every `## H2` is preceded by a blank line (no H2 glued to the prose above);
      (2) the file has no trailing blank line(s) at end-of-file.
    Deliberately excludes the anchor-page-only "no blank after the H1" glue rule
    (that is `R-anchor-page-07`'s job) and the "no doubled blank line" rule (widely
    tolerated in practice), which would both be noisy on ordinary docs. Blank-line
    checks skip fenced code blocks."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    lines = text.splitlines()
    # This is where the third copy of the private fence toggle was found, and the
    # one that mattered most: `R-progressive` is `where:: always`, so it ran over
    # every doc in the vault. `F113 — Decisions facet…md` opens a ```markdown
    # fence at line 54 and never closes it; CommonMark runs that fence to
    # end-of-document, but the toggle read the line-98 opener as a closer, so the
    # `## md-formatting` heading on line 99 — plainly inside a code sample — was
    # judged a live H2 glued to the prose above. Verdict diff over all 7366 vault
    # docs: one move, that false positive, nothing else.
    fenced = _fenced_mask(text)
    fails = []
    # (1) every H2 preceded by a blank line
    for i, ln in enumerate(lines):
        if re.match(r"^## \S", ln) and not fenced[i] and i > 0 and lines[i - 1].strip() != "":
            fails.append(f"no blank line before H2 '{ln[3:33].strip()}' (line {i + 1})")
            break
    # (2) no trailing blank lines
    if lines and lines[-1].strip() == "":
        fails.append("trailing blank line(s) at end of file")
    if fails:
        return "fail", "; ".join(fails)
    return "pass", "section spacing ok"


def chk_doc_head_orientation_line(target, anchor_root, args):
    """The head's third disclosure layer ([[DSC progressive-disclosure]]): directly
    under the first H1 — after any `key:: value` inline-field lines (skill pages
    carry requires::/subsystem:: there) — the doc opens with an ORIENTATION LINE:
    one single-line prose sentence stating what this file is. Fails when (a) no
    prose line appears there (the doc jumps straight to a heading / table / list /
    figure / fence), or (b) the first prose line wraps into a second prose line
    (the orientation must be a single line, no embedded newlines; a masthead
    table directly below it is fine). Docs with no H1 pass — H1 presence is
    other rules' business."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Script-rendered query surfaces are exempt: their banner-only head is
    # R-query's shape, ruled by the user (no meta prose on Q.md / queries pages).
    if f.name == "Q.md" or f.name.endswith(" queries.md"):
        return "pass", "rendered query surface — head shape owned by R-query"
    text = _read(f)
    lines = text.splitlines()
    # T092's scan is now `_head_h1`'s job. T092 diagnosed the miss as INDENTATION
    # and relaxed to `^ {0,3}# \S`; the corpus says that was the wrong half. Its own
    # damage signature — walk past the real head, blame the file's `# BRIEF` — is
    # what `SYS/Atlas/Atlas.md` still did afterwards, because Atlas opens with TWO
    # spaces after the `#` and every spelling in this file demanded exactly one.
    h1, head = _head_h1(text)
    if h1 is None or head is None:
        return "pass", "no H1 — out of scope"
    # Downstream head tests match the PARSED heading text, so they never re-state
    # the indent/space allowance. Without that, relaxing the scan would newly SELECT
    # an indented `# RULESET` or simple-facet head and then fail to recognize it —
    # turning one blindness into two false positives.
    h1_text = "# " + head
    # Ruleset spec heads are a distinct, machine-read doc class: `# RULESET <id>`
    # followed by `where::` / `include::` / `description::` fields (some valueless,
    # e.g. a bare `include::`), NOT the breadcrumb → H1 → orientation convention.
    # The orientation-line rule does not govern them — skip (T051).
    if re.match(r"^# RULESET\b", h1_text):
        return "pass", "ruleset spec head (# RULESET) — orientation line N/A"
    # Simple facet form (DAS Doc Structure): a slug-prefixed facet page whose H1
    # fuses the breadcrumb into the title — `# [[{slug}]] {Facet}` where {slug} is
    # the filename's leading token. The wiki-link IS the breadcrumb and the head
    # is self-describing (slug ⊗ facet), so the orientation line is waived; the
    # file's essence (a list / table / figure) may follow the H1 directly.
    m_sf = re.match(r"^# \[\[([^\]|#]+)(?:\|[^\]]+)?\]\]\s+\S", h1_text)
    if m_sf and m_sf.group(1).strip() == f.stem.split(" ")[0]:
        return "pass", "simple facet form — orientation line waived (fused-breadcrumb H1)"
    field = re.compile(r"^[\w-]+::\s")
    # Machine-written stamps (`<!-- state:backlog XX -->`, `<!-- state:q XX -->`)
    # sit directly under the H1 on every state-managed doc, so they land between
    # the H1 and the orientation line. They are not prose and must be skipped —
    # without this a stamped doc can never satisfy the rule, since the stamp is
    # written by `state`, not the author (found on the HBR reference anchor).
    comment = re.compile(r"^\s*<!--.*-->\s*$")
    j = h1 + 1
    while j < len(lines) and (lines[j].strip() == "" or field.match(lines[j])
                              or comment.match(lines[j])):
        j += 1

    # At-entity form ([[DAS At Entity]] § The opening, settled with Dan 2026-08-29):
    # an `@Name.md` register page opens breadcrumb -> identity H1 -> the `| Card |`
    # table, and that facet states outright that "the one-liner slot under the H1 is
    # not used - the H1 *is* the identity line". Same argument as the simple-facet
    # form above: the head already says what the file is, so re-stating it in a
    # sentence is redundant. Keyed to the CARD, deliberately not to the `@` prefix
    # or the `AT/` path - measured 2026-08-31, 391 of the 482 failing register pages
    # carry the card and are waived here, while the 91 not yet migrated to the
    # ratified shape keep failing, which is the advisory doing its job on the tail
    # of Winnie's migration rather than being switched off across a whole folder.
    if f.name.startswith("@") and j < len(lines) and lines[j].strip().startswith("| Card"):
        return "pass", "at-entity form — orientation line waived (the H1 is the identity line)"

    def _prose(ln):
        s = ln.strip()
        if not s:
            return False
        return not s.startswith(("|", "#", "- ", "* ", "+ ", ">", "![", "```", ":>>"))

    if j >= len(lines) or not _prose(lines[j]):
        return "fail", (f"no orientation line under the H1 (line {h1 + 1}) — "
                        "expected one single-line prose sentence saying what this file is")
    nxt = lines[j + 1].strip() if j + 1 < len(lines) else ""
    if nxt and not nxt.startswith("|"):
        return "fail", (f"orientation line under the H1 (line {j + 1}) runs into the next line — "
                        "it must be a single line (no embedded newlines) followed by a blank line or the masthead table")
    return "pass", "orientation line ok"


# -- R-roadmap -----------------------------------------------------------------

def chk_file_exists(target, anchor_root, args):
    """A file (arg[0], with {slug} substituted) exists under anchor_root.

    Registered and called by no rule (T212). The obvious caller would be an
    entry-page rule — `file_exists {slug}.md` — and that is exactly the wiring
    to avoid: `R-anchor-page-02` already owns entry-page existence through
    `entry_page_matches_slug`, whose `_entry_page` resolves **two** candidates,
    `{slug}.md` then `{folder}.md`. A one-candidate check reports the 34
    anchors whose page is legitimately folder-named, which is the measured
    failure of `folder_marker_exists` recorded in `R-fct-folder`. Left generic:
    it is sound for a rule naming a specific required file, and wrong for the
    entry page.
    """
    if not args:
        return "error", "file_exists requires a path argument"
    slug = _anchor_slug(anchor_root)
    pattern = args[0].replace("{slug}", slug)
    if (anchor_root / pattern).is_file():
        return "pass", f"{pattern} exists"
    return "fail", f"{pattern} does not exist"


def chk_milestone_checkbox(target, anchor_root, args):
    """Every M-prefixed milestone H2 carries a checkbox [x], [ ], or [~]."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    # Line numbers stay true: `_strip_fenced` blanks fenced lines rather than
    # removing them, so `line {i}` still points where the reader would look.
    # Orphan today (T099).
    for i, ln in enumerate(_strip_fenced(_read(f)).splitlines(), 1):
        if re.match(r"^## (M-|M\d)", ln) and not re.match(r"^## \[[x ~]\] ", ln):
            failures.append(f"line {i}: missing checkbox")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_milestone_status_line(target, anchor_root, args):
    """TOP-LEVEL milestones (token M<n> with no dot) carry a **Status**: line within
    ~10 lines. Sub-milestones (M1.0, M1.2.3 …) track status via their checkbox alone."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    # Both halves read the stripped copy: a fenced sample milestone must not DEMAND
    # a Status line, and a fenced `**Status**:` must not SATISFY one.
    lines = _strip_fenced(_read(f)).splitlines()
    failures = []
    for i, ln in enumerate(lines):
        # The `[a-z]*` is load-bearing, and its absence was a live defect the T099
        # fence pass surfaced rather than caused. Without it, `### [x] M1.8a — …`
        # does not capture `M1.8a`: `\b` fails after `M1.8` because `a` is a word
        # character, so the regex BACKTRACKS to `M1`, where `\b` succeeds against
        # the `.`. A lettered SUB-milestone was therefore read as top-level `M1` and
        # required to carry its own **Status** line. `ABIO Roadmap.md` reported 20
        # such findings, 19 of them naming an `M1` that does have a Status line
        # while pointing at a line that is not M1. Capturing the suffix makes
        # `M1.8a` fail the `fullmatch` below, which is the intended reading.
        m = re.match(r"^#+\s+\[[x~]\]\s+(M\d+(?:\.\d+)*[a-z]*)\b", ln)
        if m and re.fullmatch(r"M\d+", m.group(1)):  # top-level only
            if not any(re.match(r"^\*\*Status\*\*:", lines[j])
                       for j in range(i + 1, min(i + 11, len(lines)))):
                failures.append(f"line {i + 1}: top milestone {m.group(1)} missing Status line")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_milestone_named_form(target, anchor_root, args):
    """Milestones use M-<Name> form (unless file is legacy-marked)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    text = _read(f)
    if "<!-- legacy-numbered-milestones -->" in text:
        return "pass", "legacy-marked"
    failures = []
    for i, ln in enumerate(text.splitlines(), 1):
        if re.match(r"^(##|###) ", ln):
            m = re.search(r"\bM(\d)", ln)
            if m:
                failures.append(f"line {i}: pure-numbered M{m.group(1)} (use M-<Name>)")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_milestone_section_separator(target, anchor_root, args):
    """Milestone bodies end with a '### .' separator before the next nearby H2."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    # This one measures DISTANCE between H2s (`nxt - start < 20`), so a fenced H2
    # does not merely add a spurious section — it shortens the gap around real ones
    # and pulls them under the <20-line arm that demands a separator. Orphan today
    # (T099). Blanked-not-removed keeps those distances honest.
    lines = _strip_fenced(_read(f)).splitlines()
    h2 = [i for i, ln in enumerate(lines) if re.match(r"^## ", ln)]
    if len(h2) < 2:
        return "pass", "fewer than 2 H2 milestones"
    failures = []
    for k in range(len(h2) - 1):
        start, nxt = h2[k], h2[k + 1]
        if any(re.match(r"^### \.\s*$", lines[j]) for j in range(start + 1, min(start + 50, nxt))):
            continue
        if nxt - start < 20:
            failures.append(f"H2 at line {start + 1}: no ### . separator before next H2")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


# -- R-log ---------------------------------------------------------------------

def _is_log_container(anchor_root: Path) -> bool:
    """True when the anchor IS a `{slug} Log` container — the standard name for the
    folder of reverse-chronological dated entries (e.g. `SV Log`). Such an anchor
    does not need a NESTED log; it is one, so R-log-01/R-log-08 (which would demand
    a `SV Log Log/` inside it) must be suppressed for it (T050)."""
    return _anchor_slug(anchor_root).endswith(" Log") or anchor_root.name.endswith(" Log")


def chk_log_path_exists(target, anchor_root, args):
    """{slug} Log/ folder or {slug} Log.md exists under the anchor."""
    if _is_log_container(anchor_root):
        return "pass", "anchor IS a {slug} Log container — no nested log required (T050)"
    slug = _anchor_slug(anchor_root)
    if (anchor_root / f"{slug} Log").is_dir() or (anchor_root / f"{slug} Log.md").is_file():
        return "pass", f"found {slug} Log"
    return "fail", f"no {slug} Log/ or {slug} Log.md under anchor"


def chk_log_dispatch_file_present(target, anchor_root, args):
    """If {slug} Log/ exists it contains {slug} Log.md with H1 '{slug} Log'."""
    slug = _anchor_slug(anchor_root)
    dir_form = anchor_root / f"{slug} Log"
    if not dir_form.is_dir():
        return "pass", "not folder-form"
    dispatch = dir_form / f"{slug} Log.md"
    if not dispatch.is_file():
        return "fail", f"folder-form exists but no {slug} Log.md dispatch file"
    if re.search(rf"^# {re.escape(slug)} Log\s*$", _read(dispatch), re.MULTILINE):
        return "pass", ""
    return "fail", f"dispatch H1 is not '# {slug} Log'"


def chk_log_entry_filenames(target, anchor_root, args):
    """Entry files in {slug} Log/ match YYYY-MM-DD / YYYY-MM / YYYY date prefixes."""
    slug = _anchor_slug(anchor_root)
    dir_form = anchor_root / f"{slug} Log"
    if not dir_form.is_dir():
        return "pass", "not folder-form"
    dispatch_name = f"{slug} Log.md"
    ext = r"(md|docx|pptx|pdf|jpeg|jpg|png|txt)"
    file_pats = [rf"^\d{{4}}-\d{{2}}-\d{{2}} .+\.{ext}$",
                 rf"^\d{{4}}-\d{{2}} .+\.{ext}$",
                 rf"^\d{{4}} .+\.{ext}$"]
    dir_pats = [r"^\d{4}-\d{2}-\d{2} ", r"^\d{4}-\d{2} ", r"^\d{4} "]
    bad = []
    for item in dir_form.iterdir():
        if item.name == dispatch_name or item.name.startswith("."):
            continue
        pats = dir_pats if item.is_dir() else file_pats
        if not any(re.match(p, item.name) for p in pats):
            bad.append(item.name)
    if bad:
        return "fail", "entries do not match pattern: " + ", ".join(bad[:3])
    return "pass", "all entries match date pattern"


def chk_log_anchor_page_link(target, anchor_root, args):
    """Anchor entry page carries a [[{slug} Log]] dispatch row."""
    if _is_log_container(anchor_root):
        return "pass", "anchor IS a {slug} Log container — no [[{slug} Log Log]] link required (T050)"
    slug = _anchor_slug(anchor_root)
    ep = _entry_page(anchor_root)
    if ep is None:
        return "error", "no anchor entry page"
    if re.search(rf"\[\[{re.escape(slug)}\s+Log[^\]]*\]\]", _read(ep)):
        return "pass", ""
    return "fail", f"no [[{slug} Log]] link in anchor page"


# -- R-brief -------------------------------------------------------------------

def chk_brief_is_last_h1(target, anchor_root, args):
    """Exactly one '# BRIEF' H1, content after it, and it is the last H1.
    Consolidates has_brief_section (R-facet-spec) into the stricter R-brief check."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    lines = text.splitlines()
    # Both scans run over the FENCE-STRIPPED copy (line-for-line with `lines`, so
    # indices stay usable against the original). A Brief that shows a shell example
    # — `# rebuild the index` inside a ```bash block, which is what a Brief is FOR —
    # otherwise registers as an H1 below `# BRIEF` and the checker reports the
    # heading is not last. The backward `^#\s+\S` scan made that worse than the
    # forward ones: it starts at the file's END, where the examples live.
    stripped = _strip_fenced(text).splitlines()
    # Compare the PARSED heading text, not the literal line: `#\tBRIEF` and
    # `# BRIEF #` are both H1s whose content is exactly `BRIEF` by this file's own
    # `_H1_RE`, and a function that carries two definitions of an H1 is the very
    # thing the primitive exists to stop. (No vault doc spells it either way today.)
    def _is_brief(ln):
        m = _H1_RE.match(ln)
        return bool(m) and m.group(1) == "BRIEF"

    brief_count = sum(1 for ln in stripped if _is_brief(ln))
    if brief_count == 0:
        return "fail", "no '# BRIEF' heading"
    if brief_count > 1:
        return "fail", f"multiple '# BRIEF' headings ({brief_count})"
    last_h1 = None
    for i in range(len(stripped) - 1, -1, -1):
        if _H1_RE.match(stripped[i]):
            last_h1 = i
            break
    if last_h1 is None or not _is_brief(stripped[last_h1]):
        return "fail", "'# BRIEF' is not the last H1"
    if not "\n".join(lines[last_h1 + 1:]).strip():
        return "fail", "'# BRIEF' section is empty"
    return "pass", ""


def chk_brief_h1_matches_name(target, anchor_root, args):
    """A '* Brief.md' sidecar's H1 equals its filename (without .md)."""
    if not target.is_file() or not target.name.endswith(" Brief.md"):
        return "pass", "not a Brief.md file"
    expected = target.stem
    _, h1 = _head_h1(_read(target))
    if h1 is None:
        return "fail", "no H1 heading"
    return ("pass", h1) if h1 == expected else ("fail", f"H1 {h1!r} != filename {expected!r}")


def chk_brief_not_nested(target, anchor_root, args):
    """Briefs don't nest: no '* Brief Brief.md', no '# BRIEF' inside a '* Brief.md'."""
    if not target.is_file() or not target.name.endswith(" Brief.md"):
        return "pass", "not a Brief.md file"
    if " Brief Brief.md" in target.name:
        return "fail", "nested brief: file named '* Brief Brief.md'"
    # A Brief that QUOTES the `# BRIEF` heading — explaining the convention to the
    # agent that reads it, which is exactly what a Brief is for — is not a nested
    # brief. Orphan today (T099); converted so wiring it later is safe.
    if re.search(r"^# BRIEF$", _strip_fenced(_read(target)), re.MULTILINE):
        return "fail", "Brief.md file contains '# BRIEF' heading"
    return "pass", ""


# -- R-design ------------------------------------------------------------------

def chk_design_folder_children(target, anchor_root, args):
    """{slug} Design/ contains required children (args are stem names, e.g. PRD)."""
    if target.is_file():
        return "pass", "not a folder"
    name = _anchor_slug(anchor_root)
    design = anchor_root / f"{name} Design"
    if not design.is_dir():
        return "pass", "no Design folder (N/A)"
    missing = [a for a in args
               if not ((design / f"{name} {a}.md").is_file() or (design / f"{name} {a}").is_dir())]
    if missing:
        return "fail", "missing children: " + ", ".join(missing)
    return "pass", ""


def chk_status_facets_initialized(target, anchor_root, args):
    """When {slug} Design/ exists, {slug} Track/{slug} Status.md has the facet lines (args)."""
    name = _anchor_slug(anchor_root)
    if not (anchor_root / f"{name} Design").is_dir():
        return "pass", "no Design folder (N/A)"
    status_file = anchor_root / f"{name} Track" / f"{name} Status.md"
    if not status_file.is_file():
        # `state status <slug> show` creates the file with every facet at
        # `none` the first time /design reads it, so the picker never breaks
        # on absence. Demanding it up front produced files that lie (five
        # `none` lines nobody asked for) — the same shape T625 retired for
        # R-design-02. Only a file that EXISTS and lacks the lines is a defect.
        return "pass", "no Status.md yet (created on demand by `state status show`)"
    text = _read(status_file)
    missing = [a for a in args if not re.search(rf"^{re.escape(a)}\s*::", text, re.MULTILINE)]
    if missing:
        return "fail", "missing facet lines: " + ", ".join(missing)
    return "pass", ""


# -- R-file-association --------------------------------------------------------

_facet_names_cache: set[str] | None = None


def _registered_facet_names() -> set[str]:
    """Every facet the registry declares, as a bare name — `facets/DAS <Name>.md`
    minus the prefix. Read once per process; the folder holds 77 files.

    This is the *registry*, not a guess: a name is here because someone wrote a
    facet spec for it. `chk_facet_registered` asks the mirror-image question
    (is this spec linked from `DAS Facets.md`), so the two ends of the same
    catalog are now both consulted rather than one being re-invented.
    """
    global _facet_names_cache
    if _facet_names_cache is None:
        try:
            _facet_names_cache = {
                p.stem[4:] for p in (REPO_ROOT / "facets").glob("DAS *.md")
                if len(p.stem) > 4
            }
        except OSError:
            _facet_names_cache = set()
    return _facet_names_cache


def chk_file_association_folder_structure(target, anchor_root, args):
    """Method-3 facet folder: has {Folder}.md anchor + dispatch table linking items.

    Scope is `{Parent} {Facet}s/` where **`{Facet}` names a registered facet**
    (T561). It used to be the plural suffix alone — `re.search(r"\\s+\\w+s$")` —
    and a plural name is evidence of nothing. Measured vault-wide before the
    change and after:

        name-only          372 folders in scope, **271 fail** (73%)
        registered facet   100 folders in scope,    48 fail

    The 223 findings that go away are not judgment calls. They are
    `NJDB Databricks`, `NJDB Weights & Biases`, `@Buck Shlegeris`, `My Dates`,
    `Cap tables`, `SV Wings`, `Moms Files` — company names, a person, and
    ordinary topic folders whose last letter is `s`, each told to grow a
    dispatch table for items it does not have. The 48 that remain are real:
    mostly `{slug} Features/` folders across the fleet with no `{slug}
    Features.md` index, which [[DAS Features]] does require.

    **Nothing passing is lost**, because a folder leaving scope was either
    already passing or was never a facet folder. 49 currently-passing folders
    drop out; a pass that becomes a non-question costs nothing.

    Two residuals, stated because a silent narrowing is how a rule stops
    meaning what it says:

      1. **The `{Parent}` half of `R-file-association-03` is still unchecked.**
         Requiring the prefix to match an enclosing folder or declared slug
         would cut scope to 53 and findings to 27 — but it also drops **75**
         currently-passing folders, because multi-word facet names (`SVAR Dev
         Docs`, `SVW User Docs`) put a qualifier between parent and facet and
         the naive split reads `SVAR Dev` as the parent. That is a real
         refinement and it needs the multi-word facet question answered first.
      2. **A stray singular/plural coincidence still admits a few.**
         `2025-10-07 Derm Docs` matches because `Doc` is a facet. The parent
         test above is what would remove it, which is the argument for doing
         residual 1 rather than patching around it.

    The pebble stores that co-motivated T561 need no exemption clause here:
    there is no `DAS Pebble` facet, so all 19 `{slug} Pebbles/` folders leave
    scope with the other 223. Their other reported failure, `R-anchor-page-02`,
    was measured at **1 of 19**, not fleet-wide — [[Eli]] is the one store that
    picked up a stray 0-byte `.anchor`, and the row generalized from it.
    """
    if not target.is_dir():
        return "pass", "not a directory"
    folder = target.name
    m = re.search(r"\s+(\w+)s$", folder)
    if not m:
        return "pass", "not a plural-suffix folder"
    facet = m.group(1)
    if not ({facet, f"{facet}s"} & _registered_facet_names()):
        return "pass", f"plural suffix {facet + 's'!r} names no registered facet"
    anchor_file = target / f"{folder}.md"
    if not anchor_file.is_file():
        return "fail", f"method-3 folder missing anchor file {folder}.md"
    # R-file-association-07 asserts "the dispatch LISTS every item file", so links
    # are harvested from the DISPATCH AREA — table rows and list items — not from
    # the whole document, which is what this did (T103a). "The dispatch links its
    # items" was really "the doc mentions them somewhere", prose paragraphs and
    # fenced examples included.
    #
    # The area is deliberately WIDER than the rule's own word "table". Measured:
    # narrowing to table rows alone newly failed five folders, and one of them is
    # `examples/HBR/HBR Design/HBR Features` — this repo's reference method-3
    # folder, whose items are a bullet list under a `^^^` auto-management
    # separator. When the corpus and the rule's wording disagree and the reference
    # instance is on the corpus's side, the wording is what is narrow. A list item
    # under the masthead is a dispatch entry; a sentence in § Notes is not.
    text = _strip_fenced(_read(anchor_file))
    dispatch = [ln for ln in text.splitlines()
                if _is_table_row(ln) or re.match(r"^\s*[-*+]\s", ln)]
    if not any(re.search(r"\|\s*\[\[[^\]]+\]\]", ln) for ln in text.splitlines()
               if _is_table_row(ln)):
        return "fail", f"anchor {folder}.md has no dispatch table with wiki-links"
    items = [p for p in target.glob("*.md") if p != anchor_file]
    if not items:
        return "fail", f"method-3 folder {folder} contains no item files"
    item_names = {p.stem for p in items}
    links = re.findall(r"\[\[([^\]|]+)", "\n".join(dispatch))
    # Compared against `p.stem`, so the target must be reduced to a BASENAME, and
    # two steps of that were wrong in ways that both zeroed the intersection and so
    # produced the same "links none of the N item files" on a compliant folder.
    # `.split("/")[0]` took the FIRST path segment, but a wiki-link resolves by its
    # LAST (`[[SKA Notes/Item One]]` is `Item One`). And the capture class stops at
    # `|` while happily eating the backslash before it, so the mandated in-table
    # form `[[F001 — Thing\|F001]]` yielded `F001 — Thing\` — a stem no file has.
    linked = {link.rstrip("\\").split("#")[0].split("/")[-1].strip() for link in links}
    if not item_names & linked:
        return "fail", f"dispatch table links none of the {len(items)} item files"
    return "pass", f"folder structure OK: {len(items)} items linked"


# -- R-dated-entry-stream ------------------------------------------------------

def chk_dated_entries_reverse_chronological(target, anchor_root, args):
    """Inline H2 dated entries (## YYYY-MM-DD — Title) are newest-first."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    dates = []
    # A log doc quoting an older entry inside a fence would inject that entry's date
    # into the sequence at the point it is QUOTED, not where it belongs — and the
    # failure names two real dates, so it reads as a genuine ordering error.
    for ln in _strip_fenced(_read(f)).splitlines():
        m = re.match(r"^## (\d{4}-\d{2}-\d{2}) —", ln)
        if m:
            dates.append(m.group(1))
    if not dates:
        return "pass", "no dated entries found"
    for i in range(len(dates) - 1):
        if dates[i] < dates[i + 1]:
            return "fail", f"not reverse-chronological: {dates[i]} before {dates[i + 1]}"
    return "pass", f"all {len(dates)} entries reverse-chronological"


def chk_dated_entry_file_naming(target, anchor_root, args):
    """Method-3 dated entry file matches 'YYYY-MM-DD — Title.md'; H1 omits the date."""
    if target.is_dir():
        return "pass", "directory scope"
    m = re.match(r"^(\d{4}-\d{2}-\d{2}) — (.+)\.md$", target.name)
    if not m:
        return "pass", "not a dated-entry file"
    date_str, title = m.group(1), m.group(2)
    _, h1 = _head_h1(_read(target))
    if h1 is None:
        return "fail", "no H1 found in entry file"
    if h1.startswith(date_str):
        return "fail", f"H1 contains date prefix ({date_str}); expected just {title!r}"
    if h1 == title:
        return "pass", ""
    return "fail", f"H1 is {h1!r}, expected {title!r}"


# -- R-messages ----------------------------------------------------------------

def chk_h1_is_anchor_messages(target, anchor_root, args):
    """H1 matches the file's own '{prefix} Messages' name (prefix from the basename,
    e.g. 'HBR Messages.md' -> 'HBR Messages') — robust to nested anchors whose files
    carry the root slug rather than the sub-anchor folder name."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    want = Path(f).stem  # the file's own name without .md ("HBR Messages")
    _, h1 = _head_h1(_read(f))
    if h1 is None:
        return "fail", "no H1"
    return ("pass", h1) if h1 == want else ("fail", f"H1 {h1!r} is not '{want}'")


# -- R-naming (extra) ----------------------------------------------------------

def chk_folder_marker_exists(target, anchor_root, args):
    """Every nested folder with a .anchor has a matching {folder}.md marker file."""
    if not target.is_dir():
        return "error", "target must be a directory"
    failures = []
    for folder in target.rglob("*"):
        if not folder.is_dir() or "/.git/" in str(folder):
            continue
        if not (folder / ".anchor").is_file():
            continue
        if not (folder / f"{folder.name}.md").is_file():
            failures.append(f"{folder.name}/")
    if failures:
        return "fail", "missing marker files: " + ", ".join(failures)
    return "pass", ""


# -- R-md ----------------------------------------------------------------------

def chk_md_table_blank_lines(target, anchor_root, args):
    """Markdown tables need blank lines before the header and after the table."""
    if not target.is_file():
        return "pass", "not a file"
    text = _read(target)
    lines = text.splitlines()
    issues = []
    i = 0
    fenced = _fenced_mask(text)
    while i < len(lines):
        if fenced[i]:
            i += 1
            continue
        if re.match(r"^\s*\|", lines[i]) and i + 1 < len(lines) and re.match(r"^\s*\|[\s|:-]+$", lines[i + 1]):
            if i > 0 and lines[i - 1].strip():
                issues.append(f"table at line {i + 1}: no blank line before header")
            end = i + 2
            while end < len(lines) and re.match(r"^\s*\|", lines[end]):
                end += 1
            if end < len(lines) and lines[end].strip():
                issues.append(f"table at line {i + 1}: no blank line after table end (line {end + 1})")
            i = end
            continue
        i += 1
    if issues:
        return "fail", "; ".join(issues)
    return "pass", ""


def chk_md_fence_no_markdown(target, anchor_root, args):
    """R-markdown-11: a fenced code block must not contain markdown meant to render
    (wiki-links or headings). Mechanically detectable; the *fix* needs judgment
    (re-express as live markdown), so this rule carries NO `fix::` — it messages."""
    if not target.is_file():
        return "pass", "not a file"
    text = _read(target)
    # Fence pairing comes from `_FENCE_RE`, not a local toggle. The toggle this
    # replaced tested `startswith("```")`, which is blind twice over: a `~~~`
    # fence was never a fence at all, so its contents were never inspected AND a
    # ``` line inside one flipped the toggle, exempting or checking every fence
    # below it at random. That is the same defect `_strip_fenced` was cured of
    # earlier in F296, left standing in the one checker whose whole subject is
    # fences. `_FENCE_RE` also runs an unclosed fence to end-of-document the way
    # CommonMark does; the toggle silently dropped that fence's body on the floor.
    for m in _FENCE_RE.finditer(text):
        inner = m.group(0).split("\n")
        opener, inner = inner[0], inner[1:]
        # The info string is whatever follows the fence-character run. A
        # language-tagged fence (```python, ~~~bash, ```json …) is literal source
        # and is EXEMPT — code legitimately contains `[[` (a regex) or `#` (a
        # comment). Only fences meant to SHOW rendered markdown — untagged, or
        # tagged `markdown`/`md` — are checked.
        info = opener.strip().lstrip(m.group(1)[0]).strip().lower()
        if info and info not in ("markdown", "md"):
            continue
        if inner and re.match(r"^[ \t]{0,3}" + re.escape(m.group(1)) + r"[ \t]*$", inner[-1]):
            inner = inner[:-1]  # drop the closer; an unclosed fence has none
        # De-indent the body by the OPENER's own indent, then probe at column zero.
        # Both halves of that are corpus-driven. A fence nested in a list item
        # carries its whole body at the fence's indent, so its `## Choice points`
        # is at column zero *relative to the fence* — probing the raw line missed
        # three real instances (`survey-skill.md`, DMUX `F026`, HA `F064`), each a
        # ```markdown block showing headings the author meant to render. But the
        # blanket `^ {0,3}` relaxation used everywhere else in F296 is WRONG here:
        # it newly failed `TPM OKR Cards.md` on `  # evaluations completed` (a
        # count symbol) and `MACAPP restic.md` on `  # Stop the job` (a shell
        # comment) — both column-zero fences whose `#` is genuinely indented and
        # genuinely not a heading. De-indenting separates the two cases exactly.
        pad = len(opener) - len(opener.lstrip())
        blob = "\n".join(ln[pad:] if ln[:pad].isspace() else ln for ln in inner)
        # `[ \t]` rather than `\s`: `\s` matches a newline, so a lone `#` on its
        # own line read as a heading.
        if "[[" in blob or re.search(r"^#{1,6}[ \t]", blob, re.M):
            line = text.count("\n", 0, m.start()) + 1
            return "fail", (f"fenced code block at line {line} contains markdown "
                            "(wiki-link or heading) — re-express as live markdown")
    return "pass", ""


def chk_md_table_pipe_escape(target, anchor_root, args):
    """R-markdown-01: a wiki-link inside a table cell must escape its pipe (`[[A\\|B]]`)."""
    if not target.is_file():
        return "pass", "not a file"
    # Test the MASKED line, report the real one (F296): a fenced literal example
    # of a table row is not a table row. `_code_masked_lines` blanks code
    # length-preservingly, so a fenced row's `|` is gone and the line numbers of
    # everything else still line up.
    hits = []
    for ln, masked in enumerate(_code_masked_lines(_read(target)), 1):
        if not masked.lstrip().startswith("|"):
            continue
        for m in _WIKILINK_RE.finditer(masked):
            # Parity, via the one shared predicate — never a local lookbehind (T224).
            if _unescaped_pipe_positions(m.group(0)):
                hits.append(f"line {ln}")
                break
    if hits:
        return "fail", "unescaped pipe in table wiki-link — " + ", ".join(hits[:5])
    return "pass", ""


def chk_md_em_dash(target, anchor_root, args):
    """R-markdown-05 (conservative): the spaced double-hyphen ` -- ` (a typed em-dash)
    outside code should be `—`. Only the spaced form is flagged — never `--flag`, `---`."""
    if not target.is_file():
        return "pass", "not a file"
    # `_mask_code`, not a local re-roll of it (F296): the hand-rolled trio here
    # paired fence runs anywhere on a line, so a zero-width-space-escaped nested
    # fence left the real inner block exposed — and `fix_md_em_dash` then rewrote
    # the code it exposed.
    # Link targets are masked on top of code (T604): the interior of a `[[…]]`
    # is a FILENAME, and converting a spaced double-hyphen there breaks the link
    # rather than improving the prose.
    masked = _mask_code(_read(target))
    masked = _blank_regions(masked, _link_target_regions(masked))
    hits = [f"line {ln}" for ln, raw in enumerate(masked.splitlines(), 1) if " -- " in raw][:5]
    if hits:
        return "fail", "spaced double-hyphen em-dash — " + ", ".join(hits)
    return "pass", ""


def chk_md_svg_embed_width(target, anchor_root, args):
    """Every ![[x.svg]] embed carries a |width hint (page-wide default |3000).
    Bare embeds render fit-to-column thumbnails. Skips code fences / inline code."""
    if not target.is_file():
        return "pass", "not a file"
    bare = []
    def _collect(seg):
        bare.extend(re.findall(r"!\[\[[^\]|]+?\.svg\]\]", seg))
        return seg
    _repl_outside_code(_read(target), _collect)
    if bare:
        return "fail", "bare SVG embed(s) missing |width hint: " + ", ".join(bare[:5])
    return "pass", ""


def _ends_with_terminal_link(s: str) -> bool:
    """True iff the *literal* last token of `s` is a link — a wiki-link closing
    `]]`, a STRUCK wiki-link closing `]]~~`, or a markdown/hook link closing the
    `)` of a `](…)` — with NO trailing whitespace, punctuation, or `^block-anchor`
    after it.

    F278. This is a deliberate line-for-line port of `ends_with_terminal_link` in
    HookAnchor (`HookAnchorApp/src/systems/anchor_tracking/links.rs:243`). The two
    tools rewrite the SAME lines, so they must share ONE canonical form — a
    second, independently-derived predicate is precisely how they drift back into
    the strip/re-pad oscillation this rule exists to end. Port, don't re-derive.

    The struck arm (`]]~~`) is HA's F135 idempotency fix and is load-bearing here
    too: strikethrough is applied to broken links AFTER padding, so a padded link
    that later goes broken re-reads as `~~[[X]]~~ `. If the predicate refused the
    struck form that space would be stranded and stripped on the next pass — a
    one-pass oscillation. Accepting both states makes the pad a fixpoint."""
    if s.endswith("]]") and "[[" in s:
        return True
    if s.endswith("]]~~") and "~~[[" in s:
        return True
    # Markdown / hook link `[text](url)`. Guard against a bare prose `)`: the `)`
    # must close a `](…)` whose `[` opens before it, and the URL must not itself
    # contain a `)`.
    if s.endswith(")"):
        open_ = s.rfind("](")
        if open_ != -1:
            url = s[open_ + 2:-1]
            if "[" in s[:open_] and ")" not in url:
                return True
    return False


def _terminal_link_pad_lines(text: str):
    """Yield `(index, line)` for the lines F278's pad applies to — prose lines
    whose terminal token is a link. Table rows, fenced/inline code and YAML
    frontmatter are excluded (see `chk_md_terminal_link_pad` for why tables are
    `ha`'s job, not this rule's)."""
    lines = text.split("\n")
    masked = _mask_code(text).split("\n")
    start = 0
    if lines and lines[0].strip() == "---":       # YAML frontmatter
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    for i in range(start, len(lines)):
        raw = lines[i]
        if i < len(masked) and masked[i].strip() == "" and raw.strip() != "":
            continue                              # inside a fence / code span
        if raw.lstrip().startswith("|"):
            continue                              # table row — `ha` owns cell padding
        yield i, raw


def chk_md_terminal_link_pad(target, anchor_root, args):
    """R-markdown-16 (F278) — a prose line whose last token is a link carries
    exactly ONE trailing space.

    In Obsidian, clicking a line that ends in a link expands it to source form;
    one trailing space gives a non-link click target and kills that expansion. It
    is invisible in every rendered view. `ha` already stamps this form on the
    content it generates (F135); this rule covers the agent writes `ha` never
    rewrites, so together they cover the vault.

    NEVER two spaces — two is a markdown `<br>` hard break. The pad is only ever
    appended to a line that has no trailing space, and `_ends_with_terminal_link`
    is false once a space is present, so a second application is a no-op.

    Table rows are deliberately out of scope. A cell's canonical padded form is
    two spaces before the closing `|` (one from ordinary `| cell |` spacing, one
    from the pad), so deciding whether a cell is already padded means inferring
    that table's baseline spacing convention — and column-aligned tables use
    padding for source readability a normalizer would destroy. `ha` generates
    those cells and already pads them; this rule stays out."""
    if not target.is_file():
        return "pass", "not a file"
    hits = [str(i + 1) for i, raw in _terminal_link_pad_lines(_read(target))
            if _ends_with_terminal_link(raw)][:5]
    if hits:
        return "fail", "terminal link missing its single trailing space at line(s) " + ", ".join(hits)
    return "pass", ""


def chk_md_trailing_ws(target, anchor_root, args):
    """Trailing whitespace on a line (never content — pure normalization).

    F278 exemption: exactly ONE space following a terminal link is the canonical
    pad shared with `ha` (see `chk_md_terminal_link_pad`), not noise. Without this
    carve-out the two rules fight inside warden itself — R-markdown-16 appends the
    space on every write and R-markdown-14 strips it straight back, the
    continuous-corruption failure mode F278 was gated to avoid. Two or more
    trailing spaces remain a finding: two render as a `<br>` hard break."""
    if not target.is_file():
        return "pass", "not a file"
    hits = []
    for ln, raw in enumerate(_read(target).splitlines(), 1):
        if raw == raw.rstrip():
            continue
        if raw[:-1] == raw.rstrip() and _ends_with_terminal_link(raw.rstrip()):
            continue                              # the one sanctioned pad space
        hits.append(str(ln))
    if hits:
        return "fail", "trailing whitespace at line(s) " + ", ".join(hits[:5])
    return "pass", ""


def _mask_code(text: str) -> str:
    """Blank ``` / ~~~ fences and inline code spans (length-preserving) so
    code examples never trip prose-level markdown checks.

    A fence delimiter must OPEN ITS LINE (CommonMark allows up to three spaces
    of indent). Matching a bare ``` anywhere on a line mis-pairs on two shapes
    that both occur in this corpus:

    - Prose that names a fence inline — ``the first ```python``` block`` —
      where the run is content, not a delimiter.
    - A nested fence escaped with a zero-width space (`\\u200b```) so it renders
      literally instead of closing the block it sits inside. That is not a
      fence at all, but the old pattern paired the OUTER opener against it and
      left the real inner block unmasked. Found 2026-08-01 in
      `skills/audit/audit-markdown.md`, where it exposed 13 lines of Python to
      the prose checks and produced a phantom R-markdown-13 finding.
    """
    return _blank_regions(text, _code_regions(text))


_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")


def _indented_code_regions(text: str) -> list[tuple[int, int]]:
    """Char ranges of CommonMark INDENTED code blocks — 4+ spaces of indent,
    opened after a blank line, at top level.

    T222 defect 1. Neither `_mask_code` nor `_repl_outside_code` knew this block
    kind existed, so `fix_md_em_dash` rewrote a spaced double-hyphen INSIDE one —
    turning a git pathspec separator into an em-dash and leaving a valid-looking
    but broken command that would have shipped to another agent as instructions.
    R-markdown-05's own text scopes the rule to "a definition-list bullet (or
    prose)", so a `<pre>` block was always outside its stated intent.

    Top level is load-bearing and is why this is a scanner rather than a regex.
    CommonMark measures the four spaces from the CONTAINING BLOCK's content
    column, so a nested bullet legitimately carries four spaces of list indent and
    is prose, not code. Masking those would make the em-dash check silently blind
    across most of the corpus — a silent green, the worse failure direction. So a
    run qualifies only when the nearest preceding non-blank line is itself
    unindented and is not a bullet, which is the one case needing no block parser
    to decide.

    Measured over the vault: 1,983 lines in 132 files, 34 of them carrying
    ` -- `. Spot-checked, they are legacy notes written wholly at four spaces —
    documents markdown really does render as one `<pre>`, where an em-dash
    rewrite is both invisible and wrong. The permissive variant (drop the
    top-level test) claimed 10,333 lines and swept up ordinary nested bullets.
    """
    lines = text.split("\n")
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1
    out, i, n = [], 0, len(lines)
    while i < n:
        if re.match(r"^ {4,}\S", lines[i]) and i > 0 and lines[i - 1].strip() == "":
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            prev = lines[j] if j >= 0 else ""
            top_level = j < 0 or (not prev.startswith((" ", "\t")) and not _BULLET_RE.match(prev))
            k = i
            while k < n and (lines[k].strip() == "" or re.match(r"^ {4,}", lines[k])):
                k += 1
            while k > i and lines[k - 1].strip() == "":
                k -= 1
            if top_level:
                out.append((starts[i], starts[k - 1] + len(lines[k - 1])))
            i = k
        else:
            i += 1
    return out


def _code_regions(text: str) -> list[tuple[int, int]]:
    """THE answer to "which bytes of `text` are code" — fenced blocks, indented
    blocks, and inline spans, in that precedence.

    T222 defect 2. `chk_md_em_dash` masked with `_mask_code` while
    `fix_md_em_dash` replaced through `_repl_outside_code`, and the two spelled
    the inline-span class differently — the checker's excluded only newline, the
    replacer's excluded newline AND backtick. On a line with several spans they
    masked different regions, so the checker could report clean while the fixer
    still rewrote, and no test caught it because each was internally consistent.

    One predicate, three callers, no second derivation. This is the same
    "port, don't re-derive" discipline already written into
    `_ends_with_terminal_link`, and `_repl_outside_code` is a textbook chokepoint
    that had been bypassed by its own paired checker.
    """
    fill = "\x00"
    blank = lambda m: re.sub(r"[^\n]", fill, m.group(0))
    masked = _FENCE_RE.sub(blank, text.replace(fill, " "))
    masked = _blank_regions(masked, _indented_code_regions(masked), fill)
    masked = _SPAN_RE.sub(blank, masked)
    return [(m.start(), m.end()) for m in re.finditer(fill + "+", masked)]


def _blank_regions(text: str, regions, fill: str = " ") -> str:
    """`text` with every char in `regions` replaced by `fill`, newlines kept.
    Length-preserving, so masked and raw line up index-for-index."""
    if not regions:
        return text
    out = list(text)
    for a, b in regions:
        for i in range(a, b):
            if out[i] != "\n":
                out[i] = fill
    return "".join(out)


def _link_target_regions(text: str) -> list[tuple[int, int]]:
    r"""Char ranges of LINK TARGETS — the `[[…]]` interior up to its display pipe,
    and the `(…)` of a `[text](url)`.

    T604. A wiki-link target is a FILENAME, and a filename may legitimately hold
    a spaced double-hyphen; rewriting it to an em-dash points the link at a file
    that does not exist. That corruption is silent in all three directions at
    once — Obsidian renders a dead link as ordinary prose, the fixer reports
    success, and the write that triggered the pass was somewhere else in the file
    entirely. Caught in the act on `SV/SV People/SV Individuals/@Sports Visio.md`
    and confirmed by `git diff`. Blast radius 27 files on 2026-08-28, up from the
    14 first counted on 2026-08-11 — which is the rate it grows at while unfixed.

    Only the TARGET is masked, never the display half: display text is prose the
    reader actually sees, so ` -- ` there is exactly what R-markdown-05 is for.
    The pipe is where one stops and the other starts — and it is matched in both
    the bare `|` and the table-escaped `\|` form (R-markdown-01 escapes every
    pipe inside a table cell), because `find` stops at the `|` either way and the
    stray backslash left in front of it is target, not prose.

    Distinct from [[Tink Backlog#^T375|T375]], which fixed three CODE-masking
    defects in this same fixer: a wiki-link is not code, so none of that
    machinery ever looked at one.
    """
    regions = []
    for m in _WIKILINK_RE.finditer(text):
        start = m.start() + 2          # past the `[[`
        inner = m.group(1)
        cut = inner.find("|")
        regions.append((start, start + (len(inner) if cut == -1 else cut)))
    # `[text](url)` — the url only. The `)`-free body matches the convention
    # `_ends_with_terminal_link` already uses for the same construct.
    for m in re.finditer(r"\]\(([^)\n]*)\)", text):
        regions.append((m.start(1), m.end(1)))
    return regions


# A code-span delimiter is a backtick run matched by a run of EXACTLY the same
# length — CommonMark is explicit that a run "not preceded or followed by a
# backtick" is what delimits. The plain `` (`+)[^\n]*?\1 `` this replaced let a
# short opener close against a SUBSTRING of a longer run, which is how a doc
# writing `` ` ``` ` `` (a one-backtick span whose content is a fence marker —
# ordinary when documenting markdown) had its span parity shifted for the rest of
# the line, exposing every later backticked `<tag>` to the prose checks.
# `warden/Warden Design/Warden Semantics.md` carried two such false failures.
_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)[^\n]*?(?<!`)\1(?!`)")


# The one fence pattern (F296). Lifted out of `_mask_code` because
# `_repl_outside_code` needs the same pairing and had drifted onto the old
# unanchored `` ```[\s\S]*?``` `` — which is how `fix_md_em_dash` came to rewrite
# real code INSIDE a fence, on the on-write path, with the re-check then passing
# and the driver reporting it "fixed". Masking and replacing are different
# operations over the same structure; only the structure is shared, and it is
# shared HERE so the next one cannot drift again.
#
# The second branch is the UNCLOSED fence, and it must be `[\s\S]*\Z` rather than
# a bare `\Z`: CommonMark runs an unclosed block to the end of the document, and a
# bare `\Z` only fires when the opener happens to sit on the last line. With it,
# a stray ``` in the middle of a file matched nothing at all — so `_mask_code`
# left the rest of the file exposed, its inline-span pass then chewed the opener
# down to `` `python ``, and `fix_md_em_dash` rewrote the code below it. That is
# F296 finding 1 verbatim, surviving inside finding 1's own fix.
#
# The indent bound is `[ \t]*`, not CommonMark's `{0,3}`, and that is deliberate.
# CommonMark measures those three spaces from the containing BLOCK's content
# column, not from column zero — so a fence nested in a list item legitimately
# carries the list's indent, commonly four. Measuring from column zero instead
# made such a fence invisible: `HA F008 — Electric Anchor.md` documents a table
# inside a ```-fence indented four inside a list item, and with the strict bound
# `chk_md_table_blank_lines` read those rows as a LIVE table and demanded a blank
# line inside a code sample. Twelve vault docs carry a >=4-indented fence marker,
# eight of them wrapping a table row, heading or wiki-link — small, but every one
# of them is a doc that shows markup rather than uses it, which is the exact
# population fence-awareness exists to protect. Tracking the containing block's
# indent needs a block parser this file does not have and does not want; the cost
# of the relaxation is that a fence sitting inside a 4-space INDENTED CODE BLOCK
# is treated as a fence, and its contents were literal code either way.
_FENCE_RE = re.compile(
    r"(?m)^[ \t]*(`{3,}|~{3,})[^\n]*(?:\n[\s\S]*?^[ \t]*\1[ \t]*$|[\s\S]*\Z)")


def _fenced_mask(text: str) -> list[bool]:
    """Per-line "is this line inside a code fence" flags, marker lines included.

    T099. Seven places in this file answered that question with a private
    `in_fence` toggle, and every one of them was wrong in at least one of the
    three ways `_FENCE_RE` exists to fix: blind to `~~~` entirely, invertible by a
    ``` appearing inside a `~~~` block, and — the one that actually moved a
    verdict — reading the NEXT opener as a closer when a fence is left unclosed,
    which CommonMark runs to end-of-document instead.

    Patching them one at a time is the loop this consolidation ends: F296 fixed
    the toggle in `_strip_fenced`, then found the identical toggle still standing
    in `chk_md_fence_no_markdown` — the one checker whose entire subject is
    fences — and then found it a third time in `chk_progressive_disclosure_layout`,
    on a rule scoped `where:: always`. Three finds, three presses, one defect.

    Marker lines read True because every consumer here skips them: an opener is
    not prose, and no caller wants to see it. `_strip_fenced` and `_mask_code`
    stay separate — they BLANK text rather than classify lines, and
    `_disclosure_units` hashes the blanked form, so they cannot be collapsed into
    this without re-hashing the registry.
    """
    lines = text.splitlines()
    inside = set()
    for m in _FENCE_RE.finditer(text):
        for i in range(text.count("\n", 0, m.start()),
                       text.count("\n", 0, m.end()) + 1):
            inside.add(i)
    return [i in inside for i in range(len(lines))]


def _code_masked_lines(text: str) -> list[str]:
    """`text` split into lines with every code region blanked, length-preserved.

    For the checkers AND fixers that decide line-by-line whether a line is prose:
    zip these against the real lines, TEST the masked one, EDIT the real one. A
    fixer that tests the real line cannot tell a literal example from the thing it
    is an example of, and rewrites both — F296 finding 2, where a fenced
    `| [[A|B]] | cell |` was silently escaped to `| [[A\\|B]] |`."""
    return _mask_code(text).splitlines()


def chk_md_inline_field_value(target, anchor_root, args):
    """R-markdown-06: a `key:: value` inline field carries no second `::` in
    its value — Dataview misparses (value truncates / next field eaten).
    Fenced and inline-code occurrences are examples, not fields."""
    if not target.is_file():
        return "pass", "not a file"
    hits = [f"line {ln}" for ln, raw in enumerate(_mask_code(_read(target)).splitlines(), 1)
            if re.match(r"[a-z][a-z0-9_-]*::[^\n]*::", raw)][:5]
    if hits:
        return "fail", "second `::` inside an inline-field value — " + ", ".join(hits)
    return "pass", ""


# Real HTML elements Obsidian renders — these are intentional markup, never a
# stray tag. Everything else `<word>`-shaped outside code is eaten silently.
_HTML_ALLOW = {
    "a", "abbr", "b", "big", "blockquote", "br", "caption", "center", "cite",
    "code", "dd", "details", "div", "dl", "dt", "em", "figcaption", "figure",
    "font", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "iframe", "img",
    "ins", "kbd", "li", "mark", "ol", "p", "pre", "s", "small", "span",
    "strike", "strong", "sub", "summary", "sup", "table", "tbody", "td",
    "th", "thead", "tr", "u", "ul", "video", "audio", "source", "picture",
}
# Q002 (2026-08-01, Dan): single-letter placeholders like `F<n>` are NO LONGER
# exempt. The exemption was justified by a feared storm that measurement did not
# support — the real radius was 25 occurrences in 15 files — and the sites were
# mostly SHIPPED DAS artifacts (templates, skill docs), where a bare `<n>` parses
# as an unknown HTML element and silently VANISHES from the rendered page. That
# makes it a rendering defect in the thing a newcomer reads first, not a
# notation preference. All sites now carry backticks; T084 did the sweep.


_STRAY_TAG_RE = re.compile(
    # A `\<` is markdown's own escape and renders as a literal `<`, so it is one
    # of the remediations R-markdown-13 offers. Matching it would fail an author
    # for having taken the fix — the lookbehind is why `\<keep where, delete
    # which\>` in SKA F069 is not a finding.
    r"(?<!\\)</?([A-Za-z][A-Za-z0-9_-]*)"
    # Everything after the name up to `>`. Without this the checker saw only
    # single-token tags, so `Box<dyn Error>` and `<the actual question>` — the
    # generic named in R-markdown-13's own text, and the multi-word placeholder
    # that is the commonest form of the defect — both PASSED. The trailing
    # `[^<>\n\\]` keeps the escaped CLOSING `\>` out too, so an author who
    # escaped both ends is not half-flagged. 20 more vault docs, 0 regressions
    # (T212, measured over 8,158).
    r"(?:\s[^<>\n]*[^<>\n\\])?>")


def chk_md_stray_angle_tag(target, anchor_root, args):
    """R-markdown-13: a bare `<Identifier>` glued to a tag-name character is
    parsed as an unknown HTML element and silently disappears (often eating
    text). Known HTML tags render; code spans are literal.

    Single-letter placeholders are NOT exempt — see the Q002 note above
    `_HTML_ALLOW`. This docstring claimed they were, five lines under the
    comment recording that Dan revoked the exemption on 2026-08-01 and that
    T084 swept the sites; the code has never implemented it. A docstring that
    promises an exemption the code refuses teaches an author to argue with a
    true finding, which is the R-markdown-13 rule text's defect too (T212).
    """
    if not target.is_file() or target.suffix.lower() in (".html", ".htm"):
        return "pass", "not applicable"
    hits = []
    for ln, raw in enumerate(_mask_code(_read(target)).splitlines(), 1):
        for m in _STRAY_TAG_RE.finditer(raw):
            name = m.group(1)
            if name.lower() in _HTML_ALLOW:
                continue
            hits.append(f"line {ln} <{name}>")
            break
    if hits:
        return "fail", "stray `<tag>`-like angle brackets — " + ", ".join(hits[:5])
    return "pass", ""


# -- SVG geometry / hygiene / c4 (R-diagram-geometry, R-svg-hygiene, R-c4) -----

def _svg_root(target):
    import xml.etree.ElementTree as ET
    return ET.parse(target).getroot()


def _svg_containers_bboxes(root):
    """[(bbox, elem)] for rect/ellipse/polygon, namespace-agnostic."""
    bboxes = []
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        try:
            if tag == "rect":
                x, y = float(elem.get("x", 0)), float(elem.get("y", 0))
                w, h = float(elem.get("width", 0)), float(elem.get("height", 0))
                bboxes.append(((x, y, x + w, y + h), elem))
            elif tag == "ellipse":
                cx, cy = float(elem.get("cx", 0)), float(elem.get("cy", 0))
                rx, ry = float(elem.get("rx", 0)), float(elem.get("ry", 0))
                bboxes.append(((cx - rx, cy - ry, cx + rx, cy + ry), elem))
            elif tag == "polygon":
                pts = [float(v) for v in elem.get("points", "").replace(",", " ").split()]
                if pts:
                    xs, ys = pts[0::2], pts[1::2]
                    bboxes.append(((min(xs), min(ys), max(xs), max(ys)), elem))
        except (ValueError, TypeError):
            continue
    return bboxes


def chk_svg_geometry_overlap(target, anchor_root, args):
    """No two opaque container bboxes partially overlap (containment is OK)."""
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    try:
        bboxes = _svg_containers_bboxes(_svg_root(target))
    except Exception as e:
        return "error", f"{type(e).__name__}: {e}"

    def intersect(b1, b2):
        return b1[0] < b2[2] and b1[2] > b2[0] and b1[1] < b2[3] and b1[3] > b2[1]

    def contains(b1, b2):
        return b1[0] <= b2[0] and b1[1] <= b2[1] and b1[2] >= b2[2] and b1[3] >= b2[3]

    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            b1, b2 = bboxes[i][0], bboxes[j][0]
            if intersect(b1, b2) and not (contains(b1, b2) or contains(b2, b1)):
                return "fail", "overlapping containers detected"
    return "pass", ""


def chk_svg_label_collision(target, anchor_root, args):
    """No two <text> bounding boxes overlap."""
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    try:
        root = _svg_root(target)
    except Exception as e:
        return "error", f"{type(e).__name__}: {e}"
    bboxes = []
    for t in root.iter():
        if t.tag.split("}")[-1] != "text":
            continue
        try:
            x, y = float(t.get("x", 0)), float(t.get("y", 0))
            fs = float(t.get("font-size", 16))
        except (ValueError, TypeError):
            continue
        w = len(t.text or "") * (fs * 0.6)
        bboxes.append((x, y - fs, x + w, y))

    def intersect(b1, b2):
        return b1[0] < b2[2] and b1[2] > b2[0] and b1[1] < b2[3] and b1[3] > b2[1]

    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            if intersect(bboxes[i], bboxes[j]):
                return "fail", "text labels collide"
    return "pass", ""


def chk_svg_no_orphan_defs(target, anchor_root, args):
    """Every id under <defs> is referenced by url(#id) or a #-bearing attribute.

    A file that does not parse is R-svg-hygiene-03's finding, not this one — so
    the unparseable case answers `pass` with a pointer rather than `error`. An
    `error` verdict means *the checker malfunctioned*, and reporting one absent
    baseline twice, once in that voice, is the fault T212 fixed in
    `no_track_row_if_ecosystem_traits` on 2026-08-11.
    """
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    try:
        text = _read(target)
        root = _svg_root(target)
    except Exception as e:
        return "pass", (f"unparseable ({type(e).__name__}) — R-svg-hygiene-03 "
                        f"reports that")
    defs_ids = set()
    for elem in root.iter():
        if elem.tag.split("}")[-1] == "defs":
            for child in elem:
                if child.get("id"):
                    defs_ids.add(child.get("id"))
    if not defs_ids:
        return "pass", "no defs entries"
    referenced = set(re.findall(r"url\(#([^)]+)\)", text))
    for m in re.finditer(r'#([A-Za-z0-9_.:-]+)"', text):
        referenced.add(m.group(1))
    orphans = defs_ids - referenced
    if orphans:
        return "fail", "orphan defs ids: " + ", ".join(sorted(orphans))
    return "pass", ""


def chk_svg_validates_xml(target, anchor_root, args):
    """SVG validates as well-formed XML (via xmllint, else stdlib parse)."""
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    import subprocess
    try:
        result = subprocess.run(["xmllint", "--noout", str(target)],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "pass", ""
        return "fail", f"xmllint exited with code {result.returncode}"
    except FileNotFoundError:
        try:
            _svg_root(target)
            return "pass", "stdlib parse (xmllint unavailable)"
        except Exception as e:
            return "fail", f"XML parse error: {e}"
    except Exception as e:
        return "error", f"validation error: {e}"


def chk_svg_title_or_legend(target, anchor_root, args):
    """SVG has a title (y < y_thresh, font-size >= min_font) or a legend group.
    Args: [y_thresh=60, min_font=24]."""
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    try:
        root = _svg_root(target)
    except Exception as e:
        return "error", f"XML parse failed: {e}"
    y_thresh = int(args[0]) if len(args) > 0 else 60
    min_font = int(args[1]) if len(args) > 1 else 24
    for t in root.iter():
        tag = t.tag.split("}")[-1]
        if tag == "text":
            try:
                y = float(t.get("y", 0))
                fs = float(t.get("font-size", 0) or 0)
                if y < y_thresh and fs >= min_font:
                    return "pass", f"title at y={y}, font-size={fs}"
            except (ValueError, TypeError):
                pass
        elif tag == "g":
            gid = (t.get("id") or "").lower()
            if "legend" in gid or "key" in gid:
                return "pass", f"legend group: {gid}"
    return "fail", f"no title (y<{y_thresh}, font>={min_font}) or legend group"


def chk_facet_has_ruleset(target, anchor_root, args):
    """R-facet-spec-18: a facet spec has a ruleset — an embedded `# RULESET R-<x>`
    OR a linked sibling `[[R-<x>]]`. Either form satisfies the requirement."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Code-masked (T099, deepened by T103a): both tests here fail OPEN — a `# RULESET
    # R-x` or `[[R-x]]` shown as an EXAMPLE would satisfy the rule, and a facet spec
    # illustrating what a ruleset looks like is the single most likely doc in the
    # vault to carry one. The wrong direction to be blind in: a doc with no ruleset
    # at all passes because it explains rulesets well. `_strip_fenced` closed only
    # the fenced half — a facet naming its ruleset as an INLINE span, `` `[[R-x]]` ``,
    # in ordinary prose still passed, which is the same failure one layer down.
    t = _mask_code(_read(f))
    if re.search(r"^#+\s*RULESET\s+R-", t, re.MULTILINE):
        return "pass", "embedded ruleset"
    if re.search(r"\[\[R-[^\]|]+", t):
        return "pass", "linked sibling ruleset"
    return "fail", "no embedded # RULESET R- and no linked [[R-...]] ruleset"


def chk_facet_h1_form(target, anchor_root, args):
    """R-facet-spec-02 (mechanical part): a catalog facet's H1 reads `# DAS <Name>`.
    The singular-vs-plural judgment is left to the agent."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    _, h1 = _head_h1(_read(f))
    if h1 is None:
        return "fail", "no H1"
    return ("pass", "") if re.match(r"^DAS\s+\S", h1) else ("fail", f"H1 is not `# DAS <Name>`: {('# ' + h1)!r}")


def chk_facet_registered(target, anchor_root, args):
    """R-facet-spec-03: the facet is linked in the facet index — facets/DAS Facets.md."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    name = f.stem
    # dispatch tables use escaped pipes — `[[Name\|alias]]` — so allow an optional backslash
    pat = re.compile(r"\[\[" + re.escape(name) + r"\s*(\\?\||\]|/)")
    indices = [REPO_ROOT / "facets" / "DAS Facets.md"]
    for idx in indices:
        if idx.is_file() and pat.search(_read(idx)):
            return "pass", "registered in index"
    return "fail", f"'{name}' not linked in DAS Facets.md"


def chk_facet_tldr_if_substantial(target, anchor_root, args):
    """R-facet-spec-07: a substantial facet spec carries a **TLDR**; small specs are exempt."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Fence-stripped (T099) for the RULE count and for the TLDR probe. Fenced
    # sample rules inflate the count, so a small spec that merely explains rules
    # is judged substantial and failed; a fenced `**TLDR**` example does the
    # reverse and passes a spec that has none. Only the RULE count actually moves:
    # `_strip_fenced` blanks lines rather than removing them, so the `> 120`
    # line-count arm reads the same either way. Two docs move on the count, both
    # outside `R-facet-spec`'s `DAS *.md` scope; in scope this is preventive.
    t = _strip_fenced(_read(f))
    substantial = len(re.findall(r"^#+\s+RULE\s+R-", t, re.MULTILINE)) >= 5 or len(t.splitlines()) > 120
    if not substantial:
        return "pass", "small spec — TLDR exempt"
    if re.search(r"\*\*TLDR\*\*", t):
        return "pass", "TLDR present"
    return "fail", "substantial spec lacks a **TLDR** block"


def chk_facet_cardinality_declared(target, anchor_root, args):
    """R-facet-spec-10: the spec declares cardinality — one (per anchor) or many."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    t = _read(f)
    pats = [
        r"[Cc]ardinality[^\n]{0,60}\b(one|many)\b",                                   # "cardinality: one"
        r"cardinality[- ](one|many)",                                                  # "cardinality-one"
        r"\b(one|many|exactly one|at most one)\b[^\n]{0,40}\bper\b[^\n]{0,30}\b(anchor|system|repo|repository|bundle|project|folder)\b",  # "one per anchor", "One per system"
    ]
    if any(re.search(p, t, re.IGNORECASE) for p in pats):
        return "pass", "cardinality declared"
    return "fail", "cardinality (one / many) not declared"


def chk_facet_examples_row(target, anchor_root, args):
    """R-facet-spec-25: the masthead carries an `Examples` row with >= 1 wiki-link."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    # Fence-stripped and `{0,3}`-bounded (T103a/b), and it was wrong in BOTH
    # directions: a facet spec showing what an Examples row looks like satisfied
    # the rule with its own picture, while a legally-indented real row was
    # reported missing. `_is_table_row` is the one definition of a table row.
    for line in _strip_fenced(_read(f)).splitlines():
        if _is_table_row(line) and re.match(r"^ {0,3}\|\s*Examples\s*\|", line):
            return ("pass", "examples row present") if "[[" in line else ("fail", "Examples row has no wiki-link")
    return "fail", "no Examples row in masthead"


# --- R-backlog (F228 frontier invariants) -----------------------------------

_FRONTIER_H2S = ("Active", "Ready", "Now", "Next")
# The title run is "anything up to the closing `**`", which is NOT `[^*]*`: a
# title may legitimately carry a lone asterisk (a glob — `svg_*`, `* Agenda.md`),
# and `[^*]*` cannot cross it, so the whole row reads as bracketless. That is
# under-enforcement, not a stray warning — the bracket-keyed checks (R-backlog-02
# /-04/-05) skip a row they cannot read. Match a non-`*` char OR a `*` that does
# not begin the closing `**`; the branches are disjoint, so no backtracking.
_ROW_BRACKET_RE = re.compile(
    r"^-\s+\*\*(?:\[([^\[\]]+)\]\*\*|(?:[^*]|\*(?!\*))*\*\*\s*\[([^\[\]]+)\])")


def _backlog_rows(text):
    """(line_no, h2, row_line, subs) per top-level `- **…**` row; subs = the
    row's indented lines. A new H2 or a col-0 non-list line closes the row;
    blank lines are neutral (sub-bullets may follow a spacer)."""
    rows = []
    h2 = None
    cur = None
    fenced = _fenced_mask(text)
    for i, ln in enumerate(text.splitlines(), 1):
        # A fenced block inside a row is NEUTRAL — it neither closes the row nor
        # joins its sub-bullets (F296 finding 4). A row that documents a command
        # opens the fence at column 0, which the `elif ln.strip()` arm below read
        # as "a col-0 non-list line", closing the row and DETACHING the
        # `- **Next:**` that followed — a false "[Ready] row declares no
        # `- **Next:**` step" on a row that declares one, whose obvious
        # remediation is to add a second, duplicate Next. Keeping fenced content
        # out of `subs` also means a fenced `- **Q1 —` example is not counted as
        # one of the row's questions.
        if fenced[i - 1]:
            continue
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            h2, cur = m.group(1), None
            continue
        if re.match(r"^-\s+\*\*", ln):
            cur = [i, h2, ln, []]
            rows.append(cur)
        elif cur is not None and re.match(r"^\s+\S", ln):
            cur[3].append(ln)
        elif ln.strip():
            cur = None
    return [tuple(r) for r in rows]


def _row_bracket(row_line):
    """The row's status bracket: either leading bold (`- **[Ready]** …`) or
    immediately after the bold title (`- **Title** [Ready] — …`). Brackets
    appearing later in the body are prose mentions, not status."""
    m = _ROW_BRACKET_RE.match(row_line)
    if not m:
        return None
    return (m.group(1) or m.group(2) or "").strip()


_BE_MOD = None


def _be_mod():
    """Lazy import of the workflow skill's backlog-edit module — the producer
    of the F332 derived-row grammar, borrowed here (never copied — T120) for
    the doc-`next::` exemption."""
    global _BE_MOD
    if _BE_MOD is None:
        import importlib.util
        bp = (Path(__file__).resolve().parent.parent.parent
              / "workflow" / "scripts" / "backlog-edit.py")
        spec = importlib.util.spec_from_file_location("backlog_edit_for_plan", bp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _BE_MOD = mod
    return _BE_MOD


def chk_backlog_frontier_planned(target, anchor_root, args):
    """R-backlog-02: [Ready]/[Active] rows under frontier H2s carry a
    `- **Next:**` sub-bullet declaring the next autonomous step — OR, since
    F332 (2026-08-15), are derived rows (`→ [[doc|id]]`) whose doc carries a
    `next::` field; the regenerator deliberately drops the row-side sub-bullet
    when the doc holds the Next, so demanding both would re-create what F332
    removed."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        if h2 not in _FRONTIER_H2S:
            continue
        b = _row_bracket(row)
        if b and re.fullmatch(r"(?:\d+\s+)?(Ready|Active)", b):
            if not any(re.match(r"^\s+-\s+\*\*Next:\*\*", s) for s in subs):
                try:
                    be = _be_mod()
                    if be.read_doc_next(be.arrow_doc_path(row)):
                        continue
                except Exception:
                    pass
                failures.append(f"line {i}: [{b}] row declares no `- **Next:**` step")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_backlog_frontier_bracketed(target, anchor_root, args):
    """R-backlog-03: rows under ## Now / ## Next carry a status bracket
    (bare `[ ]` / bracketless = ungroomed frontier)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        if h2 not in ("Now", "Next"):
            continue
        b = _row_bracket(row)
        if not b:
            failures.append(f"line {i}: ungroomed frontier row (no status bracket)")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


_VERIFY_SUB_RE = re.compile(r"^\s+-\s+\*\*Verify:\*\*")
_PROBE_SUB_RE = re.compile(r"^\s+-\s+\*\*Probe:\*\*")


def chk_backlog_verify_concrete(target, anchor_root, args):
    """R-backlog-04: a `[Verify*]` row carries a `- **Verify:**` sub-bullet with
    the concrete yes/no the USER answers; a `[Watching*]` row carries that or a
    `- **Probe:**` — the F305 agent-owned deferred check and its trigger.

    The Watching half was relaxed by T237, which fixed three code sites (the
    `define` refusal, F240's ownership gate, audit-q C41) and missed two: the
    ruleset prose that is the authority they implement, and this checker. So a
    row moved to its designed `[Watching]`+Probe shape was accepted by `state`
    and then nagged by Warden on the same write — the read-the-warning-and-
    ignore-it training the audit discipline exists to prevent (ATT, 2026-08-18).

    The Verify half is deliberately NOT relaxed. `[Verify*]` is the user-owned
    family; letting a Probe satisfy it would be a way to park a user check where
    the user never sees it.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if not b:
            continue
        if b.startswith("Verify"):
            if not any(_VERIFY_SUB_RE.match(s) for s in subs):
                failures.append(f"line {i}: [{b}] row has no `- **Verify:**` question")
        elif b.startswith("Watching"):
            if not any(_VERIFY_SUB_RE.match(s) or _PROBE_SUB_RE.match(s) for s in subs):
                failures.append(
                    f"line {i}: [{b}] row has neither a `- **Verify:**` question "
                    f"nor a `- **Probe:**` agent-check")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


_TIMED_BRACKET_RE = re.compile(r"^(Waiting|Watching)\s+\d+[dh]$")
_BLOCKED_FEATURE_RE = re.compile(r"^Blocked\s+F\d+$")
_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_QNUM_SUB_RE = re.compile(r"^\s+-\s+\*\*Q\d+\b")
_DOC_LINK_RE = re.compile(r"→\s*\[\[")
# F275 — a standalone `Q<n>` row IS its own question: the number lives in the
# row header, so it needs neither an inline Q sub-bullet nor a link to a
# Q-bearing doc. `backlog-edit.check_questions_promise` already exempts these at
# write time; without the same exemption here the audit contradicts the writer
# and every Q-row `state` mints is flagged the moment it exists.
_STANDALONE_Q_ROW_RE = re.compile(r"^-\s+\*\*Q\d+\b")


def _row_body(row_line):
    """Prose after the row's status bracket, i.e. the description that follows
    the bold title + `[Bracket]`. Anchored on the bracket match so an em-dash
    *inside* the title (`F026 — Post-freeze flag-diff`) is not mistaken for the
    title→body separator."""
    m = _ROW_BRACKET_RE.match(row_line)
    rest = row_line[m.end():] if m else row_line
    parts = re.split(r"—", rest, maxsplit=1)
    return (parts[1] if len(parts) > 1 else rest).strip()


def chk_backlog_questions_have_numbered_q(target, anchor_root, args):
    """R-backlog-05: every [Questions] row keeps its bracket promise — clicking
    it lands on numbered Q<n>. Satisfied by an inline `- **Q<n>` sub-bullet OR a
    `→ [[Doc]]` link delegating the Qs to a feature doc's ## Open Questions."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if b and re.fullmatch(r"(?:\d+\s+)?Questions", b):
            if _STANDALONE_Q_ROW_RE.match(row):
                continue  # F275 — self-backing; its number is in the header
            has_inline_q = any(_QNUM_SUB_RE.match(s) for s in subs)
            has_doc_link = bool(_DOC_LINK_RE.search(row)) or any(_DOC_LINK_RE.search(s) for s in subs)
            if not (has_inline_q or has_doc_link):
                failures.append(f"line {i}: [{b}] row has no numbered Q<n> and no → [[Doc]] link")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_backlog_blocker_named(target, anchor_root, args):
    """R-backlog-06: every [Blocked]/[Waiting*]/[Watching*] row names its
    obstacle — a specific body sentence (or sub-bullet), never a bare bracket
    (the lazy-Blocked/Waiting/Watching failure mode). [Blocked F<NNN>] is exempt:
    the chained link IS the description."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if not b:
            continue
        head = b.split()[0]
        if head not in ("Blocked", "Waiting", "Watching"):
            continue
        if _BLOCKED_FEATURE_RE.match(b):          # chained form — the F<NNN> link is the description
            continue
        has_sub = any(s.strip().startswith("-") for s in subs)
        if len(_row_body(row)) < 15 and not has_sub:
            failures.append(f"line {i}: [{b}] row names no obstacle (lazy-{head})")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_backlog_timed_has_expiry_date(target, anchor_root, args):
    """R-backlog-07: every timed [Waiting Nd/Nh] / [Watching Nd/Nh] row carries
    an absolute YYYY-MM-DD date in the body — relative durations age and "1d" is
    meaningless without knowing when it was written."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if b and _TIMED_BRACKET_RE.match(b):
            blob = row + "\n" + "\n".join(subs)
            if not _DATE_RE.search(blob):
                failures.append(f"line {i}: [{b}] row has no absolute YYYY-MM-DD expiry date")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


_STEN_ANCHOR_RE = re.compile(r"^(\.\.\.|==)\s+\S")
# R-template-08's cut-line, matched leniently exactly as that rule specifies:
# the phrase `template notes` flanked by >=3 dashes, case- and spacing-
# insensitive, with the scissors optional.
#
# "DASHES OF ANY KIND" IS LITERAL, and the first draft of this read `-{3,}` —
# ASCII hyphen only. The canonical form the corpus actually uses is
# `✂ ──── template notes ──── ✂`, whose rule is U+2500 BOX DRAWINGS LIGHT
# HORIZONTAL. So the ASCII-only class matched **zero of 29** live templates,
# and because a missing cut-line makes R-template-13/-14 defer to R-template-08,
# both new checkers returned `pass` on the entire corpus while checking
# nothing. Caught by measuring the rules before trusting them; it would have
# read as a clean green forever.
_DASH = "\\-\u2010-\u2015\u2212\u2500\u2501"
_CUTLINE_RE = re.compile(
    rf"^\s*(?:✂\s*)?[{_DASH}]{{3,}}\s*template\s+notes\s*[{_DASH}]{{3,}}(?:\s*✂)?\s*$", re.I)
_STENCIL_DECL_RE = re.compile(r"^\s*stencil::\s*(\S+)\s*$")
_PATH_DECL_RE = re.compile(r"^\s*path::\s*(\S.*?)\s*$")
_STENCIL_VERSION_RE = re.compile(r"^V\d+\.\d+$")


def _is_template_file(f):
    """The ` Template` suffix prefilter of R-template-04 — title-case T."""
    return f.name.endswith(" Template.md")


def _template_notes(f):
    """The lines BELOW the cut-line, where declarations live — or None when the
    file has no cut-line at all.

    Returning None rather than [] matters: no cut-line means R-template-08 is
    the violated rule, and reporting `stencil:: missing` on such a file would
    send the author to add a declaration into a region that does not exist."""
    lines = _read(f).splitlines()
    for i, ln in enumerate(lines):
        if _CUTLINE_RE.match(ln):
            return lines[i + 1:]
    return None


def chk_template_stencil_declared(target, anchor_root, args):
    """R-template-13: a stencil template declares `stencil:: V1.0` below the
    cut-line, and that declaration — not the filename — is what makes it one.

    MIGRATION: the filename stays a fallback on purpose. Measured 2026-08-20,
    **0 of 36** templates in the vault carried this declaration, so making it
    the sole test of templatehood on day one would have made every template in
    the vault stop being a template at once. Detection is therefore `stencil::`
    if present, else the ` Template` suffix — and a template detected only by
    its suffix is a FINDING, never a non-template. The fallback comes out when
    the count reaches zero, not before.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    if not _is_template_file(f):
        return "pass", "not a template specimen"
    notes = _template_notes(f)
    if notes is None:
        return "pass", "no cut-line — R-template-08's finding, not this one"
    decl = next((m.group(1) for m in
                 (_STENCIL_DECL_RE.match(ln) for ln in notes) if m), None)
    if decl is None:
        return "fail", ("no `stencil::` declaration below the cut-line — the file is "
                        "a template only by its filename, which R-template-13 keeps "
                        "as a migration fallback. Add `stencil:: V1.0`")
    if not _STENCIL_VERSION_RE.match(decl):
        return "fail", (f"`stencil:: {decl}` is not a version — the form is `V<major>.<minor>`, "
                        f"e.g. `V1.0`. The token names which STEN grammar the specimen "
                        f"was written against, so it has to be readable as one")
    return "pass", ""


def chk_template_path_declared(target, anchor_root, args):
    """R-template-14: a template declares the path it instantiates to.

    Required even when the exemplar is empty — a blank template still has to
    say what it makes, which is the case that shows the declaration is doing
    real work rather than restating the filename.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    if not _is_template_file(f):
        return "pass", "not a template specimen"
    notes = _template_notes(f)
    if notes is None:
        return "pass", "no cut-line — R-template-08's finding, not this one"
    paths = [m.group(1) for m in (_PATH_DECL_RE.match(ln) for ln in notes) if m]
    if not paths:
        # The fix is mechanically derivable during migration, so the message
        # carries it rather than making the author reconstruct the old rule.
        derived = f.name[:-len(" Template.md")].lstrip("_")
        return "fail", (f"no `path::` declaration below the cut-line — add one naming the "
                        f"file this template produces. Derived from the current filename "
                        f"that is `path:: {derived}.md`")
    if len(paths) > 1:
        return "fail", (f"{len(paths)} `path::` declarations — a template produces one "
                        f"path; a repeatable member expresses that with a free variable "
                        f"in its path (R-template-10), not with a second line")
    return "pass", ""
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _template_first_heading(f):
    """(depth, text) of a template specimen's first heading, or None.

    THE SPINE IS SKIPPED, and that is the whole reason this is a function
    rather than a look at line one. A specimen is live markdown, so it carries
    whatever a real instance carries — and per `DAS spine` a real page may open
    with a `:>>` breadcrumb or a masthead table ABOVE its H1. Measured
    2026-08-20: of 29 file templates in the vault, 11 do not have a heading on
    their first content line, and five of those are spines doing exactly what
    the spec asks. Reading line one would have called those defects.
    """
    lines = _read(f).splitlines()
    i = 0
    if lines and lines[0].strip() == "---":                     # frontmatter
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    for ln in lines[i:]:
        # `_is_table_row` rather than `ln.startswith("|")` — T099's rule that a
        # checker must never re-spell what a table row IS. structure-lint
        # caught the hand-rolled version here on the commit that added it.
        if not ln.strip() or ln.lstrip().startswith(":>>") or _is_table_row(ln):
            continue                                            # spine
        m = _HEADING_RE.match(ln)
        return (len(m.group(1)), m.group(2)) if m else None
    return None


def chk_template_anchor_declared(target, anchor_root, args):
    """R-template-11: a specimen that opens BELOW `# H1` declares an anchor.

    Per `STEN Language`, a stencil with no anchor marker governs the **whole
    document** — that is one of the language's four defaults, and it is what
    makes the marker free for everything already written. The failure this
    catches is a specimen that opens at `##` or lower with no marker: it claims
    whole-document by the default while plainly being a fragment of one, and a
    reader cannot tell which was meant.

    The two markers are `# ... NAME` (this depth or deeper) and `# == NAME`
    (exactly this depth), specified in `STEN Language` since M2, 2026-08-07.

    PASSES DELIBERATELY: a specimen with no heading at all. Ruled legal by Dan
    2026-08-20 (T567 Q1) on the open-world default — a stencil says what is
    present, never what is absent, so a stencil that says nothing constrains
    nothing. It anchors at the document root by the same no-marker default that
    governs an `# H1`. This is a stated rule now, not the undecided
    out-of-scope note it replaced.

    Note the first-heading read stops at the first non-spine line, so a
    specimen opening on a tag line (`#pp.`) or plain prose is headingless here
    even when an `# H1` sits further down. That is intended: the anchor is read
    from where the specimen starts.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    if not f.name.startswith("_") or " Template" not in f.name:
        return "pass", "not a template specimen"
    h = _template_first_heading(f)
    if h is None:
        return "pass", "no heading — out of scope (see docstring)"
    depth, text = h
    if depth == 1 or _STEN_ANCHOR_RE.match(text):
        return "pass", ""
    return "fail", (
        f"specimen opens at `{'#' * depth}` with no anchor marker — it claims "
        f"the whole document by default while reading as a fragment. Declare "
        f"the anchor (`{'#' * depth} ... {{NAME}}` for this-depth-or-deeper, "
        f"`{'#' * depth} == {{NAME}}` for exactly-this-depth), or raise it to "
        f"`# H1` if it really does govern a whole file")


_USER_SUB_RE = re.compile(r"^\s+-\s+\*\*User:\*\*")
_USER_BRACKET_RE = re.compile(r"(?:\d+\s+)?User")
_WHY_USER_ACTION_ANNOT_RE = re.compile(r"·\s*\*why-user-action:")


def chk_backlog_user_action_named(target, anchor_root, args):
    """R-backlog-08: a `[User]` row names the user-only action it waits on, in a
    `- **User:**` sub-bullet, and says which credential or human-only faculty
    that action needs. The on-write half of F259's contract.

    TWO clauses, because C51 and the F259 mint gate are not the same check and
    mirroring only the audit would have left half the contract unstated. C51
    asks whether an ACTION is named; the gate additionally refuses a `[User]`
    entry without `--why-user-action`, which persists on the row as a
    `· *why-user-action: …*` trailer. Naming the action says what to do; the
    justification says why it cannot be the agent doing it — and that second
    claim is the one that decides whether the row belongs in a person's queue
    at all. Same two-clause shape as R-backlog-09, for the same reason.

    `[User]` is the one bracket whose whole meaning is *the agent has stopped and
    the person must act*, and its count folds into the banner's Questions bucket
    — so an unnamed one costs the user a click into a row that does not say what
    it wants. That is the shape [[DAS Backlog]] calls a thought-terminating
    label, and it is worse here than in `[Blocked]`: a blocked row is at least
    honest that nobody is being asked, whereas an unnamed `[User]` row is
    addressed to someone and does not tell them what for.

    NO DOC-SIDE EXEMPTION, deliberately, and it is worth saying why since
    R-backlog-02 sitting a few lines up HAS one. F332 moved exactly one field
    into the arrow-linked doc — `next::` — and `backlog-edit` reads only that
    one back; `- **User:**`, `- **Verify:**` and `- **Probe:**` all stay on the
    row. Granting this rule the same escape would exempt every row in the vault,
    because the field it would look for is one nothing writes.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if not (b and _USER_BRACKET_RE.fullmatch(b)):
            continue
        sub = next((s for s in subs if _USER_SUB_RE.match(s)), None)
        if sub is None:
            failures.append(
                f"line {i}: [{b}] row names no user-only action "
                f"(no `- **User:**` sub-bullet)")
        elif not _WHY_USER_ACTION_ANNOT_RE.search(sub):
            failures.append(
                f"line {i}: [{b}] row's action names no credential or human-only "
                f"faculty (no `· *why-user-action: …*`)")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


_WHY_USER_ANNOT_RE = re.compile(r"·\s*\*why-user:")

_AQ_MOD = None


def _aq_mod():
    """Lazy import of audit-q — borrowed for `_pending_q_blocks`, the slicing
    that decides which `**Q<n>` bullets are PENDING (outside any `### Resolved`
    / `### Removed` zone). That walk is already the single source of truth
    shared with `state`'s revalidate, both built on `backlog-edit` primitives;
    a third spelling here would be a third thing to drift, and it would drift
    invisibly — a checker that disagreed about which Qs are pending would nag
    resolved questions or ignore live ones, and both look like the corpus being
    wrong rather than the instrument. Import is side-effect-free (audit-q builds
    its vault index in `main`, not at module scope) and measured at ~50 ms."""
    global _AQ_MOD
    if _AQ_MOD is None:
        import importlib.util
        import sys as _sys
        aq_path = Path(__file__).resolve().parent / "audit-q.py"
        spec = importlib.util.spec_from_file_location("audit_q_for_plan", aq_path)
        mod = importlib.util.module_from_spec(spec)
        # Registered BEFORE exec, unlike `_be_mod` above, and the asymmetry is
        # load-bearing: audit-q defines `@dataclass` types, and dataclass
        # construction resolves annotations through `sys.modules[cls.__module__]`.
        # Executing an unregistered module makes that lookup return None and the
        # import dies on `'NoneType' object has no attribute '__dict__'` — a
        # message that names neither dataclasses nor the missing registration.
        _sys.modules["audit_q_for_plan"] = mod
        spec.loader.exec_module(mod)
        _AQ_MOD = mod
    return _AQ_MOD


def chk_features_question_why_ask(target, anchor_root, args):
    """R-fct-features-05: a pending Open Question in a feature doc has earned
    its way to the user. The file-scoped half of F257's gate.

    Two clauses, mirroring `backlog-edit.question_mint_gate` exactly:

      1. the question is not AGENT-TERRITORY — ordering, batching, rollback, a
         cosmetic rename. Those are never the user's call (F068), and the gate
         refuses them regardless of `--why-ask`, so this clause has no override
         either.
      2. a `Lean` / `Strong` recommendation carries a `· *why-ask: …*`
         annotation. A recommendation is the agent saying it can decide; asking
         anyway is the thing that needs justifying. `Recommendation: None` — the
         honest ask — passes untouched and always has.

    THIS IS NOT MERELY C50 PARITY; it closes a reachability hole. C50 walks
    feature docs by following `→ [[doc]]` from `[Questions]` backlog rows, so a
    doc whose row is bracketed anything else — or that has no row at all — is
    never swept, however many recommendation-bearing questions it holds. This
    rule is keyed on the FILE by `R-fct-features`' `where::`, so the row's
    bracket cannot hide it.

    Both predicates are borrowed from `backlog-edit`, the module the mint gate
    itself calls, and the pending-Q slicing from `audit-q` — nothing about the
    contract is restated here.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    try:
        be, aq = _be_mod(), _aq_mod()
    except Exception as exc:
        return "error", f"cannot borrow the F257 predicates: {exc}"
    try:
        lines = _read(f).splitlines()
    except Exception as exc:
        return "error", f"cannot read {f.name}: {exc}"
    failures = []
    for q_num, q_line, block in aq._pending_q_blocks(lines):
        if be.is_agent_territory_question(block):
            failures.append(
                f"line {q_line}: Q{q_num} is agent-territory (ordering / batching / "
                f"rollback / cosmetic rename) — decide it and announce, never ask")
        elif (be.recommendation_strength(block) in ("Lean", "Strong")
                and not be.has_why_ask_annotation(block)):
            failures.append(
                f"line {q_line}: Q{q_num} carries a recommendation but no "
                f"`· *why-ask: …*` — a lean means you can likely decide (F068)")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_backlog_verify_is_user_grade(target, anchor_root, args):
    """R-backlog-09: a surfaced `- **Verify:**` question is one only the USER
    can answer, and says which human faculty it needs. The on-write half of
    F240's ownership gate; audit-q C47 is the same check run as a sweep.

    Mirrors both of the mint gate's refusals, because they catch different
    mistakes and either alone leaves a hole:

      1. the question must not read as a MACHINE EVENT — "did the hook fire",
         "does the file exist", a bare command to run. That is agent-grade: if
         the answer lives in a file, a log, or a probe, the agent runs it now
         and the row never reaches the user's queue. Refused regardless of the
         justification, exactly as the gate refuses it — a why-user sentence
         attached to a machine question does not make it the user's.

      2. it must carry the `· *why-user: …*` annotation naming the faculty —
         taste, preference, ratification, passive-use observation. Without it
         the row asserts the user is better positioned and never says why, and
         that claim is the entire basis for spending their attention.

    The phrasing test is BORROWED from `backlog-edit.is_mechanical_verify`, the
    same function the mint gate and audit-q C47 call — never re-implemented
    (T120). A second copy of a heuristic is a second thing to drift, and the
    drift would be silent in the direction that matters: a checker that had
    quietly stopped agreeing with the writer would nag rows `state` accepts.

    Rows with a `- **Probe:**` and no `- **Verify:**` are untouched — R-backlog-04
    lets a `[Watching]` row be agent-owned, and this rule is about what reaches
    the user, so a row that surfaces nothing has nothing to justify.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    try:
        is_mech = _be_mod().is_mechanical_verify
    except Exception as exc:
        return "error", f"cannot borrow is_mechanical_verify from backlog-edit: {exc}"
    failures = []
    for i, h2, row, subs in _backlog_rows(_read(f)):
        b = _row_bracket(row)
        if not b or not (b.startswith("Verify") or b.startswith("Watching")):
            continue
        for s in subs:
            if not _VERIFY_SUB_RE.match(s):
                continue
            q = s.split("**Verify:**", 1)[1].strip()
            if is_mech(q):
                failures.append(
                    f"line {i}: [{b}] Verify question reads as a machine event — "
                    f"agent-grade, so run it now and set [Done], or [Waiting] "
                    f"with an agent-check plan")
            elif not _WHY_USER_ANNOT_RE.search(q):
                failures.append(
                    f"line {i}: [{b}] Verify question names no human faculty "
                    f"(no `· *why-user: …*`)")
            break
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


# -- R-agenda (T071 wire-up) ---------------------------------------------------
# The Agenda facet's rules were written with `check::` refs before any checker
# existed, so all nine sat inert — and inert is invisible, because
# `audit_on_write` suppresses `error` verdicts. Anchor-scope rules (03, 09) take
# the anchor root; the rest are file-scope on the `* Agenda.md` the `where::`
# clause selects.

_AGENDA_H2S = ["Purpose", "Success", "Approach", "Constraints", "Cadence"]

# A `{slug} Track` folder carries its own `.anchor`, so the anchor_root handed
# to a checker for a file living there is the FACET sub-anchor, not the project
# that owns it — `_anchor_slug` would answer "SV Track" where the rules mean
# "SV". Walk up past the facet sub-anchors to the owning anchor.
_AGENDA_FACET_SUFFIXES = (" Track", " Design", " User Docs", " Dev Docs")


def _agenda_owner(anchor_root: Path) -> Path:
    d = anchor_root
    while (any(d.name.endswith(s) for s in _AGENDA_FACET_SUFFIXES)
           and (d.parent / ".anchor").is_file()):
        d = d.parent
    return d


def _agenda_is_instance(f: Path, anchor_root: Path) -> bool:
    """Is this `* Agenda.md` actually an instance of the Agenda FACET?

    The `where::` glob is `* Agenda.md`, which also catches documents that
    merely end in the word — a research agenda, a meeting agenda. The facet is
    elective (R-agenda-10: never scaffolded), so a file is an instance when the
    anchor has evidently adopted it: named `{slug} Agenda.md` for its owning
    anchor, or sitting under that anchor's `{slug} Track/`.

    Both halves are needed, and each keeps a rule's teeth: the name test lets
    R-agenda-02 fire on `{slug} Design/{slug} Agenda.md`, and the location test
    lets R-agenda-01 fire on `{slug} Track/{slug} Agenda 2026.md`.
    """
    owner = _agenda_owner(anchor_root)
    slug = _anchor_slug(owner)
    if f.name == f"{slug} Agenda.md":
        return True
    track = f"{slug} Track"
    return f.parent.name == track or (f.parent.parent.name == track
                                      if f.parent.parent else False)


def _agenda_h2s(text: str) -> list[str]:
    """H2 titles in file order, fences skipped."""
    fenced = _fenced_mask(text)
    return [ln[3:].strip() for i, ln in enumerate(text.splitlines())
            if not fenced[i] and ln.startswith("## ")]


def chk_agenda_filename_valid(target, anchor_root, args):
    """R-agenda-01: the file is named `{slug} Agenda.md` — no qualifier suffix."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    slug = _anchor_slug(_agenda_owner(anchor_root))
    if f.name == f"{slug} Agenda.md":
        return "pass", ""
    return "fail", (f"basename is {f.name!r}, expected '{slug} Agenda.md' — "
                    "the Track dispatch, the audit, and any future scaffolder all "
                    "key on this exact name")


def chk_agenda_in_track_folder(target, anchor_root, args):
    """R-agenda-02: the Agenda lives under `{slug} Track/`, not Design, not the root."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    slug = _anchor_slug(_agenda_owner(anchor_root))
    track = f"{slug} Track"
    # Two legal shapes: `{Track}/{slug} Agenda.md` and the folder-doc form
    # `{Track}/{slug} Agenda/{slug} Agenda.md`.
    if f.parent.name == track or (f.parent.name == f"{slug} Agenda"
                                  and f.parent.parent.name == track):
        return "pass", ""
    return "fail", (f"sits in {f.parent.name!r} — Agenda is tracking metadata about the "
                    f"activity, so it belongs under '{track}/'")


def chk_agenda_single_per_anchor(target, anchor_root, args):
    """R-agenda-03: at most one Agenda per anchor, nested anchors excluded."""
    anchor_root = _agenda_owner(anchor_root)
    found = []
    for cand in anchor_root.rglob("* Agenda.md"):
        # A nested anchor owns its own Agenda; walk up to the nearest .anchor.
        d = cand.parent
        while d != anchor_root and d.parent != d:
            if (d / ".anchor").is_file() and _agenda_owner(d) == d:
                break        # a real nested anchor owns its own Agenda
            d = d.parent
        if d == anchor_root:
            found.append(cand)
    if len(found) <= 1:
        return "pass", f"{len(found)} agenda"
    rel = ", ".join(str(x.relative_to(anchor_root)) for x in sorted(found))
    return "fail", (f"{len(found)} Agendas under one anchor ({rel}) — two competing "
                    "theories of victory with nothing to say which governs")


def chk_agenda_required_h2s(target, anchor_root, args):
    """R-agenda-04: all five required H2s present (`Success` matches on its prefix)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    present = _agenda_h2s(_read(f))
    missing = [h for h in _AGENDA_H2S
               if not any(x == h or x.startswith(h) for x in present)]
    if not missing:
        return "pass", ""
    return "fail", (f"missing required H2(s): {', '.join('## ' + h for h in missing)} — "
                    "the five sections are the facet's whole content contract")


def chk_agenda_h2_order(target, anchor_root, args):
    """R-agenda-05: the required H2s appear in the declared order."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    present = _agenda_h2s(_read(f))
    seen = []
    for x in present:
        for h in _AGENDA_H2S:
            if (x == h or x.startswith(h)) and h not in seen:
                seen.append(h)
                break
    expected = [h for h in _AGENDA_H2S if h in seen]
    if seen == expected:
        return "pass", ""
    return "fail", (f"required H2s run {' → '.join(seen)}, expected "
                    f"{' → '.join(expected)} — the order is an argument, not a layout")


_AGENDA_INTERVAL = re.compile(
    r"\b(weekly|monthly|quarterly|annual(?:ly)?|every\s+\d+\s+(?:day|week|month)s?)\b",
    re.IGNORECASE)


def chk_agenda_cadence_stated(target, anchor_root, args):
    """R-agenda-06: `## Cadence` names a revisit interval."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    lines = _read(f).splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## Cadence")), None)
    if start is None:
        return "fail", "no `## Cadence` section"
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
               len(lines))
    body = "\n".join(lines[start + 1:end])
    if _AGENDA_INTERVAL.search(body):
        return "pass", ""
    return "fail", ("`## Cadence` names no interval — an Agenda has no execution "
                    "forcing-function, so the stated interval is the only thing "
                    "keeping it from rotting silently")


_AGENDA_BRACKET = re.compile(
    r"\[(Ready|Active|Blocked|Verify|Done|Questions|Waiting|Watching|Designing|Implementing)\]")
_AGENDA_BLOCKID = re.compile(r"\^[FT]\d{3}")


def chk_agenda_no_work_rows(target, anchor_root, args):
    """R-agenda-07: no workflow brackets and no work-item block anchors."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    text = _read(f)
    fenced = _fenced_mask(text)
    hits = []
    for n, line in enumerate(text.splitlines(), start=1):
        if fenced[n - 1]:
            continue
        m = _AGENDA_BRACKET.search(line) or _AGENDA_BLOCKID.search(line)
        if m:
            hits.append(f"line {n}: {m.group(0)}")
    if not hits:
        return "pass", ""
    return "fail", ("work rows in an Agenda are invisible to `state`, absent from Q.md, "
                    "and unreachable by /groom and /crank — " + "; ".join(hits[:4]))


def chk_agenda_header_shape(target, anchor_root, args):
    """R-agenda-08: frontmatter `description:` plus an `# {slug} Agenda` H1."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if not _agenda_is_instance(f, anchor_root):
        return "pass", "not an Agenda-facet instance (elective facet, not adopted here)"
    text = _read(f)
    fm = _frontmatter(text)
    problems = []
    if fm is None:
        problems.append("no YAML frontmatter")
    elif not re.search(r"^description:\s*\S", fm, re.MULTILINE):
        problems.append("frontmatter has no non-empty `description:`")
    slug = _anchor_slug(_agenda_owner(anchor_root))
    _, h1 = _head_h1(text)
    if h1 is None:
        problems.append("no H1")
    elif h1 != f"{slug} Agenda":
        problems.append(f"H1 is {('# ' + h1)!r}, expected '# {slug} Agenda'")
    return ("pass", "") if not problems else ("fail", "; ".join(problems))


def chk_agenda_track_dispatch_linked(target, anchor_root, args):
    """R-agenda-09: `{slug} Track.md` carries a row linking `[[{slug} Agenda]]`."""
    anchor_root = _agenda_owner(anchor_root)
    slug = _anchor_slug(anchor_root)
    track = anchor_root / f"{slug} Track" / f"{slug} Track.md"
    if not track.is_file():
        return "pass", "no Track dispatch page"
    # Dispatch cells escape the pipe, so allow `[[X\|alias]]` as well as `[[X]]`.
    pat = re.compile(r"\[\[" + re.escape(f"{slug} Agenda") + r"\s*(\\?\||\]|#|/)")
    if pat.search(_read(track)):
        return "pass", ""
    return "fail", (f"'{slug} Track.md' does not link [[{slug} Agenda]] — an elective "
                    "facet nothing links to is a file the next agent never opens")


# -- R-rocks (T156 wire-up) ---------------------------------------------------
# The Rocks facet shipped nine `check::` refs and no implementations — the same
# failure T071 fixed for Agenda, and it stays quiet for the same reason:
# `_needs_judgment` is a membership test, so an unresolvable ref does not error,
# it promotes the rule to billed agent judgment. Eight of the nine reached the
# F289 ghost report; the ninth never did, because `RULE R-rocks-05` was headed
# `(checked, warn)` — not one of the four tiers `_RULE_RE` admits — so the parser
# skipped the heading and folded rule 05's `check::` onto rule 04, which is why
# the report named `R-rocks-04 — rocks_member_ranked`. The tier is fixed in the
# ruleset; the warn semantics live in the checker's verdict, where they belong.
#
# Scope differs from Agenda in one way that shapes everything below. Agenda's
# `where::` selects ONE file per anchor; Rocks' selects `* Rocks/**` — every
# member of the folder. Five of the nine rules are about the FOLDER (01, 02, 03,
# 08, 09), so ungated they would emit the same verdict once per rock;
# `_rocks_spokesfile` names the single member each folder-wide verdict reports
# against, and it is the folder-note whenever there is one.

_ROCKS_SUFFIX = " Rocks"

# `{slug} Rocks/` carries its own `.anchor` and so does the `{slug} Track/` above
# it, so the anchor_root a checker is handed is one or two facet sub-anchors below
# the anchor whose slug the rules mean.
_ROCKS_FACET_SUFFIXES = _AGENDA_FACET_SUFFIXES + (_ROCKS_SUFFIX,)


def _rocks_owner(start: Path) -> Path:
    """The project anchor that owns a Rocks folder.

    Same intent as `_agenda_owner` and one step laxer: it does not require each
    step's parent to carry an `.anchor`. A Rocks checker is often handed the
    Rocks folder itself as anchor_root — one level deeper than anything the
    Agenda walk sees — and a `{slug} Track/` without its own `.anchor` is legal.
    """
    d = start if start.is_dir() else start.parent
    while any(d.name.endswith(s) for s in _ROCKS_FACET_SUFFIXES) and d.parent != d:
        d = d.parent
    return d


def _rocks_folder(f: Path) -> Path | None:
    """The nearest enclosing `* Rocks/` folder, or None when there is none.

    The `where::` glob only selects files under one, so this is the belt to that
    glob's braces — and the thing that makes an anchor-scope invocation, where
    `_as_file` hands back an entry page from somewhere else entirely, a pass
    instead of a wrong finding."""
    for d in (f if f.is_dir() else f.parent, *f.parents):
        if d.name.endswith(_ROCKS_SUFFIX):
            return d
    return None


def _rocks_is_instance(folder: Path) -> bool:
    """Is this `* Rocks/` folder an instance of the Rocks FACET?

    The facet is elective (R-rocks-10), so a folder counts only when the anchor
    has evidently adopted it: named `{slug} Rocks/` for its owning anchor, or
    sitting directly under that anchor's `{slug} Track/`. Both halves keep a
    rule's teeth, exactly as in `_agenda_is_instance` — the name test is what
    lets R-rocks-02 fire on a `{slug} Design/{slug} Rocks/`, the location test is
    what lets R-rocks-01 fire on a `{slug} Track/{slug} Big Rocks/`."""
    slug = _anchor_slug(_rocks_owner(folder))
    return (folder.name == f"{slug}{_ROCKS_SUFFIX}"
            or folder.parent.name == f"{slug} Track")


def _rocks_note(folder: Path) -> Path:
    """The folder-note the facet mandates, `{slug} Rocks.md`. It need not exist —
    that absence is R-rocks-01's finding and nobody else's."""
    slug = _anchor_slug(_rocks_owner(folder))
    return folder / f"{slug}{_ROCKS_SUFFIX}.md"


def _rocks_members(folder: Path) -> list[Path]:
    """The rock files: every `*.md` directly in the folder except the folder-note.

    Both spellings of the note are excluded — the mandated `{slug} Rocks.md` and
    the folder's own name — so a misnamed folder does not also read as a rock and
    collect a second finding for the same defect."""
    skip = {_rocks_note(folder).name, f"{folder.name}.md"}
    try:
        return sorted(p for p in folder.glob("*.md")
                      if p.is_file() and p.name not in skip)
    except OSError:
        return []


def _rocks_spokesfile(folder: Path) -> Path | None:
    """The one member a FOLDER-scope verdict is reported against.

    The folder-note when it exists — that is the document a folder-wide finding
    is actually about. Otherwise the alphabetically first `*.md`, which is stable
    across runs and always present when the selector matched anything at all;
    without this fallback R-rocks-01 would go silent in the one case it exists
    for, a Rocks folder with no folder-note."""
    note = _rocks_note(folder)
    if note.is_file():
        return note
    try:
        cands = sorted(p for p in folder.glob("*.md") if p.is_file())
    except OSError:
        return None
    return cands[0] if cands else None


def _rocks_gate(target, anchor_root, folder_scope: bool):
    """Shared preamble for every R-rocks checker.

    Returns `(file, folder, slug, None)` when the checker should run, or
    `(None, None, None, verdict)` when it should not — the target is not inside a
    `* Rocks/` folder, the folder is not an instance of the elective facet, or
    (folder-scope only) this target is not the member the folder's one verdict is
    reported against."""
    f = _as_file(target, anchor_root)
    if f is None:
        return None, None, None, ("error", "no file")
    folder = _rocks_folder(f)
    if folder is None:
        return None, None, None, ("pass", "not inside a `* Rocks/` folder")
    if not _rocks_is_instance(folder):
        return None, None, None, ("pass", "not a Rocks-facet instance "
                                          "(elective facet, not adopted here)")
    if folder_scope:
        spokes = _rocks_spokesfile(folder)
        if spokes is None:
            return None, None, None, ("pass", "empty Rocks folder")
        if f != spokes:
            return None, None, None, ("pass", "folder-scope rule — judged once, "
                                              f"on '{spokes.name}'")
    return f, folder, _anchor_slug(_rocks_owner(folder)), None


def chk_rocks_folder_named(target, anchor_root, args):
    """R-rocks-01: the folder is `{slug} Rocks/` and holds a `{slug} Rocks.md`."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    problems = []
    if folder.name != f"{slug} Rocks":
        problems.append(f"folder is {folder.name!r}, expected '{slug} Rocks' — "
                        "no qualifier suffix, no singular form")
    if not (folder / f"{slug} Rocks.md").is_file():
        problems.append(f"no folder-note '{slug} Rocks.md' inside it")
    try:
        alts = sorted(d.name for d in folder.parent.iterdir()
                      if d.is_dir() and d != folder
                      and d.name in (f"{slug} Big Rocks", f"{slug} Rock",
                                     f"{slug} Rocks", f"{slug} Priorities"))
    except OSError:
        alts = []
    if alts:
        problems.append("alternate folder(s) alongside: " + ", ".join(alts))
    if not problems:
        return "pass", ""
    return "fail", ("; ".join(problems) + " — the Track-dispatch wiring, this audit "
                    "and any roll-up into the vault-wide [[Rocks]] all key on the "
                    "exact name")


def chk_rocks_in_track_folder(target, anchor_root, args):
    """R-rocks-02: `{anchor}/{slug} Track/{slug} Rocks/` — not Design, not root."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    if folder.parent.name == f"{slug} Track":
        return "pass", ""
    return "fail", (f"sits in {folder.parent.name!r} — what the anchor is spending "
                    f"effort on is metadata about the activity, so it belongs under "
                    f"'{slug} Track/'; in Design it collapses the Track ⟺ Design "
                    "boundary and lands beside Roadmap, the neighbour it is most "
                    "often confused with")


def chk_rocks_single_per_anchor(target, anchor_root, args):
    """R-rocks-03: at most one Rocks folder per anchor, nested anchors excluded."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    owner = _rocks_owner(folder)
    found = []
    for cand in owner.rglob("* Rocks"):
        if not cand.is_dir() or _under_dot_dir(cand, owner):
            continue
        # A nested project anchor owns its own Rocks folder; walk up to the
        # nearest anchor that is not itself a facet sub-anchor.
        d = cand.parent
        while d != owner and d.parent != d:
            if (d / ".anchor").is_file() and _rocks_owner(d) == d:
                break
            d = d.parent
        if d == owner:
            found.append(cand)
    if len(found) <= 1:
        return "pass", f"{len(found)} rocks folder"
    rel = ", ".join(str(x.relative_to(owner)) for x in sorted(found))
    return "fail", (f"{len(found)} Rocks folders under one anchor ({rel}) — two "
                    "ranked lists for one anchor means two answers to what the big "
                    "chunks are, with nothing to say which governs")


# All-caps or mixed-caps of ≤5 characters — the shape that needs an expansion.
# A plain word (`Ingest`) is its own expansion and is not probed.
_ROCK_ABBR_RE = re.compile(r"^(?=.*[A-Z]{2})[A-Za-z]{1,5}$")


def _rock_gloss(line: str, abbr: str) -> bool:
    """Does this head line OPEN with a gloss — a short phrase ahead of an em dash
    that says something other than the rock's own abbreviation?"""
    if "—" not in line:
        return False
    head = line.split("—", 1)[0].strip().strip('"\'')
    words = re.findall(r"[A-Za-z][\w'-]*", head)
    return bool(words) and len(words) <= 6 and " ".join(words).casefold() != abbr.casefold()


def chk_rock_name_short_and_expanded(target, anchor_root, args):
    """R-rocks-04: a rock file is `{slug} {ABBR}.md` with `{ABBR}` ≤ 2 words, and
    an abbreviation carries its expansion in the file's head.

    Two halves, and they are not equally decidable. The NAME SHAPE is arithmetic
    — strip the slug prefix, count words — and it is the half [[DAS Rocks]] calls
    the one most likely to be lost when someone "improves" a rock's name for
    readability, so a violation is a `fail`.

    Whether a gloss actually EXPANDS the abbreviation is not mechanical, and the
    corpus is what settles that rather than a hunch: `HR` → *historical
    retrospective* is an acronym, but `TX` → *transcode*, `OBS` →
    *observability* and `LEX` → *life expectancy* are contractions. No initials
    test, prefix test or subsequence test admits all four — `transcode` contains
    no `x` — and a probe that fires on three of the four real rocks in the vault
    is noise that teaches a reader to skip the rule. So the probe checks the FORM
    those four share: a gloss phrase heading the `description:` or the H1
    orientation line, ahead of an em dash, saying something other than the file's
    own name. A missing one is a `warn`. Whether the phrase is the RIGHT
    expansion is stated in the rule and belongs to a reader, not to this
    function."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, False)
    if done:
        return done
    if f == _rocks_note(folder) or f.name == f"{folder.name}.md":
        return "pass", "folder-note, not a rock"
    stem = f.stem
    if not stem.startswith(f"{slug} "):
        return "fail", (f"{f.name!r} is not named '{slug} {{ABBR}}.md' — the rock's "
                        "wiki-link is the reusable unit and it carries the slug")
    abbr = stem[len(slug) + 1:].strip()
    words = abbr.split()
    if not words:
        return "fail", f"{f.name!r} has no rock name after the '{slug} ' prefix"
    if len(words) > 2:
        return "fail", (f"rock name {abbr!r} is {len(words)} words — at most two, "
                        "normally one. The link is reused in a narrow line whose "
                        "words after the colon carry the only current information; "
                        "a long link crowds them out")
    if not _ROCK_ABBR_RE.match(abbr):
        return "pass", f"name is {abbr!r} — not an abbreviation, nothing to expand"
    text = _read(f)
    fm = _frontmatter(text) or ""
    m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    heads = [m.group(1).strip() if m else ""]
    lines = text.splitlines()
    h1_idx, _ = _head_h1(text)
    heads += lines[h1_idx + 1:h1_idx + 11] if h1_idx is not None else lines[:10]
    if any(_rock_gloss(h, abbr) for h in heads):
        return "pass", ""
    return "warn", (f"no expansion of {abbr!r} heading the `description:` or the "
                    "orientation line under the H1 — a reader who does not "
                    "recognize the abbreviation can learn it here and nowhere else")


def _rocks_below_table(note: Path) -> list[tuple[int, str]]:
    """`(line number, line)` for every non-blank line BELOW the folder-note's
    dispatch table — the ranked list. Positional, taking the LAST table row in
    the file as the boundary, so a second small table inside the note does not
    hide the tier lines under it."""
    lines = _strip_fenced(_read(note)).splitlines()
    last = 0
    for i, ln in enumerate(lines):
        if _is_table_row(ln):
            last = i + 1
    return [(i + 1, ln) for i, ln in enumerate(lines) if i >= last and ln.strip()]


def _link_file_target(raw: str) -> str:
    """The file half of a wiki-link's inner text — alias, heading and block-id
    stripped, and the table-cell pipe escape with it."""
    return raw.replace("\\|", "|").split("|")[0].split("#")[0].split("^")[0].strip()


def _rocks_tier_links(note: Path) -> list[tuple[int, str]]:
    """`(line number, target)` for the LEADING wiki-link of each tier line.

    A tier line is a ranked-list line that opens with a wiki-link — the
    `[[HBR HR]]: gather stats` form [[HBR Rocks]] demonstrates. Leading only, and
    deliberately: a promotion marker (`**Elevated to [[Rocks]] 2026-08-06.**`,
    R-rocks-13) and the commentary an example carries below its ranked list both
    hold links that point outside the anchor, and `_resolve_doc` searches at most
    four ancestor anchor roots — so judging every link on the line would fail a
    correct file for a link no local resolver can see. The leading link is the
    rock being ranked, and its deadness is the one this rule is about."""
    out = []
    for ln, line in _rocks_below_table(note):
        # `_WIKILINK_RE.match` anchors at position 0, which IS the leading test —
        # the only preparation is dropping a list marker, since the ranked list is
        # authored bare but a bulleted one means the same thing.
        m = _WIKILINK_RE.match(re.sub(r"^\s*[-*+]\s+", "", line))
        if m:
            out.append((ln, _link_file_target(m.group(1))))
    return out


def chk_rocks_member_ranked(target, anchor_root, args):
    """R-rocks-05: every rock file is named on a tier line. WARN, not fail.

    A rock nobody has ranked is a real and transient state — the file lands
    first, the ranking follows — and the `...` catch-all keeps it reachable
    meanwhile, so this is cleanup pressure rather than a gate.

    Membership is read from EVERY wiki-link below the dispatch table, not just
    the leading ones `chk_rocks_tier_links_resolve` judges. The asymmetry is
    deliberate: each direction takes the side that cannot manufacture a false
    finding — a warning must not fire on a rock that is mentioned in some other
    shape, and a failure must not fire on a link that is not a rock."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    # Under DAS Stone the ranking lives in the CONTROL file (`{slug} Rock.md`,
    # in Track beside the folder), not on the folder page — an anchor page's top
    # is machine-maintained and the ranking must stay hand-arranged. Read it when
    # present and fall back to the folder page for groups not yet migrated.
    control = folder.parent / f"{slug} Rock.md"
    source = control if control.is_file() else _rocks_note(folder)
    if not source.is_file():
        return "pass", "no folder-note — R-rocks-01 owns that finding"
    if source == control:
        ranked = {_link_file_target(m.group(1)).casefold()
                  for line in source.read_text(encoding="utf-8").splitlines()
                  for m in _WIKILINK_RE.finditer(line)}
    else:
        ranked = {_link_file_target(m.group(1)).casefold()
                  for _, line in _rocks_below_table(source)
                  for m in _WIKILINK_RE.finditer(line)}
    missing = [p.stem for p in _rocks_members(folder) if p.stem.casefold() not in ranked]
    if not missing:
        return "pass", ""
    return "warn", ("rock file(s) on no tier line: " + ", ".join(missing[:5])
                    + " — reachable through the `...` catch-all, so this is cleanup "
                      "pressure, not a gate")


def _stone_control_suffixes() -> set:
    """`{" Rock", " Pebble"}` — the fixed WORD half of every kind's `control`
    template, which the DAS kind table guarantees is of the shape
    `{slug} WORD`. `stone` derives its own header detection the same way, so the
    two cannot drift apart."""
    out = set()
    for cfg in _stone_kinds().values():
        tmpl = cfg.get("control")
        if isinstance(tmpl, str) and "{slug}" in tmpl:
            out.add(tmpl.replace("{slug}", ""))
    return out


def chk_rocks_tier_links_resolve(target, anchor_root, args):
    """R-rocks-06: no dead tier lines — every tier line's rock link resolves.

    Reads the CONTROL file (`{slug} Rock.md`, in Track beside the folder) when
    one exists, exactly as `chk_rocks_member_ranked` does, falling back to the
    folder-note for groups not yet migrated. **Measured 2026-08-11: without this
    the rule was a vacuous pass across the whole live corpus** — all four rock
    groups had migrated their ranking to a control file, so the folder-note held
    0 tier lines while 12 sat unjudged one directory up, and the rule reported
    green on every group having evaluated nothing. That is the third time this
    ruleset has silently stopped judging (see R-rocks-04's note for the two
    parser folds), and the first where the cause was a migration the sibling
    checker made and this one did not.

    Two kinds of leading link are skipped, and both exclusions are what keep the
    migration from trading a vacuous pass for a false failure:

    - **A header** — a line whose leading link targets a CONTROL file
      (R-stone-04). The self-section header opens every control file.
      R-stone-05 reserves control-file names against stone names, so nothing
      real is skipped.
    - **Another anchor's stone.** Propagation under [[DAS feed]] is
      line-copying, so a control file legitimately carries lines naming stones
      owned elsewhere — and `_resolve_doc` searches at most four ancestor anchor
      roots, so it cannot see them. Judging them would fail a correct file for
      doing exactly what the feed DAG exists to do. Their deadness is the owning
      anchor's finding, per R-rocks-12 (every rock is owned by this anchor) and
      R-rocks-13's here-side-only scoping. No live group imports rocks yet, so
      this fires on nothing today; it is the landmine that would have armed
      itself the first time one did.
    """
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    control = folder.parent / f"{slug} Rock.md"
    note = control if control.is_file() else _rocks_note(folder)
    if not note.is_file():
        return "pass", "no folder-note — R-rocks-01 owns that finding"
    headers = _stone_control_suffixes()
    dead = []
    for ln, name in _rocks_tier_links(note):
        if not name:
            continue
        if any(name.endswith(h) for h in headers):
            continue        # a header (R-stone-04), not a ranked stone
        if not name.startswith(f"{slug} "):
            continue        # another anchor's stone, propagated in by line-copy
        if (folder / f"{name}.md").is_file():
            continue
        if _resolve_doc(name, folder) is not None:
            continue
        dead.append(f"line {ln}: [[{name}]]")
    if not dead:
        return "pass", ""
    return "fail", (f"tier line(s) in {note.name} linking a file that does not "
                    "exist — " + "; ".join(dead[:5]) + " — the ranked list is "
                    "the surface people act on, and a dead link makes it "
                    "untrustworthy at exactly that moment")


# The bracket vocabulary is one list, not two: R-agenda-07 and R-rocks-07 forbid
# the same grammar for the same reason, so the rocks side reuses `_AGENDA_BRACKET`
# rather than forking a copy that can drift out of step with it.
_ROCK_BLOCKID = re.compile(r"\^[FT]\d+")


def chk_rocks_no_work_rows(target, anchor_root, args):
    """R-rocks-07: a rock file carries no workflow brackets and mints no work item.

    Minting is what the block-anchor probe measures — `^F310` is how an F-number
    comes into existence. A rock file LINKING an already-minted feature is the
    facet's own prescribed behaviour ([[DAS Rocks]] § What a rock file holds), so
    a bare `F310` in prose is not a hit."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, False)
    if done:
        return done
    if f == _rocks_note(folder) or f.name == f"{folder.name}.md":
        return "pass", "folder-note, not a rock"
    text = _read(f)
    fenced = _fenced_mask(text)
    hits = []
    for n, line in enumerate(text.splitlines(), start=1):
        if fenced[n - 1]:
            continue
        m = _AGENDA_BRACKET.search(line) or _ROCK_BLOCKID.search(line)
        if m:
            hits.append(f"line {n}: {m.group(0)}")
    if not hits:
        return "pass", ""
    return "fail", ("a rock is a thinking surface, not a queue — work rows belong on "
                    f"'{slug} Backlog'; two surfaces both claiming to be the work "
                    "queue is how a work queue rots — " + "; ".join(hits[:4]))


def chk_rocks_dispatch_linked(target, anchor_root, args):
    """R-rocks-08: `{slug} Track.md` carries a row linking `[[{slug} Rocks]]`."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    track = _rocks_owner(folder) / f"{slug} Track" / f"{slug} Track.md"
    if not track.is_file():
        return "pass", "no Track dispatch page"
    # Dispatch cells escape the pipe, so allow `[[X\|alias]]` as well as `[[X]]`.
    pat = re.compile(r"\[\[" + re.escape(f"{slug} Rocks") + r"\s*(\\?\||\]|#|/)")
    if pat.search(_read(track)):
        return "pass", ""
    return "fail", (f"'{slug} Track.md' does not link [[{slug} Rocks]] — the folder is "
                    "elective, so nothing else guarantees it is reachable, and an "
                    "unlinked one is invisible to anyone navigating the anchor")


def chk_stone_dispatch_linked(target, anchor_root, args):
    """R-stone-07: `{slug} Track.md` carries a row linking the stone group.

    T603. The kind-generic port of `R-rocks-08`, which governed `* Rocks/`
    alone. `R-stone` generalised six of R-rocks' thirteen rules and stopped, so
    `sleeper`, `pebble` and `book` groups were unchecked on reachability — and
    this is the one of the seven with a LIVE victim. `SV Sleepers` is
    unreachable by navigation and nothing said so, while the rocks half of the
    identical defect DID fire in the same sweep on the same anchor. That
    asymmetry is the finding: two groups, one rule, one silence.

    The group folder is elective, so nothing else guarantees it is reachable. An
    unlinked group is invisible both to a person navigating the anchor and to
    the catch-all of every page above it — the catch-all deliberately omits a
    child the page already links, so a group nobody links is a group nobody
    sees.

    Judged once per group, on the control file, not once per member.
    """
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    track = _stone_owner(folder) / f"{slug} Track" / f"{slug} Track.md"
    if not track.is_file():
        return "pass", "no Track dispatch page"
    # EITHER target satisfies reachability, and the control file is the one that
    # usually does. `R-rocks-08` named the FOLDER because a rock group's folder
    # is what its Track page happens to link; measured across the vault on
    # 2026-08-28, every other kind links the CONTROL FILE instead
    # (`[[Tink Pebble]]`, singular) — which is the better target anyway, since
    # the control file is what a reader opens and the folder is storage. Porting
    # the folder-only predicate fired on 21 of 32 live groups, which is a rule
    # measuring a convention rather than a defect.
    names = [cfg["folder"].format(slug=slug), cfg["control"].format(slug=slug)]
    body = _read(track)
    for name in names:
        # A dispatch cell escapes the pipe, so accept `[[X\|alias]]` beside
        # `[[X]]`, and a heading or subpath reference beside a bare one.
        if re.search(r"\[\[" + re.escape(name) + r"\s*(\\?\||\]|#|/)", body):
            return "pass", ""
    return "fail", (f"'{slug} Track.md' links neither [[{names[1]}]] nor [[{names[0]}]] — "
                    "the group is elective, so nothing else guarantees it is reachable, "
                    "and an unlinked one is invisible to anyone navigating the anchor")


def _stone_leading_links(control: Path) -> list[tuple[int, str]]:
    """`(line number, target)` for the LEADING wiki-link of each control-file line.

    The kind-generic sibling of `_rocks_tier_links`, reading the whole control
    file rather than the region below a folder-note's table — under [[DAS
    Stone]] the control file IS the ranked list, with no table above it. Leading
    only, for the reason the rocks helper gives: a promotion marker, a feed
    annotation and ordinary commentary all carry links that point outside the
    anchor, and only the line's subject is the stone being ranked."""
    out = []
    for ln, line in enumerate(_strip_fenced(_read(control)).splitlines(), 1):
        m = _WIKILINK_RE.match(re.sub(r"^\s*[-*+]\s+", "", line))
        if m:
            out.append((ln, _link_file_target(m.group(1))))
    return out


def chk_stone_member_ranked(target, anchor_root, args):
    """R-stone-08: every member file is named somewhere in the control file. WARN.

    T603 leg 2, the kind-generic port of `R-rocks-05`. A stone nobody has ranked
    is a real and transient state — the file lands first, the line follows — so
    this is cleanup pressure rather than a gate. But it is the only pressure
    there is: a member absent from the control file is reachable from nothing a
    person reads, and until this port every non-rock kind had no such check at
    all. Measured 2026-08-28 across all 32 live groups: zero unranked members,
    which is why the evidence for this rule is its fixture and not the sweep.

    Membership is read from EVERY wiki-link in the control file, not only the
    leading ones `chk_stone_control_links_resolve` judges — the same asymmetry
    the rocks pair carries, each direction taking the side that cannot
    manufacture a false finding. A dated member (`book`) is seen exactly as a
    numbered one is: by its stem, never through the number regex, which cannot
    parse it."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    control = _stone_control(folder, slug, cfg)
    if not control.is_file():
        return "pass", "no control file — R-stone-01 owns that finding"
    ranked = {_link_file_target(m.group(1)).casefold()
              for m in _WIKILINK_RE.finditer(_strip_fenced(_read(control)))}
    missing = [p.stem for p in _stone_members(folder, slug, cfg)
               if p.stem.casefold() not in ranked]
    if not missing:
        return "pass", ""
    return "warn", (f"member file(s) on no line of {control.name}: "
                    + ", ".join(missing[:5])
                    + " — a stone the control file does not name is reachable "
                      "from nothing a person reads; cleanup pressure, not a gate")


def chk_stone_control_links_resolve(target, anchor_root, args):
    """R-stone-09: no dead lines — every line ranking one of THIS group's stones
    links a file that exists.

    T603 leg 2, the kind-generic port of `R-rocks-06`, with the same two
    exclusions and for the same reasons: a **header** (a leading link targeting
    a control file, R-stone-04) is not a ranked stone, and a line naming
    **another anchor's** stone is what a [[DAS feed]] propagation looks like —
    `_resolve_doc` cannot see across anchors, so judging it would fail a
    correct file for doing exactly what the feed exists to do. Ownership is
    read from the name: this group's stones all begin `{slug} `.

    Resolution is by name, so a dated member is judged exactly as a numbered
    one — the only test is whether `{name}.md` exists in the folder or resolves
    nearby. Measured 2026-08-28: zero dead lines across 32 live groups."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    control = _stone_control(folder, slug, cfg)
    if not control.is_file():
        return "pass", "no control file — R-stone-01 owns that finding"
    headers = _stone_control_suffixes()
    dead = []
    for ln, name in _stone_leading_links(control):
        if not name:
            continue
        if any(name.endswith(h) for h in headers):
            continue        # a header (R-stone-04), not a ranked stone
        if not name.startswith(f"{slug} "):
            continue        # another anchor's stone, propagated in by line-copy
        if (folder / f"{name}.md").is_file():
            continue
        if _resolve_doc(name, folder) is not None:
            continue
        dead.append(f"line {ln}: [[{name}]]")
    if not dead:
        return "pass", ""
    return "fail", (f"line(s) in {control.name} linking a stone that does not "
                    "exist — " + "; ".join(dead[:5]) + " — the control file is "
                    "the surface people act on, and a dead link makes it "
                    "untrustworthy at exactly that moment")


def chk_stone_single_per_kind(target, anchor_root, args):
    """R-stone-10: at most one group PER KIND under any one anchor.

    T603 leg 3, the kind-generic port of `R-rocks-03` — and the predicate is
    not the rock one widened. [[DAS Stone]] states the cardinality as *any
    number of kinds; at most one group per kind per anchor*, so `SV` holding a
    pebble, a rock and a sleeper group side by side is the design, and only a
    SECOND group of the same kind is the defect. A port that counted every
    stone folder would have fired on exactly the anchors using the facet best.

    Nested project anchors are excluded by the same walk the rock checker
    uses: a folder belongs to the nearest enclosing anchor that is not itself a
    facet sub-anchor. That exclusion is load-bearing here — `SV` encloses four
    pebble groups, and three of them belong to `A2X`, `SVP` and `SVH`.

    Measured 2026-08-28 across 32 live groups: every anchor holds one group
    per kind. Evidence is the fixture."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    owner = _stone_owner(folder)
    suffix = cfg["folder"].replace("{slug}", "")
    found = []
    for cand in owner.rglob(f"*{suffix}"):
        if not cand.is_dir() or _under_dot_dir(cand, owner):
            continue
        d = cand.parent
        while d != owner and d.parent != d:
            if (d / ".anchor").is_file() and _stone_owner(d) == d:
                break
            d = d.parent
        if d == owner:
            found.append(cand)
    if len(found) <= 1:
        return "pass", f"{len(found)} {suffix.strip()} group"
    rel = ", ".join(str(x.relative_to(owner)) for x in sorted(found))
    return "fail", (f"{len(found)} {suffix.strip()} groups under one anchor ({rel}) — "
                    "two lists of one kind for one anchor is two answers to the "
                    "same question with nothing to say which governs; a split "
                    "activity gets its own anchor, and that anchor its own group")


def chk_stone_folder_note_catchall(target, anchor_root, args):
    """R-stone-11: a group's folder-note, when it has one, carries a `...` row.

    T603 leg 4, the kind-generic port of `R-rocks-09`. Measured 2026-08-28:
    seven of 32 live groups have a folder-note — the five rock groups that
    carry their own `.anchor`, and both books, whose control file IS the
    folder-note — and all seven carry the catch-all. The other 25 have no
    folder-note at all, which [[DAS Stone]] permits, so a missing note is a
    pass here and never a finding: the rule is about the row, not the page.

    Why the row matters: the catch-all is what lets R-stone-08 stay a warning.
    A member the control file has not ranked is still reachable through it.
    Without it an unranked stone is genuinely invisible on that page."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    note = folder / f"{folder.name}.md"
    if not note.is_file():
        return "pass", "no folder-note — permitted for this kind"
    for block in _table_blocks(_strip_fenced(_read(note)).splitlines()):
        for row in block:
            cells = _row_cells(row)
            if cells and cells[0].strip() in ("...", "…"):
                return "pass", ""
    return "fail", (f"{note.name}'s dispatch table has no `...` catch-all row — "
                    "the catch-all is what keeps R-stone-08 a warning rather than "
                    "a gate; without it an unranked stone is invisible on this page")


def chk_rocks_folder_note_catchall(target, anchor_root, args):
    """R-rocks-09: the folder-note's dispatch table carries a `...` catch-all row."""
    f, folder, slug, done = _rocks_gate(target, anchor_root, True)
    if done:
        return done
    note = _rocks_note(folder)
    if not note.is_file():
        return "pass", "no folder-note — R-rocks-01 owns that finding"
    for block in _table_blocks(_strip_fenced(_read(note)).splitlines()):
        for row in block:
            cells = _row_cells(row)
            if cells and cells[0].strip() in ("...", "…"):
                return "pass", ""
    return "fail", ("the folder-note's dispatch table has no `...` catch-all row — "
                    "the catch-all is what makes R-rocks-05 a warning rather than a "
                    "gate; without it an unranked rock is genuinely invisible")


# -- R-stone (T164 wire-up) ---------------------------------------------------
# The Stone facet is `R-rocks` generalised: a pebble and a rock are the same
# shape of thing at two sizes, so these checkers are parameterised by KIND
# rather than written once per kind. Nothing below names `pebble` or `rock` —
# every per-kind fact (folder name, control-file name, stone prefix, digit
# count, the two display aliases) is read from the file `stone` itself reads,
# the DAS kind table (markdown; located by `stone_kinds_doc` in F080 config).
# A third kind therefore needs no code change
# here; it needs its folder glob added to `R-stone`'s `where::`, which is the
# one remaining place a kind is named twice.
#
# Why this cannot reuse `_rocks_gate`: that helper hardcodes `_ROCKS_SUFFIX`,
# so it reads a `{slug} Pebbles/` group as "not inside a `* Rocks/` folder" and
# returns a PASS. Wired that way, the four live pebble groups would have been
# silently exempt from a ruleset reporting itself as covering them — the same
# vacuous-green shape this whole task exists to end.

_STONE_KINDS_CACHE: dict | None = None


def _stone_kinds_path():
    """Where the kind table lives — `stone_kinds_doc` in F080 config."""
    return _stone_kinds_mod().resolve_doc_path()


def _stone_kinds_mod():
    """The workflow skill's kind-table parser, BORROWED not copied (T120).

    Both this file and `stone` read kinds through it, so the two cannot drift
    apart — which is exactly what happened while the declarations were JSON
    and `DAS Stone.md` carried a hand-kept second copy of the same table."""
    global _STONE_KINDS_MOD
    if _STONE_KINDS_MOD is None:
        import importlib.util
        mp = (Path(__file__).resolve().parent.parent.parent
              / "workflow" / "scripts" / "stone-kinds.py")
        spec = importlib.util.spec_from_file_location("stone_kinds_for_plan", mp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _STONE_KINDS_MOD = mod
    return _STONE_KINDS_MOD


_STONE_KINDS_MOD = None


def _stone_kinds() -> dict:
    """`{kind: cfg}` from the DAS kind table — the same table `stone` reads.

    An unreadable or malformed table yields `{}`, and every checker below then
    returns an explicit `error` rather than a quiet pass. A stone rule that
    cannot see its kinds has verified nothing and must not report that it has;
    a silent pass here is precisely the instrument-reads-zero failure that
    `R-rocks-03` shipped for a day.
    """
    global _STONE_KINDS_CACHE
    if _STONE_KINDS_CACHE is None:
        try:
            mod = _stone_kinds_mod()
            # F628: config-first — the `stones:` section in global.yaml is the
            # live type set once present; load_types falls back to the kind
            # table for installs without one. Same single implementation
            # `stone` uses (T120: borrowed, never copied).
            data = mod.load_types()
            _STONE_KINDS_CACHE = {
                k: v for k, v in data.items()
                if isinstance(v, dict) and "folder" in v
            }
        except Exception:
            _STONE_KINDS_CACHE = {}
    return _STONE_KINDS_CACHE


def _stone_kind_suffixes() -> dict:
    """`{" Rocks": ("rock", cfg)}` — a folder-name suffix to the kind it declares.

    Derived from each kind's `folder` template by deleting the `{slug}` token,
    so the suffix and the name `stone` mints cannot drift apart."""
    out = {}
    for kind, cfg in _stone_kinds().items():
        tmpl = cfg.get("folder")
        if isinstance(tmpl, str) and "{slug}" in tmpl:
            out[tmpl.replace("{slug}", "")] = (kind, cfg)
    return out


def _stone_owner(start: Path) -> Path:
    """The project anchor that owns a stone group.

    Same walk as `_rocks_owner`, over a suffix list that is computed rather than
    literal. A rock group carries its own `.anchor` and so does the `{slug}
    Track/` above it, so a checker is handed an anchor_root one or two facet
    sub-anchors below the anchor whose slug the rules mean. A pebble group
    carries no `.anchor` at all, and this walk is a no-op for it — which is
    correct, since its anchor_root is already the owning anchor."""
    sufs = _AGENDA_FACET_SUFFIXES + tuple(_stone_kind_suffixes())
    d = start if start.is_dir() else start.parent
    while any(d.name.endswith(s) for s in sufs) and d.parent != d:
        d = d.parent
    return d


def _stone_group(f: Path):
    """`(folder, kind, cfg)` for the nearest enclosing stone-group folder.

    `(None, None, None)` when the target is not inside one — the belt to the
    `where::` glob's braces, and what makes an anchor-scope invocation (where
    `_as_file` hands back some unrelated entry page) a pass rather than a wrong
    finding."""
    sufs = _stone_kind_suffixes()
    for d in (f if f.is_dir() else f.parent, *f.parents):
        for suf, (kind, cfg) in sufs.items():
            if d.name.endswith(suf):
                return d, kind, cfg
    return None, None, None


def _stone_is_instance(folder: Path, slug: str, cfg: dict) -> bool:
    """Is this folder an instance of the (elective) Stone facet?

    Both halves are load-bearing, exactly as in `_rocks_is_instance`: the name
    test is what lets the location rule fire on a group filed under Design, and
    the location test is what lets the name rule fire on a `{slug} Big Rocks/`
    sitting correctly under Track."""
    return (folder.name == cfg["folder"].format(slug=slug)
            or folder.parent.name == f"{slug} Track")


def _stone_control(folder: Path, slug: str, cfg: dict) -> Path:
    """The control file, `{slug} Track/{slug} {Word}.md`.

    It sits BESIDE the group folder, not inside it, so it is never itself
    selected by the `where::` glob — a folder-scope rule reads it, and reports
    against the group.

    **Except for a container-named kind**, where folder and control resolve to
    the same name and the control file is the folder note. Per [[DAS Facets]]
    (Dan, 2026-08-18): a word is singular when it names the container, plural
    when it names the elements. `Rocks` names the elements so `HBR Rock.md` has
    its own place beside `HBR Rocks/`; `Book` names the container, so
    `Sonar Book.md` can only live inside `Sonar Book/`. The glob concern above
    does not bite: `chk_stone_members_numbered` already exempts a `{folder}.md`
    inside the folder as the group's own anchor page."""
    name = cfg["control"].format(slug=slug) + ".md"
    if cfg["control"] == cfg["folder"]:
        return folder / name
    return folder.parent / name


def _stone_number_rx(slug: str, cfg: dict):
    """Matches EXACTLY `{slug} {PREFIX}{NNNN}` — digits and all, never a glob.

    `stone` carries the same regex and the same warning: for the rock kind the
    prefix is `R`, so a `{slug} {PREFIX}*` glob matches the group's own anchor
    page (`HBR Rocks.md` inside `HBR Rocks/`) for every rock group that exists.
    """
    return re.compile(
        rf"^{re.escape(slug)} {re.escape(cfg['prefix'])}(\d{{{cfg.get('digits', 4)}}})$")


def _stone_members(folder: Path, slug: str, cfg: dict) -> list[Path]:
    """Every `*.md` directly in the group folder that is meant to be a stone.

    The group's own anchor page is excluded under both spellings it can take —
    the folder's name and the owning slug's — so a misnamed folder collects one
    finding rather than also reading as a malformed stone."""
    skip = {f"{folder.name}.md", f"{cfg['folder'].format(slug=slug)}.md"}
    try:
        return sorted(p for p in folder.glob("*.md")
                      if p.is_file() and p.name not in skip)
    except OSError:
        return []


def _stone_spokesfile(folder: Path, slug: str, cfg: dict) -> Path | None:
    """The one member a FOLDER-scope verdict is reported against.

    The group's anchor page when there is one — that is the document a
    folder-wide finding is about. Otherwise the alphabetically first `*.md`,
    which is stable across runs and always present when the selector matched
    anything: the four live pebble groups have no anchor page, and without this
    fallback every folder-scope rule would go silent on exactly them."""
    page = folder / f"{folder.name}.md"
    if page.is_file():
        return page
    try:
        cands = sorted(p for p in folder.glob("*.md") if p.is_file())
    except OSError:
        return None
    return cands[0] if cands else None


def _stone_gate(target, anchor_root, folder_scope: bool):
    """Shared preamble for every R-stone checker.

    Returns `(file, folder, slug, cfg, None)` when the checker should run, or
    `(None, None, None, None, verdict)` when it should not."""
    if not _stone_kinds():
        return None, None, None, None, ("error", (
            f"no readable kind table at {_stone_kinds_path()} — R-stone is "
            "parameterised by kind and cannot judge anything without it"))
    f = _as_file(target, anchor_root)
    if f is None:
        return None, None, None, None, ("error", "no file")
    folder, _kind, cfg = _stone_group(f)
    if folder is None:
        return None, None, None, None, ("pass", "not inside a stone-group folder")
    slug = _anchor_slug(_stone_owner(folder))
    if not _stone_is_instance(folder, slug, cfg):
        return None, None, None, None, ("pass", "not a Stone-facet instance "
                                                "(elective facet, not adopted here)")
    if folder_scope:
        spokes = _stone_spokesfile(folder, slug, cfg)
        if spokes is None:
            return None, None, None, None, ("pass", "empty stone group")
        if f != spokes:
            return None, None, None, None, ("pass", "folder-scope rule — judged "
                                                    f"once, on '{spokes.name}'")
    return f, folder, slug, cfg, None


def chk_stone_group_located(target, anchor_root, args):
    """R-stone-01: the group is `{slug} Track/{slug} {Kind}s/` with its control file."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    want = cfg["folder"].format(slug=slug)
    problems = []
    if folder.name != want:
        problems.append(f"folder is {folder.name!r}, expected {want!r} — the kind's "
                        "`folder` template for this anchor's slug, no qualifier and "
                        "no singular form")
    if folder.parent.name != f"{slug} Track":
        problems.append(f"it sits in {folder.parent.name!r}, not '{slug} Track' — a "
                        "stone group is Track content, not Design content and not "
                        "an anchor-root folder")
    control = _stone_control(folder, slug, cfg)
    if not control.is_file():
        problems.append(f"no control file '{control.name}' beside it in Track — the "
                        "hand-arranged ordering is the half of the group a folder "
                        "of stone files cannot supply")
    if problems:
        return "fail", "; ".join(problems)
    return "pass", f"{folder.name}/ under {slug} Track/, control {control.name}"


def chk_stone_members_numbered(target, anchor_root, args):
    """R-stone-02: every stone file is `{slug} {PREFIX}{NNNN}`."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, False)
    if done:
        return done
    page = folder / f"{folder.name}.md"
    if f == page or f.name == f"{cfg['folder'].format(slug=slug)}.md":
        return "pass", "the group's own anchor page, not a stone"
    # A kind declares its member-naming shape in the table's `stone file` row;
    # `member` is derived from it, never written separately. A dated kind names
    # members `YYYY-MM-DD <Title>` — the date is the CREATION date and is NOT
    # the ordering key (ordering lives in the control file, which may be
    # machine-generated from any key). It satisfies R-stone-02's actual intent:
    # unique, monotonic, never recycled. Ruled by Dan 2026-08-28.
    if cfg.get("member") == "dated":
        if re.match(r"^\d{4}-\d{2}-\d{2} \S", f.stem):
            return "pass", f"{f.stem} — dated"
        return "fail", (
            f"{f.stem!r} is not `YYYY-MM-DD <Title>` — this kind declares "
            "date-named members in the DAS kind table's `stone file` row, and "
            "the date is the creation stamp that makes the name unique and "
            "non-recycling. Ordering is the control file's job, not the name's.")
    rx = _stone_number_rx(slug, cfg)
    if rx.match(f.stem):
        return "pass", f"{f.stem} — numbered"
    digits = cfg.get("digits", 4)
    return "fail", (
        f"{f.stem!r} is not `{slug} {cfg['prefix']}{'N' * digits}` — a stone is "
        "identified by a monotonic number that is never recycled, because a "
        "recycled number silently re-points every stale cross-anchor reference "
        "and a copied control line is indistinguishable from a fresh one. "
        "(Non-recycling itself is a claim about history and is not checkable "
        "from a snapshot; this is the half a file can evidence.)")


# The optional leading `-` admits the header_line wrap (`-[[X Pebble|X]]-`,
# dashes OUTSIDE the link — 2026-08-17); identity still comes from the target.
_STONE_FIRST_LINK_RX = re.compile(r"^\s*(?:-\s*)?\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")


def chk_stone_header_by_target(target, anchor_root, args):
    """R-stone-04: in the control file, what a line RENDERS as matches what its
    first link TARGETS — a header is a header by target, never by appearance.

    Since 2026-08-17 a header renders as the kind's `header_line` template with
    the wrap OUTSIDE the link and the bare slug as display: `-[[X Pebble|X]]-`.
    The wrap (not the display, which is now an unremarkable bare slug) is what
    makes a line LOOK like a header, so the appearance side of the check reads
    the whole line shape rather than the display alias."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, True)
    if done:
        return done
    control = _stone_control(folder, slug, cfg)
    if not control.is_file():
        return "pass", "no control file — R-stone-01 owns that finding"
    ctrl_word = cfg["control"].format(slug="").strip()
    num_rx = re.compile(
        rf"^([A-Za-z][A-Za-z0-9]*) {re.escape(cfg['prefix'])}"
        rf"\d{{{cfg.get('digits', 4)}}}$")
    # Shapes taken from the kind's own templates rather than spelled out here:
    # the header_line wrap around the link renders a header, `{slug}:` a stone.
    pre, _, suf = cfg.get("header_line", "{link}").partition("{link}")
    wrap_is_distinct = bool(pre.strip() or suf.strip())
    hdr_line_rx = re.compile(
        r"^\s*" + re.escape(pre) + r"\[\[[^\]]+\]\]" + re.escape(suf)
        + r"\s*(?::.*)?$")
    hdr_example = cfg.get("header_line", "{link}").format(
        link=f"[[… {ctrl_word}|…]]")
    stn_shape = re.compile("^" + re.escape(cfg["stone_alias"]).replace(
        r"\{slug\}", r".+") + "$")
    problems = []
    for n, line in enumerate(_strip_fenced(_read(control)).splitlines(), 1):
        m = _STONE_FIRST_LINK_RX.match(line)
        if not m:
            continue                      # a tier label or prose — neither, by design
        tgt = m.group(1).strip()
        disp = (m.group(2) if m.group(2) is not None else tgt).strip()
        is_hdr = tgt.endswith(f" {ctrl_word}")
        is_stn = bool(num_rx.match(tgt))
        if is_hdr:
            want_disp = cfg["header_alias"].format(slug=tgt[: -len(ctrl_word) - 1])
            if not hdr_line_rx.match(line) or disp != want_disp:
                problems.append(f"line {n} targets the control file {tgt!r} — so it "
                                f"IS a header — but renders as {line.strip()!r}, "
                                f"not {hdr_example!r}")
        elif wrap_is_distinct and hdr_line_rx.match(line):
            problems.append(f"line {n} renders as a header ({line.strip()!r}) but its "
                            f"first link targets {tgt!r}, which is not a `… {ctrl_word}` "
                            "control file")
        elif stn_shape.match(disp) and not is_stn:
            problems.append(f"line {n} renders as a stone ({disp!r}) but its first "
                            f"link targets {tgt!r}, which is not a numbered stone")
        elif is_stn and not stn_shape.match(disp):
            problems.append(f"line {n} targets the stone {tgt!r} but renders as "
                            f"{disp!r}, not {cfg['stone_alias'].format(slug='…')!r}")
    if problems:
        return "fail", (f"{control.name}: " + "; ".join(problems[:4])
                        + (f" (+{len(problems) - 4} more)" if len(problems) > 4 else "")
                        + " — identity comes from the link target, and a line whose "
                          "appearance disagrees with its target misleads every reader "
                          "who scans the list instead of resolving it")
    return "pass", f"{control.name}: rendering agrees with targets"


_STONE_KEY_RX = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*::(\s|$)")


def chk_stone_keys_above_prose(target, anchor_root, args):
    """R-stone-06: a stone's `key:: value` lines all precede its prose."""
    f, folder, slug, cfg, done = _stone_gate(target, anchor_root, False)
    if done:
        return done
    if f == folder / f"{folder.name}.md" or not _stone_number_rx(slug, cfg).match(f.stem):
        return "pass", "not a stone file — R-stone-02 owns any naming finding"
    lines = _read(f).splitlines()
    i, in_fm = 0, False
    if lines and lines[0].strip() == "---":         # frontmatter is not prose
        in_fm = True
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    prose_at = None
    for n, line in enumerate(lines[i:], i + 1):
        if not line.strip():
            continue
        if _STONE_KEY_RX.match(line):
            if prose_at is not None:
                return "fail", (
                    f"`{line.split('::')[0]}::` is at line {n}, below prose that "
                    f"starts at line {prose_at} — keys sit at the top of a stone, "
                    "above the body, so a reader (and the parser) can take the whole "
                    "key block without scanning the file")
            continue
        if prose_at is None:
            prose_at = n
    keys = sum(1 for ln in lines[i:] if _STONE_KEY_RX.match(ln))
    note = f"{keys} key line(s) above the body" if keys else "no key lines"
    return "pass", note + (" (after frontmatter)" if in_fm else "")


# -- R-md-03 / R-code-repository-02 / R-versions-01 (T071 wire-up) -------------

def chk_no_git_probe_fallback(target, anchor_root, args):
    """R-code-repository-02: a `code`-trait anchor with no `code:` key is an error.

    The rule forbids the *fallback*, so the check asserts the misconfiguration
    the fallback would paper over: trait present, key absent. A `.git/` sitting
    at the anchor root is named in the failure because it is exactly what a
    probing resolver would have silently latched onto.
    """
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return "pass", "no .anchor"
    text = _read(dot)
    traits = re.search(r"^traits:\s*(.*)$", text, re.MULTILINE)
    has_trait = bool(traits and re.search(r"\bcode\b", traits.group(1)))
    if not has_trait:
        # A `traits:` block list also declares it.
        block = re.search(r"^traits:\s*\n((?:\s*-\s*.+\n?)+)", text, re.MULTILINE)
        has_trait = bool(block and re.search(r"^\s*-\s*code\s*$", block.group(1),
                                             re.MULTILINE))
    if not has_trait:
        return "pass", "not a code anchor"
    if re.search(r"^code:\s*\S", text, re.MULTILINE):
        return "pass", ""
    probe = " (a `.git/` sits at the anchor root — exactly what a probing " \
            "resolver would have silently latched onto)" \
            if (anchor_root / ".git").exists() else ""
    return "fail", ("declares the `code` trait but carries no `code:` key" + probe +
                    " — the key is the single source of truth; there is no "
                    "path-convention fallback and no legacy `code` symlink")


def chk_regex_basename(target, anchor_root, args):
    """R-versions-01 and friends: every file in scope has a basename matching args[0]."""
    if not args:
        return "error", "regex_basename requires a pattern argument"
    pattern = args[0]
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        return "error", f"bad pattern {pattern!r}: {exc}"
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    if rx.search(f.name):
        return "pass", ""
    return "fail", f"basename {f.name!r} does not match {pattern}"


# ── R-examples (TINK, 2026-08-08) — the gallery must be wholly invented ──────
#
# Decision: DAS Decisions § D1. A published repo authored from inside a private
# vault has a standing gradient toward real examples; it has been followed four
# separate times. These checkers are the counterweight — and they are a FLOOR,
# not a definition (R-examples-04): a marker list only ever catches identifiers
# someone thought to list.

_VAULT_MARKERS = (
    # live project slugs, word-bounded so prose like "a mux of things" is safe
    r"\b(?:DMUX|MUX|DKT|OBU|SKA|SKL|SYS|UCM|SVP|VEC|LUMEN|ATT|ATL|STEN|SONAR|Warden|MED|AIS|HA)\b",
    # product / org names
    r"DictaMUX|DictaMux|MuxUX|HookAnchor|Docket|ob-utils|SportsVisio",
    # personal identifiers
    r"Oblinger|oblinger|/Users/[a-z]|~/ob/",
)
_VAULT_RX = re.compile("|".join(_VAULT_MARKERS))


def chk_examples_no_vault_identifiers(target, anchor_root, args):
    """R-examples-01 / -02 — no vault-derived identifier in an example.

    Mentions on a markdown TABLE row are excluded on purpose. The `...` catch-all
    is an electric zone enumerating whatever files are present, so a hit there
    reports a real *file* in the gallery rather than authored prose — and the row
    cannot be edited anyway (anything written into it is discarded on the next
    rebuild). Flagging it would send the reader to fix the one line they must not
    touch. The offending file trips these rules on its own content.
    """
    try:
        text = _read(target)
    except OSError:
        return "error", "unreadable"
    bad = []
    for n, ln in enumerate(text.splitlines(), 1):
        if _is_table_row(ln):
            continue
        # The `:>>` breadcrumb is derived from where the file physically sits, not
        # authored, and R-doc-structure-01 requires it — so every example in a repo
        # nested inside a vault carries that vault's path whatever its content says.
        # That IS a real exposure, but it is one systemic fact rather than N content
        # defects, and it cannot be fixed file-by-file. Tracked separately; flagging
        # it here would bury the authored leaks this checker exists to surface.
        if ln.lstrip().startswith(":>>"):
            continue
        for m in _VAULT_RX.finditer(ln):
            bad.append(f"{n}:{m.group(0)}")
    if not bad:
        return "pass", ""
    shown = ", ".join(dict.fromkeys(bad[:6]))
    more = f" (+{len(bad) - 6} more)" if len(bad) > 6 else ""
    return "fail", (f"vault identifier(s) in example prose — {shown}{more}. "
                    "Examples are wholly invented (DAS Decisions D1): rewrite with "
                    "an invented stand-in rather than renaming the real thing.")


def chk_examples_no_drive_shaped_folder(target, anchor_root, args):
    """R-examples-03 — no `_NAME_` folder; that form is a logical-drive claim."""
    offenders = sorted({
        part for part in target.relative_to(anchor_root).parts[:-1]
        if len(part) > 2 and part.startswith("_") and part.endswith("_")
    })
    if not offenders:
        return "pass", ""
    return "fail", ("folder named " + ", ".join(offenders) +
                    " — `_NAME_` is reserved to the logical-drive vocabulary, where "
                    "it asserts a COMPLETE copy of logical drive NAME (Disk Conventions). "
                    "`_ARCHIVES_` is a real ~120 GB drive. Archive to Yore instead.")


def chk_exceptions_table_wellformed(target, anchor_root, args):
    """R-exception-discipline-05 — every row of the anchor's exception table
    parses, and the file the audit engine reads is the file the author edited.

    The whole value of an exception table is that it is trustworthy: a row with a
    typo'd rule id silently stops suppressing anything, and the finding it was
    written for reappears looking like a regression nobody accepted. So a
    malformed row is a failure of the table, reported here by the same parser the
    engine uses — never a second implementation that could disagree with it."""
    if not target.is_file():
        return "pass", ""
    if target != _exceptions_file(anchor_root):
        return "fail", (f"exception table at {target.name} is not read by the audit "
                        f"engine — the one path is "
                        f"{_exceptions_file(anchor_root).relative_to(anchor_root)}")
    rows, declined, problems = load_exceptions(anchor_root)
    if problems:
        return "fail", "; ".join(problems[:4])
    # A rule marked `confirm:: user` may not be excepted on the agent's own say-so
    # (F314, Dan 2026-08-08: "it should ask me before it puts an exception in
    # because there shouldn't be that many exceptions to the rule"). The grade IS
    # the confirmation — it is the user's act — so an ungraded row against such a
    # rule is a table that is waiting on a conversation, and it goes red until the
    # conversation happens. This is the whole enforcement surface: without it,
    # "ask first" is a sentence in a document that reads identically whether or
    # not anyone obeys it.
    unconfirmed = [r["handle"] for r in declined
                   if r["grade"] == "?" and rule_requires_user_confirmation(r["rule"])]
    if unconfirmed:
        return "fail", (f"{', '.join(unconfirmed)} propose an exception to a rule that "
                        f"requires your confirmation first (`confirm:: user`) — ask, "
                        f"then record the grade you are given")
    # F601 (D) — an A–C awarded by an agent on a `confirm:: user` rule is inert
    # (the loader never admits it) and the table goes red until the Grader cell
    # says `user`, so a row that looks granted can never sit quietly doing
    # nothing — the accepted-and-inert failure this feature exists to end.
    usurped = [f"{r['handle']} ({r['rule']}, graded by {r['grader'] or 'nobody'})"
               for r in declined if r.get("inert") == "authority"]
    if usurped:
        return "fail", (f"{'; '.join(usurped)} — only the user grades a "
                        f"`confirm:: user` rule; set the grade to `?` and ask, "
                        f"or have the user grade it (Grader = `user`)")
    detail = f"{len(rows)} approved"
    if declined:
        detail += f", {len(declined)} recorded but not suppressing"
    return "pass", detail


# --------------------------------------------------------------- R-fct-inbox
# T170. These three rules said "(checked)" for their whole life and carried no
# `check::` field, so they were agent judgment wearing a checker's label — a
# quieter failure than the one warden warns about, since `check:: missing_fn`
# earns a WARNING and no `check::` line at all earns nothing.
#
# The status vocabulary is imported from audit-q rather than restated. A second
# spelling of "what marks an entry processed" is exactly how a checker and the
# `Inbox N` banner come to disagree about which entries are pending.
# Matched against an H2's TITLE (the text `_h2_titles` returns), not the raw
# line — so the `##` spelling stays in `_H2_RE` where T099's ratchet keeps it.
_INBOX_ENTRY_RE = re.compile(r"^\d{4}-\d{2}-\d{2} — .+")
_INBOX_TAG_RE = re.compile(r"`(?:DONE|MOVED\s*→[^`]*)`")
# Tag-SHAPED: a backticked all-caps token. Used only to catch an invented or
# typo'd tag; ordinary prose backticks (`audit-q.py`, `slug`) do not match.
_INBOX_TAGLIKE_RE = re.compile(r"`([A-Z][A-Z0-9 _→+-]*)`")


def _inbox_entries(target) -> list[str]:
    """H2 titles in document order, fences skipped.

    Routed through `_h2_titles` rather than scanning for `## `: the naive form
    reads a fenced EXAMPLE of an inbox entry as a live one, which is precisely
    the class of defect T099's structure ratchet exists to stop — and it caught
    this function's first draft doing it."""
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    return [title for _, title in _h2_titles(lines)]


def chk_inbox_in_track_folder(target, anchor_root, args):
    """R-fct-inbox-01 — the Inbox sits in the anchor's Track folder.

    Co-location is the whole discoverability claim: an agent looking for an
    anchor's pending input opens `{slug} Track/` and expects it there. An Inbox
    that drifted elsewhere still parses and still counts, so nothing else in the
    system would ever report it."""
    if not target.is_file():
        return "pass", ""
    parent = target.parent.name
    if not parent.endswith(" Track"):
        return "fail", (f"Inbox sits in {parent!r}, not a `* Track/` folder — "
                        f"move it beside the anchor's other tracking surfaces")
    return "pass", f"in {parent}"


def chk_inbox_entry_headings(target, anchor_root, args):
    """R-fct-inbox-02 — every H2 is a dated entry heading.

    Tag ABSENCE is never a finding: an untagged entry is what pending means, it
    is what every `state drop` writes, and it is what `Inbox N` counts. This
    checker asserts only the heading FORM, and deliberately says nothing about
    where a tag sits, because `count_pending_inbox` accepts one anywhere in the
    entry and the two must not be able to disagree."""
    if not target.is_file():
        return "pass", ""
    bad = [h for h in _inbox_entries(target) if not _INBOX_ENTRY_RE.match(h)]
    if bad:
        return "fail", (f"{len(bad)} H2(s) are not `## YYYY-MM-DD — Topic`: "
                        + "; ".join(h[:60] for h in bad[:3]))
    n = len(_inbox_entries(target))
    return "pass", f"{n} entr{'y' if n == 1 else 'ies'}"


def chk_inbox_status_tags(target, anchor_root, args):
    """R-fct-inbox-03 — only `DONE` and `MOVED → …` appear as status tags.

    An invented tag is worse than no tag: the author believes the entry is
    processed, every consumer keys off the two sanctioned strings and so counts
    it pending forever, and nothing reports the mismatch. Scoped to the heading
    line, where tags are written — narrow enough that ordinary backticked prose
    in an entry body cannot manufacture a finding."""
    if not target.is_file():
        return "pass", ""
    bad = []
    for h in _inbox_entries(target):
        for tok in _INBOX_TAGLIKE_RE.findall(h):
            if not _INBOX_TAG_RE.search(f"`{tok}`"):
                bad.append(tok)
    if bad:
        return "fail", (f"unsanctioned status tag(s) {', '.join(repr(b) for b in bad[:3])} — "
                        f"only `DONE` and `MOVED → …` are read by anything")
    return "pass", "tags sanctioned"


# ---------------------------------------------------------------------------
# R-spine, F319 M2 — the spine checks.
#
# These are thin adapters over `spine_check.check`, deliberately. The shape
# classifier and the finding logic live in spine.py / spine_check.py, which
# md-toc.py also reads; re-implementing any of it here is how two callers come
# to disagree about what a page is. Each checker below selects ONE code from
# that one implementation.
#
# They grade `warn`, not `error`, on purpose. Turning them hard today would put
# ~900 vault pages into violation at once, the finding would stop carrying
# information, and agents would learn to scroll past it — which defeats the
# lazy-accrual milestone that depends on the check being noticed. F319 M6
# promotes them once the corpus is clean.
# ---------------------------------------------------------------------------
_SPINE_CACHE: dict = {}


def _spine_sibling(name):
    """Load one of the spine modules sitting beside this file, once.

    `spine.py` is the classifier, `spine_check.py` the detector, `spine_fix.py`
    the mover — three files, one implementation of what a spine IS. Loading
    them here rather than re-deriving shape inside audit-plan is the whole
    reason the audit and the `spine` CLI cannot drift into disagreeing.
    """
    import importlib.util
    key = "__mod__:" + name
    mod = _SPINE_CACHE.get(key)
    if mod is not None:
        return mod
    here = Path(__file__).resolve().parent
    import sys as _sys
    if str(here) not in _sys.path:
        _sys.path.insert(0, str(here))
    spec = importlib.util.spec_from_file_location(name, here / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}.py beside {here}")
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[name] = mod          # spine_fix imports spine_check by name
    spec.loader.exec_module(mod)
    _SPINE_CACHE[key] = mod
    return mod


def _spine_module():
    return _spine_sibling("spine")


def _spine_findings(f):
    """Every spine finding for one file, computed once per (path, mtime)."""
    global _SPINE_CACHE
    try:
        key = (str(f), f.stat().st_mtime_ns)
    except OSError:
        return []
    hit = _SPINE_CACHE.get(key)
    if hit is not None:
        return hit
    out = _spine_sibling("spine_check").check(f)
    _SPINE_CACHE[key] = out
    return out


def _spine_rule(code, ok_msg, grade="warn"):
    """Build a checker that reports one spine code.

    `grade` is what the rule COSTS the writer, and the two values mean very
    different things on write. `warn` never reaches the agent at all —
    `execute_on_write` surfaces only `fail` — so an advisory rule is invisible
    at the moment the page is being made, which is the moment it could have
    been fixed for free. That is not a hypothetical: [[Stones]] was created
    2026-08-10 with its H1 above the spine and a breadcrumb-first identity
    cell, and every one of these checks stayed silent (F319 § Why the write
    hook said nothing).

    So a code gets `fail` **once it has a `fix::`** — then the write repairs
    itself and the agent is told what was done, at zero cost to them. A code
    with no safe automatic repair stays `warn` until the corpus is clean,
    because a fail nobody can act on cheaply is the audit-noise trap.
    """
    def _chk(target, anchor_root, args):
        f = _as_file(target, anchor_root)
        if f is None:
            return "error", "no file"
        hits = [(ln, msg) for c, ln, msg in _spine_findings(f) if c == code]
        if not hits:
            return "pass", ok_msg
        ln, msg = hits[0]
        return grade, f"line {ln}: {msg}"
    return _chk


def _is_pointer_stub(p) -> bool:
    """Is this page a marker that just points at the real anchor page?

    46 anchor folders vault-wide hold TWO files matching the entry name — the
    anchor page and a one-line marker for the other name, so both `ESP.md` and
    `Espresso.md` resolve. Only one is the anchor page; the other is a pointer
    (`# ESP` / `(See Anchor [[Espresso]])`) and wants no spine at all.

    **Which one is the stub is not positional**, so there is no rule like "the
    slug file is the marker": in `examples/Espresso/` the slug file `ESP.md` is
    the stub, and in `Areas of Thought/` the folder-named file is, with `AOT.md`
    carrying the real page. Nor is it a phrase — matching *"Slug marker for"*
    would break the moment someone words it differently. So the test is
    structural: below the frontmatter there is an H1 and at most one other
    non-blank line, and that line points somewhere with a wiki-link. A page with
    real content never matches, however short.
    """
    # `p.h1` is the classifier's OWN, fence-aware answer to where the H1 is.
    # Re-spelling it as `startswith("# ")` here is the exact defect T099's
    # ratchet exists to catch, and it caught this one.
    rest = [l.strip() for i, l in enumerate(p.lines[p.body_start:], p.body_start)
            if l.strip() and i != p.h1]
    return len(rest) == 1 and "[[" in rest[0]


def chk_spine_h1_present(target, anchor_root, args):
    """A page that has a spine must also have an H1 beneath it.

    The spine says *where you are*; the H1 says *what this is called*. Every
    other rule in this set governs the order of those two and the sentence
    under them — and none of them noticed a page that simply never states its
    name, because they all key off an H1 that is not there. 417 pages
    vault-wide carry a spine with no H1, measured 2026-08-10.

    Auto-fixed, because the title is not a guess: it is the file's own stem,
    which is also what every `[[wiki-link]]` to this page already says.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    try:
        p = _spine_module().Spine(f)
    except Exception as e:
        return "error", f"cannot classify: {e}"
    if not p.has_spine:
        return "pass", "no spine — R-spine-09 owns this page"
    if p.h1 is not None:
        return "pass", "H1 present under the spine"
    return "fail", ("a spine with no `# H1` beneath it — the page states where "
                    "it sits but never what it is called")


def chk_mirrored_doc_has_no_spine(target, anchor_root, args):
    """R-spine-11 — a doc inside a declared mirror route carries NO spine.

    The positive half of F600, and the reason it is positive rather than an
    exemption: **an exemption and a prohibition fail in opposite directions.**
    An exemption says *do not look*, so a mirrored doc that acquires a
    breadcrumb — someone runs `spine fix` against a route not yet declared, or a
    doc is moved into a route carrying its vault masthead with it — is invisible
    forever, and the noise arrives on GitHub instead of in the audit. A
    prohibition says *look, and expect nothing*, so the same doc is a finding on
    the next pass. The exemption buys silence; the rule buys silence PLUS the
    guarantee that the silence was earned.

    Dan, 2026-08-28: *"the rule should be mirrored docs cannot have a spine,
    because it just doesn't mean anything in the receiver's environment."* A
    `:>>` breadcrumb and a dispatch masthead are built from wiki-links and
    `hook://` URIs; both render as literal noise once the file is on GitHub.

    Adoption cost, measured 2026-08-28 across the 4 resolvable routes: 184
    markdown docs, ZERO carrying a breadcrumb and ONE carrying a masthead
    (`prj/Alien Biology/Alien Biology Framework/ABIO Docs/ABIO Docs.md`). So the
    rule starts life at one finding rather than at the 138 the old direction was
    suppressing — the corpus already obeys it, and what was missing was anything
    that said so.

    No `fix::`. Stripping a spine deletes authored rows, and which of them
    belong on the vault side of the route is a judgement; a fixer that guessed
    would destroy writing that has nowhere else to live.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    try:
        mod = _spine_module()
        p = mod.Spine(f)
    except Exception as e:
        return "error", f"cannot classify: {e}"
    if not p.has_spine:
        return "pass", "no spine — correct for a mirrored doc"
    return "fail", (
        f"a mirrored doc carries a {p.shape()} spine — this file is copied into "
        f"an external repo, where a `:>>` breadcrumb and a dispatch masthead are "
        f"wiki-links and `hook://` URIs that render as literal noise. Move the "
        f"routing to a vault-side page that is not inside the route, and delete "
        f"the spine here.")


def chk_valid_spine(target, anchor_root, args):
    """Does this page open with a spine AT ALL — the one question under the
    eight shapes.

    Every other spine rule asks *which* shape and whether its parts are in
    order. This one asks only whether there is anything above the H1 to orient
    from: a `:>>` breadcrumb, or a dispatch table's identity row. A page with
    neither has no answer to "where am I", and no amount of shape-checking
    applies to it.

    **Scoped to anchor ENTRY pages**, i.e. a page that fronts its own folder.
    For those a spine is unambiguously required — the page IS the folder's
    front door. For everything else the scope is a live question (F308 Q6,
    4,941 files), and a write-time fail on an unsettled scope would land on
    every agent touching any of them. 153 of 1,275 entry pages fail this
    today, measured 2026-08-10.
    """
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    try:
        mod = _spine_module()
        p = mod.Spine(f)
    except Exception as e:
        return "error", f"cannot classify: {e}"
    if not p.fronts_folder:
        return "pass", "not an anchor entry page — spine scope is F308 Q6"
    if _is_notebook_namesake(f):
        # T556, 2026-08-20. A `<!-- notebook -->` namesake fronts a folder, so
        # `fronts_folder` is true — but [[DAS Notebook]] rules that folder is
        # NOT an anchor: "no functional `.anchor` and no dispatch table". This
        # rule's scope is anchor ENTRY pages, and a notebook narrative is not
        # one; it is the artifact stream's own front matter. Keyed to the
        # marker `nb` writes, never to the folder shape — the same key
        # `_is_state_backlog_namesake` uses, for the same reason.
        return "pass", "a notebook narrative, not an anchor entry page"
    # has_spine FIRST. A page that is nothing but a `:>>` breadcrumb passes on
    # its spine, and also matches the stub shape — reporting it as "a pointer
    # stub" would be a true verdict for a false reason, which is worse in a log
    # than a wrong verdict, because nobody re-checks a pass. 200 pages read that
    # way before this order was fixed.
    if p.has_spine:
        return "pass", f"opens with a {p.shape()} spine"
    if _is_pointer_stub(p):
        return "pass", "a pointer stub, not the anchor page it points at"
    return "fail", ("no spine at all — an anchor entry page must open with a "
                    "`:>>` breadcrumb or a dispatch-table identity row above "
                    "its H1, so a reader lands knowing where they are")


# The three that `fix_spine_position` repairs grade `fail`, so the write heals
# itself and says so. The two that need a judgment call stay `warn` until the
# corpus is clean (F319 M6 promotes them).
chk_spine_above_h1 = _spine_rule(
    "S03", "spine sits above the H1", grade="fail")
chk_identity_cell_description_first = _spine_rule(
    "S04", "identity cell leads with its description", grade="fail")
chk_orientation_line_adjoins_h1 = _spine_rule(
    "S05", "orientation line sits directly under the H1", grade="fail")
chk_masthead_over_folder_has_marker = _spine_rule(
    "S07", "no folder children are hidden")
chk_spine_heart_required = _spine_rule(
    "H02", "has a heart under its one-liner, or is short enough not to need one")
chk_marker_has_rows_below = _spine_rule(
    "S08", "marker is not degenerate")


CHECKERS = {
    # R-fct-inbox (T170) — three rules that claimed "(checked)" with no checker
    "inbox_in_track_folder": chk_inbox_in_track_folder,
    "inbox_entry_headings": chk_inbox_entry_headings,
    "inbox_status_tags": chk_inbox_status_tags,
    # R-exception-discipline (F314) — the table the engine actually reads
    "exceptions_table_wellformed": chk_exceptions_table_wellformed,
    # R-examples (TINK) — the gallery must be wholly invented
    "examples_no_vault_identifiers": chk_examples_no_vault_identifiers,
    "examples_no_drive_shaped_folder": chk_examples_no_drive_shaped_folder,
    # R-agenda (T071) — nine rules that had check:: refs but no implementation
    "agenda_filename_valid": chk_agenda_filename_valid,
    "agenda_in_track_folder": chk_agenda_in_track_folder,
    "agenda_single_per_anchor": chk_agenda_single_per_anchor,
    "agenda_required_h2s": chk_agenda_required_h2s,
    "agenda_h2_order": chk_agenda_h2_order,
    "agenda_cadence_stated": chk_agenda_cadence_stated,
    "agenda_no_work_rows": chk_agenda_no_work_rows,
    "agenda_header_shape": chk_agenda_header_shape,
    "agenda_track_dispatch_linked": chk_agenda_track_dispatch_linked,
    # R-rocks (T156) — nine more refs that had no implementation
    "rocks_folder_named": chk_rocks_folder_named,
    "rocks_in_track_folder": chk_rocks_in_track_folder,
    "rocks_single_per_anchor": chk_rocks_single_per_anchor,
    "rock_name_short_and_expanded": chk_rock_name_short_and_expanded,
    "rocks_member_ranked": chk_rocks_member_ranked,
    "rocks_tier_links_resolve": chk_rocks_tier_links_resolve,
    "rocks_no_work_rows": chk_rocks_no_work_rows,
    "rocks_dispatch_linked": chk_rocks_dispatch_linked,
    "stone_dispatch_linked": chk_stone_dispatch_linked,
    "stone_member_ranked": chk_stone_member_ranked,
    "stone_control_links_resolve": chk_stone_control_links_resolve,
    "stone_single_per_kind": chk_stone_single_per_kind,
    "stone_folder_note_catchall": chk_stone_folder_note_catchall,
    "rocks_folder_note_catchall": chk_rocks_folder_note_catchall,
    # R-stone (T164) — the kind-generic four; the other two rules of the six
    # stay `stated` on purpose (R-stone-03 is a claim about how a value was
    # CHOSEN, R-stone-05 about what the mint REFUSES — neither is content of a
    # file, and a `check::` on either would report coverage it cannot have)
    "stone_group_located": chk_stone_group_located,
    "stone_members_numbered": chk_stone_members_numbered,
    "stone_header_by_target": chk_stone_header_by_target,
    "stone_keys_above_prose": chk_stone_keys_above_prose,
    # T071 — the two other inert refs
    "no_git_probe_fallback": chk_no_git_probe_fallback,
    "regex_basename": chk_regex_basename,
    "anchor_has": chk_anchor_has,
    "entry_page_matches_slug": chk_entry_page_matches_slug,
    "frontmatter_has": chk_frontmatter_has,
    "h1_present": chk_h1_present,
    "h1_matches_slug": chk_h1_matches_slug,
    "h1_after_frontmatter": chk_h1_after_frontmatter,
    "name_slug_prefixed": chk_name_slug_prefixed,
    "slug_is_a_handle": chk_slug_is_a_handle,
    "no_blank_after_h1": chk_no_blank_after_h1,
    "breadcrumb_row": chk_breadcrumb_row,
    "design_row_iff_folder": chk_design_row_iff_folder,
    # R-doc-structure / R-dispatch-table (T008 wire-up, 2026-07-06)
    "doc_top_order": chk_doc_top_order,
    "dispatch_table_iff_anchor": chk_dispatch_table_iff_anchor,
    "dispatch_area_row": chk_dispatch_area_row,
    "dispatch_link_case_drift": chk_dispatch_link_case_drift,
    "dispatch_cell_narrative": chk_dispatch_cell_narrative,
    "dispatch_hand_link_resolves": chk_dispatch_hand_link_resolves,
    "toc_table_iff_long": chk_toc_table_iff_long,
    # R-spine-03/05 — summary presence + freshness (SKA F277)
    "summary_present_iff_complex": chk_summary_present_iff_complex,
    "summary_fresh": chk_summary_fresh,
    "regex_present": chk_regex_present,
    "regex_absent": chk_regex_absent,
    # F161 batch-2 — shared header / field
    "header_has_field": chk_header_has_field,
    "description_field_line": chk_description_field_line,
    # R-facet-spec
    "facet_dispatch_top": chk_facet_dispatch_top,
    # R-fct-system-design (Q004 re-derivation, 2026-08-05)
    "doc_in_design_folder": chk_doc_in_design_folder,
    "no_decisions_section": chk_no_decisions_section,
    "triggers_section_iff_declared": chk_triggers_section_iff_declared,
    "no_retired_location": chk_no_retired_location,
    # R-ruleset
    "all_rules_have_id": chk_all_rules_have_id,
    "rule_numbers_unique": chk_rule_numbers_unique,
    "all_rules_have_tier": chk_all_rules_have_tier,
    "checked_rules_have_pattern": chk_checked_rules_have_pattern,
    "ruleset_no_frontmatter": chk_ruleset_no_frontmatter,
    # R-status
    "status_filename_valid": chk_status_filename_valid,
    "status_in_track_folder": chk_status_in_track_folder,
    "status_facets_ordered": chk_status_facets_ordered,
    "status_cell_values_valid": chk_status_cell_values_valid,
    "status_nonone_cells_dated": chk_status_nonone_cells_dated,
    "status_user_cells_noted": chk_status_user_cells_noted,
    "status_track_dispatch_linked": chk_status_track_dispatch_linked,
    # R-architecture (T015, 2026-07-13; overview shared with R-testing-11)
    "architecture_filename_correct": chk_architecture_filename_correct,
    "architecture_h1_present": chk_architecture_h1_present,
    "overview_section_present": chk_overview_section_present,
    "architecture_diagram_section_with_embed": chk_architecture_diagram_section_with_embed,
    "no_ascii_diagram": chk_no_ascii_diagram,
    "subsystems_section_present": chk_subsystems_section_present,
    "spine_order_correct": chk_spine_order_correct,
    "subsystem_kebab_naming": chk_subsystem_kebab_naming,
    "subsystem_link_convention": chk_subsystem_link_convention,
    # R-testing
    "testing_filename_correct": chk_testing_filename_correct,
    "tests_table_present": chk_tests_table_present,
    "strategy_subsections_present_ordered": chk_strategy_subsections_present_ordered,
    "proposed_tests_structure": chk_proposed_tests_structure,
    "proposed_tests_subset_of_strategy": chk_proposed_tests_subset_of_strategy,
    "all_test_kinds_have_targets": chk_all_test_kinds_have_targets,
    "proposed_tests_rows_have_spec": chk_proposed_tests_rows_have_spec,
    "spec_cells_format_valid": chk_spec_cells_format_valid,
    "status_field_valid": chk_status_field_valid,
    # R-anchor-page (extras)
    "no_track_row_if_ecosystem_traits": chk_no_track_row_if_ecosystem_traits,
    # R-prd
    "file_path_matches_prd_locations": chk_file_path_matches_prd_locations,
    "h1_no_frontmatter": chk_h1_no_frontmatter,
    "required_sections_in_order": chk_required_sections_in_order,
    "queries_sections_subsequence": chk_queries_sections_subsequence,
    # R-query-01/-09 (T005, 2026-07-06)
    "queries_location": chk_queries_location,
    "queries_catchall_links": chk_queries_catchall_links,
    # R-query-16 (T017, 2026-07-13)
    "queries_banner_form": chk_queries_banner_form,
    "user_stories_use_rid_numbering": chk_user_stories_use_rid_numbering,
    "no_legacy_open_questions_file": chk_no_legacy_open_questions_file,
    "design_workflow_modern_names": chk_design_workflow_modern_names,
    "dispatch_table_stories_row": chk_dispatch_table_stories_row,
    # R-doc-structure / R-stories
    "no_dispatch_table": chk_no_dispatch_table,
    # R-progressive (conditional + multi-check layout)
    "dispatch_table_by_context": chk_dispatch_table_by_context,
    "progressive_disclosure_layout": chk_progressive_disclosure_layout,
    "doc_head_orientation_line": chk_doc_head_orientation_line,
    # R-spine (F319 M2) — advisory until the corpus is clean
    "spine_above_h1": chk_spine_above_h1,
    # Defined 2026-08-09 and left OUT of this dict until 2026-08-10 — so four
    # of the five spine rules resolved to no checker at all and reported
    # `error`, which `execute_on_write` deliberately never surfaces. Silent in
    # both directions: the rules looked shipped and the writes looked clean.
    "valid_spine": chk_valid_spine,
    "mirrored_doc_has_no_spine": chk_mirrored_doc_has_no_spine,
    "spine_h1_present": chk_spine_h1_present,
    # H02 (T623). Registered 2026-08-29 — it had been written and left out of this
    # dict for a day, reporting `error` on every page, which the write hook never
    # shows. The exact failure R-spine's own history paragraph describes.
    "spine_heart_required": chk_spine_heart_required,
    "identity_cell_description_first": chk_identity_cell_description_first,
    "orientation_line_adjoins_h1": chk_orientation_line_adjoins_h1,
    "masthead_over_folder_has_marker": chk_masthead_over_folder_has_marker,
    "marker_has_rows_below": chk_marker_has_rows_below,
    "identity_cell_description_first": chk_identity_cell_description_first,
    "orientation_line_adjoins_h1": chk_orientation_line_adjoins_h1,
    "masthead_over_folder_has_marker": chk_masthead_over_folder_has_marker,
    "marker_has_rows_below": chk_marker_has_rows_below,
    # R-roadmap
    "file_exists": chk_file_exists,
    "milestone_checkbox": chk_milestone_checkbox,
    "milestone_status_line": chk_milestone_status_line,
    "milestone_named_form": chk_milestone_named_form,
    "milestone_section_separator": chk_milestone_section_separator,
    # R-log
    "log_path_exists": chk_log_path_exists,
    "log_dispatch_file_present": chk_log_dispatch_file_present,
    "log_entry_filenames": chk_log_entry_filenames,
    "log_anchor_page_link": chk_log_anchor_page_link,
    # R-brief
    "brief_is_last_h1": chk_brief_is_last_h1,
    "brief_h1_matches_name": chk_brief_h1_matches_name,
    "brief_not_nested": chk_brief_not_nested,
    # R-design
    "design_folder_children": chk_design_folder_children,
    "status_facets_initialized": chk_status_facets_initialized,
    # R-file-association
    "file_association_folder_structure": chk_file_association_folder_structure,
    # R-dated-entry-stream
    "dated_entries_reverse_chronological": chk_dated_entries_reverse_chronological,
    "dated_entry_file_naming": chk_dated_entry_file_naming,
    # R-messages
    "h1_is_anchor_messages": chk_h1_is_anchor_messages,
    # R-naming (extra)
    "folder_marker_exists": chk_folder_marker_exists,
    # R-facet-spec (extra)
    "facet_has_ruleset": chk_facet_has_ruleset,
    "facet_h1_form": chk_facet_h1_form,
    "facet_registered": chk_facet_registered,
    "facet_tldr_if_substantial": chk_facet_tldr_if_substantial,
    "facet_cardinality_declared": chk_facet_cardinality_declared,
    "facet_examples_row": chk_facet_examples_row,
    # R-md
    "md_table_blank_lines": chk_md_table_blank_lines,
    "md_fence_no_markdown": chk_md_fence_no_markdown,
    "md_table_pipe_escape": chk_md_table_pipe_escape,
    "md_em_dash": chk_md_em_dash,
    "md_trailing_ws": chk_md_trailing_ws,
    "md_terminal_link_pad": chk_md_terminal_link_pad,
    "md_svg_embed_width": chk_md_svg_embed_width,
    # R-markdown re-wiring (T007, 2026-07-06)
    "md_inline_field_value": chk_md_inline_field_value,
    "md_stray_angle_tag": chk_md_stray_angle_tag,
    # R-backlog (F228 frontier invariants + per-state body contracts)
    "backlog_frontier_planned": chk_backlog_frontier_planned,
    "backlog_frontier_bracketed": chk_backlog_frontier_bracketed,
    "backlog_verify_concrete": chk_backlog_verify_concrete,
    "backlog_questions_have_numbered_q": chk_backlog_questions_have_numbered_q,
    "backlog_blocker_named": chk_backlog_blocker_named,
    "backlog_timed_has_expiry_date": chk_backlog_timed_has_expiry_date,
    "template_anchor_declared": chk_template_anchor_declared,
    "template_stencil_declared": chk_template_stencil_declared,
    "template_path_declared": chk_template_path_declared,
    "backlog_user_action_named": chk_backlog_user_action_named,
    "backlog_verify_is_user_grade": chk_backlog_verify_is_user_grade,
    # R-fct-features (T035 — F257 gate, file-scoped)
    "features_question_why_ask": chk_features_question_why_ask,
    # R-diagram-geometry / R-svg-hygiene / R-c4
    "svg_geometry_overlap": chk_svg_geometry_overlap,
    "svg_label_collision": chk_svg_label_collision,
    "svg_no_orphan_defs": chk_svg_no_orphan_defs,
    "svg_validates_xml": chk_svg_validates_xml,
    "svg_title_or_legend": chk_svg_title_or_legend,
}


def run_checker(check: str, target: Path, anchor_root: Path) -> tuple[str, str]:
    parts = check.split()
    name, args = parts[0], parts[1:]
    fn = registry().get(name)
    if fn is None:
        return "error", f"unknown checker {name!r}"
    try:
        return fn(target, anchor_root, args)
    except Exception as e:  # a checker bug must not abort the whole run
        return "error", f"{type(e).__name__}: {e}"


# How far into an anchor-dir target the verdict cache looks. Two levels: the
# root's children AND the members of its facet folders (`{slug} Design/`,
# `{slug} Track/`). T625 (2026-08-29): depth one hashed only the root's child
# NAMES, so `R-design-02` — which inspects `{slug} Design/` — kept serving a
# cached `fail` after `Sparks PRD.md` was written inside it. Touching files,
# waiting out the watcher and `ha --rescan` all changed nothing, because
# nothing at the root had a new name. Every `anchor`-scope checker that reads
# into a facet folder shares the key, so the key is what is fixed.
_ANCHOR_HASH_DEPTH = 2


def _content_hash(tp: Path) -> str:
    """Content hash of a target — file bytes, or (for an anchor-dir target) the
    (name, size, mtime) of every entry to `_ANCHOR_HASH_DEPTH`, so an edit or
    an arrival inside a facet folder invalidates the anchor's cached verdicts.
    Hidden entries are skipped except `.anchor`, whose `slug:` the checkers
    read. Cheap: an anchor root plus its facet folders is tens of entries."""
    try:
        if tp.is_file():
            return hashlib.sha256(tp.read_bytes()).hexdigest()[:12]
        sig: list[str] = []

        def walk(d: Path, depth: int) -> None:
            for p in sorted(d.iterdir(), key=lambda x: x.name):
                if p.name.startswith(".") and p.name != ".anchor":
                    continue
                try:
                    s = p.stat()
                except OSError:
                    continue
                rel = str(p.relative_to(tp))
                if p.is_dir():
                    sig.append(f"{rel}/")
                    if depth > 1:
                        walk(p, depth - 1)
                else:
                    sig.append(f"{rel}|{s.st_size}|{s.st_mtime_ns}")

        walk(tp, _ANCHOR_HASH_DEPTH)
        return hashlib.sha256("\n".join(sig).encode()).hexdigest()[:12]
    except OSError:
        return "0"


def _verdict_cache_get(cdir: Path, key: str):
    fp = cdir / "verdicts" / f"{key}.json"
    if fp.is_file():
        try:
            return json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
    return None


def _verdict_cache_put(cdir: Path, key: str, value: dict):
    d = cdir / "verdicts"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{key}.json").write_text(json.dumps(value), encoding="utf-8")


# ── Exceptions (F314): a graded, target-scoped escape from any checked rule ──
#
# `R-exception-discipline` has stated this shape since 2026-07-06 and
# `Warden Exceptions.md` has recorded three real deviations against it — and
# nothing read either file. The discipline was correct and inert, which is the
# same failure mode the spine discipline hit the day it was written: a rule with
# no enforcement surface changes nothing. This is that surface.
#
# The point of having one at all is that a rule admitting NO exception is a rule
# that gets weakened the first time it is genuinely wrong — and a weakened rule
# stops catching the cases it was right about. An escape that is numbered,
# graded, scoped to a named target and counted on every run is how a rule stays
# strict where it should be.

_EXC_GRADES = frozenset("ABCDEF")
# Only A-C suppress. `D` or lower is a grade the user CAN give and means "I read
# this deviation and it is not good enough" — so the row stays as a durable
# record of the judgment while the finding goes on failing. Without the split,
# grading was a binary dressed as a scale: every letter A-F did the same thing,
# which made the column decorative and left the user no way to say "recorded,
# and no" short of deleting the row and losing why it was ever proposed.
_EXC_PASSING = frozenset("ABC")
# The verdicts an A-C row may rewrite to `except`. `warn` joined `fail` on
# 2026-08-11 (T201 Q1 (A)); `error` never will — a crashed checker is a bug, and
# a table that could hide one would be a way to make bugs invisible by hand.
_EXC_SUPPRESSIBLE = frozenset({"fail", "warn"})
_EXC_HANDLE_RX = re.compile(r"^EX\d{3,}$")
# F601 (D): the names the Grader cell may carry to mean "the user graded this".
# Case-insensitive. Only these may award A–C on a `confirm:: user` rule.
_EXC_USER_NAMES = frozenset({"user", "dan"})
_EXC_RULE_RX = re.compile(r"^R-[a-z0-9-]+-\d{2}$")
_RULESET_OF_RULE_RX = re.compile(r"^(R-[a-z0-9-]+)-\d{2}$")
_CONFIRM_MEM: dict[str, bool] = {}


def rule_requires_user_confirmation(rule_id: str) -> bool:
    """True when this rule's ruleset declares `confirm:: user` (F314).

    Read from the rule catalog rather than from a list kept here, so the rules
    that need a conversation before they can be excepted are declared in the one
    place a reader of the rule would look — next to the rule itself.

    Resolution is by name: `R-spine-02` lives in `R-spine`. That is the same
    identity the exception table's Rule column already asserts, so a rule id that
    resolves to nothing is a malformed row, caught separately by the `^R-…-\\d\\d$`
    shape check rather than silently read as unconfirmed."""
    if rule_id in _CONFIRM_MEM:
        return _CONFIRM_MEM[rule_id]
    verdict = False
    m = _RULESET_OF_RULE_RX.match(rule_id)
    if m:
        fp = resolve_file(m.group(1))
        if fp is not None:
            try:
                blk = extract_ruleset_block(_read(fp), m.group(1))
            except OSError:
                blk = None
            if blk:
                rs = parse_ruleset_block(blk[0], fp)
                found = False
                for r in rs["rules"]:
                    if r["id"] == rule_id:
                        verdict = effective_confirm(r, rs) == "user"
                        found = True
                        break
                if not found:
                    # F601 — a `when::` moment rule (a deny) is not a doc-rule,
                    # and this planner's rule index does not carry it. Read
                    # its `confirm::` straight off the block: the rule's own
                    # field line under its `### RULE` header wins, else the
                    # ruleset's. Without this every deny read as unconfirmed —
                    # which is precisely the row (D) must never admit.
                    text = "\n".join(blk[0])
                    m2 = re.search(r"^### RULE " + re.escape(rule_id) + r"\b[^\n]*\n((?:(?!^### )[^\n]*\n?)*)",
                                   text, re.M)
                    own = None
                    if m2:
                        m3 = re.search(r"^confirm::\s*`?([^`\n]*)`?\s*$", m2.group(1), re.M)
                        if m3:
                            own = m3.group(1).strip() or None
                    verdict = (own or rs.get("confirm") or None) == "user"
    _CONFIRM_MEM[rule_id] = verdict
    return verdict


def _exceptions_file(anchor_root: Path) -> Path:
    """`{slug} Track/{slug} Exceptions.md` on the anchor that OWNS the tracking.

    One path per owning anchor, derived from where its tracking already lives —
    the location `Warden Exceptions.md` occupies and the one `HA Rules.md` and
    `MUX Rules/` independently converged on. `cab-audit.py`'s
    `.skl/lint/exceptions.md` and the audit docs' `.anchor.d/lint/exceptions.md`
    are retired rather than kept as alternatives: neither directory appears
    anywhere in the vault, so preserving them would be ambiguity over paths that
    have never held a file.

    The ancestor walk is resolution, not fallback. A folder facet carries its own
    `.anchor` — `{slug} Track/`, `{slug} Design/`, `{slug} Rocks/` — so auditing
    one makes IT the anchor root, and it owns no tracking of its own. Its
    exceptions are its owner's, and the walk finds the one anchor that has them.
    Without it, every rule firing inside a Track or Design folder would be
    unexceptable, which is most of the corpus."""
    return _exceptions_owner(anchor_root)[1]


def _exceptions_owner(anchor_root: Path) -> tuple[Path, Path]:
    """(owning anchor root, its exceptions file). Target globs in the table are
    relative to the OWNING root — the only stable frame, since auditing a Design
    or Track sub-anchor would otherwise change what every row in the same table
    means."""
    for root in _ancestor_anchor_roots(anchor_root):
        slug = _anchor_slug(root)
        trk = root / f"{slug} Track"
        if trk.is_dir():
            return root, trk / f"{slug} Exceptions.md"
    slug = _anchor_slug(anchor_root)
    return anchor_root, anchor_root / f"{slug} Track" / f"{slug} Exceptions.md"


def load_exceptions(anchor_root: Path) -> tuple[list[dict], list[dict], list[str]]:
    """Parse the anchor's exception table. Returns (admitted, declined, problems).

    `admitted` holds only rows graded A–C. Two other outcomes are well-formed and
    deliberately kept as rows rather than dropped:

    - **`?` — proposed.** The agent's own record of a deviation it accepted. It
      is durable and reviewable in the anchor's own tree, and it suppresses
      nothing. That column IS the approval gate, so a leak here would hand the
      agent every exception it ever wants.
    - **`D`–`F` — refused.** The user read the proposal and judged it poor. The
      finding keeps failing, and the row survives so the next agent to meet the
      same violation finds the answer already given instead of re-proposing it.

    `problems` is never empty-on-malformed: a row with a typo'd rule id would
    otherwise stop applying with no signal at all, which is exactly how an
    exception table decays into a pile nobody trusts."""
    fp = _exceptions_file(anchor_root)
    if not fp.is_file():
        return [], [], []
    admitted: list[dict] = []
    declined: list[dict] = []
    problems: list[str] = []
    header_n = 0
    for ln in _read(fp).splitlines():
        if not _is_table_row(ln):
            continue
        cells = _row_cells(ln)
        if len(cells) < 5:
            continue
        handle, rule, target, grade, why = (c.strip() for c in cells[:5])
        if handle.upper() == "EX" and rule.strip().lower() == "rule":
            header_n = len(cells)         # the header row fixes the column count
            continue
        if not _EXC_HANDLE_RX.match(handle):
            continue                      # separator or prose row
        # T620 (Presti, 2026-08-28) — a row one cell SHORT of the header still
        # renders, and the eye cannot see it: the F601 migration wrote
        # `{justification}  {requester} | {grader} |` (two spaces where a pipe
        # belongs) on ten rows across Warden and ATT, so Requester read empty,
        # Grader held the requester, and the grader ≠ requester check below
        # passed vacuously on eight live A/B exceptions. Counted on UNESCAPED
        # cells — `_row_cells` already discounts `\|` and `[[a\|b]]`, which is
        # what makes this a finding rather than a false alarm on every aliased
        # link. A problem, not a silent shift: a row whose columns are not
        # where the header says they are cannot be trusted to mean anything.
        # A five-cell row predates F601 and is admitted above with both
        # identities blank — that width is legal, not short.
        if header_n and len(cells) != header_n and len(cells) != 5:
            problems.append(f"{handle}: {len(cells)} cells against the header's "
                            f"{header_n} — a missing or extra pipe shifts "
                            f"Requester/Grader out of their columns; restore it")
            continue
        # F601 — Requester and Grader are the sixth and seventh cells. A row
        # that predates them (five cells) parses with both blank: the grade
        # stands on its own for an ordinary rule, exactly as before, but a
        # blank grader can never carry A–C on a `confirm:: user` rule (below).
        requester = cells[5].strip() if len(cells) > 5 else ""
        grader = cells[6].strip() if len(cells) > 6 else ""
        # A path in a markdown table is written in backticks by every other
        # convention in this vault, so authors write them here too — and the
        # glob matcher took them literally, so the row matched nothing and
        # `problems` stayed empty, which is the worst of the three possible
        # outcomes: an exception that reads as granted and suppresses nothing.
        # Measured 2026-08-27 on the vault's only file-scoped row (SV EX001,
        # graded A, target `SV Patents/SV Patents.md`, suppressing nothing
        # since the day it was written). Stripped rather than rejected: the
        # backticked form is the one a careful author writes.
        target = target.strip("`").strip()
        bad = []
        if not _EXC_RULE_RX.match(rule):
            bad.append(f"rule {rule!r} is not a rule id")
        if not target:
            bad.append("target is empty — write `**` for anchor-wide, deliberately")
        if grade not in _EXC_GRADES and grade != "?":
            bad.append(f"grade {grade!r} is not A-F (or `?` for proposed)")
        if not why:
            bad.append("no justification")
        row = {"handle": handle, "rule": rule, "target": target,
               "grade": grade, "why": why, "requester": requester,
               "grader": grader}
        # F601 — grader ≠ requester. Whoever benefits from an exception may
        # not be the one who decides it (Dan, 2026-08-28). The user is exempt:
        # he may write and grade his own row.
        if (grade in _EXC_PASSING and requester and grader
                and requester.lower() == grader.lower()
                and grader.lower() not in _EXC_USER_NAMES):
            bad.append(f"requester and grader are both {grader!r} — "
                       "grader ≠ requester (R-exception-discipline-14)")
        if bad:
            problems.append(f"{handle}: " + "; ".join(bad))
        elif (grade in _EXC_PASSING and _EXC_RULE_RX.match(rule)
                and rule_requires_user_confirmation(rule)
                and grader.lower() not in _EXC_USER_NAMES):
            # F601 (D) — grading authority is a property of the RULE. On a
            # `confirm:: user` rule only the user may award the letter; an
            # agent-graded row is recorded and INERT, never silently honoured.
            row["declined"] = (f"graded {grade} by "
                               f"{grader or 'no named grader'} on a "
                               f"`confirm:: user` rule — only the user may "
                               f"grade it; inert until the Grader cell says "
                               f"`user`")
            row["inert"] = "authority"
            declined.append(row)
        elif grade in _EXC_PASSING:
            admitted.append(row)
        else:
            row["declined"] = ("ungraded — suppresses nothing until you grade it"
                               if grade == "?" else
                               f"graded {grade} — below the C floor, so it records "
                               f"the judgment without suppressing")
            declined.append(row)
    return admitted, declined, problems


def _exception_for(excs: list[dict], rule_id: str, target: Path,
                   anchor_root: Path) -> dict | None:
    """The first admitted row covering this (rule, target), else None.

    Target is a glob over the path relative to the OWNING anchor — not to
    whatever root this run happens to be scoped on, or the same row would mean
    different files depending on where the audit was launched. Anchor-wide is
    written `**` and never a blank cell: `cab-audit.py` made blank mean
    everything, then needed a hardcoded list of rules for which blanket
    suppression is refused, a special case that existed only because the default
    was dangerous."""
    owner, _ = _exceptions_owner(anchor_root)
    try:
        rel = target.resolve().relative_to(owner.resolve()).as_posix()
    except (OSError, ValueError):
        rel = target.name
    for e in excs:
        if e["rule"] != rule_id:
            continue
        if any(_glob_rx(pat).match(c)
               for pat in _expand_braces(e["target"])
               for c in (rel, target.name)):
            return e
    return None


def execute_plan(plan: dict, cdir: Path | None) -> dict:
    """Run every matched rule that carries a `check::` ref; cache verdicts by
    (rule-id, rule-body-hash, target-content-hash). Returns a verdicts report."""
    anchor_root = Path(plan["anchor_root"])
    results = []
    # `warn` (T138) is a fourth verdict, not a soft fail: a rule that reports a
    # cosmetic condition must not land in the failure list, or the report treats
    # 98 links that route readers correctly as 98 things to repair.
    # `except` (F314) is a fifth, and it is deliberately NOT folded into `pass`:
    # a corpus with forty accepted deviations must never read like one with none.
    counts = {"pass": 0, "fail": 0, "warn": 0, "except": 0, "error": 0, "cached": 0}
    excs, exc_declined, exc_problems = load_exceptions(anchor_root)
    used: set[str] = set()
    # Rows whose rule DID fire on their target, at a severity `execute_plan`
    # cannot rewrite. Tracked separately so they never masquerade as stale.
    unsuppressable: set[str] = set()
    # Proposed rows whose rule now passes on their target — see the note at the
    # assignment below. Kept apart from `stale`, which is about GRADED rows.
    moot: set[str] = set()
    for g in plan["groupings"]:
        for r in g["rules"]:
            if not r.get("check"):
                continue
            body_hash = hashlib.sha256(f"{r['id']}|{r['check']}".encode()).hexdigest()[:12]
            for disp, tgt in zip(r["targets"], r["_target_paths"]):
                tp = Path(tgt)
                chash = _content_hash(tp)
                key = f"{r['id']}-{body_hash}-{chash}"
                cached = _verdict_cache_get(cdir, key) if cdir else None
                # A cached `error` is never trusted — see the put-side note
                # below; entries written before that rule need ignoring too.
                if cached and cached.get("status") == "error":
                    cached = None
                if cached:
                    status, detail = cached["status"], cached["detail"]
                    counts["cached"] += 1
                else:
                    status, detail = run_checker(r["check"], tp, anchor_root)
                    # An `error` is a verdict about the PLUMBING (an unregistered
                    # checker, a crash), not about the target, so it must not be
                    # keyed on the target's content: registering the checker
                    # changes nothing in the key, and the stale error was served
                    # back after the fix (T623/H02, 2026-08-29).
                    if cdir and status != "error":
                        _verdict_cache_put(cdir, key, {"status": status, "detail": detail})
                # A `fail` and a `warn` are both excepted (T201 Q1 (A), Dan
                # 2026-08-11: "audit grades A through C should suppress
                # warnings, because we've already decided that that exception
                # is okay"). The warning tier is where judgment calls live, so
                # it is where accepted deviations cluster — restricting
                # suppression to `fail` meant the tier most likely to hold a
                # real acceptance was the one tier that could not record it.
                # ATT hit this on R-spine-07 / Atticus.md, a deviation Dan had
                # personally graded `A`, and WITHDREW the row rather than leave
                # it reporting stale forever.
                #
                # An `error` is still never excepted: it is a checker that
                # crashed — a bug, not a deviation — and no table entry may
                # bury one. A row aimed at one is reported as unsuppressable
                # rather than stale, because "your row did no work" sends the
                # reader to look for a defect in the row when the defect is in
                # the checker.
                if status in _EXC_SUPPRESSIBLE and excs:
                    e = _exception_for(excs, r["id"], tp, anchor_root)
                    if e:
                        used.add(e["handle"])
                        status = "except"
                        detail = f"{e['handle']} (grade {e['grade']}) — {e['why']}" + (
                            f"  [was: {detail}]" if detail else "")
                elif status == "error" and excs:
                    e = _exception_for(excs, r["id"], tp, anchor_root)
                    if e:
                        unsuppressable.add(e["handle"])
                # A PROPOSED row whose rule now PASSES on its own target is
                # moot: the deviation it describes no longer exists, usually
                # because the checker was fixed upstream rather than because the
                # page changed. Saying "grade it" there is actively harmful —
                # grading it `A` installs a permanent blindfold over a rule that
                # is working. Tracked here, where the verdict is in hand; the
                # renderers turn it into "retire the row" instead.
                if status == "pass":
                    for _lst in (excs, exc_declined):
                        e = _exception_for(_lst, r["id"], tp, anchor_root) if _lst else None
                        if e:
                            moot.add(e["handle"])
                counts[status] = counts.get(status, 0) + 1
                results.append({"rule": r["id"], "target": disp, "status": status, "detail": detail})
    # A row that suppressed nothing is either stale — the document was fixed or
    # deleted — or its rule simply did not run at THIS scope. The report must not
    # claim to know which, only that the row did no work, because an unused row
    # left silent is how the table stops being reviewable.
    # A GRADED row whose rule passed on its own target is not "stale or out of
    # scope" — it is answerable, and the answer is that the grade is covering
    # nothing. Splitting it out is what turns the honest-but-inert "the report
    # must not claim to know which" into a row someone can actually retire; what
    # is left in `stale` is the genuinely undecidable remainder, a row whose rule
    # never ran here at all.
    stale = [e["handle"] for e in excs
             if e["handle"] not in used and e["handle"] not in unsuppressable
             and e["handle"] not in moot]
    return {"counts": counts, "results": results, "stale_exceptions": stale,
            "unsuppressable_exceptions": sorted(unsuppressable),
            "moot_exceptions": sorted(moot),
            "declined_exceptions": exc_declined, "exception_problems": exc_problems}


def render_verdicts(report: dict) -> str:
    c = report["counts"]
    out = [f"# mechanical verdicts — pass {c['pass']}  fail {c['fail']}  "
           f"warn {c.get('warn', 0)}  except {c.get('except', 0)}  "
           f"error {c['error']}  (cache hits {c['cached']})", ""]
    for v in report["results"]:
        mark = {"pass": "✓", "fail": "✗", "warn": "~",
                "except": "⊘", "error": "!"}.get(v["status"], "?")
        line = f"{mark} {v['rule']} — {v['target']}"
        if v["detail"]:
            line += f"  ({v['detail']})"
        out.append(line)
    for p in report.get("exception_problems", []):
        out.append(f"! exception row malformed — {p}")
    moot = set(report.get("moot_exceptions", []))
    for d in report.get("declined_exceptions", []):
        if d["handle"] in moot:
            out.append(f"~ {d['handle']} ({d['rule']}) — MOOT: the rule now passes on "
                       f"`{d['target']}`, so there is nothing to except. Retire the row "
                       f"— grading it would suppress a rule that is working.")
        else:
            out.append(f"~ {d['handle']} ({d['rule']}) — {d['declined']}")
    unsup = report.get("unsuppressable_exceptions", [])
    if unsup:
        out.append("~ exception(s) whose rule ERRORED — the checker crashed, so "
                   "there is no verdict to suppress. Not stale, and not your "
                   f"row's fault; fix the checker: {', '.join(unsup)}")
    graded_moot = sorted(moot - {d["handle"] for d in report.get("declined_exceptions", [])})
    if graded_moot:
        out.append("~ graded exception(s) covering a rule that now PASSES on their "
                   "own target — the grade suppresses nothing and should be "
                   f"retired: {', '.join(graded_moot)}")
    stale = report.get("stale_exceptions", [])
    if stale:
        out.append("~ exception(s) that did no work this run (stale, or the rule "
                   f"was out of scope): {', '.join(stale)}")
    return "\n".join(out)


# ── Fix stage (F177): mechanical repairs + on-write hook driver ──────────
#
# A `checked` rule may carry a `fix::` naming a FIXER that REPAIRS the target in
# place. The on-write hook (F177, the first buildable slice of F166) runs the doc
# audit on each write and splits failures two ways: a fail WITH a `fix::` is
# repaired silently (auto-fix bucket); a fail WITHOUT one is surfaced to the agent
# (message bucket) — because its correct fix needs judgment we must not guess at.


def fix_table_blank_lines(target, anchor_root, args):
    """Insert a blank line before and after every markdown table block. Paired to
    the `md_table_blank_lines` check. Deterministic and safe — only adds blanks."""
    if not target.is_file():
        return False, "not a file"
    text = _read(target)
    lines = text.split("\n")
    is_tbl = lambda l: l.lstrip().startswith("|")
    out, i, changed = [], 0, False
    n = len(lines)
    # `split("\n")` rather than `splitlines()` so the join round-trips a trailing
    # newline; `_fenced_mask` counts `splitlines()`, so pad the tail. This fixer
    # WRITES the file, and it shares its fence judgement with the check it is
    # paired to (`chk_md_table_blank_lines`) — the two disagreeing is how a fixer
    # ends up re-inserting a blank the check will flag again next run (T099).
    fenced = _fenced_mask(text)
    fenced += [False] * (n - len(fenced))
    while i < n:
        if fenced[i]:
            out.append(lines[i]); i += 1
        elif is_tbl(lines[i]):
            if out and out[-1].strip() != "":
                out.append(""); changed = True
            while i < n and is_tbl(lines[i]):
                out.append(lines[i]); i += 1
            if i < n and lines[i].strip() != "":
                out.append(""); changed = True
        else:
            out.append(lines[i]); i += 1
    if changed:
        target.write_text("\n".join(out), encoding="utf-8")
    return changed, ("inserted blank line(s) around table" if changed else "")


def _alnum(s):
    return [c for c in s if c.isalnum()]


def _alnum_subseq(orig: str, new: str) -> bool:
    """True iff every alphanumeric char of `orig`, in order, still appears in `new`
    — i.e. the fix may insert / escape / normalize whitespace, but must NOT DELETE
    any letter or digit of content. The structural no-delete safety invariant (F179)."""
    it = iter(_alnum(new))
    return all(c in it for c in _alnum(orig))


# A fixer whose CONTRACT is to move a block cannot satisfy an ordered floor:
# reordering is precisely what it does, so `_alnum_subseq` rejects every correct
# run of it. That is not a reason to exempt it from a floor — it is a reason to
# use the order-insensitive one. `_alnum_multiset` still catches the failure the
# floor exists to catch (a letter or digit deleted, or invented), and stays blind
# only to position, which the fixer's own proof covers instead: `spine_fix`
# asserts the link multiset, the H1 text, the table-row multiset, the description
# text, no lost non-blank line, and the sibling `.anchor`, and REFUSES to write
# on any mismatch. Registering a fixer here without that kind of proof would be
# a real weakening; this list is not a convenience hatch.
_REARRANGING_FIXERS = {"spine_position"}


def _alnum_multiset(orig: str, new: str) -> bool:
    """True iff `new` holds exactly the same alphanumeric characters as `orig`,
    counted — order free. The no-delete floor for a fixer that relocates text."""
    from collections import Counter
    return Counter(_alnum(orig)) == Counter(_alnum(new))


def _content_floor_holds(fix: str, orig: str, new: str) -> bool:
    """The never-delete floor, chosen by what the fixer is allowed to do."""
    name = fix.split()[0] if fix else ""
    if name in _REARRANGING_FIXERS:
        return _alnum_multiset(orig, new)
    return _alnum_subseq(orig, new)


# T178: a frozen specimen region — `<!-- begin {body} --> ... <!-- end {body} -->`
# — is a document quoting bytes verbatim on purpose (a Stencil test corpus, a
# spec's worked example). No fixer may rewrite a byte inside one, no matter how
# well-intentioned the fix (T4.a's trailing double-space hard breaks are the
# exact bytes that specimen exists to demonstrate; `fix_md_trailing_ws` strips
# them like any other line). `{body}` is whatever text follows "begin " up to
# " -->", matched verbatim on the paired "end " line — general to any marker
# vocabulary, not special-cased to Stencil's `example`/`proposal` kinds.
_FROZEN_RE = re.compile(r"<!-- begin (.+?) -->\n.*?\n<!-- end \1 -->", re.S)


def _frozen_regions(text: str) -> list[str]:
    """Every frozen-specimen block in `text`, markers included, as exact
    substrings — the unit a fixer must reproduce byte-for-byte to touch this
    file at all."""
    return [m.group(0) for m in _FROZEN_RE.finditer(text)]


def _frozen_preserved(orig: str, new: str) -> bool:
    """True iff every frozen-specimen block in `orig` still appears in `new`
    as an exact substring — a fixer may rewrite anything OUTSIDE these
    regions, but nothing inside them, ever."""
    return all(region in new for region in _frozen_regions(orig))


def _repl_outside_code(text: str, repl):
    """Apply `repl` to the parts of `text` outside code \u2014 fenced blocks, indented
    blocks, and inline spans, as `_code_regions` defines them. Reading and writing
    are different operations over the SAME structure, and the structure is shared
    (T222 defect 2); this function no longer re-derives any part of it."""
    out, i = [], 0
    for a, b in _code_regions(text):
        out.append(repl(text[i:a]))
        out.append(text[a:b])
        i = b
    out.append(repl(text[i:]))
    return "".join(out)


def _repl_outside_inline(seg: str, repl):
    """Per-line sibling of `_repl_outside_code`, for callers that have already
    excluded fences themselves via `_code_masked_lines`. Spans come from
    `_SPAN_RE` \u2014 the same pattern the maskers use \u2014 never a local re-roll."""
    out, i = [], 0
    for m in _SPAN_RE.finditer(seg):
        out.append(repl(seg[i:m.start()])); out.append(m.group(0)); i = m.end()
    out.append(repl(seg[i:]))
    return "".join(out)


def fix_md_em_dash(target, anchor_root, args):
    """Convert a spaced ` -- ` to ` \u2014 ` outside code, and REFUSE any line whose
    masking cannot be trusted.

    T222 defect 3. A code span whose CONTENT contains a backtick \u2014 unavoidable
    when documenting regexes, markdown, or nested shell \u2014 breaks paired-delimiter
    matching, and everything after it on that line silently loses its masking. The
    proof is that the first draft of T222's own backlog row was corrupted by the
    rule it describes: a span reading backtick-space-double-hyphen-space-backtick
    became an em-dash *despite being inside backticks*, because the line carried
    19 backticks. So "put it in backticks" is a good convention but NOT a
    sufficient defence.

    Odd backtick parity in the masked line is the detectable form of that: it
    means the pairing did not consume every delimiter, so this function does not
    know where code sits on that line. It skips the line and reports it. A fixer
    that cannot determine masking with certainty must refuse and report rather
    than rewrite content it does not understand \u2014 silence beats corruption,
    especially on a fix that runs unattended on every write. The paired check
    still reads the line, so the finding reaches a human instead of being quietly
    "fixed".
    """
    text = _read(target)
    raw_lines = text.split("\n")
    code_masked = _mask_code(text)
    # Two masks, deliberately. Backtick PARITY is judged on the code-masked line
    # alone, because blanking a link target could itself change that parity and
    # turn the refusal below into noise. Where to SUBSTITUTE is judged on the
    # link-masked line, so a filename holding ` -- ` is left alone (T604).
    parity_lines = code_masked.split("\n")
    masked_lines = _blank_regions(
        code_masked, _link_target_regions(code_masked)).split("\n")
    out, skipped, changed = [], [], False
    for i, raw in enumerate(raw_lines):
        m = masked_lines[i] if i < len(masked_lines) else ""
        if (parity_lines[i] if i < len(parity_lines) else "").count("`") % 2:
            skipped.append(i + 1)
            out.append(raw)
            continue
        # Decide on the masked line, edit the real one. `_mask_code` is
        # length-preserving, so the indices carry over exactly.
        for p in reversed([h.start() for h in re.finditer(r" -- ", m)]):
            raw = raw[:p] + " \u2014 " + raw[p + 4:]
            changed = True
        out.append(raw)
    note = ""
    if skipped:
        note = ("declined %d line(s) with unpaired backticks (masking unreliable): %s"
                % (len(skipped), ", ".join(str(n) for n in skipped[:5])))
    if changed:
        target.write_text("\n".join(out), encoding="utf-8")
        return True, "converted spaced ` -- ` to ` \u2014 `" + (" \u2014 " + note if note else "")
    return False, note


def fix_md_trailing_ws(target, anchor_root, args):
    """Strip trailing whitespace, PRESERVING the single F278 pad space after a
    terminal link. `rstrip()` then re-pad is deliberate: it collapses two-or-more
    spaces after a link down to the canonical one (killing an accidental `<br>`
    hard break) rather than leaving them, and it is a normalization, so applying
    it twice is a no-op."""
    text = _read(target)
    lines = text.split("\n")
    # The re-pad reuses `_terminal_link_pad_lines` — the SAME eligibility its sibling
    # `fix_md_terminal_link_pad` and the paired check use — rather than re-deriving
    # it. The local spelling this replaced carried only the table exclusion, and
    # `_ends_with_terminal_link` fires on anything ending `]]` that contains `[[`.
    # So it appended a pad INSIDE fenced code (`sub = grid[[0, 1]]` → a trailing
    # space added to a Python line) and to frontmatter values (`up: [[Parent]]`),
    # on the on-write path. Both were invisible: `chk_md_trailing_ws` and
    # `chk_md_terminal_link_pad` exempt exactly those regions, so nothing reported
    # the bytes this fixer had just written. Three fixers now share one predicate.
    padable = {i for i, _ in _terminal_link_pad_lines(text)}
    new = []
    for i, l in enumerate(lines):
        s = l.rstrip()
        new.append(s + " " if i in padable and _ends_with_terminal_link(s) else s)
    if new != lines:
        target.write_text("\n".join(new), encoding="utf-8")
        return True, "stripped trailing whitespace"
    return False, ""


def fix_md_terminal_link_pad(target, anchor_root, args):
    """F278 — append the single canonical trailing space to prose lines whose last
    token is a link. Paired to `chk_md_terminal_link_pad`; shares its predicate
    and its table/code/frontmatter exclusions, so the two agree by construction."""
    if not target.is_file():
        return False, "not a file"
    text = _read(target)
    lines = text.split("\n")
    n = 0
    for i, raw in _terminal_link_pad_lines(text):
        if _ends_with_terminal_link(raw):
            lines[i] = raw + " "
            n += 1
    if n:
        target.write_text("\n".join(lines), encoding="utf-8")
        return True, f"padded {n} terminal link(s) with one trailing space"
    return False, ""


def fix_md_table_pipe_escape(target, anchor_root, args):
    text = _read(target)
    lines = text.split("\n")
    # Decide on the masked line, edit the real one — the same pairing the check
    # uses, so writer and reader cannot disagree about which lines are table rows.
    # Before F296 this fixer tested `raw` and so escaped the pipe inside fenced
    # EXAMPLES of the row form, on the on-write path, silently.
    #
    # F296 cured the FENCE half and left the INLINE-SPAN half, which is the same
    # bug one level in: the row-ness test moved to the masked line but the `re.sub`
    # still ran over the whole raw line, spans included. A doc documenting the
    # table form as `` | `[[A|B]]` | literal shown as code | `` had its own example
    # rewritten to `` `[[A\|B]]` ``, and the check passed both before and after —
    # so nothing ever pointed at the line the fixer had just corrupted. Backticking
    # is how markdown says "literal", and it has to be a defence here too, hence
    # `_repl_outside_inline`. (`_mask_code` cannot serve: it BLANKS spans, and this
    # caller must emit the original bytes, not a masked copy.)
    masked_lines = _code_masked_lines(text)
    changed = False
    for i, raw in enumerate(lines):
        if i >= len(masked_lines) or not masked_lines[i].lstrip().startswith("|"):
            continue
        newline = _repl_outside_inline(
            raw, lambda s: _WIKILINK_RE.sub(
                lambda m: _escape_unescaped_pipes(m.group(0)), s))
        if newline != raw:
            lines[i] = newline; changed = True
    if changed:
        target.write_text("\n".join(lines), encoding="utf-8")
        return True, "escaped pipe(s) in table wiki-link(s)"
    return False, ""


def fix_breadcrumb_position(target, anchor_root, args):
    """Reposition a misplaced `:>>` breadcrumb directly above the H1, zero blank
    lines between (paired to `doc_top_order`). Two shapes are repaired: the
    breadcrumb below the H1 (moved up), and blank lines between breadcrumb and
    H1 (removed). Non-blank content between them is NOT reordered — that needs
    a judgment call, so the finding falls through to a steer."""
    if not target.is_file():
        return False, "not a file"
    lines = _read(target).split("\n")
    bidx, hidx = _breadcrumb_h1_positions(lines)
    if bidx is None or hidx is None:
        return False, ""
    if bidx > hidx:
        crumb = lines.pop(bidx)
        # popping below the H1 may leave a doubled blank where the crumb sat
        if bidx < len(lines) and lines[bidx].strip() == "" and lines[bidx - 1].strip() == "":
            lines.pop(bidx)
        lines.insert(hidx, crumb)
        target.write_text("\n".join(lines), encoding="utf-8")
        return True, "moved `:>>` breadcrumb above the H1"
    between = lines[bidx + 1:hidx]
    if between and all(ln.strip() == "" for ln in between):
        del lines[bidx + 1:hidx]
        target.write_text("\n".join(lines), encoding="utf-8")
        return True, "removed blank line(s) between breadcrumb and H1"
    return False, ""


def fix_md_svg_embed_width(target, anchor_root, args):
    """Append the page-wide default `|3000` hint to bare `![[x.svg]]` embeds.
    Paired to the `md_svg_embed_width` check; skips code fences / inline code.

    Inside a table row the hint is written `\\|3000`, because a bare `|` there is a
    CELL DELIMITER. Writing it unescaped turned `| ![[diagram.svg]] | the arch |`
    into a three-cell row, and `chk_md_table_pipe_escape` then failed the file this
    fixer had just written — two fixers fighting, one manufacturing the defect the
    other exists to remove, with the user's table broken in between.
    """
    if not target.is_file():
        return False, "not a file"
    text = _read(target)
    # Line-by-line, because the replacement now depends on whether THIS line is a
    # table row. Fence exclusion therefore cannot come from `_repl_outside_code`
    # (it tracks fence state across the whole text and would see each line alone);
    # it comes from the masked copy, which blanks fenced lines length-preservingly.
    # Inline spans are still handled by `_repl_outside_inline` per line.
    masked = _code_masked_lines(text)
    out = []
    for i, raw in enumerate(text.split("\n")):
        m = masked[i] if i < len(masked) else ""
        if raw.strip() and not m.strip():
            out.append(raw)                       # inside a fence — leave it alone
            continue
        repl = r"![[\1\|3000]]" if m.lstrip().startswith("|") else r"![[\1|3000]]"
        out.append(_repl_outside_inline(
            raw, lambda s, r=repl: re.sub(r"!\[\[([^\]|]+?\.svg)\]\]", r, s)))
    new = "\n".join(out)
    if new != text:
        target.write_text(new, encoding="utf-8")
    return (new != text), ("added |3000 width hint to bare SVG embed(s)" if new != text else "")


def fix_spine_position(target, anchor_root, args):
    """Repair the three mechanical spine rearrangements in place, by delegating
    to `spine_fix` — the same self-verified mover `spine fix --vault` runs.

    S03 move the masthead above the H1 · S04 flip the identity cell to
    description-first · S05 close the blank between H1 and orientation line.

    **This fixer invents nothing and delegates everything.** Re-implementing
    the moves here would put a second, unproven copy of them on the write path,
    and the moves are exactly the class that fails silently: three separate
    measurements during F308 were wrong from regex-splitting table cells. So
    `spine_fix` keeps its own per-file proof — link multiset, H1 text, row
    multiset, description text, no lost line, and the sibling `.anchor` — and
    **refuses rather than writing** on any mismatch. A refusal here returns
    False, which lands the finding in the message bucket for a human, which is
    the correct outcome: the page needed a judgment the machine does not have.
    """
    if not target.is_file():
        return False, "not a file"
    try:
        sfx = _spine_sibling("spine_fix")
        action, note, new = sfx.plan_file(target)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    if action != "fixed" or new is None:
        # `refused` carries a real reason (a diverging `.anchor`, a proof that
        # did not hold); surface it rather than swallowing it as "no change".
        return False, note if action == "refused" else ""
    target.write_text(new, encoding="utf-8")
    return True, f"spine rearranged ({note})"


def fix_spine_h1(target, anchor_root, args):
    """Insert `# {stem}` directly beneath the spine. Paired to `spine_h1_present`.

    The title is the file's stem — not a guess, and not the `.anchor`'s
    `title:`: the stem is what every `[[wiki-link]]` to this page already
    displays, so the H1 and the links agree by construction.

    Placement follows the head's disclosure order. A masthead is a block, so
    the H1 goes after the table with a blank line between; a `:>>` breadcrumb
    sits **directly** above its H1 with no blank (`R-doc` / `breadcrumb_position`).
    Only ever an insertion — the assertion below is that the original text
    survives verbatim, so this can add a title but never edit a page.
    """
    if not target.is_file():
        return False, "not a file"
    try:
        p = _spine_module().Spine(target)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    if not p.has_spine or p.h1 is not None:
        return False, ""
    lines = list(p.lines)
    h1 = f"# {target.stem}"
    if p.table_end is not None:
        at, block = p.table_end, [""] + [h1]
    elif p.breadcrumb is not None:
        at, block = p.breadcrumb + 1, [h1]
    else:
        return False, ""
    out = lines[:at] + block + lines[at:]
    # An insertion and nothing else: drop the lines we added and the file must
    # be byte-identical. That is stronger than the shared alnum floor, and it is
    # what makes "add a title" unable to become "rewrite a page".
    if [l for i, l in enumerate(out) if i not in range(at, at + len(block))] != lines:
        return False, "would have changed more than the inserted title"
    target.write_text("\n".join(out), encoding="utf-8")
    return True, f"inserted `{h1}` beneath the spine"


FIXERS = {
    "spine_position": fix_spine_position,
    "spine_h1": fix_spine_h1,
    "md_table_blank_lines": fix_table_blank_lines,
    "md_table_pipe_escape": fix_md_table_pipe_escape,
    "md_em_dash": fix_md_em_dash,
    "md_trailing_ws": fix_md_trailing_ws,
    "md_terminal_link_pad": fix_md_terminal_link_pad,
    "breadcrumb_position": fix_breadcrumb_position,
    "md_svg_embed_width": fix_md_svg_embed_width,
}


def run_fixer(fix: str, target: Path, anchor_root: Path) -> tuple[bool, str]:
    parts = fix.split()
    name, args = parts[0], parts[1:]
    fn = fixer_registry().get(name)
    if fn is None:
        return False, f"unknown fixer {name!r}"
    try:
        return fn(target, anchor_root, args)
    except Exception as e:  # a fixer bug must not corrupt the file silently
        return False, f"{type(e).__name__}: {e}"


def execute_on_write(plan: dict, cdir: Path | None) -> dict:
    """The on-write driver. For each matched mechanical rule that FAILS on its
    target: apply its `fix::` (and re-check) when it has one — else collect a
    message. Returns {fixed:[...], messages:[...]} (no cache: the file just changed)."""
    anchor_root = Path(plan["anchor_root"])
    fixed, messages, excepted = [], [], []
    # The on-write path must honor exceptions BEFORE the fixer runs (F314). A
    # `fix::` that repaired a document carrying an approved deviation would undo
    # the exception silently on the next save — the auto-fixer being the thing
    # that erases the record of why the file is the way it is.
    excs, exc_declined, exc_problems = load_exceptions(anchor_root)
    for g in plan["groupings"]:
        for r in g["rules"]:
            chk = r.get("check")
            if not chk:
                continue
            for disp, tgt in zip(r["targets"], r["_target_paths"]):
                tp = Path(tgt)
                status, detail = run_checker(chk, tp, anchor_root)
                if status != "fail":
                    continue
                if excs:
                    e = _exception_for(excs, r["id"], tp, anchor_root)
                    if e:
                        excepted.append({"rule": r["id"], "target": disp,
                                         "handle": e["handle"], "grade": e["grade"]})
                        continue
                fx = r.get("fix")
                if fx:
                    orig = tp.read_text(encoding="utf-8")
                    changed, fdetail = run_fixer(fx, tp, anchor_root)
                    if changed:
                        new = tp.read_text(encoding="utf-8")
                        if not _content_floor_holds(fx, orig, new):
                            tp.write_text(orig, encoding="utf-8")  # never delete content
                            messages.append({"rule": r["id"], "target": disp,
                                             "detail": (detail or "") + " — auto-fix SUPPRESSED (would alter content); fix by hand",
                                             "why": r.get("why"), "check_pattern": r.get("check_pattern")})
                            continue
                        if not _frozen_preserved(orig, new):
                            tp.write_text(orig, encoding="utf-8")  # never touch a frozen specimen region
                            messages.append({"rule": r["id"], "target": disp,
                                             "detail": (detail or "") + " — auto-fix SUPPRESSED (would rewrite a frozen "
                                             "`<!-- begin/end -->` specimen region); fix by hand",
                                             "why": r.get("why"), "check_pattern": r.get("check_pattern")})
                            continue
                        status2, _ = run_checker(chk, tp, anchor_root)
                        if status2 == "pass":
                            fixed.append({"rule": r["id"], "target": disp,
                                          "detail": fdetail or detail})
                            continue
                    # no change, or change didn't resolve it — fall through to a message
                messages.append({"rule": r["id"], "target": disp, "detail": detail,
                                 "why": r.get("why"), "check_pattern": r.get("check_pattern")})
    return {"fixed": fixed, "messages": messages, "excepted": excepted,
            "declined_exceptions": exc_declined,
            "exception_problems": exc_problems}


def render_on_write(report: dict) -> str:
    out = []
    for f in report["fixed"]:
        out.append(f"✓ fixed {f['rule']} — {f['target']}  ({f['detail']})")
    for m in report["messages"]:
        line = f"⚑ {m['rule']} — {m['target']}: {m['detail']}"
        if m.get("why"):
            line += f"  [why: {m['why']}]"
        out.append(line)
    for e in report.get("excepted", []):
        out.append(f"⊘ {e['rule']} — {e['target']}: accepted deviation "
                   f"{e['handle']} (grade {e['grade']})")
    for p in report.get("exception_problems", []):
        out.append(f"! exception row malformed, suppressing nothing — {p}")
    for d in report.get("declined_exceptions", []):
        out.append(f"~ {d['handle']} ({d['rule']}) — {d['declined']}")
    return "\n".join(out) if out else "(clean — nothing to fix or flag)"


# ── Stage 3: agent-judge scaffolding (manifest + verdict record) ─────────────
#
# The mechanical executor (--run) handles every rule with a known `check::`.
# The residue — `stated` rules, `sampled`/`checked` rules with no usable checker —
# needs agent judgment. `audit-plan <target> --judge` emits a JSON manifest of
# exactly those (rule × target) tasks, pre-filtered by the verdict cache, each with
# the full Q3 cache key `(rule-id, rule-body-hash, target-content-hash, model-id)`.
# The driving agent reads each task's rule body, judges its target, then persists
# the verdict via `audit-plan --record-verdict --key <key> --status <s>`. A re-run
# with unchanged rule + target + model serves the verdict from cache (zero agent
# work) — the same key the agent wrote under.

def _judge_body_hash(rule: dict) -> str:
    """Per-rule body hash over what the agent judges against (the flat-rule view)."""
    h = hashlib.sha256()
    h.update(f"{rule['id']}|{rule.get('tier')}|{rule.get('title')}|"
             f"{rule.get('check_pattern')}|{rule.get('why')}".encode())
    return h.hexdigest()[:12]


def _needs_judgment(rule: dict) -> bool:
    """A rule needs the agent iff it isn't mechanically executable and isn't
    awareness-only (`tracked`). Mechanical = a `check::` naming a known checker.

    `retired` and `governing` join `tracked` here, and the exclusion is the
    load-bearing half of admitting them to `_RULE_RE` (2026-08-11). This is a
    MEMBERSHIP test, not a lookup: any rule that parses without a runnable
    `check::` is promoted to billed agent judgment. So admitting the two tiers
    alone would have started charging an LLM call for every retired rule on
    every audit, forever — a fix whose cost shows up only on the invoice.
    Neither tier wants judging: a retired rule is one deliberately no longer
    enforced, and a governing rule states how its siblings resolve rather than
    making a claim about any target.
    """
    if rule["tier"] in {"tracked", "retired", "governing"}:
        return False
    chk = rule.get("check")
    if chk and chk.split()[0] in registry():
        return False
    return True


def judge_manifest(plan: dict, cdir: Path | None, model: str) -> dict:
    """Emit the agent-judgment task list, pre-filtered by the verdict cache."""
    tasks, cached = [], []
    for g in plan["groupings"]:
        for r in g["rules"]:
            if not _needs_judgment(r):
                continue
            body_hash = _judge_body_hash(r)
            for disp, tgt in zip(r["targets"], r["_target_paths"]):
                chash = _content_hash(Path(tgt))
                key = f"{r['id']}-{body_hash}-{chash}-{model}"
                hit = _verdict_cache_get(cdir, key) if cdir else None
                if hit:
                    cached.append({"rule": r["id"], "target": disp, "key": key, **hit})
                    continue
                tasks.append({
                    "rule": r["id"], "ruleset": g["ruleset"], "tier": r["tier"],
                    "title": r["title"], "selector": r["selector"],
                    "check_pattern": r.get("check_pattern"), "why": r.get("why"),
                    "flat_file": g["flat_file"], "source": g["source"],
                    "target": disp, "target_path": tgt, "key": key,
                })
    return {"model": model, "tasks": tasks, "cached": cached,
            "task_count": len(tasks), "cached_count": len(cached)}


def record_verdict(cdir: Path, key: str, status: str, detail: str) -> None:
    """Persist an agent verdict under its Q3 cache key (used by --record-verdict)."""
    _verdict_cache_put(cdir, key, {"status": status, "detail": detail})


def render_report(plan: dict, mech: dict, man: dict) -> str:
    """One unified audit view: mechanical verdicts + the agent-judgment residue."""
    c = mech["counts"]
    out = [f"# audit report — {plan['umbrella']} on {Path(plan['target']).name}", ""]
    out.append(f"- scope files: {plan['scope_file_count']}  ·  "
               f"rulesets: {len(plan['groupings'])}")
    out.append(f"- mechanical: **{c['pass']} pass · {c['fail']} fail · "
               f"{c.get('warn', 0)} warn · {c.get('except', 0)} except · "
               f"{c['error']} error** "
               f"(cache hits {c['cached']})")
    out.append(f"- to judge: **{man['task_count']}**  ·  judged-cached: {man['cached_count']}")
    out.append("")
    fails = [v for v in mech["results"]
             if v["status"] not in ("pass", "warn", "except")]
    out.append("## mechanical failures" if fails else "## mechanical — all clean")
    for v in fails:
        mark = {"fail": "✗", "error": "!"}.get(v["status"], "?")
        out.append(f"- {mark} {v['rule']} — {v['target']}"
                   + (f"  ({v['detail']})" if v["detail"] else ""))
    out.append("")
    # Cosmetic findings get their own section, below the failures and clearly
    # not among them (T138): they name nothing a reader experiences as broken.
    warns = [v for v in mech["results"] if v["status"] == "warn"]
    if warns:
        out.append(f"## cosmetic ({len(warns)} — nothing here is broken)")
        for v in warns:
            out.append(f"- ~ {v['rule']} — {v['target']}"
                       + (f"  ({v['detail']})" if v["detail"] else ""))
        out.append("")
    # Accepted deviations get a section of their own — never folded into the
    # clean count (F314). A report that hides them makes a growing exception
    # pile look exactly like a corpus that never needed one.
    excepted = [v for v in mech["results"] if v["status"] == "except"]
    probs = mech.get("exception_problems", [])
    stale = mech.get("stale_exceptions", [])
    declined = mech.get("declined_exceptions", [])
    if excepted or probs or stale or declined:
        out.append(f"## accepted deviations ({len(excepted)} suppressed — "
                   f"see `{_anchor_slug(Path(plan['anchor_root']))} Exceptions.md`)")
        # R-exception-discipline-12 — the concentration line, and it is aimed at
        # the AGENT, not the user.
        #
        # Written first on the theory that it would carry the pattern to Dan,
        # which [[Warden PRD]] § Refinement then made wrong the same day. Not
        # because a report is off-limits — one rule or one deviation is fine to
        # put in front of him — but because a LIST is an at-scale artifact, and
        # settling one row of it would not settle the next. His dissatisfaction
        # arrives from a page that looks wrong, and what he gives back is a
        # generality that re-decides every row at once.
        #
        # What survives is the other reader. The agent DOES read this report, and
        # one rule absorbing several suppressions in a single run is the shape it
        # should reconsider before adding a sixth — either the rule is wrong
        # (-10) or its own grading has drifted loose (-12). Self-correction
        # ahead of the user noticing, which is the only kind that saves him a
        # conversation. Three is the floor: two is a coincidence, and a two-row
        # list already shows it.
        by_rule: dict[str, int] = {}
        for v in excepted:
            by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1
        heavy = sorted(((n, r) for r, n in by_rule.items() if n >= 3), reverse=True)
        for n, rule in heavy:
            out.append(f"- ⚑ **{rule} is carrying {n} of them here** — one rule "
                       f"absorbing this many is the shape worth reading before "
                       f"the rows: either the rule is wrong "
                       f"([[R-exception-discipline]]-10) or the grading has "
                       f"drifted loose (-12).")
        for v in excepted:
            out.append(f"- ⊘ {v['rule']} — {v['target']}"
                       + (f"  ({v['detail']})" if v["detail"] else ""))
        for p in probs:
            out.append(f"- ! malformed exception row, suppressing nothing — {p}")
        # A refused or still-ungraded row is neither an accepted deviation nor a
        # stale one, and printing it alongside both is what keeps the table's
        # third state from reading as either of the other two.
        moot = set(mech.get("moot_exceptions", []))
        for d in declined:
            # The fourth state, and the one that used to hide inside the third:
            # a proposal whose rule now PASSES. It reads identically to "waiting
            # on a grade" while asking for the opposite action, so it gets its
            # own sentence naming the cost of doing what the old message invited.
            if d["handle"] in moot:
                out.append(f"- ~ {d['handle']} ({d['rule']} on `{d['target']}`) — "
                           f"**moot: the rule now passes on this target.** Retire "
                           f"the row; grading it would suppress a working rule. "
                           f"See [[R-exception-discipline]]-13.")
            else:
                out.append(f"- ~ {d['handle']} ({d['rule']} on `{d['target']}`) — "
                           f"{d['declined']}")
        # Distinct from stale, and the distinction is the whole point: this row
        # is well-formed, in scope, and aimed at a rule that really ran — and
        # CRASHED, so there was no verdict for it to rewrite. Reported as stale
        # it sends the reader to look for a defect in their own row.
        for h in mech.get("unsuppressable_exceptions", []):
            out.append(f"- ~ {h} — the rule **errored**: the checker crashed, so "
                       "there is no verdict to suppress. The row is not stale "
                       "and needs no repair — fix the checker; see "
                       "[[R-exception-discipline]]-08.")
        for h in sorted(moot - {d["handle"] for d in declined}):
            out.append(f"- ~ {h} — **moot: the rule now passes on this row's own "
                       f"target.** The grade is covering nothing; retire the row. "
                       f"Distinct from stale below, which cannot tell a repaired "
                       f"deviation from a rule that never ran here.")
        if stale:
            out.append("- ~ did no work this run (stale, or the rule was out of "
                       f"scope): {', '.join(stale)}")
        out.append("")
    out.append(f"## judgment residue ({man['task_count']} tasks)")
    if not man["tasks"]:
        out.append("_none — every applicable rule was mechanical or cached._")
    else:
        out.append("Run `audit-plan <target> --judge --model <M>` for the full manifest; "
                   "judge each, then `--record-verdict`. Summary by ruleset:")
        by_rs: dict[str, int] = {}
        for t in man["tasks"]:
            by_rs[t["ruleset"]] = by_rs.get(t["ruleset"], 0) + 1
        for rs in sorted(by_rs):
            out.append(f"- {rs}: {by_rs[rs]} task(s)")
    return "\n".join(out)


def render_manifest(man: dict) -> str:
    out = [f"# agent-judge manifest — model {man['model']}  ·  "
           f"{man['task_count']} to judge  ·  {man['cached_count']} cached", ""]
    if not man["tasks"]:
        out.append("_no judgment tasks — all mechanical or cached._")
    for t in man["tasks"]:
        out.append(f"## {t['rule']} — {t['target']}  ({t['ruleset']}, {t['tier']})")
        out.append(f"- {t['title']}")
        if t.get("check_pattern"):
            out.append(f"- check: {t['check_pattern']}")
        out.append(f"- record with: `--record-verdict --key {t['key']} --status <pass|fail> --detail \"…\"`")
        out.append("")
    return "\n".join(out)


# ── CLI ─────────────────────────────────────────────────────────────────────

def resolve_target(arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.exists():
        return p.resolve()
    # Treat as a slug: look under examples/ then repo root then cwd.
    for base in (REPO_ROOT / "examples", REPO_ROOT, Path.cwd()):
        cand = base / arg
        if cand.is_dir():
            return cand.resolve()
    raise SystemExit(f"audit-plan: cannot resolve target {arg!r}")


def main(argv):
    ap = argparse.ArgumentParser(prog="audit-plan")
    ap.add_argument("target", nargs="?", help="anchor path/slug or .md document")
    ap.add_argument("--mode", choices=("anchor", "doc"))
    ap.add_argument("--order", choices=("file", "rule"))
    ap.add_argument("--batch", metavar="DIR", help="rule-major sweep over anchors under DIR")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--run", action="store_true",
                    help="execute the mechanical (check::) rules and report verdicts")
    ap.add_argument("--judge", action="store_true",
                    help="emit the agent-judgment manifest (residue after --run, cache-filtered)")
    ap.add_argument("--report", action="store_true",
                    help="unified audit view: mechanical verdicts + judgment residue summary")
    ap.add_argument("--model", default="unknown",
                    help="model-id for the judgment verdict cache key (Q3)")
    ap.add_argument("--record-verdict", action="store_true",
                    help="persist one agent verdict: --key K --status pass|fail [--detail D]")
    ap.add_argument("--key")
    ap.add_argument("--status", choices=("pass", "fail", "error"))
    ap.add_argument("--detail", default="")
    ap.add_argument("--on-write", action="store_true",
                    help="F177 hook driver: fix mechanical fails in place; emit messages for fails with no fixer")
    ap.add_argument("--cache-dir")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--verify-registry", action="store_true",
                    help="check check::/fix:: refs against the registry both ways (F289)")
    args = ap.parse_args(argv)

    cdir = None if args.no_cache else cache_dir(args.cache_dir)

    if args.verify_registry:
        warns: list[str] = []
        rulesets, seen = [], set()
        for u in ("R-doc", "R-anchor"):
            for rs in flatten_umbrella(u, warns):
                if rs["name"] not in seen:
                    seen.add(rs["name"])
                    rulesets.append(rs)
        reachable = len(rulesets)
        seen_reachable = set(seen)  # snapshot before the corpus sweep widens `seen`
        for rs in all_corpus_rulesets():
            if rs["name"] not in seen:
                seen.add(rs["name"])
                rulesets.append(rs)
        rep = verify_registrations(rulesets)
        rep["reachable"] = reachable
        rep["total"] = len(rulesets)
        rep["inert_umbrellas"] = inert_umbrellas(seen_reachable, ("R-doc", "R-anchor"))
        if args.json:
            print(json.dumps(rep, indent=2))
            return 1 if rep["ghosts"] else 0
        print(f"{rep['total']} rulesets with rules — {rep['reachable']} reachable from "
              f"R-doc/R-anchor, {rep['total'] - rep['reachable']} outside the closure")
        for label, key in (("ghost refs (registered nowhere — silently agent-judgment)", "ghosts"),
                           ("undeclared (resolves only globally — breaks on extraction)", "undeclared"),
                           ("name clashes (first wins)", "clashes")):
            print(f"\n{label}: {len(rep[key])}")
            for line in rep[key]:
                print(f"  {line}")
        print(f"\ninert umbrellas (aggregate rules, arm none — T208): "
              f"{len(rep['inert_umbrellas'])}")
        print("  `audit-plan.py` resolves R-doc and R-anchor and nothing else; an "
              "include:: anywhere out here looks exactly like adoption and is not")
        for line in rep["inert_umbrellas"]:
            print(f"  {line}")
        print(f"\norphan checkers (registered, invoked by no rule): {len(rep['orphans'])}")
        print("  each is either a rule waiting to be written or dead code — "
              "only reading it tells you which")
        for n in rep["orphans"]:
            print(f"  {n}")
        return 1 if rep["ghosts"] else 0

    if args.record_verdict:
        if not args.key or not args.status:
            ap.error("--record-verdict requires --key and --status")
        if cdir is None:
            ap.error("--record-verdict needs a cache (do not pass --no-cache)")
        record_verdict(cdir, args.key, args.status, args.detail)
        print(f"recorded {args.status} for {args.key}")
        return 0

    if args.batch:
        root = Path(args.batch).expanduser().resolve()
        # T100 — same exclusion as `enumerate_scope`, and it has to be here too: an
        # anchor discovered under `.trash` would get a whole plan of its own, not
        # merely contribute files to someone else's.
        anchors = sorted({p.parent for p in root.rglob(".anchor")
                          if not _under_dot_dir(p, root)})
        order = args.order or "rule"
        stats: dict = {}
        plans = []
        for a in anchors:
            plans.append(plan_one(a, "anchor", cdir, [], sub_anchor_roots(a), stats))

        # ATT bug, 2026-08-11: this branch used to `return 0` here, BEFORE the
        # `if args.run:` below — so `--batch DIR --run` accepted the flag,
        # printed thousands of recipe lines and a tidy footer, and executed not
        # one check. Not zero findings for one ruleset: zero verdicts for every
        # rule in the corpus, silently, in the direction that manufactures
        # confidence. It had already produced one published wrong measurement
        # (`DAS Stone` read 13 RECIPE lines as 13 executed `R-rocks` verdicts).
        #
        # Wiring it is repair, not a new capability: `--run`'s help promises it
        # unconditionally, [[F001]] § What done looks like specifies "a `--batch`
        # run over a directory of anchors produces the same per-anchor reports",
        # and `test-t098-batch-harness.py` exists precisely because
        # `--batch ~/ob/kmr --run` "had never once completed" — T098 fixed the
        # decode crash that stopped it and left it returning early anyway.
        #
        # The corpus TOTAL is the point of a sweep, so it is printed last and
        # separately from the per-anchor blocks. A per-anchor total alone is
        # what you can already get by auditing anchors one at a time.
        if args.run or args.judge or args.report:
            mech_total = {"pass": 0, "fail": 0, "warn": 0,
                          "except": 0, "error": 0, "cached": 0}
            per_anchor = []
            for a, pl in zip(anchors, plans):
                entry: dict = {"anchor": str(a)}
                if args.run or args.report:
                    rep = execute_plan(pl, cdir)
                    for k in mech_total:
                        mech_total[k] += rep["counts"].get(k, 0)
                    entry["mechanical"] = rep
                if args.judge or args.report:
                    entry["judgment"] = judge_manifest(pl, cdir, args.model)
                per_anchor.append(entry)
            if args.json:
                print(json.dumps({"batch": str(root), "stats": stats,
                                  "totals": mech_total, "anchors": per_anchor},
                                 indent=2))
            else:
                for a, pl, entry in zip(anchors, plans, per_anchor):
                    if args.report:
                        print(render_report(pl, entry["mechanical"], entry["judgment"]))
                    elif args.run:
                        print(f"# {a}")
                        print(render_verdicts(entry["mechanical"]))
                    else:
                        print(render_manifest(entry["judgment"]))
                    print("\n" + "=" * 72 + "\n")
                if args.run or args.report:
                    print(f"batch total: {len(anchors)} anchors  ·  "
                          + "  ".join(f"{k} {v}" for k, v in mech_total.items()))
            # A sweep that found real failures exits non-zero, so a caller can
            # gate on it without parsing the report.
            return 1 if mech_total["fail"] or mech_total["error"] else 0

        if args.json:
            print(json.dumps({"batch": str(root), "stats": stats, "plans": plans}, indent=2))
        else:
            for pl in plans:
                print(render_recipe(pl, order, cdir))
                print("\n" + "=" * 72 + "\n")
            print(f"batch: {len(anchors)} anchors  ·  flatten cache: "
                  f"{stats.get('flatten_miss', 0)} miss / "
                  f"{stats.get('flatten_disk_hit', 0)} disk-hit / "
                  f"{stats.get('flatten_mem_hit', 0)} mem-hit"
                  f"  ·  plan cache: {stats.get('plan_miss', 0)} miss / "
                  f"{stats.get('plan_hit', 0)} hit")
        return 0

    if not args.target:
        ap.error("target required (or use --batch)")
    target = resolve_target(args.target)
    mode = args.mode or ("doc" if target.is_file() else "anchor")
    order = args.order or ("rule" if mode == "anchor" and False else "file")
    exclude = sub_anchor_roots(target) if mode == "anchor" else None
    plan = plan_one(target, mode, cdir, [], exclude)
    if args.on_write:
        report = execute_on_write(plan, cdir)
        if args.json:
            print(json.dumps(report))
        else:
            print(render_on_write(report))
        return 0
    if args.run:
        report = execute_plan(plan, cdir)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(render_verdicts(report))
        return 0
    if args.judge:
        man = judge_manifest(plan, cdir, args.model)
        if args.json:
            print(json.dumps(man, indent=2))
        else:
            print(render_manifest(man))
        return 0
    if args.report:
        mech = execute_plan(plan, cdir)
        man = judge_manifest(plan, cdir, args.model)
        if args.json:
            print(json.dumps({"plan": plan, "mechanical": mech, "judgment": man}, indent=2))
        else:
            print(render_report(plan, mech, man))
        return 0
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(render_recipe(plan, order, cdir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
