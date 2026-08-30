# RULESET R-discussion
include:: [[R-stream]] 
where:: `sentinel: ^#+ Discussion`
description:: planning trade-offs

Embedded ruleset for the Discussion facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Armed by **both** executing umbrellas: [[R-doc]], which `/audit doc` and the on-write doc-fire resolve, and [[R-anchor]], which `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[Tink Backlog#^T208|T208]]).

**Delegation.** Five placement-shape rules from the prior version moved into [[R-stream]] (preface, naming, one-form-per-parent, reverse-chronological, dispatch linkage). This ruleset retains only the rules that are Discussion-specific.

### RULE R-discussion-01 — Doc-scoped, never anchor-scoped (stated)

Discussion attaches to a specific document, not to the whole anchor. There is no `{slug} Discussion.md` form in modern anchors — that filename is the legacy anchor-scoped form, deprecated 2026-06-11.

**Check pattern:** for each `{slug} Discussion.md` found at an anchor's Plan / Design folder root, flag as legacy; auto-fix is migrate to per-doc inline or extracted form (per [[Tink Backlog]] F149 sweep).

**Why:** lumping all discussion in one anchor-level file loses provenance — the reader can't tell which spec the discussion is about without re-reading every entry.

### RULE R-discussion-02 — Discussion declares methods 1 and 2; method 3 out of scope (stated)

Per [[R-file-association]]-01, every citing facet declares its supported methods and default. Discussion's declaration: **methods 1 (inline, default) and 2 (sibling file)**. Method 3 (sibling folder of dated entry files) is out of scope — Discussion entries are not the right granularity for per-entry files.

**Check pattern:** for each Discussion instance, assert it is method 1 or method 2; method 3 instances fail with "Discussion uses methods 1+2 only; consider splitting the parent doc instead."

**Why:** if Discussion would benefit from method 3, the symptom is usually that the parent doc has accumulated too many distinct concerns — splitting the parent (and its discussion) is the right fix, not folder-extracting one document's stream.

**Tested against the hardest case, 2026-08-06** ([[Tink310 - Stream: one reverse-chronological facet at three volumes|TINK F310]] Gap 2). The obvious hole in the reasoning above is a parent that *cannot* be split, and [[DAS Rocks|Rocks]] supplies one: a rock file is a single chunk of work whose deliberation accumulates for a quarter, and the rock is the unit. It still does not want method 3. Method 2 puts `{slug} {ABBR} Discussions.md` in the `{slug} Rocks/` folder beside its rock — the folder method 3 would have to invent already exists. Worse, a method-3 `{slug} {ABBR} Discussions/` would become a *member* of the Rocks folder: it lands in the `...` catch-all and `R-rocks-05` warns on it forever, because a discussion folder is not a rock and can never be ranked. So the rule survives its strongest counter-case, and this is why — a demonstration, where the paragraph above it was a guess.

### RULE R-discussion-03 — Entry skeleton: Problem / Options Considered / Decision (sampled)

Each dated H2 entry has, in order, three H3 sub-sections: `### The Problem`, `### Options Considered`, `### Decision`. An optional `### Why This Works` may follow.

**Check pattern:** sample entries; assert the three H3s are present in order; assert no other H3s precede them.

**Why:** the skeleton makes entries skimmable, comparable, and link-targetable. Free-form prose makes the log un-greppable for "what did we decide about X." This is Discussion's per-facet declaration of the [[DAS stream]] § R-stream-02 parallel-entry-skeleton invariant.

### RULE R-discussion-04 — Append-only after Decision (stated)

Once an entry's Decision section is filled, the entry is NOT edited. Subsequent revisits to the same question create a new entry (with its own date) referencing the prior decision. The spec docs reflect the current state; the discussion is the log of how the spec got there.

**Check pattern:** stated for now; future tooling could flag entries with edit timestamps materially after their dated header (git blame check).

**Why:** an editable log loses its value as a log. Future readers need to know what was decided *and when*; editing entries destroys that.

### RULE R-discussion-05 — Where discussion does NOT attach (stated)

Discussion does NOT attach to: anchor pages (`{slug}.md`), dispatch pages (`{slug} Docs.md`, `{slug} Design.md`), the Backlog (`{slug} Backlog.md`), the Roadmap (`{slug} Roadmap.md`), `.anchor` files. Discussion belongs on the *spec* surface, not on navigation or sequencing artifacts.

**Check pattern:** for each `# Discussion` H1 or `{X} Discussions.md` found, assert `{X}` is NOT one of the forbidden kinds.

**Why:** discussion on a dispatch page would be discussion of the navigation choice (rare and unhelpful); discussion on the Backlog would discuss the sequencing of work (which belongs on the milestone's feature doc, not on the Backlog itself). Confining to spec surfaces keeps the log focused.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). **First doc-scoped facet** — distinct posture from the anchor-scoped facets that dominate the umbrella's current children. Future doc-scoped facets (Open Questions, Changelog, Revision Notes, Acceptance Criteria, etc.) follow the same shape.

## Adoption

Armed by **both** executing umbrellas: [[R-doc]], which `/audit doc` and the on-write doc-fire resolve, and [[R-anchor]], which `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[Tink Backlog#^T208|T208]]).

## See also

- [[DAS Discussion]] — facet spec this ruleset enforces.
- [[R-facet]] — umbrella catalog.
- [[DAS Stories]] — sibling facet using the same dual-form pattern (inline → extracted).
- [[DAS Rulesets]] — top-level catalog.
