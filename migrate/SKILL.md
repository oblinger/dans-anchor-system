---
name: migrate
description: >
  Change anything about an anchor — slug, traits, location, structure, naming, organization.
  Use when the user says: "migrate this", "rename the slug", "change the type",
  "move this project", "restructure this", "convert to code project",
  "reorganize", "rename", "change".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Migrate

Change anything about an anchor. The user specifies what to change and the skill intelligently reorganizes.

## Safety Rule

**Never delete. Never lose.** Files may be moved to parallel locations where the user will find them, but nothing is deleted and nothing is moved to a location the user wouldn't expect.

## What can be migrated

| Change | What happens |
|--------|-------------|
| **slug** | Rename all {slug}-prefixed files, folders, wiki-links, config |
| **Location** | Move the anchor folder, update HookAnchor, breadcrumbs, symlinks |
| **Traits** | Add/remove traits — create trait-required files and folders |
| **Structure** | Reorganize folders, move files to standard locations |
| **Naming** | Rename files to match conventions (kebab-case, Title Case) |
| **Claude session** | Move `.claude/projects/` config to match new path |

## Runbook

1. Read `.anchor` file (or frontmatter) to get current state
2. Ask the user what to change (if not specified in the command)
3. Compute the diff: what files/links/config need to change
4. Show the plan to the user — wait for approval
5. Execute: use `anchor-mv` for file renames, update config, update HookAnchor
6. Verify: run `/rewire` to ensure everything is wired correctly
