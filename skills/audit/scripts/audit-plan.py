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
from pathlib import Path

HOME = Path.home()

# ── repo discovery ──────────────────────────────────────────────────────────

def find_repo_root(start: Path) -> Path:
    """Walk up from the script to the ob-skills repo root (has facets/ + skills/)."""
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
_RULE_RE = re.compile(
    r"^#+\s+RULE\s+(R-[\w-]+-\d+)\s+[—-]\s+(.*?)\s*\((checked|sampled|stated|tracked)\)\s*$"
)
_FIELD_RE = re.compile(r"^([a-z][a-z_-]*)::\s*(.*)$")
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _strip_link_target(raw: str) -> str:
    """`[[FCT Brief#RULESET R-brief|embedded body]]` → `FCT Brief#RULESET R-brief`."""
    inner = raw.strip()
    if inner.startswith("[[") and inner.endswith("]]"):
        inner = inner[2:-2]
    return inner.split("|", 1)[0].strip()


def extract_ruleset_block(text: str, name: str | None = None) -> tuple[list[str], int] | None:
    """Return (block_lines, heading_level) for `# RULESET <name>` (or first RULESET
    block when name is None). Block spans until the next heading of level <= its own."""
    lines = text.splitlines()
    start = None
    level = None
    for i, ln in enumerate(lines):
        m = _RULESET_RE.match(ln)
        if m and (name is None or m.group(2) == name):
            start = i
            level = len(m.group(1))
            break
    if start is None or level is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        hm = re.match(r"^(#+)\s+\S", lines[j])
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
        "description": None,
        "includes": [],
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
        elif key == "where":
            rs["where"] = val or None
        elif key == "description":
            rs["description"] = val or None
        i += 1
    # RULE entries.
    cur = None
    for ln in block[i:]:
        rm = _RULE_RE.match(ln)
        if rm:
            cur = {
                "id": rm.group(1),
                "title": rm.group(2).strip(),
                "tier": rm.group(3),
                "where": None,
                "check": None,
                "check_pattern": None,
                "why": None,
            }
            rs["rules"].append(cur)
            continue
        if cur is None:
            continue
        s = ln.strip()
        wm = _FIELD_RE.match(s)
        if wm and wm.group(1) in ("where", "check"):
            cur[wm.group(1)] = wm.group(2).strip() or None
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
    return out


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

    if umbrella in _FLATTEN_MEM:
        rs, warns = _FLATTEN_MEM[umbrella]
        warnings.extend(warns)
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


def parse_selector(where: str) -> tuple[str, str]:
    """(kind, arg). kind ∈ always|file|anchor|sentinel. Bare glob → ('file', glob)."""
    w = where.strip()
    if w == "always":
        return "always", ""
    if w == "anchor":
        return "anchor", ""
    if w.startswith("file:"):
        return "file", w[len("file:"):].strip()
    if w.startswith("sentinel:"):
        return "sentinel", w[len("sentinel:"):].strip()
    return "file", w  # bare glob


def _glob_to_relpattern(glob: str) -> str:
    g = glob.strip()
    if g.startswith("{ANCHOR}/"):
        g = g[len("{ANCHOR}/"):]
    elif g == "{ANCHOR}":
        g = ""
    return g


def _anchor_name(anchor_root: Path) -> str:
    """{NAME} token → the anchor's slug (from .anchor), else its folder name."""
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


def _match_file_glob(arg: str, scope_files: list[Path], anchor_root: Path) -> list[Path]:
    """Resolve a `file:` where-glob to scope files, honoring the full spec
    ([[FCT Ruleset]] § Where clause): {ANCHOR}/{NAME} tokens, brace-alternation,
    comma-union, and gitignore-style !-negation."""
    name = _anchor_name(anchor_root)
    include: set[Path] = set()
    exclude: set[Path] = set()
    for term in _split_terms(arg):
        neg = term.startswith("!")
        if neg:
            term = term[1:].strip()
        rel = _glob_to_relpattern(term).replace("{NAME}", name)
        if not rel:
            paths = {anchor_root.resolve()}
        else:
            paths = set()
            for pat in _expand_braces(rel):
                try:
                    paths |= {p.resolve() for p in anchor_root.glob(pat)}
                except (ValueError, IndexError):
                    pass
        (exclude if neg else include).update(paths)
    hits = include - exclude
    return [p for p in scope_files if p.resolve() in hits]


def match_targets(kind: str, arg: str, scope_files: list[Path], anchor_root: Path) -> list[Path]:
    if kind == "always":
        return list(scope_files)
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
            try:
                if rx.search(p.read_text(encoding="utf-8")):
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
        parent = dot.parent.resolve()
        if parent != t:
            roots.add(parent)
    return roots


def enumerate_scope(target: Path, mode: str,
                    exclude_roots: set[Path] | None = None) -> tuple[Path, list[Path]]:
    """Return (anchor_root, scope_files). For doc mode the scope is the one file.
    Files under any path in exclude_roots (nested sub-anchors) are dropped."""
    if mode == "doc":
        return target.parent, [target]
    exclude_roots = exclude_roots or set()
    files = []
    for p in target.rglob("*.md"):
        if "/.git/" in str(p):
            continue
        if any(r == p.parent or r in p.parents for r in exclude_roots):
            continue
        files.append(p)
    return target, files


