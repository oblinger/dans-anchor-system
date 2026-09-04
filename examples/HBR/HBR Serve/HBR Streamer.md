---
description: "negotiates the session and pushes the byte range to the client"
---

| -[[HBR Streamer]]- | : a leaf component — the serve streamer<br>→ [[DAS]] → [[FEX]] → [[HBR]] → [[HBR Serve]] → [HBR Streamer](hook://p/HBR%20Streamer)  |
| --- | --- |
| Anchor | [[HBR Serve]] (parent) |
| Related | [[HBR Transcoder]] (fallback stage),  [[HBR Cache]] (segment source), |
| ... |  |

# HBR Streamer
The front of the serve pipeline — answers a play request with bytes.

The Streamer negotiates the client session — codec support, bitrate ceiling, seek position — and then serves the requested byte range straight off the catalog file when the client can direct-play it. When it cannot, the Streamer hands the request to the Transcoder and streams the segments that come back, checking the Cache first so a segment already produced for another client is never encoded twice.
