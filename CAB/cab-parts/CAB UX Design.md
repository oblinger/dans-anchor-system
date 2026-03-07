# CAB UX Design

The UX Design document (`{NAME} UX Design.md`) specifies the user-facing interface: screens, commands, output formats, and interaction flows. For CLI tools this covers command syntax and output; for GUI apps it covers screens and navigation. It contains the current spec — not rationale or alternatives.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK UX Design

| TOC |  |
| --- | --- |
| 1 | CLI Commands |
| 2 | Output Formats |
| 3 | Error Messages |



## 1 CLI Commands

| Command | Description |
|---------|-------------|
| `tsk schedule <cmd> --at <time>` | Schedule a task for a specific time |
| `tsk status` | Show all tasks grouped by state |
| `tsk cancel <id>` | Cancel a pending task |
| `tsk drain [--timeout <sec>]` | Wait for all tasks to complete |
| `tsk history [--limit <n>]` | Show completed task results |

### schedule
```
tsk schedule "python backup.py" --at "2026-03-01 02:00"
tsk schedule "npm test" --at "+30m" --priority high
```
The `--at` flag accepts absolute times (local, converted to UTC) or relative offsets (`+30m`, `+2h`).



## 2 Output Formats

### Status Output
```
PENDING  3 tasks
  #7  python backup.py          2026-03-01 02:00  priority:normal
  #8  npm test                  2026-03-01 02:30  priority:high
  #9  ./cleanup.sh              2026-03-01 03:00  priority:normal

RUNNING  1 task
  #6  make build                started 45s ago

COMPLETED  2 tasks (last 24h)
  #5  pytest tests/             exit:0  duration:12s
  #4  ./deploy.sh               exit:1  retries:3  FAILED
```

### JSON Output
All commands accept `--json` for machine-readable output.



## 3 Error Messages

| Situation | Message |
|-----------|---------|
| Invalid time | `error: cannot parse time "{input}" — use "YYYY-MM-DD HH:MM" or "+Nm/+Nh"` |
| Task not found | `error: no task with id {id}` |
| Drain timeout | `warning: drain timed out — {n} tasks still running` |

---



# Format Specification

## Location

`{NAME} UX Design.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Document Structure

### TOC
A table of contents at the top linking to major sections.

### Interface Sections
Organize by interaction surface:
- **CLI tools** — Commands table, detailed syntax per command, output format examples
- **GUI apps** — Screens, navigation flows, ASCII mockups or wireframe references
- **APIs** — Endpoint tables, request/response examples

### Output/Display Formats
Show exact output the user will see, using code blocks with realistic data.

### Error Messages
Table of error situations and their exact messages. Errors should be actionable — tell the user what went wrong and how to fix it.

## Lifecycle

- **Create** after the PRD user stories are stable enough to design interactions for
- **Update** when the interface changes — this is the current spec
- **Current spec only** — design rationale and alternatives belong in [[CAB Design Discussions]]
