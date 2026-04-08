#!/usr/bin/env python3
"""audit-docs — Compare source tree against documentation (Files.md, Dev dispatch, module docs).

Usage:
    audit-docs <anchor-path> [--json] [--verbose]

Reads:
    - Source tree from code path (via .anchor/config.yaml or .git/)
    - {NAME} Files.md
    - {NAME} Dev.md (Dev dispatch)
    - Module docs in {NAME} Dev/
    - Exceptions from .anchor/audit-docs.yaml

Outputs a diff table showing:
    - Source files missing from Files.md
    - Files.md entries pointing to nonexistent files
    - Source files missing module docs
    - Module docs not linked from Dev dispatch
    - Stale module docs (source newer than doc)
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# ── Data Model ────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = {
    ".rs", ".py", ".ts", ".tsx", ".js", ".jsx",
    ".swift", ".kt", ".java", ".go", ".c", ".cpp", ".h",
}

# Default exclusions — files that rarely need module docs
DEFAULT_EXCLUDES = [
    "**/mod.rs",
    "**/prelude.rs",
    "**/test_helpers.*",
    "**/tests/**",
    "**/*.test.*",
    "**/*.spec.*",
    "**/build.rs",
    "**/__init__.py",
    "**/conftest.py",
]


@dataclass
class Finding:
    number: int
    file: str
    status: str  # missing-doc, missing-entry, stale, unlinked, stale-entry, missing-folder-doc
    issue: str
    staleness: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_anchor_root(path: str) -> str:
    """Walk up to find .anchor/config.yaml."""
    p = os.path.abspath(path)
    while p != "/":
        if os.path.exists(os.path.join(p, ".anchor", "config.yaml")):
            return p
        p = os.path.dirname(p)
    return os.path.abspath(path)


def load_config(anchor_root: str) -> dict:
    cfg_path = os.path.join(anchor_root, ".anchor", "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_exceptions(anchor_root: str) -> list[str]:
    """Load exclusion patterns from .anchor/audit-docs.yaml."""
    exc_path = os.path.join(anchor_root, ".anchor", "audit-docs.yaml")
    if os.path.exists(exc_path):
        with open(exc_path) as f:
            data = yaml.safe_load(f) or {}
        return data.get("exclude", [])
    return []


def is_excluded(rel_path: str, excludes: list[str]) -> bool:
    for pattern in excludes:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def git_mtime(filepath: str) -> Optional[int]:
    """Get last commit timestamp for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", filepath],
            capture_output=True, text=True, cwd=os.path.dirname(filepath),
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return None


def file_mtime(filepath: str) -> Optional[int]:
    """Get file modification time."""
    try:
        return int(os.path.getmtime(filepath))
    except OSError:
        return None


# ── Source Tree ───────────────────────────────────────────────────────────────

def scan_source_tree(code_path: str, excludes: list[str]) -> dict[str, str]:
    """Return {relative_path: absolute_path} for all source files."""
    sources = {}
    for root, dirs, files in os.walk(code_path):
        # Skip hidden dirs, build dirs, node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in ("target", "build", "node_modules", ".build",
                                 "dist", "__pycache__", "vendor")]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in SOURCE_EXTENSIONS:
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, code_path)
                if not is_excluded(rel_path, excludes):
                    sources[rel_path] = abs_path
    return sources


def scan_source_dirs(code_path: str, sources: dict[str, str]) -> set[str]:
    """Return set of directories that contain source files."""
    dirs = set()
    for rel_path in sources:
        d = os.path.dirname(rel_path)
        if d:
            dirs.add(d)
    return dirs


# ── Files.md Parser ───────────────────────────────────────────────────────────

