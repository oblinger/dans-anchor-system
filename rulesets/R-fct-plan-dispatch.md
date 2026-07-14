# RULESET R-fct-plan-dispatch
include::
where:: `file: facets/DAS Plan Dispatch.md`
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
**Check pattern:** run `grep -rE '\[\[(DAS|FCT) Plan Dispatch' ~/ob/kmr/ --include="*.md"`; non-zero count = keep; zero count = deletion candidate.
**Why:** a redirect stub with no incoming links is dead weight; but premature removal breaks old wiki-links that still resolve through it.

### RULE R-fct-plan-dispatch-04 — Filename must not be renamed (stated)
The basename `DAS Plan Dispatch` is the link target old citations resolve to (renamed from `FCT Plan Dispatch` in the F229 sweep, which repointed inbound links); renaming it again silently breaks every `[[DAS Plan Dispatch]]` reference still in the vault.
**Check pattern:** file lives at `facets/DAS Plan Dispatch.md` with this exact basename.
**Why:** wiki-link resolution is name-based; the stub's value is entirely in its filename matching the old link text.
