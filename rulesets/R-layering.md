# RULESET R-layering
include::
description:: Keeps the anchor-system layer cake real — one-directional coupling (Anchorage ← Warden ← TAS-core ← DAS content), per-skill dependency footprints, and generic-vs-personal provenance legibility. Ratified 2026-07-12; spec home: SKA System Design § System layers & coupling, SKA PRD § System Layers & the Adoption Ladder.

The three disciplines these rules enforce were ratified 2026-07-12 as architecture-locked properties, not aspirations: each layer is separately adoptable only if lower layers stay ignorant of upper ones, adoption rung 2 (grab one skill) only works if every skill declares its needs, and the future TAS extraction stays a mechanical filter only if every file's provenance is legible.

### RULE R-layering-01 — Warden code never references DAS content (checked)

No file under `warden/` engine code (`warden/engine/`, `warden/warden`, `warden/warden-rs/`) may reference DAS content paths (`skills/`, `facets/`, `disciplines/`, `docs/`, `examples/`, `templates/`, `rulesets/`) or resolve them implicitly. Warden consumes rule corpora handed to it by configuration; it never reaches into the catalog. **Check pattern:** grep warden engine sources for those path segments; any hit that is not reading a configured corpus root is a violation.

### RULE R-layering-02 — Lower-layer docs stay layer-local (sampled)

Warden's own documentation, design, and tracking (`warden/Warden *`) describe Warden in its own terms — they may cite upper layers as *adopters* or *examples*, but no lower-layer behavior, interface, or invariant may be *defined* in terms of an upper layer. If deleting every DAS-specific reference from a Warden doc would leave its normative content intact, the doc passes.

### RULE R-layering-03 — Every skill declares its dependency footprint (checked)

Every `skills/<name>/SKILL.md` carries a `requires::` inline field directly after its H1. Value is comma-separated from the controlled vocabulary — `none`, `vault`, `anchor-cli`, `warden`, `skill:<name>`, `facet:<facet-name>`, `external:<binary>` — and is exactly `none` when the skill is self-contained. Format spec: SKA System Design § System layers & coupling. **Check pattern:** a `SKILL.md` without a `requires::` line, or with a token outside the vocabulary, is a violation.

### RULE R-layering-04 — Declared footprint matches actual use (sampled)

A skill's `requires::` declaration covers what the skill actually touches: a runbook or script that invokes `state`/`das` declares `anchor-cli`; one that fires or configures the rule engine declares `warden`; one that shells out to a non-bundled binary declares `external:<binary>`; one that reads or writes a facet's file shape declares `facet:<name>`. **Check pattern:** for a sampled skill, grep its SKILL.md + scripts for tool invocations and facet paths; any undeclared dependency is a violation, as is a declared dependency with no remaining use.

### RULE R-layering-05 — Every published file is provenance-legible (stated)

Every file in the published repo must be classifiable as *generic* (TAS-bound) or *personal* (Dan-specific) without archaeology. Personal material lives only in designated zones: BRIEF sections (the F223 discipline), `das-*`-prefixed skills, and examples clearly marked as instances. A file mixing generic spec and personal specifics outside those zones is a violation — the TAS recipe must stay a filter, never a per-file judgment call.
