#!/usr/bin/env python3
"""bridge — rsync helper for the `bridge sync` rsync mode (F175 Phase 3).

Explicit push/pull batch transfers — no daemon, no live sync. The "hard gate"
mode: nothing moves until you say push or pull. Same-absolute-path contract
as the other sync modes (remote path == local path unless overridden at init).

Subcommands: init, push, pull, status, remove, teardown.
Reads/writes ~/.config/bridge/hosts.yaml (shared with syncthing-helper.py);
a host has ONE sync mode at a time — switching modes = teardown + re-init.

Idempotent: re-running init on recorded state is a no-op + JSON status print.
Never deletes remote files unless --mirror is passed explicitly.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. Install: pip3 install pyyaml")

CONFIG_DIR = Path.home() / ".config" / "bridge"
HOSTS_PATH = Path(os.environ["BRIDGE_HOSTS_PATH"]) \
    if os.environ.get("BRIDGE_HOSTS_PATH") else CONFIG_DIR / "hosts.yaml"
USER_REMOTE = os.environ.get("USER", "oblinger")
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]
DEFAULT_EXCLUDES = [".DS_Store", ".Trashes", "__pycache__"]


def read_yaml(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
    tmp.rename(path)


def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def host_entry(data, host):
    return data.get("hosts", {}).get(host)


def find_folder(entry, local):
    local = str(Path(local).expanduser().resolve())
    for f in entry.get("rsync", {}).get("folders", []):
        if f["local"] == local:
            return f
    return None


def cmd_init(args):
    data = read_yaml(HOSTS_PATH)
    hosts = data.setdefault("hosts", {})
    entry = hosts.setdefault(args.host, {})
    mode = entry.get("mode")
    if mode and mode != "rsync":
        sys.exit(f"ERROR: {args.host} already has sync mode '{mode}' — one mode "
                 f"per host; run that mode's teardown first.")
    local = str(Path(args.folder).expanduser().resolve())
    if not Path(local).is_dir():
        sys.exit(f"ERROR: local folder {local} does not exist")
    remote = args.remote_path or local
    entry["mode"] = "rsync"
    folders = entry.setdefault("rsync", {}).setdefault("folders", [])
    existing = find_folder(entry, local)
    if existing:
        print(json.dumps({"ok": True, "noop": True, "host": args.host,
                          "folder": existing}))
        return
    folders.append({"local": local, "remote": remote,
                    "last_push": None, "last_pull": None})
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"ok": True, "host": args.host, "mode": "rsync",
                      "folder": {"local": local, "remote": remote}}))


def _rsync(direction, args):
    data = read_yaml(HOSTS_PATH)
    entry = host_entry(data, args.host)
    if not entry or entry.get("mode") != "rsync":
        sys.exit(f"ERROR: {args.host} has no rsync mode configured "
                 f"(run: rsync-helper.py init {args.host} <folder>)")
    folders = entry["rsync"]["folders"]
    if args.folder:
        f = find_folder(entry, args.folder)
        if not f:
            sys.exit(f"ERROR: folder {args.folder} not configured for {args.host}")
        targets = [f]
    else:
        targets = folders

    results = []
    for f in targets:
        # trailing slash on src: copy CONTENTS of the dir into dst
        if direction == "push":
            src = f["local"].rstrip("/") + "/"
            dst = f"{USER_REMOTE}@{args.host}:{f['remote'].rstrip('/')}/"
            pre = ["ssh"] + SSH_OPTS + [f"{USER_REMOTE}@{args.host}",
                                        f"mkdir -p {f['remote']!r}"]
        else:
            src = f"{USER_REMOTE}@{args.host}:{f['remote'].rstrip('/')}/"
            dst = f["local"].rstrip("/") + "/"
            pre = None
        if pre:
            subprocess.run(pre, capture_output=True, text=True)
        cmd = ["rsync", "-a", "--stats",
               "-e", "ssh " + " ".join(SSH_OPTS)]
        for ex in DEFAULT_EXCLUDES + (args.exclude or []):
            cmd += ["--exclude", ex]
        if args.mirror:
            cmd += ["--delete"]
        if args.dry_run:
            cmd += ["--dry-run"]
        cmd += [src, dst]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit(f"ERROR: rsync {direction} failed for {f['local']}: "
                     f"{res.stderr.strip()[:300]}")
        m = re.search(r"Number of regular files transferred: ([\d,]+)", res.stdout)
        xfer = int(m.group(1).replace(",", "")) if m else None
        if not args.dry_run:
            f[f"last_{direction}"] = now_iso()
        results.append({"local": f["local"], "remote": f["remote"],
                        "direction": direction, "files_transferred": xfer,
                        "mirror": bool(args.mirror), "dry_run": bool(args.dry_run)})
    if not args.dry_run:
        write_yaml(HOSTS_PATH, data)
    print(json.dumps({"ok": True, "host": args.host, "results": results}))


def cmd_push(args):
    _rsync("push", args)


def cmd_pull(args):
    _rsync("pull", args)


def cmd_status(args):
    data = read_yaml(HOSTS_PATH)
    entry = host_entry(data, args.host)
    if not entry:
        print(json.dumps({"host": args.host, "mode": None}))
        return
    print(json.dumps({"host": args.host, "mode": entry.get("mode"),
                      "rsync": entry.get("rsync")}))


def cmd_remove(args):
    data = read_yaml(HOSTS_PATH)
    entry = host_entry(data, args.host)
    if not entry or entry.get("mode") != "rsync":
        sys.exit(f"ERROR: {args.host} has no rsync mode configured")
    local = str(Path(args.folder).expanduser().resolve())
    folders = entry["rsync"]["folders"]
    entry["rsync"]["folders"] = [f for f in folders if f["local"] != local]
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"ok": True, "removed": local,
                      "remaining": len(entry["rsync"]["folders"])}))


def cmd_teardown(args):
    data = read_yaml(HOSTS_PATH)
    entry = host_entry(data, args.host)
    if not entry or entry.get("mode") != "rsync":
        print(json.dumps({"ok": True, "noop": True,
                          "note": f"{args.host} has no rsync mode"}))
        return
    del data["hosts"][args.host]
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"ok": True, "host": args.host,
                      "note": "config unwired; no files deleted on either side"}))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init", help="Record rsync mode + folder mapping for a host")
    p.add_argument("host")
    p.add_argument("folder")
    p.add_argument("--remote-path", help="remote absolute path (default: same as local)")
    p.set_defaults(fn=cmd_init)

    for name, fn in [("push", cmd_push), ("pull", cmd_pull)]:
        p = sp.add_parser(name, help=f"rsync {name} (explicit, batch)")
        p.add_argument("host")
        p.add_argument("folder", nargs="?", help="one configured folder (default: all)")
        p.add_argument("--mirror", action="store_true",
                       help="pass --delete (dst mirrors src exactly)")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--exclude", action="append")
        p.set_defaults(fn=fn)

    p = sp.add_parser("status", help="Show mode + folders + last push/pull")
    p.add_argument("host")
    p.set_defaults(fn=cmd_status)

    p = sp.add_parser("remove", help="Remove one folder from the host's rsync set")
    p.add_argument("host")
    p.add_argument("folder")
    p.set_defaults(fn=cmd_remove)

    p = sp.add_parser("teardown", help="Unwire rsync mode for a host (config only)")
    p.add_argument("host")
    p.set_defaults(fn=cmd_teardown)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
