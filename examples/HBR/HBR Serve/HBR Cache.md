---
description: "keeps hot transcoded segments on fast storage for reuse"
---

| -[[HBR Cache]]- | : a leaf component — the serve cache<br>→ [[DAS]] → [[FEX]] → [[HBR]] → [[HBR Serve]] → [HBR Cache](hook://p/HBR%20Cache)  |
| --- | --- |
| Anchor | [[HBR Serve]] (parent) |
| Related | [[HBR Streamer]] (reader),  [[HBR Transcoder]] (writer), |
| ... |  |

# HBR Cache
The serve pipeline’s segment store — transcoded output kept for the next request.

The Cache holds transcoded segments on the fastest storage the host has, keyed by catalog id and target profile, and evicts least-recently-served segments when it reaches its size budget. Two clients watching the same title at the same profile share one encode; a title that is popular this week stays resident, and one nobody plays ages out on its own.
