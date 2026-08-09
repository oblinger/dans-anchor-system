---
name: disk
description: Reconcile a mirror drive (10T / 8T / BLACK) against its catalog, in both directions, plus two capacity questions. Use when the user says "check the drive for stray files", "does the drive match the catalog", "is there anything unexpected on 8T", "will BLACK still hold the master if we resync", "what would a refresh actually copy/delete", "reconcile 10T against the catalog". Not a hash checker — pairs with the existing three-drive SHA-256 verify system, doesn't replace it.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Disk — Catalog Reconciliation
requires:: vault, external:rsync
subsystem:: [[DAS Hygiene Design]] — the Hygiene group's subsystem profile

Check a drive against its catalog in both directions, plus whether it can still hold its source and what a pending refresh would actually spend its headroom on.

## Why this exists

The existing three-drive verification system hashes files that exist on the drives and compares copy-to-copy across `10T` / `8T` / `BLACK`. It is strong at answering "is this copy faithful to that one?" — and it is structurally **incapable** of answering "is there something on this drive nobody expected?" An unlisted file is, by definition, absent from the expected-worklist, and a cross-drive hash walk only ever visits paths that exist on the drives. Nothing in that system can see a file no one told it about.

The cost of that blind spot was real: three 28.8 GB temp files once appeared in `__MASTERS__/_ARCHIVES_/` two days after a verification pass. Nothing flagged them. They were faithfully mirrored to both clones and sat unexplained for six weeks — a clean verify run had nothing to say about them, because they were never on the worklist to begin with.

`/disk reconcile` closes that gap by checking a drive against `SYS Catalog/Disk/Disk Master/Master Contents.xlsx` directly — every catalog row against the filesystem, AND every catalog-named directory against what's actually sitting inside it.

## Actions

| Action | Script | Description |
|---|---|---|
| `/disk reconcile <drive>` | `scripts/disk_reconcile.py` | Full four-part reconciliation of `<drive>` against the catalog |

Flags:

- `--refresh-from <SOURCE-LABEL>` — also preview what an `rsync -aH --delete-before` refresh FROM that drive INTO `<drive>` would do (files created/deleted, transfer bytes, top-15 largest items). Without this flag, only the catalog-vs-disk and catalog-derived capacity checks run.
- `--json` — emit one JSON object (`missing`, `relocated`, `relocated_unverified`, `never_landed`, `unexplained`, `capacity`, `refresh`, `suppressed`) instead of the text report. Same underlying data either way — computed once, rendered twice.
- `--root <path>` — override the mirror root registered for `<drive>` (production reads a fixed `MIRROR_ROOTS` table; this is mainly for pointing the tool at a test fixture).
- `--no-refresh-scan` — skip the rsync dry-run even when `--refresh-from` is given. It can take **up to an hour** on a full drive (a prior full dry run over 8.3M files took 62 minutes) — use this to get the fast three-part report and defer the refresh preview.

## Runbook

1. **Confirm the drive is mounted.** The script resolves `<drive>` to its mirror root (`10T` → `/Volumes/10T`, `8T` → `/Volumes/8T`, `BLACK` → `/Volumes/BLACK/Clone of 10T` — note BLACK's mirror is a subfolder, not the volume root) and exits 2 with the expected path if it isn't there. Don't invoke this against a drive mid-rsync or mid-verify from another process.
2. **Run it:**
   ```bash
   python3 "$HOME/ob/kmr/SYS/Bespoke/Skill Agent/dans-anchor-system/skills/disk/scripts/disk_reconcile.py" <DRIVE-LABEL>
   ```
   Add `--refresh-from <SOURCE-LABEL>` when the question is "what would refreshing this drive from that one actually do" — expect it to run long; warn the user before invoking without `--no-refresh-scan` on a full-size drive.
3. **Read the four sections in order:**
   - **(1) Expected-but-missing** — every catalog row whose path isn't on disk. A verification stamp (`8T`/`BLACK` columns) never expires, so a row can still read "verified present on both backups" while the path underneath it is empty — the report calls that out explicitly per row. Anything here that isn't a documented relocation is real data loss or an undocumented move; investigate before doing anything else.
   - **RELOCATED** — rows whose per-file `M3 YYYY-MM-DD (R<n>/K<n>/M<n>)` disposition moved out every file the row has (M-count equals the row's Files count), AND whose destination `Broken *.zip` archive was opened and confirmed to actually list the row's file. Suppressed out of (1) but never hidden — still listed with the disposition text. (An earlier version matched the words "moved"/"relocated" in the disposition text; those words appear in zero of the real workbook's distinct values, so that branch never fired on real data and was retired.)
   - **RELOCATED — CONTENTS UNVERIFIED** — the destination *directory* exists, but its `Broken *.zip` archive is missing, unreadable/corrupt, or doesn't list the row's file. A directory being present is not evidence the bytes are inside it — this state exists specifically so that gap can't be smoothed over as "relocated" on the strength of the directory alone. Counts toward the non-zero exit, same as (1) and (2).
   - **(2) Present-but-unexplained** — entries sitting in a catalog-named directory that no row accounts for. This is the direction the hash-based verify system cannot do at all; treat any hit here as a "was this supposed to be here?" question for the user, not an auto-delete.
   - **(3) Capacity ceiling** — target drive's **capacity ceiling** (never free space — free space describes the last sync, not whether the next one fits) versus the source content. Without `--refresh-from` the source number is a **catalog-Bytes-column estimate**, labeled as such, not a measurement. With it, the number comes from the rsync dry-run's own `Total file size`.
   - **(4) Refresh preview** — only with `--refresh-from`: files to create, files to delete, total transfer bytes, and the 15 largest items about to be transferred. A run that only says "it fits" is worth less than one that shows what the headroom is about to be spent on.
   - **Suppressed** — every exception applied along the way (drive-local `*.tsv` manifests, the catalog workbook itself, `READ ME FIRST.txt`, `SYNC-LOG-*.txt`, macOS per-volume cruft, and dotfiles generically), each with a reason and a count. Nothing is ever dropped silently — a guard that discards without saying so manufactures an invisible miss, which is the exact failure mode this tool exists to catch elsewhere.
4. **Exit code drives the response.** `0` = clean, nothing to do. `1` = direction (1) or (2), or RELOCATED-CONTENTS-UNVERIFIED, found something — surface it to the user before taking any action; this tool reports, it never deletes or moves anything itself. `2` = setup problem (drive not mounted, catalog unreadable, rsync failed) — fix the setup, don't reinterpret the output.
5. **Never act on a finding unilaterally.** Missing rows, unexplained entries, and "won't fit" capacity calls all go back to the user — per the Disk disciplines, destructive drive work is confirmed first, every time.

## What it is not

- **Not a hash checker.** It never reads file content or computes a checksum; it only checks path existence and directory listings against the catalog. The three-drive SHA-256 verify system still owns "is this copy faithful to that one?" — this tool answers the orthogonal question that system structurally cannot: "is there anything here nobody catalogued?"
- **Not a replacement for the three-drive verify.** Run both. A clean verify plus a clean reconcile is the actual "this drive is in the state we think it's in" claim; either alone is a partial claim about the drive.
- **Not a fixer.** It never deletes, moves, or renames anything — including the files it flags as unexplained or suppressed. Findings are handed to the user.
