# RULESET R-trait
description:: Umbrella rule set aggregating the per-trait rule sets — rule sets that activate when an anchor declares the matching Trait in its `.anchor`. Parallel to [[R-facet]] (per-facet) and [[R-skill]] (per-skill).
includes:: [[R-paper]], [[R-simple]], [[R-skill-anchor]], [[R-topic]]

> [!info] How this set is wired
> Per the 2026-06-09 design: each CAB Trait spec file (`CAB Traits/<Trait Name>.md`) will carry a `# RULESET R-<trait>` second-H1 block with the trait's structural rules — co-located with the prose that defines the Trait. This file is the catalog-side umbrella that walks all those trait-scoped rule sets via `includes::` so adopters get a single name to pull.
>
> Today, the per-trait sets still sit as folder-files at the top of the Rule Sets catalog (`R-paper/`, `R-simple/`, `R-skill-anchor/`, `R-topic/`). As each one's content firms up, it migrates into the corresponding `CAB Traits/<Trait Name>.md` spec as an embedded RULESET block — exactly the pattern facet rule sets follow with CAB Facet specs.

## Adoption

```markdown
# {NAME} Decisions
include:: [[R-trait]]
```

This single include pulls in every CAB trait's structural rules. The anchor's declared Traits (`traits:` in `.anchor`) determine which subsets actually fire when audit runs — see [[F134]] for the trigger-axis design that filters trait-scoped rules to "rules that apply because this anchor's traits match."

## See also

- [[R-facet]] — sibling umbrella for per-facet rule sets.
- [[R-skill]] — sibling umbrella for per-skill rule sets.
- [[CAB Traits]] — the trait taxonomy (Code, Topic, Skill, Paper, Simple, Track, …).
- [[CAB Aspects]] — Trait/Facet umbrella model.
- [[Rulesets]] — parent catalog.
