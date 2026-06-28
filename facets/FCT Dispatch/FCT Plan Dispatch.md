---
description: superseded by CAB Track Dispatch per F094 — see redirect below
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Dispatch]] → [FCT Plan Dispatch](hook://p/FCT%20Plan%20Dispatch)

# FCT Plan Dispatch
Redirect stub for the legacy `{NAME} Plan/` dispatch facet, superseded by [[FCT Track Dispatch]] and [[FCT Design Dispatch]] per F094.

**Related:** [[FCT Track Dispatch]],  [[FCT Design Dispatch]],  [[FCT Dispatch]]
**Examples:** [[CAE Track\|minimal (renamed from CAE Plan per F094)]],  [[HBR Track\|fuller]]

> **Superseded by [[FCT Track Dispatch]]** per [[F094 — Anchor docs folder restructure — Track _ User _ Architecture _ Dev|F094]] (2026-06-01).
>
> The `{NAME} Plan/` folder is renamed to `{NAME} Track/` matching the [[Track]] trait name. PRD / System Design / UX Design content moves into `{NAME} Design/` (see [[FCT Design Dispatch]]). The Plan slot is freed for a future top-level strategic-plan *document* inside the Track tree.
>
> This file preserved as a redirect-stub during the F094 migration window. All references to `[[FCT Plan Dispatch]]` should migrate to `[[FCT Track Dispatch]]` (planning surface) or `[[FCT Design Dispatch]]` (design surface) depending on what the citation was actually pointing at.

## Legacy reference

(Kept for the migration window — readers landing here from old wiki-links should follow [[FCT Track Dispatch]] for the new tracking surface or [[FCT Design Dispatch]] for the new design surface.)

**Cardinality: one per anchor** — a single `{NAME} Plan/` folder (now `{NAME} Track/`) existed per anchor; this redirect stub mirrors that one-per-anchor contract.

# RULESET R-fct-plan-dispatch
include::
where:: file: facets/FCT Dispatch/FCT Plan Dispatch.md
description:: Rules for the redirect stub — this file's sole job is catching incoming `[[FCT Plan Dispatch]]` links during the F094 migration window and pointing to the successors.

### RULE R-fct-plan-dispatch-01 — No normative content added to this stub (checked)
This file must not grow new prose, rules, or tables beyond the redirect callout and migration note. Its entire normative authority is delegated to [[FCT Track Dispatch]] and [[FCT Design Dispatch]].
**Check pattern:** the file body contains no `## Format`, `## Constraints`, or `### RULE` sections outside this ruleset.
**Why:** any expansion of this stub creates a second authoritative source for the Track/Design split; all additions belong in the successor specs.

### RULE R-fct-plan-dispatch-02 — Redirect callout links both successors (checked)
The redirect blockquote must link [[FCT Track Dispatch]] (planning surface) and [[FCT Design Dispatch]] (design surface) explicitly.
**Check pattern:** both `[[FCT Track Dispatch]]` and `[[FCT Design Dispatch]]` appear in the blockquote.
**Why:** incoming references pointed at `Plan/` for two distinct purposes — planning and design — each needs its own forward pointer.

### RULE R-fct-plan-dispatch-03 — File removed when zero incoming links remain (stated)
Once a vault-wide grep finds zero `[[FCT Plan Dispatch]]` references, this file may be deleted. Until then it must remain to preserve wiki-link integrity.
**Check pattern:** run `grep -r 'FCT Plan Dispatch' ~/ob/kmr/ --include="*.md"`; non-zero count = keep; zero count = deletion candidate.
**Why:** a redirect stub with no incoming links is dead weight; but premature removal breaks old wiki-links that still resolve through it.

### RULE R-fct-plan-dispatch-04 — Filename must not be renamed (stated)
The basename `FCT Plan Dispatch` is the link target old citations resolve to; renaming it silently breaks every `[[FCT Plan Dispatch]]` reference still in the vault.
**Check pattern:** file lives at `facets/FCT Dispatch/FCT Plan Dispatch.md` with this exact basename.
**Why:** wiki-link resolution is name-based; the stub's value is entirely in its filename matching the old link text.

# BRIEF

- **This file is a redirect stub, not a live spec.** Its sole job is to catch incoming `[[FCT Plan Dispatch]]` wiki-links during the F094 migration window and point readers at the successor specs.
- **The live successors are [[FCT Track Dispatch]] (planning surface) and [[FCT Design Dispatch]] (design surface).** Any new dispatch-facet content belongs in one of those — never extend this file with new prose.
- **Do NOT add normative rules, tables, or examples here.** If a question arises about the Plan/Track/Design split, update the successor spec; this stub only redirects.
- **Removal criterion:** when the vault has zero remaining `[[FCT Plan Dispatch]]` references (audit via grep), this file may be deleted. Until then it must remain to preserve link integrity.
- **Do not rename or move this file.** Its basename is the link target old citations resolve to; renaming breaks the redirect contract.
- **The frontmatter `description::` is intentionally terse** ("superseded by …"); it surfaces in Dataview / search so users see the redirect before opening — keep that phrasing aligned with the H1 callout.