# ── flattened-rules cache ───────────────────────────────────────────────────

def cache_dir(opt: str | None) -> Path:
    d = Path(opt).expanduser() if opt else (HOME / ".cache" / "ob-skills-audit")
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
            h.update(f"R|{r['id']}|{r['tier']}|{r.get('where')}|{r.get('check')}".encode())
    return h.hexdigest()[:12]


def plan_one(target: Path, mode: str, cdir: Path | None, warnings: list[str],
             exclude_roots: set[Path] | None = None, stats: dict | None = None) -> dict:
    umbrella = "R-doc" if mode == "doc" else "R-anchor"
    rulesets = flatten_umbrella_cached(umbrella, cdir, warnings, stats)
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
            kind, arg = parse_selector(effective_where(r, rs))
            if mode == "doc" and kind == "anchor":
                continue  # anchor-structure rules are N/A at the doc level
            tgts = match_targets(kind, arg, scope_files, anchor_root)
            if not tgts:
                continue  # selector miss → N/A
            matched_rules.append({
                "id": r["id"], "tier": r["tier"], "title": r["title"],
                "selector": effective_where(r, rs), "check": r.get("check"),
                "check_pattern": r.get("check_pattern"), "why": r.get("why"),
                "targets": [str(p.relative_to(anchor_root)) if p != anchor_root else "{ANCHOR}"
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
    return path.read_text(encoding="utf-8")


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


def chk_anchor_has(target, anchor_root, args):
    dot = anchor_root / ".anchor"
    if not dot.is_file():
        return "fail", "no .anchor file"
    text = _read(dot)
    missing = [k for k in args if not re.search(rf"(^|\b){re.escape(k)}\s*[:=]", text, re.MULTILINE)]
    return ("pass", "") if not missing else ("fail", f"missing in .anchor: {', '.join(missing)}")


def chk_entry_page_matches_slug(target, anchor_root, args):
    ep = _entry_page(anchor_root)
    if ep is None:
        return "fail", f"no entry page {_anchor_slug(anchor_root)}.md"
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
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    return ("pass", "") if re.search(r"^# \S", _read(f), re.MULTILINE) else ("fail", "no H1")


def chk_no_blank_after_h1(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"^# \S", ln):
            if i + 1 >= len(lines) or lines[i + 1].strip() == "":
                return "fail", "blank line directly after H1"
            return "pass", ""
    return "fail", "no H1"


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
    r"^F\d+ [—-] ",              # F<NNN> — title  (Features)
    r"^US-[A-Za-z]+-\d+ [—-] ",  # US-<RID>-<N> — title  (Stories)
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
    carries any ancestor anchor's slug (per FCT Naming §Folder-anchor files)."""
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


def chk_name_slug_prefixed(target, anchor_root, args):
    """Per-file (R-naming-01): basename starts with `{slug} ` for this anchor OR
    any ancestor anchor (nested anchors prefix with the root slug), equals an
    anchor marker, or matches a sanctioned allowlist shape (R-naming-03).
    By-chance exemptions (R-naming-04) are explicitly not mechanically audited."""
    if not target.is_file():
        return "pass", "not a file"
    slugs = _ancestor_anchor_slugs(anchor_root)
    stem = target.stem
    if any(stem == s for s in slugs):
        return "pass", "anchor marker"
    if any(stem.startswith(f"{s} ") for s in slugs):
        return "pass", ""
    for pat in _NAME_ALLOWLIST:
        if re.match(pat, stem):
            return "pass", "allowlisted pattern"
    return "fail", f"{target.name!r} lacks a {slugs!r} prefix / allowlist match"


def chk_h1_after_frontmatter(target, anchor_root, args):
    """The H1 is the first non-blank line after the YAML frontmatter. Frontmatter
    (the `--- … ---` description block) is canonical, not forbidden — this replaces
    the old body-only / inline-`description::` rules."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    body = text[m.end():] if m else text
    for ln in body.splitlines():
        if ln.strip():
            if re.match(r"^# \S", ln):
                return "pass", ""
            return "fail", f"first line after frontmatter is not an H1: {ln!r}"
    return "fail", "no body after frontmatter"


def chk_h1_matches_slug(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    slug = _anchor_slug(anchor_root)
    for ln in _read(f).splitlines():
        if ln.startswith("# "):
            h1 = ln[2:].strip()
            if re.match(rf"^{re.escape(slug)}\s*[-–—]\s+\S", h1):
                return "pass", h1
            if h1 == slug or h1 == anchor_root.name:
                return "pass", f"bare-name: {h1}"
            return "fail", f"H1 {h1!r} is not '{slug} - <name>'"
    return "fail", "no H1"


def chk_breadcrumb_row(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    for ln in _read(f).splitlines():
        if ln.lstrip().startswith("|"):
            if re.search(r"\|\s*-\[\[.+?\]\]-\s*\|.*hook://", ln.strip()):
                return "pass", ""
            return "fail", "first table row is not a breadcrumb (-[[…]]- … hook://)"
    return "pass", "no dispatch table (tableless anchor)"


def chk_design_row_iff_folder(target, anchor_root, args):
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    name = anchor_root.name
    has_folder = (anchor_root / f"{name} Design").is_dir()
    text = _read(f)
    # A *Design row*'s first cell is the design-folder link aliased exactly "Design"
    # (or a bare "Design" cell) — NOT a member doc like "UX Design"/"API Design".
    has_row = (bool(re.search(r"^\|\s*\[\[[^\]|]*\|Design\]\]", text, re.MULTILINE))
               or bool(re.search(r"^\|\s*Design\s*\|", text, re.MULTILINE)))
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


def _first_h1_idx(lines):
    for i, ln in enumerate(lines):
        if re.match(r"^# ", ln):
            return i
    return None


def chk_header_has_field(target, anchor_root, args):
    """Header (lines after H1, before first blank) carries `<field>::`. Arg: field."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    field = args[0] if args else "include"
    h1_idx = _first_h1_idx(lines)
    if h1_idx is None:
        return "fail", "no H1"
    for ln in _header_block(lines, h1_idx):
        if re.match(rf"^{re.escape(field)}::", ln):
            return "pass", ""
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
    if not re.match(r"^# ", nonblank[0]):
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
    h1_idx = _first_h1_idx(lines)
    if h1_idx is None:
        return "fail", "no H1"
    # summary line: first non-blank, non-table line within 2 lines of the H1
    summary_idx = None
    for i in range(h1_idx + 1, min(h1_idx + 3, len(lines))):
        s = lines[i].strip()
        if s and not s.startswith("|"):
            summary_idx = i
            break
    if summary_idx is None:
        return "fail", "no one-line summary after H1"
    # require a breadcrumb dispatch table within ~12 lines of the summary
    for i in range(summary_idx + 1, min(summary_idx + 12, len(lines))):
        if re.search(r"^\|\s*-\[\[.+?\]\]-\s*\|", lines[i]):
            return "pass", "H1 -> summary -> breadcrumb table"
    return "fail", "no breadcrumb dispatch table (missing masthead)"


def chk_triggers_section_iff_declared(target, anchor_root, args):
    """## Triggers present IFF triggers declared (has typed ### H3 entries)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
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


# -- R-ruleset -----------------------------------------------------------------

def chk_all_rules_have_id(target, anchor_root, args):
    """Every RULE heading matches R-<slug>-NN."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    headings = [ln for ln in _read(f).splitlines() if re.match(r"^#+\s+RULE\s+", ln)]
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
    for ln in _read(f).splitlines():
        m = re.search(r"RULE\s+(R-[a-z0-9-]+-\d{2})\b", ln)
        if m:
            if m.group(1) in seen:
                return "fail", f"duplicate rule id: {m.group(1)}"
            seen.add(m.group(1))
    return "pass", "" if seen else "no rules found"


def chk_all_rules_have_tier(target, anchor_root, args):
    """Every RULE heading ends with a (tracked|stated|sampled|checked) tier."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    headings = [ln for ln in _read(f).splitlines() if re.match(r"^#+\s+RULE\s+", ln)]
    if not headings:
        return "pass", "no rules found"
    for h in headings:
        if not re.search(r"\((tracked|stated|sampled|checked)\)\s*$", h):
            return "fail", f"rule missing tier: {h[:60]}"
    return "pass", ""


def chk_checked_rules_have_pattern(target, anchor_root, args):
    """Every (checked)/(sampled) rule body carries a **Check pattern:** field."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    missing = []
    i = 0
    while i < len(lines):
        m = re.match(r"^#+\s+RULE\s+(R-[a-z0-9-]+-\d{2})", lines[i])
        if m and re.search(r"\((checked|sampled)\)\s*$", lines[i]):
            rule_id = m.group(1)
            body = ""
            i += 1
            while i < len(lines) and not re.match(r"^#+\s+", lines[i]):
                body += lines[i] + "\n"
                i += 1
            if "**Check pattern:**" not in body:
                missing.append(rule_id)
        else:
            i += 1
    if missing:
        return "fail", "missing Check pattern: " + ", ".join(missing[:3])
    return "pass", ""


def chk_ruleset_no_frontmatter(target, anchor_root, args):
    """Standalone ruleset file (# RULESET first non-blank) has no YAML frontmatter."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    first = next((ln for ln in lines if ln.strip()), None)
    if first is None:
        return "pass", "empty file"
    if re.match(r"^#+\s+RULESET\s+R-", first):
        for ln in lines:
            if ln.strip().startswith("---"):
                return "fail", "standalone ruleset file has YAML frontmatter"
        return "pass", ""
    return "pass", "not a standalone ruleset file"


# -- R-status ------------------------------------------------------------------

def chk_status_filename_valid(target, anchor_root, args):
    """Filename is exactly '{SLUG} Status.md'."""
    slug = _anchor_slug(anchor_root)
    expected = f"{slug} Status.md"
    if target.name == expected:
        return "pass", ""
    return "fail", f"expected {expected!r}, got {target.name!r}"


def chk_status_in_track_folder(target, anchor_root, args):
    """File lives in {SLUG} Track/."""
    slug = _anchor_slug(anchor_root)
    expected_parent = anchor_root / f"{slug} Track"
    if target.parent == expected_parent:
        return "pass", ""
    return "fail", f"not in {expected_parent.name}/ folder; found in {target.parent.name}/"


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
    """{SLUG} Track.md contains a [[{SLUG} Status]] link."""
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
    """File named {SLUG} Testing.md; no legacy {SLUG} Testing Strategy.md alongside."""
    if not target.is_file():
        return "error", "target is not a file"
    slug = _anchor_slug(anchor_root)
    if target.name != f"{slug} Testing.md":
        return "fail", f"file should be '{slug} Testing.md' not '{target.name}'"
    design_dir = anchor_root / f"{anchor_root.name} Design"
    legacy = design_dir / f"{slug} Testing Strategy.md"
    if legacy.is_file():
        return "fail", f"legacy file {legacy.name} exists alongside {target.name}"
    return "pass", ""


def _section_body(lines, header_re, stop_re=r"^## "):
    """Lines under the first heading matching header_re, up to next stop_re."""
    start = None
    for i, ln in enumerate(lines):
        if re.match(header_re, ln):
            start = i
            break
    if start is None:
        return None
    out = []
    for i in range(start + 1, len(lines)):
        if re.match(stop_re, lines[i]):
            break
        out.append(lines[i])
    return out


def chk_strategy_subsections_present_ordered(target, anchor_root, args):
    """## Strategy has 4 H3s in order: Test Kinds, Completeness Targets, Responsibilities, Tier Mapping."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    lines = _read(f).splitlines()
    body = _section_body(lines, r"^## Strategy\b")
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
    lines = _read(f).splitlines()
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
    """**Name** at start of bullets under a section heading."""
    body = _section_body(lines, header_re, stop_re=r"^### ")
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
    lines = _read(f).splitlines()
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
    """Yield table-row lines under ## Proposed Tests."""
    pt_start = None
    for i, ln in enumerate(lines):
        if re.match(r"^## Proposed Tests\b", ln):
            pt_start = i
            break
    if pt_start is None:
        return None
    rows = []
    for i in range(pt_start + 1, len(lines)):
        if re.match(r"^## ", lines[i]):
            break
        if re.match(r"^\|", lines[i]):
            rows.append(lines[i])
    return rows


def chk_proposed_tests_rows_have_spec(target, anchor_root, args):
    """Every Proposed Tests table row has a non-empty last (Spec) cell."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    rows = _proposed_tests_rows(_read(f).splitlines())
    if rows is None:
        return "fail", "no ## Proposed Tests section"
    for ln in rows:
        cells = [c.strip() for c in ln.split("|")[1:-1]]
        if not cells:
            continue
        if re.match(r"^[\s:-]+$", cells[-1]):  # separator row
            continue
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
        cells = [c.strip() for c in ln.split("|")[1:-1]]
        if not cells:
            continue
        spec = cells[-1]
        if not spec or spec == "-" or re.match(r"^[\s:-]+$", spec):
            continue
        if not re.match(r"^\[\[.+\]\]$", spec) and not re.match(r"^\[[^\]]+\]$", spec):
            return "fail", f"Spec cell invalid (not wiki-link or bracket): {spec}"
    return "pass", ""


def chk_status_field_valid(target, anchor_root, args):
    """Frontmatter status: in drafting|in-review|accepted."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    fm = _frontmatter(_read(f))
    if fm is None:
        return "fail", "no YAML frontmatter"
    m = re.search(r"^status\s*:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return "fail", "frontmatter missing status: field"
    value = m.group(1).strip().strip("\"'")
    if value not in ("drafting", "in-review", "accepted"):
        return "fail", f"status value {value!r} not valid"
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
        return "error", "no file to inspect"
    if re.search(r"\|\s*\[?\[?Track\]?\]?\s*\|", _read(f)):
        return "fail", "Track row present on ecosystem anchor"
    return "pass", ""


def chk_all_files_folders_prefixed_with_name(target, anchor_root, args):
    """Every file/folder inside the anchor is prefixed with the anchor name."""
    anchor_name = anchor_root.name
    slug = _anchor_slug(anchor_root)
    exempt = {f"{slug}.md", f"{anchor_name}.md", ".anchor"}
    violations = []
    for item in anchor_root.rglob("*"):
        if "/.git/" in str(item):
            continue
        if item.name in exempt:
            continue
        if not item.name.startswith(anchor_name):
            violations.append(item.name)
    if violations:
        more = "..." if len(violations) > 5 else ""
        return "fail", "unprefixed items: " + ", ".join(violations[:5]) + more
    return "pass", ""


# -- R-prd ---------------------------------------------------------------------

def chk_file_path_matches_prd_locations(target, anchor_root, args):
    """PRD at {NAME} Design/{NAME} PRD.md or {NAME} Design/{NAME} PRD/{NAME} PRD.md."""
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
            if re.match(r"^# \S", ln):
                return "pass", ""
            return "fail", f"first non-blank line is not H1: {ln!r}"
    return "fail", "file is empty or all blank"


def _h2_headings(text):
    return [m.group(1).strip() for ln in text.splitlines()
            for m in [re.match(r"^## (.+)$", ln)] if m]


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


def chk_user_stories_use_rid_numbering(target, anchor_root, args):
    """## User Stories H3s use US-{SLUG}-N: (inline form; folder form deferred)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
    if re.search(r"\[\[\s*[^\]]*\s*Stories\s*\]\]", text):
        return "pass", "folder form (deferred to R-stories)"
    slug = _anchor_slug(anchor_root)
    in_stories = False
    ids = []
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
    """No legacy {NAME} Open Questions.md in {NAME} Design/."""
    name = anchor_root.name
    legacy = anchor_root / f"{name} Design" / f"{name} Open Questions.md"
    if legacy.is_file():
        return "fail", f"legacy Open Questions file exists: {legacy.relative_to(anchor_root)}"
    return "pass", ""


def chk_design_workflow_modern_names(target, anchor_root, args):
    """## Design Workflow uses modern phase names, not legacy ones."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    body = _section_body(_read(f).splitlines(), r"^## Design Workflow")
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
    """Dispatch table has a Stories row displaying '{NAME} Stories'."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    text = _read(f)
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


# -- R-roadmap -----------------------------------------------------------------

def chk_file_exists(target, anchor_root, args):
    """A file (arg[0], with {NAME} substituted) exists under anchor_root."""
    if not args:
        return "error", "file_exists requires a path argument"
    slug = _anchor_slug(anchor_root)
    pattern = args[0].replace("{NAME}", slug)
    if (anchor_root / pattern).is_file():
        return "pass", f"{pattern} exists"
    return "fail", f"{pattern} does not exist"


def chk_milestone_checkbox(target, anchor_root, args):
    """Every M-prefixed milestone H2 carries a checkbox [x], [ ], or [~]."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    failures = []
    for i, ln in enumerate(_read(f).splitlines(), 1):
        if re.match(r"^## (M-|M\d)", ln) and not re.match(r"^## \[[x ~]\] ", ln):
            failures.append(f"line {i}: missing checkbox")
    return ("pass", "") if not failures else ("fail", "; ".join(failures[:3]))


def chk_milestone_status_line(target, anchor_root, args):
    """TOP-LEVEL milestones (token M<n> with no dot) carry a **Status**: line within
    ~10 lines. Sub-milestones (M1.0, M1.2.3 …) track status via their checkbox alone."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    lines = _read(f).splitlines()
    failures = []
    for i, ln in enumerate(lines):
        m = re.match(r"^#+\s+\[[x~]\]\s+(M\d+(?:\.\d+)*)\b", ln)
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
    lines = _read(f).splitlines()
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

def chk_log_path_exists(target, anchor_root, args):
    """{SLUG} Log/ folder or {SLUG} Log.md exists under the anchor."""
    slug = _anchor_slug(anchor_root)
    if (anchor_root / f"{slug} Log").is_dir() or (anchor_root / f"{slug} Log.md").is_file():
        return "pass", f"found {slug} Log"
    return "fail", f"no {slug} Log/ or {slug} Log.md under anchor"


def chk_log_dispatch_file_present(target, anchor_root, args):
    """If {SLUG} Log/ exists it contains {SLUG} Log.md with H1 '{SLUG} Log'."""
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
    """Entry files in {SLUG} Log/ match YYYY-MM-DD / YYYY-MM / YYYY date prefixes."""
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


def chk_log_dispatch_newest_first(target, anchor_root, args):
    """Dispatch table lists log entries newest-first (non-increasing dates)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file to inspect"
    matches = re.findall(r"\[\[(\d{4}(?:-\d{2})?(?:-\d{2})?)\s+[^\]]*\]\]", _read(f))
    if len(matches) < 2:
        return "pass", "fewer than 2 entries"

    def norm(d):
        parts = d.split("-")
        while len(parts) < 3:
            parts.append("01")
        return "-".join(parts)

    n = [norm(m) for m in matches]
    for i in range(len(n) - 1):
        if n[i] < n[i + 1]:
            return "fail", f"dispatch not newest-first: {matches[i]} before {matches[i + 1]}"
    return "pass", ""


def chk_log_anchor_page_link(target, anchor_root, args):
    """Anchor entry page carries a [[{SLUG} Log]] dispatch row."""
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
    brief_count = sum(1 for ln in lines if ln.strip() == "# BRIEF")
    if brief_count == 0:
        return "fail", "no '# BRIEF' heading"
    if brief_count > 1:
        return "fail", f"multiple '# BRIEF' headings ({brief_count})"
    last_h1 = None
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r"^#\s+\S", lines[i]):
            last_h1 = i
            break
    if last_h1 is None or lines[last_h1].strip() != "# BRIEF":
        return "fail", "'# BRIEF' is not the last H1"
    m = re.search(r"^# BRIEF\s*$", text, re.MULTILINE)
    if m is None or not text[m.end():].strip():
        return "fail", "'# BRIEF' section is empty"
    return "pass", ""


def chk_brief_h1_matches_name(target, anchor_root, args):
    """A '* Brief.md' sidecar's H1 equals its filename (without .md)."""
    if not target.is_file() or not target.name.endswith(" Brief.md"):
        return "pass", "not a Brief.md file"
    expected = target.stem
    for ln in _read(target).splitlines():
        if ln.startswith("# "):
            h1 = ln[2:].strip()
            return ("pass", h1) if h1 == expected else ("fail", f"H1 {h1!r} != filename {expected!r}")
    return "fail", "no H1 heading"


def chk_brief_not_nested(target, anchor_root, args):
    """Briefs don't nest: no '* Brief Brief.md', no '# BRIEF' inside a '* Brief.md'."""
    if not target.is_file() or not target.name.endswith(" Brief.md"):
        return "pass", "not a Brief.md file"
    if " Brief Brief.md" in target.name:
        return "fail", "nested brief: file named '* Brief Brief.md'"
    if re.search(r"^# BRIEF$", _read(target), re.MULTILINE):
        return "fail", "Brief.md file contains '# BRIEF' heading"
    return "pass", ""


# -- R-design ------------------------------------------------------------------

def chk_design_folder_children(target, anchor_root, args):
    """{NAME} Design/ contains required children (args are stem names, e.g. PRD)."""
    if target.is_file():
        return "pass", "not a folder"
    design = anchor_root / f"{anchor_root.name} Design"
    if not design.is_dir():
        return "pass", "no Design folder (N/A)"
    name = anchor_root.name
    missing = [a for a in args
               if not ((design / f"{name} {a}.md").is_file() or (design / f"{name} {a}").is_dir())]
    if missing:
        return "fail", "missing children: " + ", ".join(missing)
    return "pass", ""


def chk_status_facets_initialized(target, anchor_root, args):
    """When {NAME} Design/ exists, {NAME} Track/{NAME} Status.md has the facet lines (args)."""
    name = anchor_root.name
    if not (anchor_root / f"{name} Design").is_dir():
        return "pass", "no Design folder (N/A)"
    status_file = anchor_root / f"{name} Track" / f"{name} Status.md"
    if not status_file.is_file():
        return "fail", f"no {status_file.relative_to(anchor_root)}"
    text = _read(status_file)
    missing = [a for a in args if not re.search(rf"^{re.escape(a)}\s*::", text, re.MULTILINE)]
    if missing:
        return "fail", "missing facet lines: " + ", ".join(missing)
    return "pass", ""


# -- R-file-association --------------------------------------------------------

def chk_file_association_folder_structure(target, anchor_root, args):
    """Method-3 plural folder: has {Folder}.md anchor + dispatch table linking items."""
    if not target.is_dir():
        return "pass", "not a directory"
    folder = target.name
    if not re.search(r"\s+\w+s$", folder):
        return "pass", "not a plural-suffix folder"
    anchor_file = target / f"{folder}.md"
    if not anchor_file.is_file():
        return "fail", f"method-3 folder missing anchor file {folder}.md"
    anchor_text = _read(anchor_file)
    if not re.search(r"\|\s*\[\[[^\]]+\]\]", anchor_text):
        return "fail", f"anchor {folder}.md has no dispatch table with wiki-links"
    items = [p for p in target.glob("*.md") if p != anchor_file]
    if not items:
        return "fail", f"method-3 folder {folder} contains no item files"
    item_names = {p.stem for p in items}
    links = re.findall(r"\[\[([^\]|]+)", anchor_text)
    linked = {link.split("|")[0].split("/")[0].split("#")[0] for link in links}
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
    for ln in _read(f).splitlines():
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
    for ln in _read(target).splitlines():
        if ln.startswith("# "):
            h1 = ln[2:].strip()
            if h1.startswith(date_str):
                return "fail", f"H1 contains date prefix ({date_str}); expected just {title!r}"
            if h1 == title:
                return "pass", ""
            return "fail", f"H1 is {h1!r}, expected {title!r}"
    return "fail", "no H1 found in entry file"


# -- R-messages ----------------------------------------------------------------

def chk_h1_is_anchor_messages(target, anchor_root, args):
    """H1 matches the file's own '{prefix} Messages' name (prefix from the basename,
    e.g. 'HBR Messages.md' -> 'HBR Messages') — robust to nested anchors whose files
    carry the root slug rather than the sub-anchor folder name."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    want = Path(f).stem  # the file's own name without .md ("HBR Messages")
    for ln in _read(f).splitlines():
        if ln.startswith("# "):
            h1 = ln[2:].strip()
            return ("pass", h1) if h1 == want else ("fail", f"H1 {h1!r} is not '{want}'")
    return "fail", "no H1"


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

def chk_md_angle_brackets_safe(target, anchor_root, args):
    """Angle brackets need surrounding whitespace (outside code fences/spans)."""
    if not target.is_file():
        return "pass", "not a file"
    text = _read(target)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]*`", " ", text)
    bad_start = re.search(r"\S<[A-Za-z_]", text)
    bad_end = re.search(r"[A-Za-z_]>\S", text)
    if bad_start or bad_end:
        msgs = []
        if bad_start:
            msgs.append(f"\\S<[A-Za-z_] at line {text[:bad_start.start()].count(chr(10)) + 1}")
        if bad_end:
            msgs.append(f"[A-Za-z_]>\\S at line {text[:bad_end.start()].count(chr(10)) + 1}")
        return "fail", "; ".join(msgs)
    return "pass", ""


def chk_md_angle_brackets_backtick_only(target, anchor_root, args):
    """Strict (R-md-03): a literal `<` or `>` may appear ONLY inside an inline code
    span or a fenced code block — everywhere else it must be backticked or escaped.
    Code spans/fences are masked out first (that is the case we must exclude); then
    two sanctioned forms are dropped — the masthead `<br>` line-break, and the leading
    `>` of a blockquote / callout line (structural, not a content bracket) — then any
    surviving angle bracket fails. Masking preserves newlines so line numbers stay accurate."""
    if not target.is_file():
        return "pass", "not a file"
    text = _read(target)
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))      # mask, keep line count
    masked = re.sub(r"```[\s\S]*?```", blank, text)          # fenced code (backtick)
    masked = re.sub(r"~~~[\s\S]*?~~~", blank, masked)        # fenced code (tilde)
    masked = re.sub(r"(`+)[^\n]*?\1", blank, masked)         # inline code spans
    masked = re.sub(r"(?i)<br\s*/?>", "  ", masked)          # sanctioned masthead <br>
    hits = []
    for ln, raw in enumerate(masked.splitlines(), 1):
        line = re.sub(r"^\s*(?:>\s?)+", "", raw)             # drop blockquote / callout `>` markers
        m = re.search(r"[<>]", line)
        if m:
            c = m.start()
            hits.append(f"line {ln}: …{line[max(0, c - 12):c + 13].strip()}…")
            if len(hits) >= 5:
                break
    if hits:
        return "fail", "raw angle bracket(s) outside code — " + "; ".join(hits)
    return "pass", ""


def chk_md_table_blank_lines(target, anchor_root, args):
    """Markdown tables need blank lines before the header and after the table."""
    if not target.is_file():
        return "pass", "not a file"
    lines = _read(target).splitlines()
    issues = []
    i = 0
    while i < len(lines):
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
    """Every id under <defs> is referenced by url(#id) or a #-bearing attribute."""
    if not target.is_file() or target.suffix.lower() != ".svg":
        return "error", "not an SVG file"
    try:
        text = _read(target)
        root = _svg_root(target)
    except Exception as e:
        return "error", f"{type(e).__name__}: {e}"
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
    t = _read(f)
    if re.search(r"^#+\s*RULESET\s+R-", t, re.MULTILINE):
        return "pass", "embedded ruleset"
    if re.search(r"\[\[R-[^\]|]+", t):
        return "pass", "linked sibling ruleset"
    return "fail", "no embedded # RULESET R- and no linked [[R-...]] ruleset"


def chk_facet_h1_form(target, anchor_root, args):
    """R-facet-spec-02 (mechanical part): a catalog facet's H1 reads `# FCT <Name>`.
    The singular-vs-plural judgment is left to the agent."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    for line in _read(f).splitlines():
        if line.startswith("# "):
            return ("pass", "") if re.match(r"^#\s+FCT\s+\S", line) else ("fail", f"H1 is not `# FCT <Name>`: {line!r}")
    return "fail", "no H1"


def chk_facet_registered(target, anchor_root, args):
    """R-facet-spec-03: the facet is linked in the facet index — FCT.md (the current
    dispatch/registry) or FCT Facets.md (the dedicated index, currently mid-migration)."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    name = f.stem
    # dispatch tables use escaped pipes — `[[Name\|alias]]` — so allow an optional backslash
    pat = re.compile(r"\[\[" + re.escape(name) + r"\s*(\\?\||\]|/)")
    indices = [REPO_ROOT / "facets" / "FCT.md", *(REPO_ROOT / "facets").rglob("FCT Facets.md")]
    for idx in indices:
        if idx.is_file() and pat.search(_read(idx)):
            return "pass", "registered in index"
    return "fail", f"'{name}' not linked in FCT.md or FCT Facets.md"


def chk_facet_tldr_if_substantial(target, anchor_root, args):
    """R-facet-spec-07: a substantial facet spec carries a **TLDR**; small specs are exempt."""
    f = _as_file(target, anchor_root)
    if f is None:
        return "error", "no file"
    t = _read(f)
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
    for line in _read(f).splitlines():
        if re.match(r"^\|\s*Examples\s*\|", line):
            return ("pass", "examples row present") if "[[" in line else ("fail", "Examples row has no wiki-link")
    return "fail", "no Examples row in masthead"


CHECKERS = {
    "anchor_has": chk_anchor_has,
    "entry_page_matches_slug": chk_entry_page_matches_slug,
    "frontmatter_has": chk_frontmatter_has,
    "h1_present": chk_h1_present,
    "h1_matches_slug": chk_h1_matches_slug,
    "h1_after_frontmatter": chk_h1_after_frontmatter,
    "name_slug_prefixed": chk_name_slug_prefixed,
    "no_blank_after_h1": chk_no_blank_after_h1,
    "breadcrumb_row": chk_breadcrumb_row,
    "design_row_iff_folder": chk_design_row_iff_folder,
    "regex_present": chk_regex_present,
    "regex_absent": chk_regex_absent,
    # F161 batch-2 — shared header / field
    "header_has_field": chk_header_has_field,
    "description_field_line": chk_description_field_line,
    # R-facet-spec
    "facet_dispatch_top": chk_facet_dispatch_top,
    "triggers_section_iff_declared": chk_triggers_section_iff_declared,
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
    # R-testing
    "testing_filename_correct": chk_testing_filename_correct,
    "strategy_subsections_present_ordered": chk_strategy_subsections_present_ordered,
    "proposed_tests_structure": chk_proposed_tests_structure,
    "proposed_tests_subset_of_strategy": chk_proposed_tests_subset_of_strategy,
    "all_test_kinds_have_targets": chk_all_test_kinds_have_targets,
    "proposed_tests_rows_have_spec": chk_proposed_tests_rows_have_spec,
    "spec_cells_format_valid": chk_spec_cells_format_valid,
    "status_field_valid": chk_status_field_valid,
    # R-anchor-page (extras)
    "no_track_row_if_ecosystem_traits": chk_no_track_row_if_ecosystem_traits,
    "all_files_folders_prefixed_with_name": chk_all_files_folders_prefixed_with_name,
    # R-prd
    "file_path_matches_prd_locations": chk_file_path_matches_prd_locations,
    "h1_no_frontmatter": chk_h1_no_frontmatter,
    "required_sections_in_order": chk_required_sections_in_order,
    "user_stories_use_rid_numbering": chk_user_stories_use_rid_numbering,
    "no_legacy_open_questions_file": chk_no_legacy_open_questions_file,
    "design_workflow_modern_names": chk_design_workflow_modern_names,
    "dispatch_table_stories_row": chk_dispatch_table_stories_row,
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
    "log_dispatch_newest_first": chk_log_dispatch_newest_first,
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
    "md_angle_brackets_safe": chk_md_angle_brackets_safe,
    "md_angle_brackets_backtick_only": chk_md_angle_brackets_backtick_only,
    "md_table_blank_lines": chk_md_table_blank_lines,
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
    fn = CHECKERS.get(name)
    if fn is None:
        return "error", f"unknown checker {name!r}"
    try:
        return fn(target, anchor_root, args)
    except Exception as e:  # a checker bug must not abort the whole run
        return "error", f"{type(e).__name__}: {e}"


def _content_hash(tp: Path) -> str:
    """Content hash of a target — file bytes, or (for an anchor-dir target) its
    sorted child-name list (the structure a `anchor`-scope checker inspects)."""
    try:
        if tp.is_file():
            return hashlib.sha256(tp.read_bytes()).hexdigest()[:12]
        return hashlib.sha256(str(sorted(p.name for p in tp.iterdir())).encode()).hexdigest()[:12]
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


def execute_plan(plan: dict, cdir: Path | None) -> dict:
    """Run every matched rule that carries a `check::` ref; cache verdicts by
    (rule-id, rule-body-hash, target-content-hash). Returns a verdicts report."""
    anchor_root = Path(plan["anchor_root"])
    results = []
    counts = {"pass": 0, "fail": 0, "error": 0, "cached": 0}
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
                if cached:
                    status, detail = cached["status"], cached["detail"]
                    counts["cached"] += 1
                else:
                    status, detail = run_checker(r["check"], tp, anchor_root)
                    if cdir:
                        _verdict_cache_put(cdir, key, {"status": status, "detail": detail})
                counts[status] = counts.get(status, 0) + 1
                results.append({"rule": r["id"], "target": disp, "status": status, "detail": detail})
    return {"counts": counts, "results": results}


def render_verdicts(report: dict) -> str:
    c = report["counts"]
    out = [f"# mechanical verdicts — pass {c['pass']}  fail {c['fail']}  "
           f"error {c['error']}  (cache hits {c['cached']})", ""]
    for v in report["results"]:
        mark = {"pass": "✓", "fail": "✗", "error": "!"}.get(v["status"], "?")
        line = f"{mark} {v['rule']} — {v['target']}"
        if v["detail"]:
            line += f"  ({v['detail']})"
        out.append(line)
    return "\n".join(out)


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
    awareness-only (`tracked`). Mechanical = a `check::` naming a known checker."""
    if rule["tier"] == "tracked":
        return False
    chk = rule.get("check")
    if chk and chk.split()[0] in CHECKERS:
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
    out.append(f"- mechanical: **{c['pass']} pass · {c['fail']} fail · {c['error']} error** "
               f"(cache hits {c['cached']})")
    out.append(f"- to judge: **{man['task_count']}**  ·  judged-cached: {man['cached_count']}")
    out.append("")
    fails = [v for v in mech["results"] if v["status"] != "pass"]
    out.append("## mechanical failures" if fails else "## mechanical — all clean")
    for v in fails:
        mark = {"fail": "✗", "error": "!"}.get(v["status"], "?")
        out.append(f"- {mark} {v['rule']} — {v['target']}"
                   + (f"  ({v['detail']})" if v["detail"] else ""))
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
    ap.add_argument("--cache-dir")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    cdir = None if args.no_cache else cache_dir(args.cache_dir)

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
        anchors = sorted({p.parent for p in root.rglob(".anchor")})
        order = args.order or "rule"
        stats: dict = {}
        plans = []
        for a in anchors:
            plans.append(plan_one(a, "anchor", cdir, [], sub_anchor_roots(a), stats))
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
