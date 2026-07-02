#!/usr/bin/env python3
"""bridge — NFS helper for the `bridge sync` NFS-via-symlink mode (F175 Phase 2).

Live mount: dev Mac exports the folder over NFS; the remote mounts it under
/Volumes/mb-<host>-<slug>/ and a symlink at the canonical path covers it, so
the file tree appears identical on both sides with zero convergence lag.

NFS is unencrypted + unauthenticated, so init is REFUSED unless the remote
resolves to a verifiably private address (Tailscale 100.64/10, RFC1918, or
.local→RFC1918). And the live steps need sudo on BOTH sides (edit
/etc/exports + nfsd on the dev Mac; mount on the remote) — this helper NEVER
runs sudo. It probes, plans, records, and checks; the agent drives the
emitted plan through an interactive box session where the user can enter
passwords.

Subcommands: probe, plan, record, status, teardown-plan.
Reads/writes ~/.config/bridge/hosts.yaml (shared; one sync mode per host).
"""
import argparse
import datetime
import ipaddress
import json
import os
import socket
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


def classify_ip(ip):
    """tailscale | rfc1918 | public"""
    addr = ipaddress.ip_address(ip)
    if addr in ipaddress.ip_network("100.64.0.0/10"):
        return "tailscale"
    if addr.is_private:
        return "rfc1918"
    return "public"


def resolve_host(host, ip_override=None):
    ip = ip_override or socket.gethostbyname(host)
    cls = classify_ip(ip)
    if cls == "rfc1918" and host.endswith(".local"):
        cls = "mdns"
    return ip, cls


def mount_point_for(host, folder):
    slug = Path(folder).name.lower().replace(" ", "-")
    return f"/Volumes/mb-{host.split('.')[0]}-{slug}"


def cmd_probe(args):
    try:
        ip, cls = resolve_host(args.host, args.ip)
    except (socket.gaierror, ValueError) as e:
        print(json.dumps({"ok": False, "error": f"cannot resolve {args.host}: {e}"}))
        sys.exit(1)
    private = cls in ("tailscale", "rfc1918", "mdns")
    out = {"ok": private, "host": args.host, "ip": ip, "class": cls}
    if not private:
        out["refusal"] = ("NFS init blocked: remote IP is public; NFS is "
                          "unencrypted and unauthenticated. Set up Tailscale "
                          "(https://tailscale.com) or move both machines onto "
                          "the same LAN, then retry.")
    print(json.dumps(out))
    sys.exit(0 if private else 1)


def _export_network(cls, ip):
    if cls == "tailscale":
        return "-network 100.64.0.0 -mask 255.192.0.0"
    net = ipaddress.ip_network(f"{ip}/24", strict=False)
    return f"-network {net.network_address} -mask {net.netmask}"


def cmd_plan(args):
    try:
        ip, cls = resolve_host(args.host, args.ip)
    except (socket.gaierror, ValueError) as e:
        sys.exit(f"ERROR: cannot resolve {args.host}: {e}")
    if cls == "public":
        sys.exit("ERROR: remote IP is public — refusing to plan an NFS export. "
                 "(See: nfs-helper.py probe)")
    local = str(Path(args.folder).expanduser().resolve())
    if not Path(local).is_dir():
        sys.exit(f"ERROR: local folder {local} does not exist")
    remote_path = args.remote_path or local
    mp = mount_point_for(args.host, local)
    devmac = socket.gethostname()
    today = datetime.date.today().isoformat()
    netspec = _export_network(cls, ip)

    print(f"# NFS-via-symlink plan — {local} → {args.host} (remote class: {cls})")
    print(f"# Steps 1-2 run ON THIS MAC (sudo); steps 3-5 run ON {args.host} (sudo).")
    print(f"# Drive via an interactive box session so the user can enter passwords.")
    print()
    print(f"# 1. THIS MAC — export the folder (append once to /etc/exports):")
    print(f"echo '{local} -rw -mapall={USER_REMOTE} {netspec}' | sudo tee -a /etc/exports")
    print(f"# 2. THIS MAC — start/refresh nfsd:")
    print(f"sudo nfsd enable && sudo nfsd restart && showmount -e localhost")
    print(f"# 3. REMOTE — create mount point + mount:")
    print(f"sudo mkdir -p '{mp}'")
    print(f"sudo mount -t nfs -o resvport,rw {devmac}:{local} '{mp}'")
    print(f"# 4. REMOTE — move aside any pre-existing content, then symlink:")
    print(f"if [ -e '{remote_path}' ] && [ ! -L '{remote_path}' ]; then "
          f"mv '{remote_path}' '{remote_path}.old.{today}'; fi")
    print(f"mkdir -p '{os.path.dirname(remote_path)}' && ln -sfn '{mp}' '{remote_path}'")
    print(f"# 5. VERIFY (remote): ls '{remote_path}/' shows this Mac's live content.")
    print(f"# 6. Record it:  nfs-helper.py record {args.host} '{local}' --mount-point '{mp}'")


