# imail — Access Methods

Email can be reached more than one way. This page is the dispatch over **how** `/io imail` gets at your mail — the trade-offs, and which is wired today. Per [[DAS granularity]], these are *surfaces within* the email capability, not separate skills. (Naming: the local Apple-Mail surface is `/io imail`; the server-side Gmail-API surface, once wired, is `/io gmail` — the `i`/`g` prefix marks which surface, not which account.)

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — Apple Mail** | every account configured in Mail.app (iCloud, Gmail, work, …), already-downloaded messages | none — Mail.app holds the credentials; we drive it via AppleScript | **✅ working** |
| **Cloud — Gmail API** | a specific Google account's mail server-side (search the full mailbox, not just what's downloaded) | the existing Google OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (same one `/io gsheet` etc. use) | **🔶 available, not yet wired** |
| **IMAP (direct)** | any IMAP server directly | per-account app-password | ⚪ not planned (Apple Mail already aggregates these) |

## Local — Apple Mail (default, working)

Drives Mail.app via AppleScript (`osascript`). **No tokens, no API keys** — Mail.app already authenticated every account. Best for: "read my email", "what's in my inbox", "search mail for X", "find that email from Y". Sees **all** accounts at once (verified 2026-06-11: iCloud + 3× gmail + sportsvisio, live inbox read).

Recipes live in [[io-imail]] (read recent, read body, search). Limits: only messages Mail.app has **downloaded** locally; read-and-search only (no send yet); requires Mail.app running / Automation permission (granted on this machine).

## Cloud — Gmail API (available via existing Google auth)

Goes to Google's servers directly — searches the **full** mailbox (including mail not downloaded locally), one Google account at a time. Uses the **same Google OAuth** already in place for Sheets/Slides/Docs/Drive, so no new credential is needed — it just needs the Gmail scope added and a `/io gmail` verb wired. Best for: deep server-side search, very large mailboxes, or scripting against a single Gmail account. **Not yet implemented** — the auth path exists; the verb doesn't.

## Which to use

- **Just looking at mail on this Mac** → local Apple Mail (`/io imail`). It's working now and spans every account.
- **Exhaustive search of one Gmail account's server-side history** → Gmail API, once wired.

Default to **local** unless you specifically need server-side reach into a single Gmail account.