def parse_files_md(files_md_path: str) -> set[str]:
    """Extract file paths mentioned in Files.md tree.

    Looks for lines with filenames (extensions) in the box-drawing tree.
    Returns set of relative paths.
    """
    if not os.path.exists(files_md_path):
        return set()

    entries = set()
    with open(files_md_path) as f:
        content = f.read()

    # Track current directory from tree structure
    dir_stack = []
    indent_stack = []

    for line in content.split("\n"):
        # Strip box-drawing prefixes to get the content
        stripped = line.lstrip()
        if not stripped:
            continue

        # Remove box-drawing characters
        clean = re.sub(r"[│├└─┌┐┘┤┬┴┼\s]*", "", stripped, count=1)
        clean = stripped
        for ch in "│├└─┌┐┘┤┬┴┼":
            clean = clean.replace(ch, "")
        clean = clean.strip()

        if not clean:
            continue

        # Measure indent (count of box-drawing prefix chars)
        indent = 0
        for ch in stripped:
            if ch in "│├└─ ┌┐┘┤┬┴┼":
                indent += 1
            else:
                break

        # Extract filename — look for something with an extension or ending with /
        # Handle wiki-links: [[Name|filename.ext]] or [[Name]]
        # Also handle plain filenames
        filename_match = re.search(r"(\S+\.\w+)", clean)
        dir_match = re.search(r"(\S+)/", clean)

        if dir_match and not filename_match:
            # This is a directory line
            dirname = dir_match.group(1)
            # Remove wiki-link syntax
            dirname = re.sub(r"\[\[[^\]]*\|([^\]]*)\]\]", r"\1", dirname)
            dirname = re.sub(r"\[\[([^\]]*)\]\]", r"\1", dirname)

            # Adjust dir_stack based on indent
            while indent_stack and indent <= indent_stack[-1]:
                dir_stack.pop()
                indent_stack.pop()
            dir_stack.append(dirname)
            indent_stack.append(indent)

        elif filename_match:
            fname = filename_match.group(1)
            # Remove wiki-link syntax
            fname = re.sub(r"\[\[[^\]]*\|([^\]]*)\]\]", r"\1", fname)
            fname = re.sub(r"\[\[([^\]]*)\]\]", r"\1", fname)

            # Build full path
            # Adjust dir_stack based on indent
            while indent_stack and indent <= indent_stack[-1]:
                dir_stack.pop()
                indent_stack.pop()

            if dir_stack:
                full_path = "/".join(dir_stack) + "/" + fname
            else:
                full_path = fname

            _, ext = os.path.splitext(fname)
            if ext in SOURCE_EXTENSIONS:
                entries.add(full_path)

    return entries


# ── Dev Dispatch Parser ───────────────────────────────────────────────────────

def parse_dev_dispatch(dev_md_path: str) -> set[str]:
    """Extract wiki-links from Dev dispatch table. Returns set of linked doc names."""
    if not os.path.exists(dev_md_path):
        return set()

    links = set()
    with open(dev_md_path) as f:
        for line in f:
            # Find wiki-links: [[Name|Alias]] or [[Name]]
            for match in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", line):
                links.add(match.group(1))
    return links


# ── Module Doc Scanner ────────────────────────────────────────────────────────

def scan_module_docs(dev_folder: str, name: str) -> dict[str, str]:
    """Return {doc_name: absolute_path} for all module docs in Dev folder."""
    docs = {}
    if not os.path.isdir(dev_folder):
        return docs

    for root, dirs, files in os.walk(dev_folder):
        for f in files:
            if f.endswith(".md") and f.startswith(name + " "):
                doc_name = f.replace(".md", "")
                docs[doc_name] = os.path.join(root, f)
    return docs


# ── Main Audit ────────────────────────────────────────────────────────────────

