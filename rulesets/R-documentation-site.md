# RULESET R-documentation-site
include::
where:: `anchor`
description:: an anchor's published web presence — Jekyll project page or MkDocs full site

What `/audit publish` checks on an anchor's documentation-site facet. Optional — cardinality one per anchor. Format of this set: [[DAS Ruleset]].

### RULE R-documentation-site-01 — At most one tier per anchor (checked)

An anchor adopts at most one Documentation Site tier — a `website/` project page OR a `docs/mkdocs.yml` full site, never both simultaneously.

**Check pattern:** not both `website/` and `docs/mkdocs.yml` are present in the anchor's repo.

**Why:** the choice point (which tier the anchor needs) is the facet's main value; two tiers means an undecided publish target.

### RULE R-documentation-site-02 — Tier is detected by folder presence (stated)

Adoption is folder-existence: `website/` ⇒ project-page tier; `docs/mkdocs.yml` ⇒ documentation-site tier. No separate declaration is needed.

### RULE R-documentation-site-03 — Full site uses the fixed stack (sampled)

A documentation-site-tier anchor's `mkdocs.yml` uses MkDocs Material + `mkdocstrings[python]` + `mkdocs-jupyter` + the roamlinks plugin (so `[[wikilinks]]` resolve), with those packages declared in `pyproject.toml` dev deps.

**Check pattern:** `mkdocs.yml` names the `material` theme and the `roamlinks` + `mkdocstrings` + jupyter plugins.

### RULE R-documentation-site-04 — Deployment goes through a `just` recipe / gh-deploy (stated)

Publishing is via `just docs-deploy` (copy `site/` to the website repo) or `mkdocs gh-deploy` (gh-pages branch) — per the [[code-publish]] workflow — not ad-hoc manual copying.
