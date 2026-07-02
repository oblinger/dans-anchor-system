#!/usr/bin/env python3
"""Warden rule-discovery scan command (F211 — Rule compiler / installer).

Discovers where rulesets live under a configured root and materializes a
ruleset index. This is the compiler's from-scratch index builder and its
per-compile freshen sweep, implementing the committed contract in
`Warden Track/Warden Features/F211 — Rule compiler and installer.md`:

  - Rulesets are authored colocated, as `# RULESET R-<name>` heading tails
    of the spec docs they enforce (`^#+ RULESET <name>` is the declaration).
  - `--rescan` (from-scratch): content-read every markdown file under the
    root, extract ruleset names, write the index.
  - default (freshen): stat-sweep — enumerate + stat all markdown, then
    content-read ONLY files that are new or whose mtime/size changed since
    the stored index; carry unchanged entries forward; drop deleted files.
    This makes the mtime index self-freshening at enumeration time: new
    ruleset files AND new rulesets in already-indexed files are both caught
    on every compile, with no filesystem watcher.

Index schema (per F211 § Carry-outs): a top-level object with `root`, a
content `hash` over the ruleset set, `files` (one entry per ruleset-bearing
file `{path, mtime_ns, size, hash, ruleset_names[]}`), and `seen` (a compact
`{path: [mtime_ns, size]}` stat map over EVERY enumerated markdown file).
`seen` is what makes the freshen sweep truly selective: without a prior stat
for a non-bearing file it would look "new" and be content-read on every
sweep, so `seen` lets an unchanged file — bearing or not — be skipped with a
single stat. Paths are stored root-relative so the index is relocatable.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time


RULESET_RE = re.compile(r"^#+\s+RULESET\s+(\S+)", re.MULTILINE)

# Directories never worth walking for authored rulesets. `.claude/worktrees`
# is skipped so sibling worktree checkouts are not double-counted (a known
# basename-collision hazard).
SKIP_DIRS = {".git", ".warden", "__pycache__", "node_modules", ".venv"}
SKIP_REL = {os.path.join(".claude", "worktrees")}


def iter_markdown(root):
    """Yield absolute paths of every `.md` file under `root`, pruning
    SKIP_DIRS and SKIP_REL. This is the enumeration half of the stat-sweep."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if any(rel_dir == s or rel_dir.startswith(s + os.sep) for s in SKIP_REL):
            dirnames[:] = []
            continue
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def extract_ruleset_names(text):
    """Return the ruleset ids declared by `# RULESET <name>` headings, in
    document order, deduplicated."""
    seen = []
    for name in RULESET_RE.findall(text):
        if name not in seen:
            seen.append(name)
    return seen


def read_entry(abspath, root, st):
    """Content-read one file and build its index entry. Only called for new
    or changed files — the expensive half of the sweep."""
    with open(abspath, "rb") as fh:
        data = fh.read()
    names = extract_ruleset_names(data.decode("utf-8", "replace"))
    return {
        "path": os.path.relpath(abspath, root),
        "mtime_ns": st.st_mtime_ns,
        "size": st.st_size,
        "hash": hashlib.sha256(data).hexdigest(),
        "ruleset_names": names,
    }


def index_hash(files):
    """A stable content hash over the whole index — the compiler's cheap
    'did anything change' check. Covers path + per-file hash + ruleset names,
    so a moved verdict or a renamed ruleset both move this hash."""
    h = hashlib.sha256()
    for entry in sorted(files, key=lambda e: e["path"]):
        h.update(entry["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(entry["hash"].encode("utf-8"))
        h.update(b"\0")
        h.update("\0".join(entry["ruleset_names"]).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def load_index(index_path):
    """Load a prior index. Returns (bearing_by_path, seen) — the ruleset
    entries keyed by path, and the all-files stat map — both {} if none."""
    try:
        with open(index_path, "r", encoding="utf-8") as fh:
            prior = json.load(fh)
    except (FileNotFoundError, ValueError):
        return {}, {}
    bearing = {e["path"]: e for e in prior.get("files", [])}
    return bearing, prior.get("seen", {})


def build_index(root, prior_bearing, prior_seen, rescan):
    """The stat-sweep. Returns (files, seen, stats). For each enumerated
    markdown file, stat it; when mtime_ns AND size match the prior `seen`
    entry (and not --rescan), skip the read and carry any prior bearing entry
    forward; otherwise content-read it. `seen` records every file's stat so
    unchanged NON-bearing files are skipped too. Files absent from the walk
    are dropped (deletions)."""
    files = []
    seen = {}
    read = reused = 0
    for abspath in iter_markdown(root):
        st = os.stat(abspath)
        rel = os.path.relpath(abspath, root)
        seen[rel] = [st.st_mtime_ns, st.st_size]
        prev = None if rescan else prior_seen.get(rel)
        if prev and prev[0] == st.st_mtime_ns and prev[1] == st.st_size:
            reused += 1
            entry = prior_bearing.get(rel)
            if entry:
                files.append(entry)
        else:
            read += 1
            entry = read_entry(abspath, root, st)
            if entry["ruleset_names"]:
                files.append(entry)
    files.sort(key=lambda e: e["path"])
    return files, seen, {"read": read, "reused": reused,
                         "bearing": len(files), "seen": len(seen)}


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="warden-scan",
        description="Scan a root for `# RULESET` blocks and write the ruleset index.",
    )
    ap.add_argument("--root", required=True,
                    help="root directory to scan (engine config parameter — the vault root)")
    ap.add_argument("--index", default=None,
                    help="index file to read/write (default: <root>/.warden/rules-index.json)")
    ap.add_argument("--rescan", action="store_true",
                    help="from-scratch rebuild: content-read every file (ignore prior index)")
    ap.add_argument("--stats", action="store_true", help="print sweep statistics to stderr")
    ap.add_argument("--quiet", action="store_true", help="do not print the index path on success")
    args = ap.parse_args(argv)

    root = os.path.abspath(os.path.expanduser(args.root))
    if not os.path.isdir(root):
        ap.error(f"root is not a directory: {root}")
    index_path = args.index or os.path.join(root, ".warden", "rules-index.json")

    started = time.perf_counter()
    prior_bearing, prior_seen = load_index(index_path)
    files, seen, stats = build_index(root, prior_bearing, prior_seen, args.rescan)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    index = {
        "root": root,
        "hash": index_hash(files),
        "files": files,
        "seen": seen,
    }
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    tmp = index_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, index_path)

    if args.stats:
        mode = "rescan" if args.rescan else "freshen"
        rulesets = sum(len(e["ruleset_names"]) for e in files)
        print(
            f"warden-scan [{mode}] {stats['bearing']} ruleset files "
            f"({rulesets} rulesets), read {stats['read']} reused {stats['reused']}, "
            f"{elapsed_ms:.0f} ms",
            file=sys.stderr,
        )
    if not args.quiet:
        print(index_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
