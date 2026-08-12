---
name: gshare
description: Publish a markdown file to a link-shared Google Doc that expires, tracked in a two-table register. Use when the user wants to hand someone a URL for a vault document, asks what is currently shared, or wants a share taken down.
---

# gshare — publish markdown to a link-shared Google Doc that expires

`gshare` is a **script, not an agent workflow**. It puts a markdown file on Drive as a link-shared Google Doc, records it in a register, and takes it back down when it expires. The expiry has to fire when nobody is asking, so no part of it depends on an agent noticing — run the command and read what it prints.

    gshare <path> [--days N | --forever] [--title T]   publish, or refresh an existing share
    gshare list [--all]                                what is published right now
    gshare clean [--dry-run]                           sweep expired rows, reconcile against Drive
    gshare rm <path | url | id>                        take one share down now
    gshare open <path | url>                           open the published doc in a browser

Default lifetime is 30 days. `gshare <same path>` again **refreshes the existing doc in place** — same URL, expiry reset — so it doubles as *renew*, and a link already handed out never breaks. Every invocation sweeps expired shares before doing anything else.

## What to know before using it

- **The register is the only store.** Two markdown tables in one vault page (`Expiring`, then `Permanent`), machine-written. The Drive file id is recovered from the URL in the `Weblink` cell, so there is no sidecar and no cache to fall out of sync. **Do not hand-edit it** — run the commands.
- **Shares are link-viewable, never searchable.** `anyone` / `reader` / `allowFileDiscovery=false`. No link means no access.
- **Taking a share down revokes the permission and then trashes the file.** In that order, and the order is load-bearing: trashing a Drive file does *not* revoke its link share — measured 2026-08-12, a trashed-but-still-shared doc serves its content exactly as before. Trashing after revoking is what keeps the content recoverable for 30 days.
- **Unregistered files in the share folder are reported, never touched.** The folder predates this script.
- **It publishes markdown only.** Frontmatter, `:>>` breadcrumbs, HTML comments, and block-ids are stripped, and `[[wiki-links]]` are flattened to their display text, because a wiki-link renders as literal brackets to someone without the vault. Tables survive as real Docs tables.

## Configuration

`~/.config/anchor-system/gshare/config.yaml` (per the F080 per-skill namespace). Nothing is hard-coded and nothing silently defaults — a missing key is an error naming the file and the key.

    drive_folder_id: <the Drive folder that receives shares>    # required
    credentials:     <OAuth client json with a drive scope>     # required
    register:        <path to the register page>                # default: {vault_root}/SYS/SYS Catalog/GShare.md
    default_days:    30

The Google Cloud project this user's credentials belong to is in Testing mode, so the refresh token expires every 7 days; `gshare` prints the re-auth command when that happens.

## Not yet built

Sharing a **folder**. It needs a decision the single-file case does not — whether a folder becomes a mirrored Drive subfolder with one Doc per file, one flattened Doc, or an index Doc of links — and those produce materially different URLs and different cleanup. Deliberately deferred, not forgotten.

## Related

- Design: `F325` in the TINK anchor.
- Transport and Drive conventions: the `io` skill's `io-gdrive` card, which owns the WEBSHARE naming rule (`YYYY-MM-DD ` prefix) that `gshare` applies.
- Not to be confused with `/publish`, which deploys an anchor's splash page to GitHub Pages — permanent, HTML, anchor-scoped.
