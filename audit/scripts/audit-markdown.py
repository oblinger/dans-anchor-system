#!/usr/bin/env python3
"""audit-markdown.py — markdown hygiene rule runner (F081).

Loads "rules-as-markdown" from two locations:
  1. Bundled (read-only):    skills/audit/rules-markdown/*.md
  2. User-space (overrides): ~/.config/ob-skills/audit-markdown/rules/*.md

Each rule file is a markdown doc with YAML frontmatter + a single fenced
```python ... ``` block defining a `check(file_path: Path) -> list[dict]`
function. The "compile step" extracts and exec's the code block.

Usage:
  audit-markdown.py <file.md> [<file2.md> ...]
        Check the named files.
  audit-markdown.py --all [<dir>]
        Scan all *.md under <dir> (default: vault_root from F080 config).
  audit-markdown.py --list-rules
        Print loaded rules + which file each came from.

Exit code: 0 if no findings, 1 if any errors, 2 on usage error.

Design: F081 — audit markdown — markdown hygiene via MCP server (v1 minimal
per F081 Q1=no MCP, Q3=Stop-hook only, Q6=bundled + user-space split).
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
import argparse
import re
import sys

# ============================================================
# Configuration — vault root from F080
# ============================================================


def _resolve_vault_root() -> Path:
    """Read vault_root from F080 config; fall back to ~/ob/kmr."""
    config_path = Path.home() / ".config" / "ob-skills" / "global.yaml"
    if config_path.is_file():
        try:
            import yaml
            with config_path.open() as f:
                data = yaml.safe_load(f) or {}
            raw = data.get("vault_root")
            if raw:
                return Path(str(raw).replace("~", str(Path.home())))
        except (ImportError, Exception):
            pass
    return Path.home() / "ob" / "kmr"


VAULT_ROOT = _resolve_vault_root()

# Rule directories (bundled + user-space).
SCRIPT_DIR = Path(__file__).resolve().parent
BUNDLED_RULES_DIR = SCRIPT_DIR.parent / "rules-markdown"
USER_RULES_DIR = Path.home() / ".config" / "ob-skills" / "audit-markdown" / "rules"

# Exclude paths from --all scan.
EXCLUDED_PATH_FRAGMENTS = (
    ".trash", "Closet", "Yore", "worktrees", ".claude",
    "node_modules", ".git", "target",
)


# ============================================================
# Rule loading — "compile" step extracts ```python``` from each .md rule
# ============================================================


@dataclass
class Rule:
    name: str
    severity: str       # 'error' or 'warning'
    source_file: Path   # the .md rule file
    check: Callable[[Path], list[dict]]


PYTHON_BLOCK_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from a rule .md file. Returns {} if none."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        import yaml
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def _load_rule_from_md(md_path: Path) -> Optional[Rule]:
    """Compile a single rule .md file into a Rule object."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm = _parse_frontmatter(text)
    name = fm.get("name", md_path.stem)
    severity = fm.get("severity", "warning")
    m = PYTHON_BLOCK_RE.search(text)
    if not m:
        print(
            f"audit-markdown: rule {md_path.name} has no ```python``` block; "
            f"skipping",
            file=sys.stderr,
        )
        return None
    code = m.group(1)
    namespace: dict = {"Path": Path, "re": re, "sys": sys}
    try:
        exec(code, namespace)
    except Exception as e:
        print(
            f"audit-markdown: rule {md_path.name} failed to compile: {e}",
            file=sys.stderr,
        )
        return None
    check_fn = namespace.get("check")
    if not callable(check_fn):
        print(
            f"audit-markdown: rule {md_path.name} has no callable `check`; "
            f"skipping",
            file=sys.stderr,
        )
        return None
    # exec'd code; type-checker can't see the signature. Wrap to assert shape.
    typed_check: Callable[[Path], list[dict]] = check_fn  # type: ignore[assignment]
    return Rule(
        name=name,
        severity=severity,
        source_file=md_path,
        check=typed_check,
    )


def load_rules() -> list[Rule]:
    """Load bundled rules first, then user-space rules. User-space overrides
    bundled when names collide (later loads take precedence)."""
    rules: dict[str, Rule] = {}
    for src_dir in (BUNDLED_RULES_DIR, USER_RULES_DIR):
        if not src_dir.is_dir():
            continue
        for rule_md in sorted(src_dir.glob("*.md")):
            rule = _load_rule_from_md(rule_md)
            if rule is not None:
                rules[rule.name] = rule  # user-space override wins
    return list(rules.values())


# ============================================================
# Runner
# ============================================================


@dataclass
class Finding:
    file: Path
    line: int
    rule: str
    severity: str
    message: str


def run_rules_on_file(file_path: Path, rules: list[Rule]) -> list[Finding]:
    """Run every rule against a single file. Returns list of Findings."""
    findings: list[Finding] = []
    for rule in rules:
        try:
            raw_results = rule.check(file_path)
        except Exception as e:
            print(
                f"audit-markdown: rule '{rule.name}' raised on "
                f"{file_path}: {e}",
                file=sys.stderr,
            )
            continue
        for raw in raw_results or []:
            findings.append(Finding(
                file=file_path,
                line=int(raw.get("line", 0)),
                rule=rule.name,
                severity=raw.get("severity", rule.severity),
                message=str(raw.get("message", "")),
            ))
    return findings


def discover_files(root: Path) -> list[Path]:
    """Walk root for .md files, respecting exclusions."""
    out: list[Path] = []
    for path in root.rglob("*.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="markdown files to check; empty = error unless --all",
    )
    parser.add_argument(
        "--all",
        nargs="?",
        const=VAULT_ROOT,
        type=Path,
        help=f"scan all *.md under <dir> (default {VAULT_ROOT})",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="list loaded rules and exit",
    )
    args = parser.parse_args()

    rules = load_rules()

    if args.list_rules:
        print(f"audit-markdown: {len(rules)} rules loaded", file=sys.stderr)
        for r in rules:
            rel = r.source_file.relative_to(Path.home()) if str(r.source_file).startswith(str(Path.home())) else r.source_file
            print(f"  {r.name:30s} [{r.severity:8s}]  ~/{rel}")
        return 0

    if not rules:
        print(
            f"audit-markdown: no rules loaded (looked in {BUNDLED_RULES_DIR} "
            f"and {USER_RULES_DIR})",
            file=sys.stderr,
        )
        return 2

    if args.all is not None:
        targets = discover_files(args.all)
    elif args.files:
        targets = []
        for p in args.files:
            if not p.is_file():
                print(f"audit-markdown: not a file (skipped): {p}", file=sys.stderr)
                continue
            if p.suffix != ".md":
                print(f"audit-markdown: not .md (skipped): {p}", file=sys.stderr)
                continue
            targets.append(p)
    else:
        print("audit-markdown: provide file paths or --all", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for f in targets:
        findings.extend(run_rules_on_file(f, rules))

    # Report
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print(
        f"\naudit-markdown: scanned {len(targets)} files; "
        f"{len(findings)} findings ({len(errors)} errors, "
        f"{len(warnings)} warnings) from {len(rules)} rules",
        file=sys.stderr,
    )
    for f in findings:
        rel = f.file.relative_to(VAULT_ROOT) if VAULT_ROOT in f.file.parents else f.file
        print(f"  [{f.severity}] {f.rule} {rel}:{f.line} — {f.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
