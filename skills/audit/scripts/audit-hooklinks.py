#!/usr/bin/env python3
"""audit-hooklinks — report `hook://` links that HookAnchor resolves to nothing.

Why this exists (HA T052, 2026-08-06). The vault's `spot://` URLs were bulk-
rewritten to `hook://` during the Spotlight-Commander migration **without the
command definitions being carried across**, so links like `hook://sensitiveopendoc`
have pointed at nothing for eleven months. Nothing detected them: the breakage
surfaced only when the user happened to reach for one command by hand. This is
the standing detector for that class.

Report-only. It never edits a file and never files a backlog row. Whether the
*renderer* should additionally strike a dead link in place is a separate
question tracked as HA T116 — this is a reporting surface, not a rendering one.

The oracle is the app, and that is load-bearing
-----------------------------------------------
Each distinct target is resolved by running `ha -m <target>`. It is tempting to
instead read `~/.config/hookanchor/commands.txt` and test set membership; two
separate ways that gets the answer wrong, both hit while building this checker:

  1. The store's line format is `PATCH! NAME:action`. A parser that splits on
     the first `:` takes the patch prefix as part of the name, so almost
     nothing resolves — first run reported **2954** dead targets.
  2. Even with names parsed correctly, exact-name membership is the wrong
     *semantics*. A bare `hook://{q}` falls through to `handle_execute_url`,
     which SEARCHES — HookAnchor matches on initials, so `hook://cnnp` opens
     `CNN Page` and is a perfectly live link. Exact lookup called it dead.

So: ask the app. A dead link is one HookAnchor's own resolver finds nothing
for, which is the only definition that matches what happens when the user
clicks it.

What counts as a target
-----------------------
Parsed with the grammar `handle_hook_url` (`src/cli/url_handlers.rs`) applies:

    hook://p/{Name}     popup on {Name}          -> checked
    hook://{Name}       jump / search            -> checked
    hook://a/...        action form              -> NOT checked
    hook://x/...        plain search string      -> NOT checked
    hook://f/...        folder / anchor+subpath  -> NOT checked
    hook://~... /...    literal filesystem path  -> checked as a path, not a command

The unchecked prefixes are **counted and reported** rather than silently
dropped: a checker that quietly ignores part of its own corpus reports a clean
sweep it did not earn.

Traversal
---------
Uses `os.walk`, NOT `grep -r`. A `grep -r <pat> .` rooted at the vault silently
returns a partial file set — a subtree search finds more hits than the whole-
vault search (measured 2026-08-10: 3 vs 8 for the same pattern). Any corpus
count taken that way is unreliable.

Usage:
    audit-hooklinks.py [--json] [--vault PATH] [--ha PATH]
                       [--show-placeholders] [--min-occurrences N]
                       [--jobs N] [--self-test]

Exit status is 0 unless the scan itself failed; findings are data, not errors.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

HOME = Path.home()
VAULT_ROOT = HOME / "ob" / "kmr"
HA_BIN = HOME / "ob" / "grove" / "HookAnchorApp" / "target" / "release" / "ha"

SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/", "/.git/")

# Prefixes that do not name a command (see module docstring).
UNCHECKED_PREFIXES = ("a/", "x/", "f/")

# Documentation placeholders — a `hook://` written to SHOW the URL form rather
# than to link anywhere. Reporting these would bury the real findings under the
# docs that describe the feature.
PLACEHOLDER_TARGETS = {
    "name", "command", "commandname", "anchor", "slug", "target",
    "somecommand", "yourcommand", "example", "foo", "bar",
}

# An unsubstituted template (`{Name}`, `<Name>`, `[Name]`).
PLACEHOLDER_SHAPE = re.compile(r"^[{<\[]|[}>\]]$")

# A target carrying no alphanumeric character at all is prose punctuation that
# happened to follow `hook://` in an example — `…`, `...`, `*`, `^`, `,`.
HAS_ALNUM = re.compile(r"[A-Za-z0-9]")

# `[label](hook://target)` — the markdown inline-link form, which is how nearly
# every real link is written. Balanced to ONE level of nested parens so a
# filename like `Foo (2019).pdf` is not truncated at its own `(`; that
# truncation silently manufactures dead targets out of live ones.
MD_LINK = re.compile(r"\]\(\s*(hook://(?:[^()\s]|\([^()]*\))*)\s*\)")

# A bare URL outside a markdown link. Stops at whitespace and at the delimiters
# that end a link in running text or a table cell.
BARE_URL = re.compile(r"hook://([^\s)\]|\"'`<>]+)")


def iter_markdown(vault_root: Path):
    for root, dirs, files in os.walk(vault_root):
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        for f in files:
            if f.endswith(".md"):
                yield Path(root) / f


def raw_urls(line: str):
    """Every `hook://` query on one line, markdown-link form taking priority."""
    seen_spans = []
    for m in MD_LINK.finditer(line):
        seen_spans.append(m.span(1))
        yield m.group(1)[len("hook://"):]
    for m in BARE_URL.finditer(line):
        # Skip anything already yielded as a markdown link.
        if any(s <= m.start() < e for s, e in seen_spans):
            continue
        yield m.group(1)


def classify(raw: str):
    """Map a raw `hook://` query to (kind, target).

    kind: 'command' (resolve through ha), 'literal' (filesystem path),
    'unchecked' (a prefix this tool does not resolve), 'placeholder'.
    """
    for pre in UNCHECKED_PREFIXES:
        if raw.startswith(pre):
            return "unchecked", raw
    if raw.startswith("p/"):
        raw = raw[2:]
    target = unquote(raw).strip()
    if not target:
        return "placeholder", raw
    if target.startswith("~") or target.startswith("/"):
        return "literal", target
    if (not HAS_ALNUM.search(target)
            or PLACEHOLDER_SHAPE.search(target)
            or target.lower() in PLACEHOLDER_TARGETS):
        return "placeholder", target
    return "command", target


def collect(vault_root: Path):
    occurrences = defaultdict(list)   # target -> [(path, line_no)]
    counts = defaultdict(int)
    placeholders = defaultdict(int)
    literals = defaultdict(list)
    files_scanned = 0

    for path in iter_markdown(vault_root):
        files_scanned += 1
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        if "hook://" not in text:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for raw in raw_urls(line):
                kind, target = classify(raw)
                counts[kind] += 1
                if kind == "placeholder":
                    placeholders[target] += 1
                elif kind == "literal":
                    literals[target].append((str(path), line_no))
                elif kind == "command":
                    occurrences[target].append((str(path), line_no))
    return files_scanned, occurrences, literals, dict(counts), dict(placeholders)


def resolves(ha_bin: Path, target: str) -> bool:
    """Does HookAnchor's own resolver find anything for this target?"""
    try:
        out = subprocess.run([str(ha_bin), "-m", target, "--format=name"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return True   # unknown, not dead — never invent a finding
    return bool(out.stdout.strip())


def check_ha(ha_bin: Path):
    """Fail loudly if the oracle is not usable — a broken `ha` would otherwise
    report every link in the vault as dead."""
    if not ha_bin.exists():
        sys.stderr.write(f"audit-hooklinks: no ha binary at {ha_bin}\n")
        raise SystemExit(2)
    probe = subprocess.run([str(ha_bin), "--dump", "--format=name"],
                           capture_output=True, text=True, timeout=120)
    if probe.returncode != 0 or not probe.stdout.strip():
        sys.stderr.write("audit-hooklinks: `ha --dump` returned nothing — the "
                         "command store is unreadable; refusing to report every "
                         "link as dead\n")
        raise SystemExit(2)
    return len(probe.stdout.splitlines())


def self_test(ha_bin: Path):
    """Red-check the oracle: a name that must resolve, and one that must not.

    Without this the tool can only report zeros credibly by accident — a
    resolver that answers 'yes' to everything and one that is actually working
    produce the same clean sweep.
    """
    live_probe = "HA"
    dead_probe = "zzz-no-such-command-zzz-t052"
    ok_live = resolves(ha_bin, live_probe)
    ok_dead = not resolves(ha_bin, dead_probe)
    print(f"self-test: live probe {live_probe!r} resolves … "
          f"{'PASS' if ok_live else 'FAIL'}")
    print(f"self-test: dead probe {dead_probe!r} does not resolve … "
          f"{'PASS' if ok_dead else 'FAIL'}")
    return ok_live and ok_dead


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--vault", type=Path, default=VAULT_ROOT)
    ap.add_argument("--ha", type=Path, default=HA_BIN)
    ap.add_argument("--show-placeholders", action="store_true")
    ap.add_argument("--min-occurrences", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--self-test", action="store_true",
                    help="check the resolver oracle both ways and exit")
    args = ap.parse_args()

    if args.self_test:
        raise SystemExit(0 if self_test(args.ha) else 1)

    known = check_ha(args.ha)
    files_scanned, occ, literals, counts, placeholders = collect(args.vault)

    targets = sorted(occ)
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        verdicts = list(ex.map(lambda t: resolves(args.ha, t), targets))
    dead = {t: occ[t] for t, ok in zip(targets, verdicts)
            if not ok and len(occ[t]) >= args.min_occurrences}
    live_targets = sum(1 for ok in verdicts if ok)
    live_occ = sum(len(occ[t]) for t, ok in zip(targets, verdicts) if ok)

    dead_missing = {t: locs for t, locs in literals.items()
                    if not Path(os.path.expanduser(t)).exists()}
    occurrences = sum(len(v) for v in dead.values())

    if args.json:
        print(json.dumps({
            "files_scanned": files_scanned,
            "commands_known": known,
            "distinct_targets_checked": len(targets),
            "distinct_dead_targets": len(dead),
            "dead_occurrences": occurrences,
            "live_targets": live_targets,
            "live_occurrences": live_occ,
            "by_kind": counts,
            "placeholders_excluded": placeholders,
            "dead_literal_paths": {t: [{"file": f, "line": n} for f, n in v]
                                   for t, v in dead_missing.items()},
            "dead": {t: [{"file": f, "line": n} for f, n in locs]
                     for t, locs in sorted(dead.items(),
                                           key=lambda kv: -len(kv[1]))},
        }, indent=2))
        return

    print(f"audit-hooklinks — {files_scanned} markdown files, "
          f"{known} known commands")
    print(f"  live      {live_targets} distinct target(s), "
          f"{live_occ} occurrence(s)")
    print(f"  DEAD      {len(dead)} distinct target(s), "
          f"{occurrences} occurrence(s)")
    print(f"  not checked: {counts.get('unchecked', 0)} a//x//f/ form(s), "
          f"{counts.get('placeholder', 0)} documentation placeholder(s)")
    if dead_missing:
        print(f"  literal paths that do not exist: {len(dead_missing)}")

    if not dead and not dead_missing:
        print("\nNo dead hook:// targets.")
        return

    print()
    for target, locs in sorted(dead.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"  hook://{target}  ({len(locs)}x)")
        for f, n in locs[:3]:
            rel = f[len(str(args.vault)) + 1:] if f.startswith(str(args.vault)) else f
            print(f"      {rel}:{n}")
        if len(locs) > 3:
            print(f"      … and {len(locs) - 3} more")

    for target, locs in sorted(dead_missing.items()):
        print(f"  hook://{target}  ({len(locs)}x)  [literal path does not exist]")
        for f, n in locs[:2]:
            rel = f[len(str(args.vault)) + 1:] if f.startswith(str(args.vault)) else f
            print(f"      {rel}:{n}")

    if args.show_placeholders and placeholders:
        print("\nExcluded as documentation placeholders:")
        for t, c in sorted(placeholders.items(), key=lambda kv: -kv[1]):
            print(f"  hook://{t}  ({c}x)")


if __name__ == "__main__":
    main()
