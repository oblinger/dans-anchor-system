# imail — Access Methods

Email can be reached more than one way. This page is the dispatch over **how** `/io imail` gets at your mail — the trade-offs, and which is wired today. Per [[DAS granularity]], these are *surfaces within* the email capability, not separate skills. (Naming: the local Apple-Mail surface is `/io imail`; the server-side Gmail-API surface is [[io-gmail|`/io gmail`]] — the `i`/`g` prefix marks which surface, not which account. Both are wired as of 2026-08-11.)

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — Apple Mail** | every account configured in Mail.app (iCloud, Gmail, work, …), already-downloaded messages | none — Mail.app holds the credentials; we drive it via AppleScript | **✅ working** |
| **Cloud — Gmail API** | a specific Google account's mail server-side (search the full mailbox, not just what's downloaded) | the existing Google OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (same one `/io gsheet` etc. use) — **Gmail scopes already granted** | **✅ wired — [[io-gmail]]** |
| **IMAP (direct)** | any IMAP server directly | per-account app-password | ⚪ not planned (Apple Mail already aggregates these) |

## Local — Apple Mail (default, working)

Drives Mail.app via AppleScript (`osascript`). **No tokens, no API keys** — Mail.app already authenticated every account. Best for: "read my email", "what's in my inbox", "search mail for X", "find that email from Y". Sees **all** accounts at once (verified 2026-06-11: iCloud + 3× gmail + work, live inbox read).

Recipes live in [[io-imail]] (read recent, read body, search). Limits: only messages Mail.app has **downloaded** locally; read-and-search only (no send yet); requires Mail.app running / Automation permission (granted on this machine).

## Cloud — Gmail API (available via existing Google auth)

Goes to Google's servers directly — searches the **full** mailbox (including mail not downloaded locally), one Google account at a time. Uses the **same Google OAuth** already in place for Sheets/Slides/Docs/Drive, so no new credential is needed. Best for: deep server-side search, very large mailboxes, or scripting against a single Gmail account.

**Less is missing than this page used to claim** (measured 2026-08-11). The scope half is done: `gsa gmail accounts` reports `oblinger@gmail.com` holding `gmail.readonly`, `gmail.modify`, `gmail.labels`, `gmail.send`, `gmail.compose` and `gmail.settings.basic` from the 2026-08-05 re-consent. The CLI half is done too — `gsa gmail search <query>` / `read <msg-id>` / `accounts` / `auth <email>` all work today, take `--account` and `--limit`, and `auth` onboards **additional** mailboxes rather than only the default one. What was missing was *only the `/io gmail` skill card*, so nothing routed to any of it and the surface read as absent. That card landed 2026-08-11 as [[io-gmail]], with the archive-search timing measured against the local route: ~1 second versus ~10 minutes.

**This is the fast path, and its absence has a measured cost.** The local route's honest archive search is **~10 min** over ~253k messages (§ Performance in [[io-imail]]), and scoping narrower to save time is a ~99% miss. Every "search all my mail" question pays that until the verb exists. It also matters per-account: a high-volume feed mailbox is best reached this way and left out of Mail.app entirely, since anything synced locally taxes every unrelated local query.

## Which to use

- **Just looking at mail on this Mac** → local Apple Mail (`/io imail`). It's working now and spans every account.
- **Exhaustive search of one Gmail account's server-side history** → Gmail API, once wired.

Default to **local** unless you specifically need server-side reach into a single Gmail account.
