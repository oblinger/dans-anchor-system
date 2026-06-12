---
name: dated-entry-stream
description: >
  Discipline. The DATED specialization of [[file-association]] — streams of
  **dated, typed, reverse-chronological entries** attached to a parent doc or
  anchor (Discussion, Log). Placement (the three methods), naming, one-way
  migration, linkage, and the one-form invariant are inherited from
  [[file-association]]; this discipline adds only the dated extras: newest-first
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

**Placement is inherited from [[file-association]].** The three methods (inline H1 / sibling file / sibling folder), the cardinality→placement rule, the suffix-naming convention, one-way migration, the one-form-per-parent invariant, and parent linkage all live in the umbrella — this discipline does not re-spell them. It adds only the **dated extras** below. The *content shape* per entry (what an entry contains) lives in each citing facet's spec — Discussion specifies its own skeleton, Log a different one.

## When this discipline applies

Whenever a facet's content is a stream of the shape above. Scope-agnostic — the parent can be:

- A document (Discussion attaches to a PRD / Architecture / UX Design / etc.)
- An anchor (anchor-level Log attaches to the anchor's Track folder)
- Both, in some facets — Log may exist at both scopes; Discussion is doc-only.

Each facet declares which scopes it supports.

## Placement (inherited)

Uses [[file-association]]'s three methods — inline H1 (1) / sibling file (2) / sibling folder (3) — chosen by the cardinality→placement rule, migrated one-way `1 → 2 → 3`, one-form-per-parent, linked from the parent's dispatch table. See the umbrella for all of that; it is **not** re-spelled here.

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

> Discussion is a [[dated-entry-stream]] attached to a parent doc. Methods supported: 1 (inline, default) and 2 (sibling file). Method 3 (sibling folder) is out of scope — Discussion entries are rarely large enough to deserve their own files.

The facet does NOT re-explain the three methods. The discipline is canonical for that.

## See also

- [[file-association]] — parent umbrella discipline.
- [[CAB Discussion]] — first citing facet (doc-scoped, methods 1 + 2).
- [[CAB Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[CAB Stories]] — sibling pattern (inline-bullet → folder-form) — same migration direction but not a dated stream; its inline form is bullets, not a dated H1 section. The pattern is related but Stories is not a dated-entry-stream.
- [[markdown]] — markdown authoring discipline (cited alongside this one for entry body conventions).


# RULESET R-dated-entry-stream
include::
description:: Rules for streams of dated, typed, reverse-chronological entries attached to a parent — three placement methods, naming convention, migration direction, parallel-entry invariant.

Embedded rule set for the dated-entry-stream sub-discipline, co-located with the discipline spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Cited by every facet whose content is a dated-entry stream. Catalog stub at [[R-dated-entry-stream]] under [[R-doc]].

### RULE R-dated-entry-stream-01 — Three named placement methods (stated)

The discipline defines exactly three placement methods: inline `# {Facet}` H1 (method 1), sibling file `{Parent} {Facet}s.md` (method 2), sibling folder `{Parent} {Facet}s/` (method 3). Citing facets pick a subset and declare a default; no fourth method is introduced ad hoc.

**Check pattern:** for each facet citing this discipline, assert its method declaration is a subset of {1, 2, 3} with a named default.

**Why:** a bounded method set is the whole point — readers (and the agent) learn three shapes and recognize them everywhere. Ad-hoc methods erode the discipline.

### RULE R-dated-entry-stream-02 — Naming convention is parent + plural facet (checked)

When extracted (methods 2 or 3): the file or folder name is `{Parent Doc/Anchor Name} {Facet}s.md` (or `/`). The facet suffix is plural; the parent's exact name comes first. Method 3's inner anchor file matches the folder name; entry files inside use ISO date prefix (`YYYY-MM-DD — <Title>.md`).

**Check pattern:** for each extracted instance, regex-match against `{Parent}\s+\w+s\.md` for method 2 and the folder + anchor-file + dated-entries shape for method 3.

**Why:** the plural signals the extracted form; the parent prefix preserves the link to what the stream is *about*. Without the convention, navigation requires open-and-skim instead of name-recognition.

### RULE R-dated-entry-stream-03 — Migration is one-way (stated)

Streams migrate `1 → 2 → 3` as they grow. Reverse migration (3 → 2, 2 → 1, or 3 → 1) is allowed only as a deliberate refactor with explicit user ack; the agent does not automatically downgrade.

**Check pattern:** stated for now; future tooling could flag reverse migrations in git history without a corresponding ack note.

**Why:** downgrading loses git-blame granularity (per-entry history, per-entry edit visibility). The cost is paid once on extraction; reversing pays it again without benefit.

### RULE R-dated-entry-stream-04 — One form per parent at a time (checked)

A given parent has at most one materialized form of a given stream: inline H1 XOR sibling file XOR sibling folder. Mixed coexistence is forbidden.

**Check pattern:** for each parent doc / anchor, count materialized forms of each facet's stream; assert ≤ 1 form per (parent, facet) pair.

**Why:** mixed forms drift — new entries land in the wrong place, readers don't know which is current, the navigation breaks.

### RULE R-dated-entry-stream-05 — Reverse chronological, newest first (checked)

Entries are ordered newest-first by date. New entries prepend; they never append.

**Check pattern:** parse entry headings (date in `## YYYY-MM-DD — Title` for methods 1/2, or filename `YYYY-MM-DD — Title.md` for method 3); assert dates are non-increasing in document/folder-listing order.

**Why:** a reader's first encounter is "what's the latest thinking / latest event?" — newest-first puts the answer first.

### RULE R-dated-entry-stream-06 — Parallel entry skeleton declared by the citing facet (sampled)

Every entry within one facet's stream follows the same H3 sub-structure. The skeleton is declared by the citing facet (Discussion → Problem / Options Considered / Decision; Log → its own shape). The discipline mandates uniformity; the facet defines the shape.

**Check pattern:** sample entries within one facet's stream; assert the same H3 set appears in the same order; flag entries missing a required H3.

**Why:** uniform skeletons make the stream scannable. Reading a third entry should not be a fresh navigation problem.

### RULE R-dated-entry-stream-07 — Dispatch linkage from parent when extracted (checked)

When a stream is extracted to method 2 or 3, the parent doc links to it from its dispatch table (or `## See also` near the top of the parent). The inline `# {Facet}` H1 is removed from the parent simultaneously.

**Check pattern:** for each extracted instance `{Parent} {Facet}s.md` (or `/`), grep `{Parent}.md` for a wiki-link to it AND assert no `# {Facet}` H1 remains in the parent.

**Why:** the link is what makes the extracted stream discoverable from the parent; the simultaneous H1 removal is the one-form-per-parent invariant in action.

### RULE R-dated-entry-stream-08 — Method 3 folder shape (checked)

When method 3 is used: the folder `{Parent} {Facet}s/` contains an anchor file `{Parent} {Facet}s.md` (H1 matches filename) with a dispatch table of all entries, PLUS one file per entry named `YYYY-MM-DD — <Title>.md` with H1 matching the title (date in filename only). The folder may also contain `.anchor` per anchor-folder convention.

**Check pattern:** for each method-3 folder, assert the anchor file exists; assert entry files match the date-prefixed naming; assert dispatch in anchor file lists every entry file.

**Why:** the folder form is only useful if its structure is predictable; ad-hoc folders defeat the per-entry-file rationale.

### RULE R-dated-entry-stream-09 — Citing facet declares supported methods + default (stated)

Every facet citing this discipline declares: (a) the subset of methods it supports, (b) which is default, (c) any out-of-scope methods with rationale.

**Check pattern:** for each facet's spec, assert a citation paragraph naming the discipline + supported-methods set + default. Audit fails when the citation is missing or the method set is undeclared.

**Why:** without the declaration the reader doesn't know whether a 3-form choice exists for that facet, the agent doesn't know what to scaffold, and the audit can't validate against the right method set.
