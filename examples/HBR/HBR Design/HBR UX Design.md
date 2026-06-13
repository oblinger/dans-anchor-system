---
description: "viewer-facing UX"
---
# HBR UX Design
What a household viewer sees: browse, then play.

| -[[HBR UX Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[HBR]] → [[HBR Design]] → [HBR UX Design](hook://p/HBR%20UX%20Design)<br>: viewer-facing UX |
| --- | --- |
| Anchor | [[HBR Design]] (parent) |
| Related | [[HBR API Design]],  [[HBR CLI]],   |

Harbor's viewer surface is a small web app served by the [[HBR Serve|Serve]] pipeline. Two screens, no account flow.

## Library
A poster grid of catalog titles with a search box; filter by type (movie / show / music). Selecting a poster opens the Player.

## Player
Full-screen playback with scrub, volume, and a quality readout (`Direct` or `Transcoding`). Closing returns to the Library at the prior scroll position.

## Voice
Plain and quiet — the media is the content; the UI gets out of the way.
