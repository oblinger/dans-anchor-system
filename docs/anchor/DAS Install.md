---
description: "`/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine."
---
# /Install
`/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine. The skill asks the user where they keep user-installed tools (a directory on `$PATH`), then wires the scripts from `~/.claude/skills/` to that location, and verifies each one runs.

| -[[DAS Install]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Install](hook://p/DAS%20Install)<br>: `/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine.|
| --- | --- |
| Related | [[skills/install/SKILL.md\|SKILL]],   |
| [[DAS Install Design\|Design]] |  |

You run it once when setting up a new machine, and again whenever a new CAB script is added to the toolkit. It's strictly a system-level wiring step — no anchor work, no edits to your projects.