def cmd_record(args):
    data = read_yaml(HOSTS_PATH)
    hosts = data.setdefault("hosts", {})
    entry = hosts.setdefault(args.host, {})
    mode = entry.get("mode")
    if mode and mode != "nfs":
        sys.exit(f"ERROR: {args.host} already has sync mode '{mode}' — one mode "
                 f"per host; run that mode's teardown first.")
    local = str(Path(args.folder).expanduser().resolve())
    entry["mode"] = "nfs"
    folders = entry.setdefault("nfs", {}).setdefault("folders", [])
    for f in folders:
        if f["local"] == local:
            print(json.dumps({"ok": True, "noop": True, "folder": f}))
            return
    rec = {"local": local, "remote": args.remote_path or local,
           "mount_point": args.mount_point,
           "recorded": datetime.datetime.now().isoformat(timespec="seconds")}
    folders.append(rec)
    write_yaml(HOSTS_PATH, data)
    print(json.dumps({"ok": True, "host": args.host, "mode": "nfs", "folder": rec}))


def cmd_status(args):
    data = read_yaml(HOSTS_PATH)
    entry = data.get("hosts", {}).get(args.host)
    if not entry or entry.get("mode") != "nfs":
        print(json.dumps({"host": args.host, "mode": (entry or {}).get("mode")}))
        return
    out = {"host": args.host, "mode": "nfs", "folders": []}
    for f in entry["nfs"]["folders"]:
        res = subprocess.run(
            ["ssh"] + SSH_OPTS + [f"{USER_REMOTE}@{args.host}",
                                  f"mount | grep -F {f['mount_point']!r}"],
            capture_output=True, text=True)
        mounted = res.returncode == 0 and bool(res.stdout.strip())
        out["folders"].append({**f, "mounted": mounted})
    print(json.dumps(out))


def cmd_teardown_plan(args):
    data = read_yaml(HOSTS_PATH)
    entry = data.get("hosts", {}).get(args.host)
    if not entry or entry.get("mode") != "nfs":
        sys.exit(f"ERROR: {args.host} has no nfs mode configured")
    print(f"# NFS teardown plan for {args.host} — sudo on both sides; files not deleted.")
    for f in entry["nfs"]["folders"]:
        print(f"# REMOTE:")
        print(f"rm '{f['remote']}'   # removes the symlink only")
        print(f"sudo umount '{f['mount_point']}' && sudo rmdir '{f['mount_point']}'")
        print(f"# THIS MAC — remove the /etc/exports line for {f['local']}, then:")
        print(f"sudo nfsd restart")
    print(f"# Then clear the record:  python3 -c \"import yaml,pathlib; "
          f"p=pathlib.Path('{HOSTS_PATH}'); d=yaml.safe_load(p.read_text()); "
          f"del d['hosts']['{args.host}']; p.write_text(yaml.safe_dump(d))\"")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("probe", help="Classify the remote's network (exit 1 if public)")
    p.add_argument("host")
    p.add_argument("--ip", help="override resolution (testing)")
    p.set_defaults(fn=cmd_probe)

    p = sp.add_parser("plan", help="Emit the exact sudo command sequence (never executes)")
    p.add_argument("host")
    p.add_argument("folder")
    p.add_argument("--remote-path")
    p.add_argument("--ip", help="override resolution (testing)")
    p.set_defaults(fn=cmd_plan)

    p = sp.add_parser("record", help="Write hosts.yaml after the plan was applied")
    p.add_argument("host")
    p.add_argument("folder")
    p.add_argument("--mount-point", required=True)
    p.add_argument("--remote-path")
    p.set_defaults(fn=cmd_record)

    p = sp.add_parser("status", help="Mode + folders + live mount probe")
    p.add_argument("host")
    p.set_defaults(fn=cmd_status)

    p = sp.add_parser("teardown-plan", help="Emit the teardown command sequence")
    p.add_argument("host")
    p.set_defaults(fn=cmd_teardown_plan)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