def audit(anchor_path: str, verbose: bool = False) -> list[Finding]:
    anchor_root = find_anchor_root(anchor_path)
    cfg = load_config(anchor_root)

    rid = cfg.get("rid", os.path.basename(anchor_root))
    traits = cfg.get("traits", ["code"])
    if isinstance(traits, str):
        traits = [traits]

    if "code" not in traits:
        print(f"Skipping — anchor traits {traits} don't include 'code'", file=sys.stderr)
        return []

    # Find code path
    code_rel = cfg.get("code", "Code")
    code_path = os.path.join(anchor_root, code_rel)
    if os.path.islink(code_path):
        code_path = os.path.realpath(code_path)
    if not os.path.isdir(code_path):
        # Maybe inline mode — check for .git
        if os.path.isdir(os.path.join(anchor_root, ".git")):
            code_path = anchor_root
        else:
            print(f"Error: Cannot find code at {code_path}", file=sys.stderr)
            return []

    # Load exceptions
    user_excludes = load_exceptions(anchor_root)
    excludes = DEFAULT_EXCLUDES + user_excludes

    if verbose:
        print(f"Anchor: {rid} at {anchor_root}", file=sys.stderr)
        print(f"Code: {code_path}", file=sys.stderr)
        print(f"Excludes: {len(excludes)} patterns", file=sys.stderr)

    # Scan source tree
    sources = scan_source_tree(code_path, excludes)
    source_dirs = scan_source_dirs(code_path, sources)

    # Find doc paths
    docs_folder = os.path.join(anchor_root, f"{rid} Docs")
    dev_folder = os.path.join(docs_folder, f"{rid} Dev")
    files_md = None
    # Search for Files.md in Dev or Plan
    for candidate in [
        os.path.join(dev_folder, f"{rid} Files.md"),
        os.path.join(docs_folder, f"{rid} Plan", f"{rid} Files.md"),
    ]:
        if os.path.exists(candidate):
            files_md = candidate
            break

    dev_dispatch = os.path.join(dev_folder, f"{rid} Dev.md")

    if verbose:
        print(f"Source files: {len(sources)}", file=sys.stderr)
        print(f"Source dirs: {len(source_dirs)}", file=sys.stderr)
        print(f"Files.md: {files_md or 'NOT FOUND'}", file=sys.stderr)
        print(f"Dev dispatch: {dev_dispatch}", file=sys.stderr)

    # Parse existing docs
    files_md_entries = parse_files_md(files_md) if files_md else set()
    dev_links = parse_dev_dispatch(dev_dispatch)
    module_docs = scan_module_docs(dev_folder, rid)

    findings = []
    n = 0

    # ── Normalize Files.md paths ──
    # Files.md tree often starts with the repo folder name (e.g., HookAnchorApp/)
    # but source scan is relative to repo root. Strip the first component if it
    # matches the repo folder name.
    repo_folder = os.path.basename(code_path)
    normalized_files_md = set()
    for entry in files_md_entries:
        # Strip repo folder prefix and any wiki-link pipe artifacts
        clean = entry.split("|")[-1] if "|" in entry else entry
        if clean.startswith(repo_folder + "/"):
            clean = clean[len(repo_folder) + 1:]
        normalized_files_md.add(clean)

    # ── Compare source → Files.md ──
    for rel_path in sorted(sources.keys()):
        if rel_path not in normalized_files_md:
            basename = os.path.basename(rel_path)
            if not any(basename == os.path.basename(e) for e in normalized_files_md):
                n += 1
                findings.append(Finding(n, rel_path, "missing-entry",
                                        f"Source file not in Files.md"))

    # ── Compare Files.md → source ──
    # Scan ALL files in repo (not just non-excluded sources) so we don't flag
    # excluded files (tests, bin/, etc.) as stale entries in Files.md.
    all_repo_files = set()
    for root, dirs, files in os.walk(code_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in ("target", "build", "node_modules", ".build",
                                 "dist", "__pycache__", "vendor")]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), code_path)
            all_repo_files.add(rel)

    for entry in sorted(normalized_files_md):
        if entry not in all_repo_files:
            basename = os.path.basename(entry)
            if not any(os.path.basename(f) == basename for f in all_repo_files):
                n += 1
                findings.append(Finding(n, entry, "stale-entry",
                                        f"Files.md entry — file does not exist in repo"))

    # ── Compare source → module docs ──
    def snake_to_pascal(snake: str) -> str:
        """Convert snake_case to PascalCase: command_ops → CommandOps."""
        return "".join(word.capitalize() for word in snake.split("_"))

    for rel_path in sorted(sources.keys()):
        basename = os.path.basename(rel_path)
        stem = os.path.splitext(basename)[0]
        expected_doc = f"{rid} {snake_to_pascal(stem)}"
        # Strict match — doc name must be exactly {RID} {PascalCase}
        found_doc = expected_doc in module_docs
        if found_doc:
            # Check freshness
            source_mtime = file_mtime(sources[rel_path]) or git_mtime(sources[rel_path])
            doc_mtime = file_mtime(module_docs[expected_doc]) or git_mtime(module_docs[expected_doc])
            if source_mtime and doc_mtime and source_mtime > doc_mtime:
                diff = source_mtime - doc_mtime
                if diff > 3600:
                    hours = diff // 3600
                    days = hours // 24
                    staleness = f"{days}d" if days > 0 else f"{hours}h"
                    n += 1
                    findings.append(Finding(n, rel_path, "stale",
                                            f"Doc '{expected_doc}' is {staleness} behind source",
                                            staleness))

        if not found_doc:
            n += 1
            findings.append(Finding(n, rel_path, "missing-doc",
                                    f"Create module doc '{expected_doc}' and link in Files.md"))

    # ── Check Files.md wiki-links to module docs ──
    # For source files that HAVE a doc, check Files.md links to it
    # Read raw Files.md content to find wiki-link patterns
    files_md_content = ""
    if files_md:
        with open(files_md) as f:
            files_md_content = f.read()

    missing_doc_files = {f.file for f in findings if f.status == "missing-doc"}
    for rel_path in sorted(sources.keys()):
        if rel_path in missing_doc_files:
            continue  # already told to create doc + link, skip separate link error
        basename = os.path.basename(rel_path)
        stem = os.path.splitext(basename)[0]
        expected_doc = f"{rid} {snake_to_pascal(stem)}"
        if expected_doc in module_docs:
            # Check if Files.md has a wiki-link for this file: [[DocName|filename]]
            link_pattern = f"[[{expected_doc}"
            if files_md_content and link_pattern not in files_md_content:
                n += 1
                findings.append(Finding(n, rel_path, "unlinked-files-md",
                                        f"Files.md has no wiki-link to '{expected_doc}'"))

    # ── Compare module docs → Dev dispatch ──
    for doc_name, doc_path in sorted(module_docs.items()):
        if doc_name not in dev_links:
            n += 1
            findings.append(Finding(n, doc_name, "unlinked",
                                    f"Module doc not linked from Dev dispatch"))

    # ── Check folder docs ──
    for d in sorted(source_dirs):
        # Count source files in this dir
        files_in_dir = [s for s in sources if os.path.dirname(s) == d]
        if len(files_in_dir) >= 2:
            dir_name = os.path.basename(d)
            expected_doc = f"{rid} {dir_name}"
            if expected_doc not in module_docs:
                n += 1
                findings.append(Finding(n, d + "/", "missing-folder-doc",
                                        f"No folder doc for directory with {len(files_in_dir)} source files"))

    # Print summary to stderr
    missing_docs = sum(1 for f in findings if f.status == "missing-doc")
    stale_docs = sum(1 for f in findings if f.status == "stale")
    missing_entries = sum(1 for f in findings if f.status == "missing-entry")
    stale_entries = sum(1 for f in findings if f.status == "stale-entry")
    unlinked = sum(1 for f in findings if f.status == "unlinked")
    unlinked_files = sum(1 for f in findings if f.status == "unlinked-files-md")
    missing_folder = sum(1 for f in findings if f.status == "missing-folder-doc")

    print(f"Source inventory: {len(sources)} files in {len(source_dirs)} directories", file=sys.stderr)
    print(f"Files.md: {len(normalized_files_md)} entries, {missing_entries} missing, {stale_entries} stale, {unlinked_files} not linked to docs", file=sys.stderr)
    print(f"Module docs: {len(module_docs)} exist, {missing_docs} missing, {stale_docs} stale, {unlinked} unlinked from Dev dispatch", file=sys.stderr)
    print(f"Folder docs: {missing_folder} missing", file=sys.stderr)
    print(f"Total findings: {len(findings)}", file=sys.stderr)
    if findings:
        print(f"STATUS: FAIL — {len(findings)} findings must be fixed", file=sys.stderr)
        print(f"NOTE: This script is not broken. Files must have precisely correct names and locations.", file=sys.stderr)
        print(f"      If the script says a doc is missing, rename or create it. Do not dismiss as false positive.", file=sys.stderr)
    else:
        print(f"STATUS: CLEAN", file=sys.stderr)

    return findings


def format_table(findings: list[Finding]) -> str:
    lines = ["| # | File | Status | Issue |",
             "|---|------|--------|-------|"]
    for f in findings:
        lines.append(f"| {f.number} | {f.file} | {f.status} | {f.issue} |")
    return "\n".join(lines)


def format_json(findings: list[Finding]) -> str:
    return json.dumps([{
        "number": f.number,
        "file": f.file,
        "status": f.status,
        "issue": f.issue,
        "staleness": f.staleness,
    } for f in findings], indent=2)


def main():
    parser = argparse.ArgumentParser(description="Audit docs against source tree")
    parser.add_argument("anchor_path", help="Path to anchor root")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    findings = audit(args.anchor_path, verbose=args.verbose)

    if args.json:
        print(format_json(findings))
    else:
        print(format_table(findings))


if __name__ == "__main__":
    main()
