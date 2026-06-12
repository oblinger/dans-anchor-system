
# EXP Orchestrator Flow

The lead is the main Claude Code session working directly with the user. It manages the research agenda, dispatches work to GPU workers, reviews results, and maintains the writeup.

For the research cycle process (Frame → Execute → Polish with pulse checks), see [[EXP Master Flow]]. For the worker's operating manual, see [[EXP Worker Instructions]]. For the full experiment lifecycle, see [[EXP Experiment Flow]]. For the deliverable format, see [[EXP Write Up Template]].

## After Every Context Compaction

**Re-read this file immediately after any context compaction.** The compaction summary preserves facts but loses process knowledge. Re-reading this flow ensures you follow the correct dispatch, monitoring, and review procedures rather than improvising.

## Reviewing Results — Never Show Raw Data

When an experiment completes, **do not** dump raw JSON, open individual plot files, or paste numerical tables into the conversation. The worker's job is to embed all plots and findings inline in the experiment spec. To review:

1. `peep` the experiment spec — that's it. The user sees findings and inline figures in one document.
2. Discuss with the user based on what they see in the spec.
3. If deeper investigation is needed, `peep` specific output files — but never paste raw results into the conversation.

## Role

The lead owns everything except step 3 (Run & Results) of the [[EXP Experiment Flow]], which it delegates to workers. Specifically:

- **Design** experiments (write specs from [[EXP Experiment Template]])
- **Dispatch** work to workers via `exp zap`
- **Monitor** remote health via `exp health`
- **Review** results with the user
- **Integrate** findings into the writeup
- **Maintain** the ROADMAP

## Active Project

The lead always needs to know the active project folder. You will be told what it is — if not, ask. The project folder contains:

- **ROADMAP.md** — backlog, ready queue, running, review queue, and full experiment history
- **writeup.md** — the deliverable being built
- **README.md** — project overview and experiment index

## The Roadmap

The ROADMAP is the lead's primary task list. It has five sections:

| Section | Meaning |
|---------|---------|
| **Backlog** | Ideas and tasks not yet designed (integration work, follow-ups) |
| **Ready** | Spec is written, experiment can be zapped immediately |
| **Running** | Currently delegated to a worker |
| **Review** | Worker done, needs lead + user review |
| **Roadmap** | Full history organized by research question |

Status markers: `[x]` done, `[~]` in progress, `[>]` delegated, `[ ]` not started.

## Dispatch Flow

When dispatching an experiment to a worker:

### 1. Pick from Ready queue
Check `ROADMAP.md` — the **Ready** section lists experiments with written specs that can be zapped immediately.

### 2. Check available workers
```bash
exp health
```
Look for remotes that are healthy and idle (no active task, or task done).

### 3. Zap
```bash
exp zap <project>/<experiment> -r <remote>
```
This points the worker at the experiment folder, updates the remote's local path to the project directory, refreshes the worker's CLAUDE.md, and sends the task with instructions to read the worker protocol fresh. No need to copy files — the worker operates directly on the project folder.

### 4. Update ROADMAP
Move the experiment from **Ready** to **Running**. Mark it `[>]` in the roadmap section.

## Monitoring

### Periodic health checks
```bash
exp health              # all remotes
exp health -r r1        # single remote
exp health --fix        # auto-clean stale files
exp health -w 60        # watch mode, refresh every 60s
```

### What to look for
- **Task done** (✓ in header) — worker filled in `_EXECUTION.md`. Move experiment to **Review** in ROADMAP.
- **Remote idle warning** — worker may be preparing, writing up, or stuck. Check with `exp check-zap -r <remote>`.
- **Stale _done** — leftover from interrupted command. Clean with `--fix`.
- **Disk low** — old experiment data accumulating. May need cleanup.

### When a task completes
1. Check `_EXECUTION.md` in the experiment's output folder — `completed:` field should be filled in
2. Read the execution summary
3. Read the updated experiment spec (the worker should have filled in Results, Key Findings, Discussion)
4. Move experiment from **Running** to **Review** in ROADMAP
5. Clear the task: `exp clear-task -r <remote>`

## Review Flow

Review one experiment at a time with the user:

1. **Open the spec** — `peep <experiment>/<experiment>.md` — figures are inline
2. **Discuss** — findings, surprises, whether it makes sense
3. **Note follow-ups** — add new experiment ideas to Backlog
4. **Update ROADMAP** — mark `[x]`, add result summary, update Key Findings
5. **Integrate** — pull findings into writeup.md (executive summary, relevant Key Findings section, Discussion)

## Designing New Experiments

When the user wants to investigate something new:

1. Pick the next experiment number in the appropriate question group (e.g., Q2_10 if Q2_09 exists)
2. Create the spec from [[EXP Experiment Template]]
3. Fill in: Goal, Approach, Dependencies, Expected Outcomes, Predictions
4. `peep` the spec for user review
5. Once approved, add to **Ready** in ROADMAP

## Key Commands

```bash
# Dispatch
exp zap <project>/<experiment> -r <remote> # dispatch experiment to worker
exp clear-task -r <remote>                 # clear completed task

# Monitor
exp health [-r name] [--fix]               # health report
exp check [lines] -r <remote>              # tail remote output
exp check-zap -r <remote>                  # check worker Claude output

# Manual intervention
exp exe "cmd" [timeout] -r <remote>        # run command on remote
exp push <folder> -r <remote>              # push files to remote
exp pull <folder> -r <remote>              # pull results from remote
exp stop -r <remote>                       # kill running command
```

## Boundaries

- **Never use raw tmux or ssh commands** — always use `exp` subcommands
- **Never interrupt a running experiment** without checking `exp health` first
- **Don't skip user review** — every completed experiment gets reviewed before integration
- **Keep ROADMAP current** — update at every lifecycle transition
- **One experiment per worker** — don't zap a new task until the previous one is cleared
