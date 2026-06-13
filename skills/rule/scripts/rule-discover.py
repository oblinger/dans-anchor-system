#!/usr/bin/env python3
"""rule-discover — walk the vault, find every rule across every anchor, group by trait and similarity.

Phase 1 of F082 (Common ruleset across projects).

Usage:
    rule-discover [--vault PATH] [--report PATH] [--threshold FLOAT]

  --vault PATH       Root to scan. Defaults to ob-skills config vault_root,
                     then ~/ob/kmr (see SKA System Design § Per-user parameters).
  --report PATH      Where to write the markdown report.
                     Defaults to ~/.config/ob-skills/rule/discovery-report.md.
  --threshold FLOAT  Jaccard similarity for clustering (0-1). Default 0.5.

The report's structure:

  # Rule Discovery Report — YYYY-MM-DD HH:MM

  ## By Trait

  ### Code

  #### Cluster: <representative-rule-name>     ← rules clustered by similarity within the trait
  - **<anchor>** R07 — Sensors and Effectors Must Be Logic-Free
    > RULE: ...
  - **<anchor>** R12 — Sensor methods are logic-free
    > RULE: ...

  #### Cluster: <representative-rule-name>
  - ...

  ### Skill
  ...

  ## Singletons (no cluster)

  - <anchor> R<NN> ... (only one rule of its kind found)

  ## Anchors without rules (sampled)
  ...

The agent reads this report and (via /rule curate) walks the user through
naming + adopting rulesets per trait, writing them to ~/.claude/skills/rule/sets/<trait>/<name>.md.
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# --- config -----------------------------------------------------------------

def vault_root_default() -> Path:
    """Resolve vault_root via ob-skills config, falling back to ~/ob/kmr."""
    try:
        import subprocess
        r = subprocess.run(
            ["ob-skills", "config", "vault_root", "--default", str(Path.home() / "ob" / "kmr")],
            capture_output=True, text=True, timeout=2,
        )
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).expanduser()
    except Exception:
        pass
    return Path.home() / "ob" / "kmr"


def report_path_default() -> Path:
    return Path.home() / ".config" / "ob-skills" / "rule" / "discovery-report.md"


# --- anchor + trait detection ----------------------------------------------

ANCHOR_FILE = ".anchor"
SKIP_PATH_FRAGMENTS = (
    "/.history/", "/Yore/", "/.git/", "/node_modules/", "/__pycache__/",
    "/.claude/worktrees/", "/.trash/", "/Closet/",
)
TRAITS_RE = re.compile(r"^traits\s*:\s*\[([^\]]*)\]\s*$", re.MULTILINE)
CAB_TYPE_RE = re.compile(r"^cab-type\s*:\s*(\S+)\s*$", re.MULTILINE)


def is_skipped(p: Path) -> bool:
    s = str(p)
    return any(frag in s for frag in SKIP_PATH_FRAGMENTS)


def find_anchors(root: Path) -> list[Path]:
    out: list[Path] = []
    for dp, dns, fns in os.walk(root):
        if is_skipped(Path(dp)):
            dns[:] = []  # prune
            continue
        if ANCHOR_FILE in fns:
            out.append(Path(dp))
    return out


def anchor_traits(anchor_dir: Path) -> list[str]:
    """Read .anchor and infer traits.
    Prefers F090's `traits: [...]` schema; falls back to `cab-type: <X>` capitalized.
    Returns [] if nothing found (unknown-trait bucket)."""
    af = anchor_dir / ANCHOR_FILE
    if not af.is_file():
        return []
    try:
        text = af.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    m = TRAITS_RE.search(text)
    if m:
        return [t.strip() for t in m.group(1).split(",") if t.strip()]
    m = CAB_TYPE_RE.search(text)
    if m:
        return [m.group(1).strip().capitalize()]
    return []


# --- rule extraction --------------------------------------------------------

RULE_HEADING_RE = re.compile(r"^###\s+(R[-A-Za-z0-9]+)\s+—\s+(.+?)\s*$", re.MULTILINE)
RULE_DECL_RE = re.compile(r"^RULE:\s+(.+?)\s*$", re.MULTILINE)


def find_rule_files(anchor_dir: Path, sub_anchors: list[Path]) -> list[Path]:
    """Rules can live in:
       - <anchor>/rules/ folder (any *.md inside)
       - <anchor>/**/*Rules.md (one or more Rules files anywhere under the anchor)
    Only scan within anchor_dir; DO NOT recurse into sub_anchors (they own those rules).
    Respect skip-fragments."""
    sub_anchor_set = {p.resolve() for p in sub_anchors}

    out: list[Path] = []
    for dp, dns, fns in os.walk(anchor_dir):
        dp_path = Path(dp)
        if is_skipped(dp_path):
            dns[:] = []
            continue
        # Prune sub-anchor subtrees (they handle their own rules)
        dns_keep = []
        for d in dns:
            sub = (dp_path / d).resolve()
            if sub in sub_anchor_set:
                continue
            dns_keep.append(d)
        dns[:] = dns_keep
        # Pick up rule files in this directory
        for fn in fns:
            p = dp_path / fn
            if is_skipped(p):
                continue
            # rules/*.md (any depth under a "rules" folder we encountered)
            if "rules" in p.parts[len(anchor_dir.parts):] and p.suffix == ".md":
                out.append(p)
            elif fn.endswith("Rules.md"):
                out.append(p)
    return out


def parse_rules(md: str) -> list[tuple[str, str, str]]:
    """Return [(rule_id, rule_name, rule_decl), ...] from a markdown rules doc."""
    out: list[tuple[str, str, str]] = []
    headings = list(RULE_HEADING_RE.finditer(md))
    for i, h in enumerate(headings):
        start = h.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(md)
        body = md[start:end]
        decl_match = RULE_DECL_RE.search(body)
        decl = decl_match.group(1) if decl_match else ""
        out.append((h.group(1), h.group(2).strip(), decl.strip()))
    return out


# --- clustering by Jaccard similarity --------------------------------------

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")
STOPWORDS = {
    "the", "and", "or", "of", "to", "in", "a", "an", "is", "are", "must",
    "not", "be", "for", "with", "on", "by", "as", "this", "that",
}


def tokens(text: str) -> set[str]:
    return {w.lower() for w in WORD_RE.findall(text) if len(w) >= 3 and w.lower() not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_rules(rules: list[dict], threshold: float) -> list[list[dict]]:
    """Greedy clustering — each rule joins the first cluster whose representative is >= threshold similar."""
    clusters: list[list[dict]] = []
    for r in rules:
        joined = False
        for c in clusters:
            if jaccard(r["tokens"], c[0]["tokens"]) >= threshold:
                c.append(r)
                joined = True
                break
        if not joined:
            clusters.append([r])
    return clusters


# --- report -----------------------------------------------------------------

def render_report(by_trait: dict[str, list[list[dict]]],
                  anchors_without_rules: list[Path],
                  unknown_trait_rules: list[dict],
                  vault: Path,
                  threshold: float) -> str:
    lines: list[str] = []
    lines.append(f"# Rule Discovery Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"_Vault: `{vault}` · Similarity threshold: {threshold:.2f}_")
    lines.append("")

    total_rules = sum(len(c) for clusters in by_trait.values() for c in clusters) + len(unknown_trait_rules)
    total_anchors_with_rules = len(
        {r["anchor"] for clusters in by_trait.values() for c in clusters for r in c}
        | {r["anchor"] for r in unknown_trait_rules}
    )
    multi_rule_clusters = sum(1 for clusters in by_trait.values() for c in clusters if len(c) > 1)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Anchors with rules:** {total_anchors_with_rules}")
    lines.append(f"- **Anchors without rules:** {len(anchors_without_rules)}")
    lines.append(f"- **Total rules parsed:** {total_rules}")
    lines.append(f"- **Multi-rule clusters (candidate common rules):** {multi_rule_clusters}")
    lines.append(f"- **Unknown-trait rules (no `traits:` / `cab-type:` in `.anchor`):** {len(unknown_trait_rules)}")
    lines.append("")

    lines.append("## By Trait")
    lines.append("")
    for trait in sorted(by_trait.keys()):
        clusters = by_trait[trait]
        lines.append(f"### {trait}")
        lines.append("")
        clusters_sorted = sorted(clusters, key=lambda c: (-len(c), c[0]["name"]))
        for i, cluster in enumerate(clusters_sorted, 1):
            if len(cluster) > 1:
                lines.append(f"#### Cluster {i} — {cluster[0]['name']}")
            else:
                lines.append(f"#### Singleton {i} — {cluster[0]['name']}")
            lines.append("")
            for r in cluster:
                lines.append(f"- **{r['anchor']}** {r['id']} — {r['name']}")
                if r["decl"]:
                    lines.append(f"  > RULE: {r['decl']}")
            lines.append("")

    if unknown_trait_rules:
        lines.append("## Unknown-trait rules")
        lines.append("")
        lines.append("Rules from anchors that don't declare a trait. (Add `traits: [...]` to the anchor's `.anchor` file, or set `cab-type:`, to bucket these correctly on the next sweep.)")
        lines.append("")
        for r in unknown_trait_rules:
            lines.append(f"- **{r['anchor']}** {r['id']} — {r['name']}")
        lines.append("")

    if anchors_without_rules:
        lines.append("## Anchors without rules (sampled)")
        lines.append("")
        for a in anchors_without_rules[:25]:
            lines.append(f"- {a}")
        if len(anchors_without_rules) > 25:
            lines.append(f"- _… and {len(anchors_without_rules) - 25} more_")
        lines.append("")

    return "\n".join(lines)


# --- main -------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="rule-discover — Phase 1 of F082")
    parser.add_argument("--vault", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    vault = (args.vault or vault_root_default()).expanduser().resolve()
    report = (args.report or report_path_default()).expanduser().resolve()

    if not vault.is_dir():
        print(f"rule-discover: vault not found: {vault}", file=sys.stderr)
        return 2

    anchors = find_anchors(vault)
    print(f"rule-discover: scanning {len(anchors)} anchors under {vault}", file=sys.stderr)

    # For each anchor, the sub-anchors are anchors whose path is strictly inside it.
    anchors_resolved = [(a, a.resolve()) for a in anchors]

    def sub_anchors_of(parent: Path) -> list[Path]:
        rp = parent.resolve()
        out = []
        for a, ar in anchors_resolved:
            if ar == rp:
                continue
            try:
                ar.relative_to(rp)
                out.append(a)
            except ValueError:
                continue
        return out

    by_trait: dict[str, list[dict]] = defaultdict(list)
    unknown_trait_rules: list[dict] = []
    anchors_without_rules: list[Path] = []

    for anchor in anchors:
        rule_files = find_rule_files(anchor, sub_anchors_of(anchor))
        if not rule_files:
            anchors_without_rules.append(anchor.relative_to(vault) if anchor.is_relative_to(vault) else anchor)
            continue

        traits = anchor_traits(anchor)
        anchor_rel = str(anchor.relative_to(vault)) if anchor.is_relative_to(vault) else str(anchor)

        for rf in rule_files:
            try:
                text = rf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for rid, rname, rdecl in parse_rules(text):
                tok = tokens(f"{rname} {rdecl}")
                if not tok:
                    continue
                rule = {
                    "anchor": anchor_rel,
                    "file": str(rf.relative_to(anchor)),
                    "id": rid,
                    "name": rname,
                    "decl": rdecl,
                    "tokens": tok,
                }
                if traits:
                    for t in traits:
                        by_trait[t].append(rule)
                else:
                    unknown_trait_rules.append(rule)

    clustered_by_trait: dict[str, list[list[dict]]] = {}
    for trait, rules in by_trait.items():
        clustered_by_trait[trait] = cluster_rules(rules, args.threshold)

    out_text = render_report(clustered_by_trait, anchors_without_rules, unknown_trait_rules, vault, args.threshold)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(out_text, encoding="utf-8")
    print(f"rule-discover: wrote {report}", file=sys.stderr)

    n_clusters = sum(len(c) for c in clustered_by_trait.values())
    print(f"rule-discover: {sum(len(rs) for rs in by_trait.values()) + len(unknown_trait_rules)} rules across {len(clustered_by_trait)} trait(s) in {n_clusters} clusters", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
