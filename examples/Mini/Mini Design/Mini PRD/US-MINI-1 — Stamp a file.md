# US-MINI-1 — Stamp a file
description:: Prepend today's date to a text file in one command

| -[[US-MINI-1]]- | : Prepend today's date to a text file.<br>→ [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[Mini]] → [[Mini Design]] → [[Mini PRD]] → [[Mini Stories]] → [US-MINI-1](hook://p/US-MINI-1) |
| --- | --- |
| [[Mini PRD]] | parent PRD |
| [[Mini Stories]] | sibling stories index |
| [[FCT Stories]] | facet spec |

## As a writer, I want to prepend today's date to a note in one command so that my notes are always dated without manual typing.

## Acceptance criteria

- `mini stamp <file>` inserts a `YYYY-MM-DD` line at the top of the file.
- Running it twice does not stack two date lines for the same day.
