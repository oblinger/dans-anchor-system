---
kind: computer
---
# {{HOSTNAME}}

{{ONE_LINE_ROLE}}

## Specs

- **CPU:** {{CPU}}
- **RAM:** {{RAM}}
- **Storage:** {{STORAGE}}
- **OS:** {{OS}}

## Access

- **Hostname:** {{HOSTNAME}}
- **Reach:** {{IP_OR_SSH_ALIAS}}

## Notes

# LOG

---

# About this template

A **file template** (worked example for [[FCT Template Files]]). It defines what one *computer record* looks like inside a `Computers/` folder — a domain-specific shape that is **not** a global facet (no other anchor type carries "computer-formatted things"), so it lives as a template local to that folder. Clone → `{Hostname}.md` in the same folder, one file per machine.

## Variables

- `{{HOSTNAME}}` — the machine's hostname; also the filename. **Always present** (it's the key).
- `{{ONE_LINE_ROLE}}` — what this machine is for (e.g. "home NAS"). Delete the line if not yet decided.
- `{{CPU}}` / `{{RAM}}` / `{{STORAGE}}` / `{{OS}}` — hardware specs. Delete any single line you don't know yet rather than leaving an empty `{{}}`.
- `{{IP_OR_SSH_ALIAS}}` — how you reach it. Delete if local-only.

`## Notes` starts empty (structural section, no placeholder). `# LOG` is a **cumulative** section — header only at creation; add reverse-chronological `### {YYYY-MM-DD}` entries as events occur, newest first.
