---
name: code
description: >
  Development workflow skill — planning, architecture, implementation, testing, release, and orchestration.
  Use with an action argument: /code plan, /code architect, /code mint, /code test, /code release, etc.
  Key sub-skills:
  /code delegate (parallel work dispatch — "delegate this", "fan out"),
  /code spike (aggressive root cause — "spike that bug"), /code bugfix (red-green bug response),
  /code forge (rebuild+restart), /code rewire (structural repair), /code replan (requirements changed),
  /code ask-questions (resolve pending decisions), /code research (investigate landscape).
  When the user says "new feature", "spike that bug", "fix this bug", "forge it", "rewire this", invoke the corresponding /code action.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Dev — Development Workflow

The unified development skill. Invoke with an action to run a workflow.

## Actions

| #   | Usage                 | File                   | Description                                                                   |
| --- | --------------------- | ---------------------- | ----------------------------------------------------------------------------- |
|     | **1x Plan** *(moved to `/design` per F120)* |                        | *Planning verbs live under `/design` — see [[design]]*                            |
| 11  | `/code anchor`         | [[code-anchor]]         | Create project anchor, all doc files, wire dispatch tables                    |
| 13  | `/code research`       | [[code-research]]       | Investigate landscape: tools, prior art, approaches                           |
| 16  | `/code plan-audit`     | [[code-plan-audit]]     | Completeness check on the plan                                                |
|     | **2x Architect**      |                        | *Agent designs the full system on paper — high-level moved to [[design-architect]]* |
| 22  | `/code modules`        | [[code-modules]]        | Files doc + per-module docs with interfaces                                   |
| 23  | `/code test-plan`      | [[code-test-plan]]      | Test design document: areas, scaffolds, categories                            |
| 25  | `/code arch-audit`     | [[code-arch-audit]]     | Architecture completeness check                                               |
|     | **3x Implement**      |                        | *Build features iteratively*                                                  |
| 29  | `/feature`             | (top-level skill)       | Feature lifecycle: design doc → agree → implement → test → done               |
| 30  | `/mint`                | (top-level skill)       | Orchestrator: spec → code → test → review → verify → commit                   |
| 31  | `/code spec`           | [[code-spec]]           | Write implementation spec for a roadmap milestone                             |
| 32  | `/code code`           | [[code-code]]           | Implement according to spec, self-check, update docs                          |
| 33  | `/code test`           | [[code-test]]           | Test advisor and developer: scaffolds, priorities, proof                      |
| 34  | `/code bugfix`         | [[code-bugfix]]         | Red test first, then spike — mandatory for every bug                          |
| 35  | `/code review`         | [[code-review]]         | Code review: correctness, anti-patterns, architecture                         |
| 36  | `/code verify`         | [[code-verify]]         | Run tests, produce completion proof                                           |
|     | **4x Release**        |                        | *Package, publish, distribute*                                                |
| 40  | `/code release`        | [[code-release]]        | Orchestrator: changelog → version → package → publish → ship                  |
| 41  | `/code changelog`      | [[code-changelog]]      | Generate changelog from commits (TBD)                                         |
| 42  | `/code version`        | [[code-version]]        | Bump version numbers (TBD)                                                    |
| 43  | `/code package`        | [[code-package]]        | Build distributable artifacts (TBD)                                           |
| 44  | `/code publish`        | [[code-publish]]        | Publish project page to oblinger.github.io                                    |
| 45  | `/code ship`           | [[code-ship]]           | Tag, push, announce (TBD)                                                     |
|     | ***Capabilities***    |                        |                                                                               |
|     | **5x Test**           |                        | *Dedicated testing pass*                                                      |
| 50  | `/code test`           | [[code-test]]           | Orchestrator: assess → scaffold → write → verify                              |
| 51  | `/code test-assess`    | (in dev-test)          | Read source, existing tests, git history                                      |
| 52  | `/code test-scaffold`  | [[code-test-scaffolds]] | Build or extend kitchen sink                                                  |
| 53  | `/code test-verify`    | (in dev-test)          | Run suite, completion proof, red-green at level 6+                            |
|     | **6x Verify**         |                        | *Validate structure and docs*                                                 |
| 60  | `/rewire`              | (top-level skill)       | Idempotent structural repair — wire dispatch tables, link files               |
| 61  | `/cab lint`           | [[cab-lint]]           | Validate anchor structure and module docs                                     |
|     | **7x Adapt**          |                        | *When requirements or design changes*                                         |
| 70  | `/code ask-questions`  | [[code-ask-questions]]  | Surface, track, and resolve open questions                                    |
| 71  | `/code replan`         | [[code-replan]]         | Selective replanning when requirements change                                 |
|     | **8x Tactical**       |                        | *On demand during development*                                                |
| 80  | `/code forge`          | [[code-forge]]          | Full rebuild + teardown + restart cycle                                       |
| 81  | `/code spike`          | [[code-spike]]          | Root cause diagnosis — 4 levels from standard debug to aggressive elimination |
| 82  | `/code mac-gui`        | [[code-mac-gui]]        | Drive a native Mac app (click/type/screenshot) to debug UI — use on demand   |
| 83  | `/code refactor`       | (TBD)                  | Extract, restructure, simplify code                                           |
|     | **9x Orchestrate**    |                        | *How to coordinate agents and branches*                                       |
| 90  | `/code delegate`       | [[code-delegate]]       | Parallel work dispatch — subagents, worktrees, grouping, backlog-for-merge    |
| 91  | `/code workers`        | [[code-workers]]        | Dispatch and manage worker agents                                             |
| 92  | `/code worktrees`      | [[code-worktrees]]      | Parallel git worktrees (TBD)                                                  |
| 92  | `/code pr-flow`        | [[code-pr-flow]]        | PR-based review workflow                                                      |
| 93  | `/code merge`          | [[code-merge]]          | Merge and conflict resolution (TBD)                                           |

## Topics

| File | When to read |
|------|-------------|
| [[code-ios]] | Project targets iOS |
| [[code-test-scaffolds]] | When planning or building test scaffolds |
| [[code-test-quality]] | When reviewing tests or self-checking |
| [[code-test-external]] | When testing code with OS/network/external dependencies |

## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory (`~/.claude/skills/dev/`) and execute its workflow
4. If no argument or unrecognized argument, show the Actions table above

## Adjacent Claude Code built-ins

Claude Code ships several **atomic-verb** built-in skills that overlap thematically with `/code` but operate at a different altitude. `/code <verb>` is **workflow orchestration** (multi-step plan → mint → test → release); the built-ins are **single-shot operations** the workflow can invoke or the user can call directly.

| Built-in | When to reach for it directly |
|---|---|
| `code-review` | Review the current diff for bugs / cleanups at a given effort level. Use directly when you have a diff to review without a full workflow context. |
| `simplify` | Quality-only review of changed code (reuse, simplification, efficiency, altitude). Subset of `code-review`. |
| `verify` | Confirm a code change actually does what it claims by running the app. `/code test` covers automated tests; `verify` covers "does it actually work end-to-end." |
| `run` | Launch and drive the project's app to see a change working. |
| `review` | Review a GitHub pull request (PR-shaped, not local-diff-shaped). |
| `security-review` | Security-focused review of pending changes. |
| `init` | Initialize a new `CLAUDE.md` for an existing codebase. |

**Rule of thumb:** if you're in the middle of `/code mint` or `/code release`, the workflow may invoke these as steps. If you just want one of them on its own, invoke it directly.
