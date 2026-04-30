---
description: How to control the local environment — browser, shell sessions, and system interaction
---

# SKL Ctrl Guide (Skill: [[ctrl/SKILL]])

The Ctrl skill manages interaction with the local macOS environment. It handles three main areas: browser automation (opening URLs, searching the web), persistent shell sessions (running commands that survive across conversations), and reading output from those sessions.

Most Ctrl actions are mapped to trigger words in CLAUDE.md. When you say "surf", "trot", or "outbox", the agent executes the corresponding command immediately without asking questions. This makes environment control feel like voice commands rather than multi-step workflows.

The underlying mechanism is `ctrl`, a Python script installed at `~/bin/ctrl`. It uses tmux for persistent sessions and Safari for browser automation.

## Commands

| Trigger Word | Command | Description |
|-------------|---------|-------------|
| **surf** `<url>` | `ctrl surf "<url>"` | Open URL in a new Safari tab |
| **trot** `<cmd>` | `ctrl trot "<cmd>"` | Run command in persistent tmux session |
| **outbox** | `ctrl outbox` | Read last 50 lines from the tmux session |
| (direct) | `ctrl search "<query>"` | Google search, optionally parse results |
| (direct) | `ctrl navigate "<url>"` | Navigate current Safari tab to a URL |
| (direct) | `ctrl outbox N` | Read last N lines from session |

## Key Concepts

- **Trigger words** — Saying "surf", "trot", or "outbox" causes immediate execution. No confirmation, no questions
- **Persistent sessions** — The tmux session (called "box") persists across Claude Code sessions. Commands you trot keep running
- **Working directory** — Always include `cd /path &&` before commands that need a specific directory, since tmux sessions don't inherit the agent's cwd
- **Search with parsing** — `ctrl search --results 5 "query"` returns structured results instead of just opening a browser tab
- **No raw tmux** — Always use `ctrl` subcommands rather than running tmux directly
