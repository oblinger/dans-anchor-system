# gmail — Gmail API (one account, full server-side history)

Search and read mail through the Gmail API. Reaches **one account's complete server-side archive**, including everything that was never downloaded to this Mac. (`gmail` = the server-side Google surface; the local Apple-Mail surface that aggregates *every* account on this machine is [[io-imail]].)

**Access methods comparison:** [[io-imail-access]] — trade-offs between Apple Mail, IMAP, the Gmail API, and the rest.

**Drafting an email?** The user's required draft format lives in [[DAS formats]] § Email draft — live markdown (never fenced) so the rendered view pastes into Mail as rich text; `To:`/`CC:`/`Subject:` lines always; bold/italic/lists/plain-URLs allowed; no blockquotes, wiki-links, or em-dashes.

## Commands

```
gsa gmail search <query>                 Search mail (Gmail query syntax)
gsa gmail read   <msg-id>                Print one message with its body
gsa gmail accounts                       List authorized mailboxes
gsa gmail auth   <email> [redirect-uri]  Authorize another mailbox

  --account <email>   pick the mailbox (default oblinger@gmail.com)
  --limit <n>         results to list (default 25)
```

`search` prints a header line — `5 shown / ~201 matched  q=<query>  account=<email>` — then one row per message: id, date, sender, subject. Feed an id straight to `read`.

```bash
gsa gmail search "in:anywhere from:anthropic.com" --limit 5
gsa gmail read 19f824a068a9f581
```

## `in:anywhere` is not optional

A bare query searches the **inbox and labeled mail only**. `in:anywhere` is what reaches the archive, Spam and Trash — which is where nearly everything lives, because Gmail archives by default and a message keeps a labeled folder only if it *has* a label.

This is the same ~99% miss the local surface has, measured on the same corpus: **all labeled folders across three accounts returned 1 hit; the archive returned 739** ([[io-imail]] § Performance). Scoping narrow does not return a smaller answer, it returns a **clean-looking wrong** one. Put `in:anywhere` in every search meant to be complete.

## Which surface to reach for

Both are correct; they cover different things, and neither is a superset.

- **[[io-imail]] (local Apple Mail)** — *every* account configured on this Mac, but only what has been **downloaded locally**. Composing, reading, and anything that should span all mailboxes at once.
- **`gmail` (this card)** — **one** account, its **entire** server-side history, whether or not it ever synced. Archive search, and anything that must be fast or repeated.

**The speed gap is the whole reason this surface exists.** Measured 2026-08-11, same machine, both routes against the full archive:

| Route | Scope | Wall clock |
|---|---|---|
| `gsa gmail search "in:anywhere …"` | full server-side archive, one account | **~1 s** |
| `imail` combined `whose` clause | ~253,000 messages, three accounts | **~10 min** |

Ten minutes is usable once and unusable in a loop. If a question needs the archive more than once, it belongs here.

**The design consequence, per [[ATT|Atticus]]:** a high-volume mailbox is best reached through `gmail` and deliberately kept **out of Mail.app**. Anything synced locally is walked by every unrelated local query, so removing a large account from Mail.app makes every `imail` search faster without losing any reach — the Gmail API still has all of it.

## Believe a zero only after a control test

A "no results" is a claim about the query as much as about the mailbox. Re-run with a term *known* to be present and confirm it comes back before reporting an absence. The control is cheap here — one second — and it separates "never happened" from "my query was broken."

Verified 2026-08-11: a nonsense term returns `0 shown / ~0 matched`, cleanly, rather than erroring. A zero from this surface is a real zero once the control passes.

## Auth

Already granted, and nothing needs doing. `gsa gmail accounts` reports `oblinger@gmail.com` holding `gmail.readonly`, `gmail.modify`, `gmail.labels`, `gmail.send`, `gmail.compose` and `gmail.settings.basic` from the 2026-08-05 re-consent.

Other mailboxes need `gsa gmail auth <email>` once each. Google OAuth tokens expire where the Apple surfaces' TCC grants do not — that asymmetry is why [[io/SKILL]] ranks local surfaces first, and it is the one recurring cost of this route. When a token lapses, `/fix gauth`.

## Related

- [[io-imail]] — the local Apple Mail surface, and its measured performance table
- [[io-imail-access]] — every access method compared, with the trade-offs
- [[io/SKILL]] — the `/io` dispatch table and the local-first ranking
