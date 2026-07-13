---
description: superseded by CAB Track Dispatch per F094 — see redirect below
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Plan Dispatch](hook://p/DAS%20Plan%20Dispatch)
# FCT Plan Dispatch
Redirect stub for the legacy `{slug} Plan/` dispatch facet, superseded by [[DAS Track Dispatch]] and [[DAS Design Dispatch]] per F094.

**Related:** [[DAS Track Dispatch]],  [[DAS Design Dispatch]],  [[DAS Dispatch]]
**Examples:** [[HBR Track\|minimal (renamed from CAE Plan per F094)]],  [[HBR Track\|fuller]]

> **Superseded by [[DAS Track Dispatch]]** per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01).
>
> The `{slug} Plan/` folder is renamed to `{slug} Track/` matching the [[Track]] trait name. PRD / System Design / UX Design content moves into `{slug} Design/` (see [[DAS Design Dispatch]]). The Plan slot is freed for a future top-level strategic-plan *document* inside the Track tree.
>
> This file preserved as a redirect-stub during the F094 migration window. All references to `~~[[DAS Plan Dispatch]]~~` should migrate to `~~[[DAS Track Dispatch]]~~` (planning surface) or `~~[[DAS Design Dispatch]]~~` (design surface) depending on what the citation was actually pointing at.

## Legacy reference

(Kept for the migration window — readers landing here from old wiki-links should follow [[DAS Track Dispatch]] for the new tracking surface or [[DAS Design Dispatch]] for the new design surface.)

**Cardinality: one per anchor** — a single `{slug} Plan/` folder (now `{slug} Track/`) existed per anchor; this redirect stub mirrors that one-per-anchor contract.

# RULESET R-fct-plan-dispatch
include::
where:: `file: facets/FCT Dispatch/FCT Plan Dispatch.md`
description:: Rules for the redirect stub — this file's sole job is catching incoming `~~[[DAS Plan Dispatch]]~~` links during the F094 migration window and pointing to the successors.

### RULE R-fct-plan-dispatch-01 — No normative content added to this stub (checked)
This file must not grow new prose, rules, or tables beyond the redirect callout and migration note. Its entire normative authority is delegated to [[DAS Track Dispatch]] and [[DAS Design Dispatch]].
**Check pattern:** the file body contains no `## Format`, `## Constraints`, or `### RULE` sections outside this ruleset.
**Why:** any expansion of this stub creates a second authoritative source for the Track/Design split; all additions belong in the successor specs.

### RULE R-fct-plan-dispatch-02 — Redirect callout links both successors (checked)
The redirect blockquote must link [[DAS Track Dispatch]] (planning surface) and [[DAS Design Dispatch]] (design surface) explicitly.
**Check pattern:** both `~~[[DAS Track Dispatch]]~~` and `~~[[DAS Design Dispatch]]~~` appear in the blockquote.
**Why:** incoming references pointed at `Plan/` for two distinct purposes — planning and design — each needs its own forward pointer.

### RULE R-fct-plan-dispatch-03 — File removed when zero incoming links remain (stated)
Once a vault-wide grep finds zero `~~[[DAS Plan Dispatch]]~~` references, this file may be deleted. Until then it must remain to preserve wiki-link integrity.
**Check pattern:** run `grep -r 'FCT Plan Dispatch' ~/ob/kmr/ --include="*.md"`; non-zero count = keep; zero count = deletion candidate.
**Why:** a redirect stub with no incoming links is dead weight; but premature removal breaks old wiki-links that still resolve through it.

### RULE R-fct-plan-dispatch-04 — Filename must not be renamed (stated)
The basename `FCT Plan Dispatch` is the link target old citations resolve to; renaming it silently breaks every `~~[[DAS Plan Dispatch]]~~` reference still in the vault.
**Check pattern:** file lives at `facets/FCT Dispatch/FCT Plan Dispatch.md` with this exact basename.
**Why:** wiki-link resolution is name-based; the stub's value is entirely in its filename matching the old link text.

# BRIEF

*(Maintainer note — this is an F094 redirect stub; its redirect / no-new-content / removal / no-rename contract lives in the ruleset above.)*

- **The frontmatter `description::` is intentionally terse** ("superseded by …") so it surfaces in Dataview / search and readers see the redirect before opening — keep that phrasing aligned with the H1 callout.
