---
description: "getting started"
---

| -[[HBR Guide]]- | : getting started<br>→ [[DAS]] → [[examples]] → [[HBR\|HARBOR]] → [[HBR User Docs\|HARBOR USER DOCS]] → [HBR Guide](hook://p/HBR%20Guide)  |
| --- | --- |
| Anchor | [[HBR User Docs]] (parent) |
| Related | [[HBR CLI]],   |
| ... |  |

# HBR Guide
Get Harbor from install to streaming in four steps.

1. **Install** — `cargo install harbor`.
2. **Configure** — write a `harbor.toml` with your watched roots and a catalog path.
3. **Scan** — `harbor scan` ingests your media into the catalog.
4. **Stream** — `harbor serve`, then open `http://<host>:8080` from any device on the LAN.

Check on it with `harbor status`; protect it with `harbor backup` (or let the scheduled backup run).
