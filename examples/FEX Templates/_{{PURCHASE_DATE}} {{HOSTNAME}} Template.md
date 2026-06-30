---
kind: computer
---
# {{HOSTNAME}}

{{
	what this machine is for — 1–3 sentences; delete if undecided
}}

**Acquired:** {{PURCHASE_DATE}}    **Spec rev:** {{spec revision — starts v1, bump on any change}}

## Specs

- **CPU:** {{cpu model + class, e.g. M3 Max 16-core}}
- **GPU:** {{gpu model + VRAM — delete the line if integrated-only}}
- **OS:** {{os name + version}}
- **RAM:** {{memory, e.g. 64 GB}}
- **Storage:** {{size + type, e.g. 2 TB NVMe}}

## Access

- **Reach:** {{HOSTNAME}}.local  ·  {{raw IP or alias — delete if mDNS works}}
- **User:** {{primary login account}}

## Notes

{{
	free-form notes — delete this section if empty
}}

# LOG

### {{date — YYYY-MM-DD}} — {{event title}}
{{
	what changed and why
}}
### ...

✂ ──── template notes ──── ✂

- **`{{HOSTNAME}}`** — the machine's hostname (e.g. `magnolia`). Fills the **H1**, the **Access** reach, and — with the date — the **filename**.
- **`{{PURCHASE_DATE}}`** — acquisition date, `YYYY-MM-DD`. The **filename** prefix and the **Acquired** line.

NOTES:
- Worked **file template** for a `Nodes/`-style folder (see [[FCT Template Files]]) — a shape specific to one folder, so a **template, not a global facet**.
- **Filename:** strip the leading `_` and the trailing ` Template` → the instance name `{{PURCHASE_DATE}} {{HOSTNAME}}.md` (e.g. `2026-06-14 magnolia.md`), date-first so the folder sorts chronologically.
- **Two placeholder forms:** `{{UPPER_SNAKE}}` is a **variable** — reused or structural, named and defined above; `{{Mixed Case description}}` is a **one-off**, described in place, no definition needed.
- **Single- vs multi-line:** inline braces hold one line (`{{event title}}`); **braces spanning their own lines** hold a block (the `{{ … }}` around *what changed*, *free-form notes*).
- **`# LOG` repeats:** the `### ...` means *another* `### {{date}} — …` entry goes here, newest first — it sits at heading level on purpose, so it is the whole entry that recurs, not the detail line. Delete the pattern and the `### ...` until a real event.
- Keep `## Specs` **alphabetical**; values are recorded **as of the purchase date**.
