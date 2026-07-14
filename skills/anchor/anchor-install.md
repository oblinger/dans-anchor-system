
# anchor-install — wire the anchor CLI tools
*(action file of [[anchor/SKILL|/anchor]]; formerly the standalone `/install` skill — folded in per F234 Q1=A, 2026-07-14)*

One-time per-machine setup that wires the anchor system's command-line scripts onto the user's `$PATH` so they can be invoked from any shell.

Install the anchor CLI tools so they're available from any shell.

## When to Use

First-time setup of a new machine, or after adding new anchor tools.

## What Gets Installed

The command-line tools live as scripts in the anchor skill's `scripts/` folder. This skill wires them so they can be invoked from any shell.

| Command | Script | Description |
|---------|--------|-------------|
| `cab-scan` | cab-scan.py | Discover all anchors, write to `~/.config/skl/anchors.yaml` |
| `cab-config` | cab-config.py | Manage `.skl/config.yaml` anchor orchestration |
| `skl-stat` | stat.py | Activity status tracking across projects |
| `cab-maintain` | maintain-check.py | Run maintenance checks (file triggers, event triggers) |
| `cab-audit` | audit/scripts/cab-audit.py | Audit anchor structure against CAB type rules |

## Workflow

1. **Ask the user** where they keep user-installed command-line tools on this machine — typically a directory on `$PATH`. The specifics depend on the user's environment; different machines have different conventions, and this skill defers to the user on placement.
2. **Wire the scripts** — symlink (or copy, per user preference) each script from the skills folder into the chosen location.
3. **Verify** — run each command with `--help` to confirm it's discoverable on `$PATH`.

## Adding New Tools

When a new anchor script is created, list it in the table above. Run `/install` again to wire the new tool.

## Skill-specific install steps

Beyond wiring CLI tools, some skills need per-machine setup — e.g., MUSE (F019) needs a launchd LaunchAgent installed to run its background sweep. The convention: each such skill ships an `install-<thing>.sh` script under its own `scripts/` directory, idempotent, safe to re-run.

Current installers:

| Skill | Script | Purpose | Detects |
|-------|--------|---------|---------|
| `muse` | `~/.claude/skills/muse/scripts/install-launchd.sh` | Write + bootstrap `com.oblinger.muse-ingest` LaunchAgent that routes MUSE's sweep through `_trust muse-sweep` | `command -v _trust` — skips silently if absent (interactive `/muse` still works) |

Run these directly on any machine where you want the background daemon. When we have 3+ FDA-gated daemons, a `das install <skill>` wrapper will iterate this table (F019 Q2 deferred).
