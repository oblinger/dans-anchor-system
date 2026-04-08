#!/usr/bin/env python3
"""anchor-mv — Move/rename markdown files and folders, updating all wiki-links.

Usage:
  anchor-mv [--dry-run] [moves-file]
  echo "old.md → new.md" | anchor-mv [--dry-run]
  anchor-mv [--dry-run] "old.md" "new.md"

Moves file format (one per line):
  CAB-create.md → cab-create.md
  cab-parts/ → CAB Parts/
  MUX Files.md → MUX Docs/MUX Dev/MUX Files.md

All paths are relative to the vault root (configured in ~/.config/skl/config.yaml).
The script scans the entire vault ONCE and applies all link replacements in one pass.

Arrow separator: → (U+2192) or -> (ASCII)
Lines starting with # are comments. Blank lines are ignored.
"""

import os
import re
import sys

import yaml


def load_vault_root():
    cfg_path = os.path.expanduser("~/.config/skl/config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        return os.path.expanduser(cfg.get("root", "~"))
    return os.path.expanduser("~")


def parse_moves(lines):
    """Parse move specifications from lines. Returns list of (old_path, new_path)."""
    moves = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split on → or ->
        if "→" in line:
            parts = line.split("→", 1)
        elif "->" in line:
            parts = line.split("->", 1)
        else:
            continue
        if len(parts) == 2:
            old = parts[0].strip()
            new = parts[1].strip()
            if old and new:
                moves.append((old, new))
    return moves


def basename_no_ext(path):
    """Get the base filename without extension."""
    return os.path.splitext(os.path.basename(path))[0]


def collect_all_md_files(vault_root):
    """Collect all .md files in the vault."""
    md_files = []
    for root, dirs, files in os.walk(vault_root):
        # Skip hidden dirs, build artifacts
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in ("node_modules", "__pycache__", "target",
                                 "build", ".build", "dist", "vendor")]
        for f in files:
            if f.endswith(".md"):
                md_files.append(os.path.join(root, f))
    return md_files


def build_replacements(moves):
    """Build a list of (old_name, new_name) for wiki-link replacements.

    For file moves: replace the basename (without extension).
    For folder moves: replace the folder name in any path-based links.
    """
    replacements = []
    for old_path, new_path in moves:
        old_base = basename_no_ext(old_path)
        new_base = basename_no_ext(new_path)

        if old_path.endswith("/"):
            # Folder rename — strip trailing slash
            old_folder = old_path.rstrip("/")
            new_folder = new_path.rstrip("/")
            replacements.append(("folder", old_folder, new_folder))
        else:
            # File rename
            if old_base != new_base:
                replacements.append(("file", old_base, new_base))
    return replacements


def apply_replacements(content, replacements):
    """Apply all replacements to markdown content. Returns (new_content, changes)."""
    changes = []
    new_content = content

    for rtype, old, new in replacements:
        if rtype == "file":
            # Replace [[old_name]] with [[new_name]]
            # Also handle [[old_name|alias]] → [[new_name|alias]]
            # And [[path/old_name]] → [[path/new_name]]

            # Pattern: [[...old_name...]] where old_name is the link target
            # Must handle: [[old_name]], [[old_name|alias]], [[folder/old_name]],
            # [[folder/old_name|alias]]
            def replace_link(m):
                full = m.group(0)
                inner = m.group(1)

                # Split on | to separate target from alias
                if "|" in inner:
                    target, alias = inner.split("|", 1)
                else:
                    target = inner
                    alias = None

                # Check if the target's basename matches old
                target_base = target.split("/")[-1] if "/" in target else target
                if target_base == old:
                    # Replace the basename in the target
                    if "/" in target:
                        new_target = "/".join(target.split("/")[:-1]) + "/" + new
                    else:
                        new_target = new

                    if alias:
                        replacement = f"[[{new_target}|{alias}]]"
                    else:
                        replacement = f"[[{new_target}]]"

                    if replacement != full:
                        changes.append((old, new, full, replacement))
                    return replacement
                return full

            new_content = re.sub(r"\[\[([^\]]+)\]\]", replace_link, new_content)

        elif rtype == "folder":
            # Replace folder name in path-based links
            # [[old_folder/file]] → [[new_folder/file]]
            def replace_folder_link(m):
                full = m.group(0)
                inner = m.group(1)

                # Split on | for alias
                if "|" in inner:
                    target, alias = inner.split("|", 1)
                else:
                    target = inner
                    alias = None

                if old in target:
                    new_target = target.replace(old, new)
                    if alias:
                        replacement = f"[[{new_target}|{alias}]]"
                    else:
                        replacement = f"[[{new_target}]]"

                    if replacement != full:
                        changes.append((old, new, full, replacement))
                    return replacement
                return full

            new_content = re.sub(r"\[\[([^\]]+)\]\]", replace_folder_link, new_content)

    return new_content, changes


