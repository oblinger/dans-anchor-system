#!/usr/bin/env python3
"""audit-plan — the resolver/planner for the rule-driven audit engine (F161).

Stage 1 (RESOLVE) of the Resolve → Run → Judge pipeline:

  1. Flatten an umbrella rule set (R-anchor / R-doc) by resolving its include:: DAG
     down to the leaf `# RULESET` blocks (standalone stubs OR embedded in facet /
     discipline / skill specs).
  2. Glob/sentinel-match each rule's `where::` selector against the target set
     (an anchor tree, or a single document) to build the (rule × target) match set.
     A selector that matches nothing => the rule is N/A (skipped, never failed).
  3. Materialize each leaf rule set as a cached flat rule file (hashed → reused).
  4. Emit a query-plan recipe: per leaf rule set, the cached flat file + each rule's
     tier + the targets it matched. The agent then follows the recipe — read a flat
     rule file, judge its listed targets — with no rule-selection thinking.

Deferred to later F161 slices (announced, not silently dropped):
  - Stage 2 mechanical execution of `checked` rules (needs machine-readable checker
    refs on each rule). For now `checked` rules are emitted flagged
    `(mechanical — checker pending)` and routed to the agent like `stated` rules.
  - The verdict cache (rule-id, rule-body-hash, target-hash, model-id) and the
    anchor-manifest cache. Only the flattened-rules cache is built here.

Usage:
  audit-plan <path-or-slug> [--mode anchor|doc] [--order file|rule]
                            [--json] [--cache-dir DIR] [--no-cache]
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
    # Prefer a hit under facets/ or the Rule Sets catalog when ambiguous.
    hits = sorted(hits, key=lambda p: (("facets" not in p.parts), len(p.parts)))
    return hits[0]


# ── rule-set parsing ────────────────────────────────────────────────────────

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
    """Resolve a link target to leaf rule sets (those with RULE entries),
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
        # embedded `# RULESET <filepart>` block (covers stub-less rule sets like
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
    """Flatten an umbrella (R-anchor / R-doc / any ruleset link) to leaf rule sets,
    de-duplicated by ruleset name (first occurrence wins)."""
    leaves = load_ruleset(umbrella, set(), warnings)
    seen, out = set(), []
    for rs in leaves:
        if rs["name"] in seen:
            continue
        seen.add(rs["name"])
        out.append(rs)
    return out


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


def match_targets(kind: str, arg: str, scope_files: list[Path], anchor_root: Path) -> list[Path]:
    if kind == "always":
        return list(scope_files)
    if kind == "anchor":
        return [anchor_root]  # synthetic: one structural check per anchor
    if kind == "file":
        rel = _glob_to_relpattern(arg)
        if not rel:
            return [anchor_root]
        try:
            hits = {p.resolve() for p in anchor_root.glob(rel)}
        except (ValueError, IndexError):
            hits = set()
        return [p for p in scope_files if p.resolve() in hits]
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

def enumerate_scope(target: Path, mode: str) -> tuple[Path, list[Path]]:
    """Return (anchor_root, scope_files). For doc mode the scope is the one file."""
    if mode == "doc":
        return target.parent, [target]
    files = [p for p in target.rglob("*.md") if "/.git/" not in str(p)]
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

def plan_one(target: Path, mode: str, cdir: Path | None, warnings: list[str]) -> dict:
    umbrella = "R-doc" if mode == "doc" else "R-anchor"
    rulesets = flatten_umbrella(umbrella, warnings)
    anchor_root, scope_files = enumerate_scope(target, mode)

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
                "targets": [str(p.relative_to(anchor_root)) if p != anchor_root else "{ANCHOR}"
                            for p in tgts],
                "_target_paths": [str(p) for p in tgts],
            })
        if matched_rules:
            groupings.append({"ruleset": rs["name"], "flat_file": flat,
                              "source": rs["source"], "rules": matched_rules})

    return {
        "umbrella": umbrella, "mode": mode,
        "target": str(target), "anchor_root": str(anchor_root),
        "scope_file_count": len(scope_files),
        "groupings": groupings, "warnings": warnings,
    }


# ── rendering ───────────────────────────────────────────────────────────────

def render_recipe(plan: dict, order: str, cdir: Path | None) -> str:
    out = []
    out.append(f"# audit-plan recipe — {plan['umbrella']} on {Path(plan['target']).name}")
    out.append("")
    out.append(f"- mode: **{plan['mode']}**  ·  order: **{order}-major**  ·  "
               f"scope files: {plan['scope_file_count']}  ·  "
               f"rule sets matched: {len(plan['groupings'])}")
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


CHECKERS = {
    "anchor_has": chk_anchor_has,
    "entry_page_matches_slug": chk_entry_page_matches_slug,
    "frontmatter_has": chk_frontmatter_has,
    "h1_present": chk_h1_present,
    "no_blank_after_h1": chk_no_blank_after_h1,
    "regex_present": chk_regex_present,
    "regex_absent": chk_regex_absent,
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
                try:
                    chash = hashlib.sha256(tp.read_bytes() if tp.is_file()
                                           else str(sorted(p.name for p in tp.iterdir())).encode()
                                           ).hexdigest()[:12]
                except OSError:
                    chash = "0"
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
    ap.add_argument("--cache-dir")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args(argv)

    cdir = None if args.no_cache else cache_dir(args.cache_dir)

    if args.batch:
        root = Path(args.batch).expanduser().resolve()
        anchors = sorted({p.parent for p in root.rglob(".anchor")})
        order = args.order or "rule"
        plans = []
        for a in anchors:
            plans.append(plan_one(a, "anchor", cdir, []))
        if args.json:
            print(json.dumps({"batch": str(root), "plans": plans}, indent=2))
        else:
            for pl in plans:
                print(render_recipe(pl, order, cdir))
                print("\n" + "=" * 72 + "\n")
        return 0

    if not args.target:
        ap.error("target required (or use --batch)")
    target = resolve_target(args.target)
    mode = args.mode or ("doc" if target.is_file() else "anchor")
    order = args.order or ("rule" if mode == "anchor" and False else "file")
    plan = plan_one(target, mode, cdir, [])
    if args.run:
        report = execute_plan(plan, cdir)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(render_verdicts(report))
        return 0
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(render_recipe(plan, order, cdir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
