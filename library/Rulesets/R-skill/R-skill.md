# RULESET R-skill
description:: Umbrella rule set aggregating the per-skill rule sets — rules associated with individual skills the agent performs (mint, ask, atlas, redline, feature, groom, etc.). Parallel to [[R-facet]] (per-facet) and [[R-trait]] (per-trait).
includes::

> [!info] How this set is wired
> Per the 2026-06-09 design: each skill spec file (`~/.claude/skills/<skill>/SKILL.md`) will carry a `# RULESET R-<skill>` block with the skill's structural rules — co-located with the runbook that defines the skill. This file is the catalog-side umbrella that walks all those skill-scoped rule sets via `includes::`.
>
> `includes::` is empty for now — embedded rule sets land skill-by-skill as the catalog matures. Likely first candidates: `R-ask` (the ask-format discipline as enforceable rules), `R-feature` (feature-doc structural invariants), `R-atlas` (Atlas discipline as rules).

> [!info] Renamed from prior R-skill (2026-06-09)
> The previous `R-skill/` folder was trait-scoped (rule sets for anchors declaring the Skill trait). That folder was renamed [[R-skill-anchor]] to free the name `R-skill` for this umbrella. The previous content was an empty placeholder; no rules were lost.

## Adoption

```markdown
# {NAME} Decisions
include:: [[R-skill]]
```

This single include pulls in every skill's structural rules. Use when authoring a skill-anchor that contains multiple skills, or when an audit pass needs to verify every skill spec's invariants.

## See also

- [[R-facet]] — sibling umbrella for per-facet rule sets.
- [[R-trait]] — sibling umbrella for per-trait rule sets.
- [[R-skill-anchor]] — trait-scoped rules for Skill-anchor type (NOT this umbrella).
- [[SKL Skills]] — the skill catalog.
- [[Rulesets]] — parent catalog.
