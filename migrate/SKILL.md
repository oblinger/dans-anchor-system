---
name: migrate
description: >
  Migrate an anchor — change its RID, traits, location, or structure.
  Use when the user says: "migrate this", "rename the RID", "change the type",
  "move this project", "restructure this anchor", "convert to code project".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Migrate

Change an anchor's identity, location, or structure. The user specifies what to change and the skill intelligently reorganizes.

## What can be migrated

| Change | What happens |
|--------|-------------|
| **RID** | Rename all {RID}-prefixed files, folders, wiki-links, config, frontmatter |
| **Location** | Move the anchor folder, update HookAnchor registration, breadcrumbs, symlinks |
| **Traits** | Add/remove traits — create/remove trait-required files and folders |
| **Claude session** | Move the `.claude/projects/` session config to match new path |

## Steps

1. Read `.anchor/config.yaml` to get current state
2. Ask the user what to change (if not specified in the command)
3. Compute the diff: what files/links/config need to change
4. Show the plan to the user — wait for approval
5. Execute: use `anchor-mv` for file renames, update config, update HookAnchor
6. Verify: run `/code rewire` to ensure everything is wired correctly

## Related

- `/code rewire` — repairs structure without changing identity
- `/cab migrate-claude` — specifically migrates the Claude Code session config
- `anchor-mv` — the script that handles wiki-link-safe file moves
