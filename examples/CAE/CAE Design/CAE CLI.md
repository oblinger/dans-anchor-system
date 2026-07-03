---
description: "command reference — every command, flag, exit code"
---

:>> [[CAE]] → [[CAE Design]]

# CAE CLI

![[CAE CLI Help.svg|1119]]

*(Help figure — source `CAE CLI Help.txt`, rendered by `cli-help-svg.py`. Edit the `.txt` and regenerate; the SVG fixes the geometry so the aligned `# comments` never re-wrap.)*

For a tutorial introduction, see [[CAE User Guide]]. Only the commands whose flags aren't obvious from the block are detailed below.

## Notes

- **submit** — `--deadline` (ISO-8601) required; `--retry N` default 3; `--priority 0–9` default 5 (higher runs sooner among the same deadline). The command to run follows a literal `--`. Prints the task id on success (`# → t-4f2`); exit 2 if the scheduler is unreachable.
- **status** — `--filter` one of `pending | running | done | failed`; `--json` for scripting. Default output is a table (`ID  STATE  DEADLINE  COMMAND`).
- **pause / resume** — both idempotent; in-flight tasks always run to completion. Design: [[F001 — Scheduler Pause]].

## Environment variables

| Variable | Purpose |
|----------|---------|
| `CAE_CONFIG` | Alternate config file. Default `~/.example-project/config`. |
| `CAE_DB` | SQLite task store. Default `~/.example-project/tasks.db`. |
| `NO_COLOR` | Suppress ANSI color (set to any value). |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success. |
| 1 | Usage error — bad flags, missing args, invalid values. |
| 2 | Runtime error — scheduler down, DB locked, permission. |
| 64 | Configuration error — invalid config file. |
