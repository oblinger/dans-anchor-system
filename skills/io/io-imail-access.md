# imail — Access Methods

Email can be reached more than one way. This page is the dispatch over **how** `/io imail` gets at your mail — the trade-offs, and which is wired today. Per [[DAS granularity]], these are *surfaces within* the email capability, not separate skills. (Naming: the local Apple-Mail surface is `/io imail`; the server-side Gmail-API surface is [[io-gmail|`/io gmail`]] — the `i`/`g` prefix marks which surface, not which account. Both are wired as of 2026-08-11.)

| Method | Reaches | Auth | Status |
|---|---|---|---|
| **Local — Apple Mail** | every account configured in Mail.app (iCloud, Gmail, work, …), already-downloaded messages | none — Mail.app holds the credentials; we drive it via AppleScript | **✅ working** |
| **Cloud — Gmail API** | a specific Google account's mail server-side (search the full mailbox, not just what's downloaded) | the existing Google OAuth at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` (same one `/io gsheet` etc. use) — **Gmail scopes already granted** | **✅ wired — [[io-gmail]]** |
| **Local mirror + index** | every *mirrored* account at once, offline, full history once fetched | app-specific password in the login Keychain (`mbsync-{account}`) | **🟡 wired, filling** — [[WIRE Mail Local Index]] |

**Latency is the whole reason there are three.** Measured 2026-08-11 on this machine, same corpus: local index **~15 ms**, Gmail API **~1 s**, Apple Mail **~10 min**. That is not a tuning difference — it decides whether searching mail is something an agent does *in passing* while answering a question, or a thing it must plan around.

## Local — Apple Mail (default, working)

Drives Mail.app via AppleScript (`osascript`). **No tokens, no API keys** — Mail.app already authenticated every account. Best for: "read my email", "what's in my inbox", "search mail for X", "find that email from Y". Sees **all** accounts at once (verified 2026-06-11: iCloud + 3× gmail + work, live inbox read).

Recipes live in [[io-imail]] (read recent, read body, search). Limits: only messages Mail.app has **downloaded** locally; read-and-search only (no send yet); requires Mail.app running / Automation permission (granted on this machine).

## Cloud — Gmail API (available via existing Google auth)

Goes to Google's servers directly — searches the **full** mailbox (including mail not downloaded locally), one Google account at a time. Uses the **same Google OAuth** already in place for Sheets/Slides/Docs/Drive, so no new credential is needed. Best for: deep server-side search, very large mailboxes, or scripting against a single Gmail account.

**Less is missing than this page used to claim** (measured 2026-08-11). The scope half is done: `gsa gmail accounts` reports `oblinger@gmail.com` holding `gmail.readonly`, `gmail.modify`, `gmail.labels`, `gmail.send`, `gmail.compose` and `gmail.settings.basic` from the 2026-08-05 re-consent. The CLI half is done too — `gsa gmail search <query>` / `read <msg-id>` / `accounts` / `auth <email>` all work today, take `--account` and `--limit`, and `auth` onboards **additional** mailboxes rather than only the default one. What was missing was *only the `/io gmail` skill card*, so nothing routed to any of it and the surface read as absent. That card landed 2026-08-11 as [[io-gmail]], with the archive-search timing measured against the local route: ~1 second versus ~10 minutes.

**This is the fast path, and its absence has a measured cost.** The local route's honest archive search is **~10 min** over ~253k messages (§ Performance in [[io-imail]]), and scoping narrower to save time is a ~99% miss. Every "search all my mail" question pays that until the verb exists. It also matters per-account: a high-volume feed mailbox is best reached this way and left out of Mail.app entirely, since anything synced locally taxes every unrelated local query.

## Local mirror + index (fastest; the only offline route)

`mbsync` mirrors each account's `[Gmail]/All Mail` into `~/Mail/`, `notmuch` indexes it, and queries hit a Xapian index — no network, no Mail.app, and **one query spans every mirrored account**, which neither other route can do. Driven by `~/bin/mailsync`; full wiring, credentials and bring-up at [[WIRE Mail Local Index]].

    notmuch search --format=json 'from:stripe.com and date:2026-01-01..'
    notmuch search 'tag:sportsvisio and subject:invoice'
    notmuch show --format=json id:{message-id}

Messages are tagged with their account name, derived from the on-disk path rather than from headers — Gmail rewrites headers on forwarded and group-delivered mail, so the path is the more reliable signal.

**Check coverage before trusting a zero.** This mirror is *filling*, not complete: `mailsync --status` prints per-account counts and `[[Emails]]` records which accounts are mirrored at all. A `notmuch` search over an account that was never fetched returns zero results and looks exactly like "no such mail" — the single most dangerous failure mode on this page. If completeness matters and the account is not fully mirrored, use Apple Mail and pay the ten minutes.

## Which to use

**Route by what the question needs, in this order:**

1. **Anything about a mirrored account** → the local index. It is ~40,000× faster than Apple Mail, works offline, and is the only route that searches several accounts in one query. Confirm coverage first (above).
2. **`dan@sportsvisio.com`** → Apple Mail, or the local index once mirrored. **The Gmail API cannot reach it** — the org disabled API access, which is exactly why the local mirror was built.
3. **Server-side history of one Gmail account not yet mirrored** → [[io-gmail]]. Reaches mail never downloaded locally, ~1 s.
4. **Any account not mirrored, when completeness matters** → local Apple Mail (`/io imail`). Spans every configured account, but ~10 min archive-wide, and narrowing the scope to save time is a ~99% miss.
5. **Sending mail** → Apple Mail or [[io-gmail]]. The local index is **read-only by construction** — `mbsync` runs `Sync Pull` and can never write to a mail server.

Default to **local** unless you specifically need server-side reach into a single Gmail account.
