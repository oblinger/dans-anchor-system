# ical — Access Methods

The calendar can be reached more than one way. This page is the dispatch over **how** `/io ical` gets at your events — the trade-offs, and which is wired today. Per [[DAS granularity]], these are *surfaces within* the calendar capability, not separate skills. (Naming: the local Apple/EventKit surface is `/io ical`; the server-side Google Calendar API surface, once wired, is `/io gcal`.)

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — EventKit** | every calendar in the local macOS Calendar (iCloud + the Google accounts that sync into it) — **read and write** | none — the calling process holds a one-time macOS Calendar (TCC) grant, which covers both | **✅ working** |
| **Cloud — Google Calendar API** | a specific Google account's calendar server-side | the existing Google OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (same one `/io gsheet` etc. use) | **🔶 available, not yet wired** |
| **AppleScript (`osascript`)** | the local Calendar via Calendar.app scripting | none | ⚪ rejected — ~18s per query (the `whose` clause scans the whole event store); EventKit does the same in ~1s |

## Local — EventKit (default, working)

Queries the local Calendar store's indexed predicate directly via `scripts/calendar-today.swift` (run through the `swift` interpreter). **No tokens, no API keys** — the local Calendar already aggregates every synced account, so it is a superset of the Google calendars with no expiring permission to renew. Best for: "what's on my calendar today", morning briefings, "what do I have tomorrow" — and, since 2026-08-20, **creating events**: `scripts/calendar-write.swift` does `list` / `create` / `show` / `delete`, with `--dry-run` on both mutating verbs. Recipes live in [[io-ical]].

**One TCC grant covers both halves** — each script calls `requestFullAccessToEvents`, the macOS 14+ full-access API, and adding writes raised no second prompt (verified 2026-08-20). Remaining limits: **whole-day offsets only** on the reader; **no in-place edit** of an existing event and **no recurring-series handling** beyond `.thisEvent` on the writer — delete-and-recreate is the supported edit.

## Cloud — Google Calendar API (available via existing Google auth)

Goes to Google's servers directly — reaches a single Google account's calendar server-side, including calendars not mirrored into the local Calendar. Uses the **same Google OAuth** already in place for Sheets/Slides/Docs/Drive, so no new credential is needed — it just needs the Calendar scope added and a verb wired. Best for: a Google calendar that does not sync locally, or scripting against one account server-side. **Not yet implemented** — the auth path exists; the verb doesn't.

## Which to use

- **Reading your calendar on this Mac** → local EventKit (`/io ical`). It's working now and spans every account that syncs into the local Calendar.
- **A Google calendar that isn't mirrored locally** → Google Calendar API, once wired.

Default to **local** — it aggregates every account and needs no renewable permission.
