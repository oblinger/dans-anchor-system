---
description: "per-document discussion log — dated trade-off threads attached to the doc they're about"
group: slot
---

| -[[DAS Discussion]]- | → [[DAS]] → [[FCT]] → [DAS Discussion](hook://p/DAS%20Discussion)  |
| --- | --- |
| Related | [[DAS Decisions]],  [[DAS Log]],  [[DAS PRD]],  [[DAS stream]],   |
| Examples | [[HA Frontmatter\|inline method-1]],  [[HA Design Discussions\|sibling-file method-2]],   |
| Rules | [[R-discussion]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Discussion
Per-document discussion log — dated trade-off threads attached to the doc they're about.

**TLDR** — A doc-scoped stream (cardinality: many) that attaches to spec docs — PRDs, Architecture, feature docs, etc. Each entry follows a Problem / Options Considered / Decision skeleton. Two placement methods: inline `# Discussion` H1 (default) or sibling `{Parent} Discussions.md` (when inline grows past ~2 screens). Append-only after Decision is filled. Does NOT attach to navigation/sequencing artifacts (anchor pages, dispatch pages, Backlog, Roadmap).

Discussion is the first **document-scoped facet** in CAB. Unlike anchor-scoped facets (which carry one instance per anchor — `{slug} Backlog.md`, `{slug} PRD.md`), a document-scoped facet attaches to a specific *document* and may exist many times within one anchor (one Discussion per discussable doc). The provenance — *what is being discussed* — is preserved by anchoring the discussion to the document it's about.

The principle: **discussion belongs to the thing being discussed**. A discussion about a PRD belongs to that PRD. A discussion about a feature belongs to that feature doc. A discussion about an Architecture sub-page belongs to that sub-page. Pulling all discussion into one anchor-level file (the historical `{slug} Discussion.md`) loses the link to provenance and forces the reader to grep for the relevant thread.

> [!info] Migrated from anchor-scoped
> CAB Discussion was previously anchor-scoped (`{slug} Docs/{slug} Plan/{slug} Discussion.md`, one per anchor). 2026-06-11: re-scoped to per-document. Existing `{slug} Discussion.md` files in legacy anchors continue to work but are deprecated; new discussions follow the doc-scoped form. CAE's `CAE Discussion.md` is a legacy worked example pending migration.

## Placement — Discussion is a stream

Discussion is a [[DAS stream]] attached to a parent doc. **Methods supported: 1 (inline, default) and 2 (sibling file).** Method 3 (sibling folder) is out of scope for Discussion — entries are rarely large or numerous enough to deserve their own files; if Discussion ever grows to method-3 size, the right move is usually to split the parent doc, not the discussion. Where the parent genuinely cannot be split — a [[DAS Rocks|rock]] file is the case that tested this, 2026-08-06 — method 2 still fits, because the parent's own folder is already the folder method 3 would have to invent. Full rationale at `R-discussion-02`.

- **Method 1 — inline `# Discussion` H1** at the end of the parent doc. Default for any new discussion.
- **Method 2 — sibling file `{Parent} Discussions.md`** (plural). Migrate when the inline form has grown past ~1–2 screens of body content. Parent doc links to it from its dispatch table; the inline `# Discussion` H1 is removed.

Naming, migration direction, dispatch linkage, one-form-per-parent invariant, and reverse-chronological ordering all come from [[DAS stream]] — see that discipline for the canonical rules.

## Entry shape

Each dated H2 entry follows a four-section skeleton (the last is optional). This is Discussion's facet-specific entry shape (the *parallel-entry-skeleton invariant* from [[DAS stream]] § R-stream-02 requires *some* skeleton; this is the one Discussion uses):

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

H3 headings (`### The Problem`, `### Decision`, etc.) are required — they make entries skimmable and link-targetable. Body content uses the [[DAS markdown]] discipline (definition lists, wiki-links, no markdown in fenced code blocks).

## Where to attach Discussion

Any document in any anchor MAY have a Discussion attached. Common attachment points:

- Design facets — `{slug} PRD.md`, `{slug} Architecture.md`, `{slug} UX Design.md`, `{slug} API Design.md`, `{slug} Testing.md`, `{slug} Roadmap.md`. (Most common — design choices breed discussion.)
- Feature docs — `F<NNN> — Title.md` in `{slug} Features/`. Per-feature design threads.
- Architecture sub-pages — `{slug} Architecture/{Subsystem}.md`. Per-subsystem discussion.
- Long-lived spec docs — anything where decisions accumulate over time.

Documents that typically do NOT carry discussion: the anchor page (`{slug}.md`, navigation only), dispatch pages (`{slug} Design.md`), the Backlog (`{slug} Backlog.md` — discussion belongs on the feature doc the row points at), the Roadmap (`{slug} Roadmap.md` — discussion belongs on the milestone's feature doc, not on the sequencing artifact itself).

## Audit posture

Discussion is **append-only**. Entries are never edited after the Decision is filled; the document the discussion attaches to (the PRD, the Architecture, etc.) reflects the current state — the discussion is the log of how it got there. Subsequent revisits to the same question create a new entry (with its own date) referencing the prior decision.

## Relationship to other facets

| Facet | Relationship |
|---|---|
| **[[DAS PRD]] / [[DAS Architecture]] / [[DAS UX Design]] / [[DAS API Design]] / etc.** | The *spec* surfaces (anchor-scoped). Discussion attaches to any of them as a doc-scoped peer. |
| **[[DAS Decisions]]** | Anchor-level decisions log — *load-bearing* decisions that span the anchor. Discussion is finer-grained, per-document, captures the reasoning *behind* a single doc's choices. The decisions log gets the headlines; the discussion gets the deliberation. |
| **Open Questions (on feature docs)** | When an open question on a feature doc spawns extended analysis that doesn't fit in the question body, that analysis goes into the feature doc's `# Discussion` (inline) or `F<NNN> Discussions.md` (extracted). Resolving the question links to the discussion entry. |
| **[[DAS Log]]** | Sibling [[DAS stream]] facet — Log uses the same three placement methods, different entry skeleton, different attachment scope (anchor-level today, potentially doc-level later). |

## See also

- [[DAS stream]] — discipline owning placement, naming, migration, dispatch linkage.
- [[DAS file-association]] — parent umbrella discipline.
- [[DAS Decisions]] — anchor-level decisions log (different altitude).
- [[DAS Log]] — sibling stream facet.
- [[DAS Facets]] — facet catalog with the Document-scoped row.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body and ruleset above.)*

- **Don't revert to anchor-scoped wiring** — Discussion was re-scoped anchor→doc on 2026-06-11; legacy `{slug} Discussion.md` is deprecated (migration tracked in [[TINK Backlog]] § F149).
- **Placement / naming logic lives in [[DAS stream]]** (`R-stream`) — edit those rules there, not here; this spec owns only Discussion-specific rules.
