---
name: io
description: >
  External system I/O — read from and write to external applications and services.
  Google Workspace: Sheets, Slides, Drive, Docs. Apple: Mail, Calendar.
  Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides",
  "upload to drive", "read my email", "search mail for", "find that email from",
  "what's on my calendar", "read my calendar", "what do I have today".
  Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io email, /io calendar, /io notion.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
user_invocable: true
---

# IO — External System I/O
requires:: external:ctrl, external:gsa
subsystem:: [[DAS Doc Design]] — the Doc group's subsystem profile

Read from and write to external services. Each sub-skill is an access card with ranked methods.

## Actions

| Group | Usage | File | Description |
|-------|-------|------|-------------|
| **Apple** | `/io email` | [[io-email]] · [[io-email-access]] | Email — **local Apple Mail** (working) or **Google Gmail API** (via existing Google auth; not yet wired). See [[io-email-access]] for the two access methods. |
| **Apple** | `/io calendar` | [[io-calendar]] · [[io-calendar-access]] | Calendar — **local macOS Calendar** (EventKit, working): today's events, optional `+N` days ahead. Superset of the synced Google calendars. See [[io-calendar-access]] for the access methods. |
| **Google** | `/io gsheet` | [[io-gsheet]] | Google Sheets |
| **Google** | `/io gslide` | [[io-gslide]] | Google Slides |
| **Google** | `/io gdoc` | [[io-gdoc]] | Google Docs |
| **Google** | `/io gdrive` | [[io-gdrive]] | Google Drive search |
| **Google** | `/io gauth` | → `/fix gauth` | Re-authorize Google OAuth (when token expires) |
| **Microsoft** | `/io excel` | [[io-excel]] | **Excel** — local `.xlsx`, live-coordinated (save-before-read / reload-after-write), formatting-preserving |
| **Notion** | `/io notion` | [[io-notion]] | Notion pages and databases (TBD) |

## Auth

Google API: OAuth at `~/.google_workspace_mcp/credentials/oblinger@gmail.com.json`. Token expires every 7 days (Testing mode). Personal account only.

IDs accept full Google URLs or bare document IDs.

## Dispatch

1. Parse the argument to determine the action
2. Read the sub-skill file — it lists ranked methods
3. Try method 1. If it fails, try method 2.
