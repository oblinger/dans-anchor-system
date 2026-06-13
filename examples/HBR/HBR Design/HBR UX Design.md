---
description: "viewer-facing UX — Library grid + Player, Direct/Transcoding readout"
---
# HBR UX Design
What a household viewer sees: browse the catalog, then play a title — on whatever device is in hand.

| -[[HBR UX Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR UX Design](hook://p/HBR%20UX%20Design)<br>: viewer-facing UX |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR API Design]],  [[HBR CLI]],  [[HBR Architecture]],  [[HBR PRD]],   |

## TLDR
- **Audience** — a household viewer on a LAN device (TV browser, phone, laptop); no account, no install.
- **Surface** — a two-screen web app served by [[HBR Serve|Serve]]: **Library** (poster grid + search) and **Player** (scrub / volume / quality readout).
- **Vocabulary** — the screen speaks in *catalog*, *title*, and *stream*; the viewer never sees rows, hashes, or codecs.
- **Output** — one playing stream; a `Direct` vs `Transcoding` badge is the only system-state the viewer reads.
- **Error voice** — quiet and reassuring: short banner, plain cause, one obvious next step. No codes, no stack traces.
- **Discovery** — the LAN URL is the whole front door; the grid is self-explanatory, the player chrome auto-hides.

## Figure

```
  Phone                          TV browser
 ┌──────────────┐               ┌────────────────────────────┐
 │  Harbor   🔍 │   tap title   │                            │
 │ ┌──┐┌──┐┌──┐ │  ──────────▶  │      ▶  (playing)          │
 │ │▦ ││▦ ││▦ │ │               │   ━━━━━━●───────  12:04     │
 │ └──┘└──┘└──┘ │               │   Direct                   │
 └──────────────┘               └────────────────────────────┘
   Library screen                  Player screen
        │                                  │
        └─── one Serve pipeline, one catalog, one LAN URL ───┘
```

*The viewer's whole world: a grid that opens a player. The catalog, transcoder, and cache all live behind the single URL.*

## Overview
Harbor's viewer surface is deliberately small: a browser points at one LAN URL and lands on the **Library**, a poster grid over the whole catalog; tapping a poster opens the **Player**. That is the entire app — two screens, one transition, no chrome the viewer didn't ask for. Everything behind it ([[HBR Serve|Serve]] streaming, the transcoder, the cache, the SQLite catalog) is invisible; the viewer reads only posters, a scrubber, and a one-word quality badge. The owner-facing surface (ingest, config, recovery) is the [[HBR CLI|CLI]] — a separate audience with a separate doc. This file specifies only what a *household viewer* touches.

## Audience
A family member at home, opening a browser on a TV, phone, or laptop already on the house LAN. They have no Harbor account, installed nothing, and know only the address the owner gave them. Their goal is immediate: find something to watch and play it on the device in their hand. They are not technical and will not read documentation — the surface must explain itself, and a failure must never look like a server error. The owner's surface (ingest, config, recovery) is the [[HBR CLI|CLI]], not this web app; this doc covers only the *viewer*.

## System Concepts
The viewer's three nouns. Everything on screen maps to one of these; nothing else (rows, content-hashes, codecs, cache keys) ever surfaces.

- **Catalog** — the whole browsable library. One Harbor instance, one catalog. The Library screen *is* the catalog rendered as posters.
- **Title** — one playable thing: a movie, a show episode, a music track. A poster in the grid; a stream in the player. Carries a name, poster, and duration — the only metadata the viewer sees.
- **Stream** — a title in motion: the bytes [[HBR Serve|Serve]] sends to the device, either the source file unchanged (**Direct**) or re-encoded on the fly (**Transcoding**). Exactly one stream plays at a time per device.

## Entry-points
The viewer surface is two screens reachable from one URL. Every viewer-invocable thing is here.

| Screen | Purpose | Source |
|---|---|---|
| **Library** | Poster grid over the catalog; search + type filter; tap a poster to play. | US-HBR-3 |
| **Player** | Full-screen playback — scrub, volume, `Direct`/`Transcoding` badge, back. | US-HBR-3, US-HBR-4 |

## Screens

### Library
A poster grid over the whole catalog, with a search box and a type filter (All / Movies / Shows / Music). Posters lazy-load as the viewer scrolls. Selecting a poster opens the Player. (Source: US-HBR-3.)

```
┌──────────────────────────────────────────────────────────┐
│  Harbor          [ search… 🔍 ]   ( All  Movies  Shows  Music )│
├──────────────────────────────────────────────────────────┤
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐          │
│  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │          │
│  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │          │
│  └────────┘  └────────┘  └────────┘  └────────┘          │
│   Arrival      Dune       The Wire    Blue Note          │
│   1h 56m       2h 35m     S1·E1       42m                │
│                                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐          │
│  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │  │ ▦▦▦▦▦▦ │          │
│  └────────┘  └────────┘  └────────┘  └────────┘          │
└──────────────────────────────────────────────────────────┘
```

### Player
Full-screen playback with a scrubber, current/total time, volume, and a quality badge (`Direct` or `Transcoding`). Chrome auto-hides after a few seconds of no interaction and reappears on tap/move. Closing returns to the Library at the prior scroll position. (Source: US-HBR-3, US-HBR-4.)

```
┌──────────────────────────────────────────────────────────┐
│  ‹ Back          Arrival                          ⚙        │
│                                                          │
│                                                          │
│                     ▶  (video)                           │
│                                                          │
│                                                          │
│  ━━━━━━━━━━━━━●───────────────────   12:04 / 1:56:10     │
│  ⏯   🔊 ━━━●──                       [ Direct ]          │
└──────────────────────────────────────────────────────────┘
```

## Output shapes
The viewer-facing surface is **human-only video** — there is no `--json` here; structured output is the [[HBR API Design|API]]'s job (the web app *consumes* that API). Two things the viewer reads with their eyes:

- **The playing stream** — the video itself, the default and only "output." Scrub, volume, and back are the controls.
- **The quality badge** — the single piece of system-state made visible: `Direct` (source played untouched) or `Transcoding` (Serve re-encoding live for this device). See [Output / States](#output--states).

The underlying playlist/manifest the player fetches (HLS/DASH, byte ranges) is structured but is API surface, not viewer surface — it never appears as text in the UI.

## Output / States
The badge in the Player is the viewer's whole model of "how is this playing." Two states, one transition.

| Badge | Meaning | When |
|---|---|---|
| `Direct` | Source file streamed unchanged; lowest latency, best quality. | Device supports the title's codec (US-HBR-3). |
| `Transcoding` | Serve re-encodes the stream live to a device-compatible profile. | Device can't play the source codec (US-HBR-4). |

```
   start playback
        │
        ▼
   device codec supported?
    ├── yes ──▶  [ Direct ]
    └── no  ──▶  Serve transcodes ──▶  [ Transcoding ]   (a brief "Preparing…" first)
```

The choice is automatic — the viewer never picks a format. The only visible difference between states is the badge and a slightly longer start when transcoding spins up.

## Error voice
**Tone: quiet and reassuring.** A failure shows a short centered banner — plain cause, one obvious action — never a code, codec name, or stack trace. The viewer should feel the *library* hiccuped, not that they broke a server.

| Situation | Message | Action offered |
|---|---|---|
| Server unreachable | "Can't reach Harbor. Check you're on the home network." | Retry |
| Title won't play | "This one won't play right now. Try again in a moment." | Back to Library |
| Transcode failed | "Couldn't prepare this for your device." | Back to Library |
| Empty / no results | "Nothing here yet." (Library) · "No matches." (search) | — |

## Discovery
The **LAN URL** is the entire front door — the owner shares `http://harbor.local:<port>/` (or an IP) and that is all a viewer needs; there is no sign-in, menu, or onboarding. From there the surface is self-teaching: the poster grid reads as "tap to watch," search and the type filter sit in plain view at the top, and the Player chrome surfaces on first tap then fades. No help screen ships — if a viewer needs instructions, the UX has failed.

## Design decisions
Load-bearing UX choices. Rationale that cites a ruleset bridges to [[HBR Decisions]].

| ID | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| D-UX1 | Two screens only — Library and Player | Browse / detail / settings / queue screens | A household library is "find one thing, watch it." A detail page and queue add navigation without serving the core story; deferred past v1. |
| D-UX2 | Show a `Direct` / `Transcoding` badge | Hide it entirely; or expose full codec/bitrate | The viewer benefits from knowing *why* a start was slow, but codec detail is noise. One word is the right altitude. |
| D-UX3 | Automatic transcode, never a format picker | Let the viewer choose quality/format | The PRD promise is "just works regardless of source format." A picker pushes a server concern onto a non-technical viewer (US-HBR-4). |
| D-UX4 | No accounts, no per-viewer state | Per-user profiles, watch history | v1 is one household on one LAN; identity and history are explicitly deferred. The URL is the only credential. |
| D-UX5 | Errors as plain banners, no codes | Surface HTTP/codec errors verbatim | A non-technical viewer reads a code as "I broke it." Quiet, actionable banners keep the failure feeling like the library, not the server. |

## Voice
Plain and quiet — the media is the content; the UI gets out of the way. Few words, no jargon, no chrome the viewer didn't ask for.
</content>
</invoke>
