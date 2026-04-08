# Anchor Setup

Create a new project anchor with the correct type, all required doc files, and wired dispatch tables. This is the first step before any planning begins.

## When to Use

When starting a new project or formalizing an existing codebase into the anchor system. Run before `/code prd`.

## Workflow

This delegates to `/cab setup` (the [[cab-create]] skill), which handles:

1. Gather information — type, name, parent, description, RID
2. Create the full file skeleton — ALL doc files upfront (PRD, System Design, Discussion, Roadmap, etc.)
3. Wire all dispatch tables — every file linked from its parent
4. Register with HookAnchor
5. Verify with `cab-lint --level 3`

After the anchor is created, return to `/code plan` to continue with the PRD step.

## Why Delegate to CAB

Anchor creation is a CAB concern — it's about folder structure, naming conventions, and dispatch tables. The dev skill provides the development lifecycle; CAB provides the project structure. Keeping them separate means anchor creation stays consistent whether invoked from `/code plan`, `/cab setup`, or directly.
