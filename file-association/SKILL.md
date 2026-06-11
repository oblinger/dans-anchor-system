---
name: file-association
description: >
  Discipline. Umbrella for the structural patterns by which content is physically
  attached to a parent document — file naming, folder structure, dispatch linkage,
  in-doc placement. Cited by doc-scoped facets that need to express *how* their
  content sits relative to its parent. Currently materializes one sub-discipline:
  [[dated-entry-stream]] (the inline / sibling-file / sibling-folder shapes for
  streams of dated typed entries). The discipline may grow to cover other
  attachment patterns (trailing-section placement for Brief, references-list
  patterns, etc.) — for now it serves as a stable name to cite while the broader
  category is still emerging.
tools: Read
user_invocable: false
---

# File Association

The discipline that names **how content is physically attached to a parent document**. Concerns: file naming (suffix conventions on sibling files), folder structure (when a stream of content earns its own folder), dispatch linkage (how the parent advertises its associated content), and in-doc placement (when content lives at the bottom of the parent vs. extracted to a sibling). NOT navigation, wiki-link semantics, or basename resolution — those are markdown / Obsidian mechanics, not authoring choices.

This file is an umbrella. Its job is to be a stable citation target while the broader category emerges; concrete rules and patterns live in the sub-disciplines below.

## Sub-disciplines

| Sub-discipline | Scope | Pattern |
|---|---|---|
| [[dated-entry-stream]] | Streams of dated, typed, reverse-chronological entries attached to a parent doc or anchor (Discussion, Log, etc.) | Three placement methods — inline H1 / sibling file / sibling folder. One-way migration as the stream grows. |

Other sub-disciplines may join as authoring patterns accumulate (candidates: *trailing-section* for static bottom-of-doc content like Brief; *references-list* for cross-link catalogs; *figure-attachment* for sourced-alongside-output diagrams). None are spec'd yet — they're listed here only to mark the boundary.

## What this discipline is NOT

- **NOT progressive-disclosure.** That discipline owns *what the reader sees first vs. later* — preface zones, altitudes, dispatch-table navigation patterns. File-association owns *where the author puts related content* on disk and how the parent points at it.
- **NOT a generic "linking" or "association" discipline.** Wiki-links, hook URIs, breadcrumbs, frontmatter `parent::` fields — those are Obsidian and markdown mechanics, not authoring choices. The vault has many association mechanisms; this discipline only covers the *structural / file-shaped* ones.
- **NOT for one-off cross-references.** A wiki-link from one doc to another is just a wiki-link. File-association is for *patterns* — repeatable shapes that multiple facets share.

## When to cite

When authoring a doc-facet (or any facet) that needs to declare *how its content sits relative to a parent*. Cite the sub-discipline that matches the pattern; sub-disciplines carry the actual rules. Example:

> Discussion is a [[dated-entry-stream]] attached to a parent doc. Methods supported: 1 (inline, default) and 2 (sibling file).

The facet doesn't re-explain the methods; it just names which it supports and which is default.

## See also

- [[dated-entry-stream]] — first materialized sub-discipline.
- [[progressive-disclosure]] — sibling discipline; what-goes-where-in-a-doc for the reader.
- [[markdown]] — sibling discipline; how the markdown text itself is written.
- [[CAB Discussion]] — current facet citing this discipline (via the sub-discipline).
- [[CAB Log]] — facet using the dated-entry-stream shape at the anchor scope.
