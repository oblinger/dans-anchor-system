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
OB_SKILLS_GLOBAL = Path.home() / ".config" / "ob-skills" / "global.yaml"
CLAUDE_HOME = Path.home() / ".claude"
XDG_CONFIG = Path.home() / ".config"
PROJECTS_DIR = CLAUDE_HOME / "projects"
MEMORY_FOLDER_ID = "claude-memory"
HELPER = Path(__file__).parent / "syncthing-helper.py"
USER = "oblinger"
SSH_OPTS = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]

# Memory dirs live at the harness-standard path projects/<key>/memory/.
# The ignore file admits ONLY those; transcripts and the rest of the
# projects tree never cross (F159 — invariant moved to the ignore layer).
MEMORY_STIGNORE = "!/*/memory\n!/*/memory/**\n*\n"


def get_vault_root():
    """vault_root from ob-skills global.yaml — the single source of truth
    for 'where the vault is' (F159). Missing => loud failure, no fallback."""
    g = read_yaml(OB_SKILLS_GLOBAL)
    vr = g.get("vault_root")
    if not vr:
        sys.exit(f"ERROR: vault_root not set in {OB_SKILLS_GLOBAL} — "
                 "claude bridge derives the vault sync path from it (F159).")
    return str(Path(vr).expanduser())


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


def sync_paths(env):
    """vault_root (implicit first entry, F159) + any additional config paths."""
    return [get_vault_root()] + [p for p in env.get("sync", []) or []]


def sync_coverage(host):
    """Which claude_environment sync paths are covered by a sync-bridge for host."""
    env = get_manifest()
    hosts = read_yaml(HOSTS_PATH).get("hosts", {})
    he = hosts.get(host, {})
    covered = set()
    if he.get("mode") == "syncthing":
        for f in he.get("syncthing", {}).get("folders", []):
            covered.add(f.get("local"))
    out = []
    for p in sync_paths(env):
        out.append({"path": p, "covered": p in covered})
    return out


def memory_share_recorded(host):
    he = read_yaml(HOSTS_PATH).get("hosts", {}).get(host, {})
    return any(f.get("folder_id") == MEMORY_FOLDER_ID
               for f in he.get("syncthing", {}).get("folders", []))


def setup_memory_share(host):
    """F159 — bidirectional Syncthing share over ~/.claude/projects, ignore-
    filtered to */memory/** on BOTH devices. Idempotent via hosts.yaml record."""
    if memory_share_recorded(host):
        return {"memory": "already recorded — skipping setup"}

    # .stignore must be in place on both sides BEFORE the share exists, so the
    # first scan never offers transcripts. It is per-device (never synced).
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECTS_DIR / ".stignore").write_text(MEMORY_STIGNORE)
    subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{host}",
                    f"mkdir -p ~/.claude/projects && printf '%s' '{MEMORY_STIGNORE}' > ~/.claude/projects/.stignore"],
                   check=True, capture_output=True)

    share = subprocess.run(
        [sys.executable, str(HELPER), "share", "--host", host,
         "--folder", str(PROJECTS_DIR), "--folder-id", MEMORY_FOLDER_ID,
         "--local-mode", "sendreceive", "--remote-mode", "sendreceive"],
        capture_output=True, text=True)
    if share.returncode != 0:
        sys.exit(f"ERROR: memory share creation failed: {share.stderr.strip()[:300]}")

    # record preserves device ids only if we pass them back (its args are
    # authoritative) — read the existing pair out of hosts.yaml first.
    st = read_yaml(HOSTS_PATH).get("hosts", {}).get(host, {}).get("syncthing", {})
    rec = subprocess.run(
        [sys.executable, str(HELPER), "record", "--host", host,
         "--folder", str(PROJECTS_DIR), "--folder-id", MEMORY_FOLDER_ID,
         "--local-id", st.get("device_id_local", ""),
         "--remote-id", st.get("device_id_remote", ""),
         "--move-aside", "(none — ignore-filtered memory share, F159)"],
        capture_output=True, text=True)
    return {"memory": "share created (sendreceive both sides, memory-only ignore)",
            "share": share.stdout.strip()[:200],
            "recorded": rec.returncode == 0}


