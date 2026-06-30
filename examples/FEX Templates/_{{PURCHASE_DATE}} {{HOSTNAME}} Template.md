---
kind: computer
---
# {{HOSTNAME}}

{{ROLE}}

**Acquired:** {{PURCHASE_DATE}}    **Spec rev:** {{SPEC_VERSION}}

## Specs

- **CPU:** {{CPU}}
- **GPU:** {{GPU}}
- **OS:** {{OS}}
- **RAM:** {{RAM}}
- **Storage:** {{STORAGE}}

## Access

- **Reach:** {{HOSTNAME}}.local  ·  {{IP_OR_SSH_ALIAS}}
- **User:** {{LOGIN_USER}}

## Notes

{{NOTES}}

# LOG

### {{DATE}} — {{EVENT_TITLE}}
{{DETAILS}}
### ...

✂ ──── template notes ──── ✂

This is a worked **file template** (see [[FCT Template Files]]) — one *computer record* for a `Nodes/`-style folder. The shape is specific to that one folder, so it is a **template, not a global facet**. Everything below this `✂ … template notes … ✂` cut-line is *about* the template and is **removed when you clone** — the unambiguous end of the exemplar. The cut-line matcher is lenient: the exact phrase **template notes** with ≥3 dashes either side, case- and spacing-insensitive; scissors optional.

**Filename — the composite key.** A template file starts with `_` and ends with ` Template`; **strip both, and what remains is the instance filename.** Here `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` → `{{PURCHASE_DATE}} {{HOSTNAME}}.md` (e.g. `2026-06-14 magnolia.md`) — a **composite** of two variables, date-first so the folder sorts chronologically. Both are reused across the body: `{{HOSTNAME}}` also fills the **H1** and the **Access** reach; `{{PURCHASE_DATE}}` also fills the **Acquired** line. One substitution per variable fills every site.

**Single-line vs multi-line values.** A placeholder that sits **inline** (within a heading or sentence) holds a single line — `{{EVENT_TITLE}}`, `{{CPU}}`. A placeholder on **its own line** holds a multi-line block — `{{ROLE}}`, `{{NOTES}}`, `{{DETAILS}}`. The Variables list tags each.

**The `# LOG` repeats.** The exemplar shows one entry-pattern; the **`### ...`** beneath it means *"another `### {{DATE}} — …` entry goes here, newest first."* It is an `### ` heading (not a bare `...`) on purpose — the dots sit at the **level of the thing that repeats**, so it is the whole H3 entry that recurs, not the `{{DETAILS}}` line. The pattern's fields stay `{{placeholders}}`, so it is never mistaken for a real entry; delete the pattern **and** the `### ...` until the first real event.

## Conventions

- List `## Specs` in **alphabetical order**.
- Spec values are recorded **as of the purchase date**; bump `{{SPEC_VERSION}}` (starts `v1`) whenever they change — a RAM upgrade, an OS reinstall.

## Variables

- `{{HOSTNAME}}` — single-line. Hostname (e.g. `magnolia`); also the **filename** (with the date), the **H1**, and the **Access** reach. **Always present** — the key.
- `{{PURCHASE_DATE}}` — single-line. Acquisition date, `YYYY-MM-DD`; also the **filename** prefix. **Always present** — the key's date half.
- `{{ROLE}}` — multi-line. What the machine is for; 1–3 sentences. Delete the line if undecided.
- `{{SPEC_VERSION}}` — single-line. Spec revision; starts `v1`, bump on any hardware/OS change.
- `{{CPU}}` — single-line. CPU model + class (e.g. `M3 Max, 16-core`).
- `{{GPU}}` — single-line. GPU model + VRAM; delete the line if integrated-only.
- `{{OS}}` — single-line. OS name + version.
- `{{RAM}}` — single-line. Memory size (e.g. `64 GB`).
- `{{STORAGE}}` — single-line. Size + type (e.g. `2 TB NVMe`).
- `{{IP_OR_SSH_ALIAS}}` — single-line. Raw IP or alias for when `{{HOSTNAME}}.local` isn't reachable; delete if mDNS works.
- `{{LOGIN_USER}}` — single-line. Primary login account.
- `{{NOTES}}` — multi-line. Free-form; delete the whole `## Notes` section if empty.
- `{{DATE}}` / `{{EVENT_TITLE}}` / `{{DETAILS}}` — the `# LOG` entry. `{{DATE}}` (`YYYY-MM-DD`, single-line) · `{{EVENT_TITLE}}` (single-line) · `{{DETAILS}}` (**multi-line** — what changed and why, a paragraph or more). Delete the whole pattern + the `### ...` until the first event.
