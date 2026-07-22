# Calendar Access Methods

The calendar can be reached more than one way. This page is the dispatch over **how** `/io calendar` gets at your events — the trade-offs, and which is wired today. Per [[DAS granularity]], these are *surfaces within* the calendar capability, not separate skills.

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — EventKit** | every calendar in the local macOS Calendar (iCloud + the Google accounts that sync into it) | none — the calling process holds a one-time macOS Calendar (TCC) grant | **✅ working** |
| **Cloud — Google Calendar API** | a specific Google account's calendar server-side | the existing Google OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (same one `/io gsheet` etc. use) | **🔶 available, not yet wired** |
| **AppleScript (`osascript`)** | the local Calendar via Calendar.app scripting | none | ⚪ rejected — ~18s per query (the `whose` clause scans the whole event store); EventKit does the same in ~1s |

## Local — EventKit (default, working)

Queries the local Calendar store's indexed predicate directly via `scripts/calendar-today.swift` (run through the `swift` interpreter). **No tokens, no API keys** — the local Calendar already aggregates every synced account, so it is a superset of the Google calendars with no expiring permission to renew. Best for: "what's on my calendar today", morning briefings, "what do I have tomorrow". Recipes live in [[io-calendar]]. Limits: read-only; one-time Calendar TCC grant required (see [[io-calendar]] § Permission); whole-day offsets only.

## Cloud — Google Calendar API (available via existing Google auth)

Goes to Google's servers directly — reaches a single Google account's calendar server-side, including calendars not mirrored into the local Calendar. Uses the **same Google OAuth** already in place for Sheets/Slides/Docs/Drive, so no new credential is needed — it just needs the Calendar scope added and a verb wired. Best for: a Google calendar that does not sync locally, or scripting against one account server-side. **Not yet implemented** — the auth path exists; the verb doesn't.

## Which to use

- **Reading your calendar on this Mac** → local EventKit (`/io calendar`). It's working now and spans every account that syncs into the local Calendar.
- **A Google calendar that isn't mirrored locally** → Google Calendar API, once wired.

Default to **local** — it aggregates every account and needs no renewable permission.
