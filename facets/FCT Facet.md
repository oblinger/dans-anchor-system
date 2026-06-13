---
description: "the Facet primitive — what a facet is and how to write its spec"
---
# FCT Facet

A **facet** is a narrow, usually file-based aspect of an anchor — one specific structural feature (a `Backlog` file, an `Architecture` doc, a website subfolder), defined by its own spec doc and detected (by default) through file-existence. This page is the spec for *the facet kind itself*: what a facet is and the shape every facet spec doc takes. It is the singular **definition**; [[FCT Facets]] (plural) is the **index** of all concrete facets.

Facets are one of the two kinds of [[CAB Aspects|Aspect]] — the narrow, file-based kind; the broad declared-paradigm kind is the [[CAB Traits|Trait]]. The shared model lives in [[CAB Aspects]]; this page is the facet-authoring view of it.

**Worked examples (real facet instances):** [[FEX Manifest]] (a skill-world doc facet), [[HBR Backlog]], [[HBR Architecture]], [[HBR PRD]], [[HBR Roadmap]] — catalogued in [[FEX]].

# Reference Example
---

A facet spec doc has this shape — illustrated with a small `Manifest` facet:

```markdown
---
description: the record a snapshot bundle carries
---
# Manifest

## What it is
A manifest.txt written beside each snapshot bundle so a restore knows what state it captured.

## How it's detected
File-existence — a manifest.txt inside a snapshots/<label>/ directory.

## Format
One `key: value` per line, keys lower-case; required keys label, commit, branch, created; paths bundle-relative.

## Constraints
- Exactly one manifest per bundle (cardinality: one).
- No absolute paths (format invariant).

## Expected Usage
- Written by the snapshot skill at capture; read by restore and by the retention sweep.

## Skills and audits that attach
- The snapshot skill writes it; an audit checks it against the R-fex-manifest rule set.
```

For a *worked instance* of this facet — an actual manifest — see [[FEX Manifest]].

---

# Format Specification

## Location
A facet spec is one file: `facets/FCT <Name>.md` (published form; historically `CAB/CAB Facets/<Name>.md`). One spec per facet; it is authoritative for that facet.

## The six things a facet spec declares
Per [[CAB Aspects]] § Facet, every facet spec owns six things:

1. **Detection** — how the system decides the facet is present. Default file-existence; override in the spec for anything else.
2. **Cardinality** — `one` (one Backlog per anchor) or `many` (many Feature docs per anchor).
3. **Format constraints** — filename pattern, frontmatter, required body sections, naming.
4. **Behavior** — which skills and audits act on the facet.
5. **Constraints** — legal-usage rules: mutual exclusion, co-requirement, format invariants.
6. **Expected Usage** — recommended patterns: common combinations, typical scale, naming, skill pairings.

## Spec-doc shape
Every Aspect spec — Trait or Facet — uses the same section order (see [[CAB Aspects]] § Spec-doc structure):
`## What it is` → `## How it's detected` → `## Format` → `## Constraints` → `## Expected Usage` → `## Skills and audits that attach`, plus an optional `## Triggers` when the facet declares behavioral triggers.

## Facet vs Trait
File-shaped narrow aspect → **Facet** (here). Broad declared paradigm in `traits:` → **Trait** ([[CAB Traits]]). If it's about a specific file or folder it's a Facet; if it names what the anchor *is*, it's a Trait. Full distinction: [[CAB Aspects]] § Trait vs Facet.

# BRIEF

- **This is the spec for the *facet* primitive** — what a facet is and the shape of a facet spec doc. Sibling to [[FCT Skill]] (skill primitive) and [[FCT Rules]] (rule-set primitive); indexed from [[FCT Primitives]].
- **Singular, not the index.** [[FCT Facets]] (plural) is the *catalog* of concrete facets; this page (singular) *defines the kind*. The Primitives-row "Facet" link points here, not at the index.
- **The umbrella model lives in [[CAB Aspects]]** — don't duplicate the Aspect/Trait/Facet vocabulary, the six-section rationale, or the composability matrix here; link to it. This page is the facet-authoring view: the six declarations + the spec-doc shape + real examples.
- **Examples are real instances**, defined per [[FEX]] — [[FEX Manifest]] and the HBR facet set ([[HBR Backlog]], [[HBR Architecture]], [[HBR PRD]], …). Keep these links current as the gallery evolves.
