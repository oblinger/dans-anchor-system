---
description: "Harbor's serve pipeline — delivers catalog media to clients."
---

# Harbor Serve
The serve pipeline — streams catalog media to players, transcoding on demand.

| -[[Harbor Serve]]- | → [HBR](hook://HBR) → [Harbor Serve](hook://p/Harbor%20Serve)<br>: a group container page — the Serve pipeline's three modules |
| --- | --- |
| Anchor | [[Harbor Components]] (parent) |
| Related | [[Harbor Ingest]] (sibling group),  [[Harbor Operate]] (sibling group), |
| [[Harbor Streamer\|Streamer]] | negotiates the session and pushes the byte range to the client |
| [[Harbor Transcoder\|Transcoder]] | re-encodes to a client-supported codec when direct play fails |
| [[Harbor Cache\|Cache]] | keeps hot transcoded segments on fast storage for reuse |
| ... |  |
