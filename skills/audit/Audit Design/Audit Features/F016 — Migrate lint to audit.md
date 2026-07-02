---
description: "Retire /lint into /audit: hard rename, 1:1 subaction map, vault-wide reference sweep."
---

# [[SKA]] · F078 — Migrate `/lint` → `/audit` — deprecate lint skill, sweep references

## Summary

Migrate the `/lint` skill family into `/audit`, per the user's direction to unify everything under "audit." Subactions map 1:1 by name where possible; vault-wide sweep converts `/lint X` → `/audit X` references; the `cab-lint.py` helper script renames to `cab-audit.py`, and any user-side `$PATH` wiring updates correspondingly. Q1–Q3 resolved 2026-07-01 — executing.

## Design

### 1. Migration steps (high-level)

1. **Audit current `/lint` surface.** Read `skills/lint/SKILL.md`, list every subaction + the constraints it checks.
2. **Map to `/audit` subactions** per Q2 resolution. Document the 1:1 (or 1:N) map.
3. **Rename script + symlink** per Q3 resolution.
4. **Sweep vault references** — `[[SKA lint]]` → `[[SKA audit]]`, `/lint X` → `/audit X`, `cab-lint` → `cab-audit`. Skill files, CAB facets, anchor pages, per-anchor docs all in scope.
5. **Delete `skills/lint/`** per Q1 resolution. Remove from skill-dispatch / skills.md index.
6. **Verify** with `audit q` (per F076) — the sweep should leave zero broken `[[SKA lint]]` wiki-links.

### 2. Scope of the reference sweep

`[[SKA lint]]` and `/lint X` references in:
- All `skills/**/SKILL.md` and companion `.md` files
- CAB facet specs (`CAB/CAB Facets/*.md`)
- `skills/skills.md` / CAB Skills index
- Anchor pages (`{NAME}.md`) that mention lint in dispatch tables or prose
- Per-anchor docs that reference `/lint` invocation in workflows
- Trigger words file in `~/.claude/CLAUDE.md` if lint has a trigger

### 3. Out of scope

- Adding new audit subactions beyond what `/lint` had. Pure migration; no scope creep.
- Changing the `/audit` skill's existing surface (sub-action naming, runbook structure). The migration brings lint into audit; it doesn't reshape audit.
- Renaming `~/.anchor.d/lint/` directory (if it exists) — separate concern; defer.

## Status

Designing — parked in `## Later`. No urgency.

## Resolved

*Q1–Q3 resolved by the user 2026-07-01 (chat): all three land on option (a), matching the filed recommendations.*

- **Q1 — Hard rename or alias?** — **(a) Hard rename.** "I don't want lint to exist anymore." The `/lint` skill is deleted outright; the vault-wide sweep converts every reference. No alias, no shim. ^F016-Q1
- **Q2 — Subaction mapping** — **(a) 1:1 by name.** Each `/lint` subaction becomes the same-named `/audit` subaction (merge logic where both exist). Standing instruction: if a name is genuinely wrong/colliding, surface it to the user; otherwise map mechanically. ^F016-Q2
- **Q3 — `cab-lint.py` disposition** — **(a) Rename to `cab-audit.py`**, keep it standalone (not absorbed), update any `$PATH`/symlink wiring. ^F016-Q3
