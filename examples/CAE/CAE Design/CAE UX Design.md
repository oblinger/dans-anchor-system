# CAE UX Design
description:: user-facing CLI surface — commands, output shape, error voice

| -[[CAE UX Design]]- | : Human CLI interface intent — commands, output shape, error voice, discovery.<br>→ [[KM]] → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [[CAE Design]] → [CAE UX Design](hook://p/CAE%20UX%20Design) |
| --- | --- |
| [[CAE PRD]] | parent PRD — user stories drive this design |
| [[CAE API Design]] | sibling — programmatic surface for crate embedders |
| [[CAE CLI]] | downstream — exhaustive flag/exit-code reference |
| [[CAB UX Design]] | facet spec this doc follows |

**TL;DR.**
- Audience: a developer at a terminal, typing or piping. Default output is for the eye; `--json` is for `jq`.
- Spine: 5 verbs — `schedule`, `status`, `history`, `cancel`, `drain` — cover the three CAE PRD stories.
- Output: human-readable grouped-by-state default + structured `--json` opt-in; the two must show the same data.
- Errors: terse `cae: <named-failure> — <hint>` envelope, exit codes from `sysexits.h`.
- Discovery: `cae --help` lists verbs in story-order; `cae <verb> --help` per-verb; `man cae` for the long form.

**Figure — annotated session.**

```
$ cae schedule "python backup.py" --at "+30m"           # ① relative time
scheduled T-042  at 2026-03-01 02:30                    #   → confirmation prints the assigned ID + resolved time

$ cae status                                            # ② grouped by lifecycle state, counts at the top
PENDING  2 tasks
  T-042  in 28m   python backup.py
  T-043  in 1h    npm test --ci
RUNNING  1 task
  T-040  for 4m   rsync -av /data /backup
DONE     1 task
  T-039  6m ago   ✓ python report.py (3.2s)

$ cae cancel T-042                                      # ③ explicit ID; named confirmation
cancelled T-042                                          #   exit 0; no further output

$ cae status --json | jq '.pending[].id'                # ④ structured opt-in for piping
"T-043"
```

## Audience

A developer working at a terminal in an interactive shell — typically scripting batch jobs (overnight backups, CI cleanups, scheduled report generation) on a personal workstation or a small server. They know shell idioms (`|`, `&&`, exit codes), they read output with their eyes by default, and they reach for `jq` when they want to script against `cae` output. They are **not** writing GUI clients; for that, the sibling [[CAE API Design]] covers the Rust crate form.

## Entry-points

The five verbs cover the three PRD stories and one operational concern (`drain`).

| Verb | Synopsis | Purpose | Source story |
|---|---|---|---|
| `cae schedule "<cmd>" --at <time>` | Submit a deferred task | Submit a shell command to run at a future time, optionally with priority + retry policy. | US-CAE-1 |
| `cae status [--state <s>]` | List tasks grouped by lifecycle state | At-a-glance view of pending / running / done / failed tasks. | US-CAE-2 |
| `cae history [--limit <n>]` | Reverse-chronological terminal-state tasks | Show what finished, what failed, retry counts, durations. | US-CAE-2, US-CAE-3 |
| `cae cancel <id>` | Cancel a pending task | Remove a task from the pending queue before it runs. | US-CAE-1 (implicit) |
| `cae drain [--timeout <sec>]` | Block until running tasks complete | Operational: wait for the queue to settle before shutdown. | Operational |

Time specs (`--at`) accept both absolute (`2026-03-01 02:00` — local, converted to UTC) and relative offsets (`+30m`, `+2h`, `+1d`).

## Output shapes

Two forms across every verb that emits content. The default is for the eye; the opt-in is for the pipe. **Both encode the same data** — `--json` is not a separate, richer view.

### Default — grouped by lifecycle state

For `cae status`:

```
PENDING  2 tasks
  T-042  in 28m   python backup.py
  T-043  in 1h    npm test --ci
RUNNING  1 task
  T-040  for 4m   rsync -av /data /backup
DONE     2 tasks
  T-039  6m ago   ✓ python report.py (3.2s)
  T-038  9m ago   ✓ pg_dump prod (24.1s)
FAILED   1 task
  T-037  12m ago  ✗ ./deploy.sh (exit 1, 3 retries)
```

Counts surface in the section header so a fast scan tells the user "what's about to run, what's running, what's done." Within each section, items are time-sorted (pending: soonest first; running: longest-running first; terminal: most recent first).

For `cae history`:

```
2026-03-01 03:12  T-039  ✓  python report.py        3.2s
2026-03-01 02:48  T-037  ✗  ./deploy.sh             exit 1, retries 3
2026-03-01 02:30  T-035  ✓  npm install             24.1s, retries 1
```

### Structured opt-in — `--json`

Every command that emits content accepts `--json`. Output is a single JSON document on stdout; no decorative whitespace, no banners. Shape mirrors the default output's grouping:

```json
{
  "pending": [
    {"id": "T-042", "command": "python backup.py", "scheduled_at": "2026-03-01T02:30:00Z", "priority": "normal"},
    {"id": "T-043", "command": "npm test --ci", "scheduled_at": "2026-03-01T03:00:00Z", "priority": "high"}
  ],
  "running": [
    {"id": "T-040", "command": "rsync -av /data /backup", "started_at": "2026-03-01T01:56:00Z"}
  ],
  "done": [
    {"id": "T-039", "command": "python report.py", "finished_at": "2026-03-01T01:54:00Z", "duration_ms": 3200, "exit_code": 0}
  ],
  "failed": [
    {"id": "T-037", "command": "./deploy.sh", "finished_at": "2026-03-01T01:48:00Z", "exit_code": 1, "retry_count": 3, "final_error": "deploy step 4 failed"}
  ]
}
```

Schema is stable per [[CAE API Design]] § Stability (the JSON output IS a programmatic surface even when emitted from the CLI; changes to its shape follow semver).

## Error voice

Tone: **terse, named, actionable**. Errors prefix with `cae:`, name the failure mode, hint the fix.

| Situation | Message | Exit code |
|---|---|---|
| Invalid time spec | `cae: cannot parse time "{input}" — use "YYYY-MM-DD HH:MM" or "+Nm" / "+Nh" / "+Nd"` | `EX_USAGE` (64) |
| Task ID not found | `cae: no task with id {id} — see 'cae history' for past tasks` | `EX_USAGE` (64) |
| Cannot reach store | `cae: cannot open task store at {path} — check permissions` | `EX_IOERR` (74) |
| Task already running (cancel) | `cae: task {id} already running — use 'cae drain' to wait for completion` | `EX_TEMPFAIL` (75) |
| Drain timed out | `cae: drain timed out — {n} tasks still running` (warning to stderr; exit 0 with `--soft`, `EX_TEMPFAIL` without) | `0` or `75` |
| Internal panic | `cae: internal error — please report at {repo}/issues with command: {cmd}` | `EX_SOFTWARE` (70) |

Exit codes follow `sysexits.h` conventions; full table in [[CAE CLI]] § Exit codes. Errors go to stderr; stdout stays clean for piping. Color is auto-disabled when stdout is not a TTY (so `cae status | grep` is grep-clean).

## Discovery

How a user encounters the surface for the first time:

- **`cae --help`** lists all five verbs in **story order** (not alphabetical), with a one-line synopsis each. The header is the one-paragraph CAE pitch from the PRD.
- **`cae <verb> --help`** is per-verb, exhaustive within that verb. Examples + every option.
- **`man cae`** is the long form — concept overview, exit code table, full flag reference. Generated from [[CAE CLI]] at build time.
- **First-run greeting**: invoked with no args, `cae` prints "usage: cae <verb> [args] — try 'cae --help'" and exits 64. Does NOT print a full help screen unsolicited.

The verb list is the load-bearing discovery surface. Adding a new verb means it appears in `cae --help` in its story-order slot; users discover it on the next `--help`.

## Design decisions

| ID | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| D-UX1 | Default output human-readable; `--json` for pipes | Always-JSON, always-pretty | Most usage is interactive at the terminal. Pipe-friendly is opt-in to keep the eye-readable form readable. |
| D-UX2 | Five flat top-level verbs (no `cae task schedule` form) | Subcommand grouping (`cae task <verb>`) | Memorability over taxonomy — top-level verbs read faster, especially with shell completion. |
| D-UX3 | Time specs accept both absolute and relative | Force one form | Different mental models for different tasks ("at 3am" vs "in 2 hours"); both are common; auto-detect by leading `+`. |
| D-UX4 | Group `status` by lifecycle state, not by ID | Flat list sorted by ID; sorted by time | Most common query is "what's about to run / what's running" — state grouping puts the answer at the top of the screen. |
| D-UX5 | Errors carry task ID + named cause | Generic "command failed" | Failures should be greppable and actionable. `cae: task T-042 failed after 3 retries — exit 127 (command not found)` tells the user where to look. |
| D-UX6 | First-run prints usage hint, not full `--help` | Print full help when args missing | Terse default reduces noise for the common typo (`cae stats` instead of `cae status`); user pulls full help on demand. |
| D-UX7 | Color auto-disabled when stdout is not a TTY | Always color; `--no-color` flag | Pipe-cleanliness is the default; users running interactively get color for free; no flag-flipping for common case. |

## See also

- [[CAE PRD]] — user stories that drive this design (US-CAE-1..3).
- [[CAE API Design]] — sibling facet covering the Rust crate's programmatic surface.
- [[CAE CLI]] — downstream reference (every flag, every exit code).
- [[CAE Architecture]] — system organization that produces this surface.
- [[CAB UX Design]] — facet spec; embedded [[#RULESET R-ux|R-ux]] ruleset.
