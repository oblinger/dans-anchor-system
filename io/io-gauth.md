# /io gauth — Google OAuth Authorization

Re-authorize Google API access when the token expires (every 7 days in Testing mode).

## Steps

### 1. Announce — MANDATORY

Print this to the user before doing anything:

**🔑 Google Reauthorization — Opening browser for Google sign-in. Please authorize when prompted.**

### 2. Run reauth script via box

```bash
ctrl box "python3 ~/.claude/skills/anchor/scripts/gsa-reauth.py"
```

The script opens a browser, user authorizes, tokens are saved automatically.

### 3. Verify

```bash
gsa search sheets
```

If it returns results, auth is working. If it fails, the user may not have completed the browser authorization.

## Accounts

Credentials stored per-email at `~/.google_workspace_mcp/credentials/`:

| Account | File | Status |
|---------|------|--------|
| `{user}@gmail.com` | `{user}@gmail.com.json` | Active — personal |
| Work account | (TBD) | Requires admin approval or separate Cloud project |

## Default Scratch Folder

When creating Google documents without a specific destination:

**Folder ID:** `1iDblgOfxU8B6c_QwffCvKa2xaWHLGd8M`
https://drive.google.com/drive/folders/1iDblgOfxU8B6c_QwffCvKa2xaWHLGd8M

## Notes

- Token expires every 7 days — Google Cloud project `oblio-claude-access` is in Testing mode
- To fix permanently: publish the app in Google Cloud Console
- The reauth script uses `prompt=consent` to always get a fresh refresh token
