---
name: dev
description: >
  Development workflow skill — planning, execution, setup, and replanning.
  Use with an action argument: /dev setup, /dev plan, /dev execute, /dev replan.
  Also contains reference topics for domain-specific development concerns.
tools: Read, Write, Edit, Bash, Glob, Grep, Task
user_invocable: true
---

# Dev — Development Workflow

The unified development skill. Invoke with an action to run a workflow, or read the topic files for domain-specific guidance.


## Planning Flow

See [[dev-plan]] for the full workflow. Six steps built in order:
1. PRD → 2. UX Design → 3. System Design → 4. Files + Module Docs → 5. Roadmap → 6. Document
- Open Questions accumulate from any stage, resolved in batches, cascaded back.
- Document step creates the dispatch tree so every doc is reachable from the anchor page.


## Execution Loop

See [[dev-execute]] for details. On each `next`, work on the highest-priority item that has actionable work:

1. **Unblock Workers** — Review PRs, merge, dispatch new workers
2. **Legwork** — User feedback, roadmap updates, doc fixes, backlog items
3. **Spec Work** — Write implementation specs for upcoming roadmap items
4. **Rescan** — Design consistency, docs vs code, surface decisions


## Actions

Each action is defined in a sub-file. When invoked, read the corresponding file and execute its workflow.

| Usage          | File             | Description                                                                                         |
| -------------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| `/dev plan`    | [[dev-plan]]    | 6-step planning flow: PRD, UX, System Design, Files+Modules, Roadmap, Document                      |
| `/dev execute` | [[dev-execute]] | Execution loop: Unblock Workers → Legwork → Spec Work → Rescan |
| `/dev replan`  | [[dev-replan]]  | Selective replanning when requirements change or design gaps surface                                |
| `/dev setup`   | [[dev-setup]]   | Interactive dev environment setup: project type → component selection → file creation               |
| `/dev forge`   | [[dev-forge]]   | Full rebuild + teardown + restart cycle for the running app                                         |
| `/dev publish` | [[dev-publish]] | Publish a project page to oblinger.github.io — splash, docs, downloads                             |

## Topics

Reference files for domain-specific development. Read when relevant to the current project.

| File | When to read |
|------|-------------|
| [[dev-ios]] | Project targets iOS |
| [[dev-testing]] | Testing principles, live test conventions |

## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory (`~/.claude/skills/dev/`) and execute its workflow
4. If no argument or unrecognized argument, show the usage block above
