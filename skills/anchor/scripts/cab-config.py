#!/usr/bin/env python3
"""cab-config — Manage .anchor file for anchor orchestration.

Usage:
  cab-config init [--traits <trait>]     Create .anchor with defaults
  cab-config show                         Display current config
  cab-config set <key> <value>            Set a config key
  cab-config get <key>                    Get a config key's value
  cab-config path <key>                   Get absolute path for a config key

Standard keys:
  slug       Anchor's short identifier (e.g., DMUX)
  traits     List of traits (simple, topic, code, paper, skill)
  now        Path to the Now file (active work dashboard)
  rules      Path to the Rules file
  backlog    Path to the Backlog file
  inbox      Path to the Inbox file
  code       Path to the code repository. Required when the anchor has
             the `code` trait. May be absolute, or relative to the anchor
             root (e.g. `.` for inline repos, `../../proj/foo` for linked).

All other paths are relative to the anchor root (where .anchor lives).
The `code` key accepts absolute paths as well (see above).
"""

import os
import sys
import yaml


def find_anchor_root():
    """Walk up from cwd to find the directory containing .anchor file or .anchor/ dir."""
    d = os.getcwd()
    while d != "/":
        # New format: .anchor flat file
        if os.path.isfile(os.path.join(d, ".anchor")):
            return d
        # Legacy format: .anchor/ directory
        if os.path.isdir(os.path.join(d, ".anchor")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()


def config_path(root=None):
    """Return path to .anchor file."""
    if root is None:
        root = find_anchor_root()
    return os.path.join(root, ".anchor")


def load_config(root=None):
    """Load config, return (dict, anchor_root)."""
    if root is None:
        root = find_anchor_root()
    path = config_path(root)
    # New format: .anchor is a flat file
    if os.path.isfile(path):
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg, root
    # Legacy format: .anchor/config.yaml
    legacy = os.path.join(path, "config.yaml")
    if os.path.exists(legacy):
        with open(legacy) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg, root
    return {}, root


def save_config(cfg, root=None):
    """Save config to .anchor file (flat YAML)."""
    if root is None:
        root = find_anchor_root()
    path = config_path(root)
    # If legacy .anchor/ directory exists, migrate to flat file
    if os.path.isdir(path):
        # Write to .anchor/config.yaml for backwards compat
        legacy = os.path.join(path, "config.yaml")
        with open(legacy, "w") as f:
            yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
    else:
        with open(path, "w") as f:
            yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)


def resolve_path(root, relative_path):
    """Resolve a config path relative to anchor root."""
    if not relative_path:
        return None
    return os.path.join(root, relative_path)


def detect_slug(root):
    """Try to detect the slug from the anchor root directory."""
    for f in os.listdir(root):
        if f.endswith(".md") and not f.startswith("."):
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    first_lines = fh.read(500)
                if "cab-type:" in first_lines or "cab-traits:" in first_lines or "traits:" in first_lines:
                    slug = f.replace(".md", "")
                    return slug
            except Exception:
                continue
    return os.path.basename(root)


def detect_paths(root, slug):
    """Auto-detect standard paths based on what exists."""
    paths = {}

    docs = f"{slug} Docs"
    plan = os.path.join(docs, f"{slug} Plan")

    if os.path.isdir(os.path.join(root, plan)):
        for key, pattern in [
            ("now", f"{slug} Now.md"),
            ("rules", f"{slug} Rules.md"),
            ("backlog", f"{slug} Backlog.md"),
            ("inbox", f"{slug} Inbox.md"),
        ]:
            candidate = os.path.join(plan, pattern)
            if os.path.exists(os.path.join(root, candidate)):
                paths[key] = candidate

    if os.path.exists(os.path.join(root, "Code")):
        paths["code"] = "Code"

    return paths


def cmd_init(trait=None):
    """Create .anchor file with auto-detected defaults."""
    root = find_anchor_root()
    path = config_path(root)

    if os.path.isfile(path) or (os.path.isdir(path) and os.path.exists(os.path.join(path, "config.yaml"))):
        print(f"Config already exists: {path}")
        print("Use 'cab-config set <key> <value>' to modify.")
        return

    slug = detect_slug(root)
    paths = detect_paths(root, slug)

    cfg = {"slug": slug}
    if trait:
        cfg["traits"] = [trait]
    cfg.update(paths)

    save_config(cfg, root)
    print(f"Created: {path}")
    print(f"slug: {slug}")
    for k, v in paths.items():
        exists = "✓" if os.path.exists(os.path.join(root, v)) else "✗"
        print(f"  {k}: {v}  {exists}")


def cmd_show():
    """Display current config."""
    cfg, root = load_config()
    if not cfg:
        print("No config found. Run 'cab-config init' first.")
        return

    print(f"Anchor root: {root}")
    print(f"Config: {config_path(root)}")
    print()
    for k, v in cfg.items():
        if k in ("slug", "rid", "traits", "title", "description"):
            print(f"  {k}: {v}")
        else:
            abs_path = resolve_path(root, v)
            exists = "✓" if abs_path and os.path.exists(abs_path) else "✗"
            print(f"  {k}: {v}  {exists}")


def cmd_set(key, value):
    """Set a config key."""
    cfg, root = load_config()
    cfg[key] = value
    save_config(cfg, root)
    print(f"Set {key} = {value}")


def cmd_get(key):
    """Get a config key's value."""
    cfg, root = load_config()
    value = cfg.get(key)
    if value is None:
        print(f"Key '{key}' not set", file=sys.stderr)
        sys.exit(1)
    print(value)


def cmd_path(key):
    """Get absolute path for a config key."""
    cfg, root = load_config()
    value = cfg.get(key)
    if value is None:
        print(f"Key '{key}' not set", file=sys.stderr)
        sys.exit(1)
    abs_path = resolve_path(root, value)
    if abs_path and os.path.exists(abs_path):
        print(abs_path)
    else:
        print(f"Path does not exist: {abs_path}", file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip())
        sys.exit(1)

    cmd = args[0]

    if cmd == "init":
        trait = None
        if "--traits" in args:
            idx = args.index("--traits")
            if idx + 1 < len(args):
                trait = args[idx + 1]
        elif "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                trait = args[idx + 1]
        cmd_init(trait)

    elif cmd == "show":
        cmd_show()

    elif cmd == "set" and len(args) >= 3:
        cmd_set(args[1], args[2])

    elif cmd == "get" and len(args) >= 2:
        cmd_get(args[1])

    elif cmd == "path" and len(args) >= 2:
        cmd_path(args[1])

    else:
        print(__doc__.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()
