---
description: "LAN HTTP API surface"
---
# HBR API Design
The HTTP API the [[HBR UX Design|viewer app]] calls: browse the catalog, stream bytes, transcode on demand.

| -[[HBR API Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR API Design](hook://p/HBR%20API%20Design)<br>: LAN HTTP API surface |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR PRD]],  [[HBR UX Design]],  [[HBR Architecture]],  [[HBR CLI]],   |

**TL;DR.**
- Consumer: the Harbor web client (browser JS on the LAN) fetching JSON and streaming bytes from the [[HBR Serve|Serve]] pipeline.
- Surface: 5 endpoints under `/api` — catalog list, title detail, range stream, transcode session open, transcode segment.
- Error envelope: one JSON body `{ "error": { "code", "message" } }` over standard HTTP status codes; one shape on every error path.
- Stability: unversioned LAN-local pre-1.0; the web client ships in the same binary, so client+server move together. `/api/v1` reserved for the first third-party consumer.
- Transport: plain HTTP on the configured `listen` address; no auth (single trust boundary per [[HBR PRD]] non-goals); `Range` for direct-play, session+segment for transcode.

**Figure — canonical call.**

```http
GET /api/titles/4f2a HTTP/1.1          → 200 { "id":"4f2a","title":"Dune","codec":"hevc",... }
GET /api/stream/4f2a HTTP/1.1          → 206 Partial Content   (direct-play, Range honored)
Range: bytes=0-1048575

POST /api/titles/4f2a/transcode        → 200 { "session":"s91","playlist":"/api/transcode/s91/playlist" }
{ "profile": "h264-720p" }             (device can't direct-play; open a session, then pull segments)
```

## Consumer

The **Harbor web client** — browser JavaScript served by the Serve pipeline to any device on the home LAN (TV, phone, laptop). It is the only programmatic consumer: it fetches catalog JSON to render the Library grid, fetches title detail to open the Player, then either streams source bytes directly or opens a transcode session and pulls segments. Integration shape is **request/response JSON for metadata, long-lived range/segment streaming for media** — no websockets, no polling loop beyond the player's natural segment pulls.

There is deliberately **no cross-host or third-party consumer** in v1: the API is LAN-local, unauthenticated, and shipped inside the same binary as the client that calls it. Stable third-party integration is the reason `/api/v1` is reserved but not yet promised.

## Surface

The client renders the Library from `list`, opens the Player from `detail`, then either streams ranges directly or opens a transcode session and pulls segments.

| Entry | Method + Path | Purpose | Source story |
|---|---|---|---|
| `list` | `GET /api/titles?q=&type=` | List catalog titles (id, title, type, duration, poster URL) with optional search + type filter. | [[HBR Stories#^US-HBR-3\|US-HBR-3]] |
| `detail` | `GET /api/titles/{id}` | Full metadata for one title — codec, container, available stream variants. | [[HBR Stories#^US-HBR-3\|US-HBR-3]] |
| `stream` | `GET /api/stream/{id}` | Direct-play the source bytes; honors `Range` for seek/scrub. | [[HBR Stories#^US-HBR-3\|US-HBR-3]] |
| `transcode-open` | `POST /api/titles/{id}/transcode` | Open a transcode session for a device profile; returns a session id + playlist URL. | [[HBR Stories#^US-HBR-4\|US-HBR-4]] |
| `transcode-segment` | `GET /api/transcode/{session}/seg/{n}` | Fetch one transcoded segment of an open session. | [[HBR Stories#^US-HBR-4\|US-HBR-4]] |

Poster bytes are served as static assets under `/posters/{id}` (not part of the API contract; referenced by the URLs `list`/`detail` return). JSON bodies use the catalog's schemas — see [[HBR API Doc]] for per-field reference; this doc covers *intent*.

## Contract semantics

| Entry | Idempotent? | Side-effects | Concurrency | Deadlines / timeouts |
|---|---|---|---|---|
| `list` | yes; read-only | none | safe; point-in-time catalog snapshot | none |
| `detail` | yes; read-only | none | safe | none |
| `stream` | yes; read-only | none | many concurrent ranges per title are safe (Serve is read-only on the catalog) | none; client drives via `Range` |
| `transcode-open` | **no** — each POST opens a new session unless an identical `(title, profile)` session is live, which it reuses | spawns a Transcoder job; allocates Cache space | one job per `(title, profile)`; duplicate opens coalesce | session idle-expires after the configured TTL (default 60s without a segment pull) |
| `transcode-segment` | yes for a given `(session, n)` — same bytes on repeat | extends the session's idle deadline; may pre-transcode later segments | safe; segments served from the Cache | 404 once the session has expired or `n` is past end |

**Sessions are ephemeral and reclaimable.** A transcode session is not durable state: if it idle-expires or the server restarts, the client re-POSTs `transcode-open` and resumes. Direct-play (`stream`) carries no session and survives restarts transparently because it is a stateless range read.

## Error model

One envelope across every endpoint: a standard HTTP **status code** plus a JSON body of the single shape below. Mixing envelope forms (some endpoints bare text, others a different JSON shape) is forbidden by [[FCT API Design#RULESET R-api\|R-api-05]].

```json
{
  "error": {
    "code": "title_not_found",
    "message": "no title with id 4f2a"
  }
}
```

Status-code taxonomy:

| Status | `code` examples | Meaning |
|---|---|---|
| `200 OK` | — | success (JSON body, or media bytes for `stream` / `transcode-segment`) |
| `206 Partial Content` | — | successful `Range` response from `stream` |
| `400 Bad Request` | `bad_filter`, `bad_profile` | malformed query/body — bad `type=`, unknown transcode profile |
| `404 Not Found` | `title_not_found`, `session_expired`, `segment_out_of_range` | unknown title, expired/unknown session, segment past end |
| `416 Range Not Satisfiable` | `bad_range` | `Range` header outside the asset |
| `503 Service Unavailable` | `catalog_unavailable`, `transcoder_busy` | catalog mid-recovery (US-HBR-5) or no transcode slot free |
| `500 Internal Server Error` | `internal` | unexpected fault; `message` is operator-facing |

The `code` field is a **stable machine-readable string** the client switches on (e.g. `session_expired` → silently re-open); `message` is human/operator-facing and may change wording freely. The media endpoints (`stream`, `transcode-segment`) return the JSON envelope only on the error path — the success path is raw bytes.

## Stability + compatibility

**Stability posture: pre-1.0, LAN-local, unversioned in practice.** The web client and the HTTP server ship in the **same binary** (one Rust workspace), so they always move together — there is no skew between a deployed client and server, and changing a path needs no migration. This is why no auth and no version negotiation exist yet.

- **Reserved prefix:** all endpoints already live under `/api/`; the `/api/v1` namespace is **reserved** for the first external (non-bundled-client) consumer. Until then paths may change between Harbor releases in lockstep with the client.
- **Versioning scheme at 1.0 (planned):** once `/api/v1` is promised to a third party, semver applies — additive changes within `v1`, breaking changes mint `/api/v2` and run both for a deprecation horizon.
- **Deprecation policy (post-1.0):** a deprecated endpoint version is honored for **≥ 1 minor release after the deprecation notice**, and never removed in a patch. A concrete horizon, not "we'll try to be compatible."
- **Stable surfaces callers may rely on:** the error envelope shape, the `error.code` string set, and the `Range` / `206` direct-play contract.
- **Non-commitments:** transcode session ids and segment URL shapes (opaque — derive them only from `transcode-open`'s response, never construct them); poster URL paths; on-disk Cache layout; exact segment durations.

## Design decisions

| ID | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| D-API1 | One JSON error envelope `{ error: { code, message } }` over HTTP status codes | Bare-text errors; per-endpoint error shapes; RFC 7807 problem+json | One shape the client switches on by `code`; status code carries the class, `code` the specifics. RFC 7807 is heavier than a LAN-local single-consumer surface needs. |
| D-API2 | Direct-play via standard `Range` / `206`; transcode via session + segments | Always transcode (wastes CPU + quality on capable devices); always direct (excludes incompatible devices) | Honors the PRD's "direct-play when supported, transcode only when not" — `Range` reuses browser-native seeking for the common case; sessions isolate the expensive path. |
| D-API3 | Transcode is a stateful session (`transcode-open` → segments), not one long stream | A single chunked-transfer stream per playback | Sessions let the Cache serve segments, survive client seeks, and let duplicate opens coalesce onto one Transcoder job; a single long stream can't be shared or resumed. |
| D-API4 | No auth in v1; LAN single-trust-boundary | Token auth; per-device pairing | Matches [[HBR PRD]] non-goals (single household, one trust boundary); auth adds a surface with no v1 payoff. The binary binds to a LAN address only. |
| D-API5 | `transcode-open` coalesces identical `(title, profile)` requests | Strictly one session per POST | Two viewers starting the same title on the same device class share one Transcoder job — saves CPU + Cache; the client never knows it was coalesced. |
| D-API6 | Opaque session ids + segment URLs (client uses returned URLs, never constructs them) | Predictable `/{session}/seg/{n}` the client builds itself | Opacity lets the server change session/segment routing without breaking clients while the binary ships client+server together pre-1.0. |
| D-API7 | `503 catalog_unavailable` during recovery rather than blocking or failing hard | Block the request until recovery finishes; return `500` | US-HBR-5 recovery is bounded; a retryable `503` lets the client back off and the Library reappear automatically without an error dialog. |

## See also

- [[HBR PRD]] — user stories (US-HBR-3, US-HBR-4) that drive this surface.
- [[HBR UX Design]] — the human Library / Player surface the client renders.
- [[HBR Architecture]] — the [[HBR Serve|Serve]] pipeline that backs every endpoint.
- [[HBR API Doc]] — per-module reference for the JSON schemas (*what exists*).
- [[FCT API Design]] — facet spec; embedded [[FCT API Design#RULESET R-api\|R-api]] ruleset.
