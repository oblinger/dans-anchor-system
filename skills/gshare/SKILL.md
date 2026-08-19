---
name: gshare
description: Publish a markdown file to a link-shared Google Doc that expires, tracked in a two-table register. Use when the user wants to hand someone a URL for a vault document, asks what is currently shared, or wants a share taken down.
---

# gshare — publish markdown to a link-shared Google Doc that expires

`gshare` is a **script, not an agent workflow**. It puts a markdown file on Drive as a link-shared Google Doc, records it in a register, and takes it back down when it expires. The expiry has to fire when nobody is asking, so no part of it depends on an agent noticing — run the command and read what it prints.

    gshare <path> [--days N | --forever] [--title T] [--pdf]   publish, or refresh an existing share
    gshare list [--all]                                what is published right now
    gshare clean [--dry-run]                           sweep expired rows, reconcile against Drive
    gshare rm <path | url | id>                        take one share down now
    gshare open <path | url>                           open the published doc in a browser

Default lifetime is 30 days. `gshare <same path>` again **refreshes the existing doc in place** — same URL, expiry reset — so it doubles as *renew*, and a link already handed out never breaks. Every invocation sweeps expired shares before doing anything else.

## What to know before using it

- **The register is the only store.** Two markdown tables in one vault page (`Expiring`, then `Permanent`), machine-written. The Drive file id is recovered from the URL in the `Weblink` cell, so there is no sidecar and no cache to fall out of sync. **Do not hand-edit it** — run the commands.
- **Shares are link-viewable, never searchable, and never listable.** Each *file* gets `anyone` / `reader` / `allowFileDiscovery=false`. No link means no access, and there is no index anyone can browse to discover what else exists. The three properties come from two different places, which is the part worth remembering: *viewable-by-link* and *not-searchable* are the per-file permission; **not-listable is the folder being private**, and nothing else.
- **The `GShare` folder itself is private, permanently, and that is load-bearing.** It is tempting to share the folder so children inherit — do not. In Drive, sharing a folder **is** granting permission to list it, and an inherited permission **cannot be removed from a child**. So a shared `GShare` would hand anyone with the folder link a browsable index of every document ever published, and the only way back out would be moving files elsewhere. Per-file permissions cost one extra API call and keep each share an independent secret. Decided by Dan 2026-08-19 (see § Decisions).
- **Taking a share down revokes the permission and then trashes the file.** In that order, and the order is load-bearing: trashing a Drive file does *not* revoke its link share — measured 2026-08-12, a trashed-but-still-shared doc serves its content exactly as before. Trashing after revoking is what keeps the content recoverable for 30 days.
- **Unregistered files in the share folder are reported, never touched.** The folder predates this script.
- **It publishes markdown only.** Frontmatter, `:>>` breadcrumbs, HTML comments, and block-ids are stripped, and `[[wiki-links]]` are flattened to their display text, because a wiki-link renders as literal brackets to someone without the vault. Tables survive as real Docs tables.
- **Figures travel (F335).** The conversion path is pandoc DOCX → Drive's DOCX→Doc importer, so images ride *inside* the payload: Obsidian `![[image]]` embeds are resolved through the vault, mermaid fences render to PNG via `mmdc`, and SVG is rasterized via `rsvg-convert` (Docs mangles imported SVG). Callouts (`> [!note]`) become styled blockquotes. `pandoc`, `mmdc`, and `rsvg-convert` are hard dependencies — a missing tool dies with install instructions.
- **Obsidian-only constructs never block a publish — they gap and report.** Dataview/query blocks, Excalidraw drawings without an exported image, note transclusions, and missing embeds each become a clearly-marked ⚠ gap in the published Doc, and the CLI prints "published, but N constructs could not convert: …" naming each with its line number. Nothing silent, nothing refused. (There is deliberately no auto-fallback to PDF: those constructs render only inside Obsidian's plugin runtime, so a PDF would have the identical holes.)
- **`--pdf` publishes a PDF instead of an editable Doc** — for docs whose value is layout. Same register, same expiry, same rm/refresh verbs; rendered via pandoc HTML + headless Chrome print with a vault-ish stylesheet. Switching a share's lane (doc ↔ pdf) takes the old file down and mints a new URL — Drive cannot convert one into the other in place.

## Decisions

### The share folder is private; permission is granted per file (Dan, 2026-08-19)

**Decision.** `gshare` publishes into **`Oblio/GShare`** in the personal Google account — a folder that is **owner-only and stays that way** — and grants access by setting `anyone` / `reader` / `allowFileDiscovery=false` on **each document**. Renamed from `WEBSHARE` on 2026-08-19; the id is unchanged, so every URL ever handed out still resolves.

**What this buys, stated as the three properties Dan asked for.** A link works for anybody, with no Google account and no membership in anything. Nothing is searchable — the documents never appear in Google results. And nothing is enumerable: there is no folder, index, or listing anyone can open to find out what else has been published. Each share is an independent secret whose only key is its URL.

**Why the folder is not shared, though inheritance looks like the tidier design.** The original proposal was to share the `GShare` folder once and let children inherit, so permissions would live in exactly one place. It cannot be done, and the reason is worth writing down because it will look like an oversight later: **in Drive, sharing a folder is the same act as granting permission to list it**, and an inherited permission **cannot be removed from a child**. A shared `GShare` would therefore turn every document ever published into one browsable index, reachable by anyone holding a single folder link — and there would be no way to exempt an individual file short of moving it out of the folder. The non-listable property and the inheritance property are the same switch, and only one of them can be on.

`GShare` deliberately sits at the top of `Oblio` rather than inside `Oblio/public`, for the same reason: `Oblio/public` is already `anyone/reader`, so anything placed beneath it inherits that and becomes listable.

**A trap in the API's naming.** `allowFileDiscovery=false` reads like "cannot be discovered" but means only **not surfaced by Google search**. It has nothing to do with listing: someone holding a shared folder's link can enumerate its contents regardless. The not-listable guarantee here comes from the folder being private, full stop — never from this flag.

**Per-document escalation stays available and stays local.** Opening one published doc and switching it to editable, or adding a named collaborator, affects that document only. Because there is no inherited grant, a change to one share can never widen another.

## Configuration

`~/.config/anchor-system/gshare/config.yaml` (per the F080 per-skill namespace). Nothing is hard-coded and nothing silently defaults — a missing key is an error naming the file and the key.

    drive_folder_id: <the Drive folder that receives shares>    # required
    credentials:     <OAuth client json with a drive scope>     # required
    register:        <path to the register page>                # default: {skill_data_root}/gshare/gshare register.md
    default_days:    30

The Google Cloud project this user's credentials belong to is in Testing mode, so the refresh token expires every 7 days; `gshare` prints the re-auth command when that happens.

### Setting it up from scratch

1. **Create the destination folder** in the personal Drive account — `Oblio/GShare` for this user. **Do not share it.** Leave it owner-only; § Decisions explains why that is a requirement rather than a default.
2. **Do not nest it under an already-shared folder.** Check the parent chain: if any ancestor carries an `anyone` permission, the new folder inherits it and the not-listable guarantee is gone before the first publish.
3. Put its id in `drive_folder_id`.
4. Point `credentials` at an OAuth client json holding a refresh token with a Drive scope.
5. **Verify the guarantee rather than assuming it**, with two checks that measure opposite things:
   - the folder is private — `GET /files/<folder_id>/permissions` returns `user/owner` and nothing else;
   - a published file is public — `curl -s -o /dev/null -w '%{http_code}' https://docs.google.com/document/d/<id>/export?format=txt` returns **307**. Probe `/export`, never `/edit`: a denied `/edit` returns **200** carrying Google's "you need access" page, so it cannot tell the two apart.

## Not yet built

Sharing a **folder**. It needs a decision the single-file case does not — whether a folder becomes a mirrored Drive subfolder with one Doc per file, one flattened Doc, or an index Doc of links — and those produce materially different URLs and different cleanup. Deliberately deferred, not forgotten.

## Related

- Design: `F325` (base) and `F335` (fidelity upgrade: DOCX intermediate, rendered figures, gap report, --pdf lane) in the TINK anchor.
- Transport and Drive conventions: the `io` skill's `io-gdrive` card, which owns the GShare naming rule (`YYYY-MM-DD ` prefix) that `gshare` applies.
- Not to be confused with `/publish`, which deploys an anchor's splash page to GitHub Pages — permanent, HTML, anchor-scoped.
