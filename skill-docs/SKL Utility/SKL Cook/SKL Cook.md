---
description: "`/cook <recipe>` (or `/cook <recipe> and <recipe> and ...`) answers the question \"what do I need to do before I start cooking?\" The skill looks up each recipe in your Paprika library, pulls its ing…"
---
# /Cook
`/cook <recipe>` (or `/cook <recipe> and <recipe> and ...`) answers the question "what do I need to do before I start cooking?" The skill looks up each recipe in your Paprika library, pulls its ingredients, and sorts them into four buckets: **Repurchase** (need to buy), **Verify** (probably have it but check), **Downstairs** (grab from basement storage), and **Remaining** (already on hand, grouped by category like Spices / Staples / Freezer). It uses `~/ob/kmr/Topic/Food/Food Categories.md` as the source of truth for what you keep where.

| -[[SKL Cook]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Utility]] → [SKL Cook](hook://p/SKL%20Cook)<br>: the SKL Cook doc |
| --- | --- |
| Related | [[skills/cook/SKILL.md\|SKILL]],   |
| [[SKL Cook Design\|Design]] |  |

After printing the four lists, the skill batches up its "I'm assuming you have these on hand" guesses (especially aggressive on spices) into a single confirmation prompt so you can rubber-stamp a whole pile of pantry items at once. Then it pushes the lists to a fresh Apple Reminders list named `Cook YYYY-MM-DD HH:MM` — one reminder per section, packed into the notes field — so you can take Repurchase / Verify / Downstairs into the store on your phone.
