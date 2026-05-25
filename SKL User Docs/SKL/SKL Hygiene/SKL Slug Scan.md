# /slug-scan

`/slug-scan` discovers anchors that have a slug (a short ID like `ODC`, `HA`, `SKA`) and syncs them into the slug index table at `~/ob/kmr/SYS/Closet/Tiny IDs/TID/TID.md`. Use it when you say "slug scan" or "sync slugs" — typically after creating a new slugged anchor and you want it indexed.

The flow is: rescan HookAnchor (`ha --rescan`), then run `scan_rid.py delta` to find new slugs since the last index update, then paste the resulting table rows into the top (dated) table of `TID.md` in reverse-chronological order. Descriptions come from the anchor marker file's frontmatter `desc:` field — the marker file is authoritative, so if the table disagrees, update the table. Rules: **never delete slug rows** (only add or update), new entries go to the top table not the ROOT hierarchy, and you can regenerate the hierarchy with `scan_rid.py tree` whenever you need to.
