---
kind: computer
---
# {{HOSTNAME}}

{{ROLE}}

**Acquired:** {{PURCHASE_DATE}}    **Spec rev:** {{SPEC_VERSION}}

## Specs

- **CPU:** {{CPU}}
- **OS:** {{OS}}
- **RAM:** {{RAM}}
- **Storage:** {{STORAGE}}

## Access

- **Reach:** {{IP_OR_SSH_ALIAS}}

## Notes

{{NOTES}}

# LOG

# About this template

A **file template** (worked example for [[FCT Template Files]]) — one *computer record* in a `Computers/` folder. The shape is domain-specific to that one folder, so it is a **template, not a global facet**. Clone → `{Hostname}.md`, one file per machine. Everything from this `# About this template` heading down is *about the template* and is **not** copied into a record — it is the unambiguous end of the exemplar.

**Conventions** (about the data as a whole, not tied to any single field):

- List `## Specs` in **alphabetical order**.
- Spec values are recorded **as of the purchase date**; bump `{{SPEC_VERSION}}` whenever they change (a RAM upgrade, an OS reinstall).
- `# LOG` is **cumulative** — leave it empty at creation; add `### {YYYY-MM-DD}` entries newest-first as events occur.

## Variables

- `{{HOSTNAME}}` — hostname; also the filename. **Always present** (it is the key).
- `{{ROLE}}` — what the machine is for; **1–3 sentences, may span multiple lines**. Delete the line if undecided.
- `{{PURCHASE_DATE}}` — acquisition date, **format `YYYY-MM`** (e.g. `2026-06`). Delete the line if unknown.
- `{{SPEC_VERSION}}` — spec revision; starts at `v1`, bump on any hardware/OS change.
- `{{CPU}}` / `{{OS}}` / `{{RAM}}` / `{{STORAGE}}` — spec values; delete any single line not yet known rather than leaving an empty `{{}}`.
- `{{IP_OR_SSH_ALIAS}}` — how you reach it (IP, SSH alias). Delete the line if local-only.
- `{{NOTES}}` — free-form; delete the whole `## Notes` section if empty.
