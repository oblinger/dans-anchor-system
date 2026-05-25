---
name: install
description: Install CAB command-line tools — make stat, cab-config, cab-scan, cab-lint available from any shell. Run once per machine.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Install — Set up CAB tools

Install CAB command-line tools so they're available from any shell.

## When to Use

First-time setup of a new machine, or after adding new CAB tools.

## What Gets Installed

The CAB command-line tools live as scripts in the skills folder. This skill wires them so they can be invoked from any shell.

| Command | Script | Description |
|---------|--------|-------------|
| `cab-scan` | cab-scan.py | Discover all anchors, write to `~/.config/skl/anchors.yaml` |
| `cab-config` | cab-config.py | Manage `.skl/config.yaml` anchor orchestration |
| `skl-stat` | stat.py | Activity status tracking across projects |
| `cab-maintain` | maintain-check.py | Run maintenance checks (file triggers, event triggers) |
| `cab-lint` | LINT/cab-lint.py | Lint anchor structure against CAB type rules |

## Workflow

1. **Ask the user** where they keep user-installed command-line tools on this machine — typically a directory on `$PATH`. The specifics depend on the user's environment; different machines have different conventions, and this skill defers to the user on placement.
2. **Wire the scripts** — symlink (or copy, per user preference) each script from the skills folder into the chosen location.
3. **Verify** — run each command with `--help` to confirm it's discoverable on `$PATH`.

## Adding New Tools

When a new CAB script is created, list it in the table above. Run `/install` again to wire the new tool.
