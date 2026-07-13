---
name: io
description: >
  External system I/O — read from and write to external applications and services.
  Google Workspace: Sheets, Slides, Drive, Docs. Email via Apple Mail.
  Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides",
  "upload to drive", "read my email", "search mail for", "find that email from".
  Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io email, /io notion.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
user_invocable: true
---

# IO — External System I/O
requires:: external:ctrl, external:gsa

Read from and write to external services. Each sub-skill is an access card with ranked methods.

## Actions

| Usage | File | Description |
|-------|------|-------------|
| `/io excel` | [[io-excel]] | **Microsoft Excel** — local `.xlsx`, live-coordinated (save-before-read / reload-after-write), formatting-preserving |
| `/io gsheet` | [[io-gsheet]] | Google Sheets |
| `/io gslide` | [[io-gslide]] | Google Slides |
| `/io gdoc` | [[io-gdoc]] | Google Docs |
| `/io gdrive` | [[io-gdrive]] | Google Drive search |
| `/io email` | [[io-email]] · [[io-email-access]] | Email — **local Apple Mail** (working) or **Google Gmail API** (via existing Google auth; not yet wired). See [[io-email-access]] for the two access methods. |
| `/io notion` | [[io-notion]] | Notion pages and databases (TBD) |
| `/io gauth` | → `/fix gauth` | Re-authorize Google OAuth (when token expires) |

## Auth

Google API: OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`. Token expires every 7 days (Testing mode). Personal account only.

IDs accept full Google URLs or bare document IDs.

## Dispatch

1. Parse the argument to determine the action
2. Read the sub-skill file — it lists ranked methods
3. Try method 1. If it fails, try method 2.
