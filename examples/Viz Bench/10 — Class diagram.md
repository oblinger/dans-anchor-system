---
description: "UML class model for a music-streaming app: User/Playlist/Track with inheritance, composition, and typed associations."
---
# 10 — Class diagram

**Diagram kind:** UML class diagram.
**Layout challenge:** mixing three distinct relationship semantics on one canvas — inheritance (generalization), composition (filled-diamond whole/part with lifecycle dependence), and plain association (typed, navigable, with multiplicities) — while every class still legibly shows its member compartments (attributes + operations). The engine must route many edge types between the same boxes without crossing-clutter and keep all member text readable.

**Domain:** the core object model of a music-streaming application (accounts, content catalog, playlists, and playback).

## Nodes
Each node is a UML class box with a name compartment, an attributes compartment, and an operations compartment.

- `Account` — abstract base account [class, abstract]
  - attributes: `id: UUID`, `email: String`, `createdAt: Date`
  - operations: `login(): Boolean`, `logout(): void`
- `FreeAccount` — ad-supported tier [class]
  - attributes: `adInterval: Int`
  - operations: `showAd(): void`
- `PremiumAccount` — paid subscription tier [class]
  - attributes: `renewalDate: Date`, `priceTier: String`
  - operations: `downloadOffline(t: Track): Boolean`
- `User` — profile owning an account [class]
  - attributes: `displayName: String`, `country: String`
  - operations: `follow(u: User): void`
- `Playlist` — ordered collection of tracks [class]
  - attributes: `title: String`, `isPublic: Boolean`
  - operations: `addTrack(t: Track): void`, `reorder(): void`
- `PlaylistItem` — one slot in a playlist [class]
  - attributes: `position: Int`, `addedAt: Date`
- `Track` — a catalog song [class]
  - attributes: `title: String`, `durationSec: Int`, `isrc: String`
  - operations: `play(): Stream`
- `Album` — a release grouping tracks [class]
  - attributes: `title: String`, `releaseDate: Date`
- `Artist` — performer [class]
  - attributes: `name: String`, `verified: Boolean`
- `PlaybackSession` — an active listening session [class]
  - attributes: `startedAt: Date`, `deviceId: String`
  - operations: `pause(): void`, `skip(): void`
- `AudioStream` — the decoded audio for a session [class]
  - attributes: `bitrateKbps: Int`, `codec: String`
- `Genre` — classification tag [class]
  - attributes: `name: String`

## Edges
Edge styles: generalization (hollow-triangle, solid); composition (filled-diamond at the whole, solid); association (plain solid line, navigable, with role/multiplicity); dependency (dashed arrow). Direction is given as source → target with the source listed first.

- `FreeAccount` → `Account` : "generalization (is-a)" [solid]
- `PremiumAccount` → `Account` : "generalization (is-a)" [solid]
- `User` → `Account` : "has — owns 1 account [1]" [solid]
- `User` → `Playlist` : "creates — owns playlists [0..*]" [solid]
- `Playlist` → `PlaylistItem` : "composition — contains items [1..*]" [solid]
- `PlaylistItem` → `Track` : "references — points to track [1]" [solid]
- `Album` → `Track` : "composition — contains tracks [1..*]" [solid]
- `Artist` → `Album` : "produces — releases albums [0..*]" [solid]
- `Track` → `Artist` : "performedBy — credited artists [1..*]" [solid]
- `Track` → `Genre` : "taggedWith — genres [0..*]" [solid]
- `User` → `PlaybackSession` : "starts — active sessions [0..*]" [solid]
- `PlaybackSession` → `Track` : "nowPlaying — current track [1]" [solid]
- `PlaybackSession` → `AudioStream` : "composition — owns stream [1]" [solid]
- `PremiumAccount` → `Track` : "downloads (dependency) — offline copy" [dashed]

## Groups / lanes / cardinality
- No swimlanes or containers — a flat class model.
- Cardinalities are carried on the association/composition edges as bracketed multiplicities (e.g. `[1]`, `[0..*]`, `[1..*]`) and must be preserved exactly.
- Three edge semantics must be visually distinguishable: generalization (hollow triangle, 2 edges), composition (filled diamond at the whole-end, 3 edges: Playlist→PlaylistItem, Album→Track, PlaybackSession→AudioStream), plain association (8 edges), dependency (dashed, 1 edge).
- `Account` is rendered as abstract (italic name or `{abstract}`).

## Acceptance
- Fidelity: the render contains exactly these 12 nodes and 14 edges (count + labels + multiplicities match; relationship semantics — generalization vs. composition vs. association vs. dependency — preserved); none added or dropped.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
