---
description: "HTTP API"
---
# HBR API Design
The HTTP API the [[HBR UX Design|viewer app]] calls — read-only browse plus one streaming endpoint.

| -[[HBR API Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR API Design](hook://p/HBR%20API%20Design)<br>: HTTP API |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR CLI]],  [[HBR UX Design]],   |

Base path `/api`. JSON for metadata, raw bytes for media. No auth in v1 (LAN-only, single household).

- `GET /api/titles?q=&type=` — search the catalog; returns `id`, `title`, `type`, `duration`.
- `GET /api/titles/{id}` — one title's full metadata and available streams.
- `GET /api/stream/{id}` — the media bytes; honors HTTP `Range`, direct-plays when the client accepts the source codec, else transcodes (see [[HBR Decisions|D02]]).

Every error uses one envelope — `{ "error": { "code": "...", "message": "..." } }` — with a matching HTTP status.
