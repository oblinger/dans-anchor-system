---
name: exp
description: Remote-experimentation toolkit — runs ML workloads on ephemeral GPU instances (vast.ai) via SSH + rsync + watcher daemon. Multi-remote, with named workers and a zap dispatch pattern.
user_invocable: false
---

# EXP — Remote Experimentation

Bash-based toolkit for running ML experiments on ephemeral remote GPU instances. Manages SSH connections, file sync (rsync), command execution through a watcher daemon, and a worker-pane pattern for delegating experiment runs to autonomous Claude Code sessions.

EXP is a CLI tool, not a slash-command skill. Skills consume it transparently when they need remote execution; the user invokes it directly as `exp <subcommand>`.

## Contents

- **`scripts/exp`** — dispatcher (the binary you put on `$PATH`). Self-relative: sources `exp.sh` from its own directory.
- **`scripts/exp.sh`** — all subcommand implementations as shell functions. Must be sourced; never executed directly.
- **`scripts/exp-watcher.sh`** — daemon copied to each remote on `exp init`. Polls `/workspace/_run.cmd` and writes exit codes to `/workspace/_done`.
- **`docs/`** — user-facing flow docs (Master / Experiment / Orchestrator flows, Worker Instructions, Templates, Backlog, and a Claude-Code-specific `CLAUDE.md`).

## Install

The CLI lives at `scripts/exp` inside this skill. Wire it onto `$PATH` via symlink:

```bash
ln -sfn "$HOME/.claude/skills/exp/scripts/exp" ~/bin/exp
```

The wrapper resolves its own directory at runtime, so it works from any `$PATH` location as long as `exp.sh` and `exp-watcher.sh` sit next to it.

Worker-instructions symlink (read by `exp zap` worker sessions):

```bash
ln -sfn "$HOME/.claude/skills/exp/docs/EXP Worker Instructions.md" ~/.config/exp/exp-worker.md
```

## Quick reference

```bash
exp init <ip:port> -r <name>       # save remote, verify, start watcher
exp init "port root@ip" -r <name>  # vast.ai SSH-paste format
exp exe "cmd" [timeout] -r <name>  # full round-trip (push → run → pull)
exp push <folder> -r <name>        # rsync experiment folder up
exp pull <folder> -r <name>        # rsync results back
exp status [-r <name>]             # SSH + watcher + GPU + disk (1 SSH call)
exp health [-r <name>] [--fix]     # health report; --fix cleans stale state
exp check [lines] -r <name>        # tail remote tmux output
exp stop -r <name>                 # kill running command on remote
exp close -r <name>                # tear down watcher
exp list                           # show all configured remotes
exp default [<name>]               # show or set default remote
exp worker <name> --host "port root@ip"   # create/update worker (idempotent)
exp zap <folder> [instruction] -r <name>  # dispatch experiment to worker
exp teardown -r <name>             # full teardown (stop + config + tmux)
exp build                          # assemble deliverable ZIP
```

## Architecture (one paragraph)

`exp init` writes `~/.config/exp/<name>.conf` (host, port, local path, GPU info) and starts a tmux session on the remote running `exp-watcher.sh`. The watcher polls a command file and writes exit codes. `exp exe` rsyncs the experiment folder up, drops a command via SSH pipe (avoids quoting), polls completion every 2s, and rsyncs filtered results back. Each remote has independent config and its own watcher; commands take `-r <name>` (default `r1`). `exp worker` adds a Claude Code pane next to the watcher; `exp zap` dispatches an experiment folder + instructions into that pane.

Full flow docs: [[EXP Master Flow]], [[EXP Experiment Flow]], [[EXP Orchestrator Flow]], [[EXP Worker Instructions]].

## CRITICAL — never use raw tmux or ssh

**NEVER run `tmux kill-session`, `tmux send-keys`, `tmux kill-window`, or any raw tmux command against EXP sessions.**
**NEVER run raw `ssh` to an EXP remote.**

No exceptions — not for cleanup, restart, or testing. Raw tmux commands have destroyed user terminal windows and worker contexts before. Always use `exp` subcommands; if none fits, propose adding one rather than working around the toolkit.

- "Clean up workers" → `exp health --fix`, not `tmux kill-session`.
- "Restart a watcher" → `exp init -r <name>` (idempotent), not raw tmux/ssh.
- "Refresh worker Claude" → propose a new `exp` subcommand; don't kill the session.

## Conventions

- Experiment folders: `NNN_name/` (e.g., `001_mnist_mlp/`, `002b_row_shuffle/`). Templates in `docs/EXP Experiment Template.md`.
- Remote workspace: `/workspace` (everything synced lands here).
- Remote Python: `/venv/main/bin/python`.
- `exp pull` filters: png, csv, log, json, pt, safetensors, npy. `exp push` mirrors with `--delete`.
- SSH disables host-key checking (`StrictHostKeyChecking=no`) because vast.ai instances are ephemeral.

## See also

- `docs/CLAUDE.md` — when Claude Code is acting as EXP maintainer (monitoring, diagnostics, restarting watchers safely).
- [[F079 — Fleet]] — future streaming refactor of this architecture (pure-reader watcher, JSONL events).
