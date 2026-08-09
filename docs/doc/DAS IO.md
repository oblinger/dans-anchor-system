---
description: "How to read from and write to external services — Google Workspace, email, file sync"
---

| -[[DAS IO]]- | → [[DAS]] → [docs](hook://docs) → [DAS IO](hook://p/DAS%20IO)<br>: How to read from and write to external services — Google Workspace, email, file sync |
| --- | --- |
| Skill anchor | [[SKA io]],   |
| Runtime | [[io/SKILL\|io SKILL.md]],   |
| Group | [[SKA Access]] (accessor — external cloud services) |
| ... |  |

# DAS IO

The **io** skill is the gateway between this Mac and external services — cloud (Google Workspace, email, Notion) and local desktop apps (Microsoft Excel). Each surface is a subcommand (`/io <surface>`).

**The aim is live, bidirectional I/O.** Where the surface allows, io makes an external document behave like one you and the agent co-edit *live* — the agent reads your latest, you see the agent's edits, and neither side clobbers the other. It isn't guaranteed for every surface, but that's the design intent — and it's fully realized for **Excel** (`/io excel`): a save-before-read / reload-after-write handshake makes a local `.xlsx` behave, in practice, exactly like live editing.

Say "put this in sheets", "update the Excel", "search my email for X" — the agent routes to the subskill below.

## Subskills

| Subskill | Surface | Reaches | Doc |
| --- | --- | --- | --- |
| **Google Workspace** (via the `gsa` CLI + OAuth) | | | |
| `/io gsheet` | Google Sheets | read / write / append cells, find sheets | [[io/io-gsheet\|io-gsheet]] |
| `/io gslide` | Google Slides | extract text, presentation metadata | [[io/io-gslide\|io-gslide]] |
| `/io gdoc` | Google Docs | read / write docs | [[io/io-gdoc\|io-gdoc]] |
| `/io gdrive` | Google Drive | search Drive | [[io/io-gdrive\|io-gdrive]] |
| **Microsoft Office** (local files via the `io-excel` CLI + AppleScript) | | | |
| `/io excel` | Microsoft Excel | probe / read / set cells, build a grid from a markdown table — **live-coordinated** (save-before-read, reload-after-write), formatting-preserving | [[io/io-excel\|io-excel]] |
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
- **Excel behaves like live editing** — `io-excel` wraps each op in an AppleScript handshake: it **saves the target workbook before reading** (so disk == the user's latest) and **reloads it in Excel after writing** (so the change shows and isn't clobbered on a later save). Edits are formatting-preserving (load-modify-save; cell values only). The one contract: the user must ⌘S their formatting before the agent writes — the post-write reload discards *unsaved* Excel changes. Charts/images/pivots/macros are not openpyxl-modeled and get dropped on save — don't `set` workbooks containing them.
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

## Key `io-excel` commands

```bash
io-excel probe <file>                                       # sheets, dims, headers
io-excel read  <file> [--sheet S] [--cols ...] [--where "COL op VAL"] [--format md|tsv|json]
io-excel set   <file> --key-col A --key S4 --col Workaround --value "..."   # locate-by-key (preferred)
io-excel set   <file> --cell G5 --value "..."               # direct cell
io-excel from-md <file> --md <doc.md> [--table N | --list]  # build a grid from a markdown table
```

`--where` ops: `contains` / `startswith` / `=` / `!=`. `--cols` takes header names or column letters. `-v` shows the live handshake; `--no-live` skips it.
