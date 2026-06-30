---
kind: disk
---
# {{DISK_LABEL}}

{{
	what's on this disk — a sentence or two; delete for a fresh/blank disk
}}

## Physical

- **Type:** {{ssd / hdd / flash / optical}}
- **Capacity:** {{size, e.g. 4 TB}}
- **Interface:** {{usb-c / thunderbolt / sata / internal}}
- **Status:** {{in-use / archived / failed / wiped}}

## Contents

See `{{DISK_LABEL}} Manifest.md` in this folder for the full file listing.

## Notes

{{
	free-form notes — delete this section if empty
}}

# LOG

### {{date — YYYY-MM-DD}} — {{event title}}
{{
	what changed
}}
### ...

✂ ──── template notes ──── ✂

- **`{{DISK_LABEL}}`** — short label for the disk (e.g. `Crucible`). The **unified key**: it names the **folder**, this **marker file**, the **`{{DISK_LABEL}} Manifest.md`** beside it, and the **H1** — one substitution fills every site.

NOTES:
- Worked **folder template** for a `Disks/`-style folder (see [[FCT Template Folders]]) — a disk is a *folder*, not a single file, because its record spans more than one document: this marker plus a generated manifest.
- **Folder name:** strip the leading `_` and trailing ` Template` from the folder → `{{DISK_LABEL}}/`; the marker inside strips the same way → `{{DISK_LABEL}}.md`. The whole folder clones as a unit — one folder per disk.
- **Unified variables:** every `{{DISK_LABEL}}` — folder name, marker name, manifest name, and the bodies — binds to one value; fill it once and the whole folder updates together.
- **Repeating files:** a file whose name carries an **unbound** variable is a *repeatable slot* — add one per value, no `...` needed. (E.g. a `Nodes/` folder holding `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` gets one record per machine.) The unbound variable in the name *is* the "repeats" signal — the inter-file analog of the intra-file `### ...`.
- **Placeholder forms, multi-line braces, and `### ...`** work exactly as in a [[FCT Template Files|file template]].
