---
description: "`/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine."
---

| -[[DAS Install]]- | : `/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Install](hook://p/DAS%20Install)  |
| --- | --- |
| Related | [[skills/install/SKILL.md\|SKILL]],   |
| [[DAS Install Design\|Design]]  |  |
| ... |  |

# DAS Install
`/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-audit`) onto a fresh machine. The skill asks the user where they keep user-installed tools (a directory on `$PATH`), then wires the scripts from `~/.claude/skills/` to that location, and verifies each one runs.

You run it once when setting up a new machine, and again whenever a new CAB script is added to the toolkit. It's strictly a system-level wiring step — no anchor work, no edits to your projects.
