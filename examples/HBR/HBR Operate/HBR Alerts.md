---
description: "a leaf component — the operate alerts"
---

| -[[HBR Alerts]]- | : a leaf component — the operate alerts<br>→ [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [[HBR Operate]] → [HBR Alerts](hook://p/HBR%20Alerts)  |
| --- | --- |
| Anchor | [[HBR Operate]] (parent) |
| Related | [[HBR Metrics]] (source),  [[HBR Backup]] (watched job), |
| ... |  |

# HBR Alerts
The operate pipeline’s voice — turns a bad number into a notification.

Alerts reads the Metrics stream and compares each sample against the thresholds in the config: transcoder queue above its limit, cache hit-rate below its floor, a backup older than its schedule allows, disk on a library root nearly full. A crossed threshold sends one notification through the configured channel and holds until the metric recovers, so a sustained problem is reported once rather than every sample.
