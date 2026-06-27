---
description: Glossary — dated folders, dated sections, vocabulary used across CAB
---
# CAB Defined Terms

Glossary of cross-cutting vocabulary used throughout the CAB spec — shared terms that don't belong to any single facet, rule, or trait.

- **DATED FOLDER** — A folder where all files and subfolders within it are prefixed with the date format (`YYYY-MM-DD`). Items sort in chronological order when viewed alphabetically.

- **DATED SECTIONS** — A file composed of H2 sections whose titles begin with a date prefix (`## YYYY-MM-DD — Title`), listed in reverse chronological order (newest first). Used for notes, features, todo, and log files.

- **ANCHOR-ROOT** — An anchor whose folder is not contained inside another anchor's folder tree. Anchor-roots are top-level entry points to the kmr anchor graph; every other anchor is reachable by walking *down* from some anchor-root via folder nesting. The authoritative list lives at `~/ob/kmr/Roots/Roots.md` § Anchor-roots. Per [[F057 — Anchor-root concept and scan_tid migration]]: `scan_tid.py tree` reads this list at runtime and verifies each name against `ha --dump` (structural check: `.anchor` marker present + not nested under another listed root). Related: [[_]], [[SLUG]], [[CAB]].

# BRIEF

- **This page is a flat glossary of cross-cutting CAB vocabulary** — terms that show up in multiple facet specs, rules, or skill runbooks and need one canonical definition. Each entry is a bullet with a bolded ALL-CAPS term head, an em-dash, and a self-contained definition.
- **Inclusion test**: a term belongs here only if it is (a) used in more than one CAB doc, AND (b) too small to deserve its own page. Single-facet vocabulary stays in that facet's spec; anything large enough to grow sub-sections gets promoted to a standalone `CAB <Term>.md` and removed from this list.
- **NOT for**: facet-specific shape rules (those live in `CAB <Facet>.md`), trait-wide rules (`CAB <Trait>.md`), markdown-rendering rules ([[R-markdown]]), or anchor-local conventions (`{NAME} Rules.md`). Do not pile general CAB explanation, examples, or design rationale here — keep entries terse.
- **Entry shape is load-bearing**: `- **TERM** — definition.` with the term in ALL CAPS bold. The ALL-CAPS form lets other docs reference the term unambiguously in prose without needing wiki-links. Preserve this exact format when adding entries.
- **Ordering**: entries are listed in the order they were added (not alphabetized) so that older, more foundational terms come first. Append new terms to the end; do not re-sort.
- **Cross-link sparingly**: include `Related: [[X]], [[Y]]` at the end of an entry only when the related page is essential context. Avoid turning entries into mini-dispatch-tables — that is what `CAB Base.md` is for.
