---
description: How to use the development workflow — from planning through implementation and release
---

# SKL Dev Guide (Skill: [[code/SKILL]])

The Dev skill is a 9-stage development lifecycle covering everything from initial planning to release and orchestration. Each stage has numbered actions (10s for Plan, 20s for Architect, 30s for Implement, etc.) that can be invoked individually or run as part of a larger orchestration flow.

The most common entry points are `/code feature` for building something new, `/code bugfix` for fixing a bug (red test first, always), and `/code spike` for aggressive root-cause diagnosis. For greenfield projects, start with `/code plan` which walks through PRD, UX, and system design before any code is written.

The Dev skill integrates with other skills: CAB for project structure, Rule for constraint checking, and stat for tracking activity status. Feature work follows a lifecycle: design doc, agreement, implementation, testing, done — with stat entries tracking progress.

## Commands

| Command | Description |
|---------|-------------|
| `/code plan` | Full planning pass: anchor, PRD, UX, system design, audit |
| `/code architect` | Architecture pass: system design, modules, test plan, roadmap |
| `/code mint` | Implementation pass: spec, code, test, review, verify, commit |
| `/code feature` | Feature lifecycle: design doc, agree, implement, test, done |
| `/code bugfix` | Red test first, then spike — mandatory for every bug |
| `/code spike` | Root cause diagnosis — 4 levels from standard to aggressive |
| `/code forge` | Full rebuild + teardown + restart cycle |
| `/code rewire` | Structural repair — wire dispatch tables, link files |
| `/code modules` | Create/update per-module documentation |
| `/code delegate` | Parallel work dispatch — subagents, worktrees, grouping |
| `/code release` | Release pass: changelog, version, package, publish, ship |
| `/code test` | Test pass: assess, scaffold, write, verify |
| `/code replan` | Selective replanning when requirements change |
| `/code open-questions` | Surface and resolve pending design decisions |

## Key Concepts

- **9-stage lifecycle** — Plan (1x), Architect (2x), Implement (3x), Release (4x), Test (5x), Verify (6x), Adapt (7x), Tactical (8x), Orchestrate (9x)
- **Feature lifecycle** — The `/code feature` flow is the primary way to build things: propose a design doc, get user agreement, then implement
- **Bugfix discipline** — Every bug fix starts with a red test. No exceptions. Then spike the root cause
- **Forge** — Tear everything down and rebuild. Use when the system is in a confused state
- **Delegate** — Fan out work to parallel agents or worktrees. The orchestration layer for large projects
- **No implementation without approval** — New features must be proposed and approved before coding begins
