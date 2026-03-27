# Email — Read and Search Email

Read, search, and access email through Apple Mail using AppleScript. No OAuth tokens, no API keys — Mail.app handles all authentication natively.

**Access methods comparison:** See [[io-email-access]] for trade-offs between Apple Mail, IMAP, Gmail API, and other approaches.

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
