---
name: stream
description: "*Kind* — dated-entry stream (); one file per decision"
tools: Read
user_invocable: false
group: slot
---

# Stream

A **stream** is an expansion space you can attach to anything — a place where material always has a defined home, kept in order automatically, growing from a section to a file to a folder as it earns the room.

**That is what the facet is for, and it is worth stating before the mechanics.** Without a stream, content with no obvious home gets jammed wherever there is space, and a knowledge base loses its shape one improvisation at a time. A stream removes the improvisation: there is never a moment when the answer to *"where does this note go?"* is *"nowhere yet."* Datedness and reverse-chronological ordering are how it stays legible at volume; the relief-valve property is why it matters.

**Say it either way.** *"Log is a stream."* *"Discussion is a streaming facet."* The noun and the adjective both work, which is most of why this is the name that carries the vocabulary — [[DAS file-association]] underneath is machinery, cited by link and never spoken.

A stream is content of the form:

- **Dated** — every entry's heading carries a date (`YYYY-MM-DD`).
- **Typed** — every entry follows a parallel skeleton appropriate to its facet (Discussion entries have Problem / Options / Decision; Log entries have a different shape; the skeleton is per-facet but uniform *within* a facet).
- **Reverse-chronological** — newest entry first.
- **Attached to a parent** — the stream lives "about" a specific document (or, for anchor-scoped facets, a specific anchor) — the thing being discussed, the thing being logged.
- **Append-style** — new entries prepend; old entries are not edited after their decision/outcome is recorded.

**Placement is inherited from [[DAS file-association]].** The three methods (inline H1 / sibling file / sibling folder), the cardinality→placement rule, the suffix-naming convention, one-way migration, the one-form-per-parent invariant, and parent linkage all live in the umbrella — this discipline does not re-spell them. It adds only the **dated extras** below. The *content shape* per entry (what an entry contains) lives in each citing facet's spec — Discussion specifies its own skeleton, Log a different one.

## When this discipline applies

Whenever a facet's content is a stream of the shape above. Scope-agnostic — the parent can be:

- A document (Discussion attaches to a PRD / Architecture / UX Design / etc.)
- An anchor (anchor-level Log attaches to the anchor's Track folder)
- Both, in some facets — Log may exist at both scopes; Discussion is doc-only.

Each facet declares which scopes it supports.

**A stream is permitted on any document; only a citing facet may narrow that.** The discipline states no exclusion of its own — its selector is a content sentinel, so it already reaches whatever document carries dated entries, and adding a document-class exclusion here would fail documents that are correct. [[DAS Discussion]] narrows it and is the only facet that does: a Discussion does not attach to navigation or sequencing artifacts (anchor page, dispatch page, Backlog, Roadmap), because a discussion belongs on the thing being decided, not on the index to it. That exclusion is Discussion's, not the discipline's — a Log-shaped or history-shaped stream on an anchor page or a facet dispatch page is ordinary and correct. Measured across the corpus 2026-08-08: **zero** Backlogs, Roadmaps or dispatch pages carry a Discussion, so Discussion's exclusion holds in fact; **five** navigation-role documents carry a non-Discussion dated stream, which hoisting the exclusion up to this discipline would have converted into five false findings.

## Placement (inherited)

Uses [[DAS file-association]]'s three methods — inline H1 (1) / sibling file (2) / sibling folder (3) — chosen by the cardinality→placement rule, migrated one-way `1 → 2 → 3`, one-form-per-parent, linked from the parent's dispatch table. See the umbrella for all of that; it is **not** re-spelled here.

**Dated default:** a dated stream's inline form (method 1) is a `# {Facet}` H1 holding **dated H2 sub-entries** (newest first). When extracted, the plural suffix applies (`Discussions`, `Logs`).

## Dated extras (what this specialization adds)

- **Dated entry-file naming (method 3).** Each per-entry file leads with an ISO date prefix, then a separator, then the title. The **date prefix is the invariant**; the separator is not. Both `2026-06-11 — <Title>.md` (em-dash, recommended for new streams) and `2026-06-11 <Title>.md` (plain space, what the corpus actually uses — 126 files to 0, measured 2026-08-08) are admitted. Under the em-dash form the H1 omits the date; where a citing facet specifies its own top-of-doc header, that facet's rule governs. *(This is the dated specialization of file-association's "per-item naming"; non-dated collections name by title alone.)* (See R-stream-03.)
- **Reverse-chronological, prepend.** Entries are ordered newest-first; new entries **prepend**, never append. (See R-stream-01.)
- **Append-style immutability.** Old entries are not edited after their decision/outcome is recorded — the stream is a ledger.

## Parallel entry skeleton

Within one facet's stream, every entry follows the same H3 sub-structure. Discussion's skeleton is Problem / Options Considered / Decision / (optionally Why This Works). Log's skeleton is per its facet spec. The discipline doesn't dictate which skeleton — it dictates that the *facet* declare one, and that every entry conform.

This invariant is what makes the stream scannable. Readers can predict where to look for "what was decided" or "what failed" within any entry; un-uniform entries force re-reading every time.

**The discipline declares no default skeleton, and the corpus is why.** The obvious alternative — Stream ships one skeleton that facets override — was measured against the six citing facets 2026-08-08 and does not survive: their entries are not variations on a shape, they are different kinds of object. One mandates four H3s; one specifies a wholly different entry shape for dated *files*; one's entry is a blockquoted message whose status tag is the payload; two are entire files fronted by a `# {date} {name}` H1 and have no H3 structure to default; one specifies a section order instead. A default would be inherited by one facet and overridden by five, which is not a default — it is one facet's shape promoted above its peers and then contradicted everywhere. `R-stream-02` therefore requires *that* a skeleton exist and be uniform within a facet, and says nothing about which.

## Citing facets declare their methods

Each facet citing this discipline declares:
1. Which methods it supports (a subset of 1, 2, 3).
2. Which is default.
3. Any facet-specific edge cases (e.g., "method 3 is overkill for Discussion since entries rarely warrant their own files").

Example citation in a facet spec:

> Discussion is a [[DAS stream]] attached to a parent doc. Methods supported: 1 (inline, default) and 2 (sibling file). Method 3 (sibling folder) is out of scope — Discussion entries are rarely large enough to deserve their own files.

The facet does NOT re-explain the three methods. The discipline is canonical for that.

## See also

- [[DAS file-association]] — parent umbrella discipline.
- [[DAS Discussion]] — first citing facet (doc-scoped, methods 1 + 2).
- [[DAS Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[DAS Stories]] — sibling pattern (inline-bullet → folder-form) — same migration direction but not a dated stream; its inline form is bullets, not a dated H1 section. The pattern is related but Stories is not a stream.
- [[DAS markdown]] — markdown authoring discipline (cited alongside this one for entry body conventions).

The companion ruleset lives at [[R-stream]].
