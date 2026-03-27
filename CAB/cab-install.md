# Install — Set Up CAB Tools

Install CAB command-line tools into the user's environment.

## When to Use

First-time setup of a new machine, or after adding new CAB tools.

## What Gets Installed

Symlinks from `~/bin/` to scripts in the CAB skill folder (`~/.claude/skills/CAB/`):

| Command | Script | Description |
|---------|--------|-------------|
| `cab-scan` | cab-scan.py | Discover all anchors, write to ~/.config/skl/anchors.yaml |
| `cab-config` | cab-config.py | Manage .skl/config.yaml anchor orchestration |
| `skl-stat` | stat.py | Activity status tracking across projects |
| `cab-maintain` | maintain-check.py | Run maintenance checks (file triggers, event triggers) |
| `cab-lint` | LINT/cab-lint.py | Lint anchor structure against CAB type rules |

## Workflow

### 1. Ensure ~/bin exists and is on PATH

```bash
mkdir -p ~/bin
# Verify ~/bin is in PATH (should already be via .zshrc or .bash_profile)
```

### 2. Create symlinks

```bash
ln -sf ~/.claude/skills/CAB/stat.py ~/bin/skl-stat
ln -sf ~/.claude/skills/CAB/LINT/cab-lint.py ~/bin/cab-lint
```

### 3. Verify

```bash
stat --help
cab-lint --help
```

## Adding New Tools

When a new CAB script is created:
1. Add it to the table above
2. Add the symlink command to Step 2
3. Run `/cab install` to update
