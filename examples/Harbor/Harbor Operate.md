---
description: "Harbor's operate pipeline — keeps the server healthy and recoverable."
---

# Harbor Operate
The operate pipeline — backs up the catalog and watches the server's health.

| -[[Harbor Operate]]- | → [HBR](hook://HBR) → [Harbor Operate](hook://p/Harbor%20Operate)<br>: a group container page — the Operate pipeline's three modules |
| --- | --- |
| Anchor | [[Harbor Components]] (parent) |
| Related | [[Harbor Ingest]] (sibling group),  [[Harbor Serve]] (sibling group), |
| [[Harbor Backup\|Backup]] | snapshots the catalog database and config on a schedule |
| [[Harbor Metrics\|Metrics]] | samples throughput, cache hit-rate, and transcode load |
| [[Harbor Alerts\|Alerts]] | fires notifications when a metric crosses its threshold |
| ... |  |
