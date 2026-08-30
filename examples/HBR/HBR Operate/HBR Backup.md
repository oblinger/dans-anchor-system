---
description: "snapshots the catalog database and config on a schedule"
---

| -[[HBR Backup]]- | : a leaf component — the operate backup<br>→ [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [[HBR Operate]] → [HBR Backup](hook://p/HBR%20Backup)  |
| --- | --- |
| Anchor | [[HBR Operate]] (parent) |
| Related |  |
| [[HBR Metrics]] | reports last-run age |
| [[HBR Alerts]] | fires on a missed run |
| ... |  |

# HBR Backup
The operate pipeline’s safety net — a nightly checkpoint of everything that is not media.

Backup snapshots the catalog database and the server config into the configured backup directory on the cron schedule in the config file, keeping a rolling window of dated copies. Media files are deliberately not included — they are large and already live on the library roots — so a restore is a copy of one small directory. The age of the newest snapshot is published to Metrics, and a schedule that is missed raises an alert.
