---
name: io
description: >
  External system I/O — read from and write to external applications and services.
  Google Workspace: Sheets, Slides, Drive, Docs. Apple: Mail, Calendar, Health.
  Use when the user says: "put this in sheets", "read the spreadsheet", "update the slides",
  "upload to drive", "read my email", "search mail for", "find that email from",
  "what's on my calendar", "read my calendar", "what do I have today",
  "pull my health data", "what's my sleep/heart rate", "check my apple health".
  "look up a contact", "what's their phone number", "find them in my contacts", "how do you spell their name".
  "search my mail fast", "search all my accounts at once".
  Subcommands: /io gsheet, /io gslide, /io gdoc, /io gdrive, /io gmail, /io imail, /io local-mail, /io ical, /io ihealth, /io contacts, /io excel, /io pptx, /io notion.
tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
user_invocable: true
---

# IO — External System I/O
requires:: external:ctrl, external:gsa
subsystem:: [[DAS Doc Design]] — the Doc group's subsystem profile

Read from and write to external services. Each sub-skill is an access card with ranked methods.

**Command naming — a set of usable names, not an enforced scheme.** `g*` = Google cloud API (server-side, one account, expiring token): `gsheet`, `gslide`, `gdoc`, `gdrive`, `gmail`, and the future `gcal`. `i*` = Apple/local macOS frameworks (aggregate every account on this Mac): `imail`, `ical`, `ihealth`. The prefix marks *which access surface*, not which account — `imail` (local Apple Mail) already reads your Gmail if it syncs into Mail.app; `gmail` hits Gmail's API directly.

**The prefix is a convenience, and it stops where it stops being usable** (Dan, 2026-08-11). `imail` and `gmail` earn their compression by being said constantly — the voice engine has learned them. A one-letter prefix on a rarely-spoken name buys a few characters and costs recognition: `lmail` for the local index was rejected on exactly that ground, in favour of **`local-mail`**, which dictates and parses cleanly. *"I don't think we need consistency. We just need to have a set of names for things."* So do not extend the scheme by reflex — name a new surface whatever a person can reliably say out loud.

## Routing policy — local first, MCP last (F004, reaffirmed 2026-08-05)

**Prefer the surface that needs no expiring credential.** Ranked, and the ranking is the point:

1. **Local Apple frameworks (`i*`)** — `imail`, `ical`, `ihealth`, `contacts`. A TCC grant is given once and does not expire; an OAuth token does. Local is also a **superset** for calendar (Family / Birthdays / iCloud calendars were never reachable through Google at all). Established by [[F004 — Calendar via local macOS Calendar, not Google OAuth|LUMEN F004]] in the user's own words: *"Google permissions really suck — they don't stay active."*
2. **`gsa` CLI (`g*`)** — the direct Google API client for Sheets, Slides, Docs, and Drive search. **No MCP server involved.** Verified working 2026-08-05.
3. **The `workspace-mcp` server** — the fallback of last resort, and only for Google surfaces `gsa` does not implement (Gmail API, Chat, Forms, Apps Script).

**Use the MCP server for as little as possible.** It is one more moving part on the same single credential store, and two independent failures make it the weakest link:

