# Publish — Pre-Publish Audit

Scan files that will be published (to GitHub, npm, crates.io, etc.) for personally identifiable information, credentials, sensitive paths, and other content that should not be made public. **Reports findings only.** Fix work goes into a backlog entry; no files are modified.

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
| Email addresses | `you@gmail.com`, `name@company.com` |
| Home directory paths | `/Users/{user}/`, a personal vault root |
| Personal folder structures | vault paths, anchor paths |
| Account names/usernames | hardcoded usernames |
| Phone numbers | `(555) 123-4567` |
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

### 5. Build the findings table

```
## Audit: Publish — {slug}
Files scanned: 34
PII found: 2 instances
Credentials: 0
Sensitive paths: 3

PII:
  - src/config.rs:42 — email address "you@gmail.com"
  - docs/setup.md:15 — home path "/Users/{user}/"

Sensitive paths:
  - CLAUDE.md:8 — vault path "~/ob/kmr/prj/"
  - src/main.rs:12 — config path "~/.config/skl/"
  - tests/fixtures.rs:5 — absolute home path
```

Print the table. **If `dry` substring is in args**, stop here — print "dry-run — no backlog entry written" (and still print the credential gate verdict from step 7).

### 6. Write the backlog entry

Locate `{slug} Docs/{slug} Plan/{slug} Backlog.md`. Read it, find the lowest unused B-number (per [[DAS Backlog]] § Format), and append a new bullet under `## Upcoming`:

```
- **B<n> — Publish audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit publish`. **Credentials must be cleared before publishing.** Sub-bullets are candidate splits if this needs to be broken up.
  - credentials: <file:line> — <kind>
  - PII: <file:line> — <kind>
  - sensitive-path: <file:line> — <kind>
  - …
```

Order sub-bullets by category: **credentials** first (blocking), then **PII**, then **sensitive-path**. Within each category, sort by file path. Keep each sub-bullet to one line.

If there are zero findings, do **not** write an entry.

### 7. Credential gate (always print, even on dry)

If any credentials were found, print explicitly:

```
publish: BLOCKED — N credentials found. Clear them before publishing.
```

PII and sensitive paths are **warnings**, not blockers — the user decides whether to fix them or accept the exposure.

### 8. Report

Print a one-line summary in addition to the credential gate:
- With findings: `publish: N findings (C creds, P PII, S paths) → B<n>`
- Clean: `publish: clean — no entry written`
- Dry: `publish: N findings (dry-run, no entry written)`

The orchestrator (or single-skill caller) will roll this up into the final stat post.
