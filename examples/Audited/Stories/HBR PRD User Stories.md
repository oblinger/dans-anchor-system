# HBR PRD User Stories
description:: audited excerpt — the inline `## User Stories` section of HBR PRD (inline-subsection form, US-HBR-1..5)

This is the audited rendering of the **inline-subsection form** of the Stories facet — the `## User Stories` section as it lives inside [[HBR PRD]]. Inline form keeps the stories inside the PRD (no separate `{NAME} Stories.md`); each story is a short `### US-<RID>-N` subsection with the canonical `As a … I want … so that …` sentence plus one `**Acceptance:**` line, fronted by a grouping index table. This is the good shape once stories deserve stable identifiers + an acceptance line but still don't warrant their own pages.

## User Stories

| | Description |
| --- | --- |
| **Ingest** | |
| [[#US-HBR-1 — Add a library\|US-HBR-1]] — Add a library | Owner points Harbor at a folder; it appears, deduped, in the catalog. |
| [[#US-HBR-2 — Re-scan on change\|US-HBR-2]] — Re-scan on change | New files in a watched folder show up without a full re-ingest. |
| **Serve** | |
| [[#US-HBR-3 — Browse and play\|US-HBR-3]] — Browse and play | Family member browses the catalog and plays a title on the device in hand. |
| [[#US-HBR-4 — Transcode on demand\|US-HBR-4]] — Transcode on demand | A title in an unsupported codec still plays, transcoded to fit the device. |
| **Operate** | |
| [[#US-HBR-5 — Recover after a crash\|US-HBR-5]] — Recover after a crash | Owner restarts Harbor after a power loss and the catalog is intact. |

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

- [[HBR PRD]] — parent PRD this stories section lives inside
- [[FCT Stories]] — facet spec that governs this form
