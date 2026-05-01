---
description: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure
---
# CAE — Common Anchor Example

| -[[CAE]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [CAE](hook://p/CAE)<br>: Common Anchor Example — reference anchor — a fully-wired example of the canonical CAB structure |
| --- | --- |
| External | [Repo](https://github.com/example/cae-example), [Project Page](https://example.github.io/cae-example/) |
| ~~[CAE User/CAE User](hook://CAE%20User/CAE%20User)~~ | [[CAE User Guide\|User Guide]], [[CAE CLI\|CLI]] |
| [[CAE Plan\|Plan]]+ | [[CAE Backlog\|Backlog]], [[CAE Features\|Features]], [[CAE Icebox\|Icebox]], [[CAE Inbox\|Inbox]], [[CAE PRD\|PRD]], [[CAE Roadmap\|Roadmap]], [[CAE Rules\|Rules]], [[CAE System Design\|System Design]], [[CAE Triage\|Triage]] |
| [[CAE Plan\|Plan]] | [[CAE Inbox\|Inbox]], ~~[[CAE Open Questions\|Open Q]]~~, [[CAE Backlog\|Backlog]], [[CAE Roadmap\|Roadmap]] |
| ~~[CAE Dev/CAE Dev](hook://CAE%20Dev/CAE%20Dev)~~ | [[CAE Files\|Files]], [[CAE Architecture\|Architecture]] |
| Research | — |



## Overview

CAE is the **Common Anchor Example** — a self-contained reference anchor whose purpose is to demonstrate the canonical CAB structure. Every file here shows the correct format for its type. CAB specs (in `skills/CAB/cab-facets/`) describe *what each piece is and why*; CAE shows *exactly what the files look like*.

The content below the structural level is illustrative. CAE's fictional project is a simple CLI scheduler — enough domain to give the PRD, System Design, and module docs realistic content to demonstrate.



## Design Principles

Canonical statements live in ~~[[CAE Rules#Design Principles\|CAE Rules § Design Principles]]~~. This page names them for quick scanning.

- **~~[[CAE Rules#P01 — One Queue, One Clock\|P01]]~~** — one queue, one clock
- **~~[[CAE Rules#P02 — Fail Loudly, No Silent Fallbacks\|P02]]~~** — fail loudly, no silent fallbacks
- **~~[[CAE Rules#P03 — Deterministic Tests\|P03]]~~** — deterministic tests

Writing the principle once (in Rules) and referencing it by ID everywhere else keeps the single source of truth and eliminates drift.
