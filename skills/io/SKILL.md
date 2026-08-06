---
name: io
description: >
  External system I/O — read from and write to external applications and services.
  Google Workspace: Sheets, Slides, Drive, Docs. Apple: Mail, Calendar, Health.
  Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides",
  "upload to drive", "read my email", "search mail for", "find that email from",
  "what's on my calendar", "read my calendar", "what do I have today",
  "pull my health data", "what's my sleep/heart rate", "check my apple health".
  Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io imail, /io ical, /io ihealth, /io notion.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
user_invocable: true
---

# IO — External System I/O
requires:: external:ctrl, external:gsa
subsystem:: [[DAS Doc Design]] — the Doc group's subsystem profile

Read from and write to external services. Each sub-skill is an access card with ranked methods.

**Command naming — a single-letter provider/surface prefix** so capabilities don't collide across providers. `g*` = Google cloud API (server-side, one account, expiring token): `gsheet`, `gslide`, `gdoc`, `gdrive`, and the future `gmail`/`gcal`. `i*` = Apple/local macOS frameworks (aggregate every account on this Mac): `imail`, `ical`, `ihealth`. The prefix marks *which access surface*, not which account — `imail` (local Apple Mail) already reads your Gmail if it syncs into Mail.app; `gmail` (once wired) hits Gmail's API directly. Same local-vs-cloud split the `*-access` cards document.

## Actions

| Group | Usage | File | Description |
|-------|-------|------|-------------|
| **Apple** | `/io imail` | [[io-imail]] · [[io-imail-access]] | Email via **local Apple Mail** (working). Server-side **Google Gmail API** surface is `/io gmail` (not yet wired). See [[io-imail-access]] for the access methods. |
| **Apple** | `/io ical` | [[io-ical]] · [[io-ical-access]] | Calendar via **local macOS Calendar** (EventKit, working): today's events, optional `+N` days ahead. Superset of the synced Google calendars. Server-side Google Calendar surface would be `/io gcal`. See [[io-ical-access]]. |
| **Apple** | `/io ihealth` | [[io-ihealth]] | Apple Health / HealthKit — **local daily JSON drop** (working, no auth): sleep, heart rate, HRV, activity, overnight vitals, gait. One file per day off the Watch/iPhone. Pipe + traps: [[WIRE Health Auto Export]], [[LUMEN Data Sources]]. |
| **Google** | `/io gsheet` | [[io-gsheet]] | Google Sheets |
| **Google** | `/io gslide` | [[io-gslide]] | Google Slides |
| **Google** | `/io gdoc` | [[io-gdoc]] | Google Docs |
| **Google** | `/io gdrive` | [[io-gdrive]] | Google Drive search |
| **Google** | `/io gauth` | → `/fix gauth` | Re-authorize Google OAuth (when token expires) |
| **Microsoft** | `/io excel` | [[io-excel]] | **Excel** — local `.xlsx`, live-coordinated (save-before-read / reload-after-write), formatting-preserving |
| **Notion** | `/io notion` | [[io-notion]] | Notion pages and databases (TBD) |

## Auth

Google API: OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`. Token expires every 7 days (Testing mode). Personal account only.

IDs accept full Google URLs or bare document IDs.

## Dispatch

1. Parse the argument to determine the action
2. Read the sub-skill file — it lists ranked methods
3. Try method 1. If it fails, try method 2.
