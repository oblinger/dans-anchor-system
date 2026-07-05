# RULESET R-progressive
include:: [[DSC progressive-disclosure#RULESET R-progressive\|embedded body]]
description:: Conditional, multi-check document-layout rules of progressive disclosure — dispatch-table placement + section spacing; checked on every markdown document.

Catalog-side stub for the progressive-disclosure discipline's ruleset. Canonical body lives embedded inside the [[DSC progressive-disclosure]] discipline file per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[DSC progressive-disclosure#RULESET R-progressive|the embedded block]]. 2 rules:

- **R-progressive-01** — never both a self-masthead and a `:>>` breadcrumb (a doc uses one navigation form, not two).
- **R-progressive-02** — progressive-disclosure section spacing (blank before every H2; no trailing blank line).

## Position in the catalog

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella), beside [[R-markdown]]. Applies to every markdown doc (`always`) — each rule decides internally whether/how it constrains a given doc.

## See also

- [[DSC progressive-disclosure]] — discipline spec; contains the embedded RULESET body.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[R-markdown]] — sibling always-applies ruleset (mechanical + authoring markdown rules).
