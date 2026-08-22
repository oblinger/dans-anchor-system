# imail — Apple Mail (read & search)
The Apple Mail surface — the only one that can **send**, and the wrong one for searching.

> ## 🚨 DO NOT SEARCH MAIL FROM HERE — USE THE INDEX
>
> **Searching with AppleScript against Mail.app is forbidden.** Use **[[io-local-mail|`/io local-mail`]]** (`notmuch`) — milliseconds instead of minutes, every mirrored account in one query, no GUI app involved.
>
> The user, 2026-08-13, after a ten-minute sweep: *"I don't know what you're doing here with OSA script, but I don't think you should be doing it. If you want to look in my email, you should not be using that. There's an index on my email that you should be using… You gotta put a remembrance in for this, man. This has happened multiple times."*
>
> **A zero from the index is not permission to come back here.** Run `mailsync --status`; if the account you need shows 0, run `mailsync <account>` and **tell the user** — including when it fails, which it can (`PassCmd exited with status 44` on the `oblinger` account, 2026-08-13). A broken mirror is a bug to report, not a reason to fall back to a slow sweep.
>
> **What this page is still for:** **composing and sending** — the index is read-only by construction — and reaching an account that genuinely is not mirrored, *after* the mirror has been tried and the user has been told. Even then scope tightly and always wrap in `with timeout of N seconds`; the Apple Event default is 120 s and it dies silently.
>
> **Not sure where to look?** Order and shipping details are usually faster from the retailer's own order history in a real browser session on haorui than from mail at all.

Read, search, and access email through Apple Mail using AppleScript. No OAuth tokens, no API keys — Mail.app handles all authentication natively. (`imail` = the local Apple-Mail surface; the server-side Gmail-API surface is [[io-gmail|`/io gmail`]], wired 2026-08-11.)

**Access methods comparison:** See [[WIRE Mail]] for trade-offs between Apple Mail, IMAP, Gmail API, and other approaches.

**Drafting an email?** The user's required draft format lives in [[DAS formats]] § Email draft — live markdown (never fenced) so the rendered view pastes into Mail as rich text; `To:`/`CC:`/`Subject:` lines always; bold/italic/lists/plain-URLs allowed; no blockquotes, wiki-links, or em-dashes.

## Composing — staging a draft for the user to send

**Use `~/ob/grove/commons/arec/stage-email`.** It creates exactly one visible composition window and **never sends**.

```
stage-email --to A[,B] [--cc C] --subject S --body-file F --from ADDR --agent SLUG [--wait N] [--routine]
```

**Every recipient is staged with a safety catch — a trailing `@` on the address, followed by the staging agent's one- or two-letter tag** (`will@fractional.ai@s`) — so Mail refuses the message locally and it cannot leave the machine. **Dan deletes that tail to arm the draft**; that is the deliberate act that makes sending his. **Always pass `--agent`**: the catch is the only place an agent name can be written that cannot ride along on the sent message, so it never goes in the subject, the body or a header. Pass `--routine` only when the destination is genuinely low-stakes. **It also reads the draft back after staging** (window count, subject, recipients, sender, body) and exits 6 rather than reporting a success it did not verify — two staging attempts on 2026-08-21 returned 0 while the window came up blank.

**Fixtures never use a real contact — test against `wef234@gmail.com`.**

**It refuses (exit 3) while any draft is already open, and clears nothing.** That is the whole safety property: an agent that closes existing drafts to simplify its own verification destroys whatever the user was editing — which happened on 2026-08-20. On exit 3, tell the user what is in the way and retry with `--wait 180`.

Full routine, gotchas and constraints: [[AREC Stage Email]].

## Reading Recent Messages

```applescript
osascript -e '
tell application "Mail"
    set msgs to messages 1 thru 5 of inbox
    set output to ""
    repeat with m in msgs
        set subj to subject of m
        set sndr to sender of m
        set dt to date received of m
        set output to output & dt & "  " & sndr & "  " & subj & linefeed
    end repeat
    return output
end tell'
```

