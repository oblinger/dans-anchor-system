---
description: "Retire /lint into /audit: hard rename, 1:1 subaction map, vault-wide reference sweep."
---

# [[SKA]] · F078 — Migrate `/lint` → `/audit` — deprecate lint skill, sweep references

## Open Questions

- **Q1 — Hard rename or alias?** When the user (or an agent) invokes `/lint <X>`, what happens after this feature ships? ^F078-Q1
  - (a) **Hard rename** — `/lint` skill is deleted. References sweep across the vault converts `/lint <X>` → `/audit <X>`. Clean break.
  - (b) **Alias** — `/lint` stays as a thin wrapper that forwards to `/audit <closest equivalent>`. Backward-compatible; no vault-wide sweep needed. The vocabulary is dual ("lint" or "audit" both work) but documentation pivots to "audit."
  - (c) **Deprecation shim** — `/lint` prints "deprecated; use `/audit <X>` instead" and exits non-zero. Forces user/agent to update call sites without auto-routing.
  - **Recommendation: (a).** The user's stated goal is "get rid of lint and turn everything into audits" — that's a clean-break frame. Aliases produce dual vocabulary that drifts ("which one is canonical now?"). Sweep cost is bounded (~dozens of references vault-wide); pay it once.
- **Recommendation:** None — needs user decision (C9 stub 2026-05-26).

- **Q2 — Subaction mapping.** What does each `/lint` subaction become under `/audit`? ^F078-Q2
  - (a) **1:1 map by name.** `/lint structure` → `/audit structure` (already exists; merge logic if both have it). `/lint` (no arg) → either deprecated or maps to `/audit structure` (the closest equivalent).
  - (b) **Reshape during migration.** Use the move as an opportunity to split or merge subactions — e.g., if `/lint` checks five things that conceptually belong in different audit categories, split them.
  - (c) **Investigate first.** Don't pre-commit to the mapping; the implementer audits both surfaces, then proposes the map as a Q3 follow-up.
  - **Recommendation: (a).** Same-named subactions map 1:1; this minimizes blast radius. The current `/lint` skill's surface is small enough (structural conformance, dispatch tables, missing files, module-doc coverage) that all of it fits under `/audit structure` and `/audit docs`. If overlap is found during implementation, surface as a sub-question.
- **Recommendation:** None — needs user decision (C9 stub 2026-05-26).

- **Q3 — Disposition of the `cab-lint.py` helper script and any `$PATH` shortcut to it.** ^F078-Q3
  - (a) **Rename to `cab-audit.py`** + update any user-side `$PATH` wiring. Preserves the helper's shell-invocability; updates the vocabulary.
  - (b) **Absorb into audit subaction scripts.** The script logic gets folded into `skills/audit/scripts/audit-structure.py` (or wherever applicable); the standalone `cab-lint.py` is deleted.
  - (c) **Keep `cab-lint.py` as-is.** The script is implementation; the skill is the user-facing surface. Renaming the script is cosmetic.
  - **Recommendation: (a).** Vocabulary consistency matters more than backward-compatible script names. The `cab-lint` shortcut is rarely typed (most invocations go through `/lint` skill); the rename cost is whatever wiring the user has on their `$PATH`. Keep the script standalone (don't absorb per (b)) — it's still useful as a direct-invocation tool.
- **Recommendation:** None — needs user decision (C9 stub 2026-05-26).

## Summary

Migrate the `/lint` skill family into `/audit`, per the user's direction to unify everything under "audit." Subactions map 1:1 by name where possible; vault-wide sweep converts `/lint X` → `/audit X` references; the `cab-lint.py` helper script renames to `cab-audit.py`, and any user-side `$PATH` wiring updates correspondingly. Filed in `## Later` — no urgency; ship when convenient (likely after F076 `/audit q` is Done and the audit-family is otherwise stable).

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
