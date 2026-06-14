---
description: "`/move` relocates an anchor folder to a new path and updates every path-dependent system that indexes it — HookAnchor, Claude Code session history, hardcoded paths inside the anchor's own configs, …"
---
# /Move
`/move` relocates an anchor folder to a new path and updates every path-dependent system that indexes it — HookAnchor, Claude Code session history, hardcoded paths inside the anchor's own configs, the slug index, and any published docs. Use it when you say "move this anchor" or "relocate the project." It uses `mv` rather than `cp` (never `cp` — duplicate files break Obsidian wiki-link resolution silently) and stages a safety-net zip of the source at the old location until you've verified the move worked end-to-end.

| -[[SKL Move]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Anchor]] → [SKL Move](hook://p/SKL%20Move)<br>: the `/move` skill |
| --- | --- |
| Related | [[skills/move/SKILL.md\|SKILL]],   |
| [[SKL Move Design\|Design]] |  |

The skill walks through eight steps: zip + move, rename the Claude Code session folder, reindex HookAnchor, grep for hardcoded old-path references in CLAUDE.md / justfile / pyproject / etc., rebuild docs if published, update the slug index, verify the anchor opens cleanly at the new location, then delete the backup zip. Git remotes and Obsidian relative wiki-links keep working without intervention.