## Reading a Message Body

```applescript
osascript -e '
tell application "Mail"
    set m to message 1 of inbox
    set subj to subject of m
    set sndr to sender of m
    set body_text to content of m
    return "FROM: " & sndr & linefeed & "SUBJECT: " & subj & linefeed & linefeed & body_text
end tell'
```

## Searching Messages

```applescript
osascript -e '
tell application "Mail"
    set acct to account "Gmail"
    set mbox to mailbox "INBOX" of acct
    set matches to (messages of mbox whose subject contains "workflow")
    set output to ""
    repeat with m in matches
        set subj to subject of m
        set sndr to sender of m
        set output to output & sndr & "  " & subj & linefeed
    end repeat
    return output
end tell'
```

## Search Filters

AppleScript `whose` clause supports:
- `subject contains "keyword"`
- `sender contains "name@example.com"`
- `date received > date "March 1, 2026"`
- `read status is false` (unread)
- `was forwarded is false`

Combine with `and`/`or`:
```
messages whose subject contains "meeting" and sender contains "boss@work.com"
```

## Listing Mailboxes

```applescript
osascript -e '
tell application "Mail"
    set output to ""
    repeat with acct in accounts
        set acctName to name of acct
        repeat with mbox in mailboxes of acct
            set output to output & acctName & " / " & name of mbox & linefeed
        end repeat
    end repeat
    return output
end tell'
```

## Reading from Specific Account/Mailbox

```applescript
osascript -e '
tell application "Mail"
    set mbox to mailbox "INBOX" of account "Gmail"
    set msgs to messages 1 thru 3 of mbox
    ...
end tell'
```

## Notes

- Mail.app must be running (AppleScript will launch it if not, but first launch is slow)
- Messages are indexed locally — search is fast
- Works with any account configured in Mail.app (Gmail, iCloud, Exchange, etc.)
- No tokens to refresh, no OAuth to configure
- For large result sets, limit with `messages 1 thru N` to avoid slowness
- Reading message body (`content of m`) returns plain text; use `source of m` for raw MIME

## Gotchas & Recipes — verified 2026-06-11

### Discovering the mailbox structure first

List all accounts × mailboxes BEFORE constructing a search. The "right" mailbox name and the account label vary per machine:

```applescript
tell application "Mail"
    set output to ""
    repeat with acct in accounts
        set acctName to name of acct
        repeat with mbox in mailboxes of acct
            set output to output & acctName & " / " & name of mbox & linefeed
        end repeat
    end repeat
    return output
end tell
```

### Gmail: `All Mail` and `Sent Mail` are NOT addressable by their plain name

This LOOKS like it should work but **fails**:
```applescript
set mbox to mailbox "Sent Mail" of account "{user}@gmail.com"
-- ERROR: Mail got an error: Can't get mailbox "Sent Mail" of account ...
```

Two methods that DO work:

**Method 1 — bracketed IMAP path** (fast, exact name):
```applescript
set mbox to mailbox "[Gmail]/All Mail" of account "{user}@gmail.com"
set mbox to mailbox "[Gmail]/Sent Mail" of account "{user}@gmail.com"
```

