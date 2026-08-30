---
description: "samples throughput, cache hit-rate, and transcode load"
---

| -[[HBR Metrics]]- | : a leaf component — the operate metrics<br>→ [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [[HBR Operate]] → [HBR Metrics](hook://p/HBR%20Metrics)  |
| --- | --- |
| Anchor | [[HBR Operate]] (parent) |
| Related | [[HBR Backup]] (source),  [[HBR Alerts]] (consumer), |
| ... |  |

# HBR Metrics
The operate pipeline’s instrument panel — the numbers that say whether the server is healthy.

Metrics samples the server on a fixed interval: bytes served, active sessions, cache hit-rate, transcoder queue depth and CPU load, catalog size, and the age of the newest backup. Samples are kept as a compact ring on disk and exposed on a local endpoint for the dashboard. Metrics only measures; deciding that a number is bad belongs to Alerts.
