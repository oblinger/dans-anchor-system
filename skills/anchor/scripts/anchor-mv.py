#!/usr/bin/env python3
"""anchor-mv — Move/rename markdown files and folders, updating all wiki-links.

Usage:
  anchor-mv [--dry-run] [--force] [moves-file]
  echo "old.md → new.md" | anchor-mv [--dry-run] [--force]
  anchor-mv [--dry-run] [--force] "old.md" "new.md"

Moves file format (one per line):
  CAB-create.md → cab-create.md
  cab-parts/ → CAB Parts/
  MUX Files.md → MUX Docs/MUX Dev/MUX Files.md

All paths are relative to the vault root (configured in ~/.config/skl/config.yaml).

Arrow separator: → (U+2192) or -> (ASCII)
Lines starting with # are comments. Blank lines are ignored.

This is a THIN FRONT-END. Every move is executed by `anchor update`, the
sanctioned path-to-path renamer in the `anchorage` crate — this script parses
the move list and shells out, and owns no rename or link-rewriting logic of its
own (HA T044, 2026-08-04, Q1 = B).

Why it was retired: this script used to hand-roll both halves. Its mover was a
bare `os.rename()` that checked only that the *source* existed, so a move onto
an existing path silently squashed it — on 2026-08-03 that destroyed the
24-line `[[ATT]]` anchor page during a Staff-prefix sweep, exit 0 and no
warning. `anchor update` refuses a collision by default (`RenameCollision`,
non-zero exit, both files intact) and overwrites only under `--force`. Its
link rewriting is also strictly broader than the regex pass this replaced:
wiki-links, `hook://` URLs, and relative markdown links, in one mechanism.
"""

import os
import shutil
import subprocess
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
        old, new = parts[0].strip(), parts[1].strip()
        if old and new:
            moves.append((old.rstrip("/"), new.rstrip("/")))
    return moves


def resolve(vault_root, path):
    """Vault-relative paths win; fall back to cwd-relative for a loose invocation."""
    if os.path.isabs(path):
        return path
    in_vault = os.path.join(vault_root, path)
    if os.path.exists(in_vault):
        return in_vault
    return os.path.abspath(path)


def execute_moves(vault_root, moves, dry_run=False, force=False):
    """Delegate every move to `anchor update`. Returns the number that failed."""
    anchor = shutil.which("anchor")
    if not anchor:
        # No fallback: a silent regex-only pass would move nothing and report
        # success, which is exactly the failure mode this rewrite removed.
        print(
            "anchor-mv: `anchor` not found on PATH — cannot move anything.\n"
            "           Build it: cargo build --release in docket/anchorage,\n"
            "           and symlink target/release/anchor into ~/bin.",
            file=sys.stderr,
        )
        sys.exit(1)

    failures = 0
    for old_path, new_path in moves:
        src = resolve(vault_root, old_path)
        dst = new_path if os.path.isabs(new_path) else os.path.join(vault_root, new_path)

        if not os.path.exists(src):
            print(f"  SKIP: {old_path} — not found", file=sys.stderr)
            continue

        cmd = [anchor, "update", src, dst, "--root", vault_root, "--mkpath"]
        if dry_run:
            cmd.append("--dry-run")
        if force:
            cmd.append("--force")

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            failures += 1
            detail = (proc.stderr or proc.stdout).strip()
            print(f"  FAILED: {old_path} → {new_path}\n    {detail}", file=sys.stderr)
            continue

        print(f"  {'WOULD MOVE' if dry_run else 'MOVED'}: {old_path} → {new_path}")
        for line in (proc.stdout or "").splitlines():
            if "rewrote" in line or "would rewrite" in line:
                print(f"    {line.strip()}")

    return failures


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    force = "--force" in args
    args = [a for a in args if a not in ("--dry-run", "--force")]

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
            print((__doc__ or "").strip())
            sys.exit(1)
        moves = parse_moves(sys.stdin.readlines())
    else:
        print((__doc__ or "").strip())
        sys.exit(1)

    if not moves:
        print("No moves specified.", file=sys.stderr)
        sys.exit(1)

    print(f"Vault root: {vault_root}")
    print(f"Moves: {len(moves)}")
    if dry_run:
        print("DRY RUN — no changes will be made")
    if force:
        print("FORCE — an existing destination will be OVERWRITTEN")
    print("\nFile moves:")

    failures = execute_moves(vault_root, moves, dry_run, force)

    if failures:
        print(
            f"\n{failures} of {len(moves)} move(s) failed — nothing was forced.\n"
            "Re-run with --force only if overwriting the destination is intended.",
            file=sys.stderr,
        )
        sys.exit(1)

    if dry_run:
        print("\nDry run complete. Run without --dry-run to apply.")
    else:
        print(f"\nDone. {len(moves)} path(s) moved, links rewritten by `anchor update`.")


if __name__ == "__main__":
    main()