- **It is not currently reachable as an MCP.** `claude mcp list` reports no servers — an `ANTHROPIC_API_KEY` precedence warning blocks registration, so `ob_boot` re-registers it into a void at every login. The server itself is healthy on `:8000`; only the Claude Code integration is broken. Reaching it means speaking JSON-RPC over HTTP by hand.
- **Its token expires every 7 days** (the OAuth app is in Testing mode), and nothing probes it — so the credentials rot silently and the first symptom is an unrelated task failing. See [[ATT Backlog#^T229|ATT T229]].

**One credential store, two clients.** `gsa` and `workspace-mcp` both read `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`. There are not two OAuth paths to repair — one consent fixes both. When re-consenting, **tick "Select all"**: the permission checkboxes default to unchecked, and clicking straight through grants `email`/`profile`/`openid` only, which then fails as HTTP 403 *insufficient scopes* rather than as an auth error.

**The one measured exception to local-first.** Searching the whole archive is a Google job, not a local one — but the local path does work, contrary to what this line used to claim. Re-measured 2026-08-10: one combined `whose` clause over ~253k All Mail messages across three accounts finished in **~10 minutes** and returned its hits. The earlier "timed out at ~40 minutes" was a query with **no `with timeout of N seconds` wrapper**, dying at the 120-second Apple Event default and reporting nothing. Mail's SQLite index is still TCC-blocked to the shell, so there is no filesystem shortcut. **Mail is the standing exception to the local-first ranking: the index outranks `imail`.** Search and bulk reading go to **[[io-local-mail|`/io local-mail`]]** (`notmuch`, ~15 ms) — `R-ob-osascript-01` denies AppleScript mail search outright. `imail` is the **router** for mail on this Mac and the surface for the two things the index cannot do: showing Dan a message in the Mail window, and reaching an account that genuinely is not mirrored. Reach for **[[io-gmail|`/io gmail`]]** when archive search must be fast or repeated, or when the mirror is blind — the same archive answers in **~1 second** there against the local route's ten minutes, measured 2026-08-11. Measured table and the pitfalls: [[io-imail]] § Performance and [[io-gmail]].

## Actions

| Group | Usage | File | Description |
|-------|-------|------|-------------|
| **Apple** | `/io imail` | [[io-imail]] · [[io-local-mail]] | Email via **local Apple Mail** (working) — *every* account on this Mac, but only what is downloaded locally. Composing lives here. For one account's full server-side archive, use [[io-gmail\|`/io gmail`]]. Access methods: [[WIRE Mail]]. |
| **Local** | `/io local-mail` | [[io-local-mail]] · [[WIRE Mail Local Index]] | **Fastest mail route by four orders of magnitude** (~15 ms vs `imail`'s ~10 min), works offline, and the only surface that searches several accounts in **one** query. Read-only. The mirror is still filling — check `mailsync --status` and [[Emails]] before believing a zero result. |
| **Apple** | `/io ical` | [[io-ical]] · [[io-ical-access]] | Calendar via **local macOS Calendar** (EventKit, working) — **read and write**: today's events or `+N` days ahead, and create / show / delete events with notes, alarms and all-day spans. Superset of the synced Google calendars. Server-side Google Calendar surface would be `/io gcal`. See [[io-ical-access]]. |
| **Apple** | `/io ihealth` | [[io-ihealth]] | Apple Health / HealthKit — **local daily JSON drop** (working, no auth): sleep, heart rate, HRV, activity, overnight vitals, gait. One file per day off the Watch/iPhone. Pipe + traps: [[WIRE Health Auto Export]], [[LUMEN Data Sources]]. |
| **Apple** | `/io contacts` | [[io-contacts]] | macOS **Contacts** (read-only) — `search` / `show` / `count` over every account synced to this Mac, no auth. Use it instead of hand-written `osascript`; a zero names the corpus so an empty result is never confused with a broken reader. |
| **Google** | `/io gsheet` | [[io-gsheet]] | Google Sheets |
| **Google** | `/io gslide` | [[io-gslide]] | Google Slides |
| **Google** | `/io gdoc` | [[io-gdoc]] | Google Docs |
| **Google** | `/io gdrive` | [[io-gdrive]] | Google Drive search |
| **Google** | `/io gmail` | [[io-gmail]] | **Gmail API** (working) — one account's *complete* server-side history, archive included. ~1 s where the local route takes ~10 min. `in:anywhere` is mandatory or the search misses ~99%. |
| **Google** | `/io gauth` | → `/fix gauth` | Re-authorize Google OAuth (when token expires) |
| **Microsoft** | `/io excel` | [[io-excel]] | **Excel** — local `.xlsx`, live-coordinated (save-before-read / reload-after-write), formatting-preserving |
| **Microsoft** | `/io pptx` | [[io-pptx]] | **PowerPoint** — local `.pptx`, live-coordinated (same handshake as excel); slides/bullets/notes via python-pptx, unmodeled parts survive |
| **Notion** | `/io notion` | [[io-notion]] | Notion pages and databases (TBD) |

## Auth

Google API: OAuth at `~/.google_workspace_mcp/credentials/{account}.json` — **one directory, both clients** (`gsa` and `workspace-mcp`), one file per authorized account. Token expires every 7 days (Testing mode). Re-consent via `/io gauth`, and see § Routing policy for the "Select all" trap that silently grants zero API scopes.

**There is more than one account, and the account is a parameter on every `g*` surface.** `gsa --account <email>` (or `$GSA_ACCOUNT` for a whole session) selects the identity for sheets, slides, docs, drive search **and** gmail; omitted, everything runs as `oblinger@gmail.com`. `gsa gmail accounts` lists what is authorized and which scopes each holds — check it before concluding a document is missing, because **a file you cannot see is far more often the wrong identity than a real absence**: the personal account gets a clean `404` on a SportsVisio doc, which reads exactly like "no such file".

Until 2026-08-28 `--account` was parsed in the `gmail` branch alone, which was backwards — `dan@sportsvisio.com` holds documents/drive/spreadsheets/presentations and **no** Gmail scope, so the one service it could be addressed on was the one it is not authorized for. The flag is now global.

Apple surfaces (`imail`, `ical`, `ihealth`, `contacts`) carry **no auth here** — they run on TCC grants that do not expire, which is the whole reason they rank first. They are also the only surfaces that are natively multi-account: `imail` reads every mailbox on this Mac at once, where each `g*` call speaks as exactly one identity.

Last full re-consent: **2026-08-05**, 41 scopes granted on `oblinger@gmail.com` (Gmail, Sheets, Docs, Drive, Slides all live). `dan@sportsvisio.com` last granted 2026-08-13, 6 scopes, and its refresh token is **expired or revoked** as of 2026-08-28 — `gsa auth dan@sportsvisio.com` re-consents it.

**Read the credential file's `scopes` list as a REQUEST, not a grant.** Both files carry an identical 39 entries — full `drive` plus seven `gmail.*` — because that is what the client asks for; what an account actually holds is whatever was ticked at consent, which for the SV account was 6. A scope present in the file and absent from the grant is exactly the shape that makes a 404 read as *no such document* rather than *not authorized*.

**Publishing this app out of Testing is not a switch.** `drive` and every `gmail.*` scope are **restricted** tier, so leaving Testing needs OAuth verification plus an annual third-party CASA security assessment — weeks and money. The 7-day expiry is a property of *this app*, not of Google Drive.

**Drive access need not come through `gsa` at all.** `rclone` carries two independent remotes — `gdrive:` (personal, `oblinger@gmail.com`) and **`svdrive:`** (SportsVisio, its own `client_id`; verified working 2026-08-28, listing SV Root and reporting 54 TiB of pooled Workspace storage). They fail independently, so a dead `gsa` grant says nothing about `svdrive:`, and a task that only needs Drive *files* moved should reach for rclone before re-consenting anything. Whether `svdrive:` can **write** SV-owned files is the open question — [[TINK Backlog#^T610|TINK T610]].

IDs accept full Google URLs or bare document IDs.

## Dispatch

1. Parse the argument to determine the action
2. Read the sub-skill file — it lists ranked methods
3. Try method 1. If it fails, try method 2.