def execute_moves(vault_root, moves, dry_run=False):
    """Execute file/folder moves."""
    for old_path, new_path in moves:
        old_abs = os.path.join(vault_root, old_path) if not os.path.isabs(old_path) else old_path
        new_abs = os.path.join(vault_root, new_path) if not os.path.isabs(new_path) else new_path

        if not os.path.exists(old_abs):
            # Try relative to cwd
            old_abs = os.path.abspath(old_path)
            new_abs = os.path.abspath(new_path)

        if not os.path.exists(old_abs):
            print(f"  SKIP: {old_path} — not found", file=sys.stderr)
            continue

        if dry_run:
            print(f"  WOULD MOVE: {old_path} → {new_path}")
        else:
            os.makedirs(os.path.dirname(new_abs), exist_ok=True)
            os.rename(old_abs, new_abs)
            print(f"  MOVED: {old_path} → {new_path}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    vault_root = load_vault_root()

    # Parse moves from args, file, or stdin
    if len(args) == 2 and not os.path.exists(args[0]):
        # Two args: old new (but only if first arg isn't a file)
        moves = [(args[0], args[1])]
    elif len(args) == 2 and os.path.isfile(args[0]) and not args[0].endswith(".md"):
        # First arg is a moves file
        with open(args[0]) as f:
            moves = parse_moves(f.readlines())
    elif len(args) == 1:
        if os.path.isfile(args[0]):
            with open(args[0]) as f:
                moves = parse_moves(f.readlines())
        else:
            print("Error: file not found:", args[0], file=sys.stderr)
            sys.exit(1)
    elif len(args) == 0:
        # Read from stdin
        if sys.stdin.isatty():
            print(__doc__.strip())
            sys.exit(1)
        moves = parse_moves(sys.stdin.readlines())
    else:
        print(__doc__.strip())
        sys.exit(1)

    if not moves:
        print("No moves specified.", file=sys.stderr)
        sys.exit(1)

    print(f"Vault root: {vault_root}")
    print(f"Moves: {len(moves)}")
    if dry_run:
        print("DRY RUN — no changes will be made\n")

    # Build replacements
    replacements = build_replacements(moves)
    print(f"Link replacements: {len(replacements)}")

    # Scan all md files
    md_files = collect_all_md_files(vault_root)
    print(f"Markdown files to scan: {len(md_files)}\n")

    # Apply replacements
    total_changes = 0
    files_changed = 0
    for md_path in md_files:
        try:
            with open(md_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (OSError, IOError):
            continue

        new_content, changes = apply_replacements(content, replacements)

        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel = os.path.relpath(md_path, vault_root)
            if dry_run:
                print(f"  {rel}: {len(changes)} links to update")
                for _, _, before, after in changes[:3]:
                    print(f"    {before} → {after}")
                if len(changes) > 3:
                    print(f"    ... +{len(changes) - 3} more")
            else:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

    # Execute file/folder moves
    print(f"\nLink changes: {total_changes} across {files_changed} files")
    print(f"\nFile moves:")
    execute_moves(vault_root, moves, dry_run)

    if dry_run:
        print(f"\nDry run complete. Run without --dry-run to apply.")
    else:
        print(f"\nDone. {total_changes} links updated, {len(moves)} files moved.")


if __name__ == "__main__":
    main()
