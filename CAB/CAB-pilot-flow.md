# cab-pilot-flow — Top-Down Design Then Implementation

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
