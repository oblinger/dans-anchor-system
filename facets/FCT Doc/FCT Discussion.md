---
description: "per-document discussion log — dated trade-off threads attached to the doc they're about"
---
# FCT Discussion
Per-document discussion log — dated trade-off threads attached to the doc they're about.

| -[[FCT Discussion]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Doc]] → [FCT Discussion](hook://p/FCT%20Discussion)<br>: per-document discussion log — dated trade-off threads attached to the doc they're about |
| --- | --- |
| Related | [[FCT Decisions]],  [[FCT Log]],  [[FCT PRD]],  [[DSC dated-entry-stream]],   |
| Examples | [[HA Frontmatter\|inline method-1]],  [[HA Design Discussions\|sibling-file method-2]],   |

**TLDR** — A doc-scoped dated-entry-stream (cardinality: many) that attaches to spec docs — PRDs, Architecture, feature docs, etc. Each entry follows a Problem / Options Considered / Decision skeleton. Two placement methods: inline `# Discussion` H1 (default) or sibling `{Parent} Discussions.md` (when inline grows past ~2 screens). Append-only after Decision is filled. Does NOT attach to navigation/sequencing artifacts (anchor pages, dispatch pages, Backlog, Roadmap).

Discussion is the first **document-scoped facet** in CAB. Unlike anchor-scoped facets (which carry one instance per anchor — `{NAME} Backlog.md`, `{NAME} PRD.md`), a document-scoped facet attaches to a specific *document* and may exist many times within one anchor (one Discussion per discussable doc). The provenance — *what is being discussed* — is preserved by anchoring the discussion to the document it's about.

The principle: **discussion belongs to the thing being discussed**. A discussion about a PRD belongs to that PRD. A discussion about a feature belongs to that feature doc. A discussion about an Architecture sub-page belongs to that sub-page. Pulling all discussion into one anchor-level file (the historical `{NAME} Discussion.md`) loses the link to provenance and forces the reader to grep for the relevant thread.

> [!info] Migrated from anchor-scoped
> CAB Discussion was previously anchor-scoped (`{NAME} Docs/{NAME} Plan/{NAME} Discussion.md`, one per anchor). 2026-06-11: re-scoped to per-document. Existing `{NAME} Discussion.md` files in legacy anchors continue to work but are deprecated; new discussions follow the doc-scoped form. CAE's `CAE Discussion.md` is a legacy worked example pending migration.

## Placement — Discussion is a dated-entry-stream

Discussion is a [[DSC dated-entry-stream]] attached to a parent doc. **Methods supported: 1 (inline, default) and 2 (sibling file).** Method 3 (sibling folder) is out of scope for Discussion — entries are rarely large or numerous enough to deserve their own files; if Discussion ever grows to method-3 size, the right move is usually to split the parent doc, not the discussion.

- **Method 1 — inline `# Discussion` H1** at the end of the parent doc. Default for any new discussion.
- **Method 2 — sibling file `{Parent} Discussions.md`** (plural). Migrate when the inline form has grown past ~1–2 screens of body content. Parent doc links to it from its dispatch table; the inline `# Discussion` H1 is removed.

Naming, migration direction, dispatch linkage, one-form-per-parent invariant, and reverse-chronological ordering all come from [[DSC dated-entry-stream]] — see that discipline for the canonical rules.

## Entry shape

Each dated H2 entry follows a four-section skeleton (the last is optional). This is Discussion's facet-specific entry shape (the *parallel-entry-skeleton invariant* from [[DSC dated-entry-stream]] § R-dated-entry-stream-06 requires *some* skeleton; this is the one Discussion uses):

```markdown
## 2026-06-11 — Thread Pool vs Async for Task Execution

### The Problem
Concise framing of the question or tension that prompted the discussion.

### Options Considered
- **A. <name>** — one-line description.
- **B. <name>** — one-line description.
- **C. <name>** — one-line description.

### Decision
What was chosen and (one sentence) the deciding factor.

### Why This Works  (optional)
Additional rationale, links to evidence, edge cases handled. Skip when the Decision section is self-evident.
```

H3 headings (`### The Problem`, `### Decision`, etc.) are required — they make entries skimmable and link-targetable. Body content uses the [[DSC markdown]] discipline (named lists, wiki-links, no markdown in fenced code blocks).

## Where to attach Discussion

Any document in any anchor MAY have a Discussion attached. Common attachment points:

- Design facets — `{NAME} PRD.md`, `{NAME} Architecture.md`, `{NAME} UX Design.md`, `{NAME} API Design.md`, `{NAME} Testing.md`, `{NAME} Roadmap.md`. (Most common — design choices breed discussion.)
- Feature docs — `F<NNN> — Title.md` in `{NAME} Features/`. Per-feature design threads.
- Architecture sub-pages — `{NAME} Architecture/{Subsystem}.md`. Per-subsystem discussion.
- Long-lived spec docs — anything where decisions accumulate over time.

Documents that typically do NOT carry discussion: the anchor page (`{NAME}.md`, navigation only), dispatch pages (`{NAME} Docs.md`, `{NAME} Design.md`), the Backlog (`{NAME} Backlog.md` — discussion belongs on the feature doc the row points at), the Roadmap (`{NAME} Roadmap.md` — discussion belongs on the milestone's feature doc, not on the sequencing artifact itself).

## Audit posture

Discussion is **append-only**. Entries are never edited after the Decision is filled; the document the discussion attaches to (the PRD, the Architecture, etc.) reflects the current state — the discussion is the log of how it got there. Subsequent revisits to the same question create a new entry (with its own date) referencing the prior decision.

## Relationship to other facets

| Facet | Relationship |
|---|---|
| **[[FCT PRD]] / [[FCT Architecture]] / [[FCT UX Design]] / [[FCT API Design]] / etc.** | The *spec* surfaces (anchor-scoped). Discussion attaches to any of them as a doc-scoped peer. |
| **[[FCT Decisions]]** | Anchor-level decisions log — *load-bearing* decisions that cite rules and span the anchor. Discussion is finer-grained, per-document, captures the reasoning *behind* a single doc's choices. The decisions log gets the headlines; the discussion gets the deliberation. |
| **Open Questions (on feature docs)** | When an open question on a feature doc spawns extended analysis that doesn't fit in the question body, that analysis goes into the feature doc's `# Discussion` (inline) or `F<NNN> Discussions.md` (extracted). Resolving the question links to the discussion entry. |
| **[[FCT Log]]** | Sibling [[DSC dated-entry-stream]] facet — Log uses the same three placement methods, different entry skeleton, different attachment scope (anchor-level today, potentially doc-level later). |

## See also

- [[DSC dated-entry-stream]] — discipline owning placement, naming, migration, dispatch linkage.
- [[DSC file-association]] — parent umbrella discipline.
- [[FCT Decisions]] — anchor-level decisions log (different altitude).
- [[FCT Log]] — sibling dated-entry-stream facet.
- [[FCT Facets]] — facet catalog with the Document-scoped row.
- [[CAE Discussion]] — legacy anchor-scoped example, pending migration (see [[SKA Backlog]] § F149).


# RULESET R-discussion
include::
where:: sentinel: ^#+ Discussion
description:: planning trade-offs

Embedded ruleset for the Discussion facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via [[R-facet]] umbrella.

**Delegation.** Five placement-shape rules from the prior version moved into [[DSC dated-entry-stream#RULESET R-dated-entry-stream|R-dated-entry-stream]] (preface, naming, one-form-per-parent, reverse-chronological, dispatch linkage). This ruleset retains only the rules that are Discussion-specific.

### RULE R-discussion-01 — Doc-scoped, never anchor-scoped (stated)

Discussion attaches to a specific document, not to the whole anchor. There is no `{NAME} Discussion.md` form in modern anchors — that filename is the legacy anchor-scoped form, deprecated 2026-06-11.

**Check pattern:** for each `{NAME} Discussion.md` found at an anchor's Plan / Design folder root, flag as legacy; auto-fix is migrate to per-doc inline or extracted form (per [[SKA Backlog]] F149 sweep).

**Why:** lumping all discussion in one anchor-level file loses provenance — the reader can't tell which spec the discussion is about without re-reading every entry.

### RULE R-discussion-02 — Discussion declares methods 1 and 2; method 3 out of scope (stated)

Per [[DSC dated-entry-stream]] § R-dated-entry-stream-09, every citing facet declares its supported methods and default. Discussion's declaration: **methods 1 (inline, default) and 2 (sibling file)**. Method 3 (sibling folder of dated entry files) is out of scope — Discussion entries are not the right granularity for per-entry files.

**Check pattern:** for each Discussion instance, assert it is method 1 or method 2; method 3 instances fail with "Discussion uses methods 1+2 only; consider splitting the parent doc instead."

**Why:** if Discussion would benefit from method 3, the symptom is usually that the parent doc has accumulated too many distinct concerns — splitting the parent (and its discussion) is the right fix, not folder-extracting one document's stream.

### RULE R-discussion-03 — Entry skeleton: Problem / Options Considered / Decision (sampled)

Each dated H2 entry has, in order, three H3 sub-sections: `### The Problem`, `### Options Considered`, `### Decision`. An optional `### Why This Works` may follow.

**Check pattern:** sample entries; assert the three H3s are present in order; assert no other H3s precede them.

**Why:** the skeleton makes entries skimmable, comparable, and link-targetable. Free-form prose makes the log un-greppable for "what did we decide about X." This is Discussion's per-facet declaration of the [[DSC dated-entry-stream]] § R-dated-entry-stream-06 parallel-entry invariant.

### RULE R-discussion-04 — Append-only after Decision (stated)

Once an entry's Decision section is filled, the entry is NOT edited. Subsequent revisits to the same question create a new entry (with its own date) referencing the prior decision. The spec docs reflect the current state; the discussion is the log of how the spec got there.

**Check pattern:** stated for now; future tooling could flag entries with edit timestamps materially after their dated header (git blame check).

**Why:** an editable log loses its value as a log. Future readers need to know what was decided *and when*; editing entries destroys that.

### RULE R-discussion-05 — Where discussion does NOT attach (stated)

Discussion does NOT attach to: anchor pages (`{NAME}.md`), dispatch pages (`{NAME} Docs.md`, `{NAME} Design.md`), the Backlog (`{NAME} Backlog.md`), the Roadmap (`{NAME} Roadmap.md`), `.anchor` files. Discussion belongs on the *spec* surface, not on navigation or sequencing artifacts.

**Check pattern:** for each `# Discussion` H1 or `{X} Discussions.md` found, assert `{X}` is NOT one of the forbidden kinds.

**Why:** discussion on a dispatch page would be discussion of the navigation choice (rare and unhelpful); discussion on the Backlog would discuss the sequencing of work (which belongs on the milestone's feature doc, not on the Backlog itself). Confining to spec surfaces keeps the log focused.

# BRIEF

- **This is the Discussion facet spec** — the doc-scoped dated-entry-stream for design trade-off threads. It was re-scoped from anchor-scoped to doc-scoped on 2026-06-11; legacy `{NAME} Discussion.md` files are deprecated (migration tracked in [[SKA Backlog]] § F149). Do not revert to anchor-scoped wiring.
- **Cardinality: many** — one Discussion per attachable doc (PRDs, Architecture, feature docs, spec sub-pages). Each Discussion belongs to the doc it's about — inlined under `# Discussion` H1 (method 1, default) or extracted to `{Parent} Discussions.md` (method 2). Method 3 is out of scope; if an inline Discussion grows that large, split the parent doc instead.
- **Placement rules and naming delegate to [[DSC dated-entry-stream]]** — this spec owns only Discussion-specific rules (entry skeleton, methods 1+2 declaration, attachment-scope guard, append-only posture). When editing placement or naming logic, update `R-dated-entry-stream`, not this file.
