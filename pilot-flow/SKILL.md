---
name: pilot-flow
description: Top-down design then implementation flow — Iterates from PRD → System Design → Roadmap → implementation. Dispatches to /code skills as design phases complete. Use when user says: "pilot flow", "top-down development".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Pilot Flow — Top-down design then implementation

Top-down design-then-implementation orchestrator that dispatches PRD → System Design → Roadmap → implementation phases to the `/code` skills.

The pilot flow is defined in Claude Code skills. This action dispatches to them.

## Planning Phase

Invoke `/code plan` — 7-step planning flow:
PRD → Open Questions → UX Design → System Design → Files → Module Descriptions → Roadmap

## Execution Phase

Invoke `/code execute` — Implementation priority loop:
User Refinements → Worker Dispatch → Spec Next → Surface Decisions → Design Rescan → Wait

## Replanning

Invoke `/code replan` — Lightweight replanning when requirements change or design gaps surface.

## Role Definition

See `/role-pilot` for the pilot role definition, `next` command protocol, git protocol, and context pacing rules.
