---
kind: disk
---
# {{DISK_LABEL}}

{{ONE_LINE_WHAT_IS_ON_IT}}

## Physical

- **Type:** {{TYPE}}
- **Capacity:** {{CAPACITY}}
- **Interface:** {{INTERFACE}}
- **Status:** {{STATUS}}

## Contents

See `{{DISK_LABEL}} Manifest.md` in this folder for the full file listing.

## Notes

# LOG

# About this template

A **folder template** (worked example for [[FCT Template Folders]]). Each disk is a *folder*, not a single file, because a disk record carries more than one document — this main record plus a generated manifest. Clone the whole `_Disk Template/` folder → `{Disk Label}/`, rename the marker to `{Disk Label}.md`, and add the manifest as it is produced.

**Folder skeleton:**

- `{Disk Label}.md` — this main record (the marker, renamed).
- `{Disk Label} Manifest.md` — the file listing; added later, not part of the at-creation content.

## Variables

- `{{DISK_LABEL}}` — short label for the disk; also the folder name and main-doc filename. **Always present** (it is the key).
- `{{ONE_LINE_WHAT_IS_ON_IT}}` — one line on the disk's purpose/contents. Delete the line for a fresh/blank disk.
- `{{TYPE}}` / `{{CAPACITY}}` / `{{INTERFACE}}` / `{{STATUS}}` — physical attributes; delete any single line not yet known rather than leaving an empty `{{}}`.

`## Notes` starts empty (structural). `# LOG` is **cumulative** — header only at creation; add `### {YYYY-MM-DD}` entries newest-first as events occur.
