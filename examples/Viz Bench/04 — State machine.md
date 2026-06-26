---
description: "Video transcoding job lifecycle — a finite state machine with retry self-loops and a re-queue back-edge"
---
# 04 — State machine

**Diagram kind:** State machine (finite-state diagram with directed, labeled transitions).
**Layout challenge:** A cyclic directed graph — the engine must place self-loops legibly, route a long back-edge that returns flow upstream against the dominant forward direction, and keep two distinct terminal states untangled, all without overlapping the labeled transitions.
**Domain:** The lifecycle of a single video-transcoding job in a media-processing pipeline, from submission through upload, encoding, validation, and either successful publication or terminal failure.

## Nodes
- Queued — job submitted, awaiting a free worker [initial state]
- Downloading — worker pulling the source asset from object storage
- Probing — inspecting container/codec/streams with ffprobe
- Transcoding — encoding to target renditions
- Validating — checksum + playback sanity-check on the output
- Uploading — pushing renditions back to object storage
- Published — renditions live and addressable [terminal: success]
- Failed — job abandoned after exhausting retries [terminal: failure]
- Cancelled — operator-aborted job [terminal: cancelled]

## Edges
- Queued → Downloading : "worker claims job" [solid]
- Downloading → Probing : "source fetched" [solid]
- Downloading → Downloading : "chunk timeout — resume" [solid]  (self-loop)
- Probing → Transcoding : "format supported" [solid]
- Probing → Failed : "unsupported codec" [solid]
- Transcoding → Transcoding : "rendition complete — next profile" [solid]  (self-loop)
- Transcoding → Validating : "all renditions encoded" [solid]
- Validating → Uploading : "checks pass" [solid]
- Validating → Transcoding : "corrupt output — re-encode" [dashed]  (back-edge)
- Uploading → Published : "all parts confirmed" [solid]
- Uploading → Queued : "storage 5xx — re-queue job" [dashed]  (back-edge)
- Queued → Cancelled : "operator abort" [dashed]
- Transcoding → Cancelled : "operator abort" [dashed]
- Validating → Failed : "max retries reached" [solid]

## Groups / lanes / cardinality
- No swimlanes. One unmistakable initial state (Queued, the only state with no incoming forward edge except the re-queue back-edge). Three terminal states (Published, Failed, Cancelled), each with no outgoing edges. Two self-loops (Downloading, Transcoding) and two back-edges (Validating→Transcoding, Uploading→Queued) that must be routed distinctly from the forward path.

## Acceptance
- Fidelity: the render contains exactly these 9 nodes and 15 edges (count + labels match); none added or dropped. Both self-loops and both back-edges must be present and correctly directed; the dashed vs. solid distinction must be preserved.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
