# Implement

Orchestrate the implementation phase — spec, code, test, review, verify, commit. Supports three modes depending on team size and workflow preference.

## Pipeline (per milestone)

| Step | Action | File | What it does |
|------|--------|------|-------------|
| 1 | Spec | [[code-spec]] | Write implementation spec for the milestone |
| 2 | Code | [[code-code]] | Implement according to the spec |
| 3 | Test | [[code-test]] | Write and run tests |
| 4 | Review | [[code-review]] | Check code quality and spec compliance |
| 5 | Verify | [[code-verify]] | Run full test suite, produce completion proof |
| 6 | Commit | — | Commit and push |

## Modes

### Solo

The pilot executes the full pipeline sequentially for each milestone. Simplest flow — one agent, one branch.

### Workers

The pilot specs milestones and dispatches them to worker agents (see [[code-workers]]). The pilot's job becomes:
1. **Spec** upcoming milestones to keep the worker pipeline full
2. **Review** completed worker PRs
3. **Unblock** workers when they have questions
4. **Merge** approved work

### Parallel

Multiple workers run simultaneously on independent milestones. The pilot manages the dispatch queue and resolves conflicts when workers' changes overlap. See [[code-pr-flow]] for the PR-based review cycle.

## Execution Loop

Always work on the highest-priority item that has actionable work, then re-evaluate:

1. **Unblock Workers** — review PRs, merge, dispatch new workers on fully-specced items
2. **Legwork** — autonomous tasks: integrate user feedback, update roadmap, doc fixes, backlog items
3. **Spec Work** — write specs for upcoming roadmap items whose dependencies are met
4. **Rescan** — check design consistency: docs vs code, intended vs actual, surface decisions

## The `next` Command

When the user types `next`, `'`, `crank`, or `end`:

1. **Assess** — walk the priority loop, identify the highest-priority actionable activity
2. **Execute autonomously** — take that action, keep going as long as there is clear forward progress
3. **Report on pause** — tell the user either a question that needs their answer, or the next actions the pilot would take

## Git Protocol

Commit after each well-defined piece of activity. Before pausing:
1. Commit any uncommitted work
2. Push all local commits
3. Merge ready PRs
4. Verify `git status` is clean

## Dispatch

On `/code it`: assess the roadmap, find the next milestone, and enter the pipeline. Default to solo mode unless the user specifies workers or parallel.
