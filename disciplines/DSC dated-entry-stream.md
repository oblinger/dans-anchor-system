---
name: dated-entry-stream
description: >
  Discipline. The DATED specialization of [[DSC file-association]] — streams of
  **dated, typed, reverse-chronological entries** attached to a parent doc or
  anchor (Discussion, Log). Placement (the three methods), naming, one-way
  migration, linkage, and the one-form invariant are inherited from
  [[DSC file-association]]; this discipline adds only the dated extras: newest-first
  ordering, prepend semantics, ISO-date entry-file naming, and the
  parallel-entry-skeleton invariant. Cited by every facet whose content is a
  dated stream; the facet declares which methods it supports and which is default.
tools: Read
user_invocable: false
---

# Dated Entry Stream

A *dated entry stream* is content of the form:

- **Dated** — every entry's heading carries a date (`YYYY-MM-DD`).
- **Typed** — every entry follows a parallel skeleton appropriate to its facet (Discussion entries have Problem / Options / Decision; Log entries have a different shape; the skeleton is per-facet but uniform *within* a facet).
- **Reverse-chronological** — newest entry first.
- **Attached to a parent** — the stream lives "about" a specific document (or, for anchor-scoped facets, a specific anchor) — the thing being discussed, the thing being logged.
- **Append-style** — new entries prepend; old entries are not edited after their decision/outcome is recorded.

**Placement is inherited from [[DSC file-association]].** The three methods (inline H1 / sibling file / sibling folder), the cardinality→placement rule, the suffix-naming convention, one-way migration, the one-form-per-parent invariant, and parent linkage all live in the umbrella — this discipline does not re-spell them. It adds only the **dated extras** below. The *content shape* per entry (what an entry contains) lives in each citing facet's spec — Discussion specifies its own skeleton, Log a different one.

## When this discipline applies

Whenever a facet's content is a stream of the shape above. Scope-agnostic — the parent can be:

- A document (Discussion attaches to a PRD / Architecture / UX Design / etc.)
- An anchor (anchor-level Log attaches to the anchor's Track folder)
- Both, in some facets — Log may exist at both scopes; Discussion is doc-only.

Each facet declares which scopes it supports.

## Placement (inherited)

Uses [[DSC file-association]]'s three methods — inline H1 (1) / sibling file (2) / sibling folder (3) — chosen by the cardinality→placement rule, migrated one-way `1 → 2 → 3`, one-form-per-parent, linked from the parent's dispatch table. See the umbrella for all of that; it is **not** re-spelled here.

**Dated default:** a dated stream's inline form (method 1) is a `# {Facet}` H1 holding **dated H2 sub-entries** (newest first). When extracted, the plural suffix applies (`Discussions`, `Logs`).

## Dated extras (what this specialization adds)

- **Dated entry-file naming (method 3).** Each per-entry file uses an ISO date prefix + em-dash + title: `2026-06-11 — <Title>.md`. The H1 inside matches the title *without* the date prefix (clean H1s; the date lives in the filename for sort order). *(This is the dated specialization of file-association's "per-item naming"; non-dated collections name by title alone.)*
- **Reverse-chronological, prepend.** Entries are ordered newest-first; new entries **prepend**, never append. (See R-dated-entry-stream-05.)
- **Append-style immutability.** Old entries are not edited after their decision/outcome is recorded — the stream is a ledger.

## Parallel entry skeleton

Within one facet's stream, every entry follows the same H3 sub-structure. Discussion's skeleton is Problem / Options Considered / Decision / (optionally Why This Works). Log's skeleton is per its facet spec. The discipline doesn't dictate which skeleton — it dictates that the *facet* declare one, and that every entry conform.

This invariant is what makes the stream scannable. Readers can predict where to look for "what was decided" or "what failed" within any entry; un-uniform entries force re-reading every time.

## Citing facets declare their methods

Each facet citing this discipline declares:
1. Which methods it supports (a subset of 1, 2, 3).
2. Which is default.
3. Any facet-specific edge cases (e.g., "method 3 is overkill for Discussion since entries rarely warrant their own files").

Example citation in a facet spec:

> Discussion is a [[DSC dated-entry-stream]] attached to a parent doc. Methods supported: 1 (inline, default) and 2 (sibling file). Method 3 (sibling folder) is out of scope — Discussion entries are rarely large enough to deserve their own files.

The facet does NOT re-explain the three methods. The discipline is canonical for that.

## See also

- [[DSC file-association]] — parent umbrella discipline.
- [[CAB Discussion]] — first citing facet (doc-scoped, methods 1 + 2).
- [[FCT Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[FCT Stories]] — sibling pattern (inline-bullet → folder-form) — same migration direction but not a dated stream; its inline form is bullets, not a dated H1 section. The pattern is related but Stories is not a dated-entry-stream.
- [[DSC markdown]] — markdown authoring discipline (cited alongside this one for entry body conventions).


# RULESET R-dated-entry-stream

include:: [[DSC file-association#RULESET R-file-association|R-file-association]]
description:: Rules ADDED by the dated specialization on top of [[R-file-association]] — newest-first ordering + prepend immutability, the parallel-entry-skeleton invariant, and ISO-date entry-file naming.

Embedded rule set for the dated-entry-stream specialization, co-located with the spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. The **general** association rules (three methods, cardinality→placement, naming, migration, one-form, linkage, folder shape, method declaration) live in [[R-file-association]] and are inherited via the `include::` above (promoted there per F154); only the **dated extras** are stated here. Catalog stub at [[R-dated-entry-stream]] under [[R-doc]].

### RULE R-dated-entry-stream-01 — Reverse chronological, newest-first, prepend-immutable (checked)

Entries are ordered newest-first by date; new entries **prepend**, never append; recorded entries are not edited after their decision/outcome lands (the stream is a ledger).

**Check pattern:** parse entry headings (date in `## YYYY-MM-DD — Title` for methods 1/2, or filename `YYYY-MM-DD — Title.md` for method 3); assert dates are non-increasing in document / folder-listing order.

**Why:** a reader's first encounter is "what's the latest thinking / latest event?" — newest-first puts the answer first; prepend-immutability preserves the audit trail.

### RULE R-dated-entry-stream-02 — Parallel entry skeleton declared by the citing facet (sampled)

Every entry within one facet's stream follows the same H3 sub-structure. The skeleton is declared by the citing facet (Discussion → Problem / Options Considered / Decision; Log → its own shape). The discipline mandates uniformity; the facet defines the shape.

**Check pattern:** sample entries within one facet's stream; assert the same H3 set appears in the same order; flag entries missing a required H3.

**Why:** uniform skeletons make the stream scannable. Reading a third entry should not be a fresh navigation problem.

### RULE R-dated-entry-stream-03 — Dated entry-file naming (method 3) (checked)

When method 3 is used for a dated stream, each per-entry file uses an ISO date prefix + em-dash + title: `YYYY-MM-DD — <Title>.md`. The H1 inside matches the title *without* the date (clean H1s; the date lives in the filename for sort order). This is the dated specialization of file-association's general sibling-folder shape ([[R-file-association]]-07).

**Check pattern:** for each method-3 dated stream, assert every entry file matches `^\d{4}-\d{2}-\d{2} — .+\.md$` and its H1 omits the date prefix.

**Why:** the ISO prefix gives correct chronological sort in any file listing while keeping the visible H1 clean.
