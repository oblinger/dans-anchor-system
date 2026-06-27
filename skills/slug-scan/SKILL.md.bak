---
name: slug-scan
description: Scan for new slugs and sync the index — Discovers anchors with slugs and updates the slug-index. Use when user says: "slug scan", "sync slugs".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Slug Scan — Sync the slug index

Runbook for the `/slug-scan` skill — discovers new anchor slugs and appends formatted rows to the master slug index at `~/ob/kmr/SYS/SYS Topic/slug/SLUG.md`.

Scan for new anchor slugs and add them to the slug index table at `~/ob/kmr/SYS/SYS Topic/slug/SLUG.md`.

## Step 1: Ensure HookAnchor Is Current

```bash
ha --rescan
```

## Step 2: Find New Slugs

```bash
cd "$(ha -p PC)" && python bin/scan_tid.py delta
```

Optional: filter by date with `--since 2025-01-01`

The script outputs ready-to-paste rows in the new dot-separated format. Pass `--update` to write them directly into SLUG.md.

## Step 3: Format

Rows use a 2-column layout — date+slug on the left, description + structured suffix on the right:

```markdown
| Slug | Description, breadcrumbs, filename, atlas |
| --- | --- |
| 2026-06-04 [[SLUG]] | Master slug index. [[SYS]] (atlas [[Atlas#SLUG\|SLUG]]) |
```

**Column 1** — `DATE [[SLUG]]`.

**Column 2** — `description. breadcrumbs ([[filename]], atlas [[Atlas#X\|X]])`. Every piece after `description` is optional:

- **breadcrumbs** — slug ancestry only, e.g. `[[SYS]] > [[MAC]]` for `MACAPP`. Omitted if the slug is anchor-root level.
- **filename** — appears inside parens when the anchor's full name differs from the slug. Omitted when they're identical.
- **atlas** — appears inside parens (as the 2nd item when both present) when the slug or full-name matches a `## H2` heading in `~/ob/kmr/MY/Atlas/Atlas.md`.
- The period separator appears only when both a description and a structured suffix are present.

## Step 4: Verify Descriptions

Descriptions come from the anchor marker file (the file matching the folder name):

```markdown
---
desc: Brief description of the project
---
```

Older anchors may use `desc::` inline. `python bin/scan_tid.py sync` does a bidirectional sync between SLUG.md row descriptions and the anchor file `desc::` line.

## Rules

- **Never delete slug rows** — only add or update.
- **New entries → top dated table** — not the ROOT slugs hierarchy table at the bottom.
- The ROOT slugs hierarchy can be regenerated with `python bin/scan_tid.py tree` (reads anchor-roots from `~/ob/kmr/Roots/Roots.md` per [[F057 — Anchor-root concept and scan_tid migration]]).
- Atlas detection is automatic — no manual atlas-link entry needed; the script looks up Atlas H2s and appends the segment when matched.

## Related

- [[Wiring Slug Index]] — full computation, design rationale, where each input comes from.
- [[SLUG]] — the target file.
