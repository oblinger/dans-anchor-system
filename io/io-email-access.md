# Email Access Methods — Reference

Comparison of approaches for accessing email programmatically. No single method covers everything — choose based on your needs.


## Main Approaches

| Method | Personal | Work | Auth Hassle | Search Speed | Send | Offline | Setup |
|--------|----------|------|-------------|-------------|------|---------|-------|
| **Apple Mail (AppleScript)** | ✓ all accounts | ✓ if in Mail.app | None — Mail.app handles it | Fast for inbox, slow for 200K+ | ✗ | ✓ | Zero |
| **IMAP (app password)** | ✓ | ✓ if IT allows | One-time app password, never expires | Fast server-side search | ✗ | ✗ | Generate app password |
| **Gmail API (OAuth)** | ✓ | ✗ unless published | Re-auth every 7 days (Testing mode) or never (Published) | Very fast server-side | ✓ | ✗ | OAuth setup + publish app |
| | | | | | | | |
| **Gmail MCP server** | ✓ | ✗ unless published | Same as Gmail API | Fast | ✓ | ✗ | npm install + OAuth |
| **Chrome/browser** | ✓ | ✓ | Login once | Slow (screenshot-based) | ✓ | ✗ | Chrome extension |
| **Local .emlx files** | ✓ | ✓ | Full Disk Access required | Slow file scan | ✗ | ✓ | Grant permission |
| **Spotlight (mdfind)** | ✓ | ✓ | Full Disk Access required | Very fast (indexed) | ✗ | ✓ | Grant permission |


## Recommendations

**For quick reads and targeted search:** Apple Mail via AppleScript. Zero setup, works with all accounts including work. Best for "show me recent emails from X" or "search inbox for Y."

**For bulk/programmatic access:** IMAP with app password. Never expires, fast server-side search, works with personal and work (if IT allows). Best for "search all 200K emails for X."

**For sending email:** Gmail API (if you publish the app) or IMAP with SMTP. Apple Mail can send via AppleScript too but it's clunky.


## Account Status

| Account | Apple Mail | IMAP | Gmail API |
|---------|-----------|------|-----------|
| {user}@gmail.com | ✓ (232K msgs) | Not configured | Token expired (7-day) |
| {user}@work | ✓ (12K msgs) | Not configured | Not set up |
| {user}@gmail.com | ✓ (1.7K msgs) | Not configured | Not set up |
| iCloud | ✓ | Not configured | N/A |


## Auth Details

### Apple Mail
No auth needed. Mail.app maintains its own connections to all configured accounts. AppleScript talks to Mail.app, not to email servers directly.

### IMAP App Password
Generate at https://myaccount.google.com/apppasswords (requires 2FA enabled). 16-character password that never expires. Store in `.skl/io/imap.yaml` (gitignored). Revoke anytime from Google Account settings.

### Gmail API OAuth
Credentials at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`. Scopes include gmail.readonly, gmail.modify, gmail.send. **Problem:** Token expires every 7 days if the Google Cloud project (`oblio-claude-access`) is in "Testing" mode. **Fix:** Publish the app in Google Cloud Console → OAuth consent screen → Publish. Once published, tokens auto-refresh indefinitely.

### Work Account (Workspace)
Work Gmail ({user}@work) access depends on IT admin settings:
- **IMAP**: may be enabled or disabled by admin
- **App passwords**: may be enabled or disabled by admin
- **OAuth**: requires the app to be whitelisted by admin
- **Apple Mail**: works if the account is configured in Mail.app (already is)
