---
description: "test strategy"
---
# HBR Testing
How Harbor is verified, layer by layer.

| -[[HBR Testing]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[HBR]] → [[HBR Design]] → [HBR Testing](hook://p/HBR%20Testing)<br>: test strategy |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Architecture]],   |

## Strategy
Test each pipeline at the cheapest tier that proves it works, then one end-to-end pass over the whole (tiers per [[DSC verification]]).

## Tests
- **Ingest — Tier 1 (agent-immediate)** — `cargo test ingest`: scan a fixture folder, assert the catalog row count and that two identical files fold to one entry.
- **Serve — Tier 1** — `cargo test serve`: request a byte range; assert direct play for an h264 fixture and a transcode for an unsupported codec.
- **Operate — Tier 2 (agent-over-time)** — a nightly job restores the latest backup into a temp dir and asserts the catalog opens.
- **End-to-end — Tier 4 (user)** — `harbor scan ./fixtures && harbor serve`, then play a title from a phone on the LAN.
