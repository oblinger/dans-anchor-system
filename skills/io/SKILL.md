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

## Routing policy — local first, MCP last (F004, reaffirmed 2026-08-05)

**Prefer the surface that needs no expiring credential.** Ranked, and the ranking is the point:

1. **Local Apple frameworks (`i*`)** — `imail`, `ical`, `ihealth`. A TCC grant is given once and does not expire; an OAuth token does. Local is also a **superset** for calendar (Family / Birthdays / iCloud calendars were never reachable through Google at all). Established by [[F004 — Calendar via local macOS Calendar, not Google OAuth|LUMEN F004]] in the user's own words: *"Google permissions really suck — they don't stay active."*
2. **`gsa` CLI (`g*`)** — the direct Google API client for Sheets, Slides, Docs, and Drive search. **No MCP server involved.** Verified working 2026-08-05.
3. **The `workspace-mcp` server** — the fallback of last resort, and only for Google surfaces `gsa` does not implement (Gmail API, Chat, Forms, Apps Script).

**Use the MCP server for as little as possible.** It is one more moving part on the same single credential store, and two independent failures make it the weakest link:

- **It is not currently reachable as an MCP.** `claude mcp list` reports no servers — an `ANTHROPIC_API_KEY` precedence warning blocks registration, so `ob_boot` re-registers it into a void at every login. The server itself is healthy on `:8000`; only the Claude Code integration is broken. Reaching it means speaking JSON-RPC over HTTP by hand.
- **Its token expires every 7 days** (the OAuth app is in Testing mode), and nothing probes it — so the credentials rot silently and the first symptom is an unrelated task failing. See [[ATT Backlog#^T022|ATT T022]].

**One credential store, two clients.** `gsa` and `workspace-mcp` both read `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`. There are not two OAuth paths to repair — one consent fixes both. When re-consenting, **tick "Select all"**: the permission checkboxes default to unchecked, and clicking straight through grants `email`/`profile`/`openid` only, which then fails as HTTP 403 *insufficient scopes* rather than as an auth error.

**The one measured exception to local-first.** Searching mail is a Google job, not a local one: Apple Mail scripting against the user's 236,962-message archive timed out at ~40 minutes, and Mail's SQLite index is TCC-blocked to the shell. Use local `imail` for reading and composing; reach for the Gmail API when the task is *search over the whole archive*.

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

Google API: OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` — **one file, both clients** (`gsa` and `workspace-mcp`). Token expires every 7 days (Testing mode). Personal account only. Re-consent via `/io gauth`, and see § Routing policy for the "Select all" trap that silently grants zero API scopes.

Apple surfaces (`imail`, `ical`, `ihealth`) carry **no auth here** — they run on TCC grants that do not expire, which is the whole reason they rank first.

Last full re-consent: **2026-08-05**, 41 scopes granted (Gmail, Sheets, Docs, Drive, Slides all live).

IDs accept full Google URLs or bare document IDs.

## Dispatch

1. Parse the argument to determine the action
2. Read the sub-skill file — it lists ranked methods
3. Try method 1. If it fails, try method 2.
