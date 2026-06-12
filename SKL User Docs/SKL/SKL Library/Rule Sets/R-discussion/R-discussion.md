# RULESET R-discussion
include:: [[CAB Discussion#RULESET R-discussion|embedded body]]
description:: Catalog stub — rules for `# Discussion` (inline) or `{Doc} Discussions.md` (extracted), the first *document-scoped* facet. Canonical body lives embedded in [[CAB Discussion]].

Catalog-side stub for the Discussion facet's rule set. The canonical body lives embedded inside the [[CAB Discussion]] facet file per the [[F133 — Rule sets folder convention + facet embedding|F133]] convention.

**To see the actual rules:** follow [[CAB Discussion#RULESET R-discussion|the embedded block]]. 9 rules covering:

- **Scope (1)** — doc-scoped, never anchor-scoped; legacy `{NAME} Discussion.md` is deprecated.
- **Placement (3)** — inline `# Discussion` H1 at parent doc end; OR extracted to sibling `{Doc} Discussions.md` (plural); one form at a time per doc.
- **Entries (2)** — reverse chronological (newest first); standard skeleton (Problem / Options Considered / Decision / optionally Why This Works).
- **Posture (1)** — append-only; spec docs reflect current state, discussion is the log of how the spec got there.
- **Scope guard (1)** — does NOT attach to anchor pages, dispatch pages, Backlog, or Roadmap.
- **Pattern (1)** — same dual-form (inline → extracted) precedent that [[FCT Stories]] uses.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). **First doc-scoped facet** — distinct posture from the anchor-scoped facets that dominate the umbrella's current children. Future doc-scoped facets (Open Questions, Changelog, Revision Notes, Acceptance Criteria, etc.) follow the same shape.

## Adoption

Pulled automatically via the [[R-facet]] umbrella; an anchor adopting `include:: [[R-facet]]` gets R-discussion for free. No explicit `include:: [[R-discussion]]` needed.

## See also

- [[CAB Discussion]] — facet spec; contains the embedded RULESET body.
- [[R-facet]] — umbrella catalog.
- [[FCT Stories]] — sibling facet using the same dual-form pattern (inline → extracted).
- [[Rule Sets]] — top-level catalog.
