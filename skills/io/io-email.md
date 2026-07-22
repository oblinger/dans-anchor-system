# Email — Read and Search Email

Read, search, and access email through Apple Mail using AppleScript. No OAuth tokens, no API keys — Mail.app handles all authentication natively.

**Access methods comparison:** See [[io-email-access]] for trade-offs between Apple Mail, IMAP, Gmail API, and other approaches.

**Drafting an email?** The user's required draft format lives in [[DAS formats]] § Email draft — live markdown (never fenced) so the rendered view pastes into Mail as rich text; `To:`/`CC:`/`Subject:` lines always; bold/italic/lists/plain-URLs allowed; no blockquotes, wiki-links, or em-dashes.

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
set mbox to mailbox "Sent Mail" of account "oblinger@gmail.com"
-- ERROR: Mail got an error: Can't get mailbox "Sent Mail" of account ...
```

Two methods that DO work:

**Method 1 — bracketed IMAP path** (fast, exact name):
```applescript
set mbox to mailbox "[Gmail]/All Mail" of account "oblinger@gmail.com"
set mbox to mailbox "[Gmail]/Sent Mail" of account "oblinger@gmail.com"
```

**Method 2 — iterate and match by name** (robust across accounts; needed if you don't know the exact path):
```applescript
set acct to account "oblinger@gmail.com"
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

### Performance

Single combined `whose` clause searches across 235k+ All Mail messages return in seconds — Mail's local Spotlight index does the heavy lifting. **Combine all filters into one `whose` clause** rather than fetching all messages then filtering in AppleScript; the latter can take many minutes.

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
