# Fix: Apple Mail Delete Key Archives Instead of Deleting

Configure Apple Mail so the Delete key archives messages (moves to All Mail) instead of moving them to Trash.

## Runbook

### 1. Apple Mail settings

- Open Mail → Preferences → Accounts
- Select the Gmail account → Mailbox Behaviors → Trash
- **Uncheck** "Store deleted messages on server" — this is the key setting
- Leave "Move deleted messages to trash" checked

### 2. Gmail web settings

- Go to Gmail → Settings → Forwarding and POP/IMAP
- Under "When a message is marked as deleted and expunged from the last visible IMAP folder"
- Select **"Archive the message"**

### 3. Report

---

**>>> USER ACTION: Change settings in Mail.app Preferences and Gmail web settings <<<**

**>>> USER ACTION: Change settings in Mail.app Preferences and Gmail web settings <<<**

**>>> USER ACTION: Change settings in Mail.app Preferences and Gmail web settings <<<**

---

Both the Mail.app setting and the Gmail server setting must be changed for this to work correctly.
