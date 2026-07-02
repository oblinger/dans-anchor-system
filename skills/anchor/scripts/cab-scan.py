#!/usr/bin/env python3
"""cab-scan — List all registered CAB anchors.

Usage:
  cab-scan                    Scan from configured root
  cab-scan <path>             Scan from specified path
  cab-scan --show             Show current anchor registry (no rescan)

Finds all folders containing a .anchor file (flat YAML) or legacy
.anchor/config.yaml directory, and writes the list to
~/.config/skl/anchors.yaml.

The scan root defaults to the 'root' key in ~/.config/skl/config.yaml,
or ~ if not configured.
"""

import os
import sys
import yaml


CONFIG_DIR = os.path.expanduser("~/.config/skl")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")
ANCHORS_PATH = os.path.join(CONFIG_DIR, "anchors.yaml")


def load_global_config():
    """Load ~/.config/skl/config.yaml."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_scan_root(explicit=None):
    """Determine where to scan."""
    if explicit:
        return os.path.expanduser(explicit)
    cfg = load_global_config()
    root = cfg.get("root", "~")
    return os.path.expanduser(root)


def scan(root):
    """Walk from root finding all folders with .anchor file or .anchor/config.yaml."""
    anchors = []
    root = os.path.abspath(root)

    skip_dirs = {
        ".git", ".svn", "node_modules", "__pycache__", ".venv",
        "target", "build", ".build", "DerivedData", ".Trash",
        "Library", "Applications", ".cache", ".npm", ".cargo",
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in skip_dirs and not d.startswith(".")
        ]

        # New format: .anchor flat file
        if ".anchor" in filenames:
            anchors.append(dirpath)
        # Legacy format: .anchor/ directory with config.yaml
        elif os.path.exists(os.path.join(dirpath, ".anchor", "config.yaml")):
            anchors.append(dirpath)

    anchors.sort()
    return anchors


def write_anchors(anchors):
    """Write anchors to ~/.config/skl/anchors.yaml."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    home = os.path.expanduser("~")
    paths = []
    for a in anchors:
        if a.startswith(home):
            paths.append("~" + a[len(home):])
        else:
            paths.append(a)
    with open(ANCHORS_PATH, "w") as f:
        yaml.dump({"anchors": paths}, f, default_flow_style=False)


def read_slug(dirpath):
    """Read slug from an anchor's .anchor file or legacy .anchor/config.yaml."""
    # New format
    anchor_file = os.path.join(dirpath, ".anchor")
    if os.path.isfile(anchor_file):
        try:
            with open(anchor_file) as f:
                cfg = yaml.safe_load(f) or {}
            return cfg.get("slug", "")
        except Exception:
            return ""
    # Legacy format
    cfg_path = os.path.join(dirpath, ".anchor", "config.yaml")
    try:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("slug", "")
    except Exception:
        return ""


def display_anchors(anchors):
    """Print anchor list with slugs."""
    home = os.path.expanduser("~")
    for a in anchors:
        display = "~" + a[len(home):] if a.startswith(home) else a
        slug = read_slug(a)
        if slug:
            print(f"  {slug:8s} {display}")
        else:
            print(f"  {'':8s} {display}")


def cmd_scan(root):
    """Scan and write results."""
    print(f"Scanning from: {root}")
    anchors = scan(root)
    write_anchors(anchors)
    print(f"Found {len(anchors)} registered anchors → {ANCHORS_PATH}")
    display_anchors(anchors)


def cmd_show():
    """Show current anchor registry without rescanning."""
    if not os.path.exists(ANCHORS_PATH):
        print("No anchors registered. Run 'cab-scan' first.")
        return
    with open(ANCHORS_PATH) as f:
        data = yaml.safe_load(f) or {}
    paths = data.get("anchors", [])
    print(f"{len(paths)} registered anchors:")
    full_paths = [os.path.expanduser(p) for p in paths]
    display_anchors(full_paths)


def main():
    args = sys.argv[1:]
    if not args:
        cmd_scan(get_scan_root())
    elif args[0] == "--show":
        cmd_show()
    elif args[0] in ("--help", "-h"):
        print(__doc__.strip())
    else:
        cmd_scan(get_scan_root(args[0]))


if __name__ == "__main__":
    main()
