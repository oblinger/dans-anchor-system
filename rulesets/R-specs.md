# RULESET R-specs
include::
where:: `file: **/specs/*/spec.md`
description:: Rules for the OpenSpec-conformant `specs/` folder ([[DAS Specs]]) — the anchor's durable per-capability behavioral contract, written only by `/finalize`'s archive-merge.

### RULE R-specs-01 — Exactly one spec.md per capability folder (stated)
`specs/<capability>/` holds exactly one file, named `spec.md`. Richer material (rationale, PRD, architecture) lives in `{slug} Design/`, never beside the spec.
**Why:** OpenSpec tooling reads exactly this shape; sibling files break conformance and blur contract vs. commentary.

### RULE R-specs-02 — Requirements are RFC-2119 with scenarios (stated)
Each spec is `# <Capability>` + `## Requirements`, with one `### Requirement: <name>` H3 per requirement using MUST/SHOULD/MAY, each carrying `#### Scenario:` Given/When/Then blocks.
**Why:** the keywords make the contract testable in principle; the scenarios make it testable in practice ([[DAS Testing]] derives scenario tests from them).

### RULE R-specs-03 — Specs change only via the archive-merge (stated)
`specs/` content is modified exclusively by `/finalize` folding a change's delta; a hand-edit to `specs/` is an audit finding.
**Why:** routing every edit through a change keeps `changes/archive/` a complete history of how the contract evolved.
