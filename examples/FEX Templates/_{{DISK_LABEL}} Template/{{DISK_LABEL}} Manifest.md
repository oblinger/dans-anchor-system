---
kind: disk-manifest
---
# {{DISK_LABEL}} Manifest

{{
	generated file listing — one row per top-level entry; produced by the disk scan, not hand-authored
}}

✂ ──── template notes ──── ✂

- **`{{DISK_LABEL}}`** — bound to the same value as the folder and marker (the unified namespace).

NOTES:
- A **skeleton member** that ships inside the `_{{DISK_LABEL}} Template/` folder. It is *not* a `_… Template` itself — it's an ordinary file named with the shared variable, so cloning the folder fills its name too.
- The body is machine-generated (the scan output); the template just reserves the file and its heading.
