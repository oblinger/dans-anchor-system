---
description: "Maintain the vault-wide glossary and router — routing, never duplication."
---

| -[[DAS Atlas]]- | : Maintain the vault-wide glossary and router — routing, never duplication.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Atlas](hook://p/DAS%20Atlas)  |
| --- | --- |
| Related | [[skills/atlas/SKILL.md\|SKILL]],   |
| [[DAS Atlas Design\|Design]]  |  |
| ... |  |

# DAS Atlas
**Atlas** is the alphabetical glossary of every named thing in the vault — anchors, concepts, standards, tools, project codenames — and `/atlas` is what keeps it current. Each entry routes to the canonical source rather than restating it: if reading an entry answers the question without following a link, the entry is wrong and the content belongs at the target.

Invoke: `/atlas add <name>` to write a new entry in alphabetical position · `/atlas update <name>` to refine an existing one · bare `/atlas` to open it read-only.

Outputs: [[Atlas]] (`~/ob/kmr/SYS/Atlas/Atlas.md`) — the file is its own documentation.

Skill: [[atlas/SKILL|atlas/SKILL.md]] · Design: [[DAS Atlas Design]].

The disciplines the skill enforces, and the reason it exists rather than direct edits: routing not duplication, no guessable info, strictly alphabetical (never categorical), one paragraph per entry, and a maintained per-letter jump table. Direct writes to `Atlas.md` break these silently, which is why `R-pathguard-04` blocks them.
