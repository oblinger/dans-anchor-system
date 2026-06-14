---
description: "`/wp <name>` creates a new dated **work product** folder inside the current anchor's `{slug} WP/` folder."
---
# /WP
`/wp <name>` creates a new dated **work product** folder inside the current anchor's `{slug} WP/` folder. Work products are the polished outputs of human+agent collaboration — papers, reports, analyses, presentations, spreadsheets — distinct from agent-generated Outputs and informal Log notes. Use it when you say "new work product," "new wp," or "create a wp."

| -[[SKL WP]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Anchor]] → [SKL WP](hook://p/SKL%20WP)<br>: the `/wp` skill |
| --- | --- |
| Related | [[skills/wp/SKILL.md\|SKILL]],   |
| [[SKL WP Design\|Design]] |  |

The skill asks you three things up front (name, brief description, type — markdown / paper / report / slides / spreadsheet), then creates a dated folder `{date} {name}/` with an anchor file inside (`{date} {name}.md`) that describes the work product and links to the deliverable. For markdown / paper / report types, the deliverable file is created directly; for slides and spreadsheet types, the anchor file points you to `/io slides` or `/io sheets` to create the Google asset. The WP dispatch page is updated newest-first, and the anchor file opens automatically so you can start writing.
