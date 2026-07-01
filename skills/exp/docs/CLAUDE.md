# CLAUDE.md

## What This Is

EXP is a bash-based toolkit for running ML experiments on ephemeral remote GPU instances (vast.ai). It manages SSH connections, file syncing (rsync), and command execution through a watcher daemon pattern. The system also supports delegating experiment execution to autonomous Claude Code worker sessions.

## Architecture

**`exp.sh`** — All commands are shell functions (not standalone scripts). Must be sourced before use: `source exp.sh`. The dispatcher script (at `scripts/exp` inside this skill, wired onto the user's `$PATH`) routes subcommands to these functions (e.g., `exp init` → `exp-init`).

**`exp-watcher.sh`** — Daemon that runs on the remote in a tmux session. Polls `/workspace/_run.cmd`, executes the command via `setsid`, writes exit code to `/workspace/_done`. The local `exp-exe` writes the command file and polls for completion.

**Execution flow (exp-exe):**
1. Auto-detects experiment folder from command (pattern: `NNN_name`, `QN_NN_name`, or `DNN_name`)
2. Rsyncs experiment folder to remote (excluding `output/`)
3. Writes command to `_run.cmd` on remote (via SSH pipe, avoids quoting issues)
4. Polls `_done` file every 2s, shows progress every 15s
5. Rsyncs results back (only: png, csv, log, json, pt, safetensors, npy)

**Multi-remote system:** Each remote is a named config in `~/.config/exp/<name>.conf` storing host, port, local path, and GPU info. All commands accept `-r <name>` (default: `r1`).

**Worker/zap pattern:** `exp worker <name>` creates a tmux session with remote watcher (top pane) and Claude Code (bottom pane). `exp zap <folder>` dispatches an experiment folder to the worker — it updates `EXP_LOCAL` to the project directory, refreshes the worker's CLAUDE.md, and sends the task. Workers read `~/.config/exp/exp-worker.md` for their protocol.

## Key Commands

```bash
source exp.sh                              # load all functions
exp init <ip:port> -r <name> -l <path>     # configure remote + start watcher
exp init "port root@ip" -r <name>          # vast.ai paste format
exp exe "cmd" [timeout] -r <name>          # full round-trip (push→run→pull)
exp push <folder> -r <name>                # rsync up
exp pull <folder> -r <name>                # rsync down (results only)
exp check [lines] -r <name>               # tail remote tmux output
exp status [-r <name>]                     # quick status: SSH, watcher, GPU, disk (1 SSH call)
exp health [-r <name>] [--fix] [--alert <pane>]  # health report (--fix cleans, --alert notifies)
exp stop -r <name>                         # kill running command on remote
exp close -r <name>                        # tear down watcher
exp worker <name> [--host ip:port]         # create/update worker (idempotent)
exp teardown -r <name>                     # full teardown: stop, remove config, kill tmux
exp zap <folder> [instruction] -r <name>   # dispatch experiment folder to worker
exp build                                  # ZIP experiments into deliverable bundle
```

## Experiment Conventions

- Experiment folders: `NNN_name/` (e.g., `001_mnist_mlp/`, `002b_row_shuffle/`)
- Each experiment has a lab notebook: `NNN_name/NNN_name.md` (using `experiment-template.md` format)
- Remote workspace: `/workspace` — all synced files land here
- Remote Python: `/venv/main/bin/python`
- Pull filters only grab result files (not code/data), push uses `--delete` (mirror)

## Important Implementation Details

- SSH options disable host key checking (`StrictHostKeyChecking=no`) since vast.ai instances are ephemeral
- Commands are sent to remote via `printf '%s\n' "$cmd" | ssh cat > _run.cmd` to avoid shell quoting problems
- The watcher runs commands via `setsid` so `exp stop` can kill the process group without killing the watcher
- `exp init` is idempotent — safe to call repeatedly; use `-f` to force teardown and re-init
- The hardcoded helpers path in `exp.sh` (`/Users/oblinger/ob/kmr/SYS/Bespoke/Remote Experimenter`) is used to push `exp-watcher.sh` to remotes
- `_exp-gather-remote()` makes ONE SSH call per remote to collect all monitoring data (PID, disk, GPU, watcher, tail) using `===SECTION===` markers — safe to run while experiments execute

## Maintainer Role

This Claude Code instance serves as the EXP system maintainer. Responsibilities:

- **Monitoring** — Run `exp status` and `exp health` to check on remotes. All monitoring is read-only and safe during active experiments.
- **Diagnostics** — When issues are detected (watcher down, disk low, stale commands), investigate using `exp check` and `exp health` before taking action.
- **Fixes** — Restart watchers with `exp init -r <name>` (idempotent). Kill stuck commands with `exp stop -r <name>`. Never use `-f` on a remote with an active experiment without user approval.
- **Protocol** — Always check `exp status` before any destructive action. Never interrupt running experiments. Report issues to the user with specific health check output.

## CRITICAL: Never Use Raw tmux or SSH

**🚨 NEVER run `tmux kill-session`, `tmux send-keys`, `tmux kill-window`, or ANY raw tmux command. 🚨**
**🚨 NEVER run raw `ssh` commands to remotes. 🚨**

This rule has NO exceptions — not for "cleanup", "fixing", "restarting", or testing. Raw tmux commands WILL destroy the user's terminal windows and worker contexts. This has already happened and caused data loss.

- Always use `exp` subcommands: `exp init`, `exp stop`, `exp close`, `exp worker`, `exp check`, `exp health`, etc.
- If no `exp` command exists for what you need, **stop and propose adding one** — do not work around the system.
- "Clean up workers" means `exp health --fix`, NOT killing tmux sessions.
- "Restart a watcher" means `exp init -r <name>`, NOT raw tmux/ssh.
- To refresh a worker Claude, propose an `exp` command for it — do not `tmux kill-session`.
