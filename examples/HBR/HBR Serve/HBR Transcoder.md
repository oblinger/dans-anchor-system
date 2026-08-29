---
description: "a leaf component — the serve transcoder"
---

| -[[HBR Transcoder]]- | : a leaf component — the serve transcoder<br>→ [[DAS]] → [[FEX]] → [[HBR\|HARBOR]] → [[HBR Serve]] → [HBR Transcoder](hook://p/HBR%20Transcoder)  |
| --- | --- |
| Anchor | [[HBR Serve]] (parent) |
| Related | [[HBR Streamer]] (caller),  [[HBR Cache]] (output sink), |
| ... |  |

# HBR Transcoder
The fallback stage of serve — makes a file playable on a client that cannot play it as stored.

The Transcoder takes a catalog file and a target profile (container, video codec, audio codec, resolution ceiling) and produces a segmented stream the client can play. It encodes just ahead of the playhead rather than the whole file, so a seek does not wait on minutes of unused output, and every finished segment is written to the Cache before it is handed back to the Streamer.
