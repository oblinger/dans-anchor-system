#!/usr/bin/env python3
"""cab-config — Manage .anchor/config.yaml for anchor orchestration.

Usage:
  cab-config init [--type <cab-type>]     Create config with defaults
  cab-config show                         Display current config
  cab-config set <key> <value>            Set a config key
  cab-config get <key>                    Get a config key's value
  cab-config path <key>                   Get absolute path for a config key

Standard keys:
  tid        Anchor's Root ID (e.g., DMUX)
  type       CAB type (simple, topic, code, paper, skill)
  now        Path to the Now file (active work dashboard)
  rules      Path to the Rules file
  backlog    Path to the Backlog file
  inbox      Path to the Inbox file
  code       Path to the code repository (usually a symlink)

All paths are relative to the anchor root (where .anchor/ lives).
"""

import os
import sys
import yaml


def find_anchor_root():
    """Walk up from cwd to find the directory containing .anchor/."""
    d = os.getcwd()
    while d != "/":
        if os.path.isdir(os.path.join(d, ".anchor")):
            return d
        d = os.path.dirname(d)
    # If no .anchor found, use cwd
    return os.getcwd()


def config_path(root=None):
    """Return path to .anchor/config.yaml."""
    if root is None:
        root = find_anchor_root()
    return os.path.join(root, ".anchor", "config.yaml")


def load_config(root=None):
    """Load config, return (dict, anchor_root)."""
    if root is None:
        root = find_anchor_root()
    path = config_path(root)
    if os.path.exists(path):
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}
    return cfg, root


def save_config(cfg, root=None):
    """Save config to .anchor/config.yaml."""
    if root is None:
        root = find_anchor_root()
    path = config_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)


def resolve_path(root, relative_path):
    """Resolve a config path relative to anchor root."""
    if not relative_path:
        return None
    return os.path.join(root, relative_path)


def detect_tid(root):
    """Try to detect the RID from the anchor root directory."""
    # Look for a file matching *name*.md with cab-type in frontmatter
    basename = os.path.basename(root)
    # Common pattern: the anchor folder name IS the RID or contains it
    for f in os.listdir(root):
        if f.endswith(".md") and not f.startswith("."):
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    first_lines = fh.read(500)
                if "cab-type:" in first_lines:
                    # This is likely the anchor page — extract RID from filename
                    tid = f.replace(".md", "")
                    return tid
            except Exception:
                continue
    return basename


def detect_paths(root, tid):
    """Auto-detect standard paths based on what exists.

    Only detects keys that scripts actually use:
    - now, rules, backlog, inbox — operational files scripts read/write
    - code — repo location for lint and build tools

    Does NOT detect navigational paths (plan, dev, user folders) —
    those belong in the anchor's dispatch table, not in config.
    """
    paths = {}

    # Docs structure: <RID> Docs/<RID> Plan/
    docs = f"{tid} Docs"
    plan = os.path.join(docs, f"{tid} Plan")

    # Look for standard operational files in plan folder
    if os.path.isdir(os.path.join(root, plan)):
        for key, pattern in [
            ("now", f"{tid} Now.md"),
            ("rules", f"{tid} Rules.md"),
            ("backlog", f"{tid} Backlog.md"),
            ("inbox", f"{tid} Inbox.md"),
        ]:
            candidate = os.path.join(plan, pattern)
            if os.path.exists(os.path.join(root, candidate)):
                paths[key] = candidate

    # Code symlink
    if os.path.exists(os.path.join(root, "Code")):
        paths["code"] = "Code"

    return paths


def cmd_init(cab_type=None):
    """Create .anchor/config.yaml with auto-detected defaults."""
    root = find_anchor_root()
    path = config_path(root)

    if os.path.exists(path):
        print(f"Config already exists: {path}")
        print("Use 'cab-config set <key> <value>' to modify.")
        return

    tid = detect_tid(root)
    paths = detect_paths(root, tid)

    cfg = {"tid": tid}
    if cab_type:
        cfg["type"] = cab_type
    cfg.update(paths)

    save_config(cfg, root)
    print(f"Created: {path}")
    print(f"RID: {tid}")
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
        if k in ("tid", "type"):
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
        cab_type = None
        if "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                cab_type = args[idx + 1]
        cmd_init(cab_type)

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
