---
description: "`exp` is the remote-experimentation toolkit — it lets you run ML workloads on ephemeral GPU instances (typically vast.ai) without juggling SSH sessions and rsync invocations by hand."
---
# /Exp
`exp` is the remote-experimentation toolkit — it lets you run ML workloads on ephemeral GPU instances (typically vast.ai) without juggling SSH sessions and rsync invocations by hand. You set up a named remote once with `exp init`, then `exp exe "cmd"` does a full round-trip: pushes your experiment folder up, runs the command via a tmux watcher daemon, polls for completion, and pulls the filtered results back (pngs, csvs, logs, checkpoints). Multi-remote by default — every command takes `-r <name>` and the configs live in `~/.config/exp/`.

| -[[SKL Exp]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Utility]] → [SKL Exp](hook://p/SKL%20Exp)<br>: the SKL Exp doc |
| --- | --- |
| Related | [[skills/exp/SKILL.md\|SKILL]],   |
| [[SKL Exp Design\|Design]] |  |

`exp` is a CLI tool you invoke directly (`exp init`, `exp exe`, `exp status`, `exp zap`, etc.) rather than a slash-command — see `exp --help` for the full subcommand list. The **`exp zap <folder>`** pattern dispatches an experiment folder + instructions to an autonomous Claude Code worker pane on a named remote, which is the workflow you'll use most. Critical rule: **never use raw `tmux` or `ssh` against EXP sessions** — always go through `exp` subcommands (cleanup is `exp health --fix`, restart is `exp init`, etc.). Raw tmux commands have destroyed worker contexts and terminal windows before.
