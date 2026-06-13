---
description: "product requirements — why Harbor exists and what v1 must deliver"
---
# HBR PRD
Why Harbor exists and what its first version must deliver.

| -[[HBR PRD]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR PRD](hook://p/HBR%20PRD)<br>: product requirements |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Stories | [[HBR Stories]] — the US-HBR-N catalog |
| Related | [[HBR UX Design]],  [[HBR Architecture]],  [[HBR Roadmap]],   |

## Overview

Harbor is a **self-hosted media server**: point it at a folder of movies, shows, and music, and it builds a browsable catalog any device on the home network can stream — transcoding on the fly only when the device can't play the source. It is one household's library, run by one person, with no cloud account and no telemetry: a single binary, a single `harbor.toml`, a single SQLite catalog.

The v1 goal is the smallest thing that earns daily use: ingest a library without duplicates, stream it to a TV / phone / laptop, and survive a crash without losing the catalog. Everything past that — accounts, DVR, mobile apps — is explicitly deferred.

## Goals

- **One-command ingest** — point Harbor at a directory; it discovers media, reads embedded metadata, and skips files already in the catalog (content-hash dedup).
- **Play anywhere on the LAN** — browse the catalog and start any title from a TV, phone, or laptop; direct-play when the device supports the codec, transcode only when it doesn't.
- **Survive a crash** — the catalog is checkpointed on a schedule; a restart resumes from the last good state with no manual repair.
- **Self-hosted and private** — one binary, one `harbor.toml`, one SQLite catalog; no cloud account, no outbound calls, no tracking.

## Non-Goals

- **Multi-user accounts / profiles** — v1 is single-household, single trust boundary. Per-user libraries add auth, sharing, and quota surfaces not worth it yet.
- **Parental controls / ratings gates** — depend on accounts; deferred with them.
- **Live TV / DVR** — a different ingest and scheduling domain; out of scope for a file-library v1.
- **Native mobile apps** — the LAN web client covers phones and tablets in v1; native apps are a post-v1 distribution problem.
- **Library editing / metadata correction UI** — Harbor reads embedded metadata; hand-correcting it is a later nicety, not a v1 blocker.

## User Stories

| | Description |
| --- | --- |
| **Ingest** | |
| [[HBR Stories#^US-HBR-1\|US-HBR-1]] — Add a library | Owner points Harbor at a folder; it appears, deduped, in the catalog. |
| [[HBR Stories#^US-HBR-2\|US-HBR-2]] — Re-scan on change | New files in a watched folder show up without a full re-ingest. |
| **Serve** | |
| [[HBR Stories#^US-HBR-3\|US-HBR-3]] — Browse and play | Family member browses the catalog and plays a title on the device in hand. |
| [[HBR Stories#^US-HBR-4\|US-HBR-4]] — Transcode on demand | A title in an unsupported codec still plays, transcoded to fit the device. |
| **Operate** | |
| [[HBR Stories#^US-HBR-5\|US-HBR-5]] — Recover after a crash | Owner restarts Harbor after a power loss and the catalog is intact. |

### US-HBR-1 — Add a library
As the **owner**, I want to point Harbor at a directory and have it ingest the media there, so that my existing library becomes browsable without manual cataloging.
**Acceptance:** `harbor ingest <path>` discovers video/audio files, reads embedded metadata (title, duration, codec), writes catalog rows, and skips any file whose content-hash is already present. Re-running on the same path adds nothing.

### US-HBR-2 — Re-scan on change
As the **owner**, I want files dropped into a watched folder to appear automatically, so that I don't re-ingest the whole library to add one movie.
**Acceptance:** a watched folder (declared in `harbor.toml`) is rescanned on a schedule; only new/changed files are processed; removed files are marked absent, not deleted from disk.

### US-HBR-3 — Browse and play
As a **family member**, I want to browse the catalog and start a title from my phone, TV, or laptop, so that I can watch without touching the server.
**Acceptance:** the LAN web client lists titles with poster + duration; selecting one starts playback within a few seconds on a device that supports the source codec (direct-play).

### US-HBR-4 — Transcode on demand
As a **family member**, I want a title in a codec my device can't play to still play, so that the library "just works" regardless of source format.
**Acceptance:** when the client reports an unsupported codec, Harbor transcodes the stream on the fly to a device-compatible profile; playback starts without the user choosing a format.

### US-HBR-5 — Recover after a crash
As the **owner**, I want Harbor to come back cleanly after a power loss, so that I never rebuild the catalog by hand.
**Acceptance:** the SQLite catalog is checkpointed on the configured schedule; after an unclean shutdown, the next start resumes from the last checkpoint with the catalog intact and in-flight ingests safely re-queued.

## See also

- [[HBR UX Design]] — the browse/play surface and CLI
- [[HBR Architecture]] — Ingest / Serve / Operate subsystems
- [[HBR Decisions]] — load-bearing choices (SQLite catalog, content-hash dedup, single binary)
