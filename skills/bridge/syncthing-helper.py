#!/usr/bin/env python3
"""bridge — Syncthing helper for the `bridge sync` mechanism (REST API).

Subcommands: pair, share, wait-converge, flip-bidirectional, record, status,
teardown, defaults. Reads/writes ~/.config/bridge/{config,hosts}.yaml.

Talks to local Syncthing daemon directly via REST; talks to remote via
SSH-wrapped curl. Idempotent — re-running a subcommand on already-applied
state is a no-op + a JSON status print.

Part of the `bridge` skill (renamed from mux-bridge per F150). This helper
backs the file-sync mechanism; `bridge claude` (environment-twin provisioning)
is handled by claude-provision.py.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. Install: pip3 install pyyaml")


CONFIG_DIR = Path.home() / ".config" / "bridge"
HOSTS_PATH = CONFIG_DIR / "hosts.yaml"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
# Legacy flat defaults file (mux-bridge era) — read as migration fallback.
LEGACY_DEFAULTS_PATH = CONFIG_DIR / "defaults.yaml"
ST_CONFIG_LOCAL = Path.home() / "Library" / "Application Support" / "Syncthing" / "config.xml"
ST_API_LOCAL = "http://127.0.0.1:8384"
USER_REMOTE = os.environ.get("USER", "oblinger")


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


def get_local_apikey():
    if not ST_CONFIG_LOCAL.exists():
        raise RuntimeError(f"Local Syncthing config missing at {ST_CONFIG_LOCAL} — daemon not started?")
    tree = ET.parse(str(ST_CONFIG_LOCAL))
    apikey = tree.getroot().find(".//gui/apikey")
    if apikey is None or not apikey.text:
        raise RuntimeError(f"No <gui><apikey> in {ST_CONFIG_LOCAL}")
    return apikey.text


def get_remote_apikey(host, user=USER_REMOTE):
    # Avoid python3 on remote (Xcode license gotcha on fresh macOS).
    # Use grep+sed to pull <apikey>...</apikey> from config.xml.
    remote = (
        'grep -E "<apikey>[^<]+</apikey>" '
        '"$HOME/Library/Application Support/Syncthing/config.xml" '
        '| head -1 | sed -E "s|.*<apikey>([^<]+)</apikey>.*|\\1|"'
    )
    cmd = ["ssh", f"{user}@{host}", remote]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"Failed to fetch remote API key from {host}: {result.stderr.strip() or '(empty output)'}")
    return result.stdout.strip()


def st_call(apikey, method, path, body=None, host=None):
    """Syncthing REST call. host=None → local; host=str → SSH-wrapped curl."""
    if host is None:
        url = f"{ST_API_LOCAL}{path}"
        req = urllib.request.Request(url, method=method)
        req.add_header("X-API-Key", apikey)
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, data=data, timeout=15) as resp:
                txt = resp.read().decode()
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} on {method} {path}: {e.read().decode()}")
    else:
        url = f"http://127.0.0.1:8384{path}"
        curl = ["curl", "-sf", "-X", method, "-H", f"X-API-Key: {apikey}"]
        if body is not None:
            curl += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
        curl.append(url)
        remote_cmd = " ".join(shlex.quote(c) for c in curl)
        result = subprocess.run(
            ["ssh", f"{USER_REMOTE}@{host}", remote_cmd],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Remote {method} {path} failed: {result.stderr.strip() or '(no stderr)'}")
        out = result.stdout.strip()
        return json.loads(out) if out else {}


def get_device_id(apikey, host=None):
    return st_call(apikey, "GET", "/rest/system/status", host=host)["myID"]


def cmd_pair(args):
    local_key = get_local_apikey()
    remote_key = get_remote_apikey(args.host)
    local_id = get_device_id(local_key)
    remote_id = get_device_id(remote_key, host=args.host)

    def add_device(key, host, peer_id, peer_name):
        cfg = st_call(key, "GET", "/rest/config", host=host)
        if any(d["deviceID"] == peer_id for d in cfg.get("devices", [])):
            return False
        cfg.setdefault("devices", []).append({
            "deviceID": peer_id,
            "name": peer_name,
            "addresses": ["dynamic"],
            "compression": "metadata",
            "introducer": False,
            "paused": False,
            "autoAcceptFolders": False,
        })
        st_call(key, "PUT", "/rest/config", body=cfg, host=host)
        return True

    local_added = add_device(local_key, None, remote_id, args.host.split(".")[0])
    remote_added = add_device(remote_key, args.host, local_id, "dev-mac")
    print(json.dumps({
        "local_id": local_id,
        "remote_id": remote_id,
        "local_added_remote_device": local_added,
        "remote_added_local_device": remote_added,
    }))


def cmd_share(args):
    local_key = get_local_apikey()
    remote_key = get_remote_apikey(args.host)
    local_id = get_device_id(local_key)
    remote_id = get_device_id(remote_key, host=args.host)
    folder_id = args.folder_id

    def add_folder(key, host, ftype):
        cfg = st_call(key, "GET", "/rest/config", host=host)
        if any(f["id"] == folder_id for f in cfg.get("folders", [])):
            # Update type if different
            for f in cfg["folders"]:
                if f["id"] == folder_id and f.get("type") != ftype:
                    f["type"] = ftype
                    st_call(key, "PUT", "/rest/config", body=cfg, host=host)
                    return "type-updated"
            return "exists"
        cfg.setdefault("folders", []).append({
            "id": folder_id,
            "label": folder_id,
            "path": args.folder,
            "type": ftype,
            "devices": [{"deviceID": local_id}, {"deviceID": remote_id}],
            "rescanIntervalS": 60,
            "fsWatcherEnabled": True,
        })
        st_call(key, "PUT", "/rest/config", body=cfg, host=host)
        return "added"

    local_r = add_folder(local_key, None, args.local_mode)
    remote_r = add_folder(remote_key, args.host, args.remote_mode)
    print(json.dumps({
        "folder_id": folder_id,
        "local_path": args.folder,
        "remote_path": args.folder,
        "local": {"mode": args.local_mode, "result": local_r},
        "remote": {"mode": args.remote_mode, "result": remote_r},
    }))


def cmd_wait_converge(args):
    remote_key = get_remote_apikey(args.host)
    start = time.time()
    last_print = 0
    last_need = None
    while time.time() - start < args.timeout:
        try:
            status = st_call(remote_key, "GET",
                             f"/rest/db/status?folder={args.folder_id}",
                             host=args.host)
            need_bytes = status.get("needBytes", 0)
            state = status.get("state", "unknown")
            global_bytes = status.get("globalBytes", 0)
            if need_bytes == 0 and state == "idle" and global_bytes > 0:
                print(json.dumps({
                    "converged": True,
                    "elapsed_sec": int(time.time() - start),
                    "globalBytes": global_bytes,
                }))
                return
            now = time.time()
            if now - last_print > 10 or last_need != need_bytes:
                pct = (1 - need_bytes / max(global_bytes, 1)) * 100 if global_bytes else 0
                print(f"  [{int(now-start)}s] state={state} need={need_bytes:,} of {global_bytes:,} ({pct:.1f}%)",
                      file=sys.stderr)
                last_print = now
                last_need = need_bytes
        except Exception as e:
            print(f"  [{int(time.time()-start)}s] error querying: {e}", file=sys.stderr)
        time.sleep(5)
    print(json.dumps({
        "converged": False,
        "elapsed_sec": int(time.time() - start),
        "error": "timeout",
    }), file=sys.stderr)
    sys.exit(2)


def cmd_flip(args):
    local_key = get_local_apikey()
    remote_key = get_remote_apikey(args.host)
    results = {}
    for label, key, host in [("local", local_key, None), ("remote", remote_key, args.host)]:
        cfg = st_call(key, "GET", "/rest/config", host=host)
        changed = False
        for f in cfg.get("folders", []):
            if f["id"] == args.folder_id and f.get("type") != "sendreceive":
                f["type"] = "sendreceive"
                changed = True
        if changed:
            st_call(key, "PUT", "/rest/config", body=cfg, host=host)
        results[label] = "flipped" if changed else "already-sendreceive"
    print(json.dumps({"folder_id": args.folder_id, **results}))


def cmd_record(args):
    data = read_yaml(HOSTS_PATH)
    data.setdefault("version", 1)
    hosts = data.setdefault("hosts", {})
    host = hosts.setdefault(args.host, {})
    host["mode"] = "syncthing"
    st = host.setdefault("syncthing", {})
    st["device_id_local"] = args.local_id
    st["device_id_remote"] = args.remote_id
    folders = [f for f in st.get("folders", []) if f.get("folder_id") != args.folder_id]
    folders.append({
        "folder_id": args.folder_id,
        "local": args.folder,
        "remote": args.folder,
        "move_aside": args.move_aside,
        "initialized": time.strftime("%Y-%m-%d"),
    })
    st["folders"] = folders
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"recorded": args.host, "folder_id": args.folder_id}))


def cmd_status(args):
    data = read_yaml(HOSTS_PATH)
    host_entry = data.get("hosts", {}).get(args.host)
    if not host_entry:
        print(json.dumps({"error": f"{args.host} not in hosts.yaml"}))
        sys.exit(1)
    mode = host_entry["mode"]
    out = {"host": args.host, "mode": mode}
    if mode != "syncthing":
        print(json.dumps(out))
        return

    try:
        local_key = get_local_apikey()
    except Exception as e:
        out["local_daemon"] = {"error": str(e)}
        print(json.dumps(out, indent=2))
        sys.exit(1)
    try:
        remote_key = get_remote_apikey(args.host)
        remote_reachable = True
    except Exception:
        remote_key, remote_reachable = None, False
    out["remote_reachable"] = remote_reachable

    folders_status = []
    for f in host_entry["syncthing"]["folders"]:
        fid = f["folder_id"]
        ls = {}
        try:
            ls = st_call(local_key, "GET", f"/rest/db/status?folder={fid}")
        except Exception as e:
            ls = {"error": str(e)}
        rs = None
        if remote_key:
            try:
                rs = st_call(remote_key, "GET", f"/rest/db/status?folder={fid}", host=args.host)
            except Exception as e:
                rs = {"error": str(e)}
        folders_status.append({
            "folder_id": fid,
            "path": f["local"],
            "local": {"state": ls.get("state"), "needBytes": ls.get("needBytes"), "globalBytes": ls.get("globalBytes")},
            "remote": {"state": rs.get("state") if rs else None,
                       "needBytes": rs.get("needBytes") if rs else None,
                       "globalBytes": rs.get("globalBytes") if rs else None},
            "move_aside": f.get("move_aside"),
        })
    out["folders"] = folders_status
    print(json.dumps(out, indent=2))


def cmd_teardown(args):
    data = read_yaml(HOSTS_PATH)
    host_entry = data.get("hosts", {}).get(args.host)
    if not host_entry or host_entry.get("mode") != "syncthing":
        print(json.dumps({"error": f"{args.host} has no syncthing entry"}))
        return

    local_key = get_local_apikey()
    try:
        remote_key = get_remote_apikey(args.host)
    except Exception:
        remote_key = None
        print(f"Warn: remote {args.host} unreachable; cleaning local side only", file=sys.stderr)

    folder_ids = [f["folder_id"] for f in host_entry["syncthing"].get("folders", [])]

    cfg = st_call(local_key, "GET", "/rest/config")
    cfg["folders"] = [f for f in cfg.get("folders", []) if f["id"] not in folder_ids]
    st_call(local_key, "PUT", "/rest/config", body=cfg)

    if remote_key:
        rcfg = st_call(remote_key, "GET", "/rest/config", host=args.host)
        rcfg["folders"] = [f for f in rcfg.get("folders", []) if f["id"] not in folder_ids]
        st_call(remote_key, "PUT", "/rest/config", body=rcfg, host=args.host)

    move_asides = [f.get("move_aside") for f in host_entry["syncthing"].get("folders", []) if f.get("move_aside")]
    del data["hosts"][args.host]
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"torn_down": args.host, "move_asides_on_remote": move_asides}))


def load_config():
    """Load ~/.config/bridge/config.yaml, migrating from the legacy flat
    defaults.yaml (mux-bridge era) on first read if needed."""
    if CONFIG_PATH.exists():
        return read_yaml(CONFIG_PATH)
    # Migrate legacy flat defaults.yaml → nested config.yaml
    legacy = read_yaml(LEGACY_DEFAULTS_PATH)
    cfg = {"version": 1, "defaults": {}, "claude_environment": {}}
    if legacy:
        d = cfg["defaults"]
        if legacy.get("default_remote"):
            d["remote"] = legacy["default_remote"]
        if legacy.get("default_mode"):
            d["sync_mode"] = legacy["default_mode"]
        if legacy.get("default_folder"):
            cfg["claude_environment"]["sync"] = [legacy["default_folder"]]
        write_yaml(CONFIG_PATH, cfg)
    return cfg


def cmd_defaults(args):
    cfg = load_config()
    cfg.setdefault("version", 1)
    cfg.setdefault("defaults", {})
    if args.set:
        for kv in args.set:
            if "=" not in kv:
                sys.exit(f"--set expects field=value, got: {kv}")
            field, value = kv.split("=", 1)
            # Accept legacy flat names too, mapping into the nested shape.
            field = {"default_remote": "remote", "default_mode": "sync_mode"}.get(field, field)
            cfg["defaults"][field] = value
        write_yaml(CONFIG_PATH, cfg)
    print(json.dumps(cfg, indent=2))


def main():
    p = argparse.ArgumentParser(prog="syncthing-helper.py", description=__doc__)
    sp = p.add_subparsers(dest="cmd", required=True)

    pr = sp.add_parser("pair", help="Pair local + remote Syncthing devices via REST")
    pr.add_argument("--host", required=True)
    pr.add_argument("--folder", help="(ignored — for symmetry)")
    pr.add_argument("--folder-id", help="(ignored — for symmetry)")
    pr.set_defaults(func=cmd_pair)

    sh = sp.add_parser("share", help="Create folder share on both sides")
    sh.add_argument("--host", required=True)
    sh.add_argument("--folder", required=True)
    sh.add_argument("--folder-id", required=True)
    sh.add_argument("--local-mode", default="sendonly", choices=["sendonly", "receiveonly", "sendreceive"])
    sh.add_argument("--remote-mode", default="receiveonly", choices=["sendonly", "receiveonly", "sendreceive"])
    sh.set_defaults(func=cmd_share)

    wc = sp.add_parser("wait-converge", help="Poll until needBytes==0 on remote")
    wc.add_argument("--host", required=True)
    wc.add_argument("--folder-id", required=True)
    wc.add_argument("--timeout", type=int, default=1800)
    wc.set_defaults(func=cmd_wait_converge)

    fl = sp.add_parser("flip-bidirectional", help="Set both sides to sendreceive")
    fl.add_argument("--host", required=True)
    fl.add_argument("--folder-id", required=True)
    fl.set_defaults(func=cmd_flip)

    re_ = sp.add_parser("record", help="Write host entry to hosts.yaml")
    re_.add_argument("--host", required=True)
    re_.add_argument("--folder", required=True)
    re_.add_argument("--folder-id", required=True)
    re_.add_argument("--local-id", required=True)
    re_.add_argument("--remote-id", required=True)
    re_.add_argument("--move-aside", required=True)
    re_.set_defaults(func=cmd_record)

    st_ = sp.add_parser("status", help="Print per-folder sync state")
    st_.add_argument("--host", required=True)
    st_.set_defaults(func=cmd_status)

    td = sp.add_parser("teardown", help="Remove folder shares on both sides")
    td.add_argument("--host", required=True)
    td.set_defaults(func=cmd_teardown)

    de = sp.add_parser("defaults", help="Read/write defaults.yaml (F146)")
    de.add_argument("--set", action="append", help="field=value, repeatable")
    de.set_defaults(func=cmd_defaults)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
