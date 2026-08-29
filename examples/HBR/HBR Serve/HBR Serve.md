---
description: "a group container page — the Serve pipeline's three modules"
---

| -[[HBR Serve]]- | : a group container page — the Serve pipeline's three modules<br>→ [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [HBR Serve](hook://p/HBR%20Serve)  |
| --- | --- |
| Anchor | [[HBR Components]] (parent) |
| Related | [[HBR Ingest]] (sibling group),  [[HBR Operate]] (sibling group), |
| [[HBR Streamer\|Streamer]]  | negotiates the session and pushes the byte range to the client |
| [[HBR Transcoder\|Transcoder]]  | re-encodes to a client-supported codec when direct play fails |
| [[HBR Cache\|Cache]]  | keeps hot transcoded segments on fast storage for reuse |
| ... |  |

# HBR Serve
The serve pipeline — streams catalog media to players, transcoding on demand.
