---
description: optional file for distant-future / someday-maybe items
---
# CAB Icebox

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Icebox.md` (optional)


The icebox file (`{NAME} Icebox.md`) holds items the user wants to remember but is **not** actively considering — distant-future ideas, parked features, "someday-maybe" entries. It is the cold-storage counterpart to the [[CAB Backlog]]: Backlog is the *active* deferred-work list, Icebox is the *frozen* one.

The term comes from Pivotal Tracker's three-bucket model (Current / Backlog / Icebox); the GTD equivalent is "Someday/Maybe."

**Optional.** Most anchors do not have an Icebox. Create the file only when the user first wants to park something there. If items in `{NAME} Backlog.md` start to feel like clutter that's never going to be acted on, that's the cue to spin up an Icebox and move them across.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Icebox.md` — Icebox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Icebox


## Frozen
- **GUI dashboard** — Web interface for task monitoring (out of scope for CLI-first phase)
- **Multi-tenant support** — Not needed until enterprise tier
- **Plugin system** — Third-party task handlers; revisit only if external demand appears

## Maybe Someday
- **GraphQL API** — Considered alongside REST, parked unless a consumer asks for it
- **Distributed scheduling** — Multi-host coordination; not relevant until single-host limits hit

---



# Format Specification

## Format

Each entry is a named-list item: bold name, em-dash, short description with the *reason* it's frozen (so a future reader knows whether the freeze still applies).

Entries are grouped under H2 sections. Suggested sections (use whichever fit; add others as needed):

- **Frozen** — Explicitly parked; out of scope for current direction
- **Maybe Someday** — Soft "we might want this" without a current driver
- **Revisit Later** — Items pinned to a future trigger (e.g. "after v2 ships")

## Location

`{NAME} Icebox.md` lives in `{NAME} Docs/{NAME} Plan/`. The file is optional — create it only when the user first wants to park an item.

## Lifecycle

- Items move **into** Icebox from Backlog when they stop being actively considered.
- Items move **out** of Icebox back to Backlog (or directly to Roadmap) when a trigger thaws them — new requirement, customer ask, design pivot.
- Icebox entries do not get deleted just for being old; the whole point is durable parking. Delete only when the idea is genuinely no longer applicable.

## Relationship to Other Planning Docs

- **Roadmap** — milestone-based execution plan
- **Backlog** — active deferred-work list, ideas that may be picked up soon
- **Icebox** — cold-storage list, not under active consideration

The cut between Backlog and Icebox is *intent to consider*, not age. A two-year-old item that the user still expects to revisit is Backlog; a two-week-old item the user has decided is out of scope is Icebox.