**Method 2 — iterate and match by name** (robust across accounts; needed if you don't know the exact path):
```applescript
set acct to account "{user}@gmail.com"
repeat with mb in mailboxes of acct
    if (name of mb) = "Sent Mail" then set sentBox to mb
    if (name of mb) = "All Mail" then set allBox to mb
end repeat
```

`INBOX` works addressed directly (`mailbox "INBOX" of account "..."`). iCloud uses `Sent Messages` (not `Sent Mail`); iCloud has no `All Mail` virtual folder.

### Sender filter — use the domain, not a full email

`whose sender contains "anthropic.com"` works. Disjunction with `or` works across many senders:
```
messages of mb whose date received > cutoff and (sender contains "anthropic" or sender contains "greenhouse" or sender contains "Last Name")
```

### Recipient filter — no `whose` clause; iterate `to recipients` per message

Recipient addresses cannot be filtered in the `whose` clause directly (`whose to recipient address contains "..."` errors). Pattern: pull all sent messages in the date range, then per-message gather `address of r` for each `r in (to recipients of m)` and `cc recipients of m`, then string-match:

```applescript
set msgs to (messages of sentBox whose date sent > cutoff)
repeat with m in msgs
    set recips to ""
    repeat with r in (to recipients of m)
        set recips to recips & "," & (address of r)
    end repeat
    repeat with r in (cc recipients of m)
        set recips to recips & ",cc:" & (address of r)
    end repeat
    if recips contains "anthropic.com" then
        -- ... emit ...
    end if
end repeat
```

### Date filter syntax

```applescript
set cutoff to date "Tuesday, May 12, 2026 at 12:00:00 AM"
-- then: whose date received > cutoff   (incoming)
-- or:   whose date sent > cutoff       (outgoing)
```

Day-of-week in the date string is optional but the full long format (with `at` and time) is most reliable across locales.

### Performance — re-measured 2026-08-10, the earlier "in seconds" was wrong

**Combine all filters into one `whose` clause** rather than fetching all messages and filtering in AppleScript. That part holds. What does *not* hold is the old claim that a combined `whose` over a 235k-message All Mail "returns in seconds" — it does not, and [[io/SKILL]] separately recorded the same search "timing out at ~40 minutes." Both were describing a run with **no explicit timeout**. Measured numbers, one combined clause (date cutoff + six `subject contains` disjuncts):

| Scope | Messages | Wall clock |
|---|---|---|
| All *labeled* folders, three accounts | ~19,000 | **25 s** |
| Gmail `All Mail`, three accounts | ~253,000 | **~10 min** |

So: seconds for labeled folders, **ten minutes** for the archive — slow but entirely usable, and *not* the 40-minute wall. Two things make the difference between those two outcomes:

- **Wrap every archive-scale query in `with timeout of N seconds`.** The default Apple Event timeout is **120 seconds**; anything longer dies with `AppleEvent timed out. (-1712)` and returns nothing, which reads as a failed search rather than a slow one. This alone explains the "40 minute timeout" folklore.
- **Run it in the background and poll the output file**, per the section below. Ten minutes is longer than any foreground tool call should hold.

### Do not scope to labeled folders to save time

Gmail archives everything into `All Mail` and a message keeps a labeled folder only if it *has* a label. Measured on the same corpus and the same query: **all labeled folders across three accounts returned 1 hit; `All Mail` returned 739.** Searching INBOX and the user's own folders and calling that a search of their mail is a ~99% miss that looks like a clean result. If the answer must be complete, pay the ten minutes.

**Believe a zero only after a control test.** A "no results" is a claim about the query as much as about the mailbox — re-run with a term *known* to be present and confirm it comes back. Cheap, and it separates "never happened" from "my query was broken."

### There is no filesystem shortcut

`~/Library/Mail`, `~/Library/Containers/com.apple.mail/…` and the Mail group container all **exist but list as empty** to a shell without Full Disk Access, and `mdfind -onlyin` over them returns **0 for every term** — including terms that are definitely present. It fails silently and looks exactly like an empty mailbox. Everything must go through Mail.app via AppleScript.

### Output strategy for long searches

For substantial scans, redirect osascript output to a file and run in background; reading the file back avoids losing output to shell-buffer limits:

```bash
osascript <<'EOF' > /tmp/mail_search.txt 2>&1
... script ...
EOF
```

Use the Bash `run_in_background: true` parameter for searches expected to take >10s.

### One-line scan pattern (incoming + outgoing in one pass)

The full recipe for "find every message to/from a domain in the last 30 days across all accounts" lives at the bottom of `/Users/oblinger/.claude/projects/-Users-oblinger-ob-kmr-RR-Lrn-LRN-Role-LRN-TPM/486b1e27-d6a4-4833-8b63-d071d6ef0bb2.jsonl` (Anthropic-scan example from 2026-06-11) — adapt the date and the disjunction list.
