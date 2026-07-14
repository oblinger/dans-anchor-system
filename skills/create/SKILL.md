---
name: create
description: >
  Create a new thing — anchor, feature, work product, spec, rule.
  Use when the user says: "create a new", "set up", "start a new", "new project",
  "new feature", "new work product", "new wp", "create a wp", "new rule".
  Requires an argument: /create anchor, /create feature, /create wp, /create spec, /create rule.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Create
requires:: skill:code, skill:feature, skill:rule
subsystem:: [[DAS Anchor Design]] — the Anchor group's subsystem profile

Dispatch skill that routes `/create <thing>` to the right creation runbook. The anchor and work-product runbooks are this skill's own action files; features, specs, and rules delegate to their owning skills.

| Usage | Runbook | Description |
|-------|---------|-------------|
| `/create anchor` | [[create-anchor]] | New anchor — folder structure, `.anchor`, dispatch tables, HookAnchor registration |
| `/create wp` | [[create-wp]] | New dated work-product folder inside `{slug} WP/` |
| `/create feature` | `/feature` | New feature design doc in the Features folder |
| `/create spec` | `/code spec` | New implementation spec for a milestone |
| `/create rule` | `/rule create` | New project rule |

(`/wp` was folded in as the `wp` action per [[F234 — Subsystem profiles — joint architecture overview per group (Phoenix prerequisite)|F234]] Q1=A, 2026-07-14 — the runbook is unchanged, only the entry point moved.)
