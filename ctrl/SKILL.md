---
name: ctrl
description: >
  Local environment control — browser automation, persistent shell sessions, and system interaction.
  Subcommands: box, outbox, surf, search, navigate, shell.
  Most subcommands are mapped to trigger words in CLAUDE.md.
tools: Bash
user_invocable: true
dependencies:
  - playwright>=1.40.0
---

# CTRL — Environment Control

Control the local macOS environment: browser automation, persistent tmux shell sessions, and system interaction.

| ACTIONS | Description |
| ------- | ----------- |
| `ctrl trot "<cmd>"` | Run command in persistent tmux session |
| `ctrl box "<cmd>"` | Alias for trot (backward compatible) |
| `ctrl outbox [N]` | Read last N lines from trot/box session (default: 50) |
| `ctrl surf "<url>"` | Open URL in new Safari tab |
| `ctrl search "<query>"` | Google search, optionally parse results |
| `ctrl navigate "<url>"` | Navigate current Safari tab to URL |
| `ctrl shell "<cmd>"` | Execute shell command in tmux |

## Trigger Words

These trigger words in CLAUDE.md map to ctrl subcommands:

| Trigger | Command |
|---------|---------|
| **trot** `<cmd>` | `ctrl trot "<cmd>"` |
| **outbox** | `ctrl outbox` |
| **surf** `<url>` | `ctrl surf "<url>"` |

## Usage

The script is at `~/.claude/skills/ctrl/ctrl.py`. It's also installed at `~/bin/ctrl`.

```bash
ctrl box "cd /path && make build"    # Run in persistent box session
ctrl outbox                          # See box output
ctrl outbox 100                      # Last 100 lines
ctrl surf "https://example.com"      # Open in Safari
ctrl search "Python docs"            # Google search
ctrl search --results 5 "query"      # Parse and return 5 results
ctrl search --json "query"           # JSON output
```

## Notes

- The `box` tmux session persists across Claude Code sessions
- Always include `cd /path &&` before commands that need a specific working directory
- `ctrl search --results N` parses Google results and returns them as structured data
