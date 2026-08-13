---
description: {slug} inbox — raw input dropped for later processing.
---
:>> [[DAS]] → [[Templates]] → [inbox markdown](hook://p/inbox%20markdown) 
# {slug} Inbox
Drop zone for raw input; an entry with no status tag is pending, and draining writes `DONE` or `MOVED → {destination}` per [[DAS Inbox]].

## {{YYYY-MM-DD}} — {{Topic}}

*from: {{sender}} · tag: {{type}}*

> {{the message, quoted verbatim}}

## {{YYYY-MM-DD}} — {{Earlier topic}}    `DONE`

{{A hand-pasted entry carries no attribution line — that line is written by `state drop` and only when the sender passed `--source` / `--tag`.}}

## {{YYYY-MM-DD}} — {{Older topic}}    `MOVED → {{destination}}`

{{...}}
