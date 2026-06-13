---
description: How to read from and write to external services — Google Workspace, email, Notion. Dispatch over the io subskills.
---

| -[[SKL IO]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[SKL/SKL]] → [[SKL Doc]] → [SKL IO](hook://p/SKL%20IO)<br>: read/write external services — Google Workspace, email, Notion. |
| --- | --- |
| Skill anchor | [[SKA io]],   |
| Runtime | [[io/SKILL\|io SKILL.md]],   |
| Group | [[SKA Access]] (accessor — external cloud services) |

# SKL IO Guide

The **io** skill is the gateway between this Mac and external **cloud services** — Google Workspace, email, and Notion. It is an *accessor* (per [[SKA Access]]): its job is the channel, not a produced artifact. Each external surface is a **subcommand** (`/io <surface>`), so the whole family costs one skill in the catalog (per [[DSC granularity]]).

Say "put this in sheets", "read the spreadsheet", "update the slides", "search my email for X", and the agent routes to the right subskill below.

## Subskills

| Subskill | Surface | Reaches | Doc |
| --- | --- | --- | --- |
| **Google Workspace** (via the `gsa` CLI + OAuth) | | | |
| `/io gsheet` | Google Sheets | read / write / append cells, find sheets | [[io/io-gsheet\|io-gsheet]] |
| `/io gslide` | Google Slides | extract text, presentation metadata | [[io/io-gslide\|io-gslide]] |
| `/io gdoc` | Google Docs | read / write docs | [[io/io-gdoc\|io-gdoc]] |
| `/io gdrive` | Google Drive | search Drive | [[io/io-gdrive\|io-gdrive]] |
| **Mail** | | | |
| `/io email` | Email | **local Apple Mail** (read + search, all accounts, no auth) — or **Gmail API** (server-side, via the same Google OAuth; not yet wired) | [[io/io-email\|io-email]] · [[io/io-email-access\|access methods]] |
| **Other services** | | | |
| `/io notion` | Notion | pages + databases | [[io/io-notion\|io-notion]] *(TBD)* |
| **Auth** | | | |
| `/io gauth` | Google OAuth | re-authorize when the token expires → `/fix gauth` | — |

## Key concepts

- **One auth, many Google surfaces** — Sheets / Slides / Docs / Drive all use the OAuth credential at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (Google Cloud project `oblio-claude-access`). The token expires every 7 days (Testing mode); `/io gauth` re-authorizes.
- **`gsa` accepts URLs or IDs** — pass a full Google URL or a bare document ID.
- **Email needs no OAuth for the local path** — `/io email` drives Apple Mail via AppleScript, reading every configured account directly. The Gmail-API path (server-side search of one account) reuses the Google OAuth above. See [[io/io-email-access|the two access methods]].
- **Accessor, not producer** — io's deliverable is the read/write across a boundary. Skills whose point is a produced artifact (a research report, a diagram) live in Search / Doc instead.

## Key `gsa` commands

```bash
gsa sheets read <id> [range]          # Read cells as JSON
gsa sheets write <id> <range> <json>  # Write cells
gsa sheets append <id> <range> <json> # Append rows
gsa sheets info <id>                  # Sheet metadata
gsa slides read <id>                  # Extract all text
gsa search sheets [query]             # Find spreadsheets
gsa search slides [query]             # Find presentations
```
