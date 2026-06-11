#!/usr/bin/env python3
"""bridge claude — provision a remote host as a Claude environment-twin.

The `bridge claude` GOAL: make <host> able to run a Claude instance as a twin
of this machine. Composes two things:

  1. Content  — the folders in config.yaml `claude_environment.sync` must be
     carried by a sync-bridge (Syncthing). This helper checks hosts.yaml and
     reports which sync folders are/aren't covered (it does NOT auto-init sync;
     that's `bridge sync`, which has its own move-aside confirmation gate).
  2. ~/.claude — rsync `claude_environment.claude_home` include MINUS exclude
     to the remote. Skills + CLAUDE.md + settings travel; transcripts
     (projects/) are a HARD exclude — high-churn, bidirectional-conflict-prone,
     and carry stale machine-local references. Fresh sessions on the twin.

Subcommands:
  plan   --host H            Show what would be provisioned (dry-run).
  apply  --host H [--bridge-ip IP]   Do it: rsync ~/.claude include−exclude.
  verify --host H            Confirm skills landed + projects/ did NOT.

Reads ~/.config/bridge/{config,hosts}.yaml. rsync runs over --bridge-ip when
given (fast Thunderbolt/LAN link), else over the hostname.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. Install: pip3 install pyyaml")

CONFIG_DIR = Path.home() / ".config" / "bridge"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
HOSTS_PATH = CONFIG_DIR / "hosts.yaml"
CLAUDE_HOME = Path.home() / ".claude"
USER = "oblinger"
SSH_OPTS = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]


def read_yaml(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_manifest():
    cfg = read_yaml(CONFIG_PATH)
    env = cfg.get("claude_environment", {})
    if not env:
        sys.exit("No claude_environment in ~/.config/bridge/config.yaml — nothing to provision.")
    return env


def sync_coverage(host):
    """Which claude_environment.sync paths are covered by a sync-bridge for host."""
    env = get_manifest()
    hosts = read_yaml(HOSTS_PATH).get("hosts", {})
    he = hosts.get(host, {})
    covered = set()
    if he.get("mode") == "syncthing":
        for f in he.get("syncthing", {}).get("folders", []):
            covered.add(f.get("local"))
    out = []
    for p in env.get("sync", []):
        out.append({"path": p, "covered": p in covered})
    return out


def cmd_plan(args):
    env = get_manifest()
    ch = env.get("claude_home", {})
    print(json.dumps({
        "host": args.host,
        "sync_coverage": sync_coverage(args.host),
        "claude_home": {
            "source": str(CLAUDE_HOME),
            "include": ch.get("include", []),
            "exclude": ch.get("exclude", []),
        },
        "note": "projects/ excluded by design — fresh sessions on the twin; transcripts never travel.",
    }, indent=2))


def cmd_apply(args):
    env = get_manifest()
    ch = env.get("claude_home", {})
    includes = ch.get("include", [])
    excludes = ch.get("exclude", [])
    if not includes:
        sys.exit("claude_home.include is empty — nothing to rsync.")

    target_host = args.bridge_ip or args.host
    dest = f"{USER}@{target_host}:~/.claude/"

    # Ensure remote ~/.claude exists
    subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}", "mkdir -p ~/.claude"],
                   check=False, capture_output=True)

    # Report sync coverage (warn, don't block)
    cov = sync_coverage(args.host)
    uncovered = [c["path"] for c in cov if not c["covered"]]
    if uncovered:
        print(f"⚠️  content NOT yet covered by a sync-bridge for {args.host}:", file=sys.stderr)
        for p in uncovered:
            print(f"     {p}  — run `bridge sync {args.host}` to mirror it", file=sys.stderr)

    results = []
    for item in includes:
        src = CLAUDE_HOME / item
        if not src.exists():
            results.append({"item": item, "result": "skipped — not present locally"})
            continue
        rsync = [
            "rsync", "-az", "--delete",
            "-e", f"ssh {' '.join(SSH_OPTS)}",
        ]
        for ex in excludes:
            rsync += ["--exclude", ex]
        # Trailing slash on dir sources so contents land at ~/.claude/<item>/
        if src.is_dir():
            rsync.append(f"{src}/")
            rsync.append(f"{dest}{item}/")
        else:
            rsync.append(str(src))
            rsync.append(f"{dest}{item}")
        r = subprocess.run(rsync, capture_output=True, text=True)
        results.append({
            "item": item,
            "result": "ok" if r.returncode == 0 else f"rsync exit {r.returncode}",
            "stderr": r.stderr.strip()[:200] if r.returncode != 0 else "",
        })
    print(json.dumps({
        "host": args.host,
        "via": target_host,
        "provisioned": results,
        "excluded": excludes,
    }, indent=2))


def cmd_verify(args):
    target_host = args.bridge_ip or args.host
    checks = {}
    # skills landed?
    r = subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}",
                        "ls ~/.claude/skills/bridge/SKILL.md 2>/dev/null && echo OK"],
                       capture_output=True, text=True)
    checks["skills_present"] = "OK" in r.stdout
    # CLAUDE.md landed?
    r = subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}",
                        "ls ~/.claude/CLAUDE.md 2>/dev/null && echo OK"],
                       capture_output=True, text=True)
    checks["claude_md_present"] = "OK" in r.stdout
    # projects/ correctly NOT provisioned?
    r = subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}",
                        "ls ~/.claude/projects 2>/dev/null | head -1"],
                       capture_output=True, text=True)
    checks["projects_excluded"] = (r.stdout.strip() == "")
    print(json.dumps({"host": args.host, "checks": checks,
                      "twin_ready": checks["skills_present"] and checks["projects_excluded"]},
                     indent=2))


def main():
    p = argparse.ArgumentParser(prog="claude-provision.py", description=__doc__)
    sp = p.add_subparsers(dest="cmd", required=True)
    for name, fn in [("plan", cmd_plan), ("apply", cmd_apply), ("verify", cmd_verify)]:
        s = sp.add_parser(name)
        s.add_argument("--host", required=True)
        s.add_argument("--bridge-ip", help="fast-link IP to rsync over (Thunderbolt/LAN)")
        s.set_defaults(func=fn)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
