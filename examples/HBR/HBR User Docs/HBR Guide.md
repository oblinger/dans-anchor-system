---
description: "getting started"
---
# HBR Guide
Get Harbor from install to streaming in four steps.

| -[[HBR Guide]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[HBR]] → [[HBR User Docs]] → [HBR Guide](hook://p/HBR%20Guide)<br>: getting started |
| --- | --- |
| Anchor | [[HBR User Docs]] (parent) |
| Related | [[HBR CLI]],   |

1. **Install** — `cargo install harbor`.
2. **Configure** — write a `harbor.toml` with your watched roots and a catalog path.
3. **Scan** — `harbor scan` ingests your media into the catalog.
4. **Stream** — `harbor serve`, then open `http://<host>:8080` from any device on the LAN.

Check on it with `harbor status`; protect it with `harbor backup` (or let the scheduled backup run).