def cmd_plan(args):
    env = get_manifest()
    ch = env.get("claude_home", {})
    cf = env.get("config_home", {})
    print(json.dumps({
        "host": args.host,
        "vault_root": get_vault_root(),
        "sync_coverage": sync_coverage(args.host),
        "memory": {
            "mode": env.get("memory", "off"),
            "share_recorded": memory_share_recorded(args.host),
            "mechanism": f"Syncthing folder {MEMORY_FOLDER_ID} over {PROJECTS_DIR}, ignore-filtered to */memory/**",
        },
        "claude_home": {
            "source": str(CLAUDE_HOME),
            "include": ch.get("include", []),
            "exclude": ch.get("exclude", []),
        },
        "config_home": {
            "source": str(XDG_CONFIG),
            "include": cf.get("include", []),
            "exclude": cf.get("exclude", []),
        },
        "note": "transcripts never travel — memory dirs are the only projects/ content that syncs (F159).",
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

    def rsync_items(source_root, items, excl, dest_root):
        out = []
        for item in items:
            src = source_root / item
            if not src.exists():
                out.append({"item": item, "result": "skipped — not present locally"})
                continue
            rsync = [
                "rsync", "-az", "--delete",
                "-e", f"ssh {' '.join(SSH_OPTS)}",
            ]
            for ex in excl:
                rsync += ["--exclude", ex]
            # Trailing slash on dir sources so contents land at <dest>/<item>/
            if src.is_dir():
                rsync.append(f"{src}/")
                rsync.append(f"{dest_root}{item}/")
            else:
                rsync.append(str(src))
                rsync.append(f"{dest_root}{item}")
            r = subprocess.run(rsync, capture_output=True, text=True)
            out.append({
                "item": item,
                "result": "ok" if r.returncode == 0 else f"rsync exit {r.returncode}",
                "stderr": r.stderr.strip()[:200] if r.returncode != 0 else "",
            })
        return out

    results = rsync_items(CLAUDE_HOME, includes, excludes, dest)

    # ob-skills config provisioning (F159) — one-way, authored on the dev machine.
    cf = env.get("config_home", {})
    cf_results = []
    if cf.get("include"):
        subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}", "mkdir -p ~/.config"],
                       check=False, capture_output=True)
        cf_results = rsync_items(XDG_CONFIG, cf["include"], cf.get("exclude", []),
                                 f"{USER}@{target_host}:~/.config/")

    # Memory share (F159) — bidirectional, ignore-filtered to memory dirs.
    memory_result = {"memory": "off (claude_environment.memory != shared)"}
    if env.get("memory", "off") == "shared":
        memory_result = setup_memory_share(args.host)

    print(json.dumps({
        "host": args.host,
        "via": target_host,
        "provisioned": results,
        "config_home_provisioned": cf_results,
        "excluded": excludes,
        **memory_result,
    }, indent=2))


def shared_index_has_no_transcripts():
    """Walk the claude-memory folder's GLOBAL Syncthing index (local REST) and
    confirm no .jsonl entry exists anywhere in it. Reuses syncthing-helper."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sth", str(HELPER))
    if spec is None or spec.loader is None:
        sys.exit(f"ERROR: cannot load syncthing helper at {HELPER}")
    sth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sth)
    key = sth.get_local_apikey()
    tree = sth.st_call(key, "GET", f"/rest/db/browse?folder={MEMORY_FOLDER_ID}")

    def walk(entries):
        for e in entries or []:
            name = e.get("name", "")
            if name.endswith(".jsonl"):
                return False
            if not walk(e.get("children")):
                return False
        return True

    return walk(tree)


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
    # Transcripts correctly NOT shared? (F159) The remote runs claude and
    # legitimately writes its OWN transcripts, so "no jsonl on remote" is the
    # wrong invariant. The right one: no .jsonl ever enters the shared
    # Syncthing index — checked from the local global index. Without a memory
    # share, fall back to the original empty-projects check.
    env = get_manifest()
    if env.get("memory", "off") == "shared":
        checks["memory_share_recorded"] = memory_share_recorded(args.host)
        checks["transcripts_excluded"] = shared_index_has_no_transcripts()
    else:
        r = subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}",
                            "ls ~/.claude/projects 2>/dev/null | head -1"],
                           capture_output=True, text=True)
        checks["transcripts_excluded"] = (r.stdout.strip() == "")
    # ob-skills config landed? (F159)
    r = subprocess.run(["ssh", *SSH_OPTS, f"{USER}@{target_host}",
                        "ls ~/.config/ob-skills/global.yaml 2>/dev/null && echo OK"],
                       capture_output=True, text=True)
    checks["ob_skills_present"] = "OK" in r.stdout
    print(json.dumps({"host": args.host, "checks": checks,
                      "twin_ready": checks["skills_present"] and checks["transcripts_excluded"]},
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
