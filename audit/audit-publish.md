# Publish — Pre-Publish Audit

Scan files that will be published (to GitHub, npm, crates.io, etc.) for personally identifiable information, credentials, sensitive paths, and other content that should not be made public.

## Workflow

### 1. Determine Published Files

Identify which files will be published:
- If the anchor has a code repo (`cab-config get code`), scan the repo
- Check `.gitignore` — only scan files that would be committed
- If User docs are published with the repo, include those too

### 2. Scan for PII

Search for patterns that indicate personal information:

| Pattern | Example |
|---------|---------|
| Email addresses | `{user}@gmail.com`, `{user}@work` |
| Home directory paths | `/Users/oblinger/`, `~/ob/kmr/` |
| Personal folder structures | vault paths, anchor paths |
| Account names/usernames | hardcoded usernames |
| Phone numbers | `(415) 494-9499` |
| IP addresses | local network IPs |
| API keys/tokens | `sk-`, `ghp_`, `Bearer` tokens |

### 3. Scan for Credentials

| Pattern | What it catches |
|---------|----------------|
| Files named `.env`, `credentials.json`, `*.key`, `*.pem` | Credential files that shouldn't be committed |
| `password`, `secret`, `api_key` in source | Hardcoded credentials |
| OAuth client secrets | `client_secret` values |
| SSH keys | Private key headers |

### 4. Scan for Sensitive Paths

| Pattern | Risk |
|---------|------|
| Absolute paths to user's home | Reveals system layout |
| Paths containing vault structure | Reveals personal organization |
| Paths to `.claude/`, `.config/` | Reveals agent configuration |
| Paths to credential files | Reveals where secrets are stored |

### 5. Report

```
## Audit: Publish — {NAME}
Files scanned: 34
PII found: 2 instances
Credentials: 0
Sensitive paths: 3

PII:
  - src/config.rs:42 — email address "{user}@gmail.com"
  - docs/setup.md:15 — home path "/Users/oblinger/"

Sensitive paths:
  - CLAUDE.md:8 — vault path "~/ob/kmr/prj/"
  - src/main.rs:12 — config path "~/.config/skl/"
  - tests/fixtures.rs:5 — absolute home path
```

### 6. Blocking

If any credentials are found, this audit **blocks publishing**. PII and sensitive paths are warnings — the user decides whether to fix them or accept the exposure.
