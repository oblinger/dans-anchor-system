---
name: code
description: >
  Development workflow skill — planning, architecture, implementation, testing, release, and orchestration.
  Use with an action argument: /code plan, /code architect, /code it, /code test, /code release, etc.
  Key sub-skills: /code feature (feature lifecycle — "new feature", "let's build", "design a feature"),
  /code delegate (parallel work dispatch — "delegate this", "fan out"),
  /code spike (aggressive root cause — "spike that bug"), /code bugfix (red-green bug response),
  /code forge (rebuild+restart), /code rewire (structural repair), /code replan (requirements changed),
  /code open-questions (resolve pending decisions), /code research (investigate landscape).
  When the user says "new feature", "spike that bug", "fix this bug", "forge it", "rewire this", invoke the corresponding /code action.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Dev — Development Workflow

The unified development skill. Invoke with an action to run a workflow.

## Actions

| #   | Usage                 | File                   | Description                                                                   |
| --- | --------------------- | ---------------------- | ----------------------------------------------------------------------------- |
|     | **1x Plan**           |                        | *Design the system before writing code*                                       |
| 10  | `/code plan`           | [[code-plan]]           | Orchestrator: anchor → prd → ux → system → plan-audit...                      |
| 11  | `/code anchor`         | [[code-anchor]]         | Create project anchor, all doc files, wire dispatch tables                    |
| 12  | `/code prd`            | [[code-prd]]            | Product requirements: goals, user stories, constraints                        |
| 13  | `/code research`       | [[code-research]]       | Investigate landscape: tools, prior art, approaches                           |
| 14  | `/code ux`             | [[code-ux]]             | UX design: screens, commands, concepts, mockups                               |
| 15  | `/code system`         | [[code-system]]         | System conversation: language, components, state, deps                        |
| 16  | `/code plan-audit`     | [[code-plan-audit]]     | Completeness check on the plan                                                |
|     | **2x Architect**      |                        | *Agent designs the full system on paper*                                      |
| 20  | `/code architect`      | [[code-architect]]      | Orchestrator: system-design → modules → test-plan → roadmap → arch-audit      |
| 21  | `/code system-design`  | [[code-system-design]]  | Architecture doc: components, APIs, data models                               |
| 22  | `/code modules`        | [[code-modules]]        | Files doc + per-module docs with interfaces                                   |
| 23  | `/code test-plan`      | [[code-test-plan]]      | Test design document: areas, scaffolds, categories                            |
| 24  | `/code roadmap`        | [[code-roadmap]]        | Ordered milestones with acceptance criteria                                   |
| 25  | `/code arch-audit`     | [[code-arch-audit]]     | Architecture completeness check                                               |
|     | **3x Implement**      |                        | *Build features iteratively*                                                  |
| 29  | `/code feature`        | [[code-feature]]        | Feature lifecycle: design doc → agree → implement → test → done               |
| 30  | `/code it`      | [[code-it]]      | Orchestrator: spec → code → test → review → verify → commit                   |
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
| 60  | `/code rewire`         | [[code-rewire]]         | Idempotent structural repair — wire dispatch tables, link files               |
| 61  | `/cab lint`           | [[cab-lint]]           | Validate anchor structure and module docs                                     |
|     | **7x Adapt**          |                        | *When requirements or design changes*                                         |
| 70  | `/code open-questions` | [[code-open-questions]] | Surface, track, and resolve open questions                                    |
| 71  | `/code replan`         | [[code-replan]]         | Selective replanning when requirements change                                 |
|     | **8x Tactical**       |                        | *On demand during development*                                                |
| 80  | `/code forge`          | [[code-forge]]          | Full rebuild + teardown + restart cycle                                       |
| 81  | `/code spike`          | [[code-spike]]          | Root cause diagnosis — 4 levels from standard debug to aggressive elimination |
| 82  | `/code refactor`       | (TBD)                  | Extract, restructure, simplify code                                           |
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
