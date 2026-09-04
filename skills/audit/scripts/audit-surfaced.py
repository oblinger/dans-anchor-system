#!/usr/bin/env python3
"""audit-surfaced.py — verify every agent recipe's `surfaced::` determination
still resolves.

Every recipe under `~/ob/kmr/SYS/Agent/Agent Recipes/` carries a `surfaced::`
line under its H1, per [[AREC]] § The fourth discipline, declaring how the
recipe reaches an agent. The claim rots silently: a memory gets renamed, a
CLAUDE.md line gets edited, and the recipe goes on asserting a mechanism that
no longer exists. This checker resolves the two checkable forms:

  memory — `<slug>`     a memory file must exist at
                        ~/.claude/projects/-Users-oblinger-ob-kmr/memory/<slug>.md
                        (slug may be written with hyphens or underscores;
                        both are accepted and normalized to underscores
                        before the filesystem check).

  CLAUDE.md — <desc>    at least one backtick- or quote-enclosed literal
                        inside <desc> must appear verbatim in
                        ~/.claude/CLAUDE.md. If <desc> carries no literal
                        excerpt at all, the claim cannot be mechanically
                        checked — reported as `unverifiable`, not `broken`.

The other two forms named in [[AREC]] — `in-area` (no mechanism to check)
and `skill — <name>` / `facet — <name>` (resolved by the skill/facet loading
machinery, out of scope here) — are counted but not validated.

Report-only. Never fixes — a stale `surfaced::` line is the author's call to
correct (memory renamed? recipe moved area? CLAUDE.md line reworded to keep
the same fact?), not something this script can safely guess.

Usage:
    audit-surfaced.py [--json]

Exit code: 1 if any `broken` finding, else 0. `unverifiable` and unparseable
lines are reported but do not fail the run — they need a human read, not a
mechanical fix, and failing the exit code on them would make the check
un-ignorable noise on every unrelated CI-style invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HOME = Path.home()
RECIPES_ROOT = HOME / "ob" / "kmr" / "SYS" / "Agent" / "Agent Recipes"
MEMORY_DIR = HOME / ".claude" / "projects" / "-Users-oblinger-ob-kmr" / "memory"
CLAUDE_MD = HOME / ".claude" / "CLAUDE.md"

SURFACED_LINE_RE = re.compile(r"^\s*surfaced::\s*(.+?)\s*$", re.MULTILINE)
# Backtick or double-quote enclosed literal excerpts inside a CLAUDE.md
# description, e.g. `` `yore` `` or `"Never ask the user to run a shell command"`.
QUOTE_RE = re.compile(r"`([^`]+)`|\"([^\"]+)\"")


def find_recipe_files(root: Path):
    """Every .md recipe file under root, skipping templates.

    Templates are prefixed `_` per [[AREC]] § Templates and other assets —
    they carry placeholder text (`{{...}}`) in their `surfaced::` line, not
    a real determination.
    """
    matches = []
    for path in sorted(root.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        matches.append(path)
    return matches


def parse_surfaced_line(text: str):
    """Return the value after `surfaced::` on its own line, or None.

    Anchored to line-start so prose that merely *mentions* `surfaced::` (as
    [[AREC]] itself does, documenting the field) is not mistaken for a
    declaration.
    """
    m = SURFACED_LINE_RE.search(text)
    if m is None:
        return None
    return m.group(1)


def classify(value: str):
    """Split a `surfaced::` value into (kind, detail).

    kind is one of: in-area, memory, claude, skill, facet, unparseable.
    """
    if "{{" in value:
        return ("unparseable", value)
    if value == "in-area" or value.startswith("in-area "):
        return ("in-area", value)
    m = re.match(r"^memory\s*—\s*`([^`]+)`", value)
    if m:
        return ("memory", m.group(1))
    m = re.match(r"^CLAUDE\.md\s*—\s*(.+)$", value)
    if m:
        return ("claude", m.group(1))
    m = re.match(r"^skill\s*—\s*(.+)$", value)
    if m:
        return ("skill", m.group(1))
    m = re.match(r"^facet\s*—\s*(.+)$", value)
    if m:
        return ("facet", m.group(1))
    return ("unparseable", value)


def resolve_memory(slug: str, memory_dir: Path) -> bool:
    """A memory file for `slug` exists, accepting hyphens or underscores."""
    normalized = slug.replace("-", "_")
    candidates = {slug, normalized, slug.replace("_", "-")}
    for candidate in candidates:
        if (memory_dir / f"{candidate}.md").exists():
            return True
    return False


def extract_quotes(desc: str):
    """Every backtick- or double-quote-enclosed literal inside desc."""
    out = []
    for m in QUOTE_RE.finditer(desc):
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def resolve_claude(desc: str, claude_text: str):
    """Return ("ok" | "broken" | "unverifiable", [matched-or-checked quotes])."""
    quotes = extract_quotes(desc)
    if not quotes:
        return ("unverifiable", [])
    for q in quotes:
        if q in claude_text:
            return ("ok", [q])
    return ("broken", quotes)


def scan(root: Path = RECIPES_ROOT, memory_dir: Path = MEMORY_DIR,
         claude_path: Path = CLAUDE_MD):
    claude_text = claude_path.read_text(encoding="utf-8") if claude_path.exists() else ""
    results = []
    for path in find_recipe_files(root):
        text = path.read_text(encoding="utf-8")
        value = parse_surfaced_line(text)
        if value is None:
            continue
        kind, detail = classify(value)
        rel = str(path.relative_to(root))
        entry = {"file": rel, "surfaced": value, "kind": kind}
        if kind == "memory":
            ok = resolve_memory(detail, memory_dir)
            entry["status"] = "ok" if ok else "broken"
            entry["slug"] = detail
        elif kind == "claude":
            status, quotes = resolve_claude(detail, claude_text)
            entry["status"] = status
            entry["checked_quotes"] = quotes
        elif kind == "unparseable":
            entry["status"] = "unparseable"
        else:
            entry["status"] = "skipped"
        results.append(entry)
    return results


def print_text(results):
    broken = [r for r in results if r["status"] == "broken"]
    unverifiable = [r for r in results if r["status"] == "unverifiable"]
    unparseable = [r for r in results if r["status"] == "unparseable"]
    ok = [r for r in results if r["status"] == "ok"]
    skipped = [r for r in results if r["status"] == "skipped"]

    print(f"/audit surfaced — {len(results)} recipe(s) with a surfaced:: line")
    print(f"  ok: {len(ok)}  broken: {len(broken)}  unverifiable: {len(unverifiable)}  "
          f"unparseable: {len(unparseable)}  skipped (in-area/skill/facet): {len(skipped)}")
    print()

    if broken:
        print("## Broken — the declared mechanism no longer resolves")
        for r in broken:
            if r["kind"] == "memory":
                print(f"  - {r['file']} — memory `{r['slug']}` not found under {MEMORY_DIR}")
            else:
                print(f"  - {r['file']} — none of {r['checked_quotes']!r} found in {CLAUDE_MD}")
        print()

    if unverifiable:
        print("## Unverifiable — CLAUDE.md description carries no literal excerpt to check")
        for r in unverifiable:
            print(f"  - {r['file']} — surfaced:: {r['surfaced']!r}")
        print()

    if unparseable:
        print("## Unparseable — surfaced:: line doesn't match a known form")
        for r in unparseable:
            print(f"  - {r['file']} — surfaced:: {r['surfaced']!r}")
        print()

    if not broken and not unverifiable and not unparseable:
        print("All checkable surfaced:: determinations resolve.")


def main(argv):
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = p.parse_args(argv[1:])

    results = scan()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_text(results)
    broken_count = sum(1 for r in results if r["status"] == "broken")
    return 1 if broken_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
