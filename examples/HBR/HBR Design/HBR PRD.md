---
description: "product requirements"
---
# HBR PRD
Why Harbor exists and what its first version must deliver.

| -[[HBR PRD]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR PRD](hook://p/HBR%20PRD)<br>: product requirements |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR Roadmap]],  [[HBR Architecture]],   |

## Problem
A household's media — movies, shows, ripped music — is scattered across drives with no single way to browse or play it on a TV, phone, or laptop. Commercial servers are heavy, cloud-tied, or track the user.

## Users
One household. The owner runs the server; family members stream from whatever device is in hand.

## Requirements (v1)
- **Ingest** — point Harbor at a folder; it finds media, reads metadata, and skips duplicates.
- **Serve** — browse the catalog and play any title; transcode only when the device can't play the source codec.
- **Operate** — survive a crash: the catalog is backed up on a schedule and basic health is observable.
- **Self-hosted** — one binary, one `harbor.toml`, one SQLite catalog; no cloud account.

## Non-goals (v1)
Multi-user accounts, parental controls, live-TV/DVR, and native mobile apps.
