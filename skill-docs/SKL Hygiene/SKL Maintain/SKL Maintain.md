---
description: "`/maintain` is the discipline that keeps **derived files in sync with their sources** inside an anchor."
---
# /Maintain
`/maintain` is the discipline that keeps **derived files in sync with their sources** inside an anchor. You declare standing maintenance orders in `{NAME} Maintenance.md` — for example, "whenever `dev/SKILL.md` changes, copy the Actions table to the bottom of `DEV.md`" — and the system watches the source files for mtime changes. When something falls out of date, the maintain hook surfaces a "⚠ Maintenance needed" message and the skill runs the recorded actions to bring derived files back into sync.

| -[[SKL Maintain]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Hygiene]] → [SKL Maintain](hook://p/SKL%20Maintain)<br>: the SKL Maintain doc |
| --- | --- |
| Related | [[skills/maintain/SKILL.md\|SKILL]],   |
| [[SKL Maintain Design\|Design]] |  |

You reach for this when you say "maintain this," "keep things synced," or "add a maintenance entry for X." Triggers can be file paths (`./skills/dev/SKILL.md`, `./Code/src/**/*.rs`), event flags (`:pr`, `:commit`, `:daily`), and actions are `copy`, `check`, or `sync`. The hook check is cheap (~3ms per read) so it runs in the background; you only notice it when something actually needs attention.
