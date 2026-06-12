# Fix: Google OAuth Reauthorization

Re-authorize Google API access when the token expires. The Google Cloud project `oblio-claude-access` is in Testing mode, so tokens expire every 7 days.

## Runbook

### 1. Announce

Print this to the user before doing anything:

---

**>>> AUTHORIZE IN BROWSER — A Google sign-in page will open. Please authorize when prompted. <<<**

**>>> AUTHORIZE IN BROWSER — A Google sign-in page will open. Please authorize when prompted. <<<**

**>>> AUTHORIZE IN BROWSER — A Google sign-in page will open. Please authorize when prompted. <<<**

---

### 2. Run reauth script via box

```bash
ctrl box "python3 ~/.claude/skills/anchor/scripts/gsa-reauth.py"
```

The script opens a browser, user authorizes, tokens are saved automatically to `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`.

### 3. Verify

```bash
gsa search sheets
```

If it returns results, auth is working. If it fails, the user may not have completed the browser authorization.

## Accounts

| Account | File | Status |
|---------|------|--------|
| `{user}@gmail.com` | `{user}@gmail.com.json` | Active — personal |

## Default Scratch Folder

When creating Google documents without a specific destination:

**Folder ID:** `1iDblgOfxU8B6c_QwffCvKa2xaWHLGd8M`
https://drive.google.com/drive/folders/1iDblgOfxU8B6c_QwffCvKa2xaWHLGd8M

## Why This Happens

Google Cloud project `oblio-claude-access` is in Testing mode — tokens expire every 7 days. To fix permanently: publish the app in Google Cloud Console (requires verification).
