# local-mail — search the local mail index

Query a **local, offline, full-text index** of the user's mail. `notmuch` answers in **milliseconds**, spans every mirrored account in **one** query, and never touches the network or Mail.app.

Sibling surfaces, all three real and none dominant: [[io-imail]] drives Apple Mail (slow, but sees every configured account and is the only one that **sends**); [[io-gmail]] hits Gmail's servers (one account, ~1 s, reaches mail never downloaded); this page is the fast local corpus. Wiring, install and credentials: [[WIRE Mail Local Index]].

## When to use this rather than a sibling

| Ask | Use |
| --- | --- |
| Search across several accounts at once | **local-mail** — the only surface that can |
| Any repeated / exploratory search | **local-mail** — ~40,000× faster than [[io-imail]] |
| Working offline | **local-mail** — the only one that works |
| Send or compose | [[io-imail]] — this index is **read-only by construction** |
| An account not mirrored, when completeness matters | [[io-imail]] (all accounts) or [[io-gmail]] (one account, server-side) |
| `dan@sportsvisio.com` | **local-mail** or [[io-imail]] — **[[io-gmail]] cannot reach it**, org policy blocks the API |

## 🚨 Check coverage before believing a zero

**An empty result means "no match *in what has been mirrored*" — which is not the same as "no such mail."** An account that was never fetched returns zero and looks exactly like a genuine miss. This is the one failure mode of this surface, and it is silent.

    mailsync --status          # per-account message counts on disk

[[Emails]] records which accounts are mirrored at all and why the others are not. If the account you need is missing or partial, **say so in your answer** or switch to [[io-imail]] — do not report a zero as though the corpus were complete.

## Recipes

    notmuch search 'from:stripe.com and date:2026-01-01..'
    notmuch search --format=json 'tag:sportsvisio and subject:invoice'
    notmuch search --output=files 'attachment:pdf and date:2026-06-01..'
    notmuch count 'tag:wef234'
    notmuch show --format=json id:{message-id}

`--format=json` is the one to reach for when parsing: it returns authors, subject, date, tags and thread IDs as structured data, with no delimiter guessing. `--output=files` gives Maildir paths for reading raw messages directly.

**Query syntax** is Xapian-backed: `from:` `to:` `subject:` `attachment:` `tag:` `date:A..B` `is:` `thread:` `path:`, combined with `and` / `or` / `not` and parentheses. Unlike Gmail's syntax, bare terms match the **full body text**.

## Account tags

Every message carries a tag naming the account it came from — `oblinger`, `sportsvisio`, `wef234`, `feedbag333`, `dqe1412`. **These are derived from the on-disk path, not from headers**, deliberately: Gmail rewrites `To:` and `Delivered-To:` on forwarded and group-delivered mail, so the header lies about which mailbox a message actually arrived in and the path does not.

## Keeping it current

    mailsync                   # fetch new mail for every account, then reindex
    mailsync {account}         # one account
    mailsync --index-only      # reindex what is on disk; no network
    mailsync --check           # per-account auth + server-side counts, ~2 s

Fetching is incremental and resumes through Gmail's socket timeouts. Indexing is cheap — measured **430 files/sec** — so `--index-only` is nearly free after any manual change to `~/Mail/`.

## Cross-references

- [[WIRE Mail Local Index]] — the mechanism: mbsync, Maildir layout, Keychain credentials, bring-up, the TCC dead end that made this necessary.
- [[Emails]] — which addresses exist and which are mirrored. The single source of truth; this page never restates it.
- [[io-imail]] · [[io-gmail]] — the sibling surfaces.
