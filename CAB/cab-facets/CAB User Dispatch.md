---
description: user docs dispatch page
---
# CAB User Dispatch

**Location:** `{NAME} Docs/{NAME} User/{NAME} User.md`


The `{NAME} User.md` dispatch page inside the `{NAME} User/` folder. Lists all user-facing documentation for the anchor.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE User/CAE User.md` — User dispatch.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---


| -[[CAE User]]- | +> |
| --- | --- |
| [[CAE User Guide\|User Guide]] | getting started and usage |
| [[CAE Cards\|Cards]] | cheat sheets and flashcards |

---



# Format Specification

## Location

`{NAME} User.md` lives inside `{NAME} Docs/{NAME} User/`.

## Structure

- **Breadcrumb** — navigates back through the dispatch tree
- **Dispatch table** — top-left cell is `-[[{NAME} User]]-`, top-right is `+: user-facing documentation`
- **Body rows** — one row per user-facing document

## Contents

Typical entries include:

| Document | Description |
|----------|-------------|
| `{NAME} User Guide.md` | Getting started, installation, usage |
| `{NAME} Cards.md` | Cheat sheets and flashcards (if in User folder) |
| `CONFIG_REFERENCE.md` | Configuration options reference |

Not all entries are required — only list documents that exist for this anchor.
