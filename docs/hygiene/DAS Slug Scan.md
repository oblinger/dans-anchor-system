---
description: "`/slug-scan` discovers anchors that have a slug (a short ID like `ODC`, `HA`, `SKA`) and syncs them into the slug index table at `~/ob/kmr/SYS/SYS Topic/slug/SLUG.md`."
---

| -[[DAS Slug Scan]]- | : `/slug-scan` discovers anchors that have a slug (a short ID like `ODC`, `HA`, `SKA`) and syncs them into the slug index table at `~/ob/kmr/SYS/SYS Topic/slug/SLUG.md`.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Slug Scan](hook://p/DAS%20Slug%20Scan)  |
| --- | --- |
| Related | [[skills/slug-scan/SKILL.md\|SKILL]],   |
| [[DAS Slug Scan Design\|Design]]  |  |
| ... |  |

# DAS Slug Scan
`/slug-scan` discovers anchors that have a slug (a short ID like `ODC`, `HA`, `SKA`) and syncs them into the slug index table at `~/ob/kmr/SYS/SYS Topic/slug/SLUG.md`. Use it when you say "slug scan" or "sync slugs" — typically after creating a new slugged anchor and you want it indexed.

The flow is: rescan HookAnchor (`ha --rescan`), then run `scan_tid.py delta` to find new slugs since the last index update, then paste the resulting table rows into the top (dated) table of `SLUG.md` in reverse-chronological order. Descriptions come from the anchor marker file's frontmatter `desc:` field — the marker file is authoritative, so if the table disagrees, update the table. Rules: **never delete slug rows** (only add or update), new entries go to the top table not the ROOT hierarchy, and you can regenerate the hierarchy with `scan_tid.py tree` whenever you need to.
