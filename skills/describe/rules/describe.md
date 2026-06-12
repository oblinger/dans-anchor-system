---
description: Default rules for the describe skill, applied across all noun types. Ships with the skill. User overrides in SRC rules/. Includes the RRR report-shape from the legacy /research family.
---
# describe — default rules

Default verb-level rules for `describe`. Ships with the skill; user overrides in `[[SRC rules/describe|SRC rules/describe.md]]`.

Pair files (`describe-person.md`, `describe-corp.md`, `describe-product.md`, `describe-book.md`, …) carry noun-specific defaults and augment these.

## Default output shape — RRR convention

Every profile follows the **Research-Report Convention** (migrated from legacy `/research`):

1. **Results table at the top** — at-a-glance comparable facts. First column is the entity name as a markdown link to its primary source URL — no separate "Name" + "URL" columns.
2. **Prose body** — overview, analysis, recommendation (only when applicable).
3. **Sources** section at the end with **full URLs** (so links work outside Obsidian).

Entries inside the report (when listing related entities) are ranked by value to the user; use a blank separator row between top-tier and the rest.

## Default depth tiers

| Tier | Output | When |
|---|---|---|
| **Quick** | Summary card (3-5 facts, single best source) | lightweight context for a conversation |
| **Standard** | Full profile (10-15 facts, 2-3 sources, contradictions flagged) | default |
| **Deep ("Dig")** | Full dossier (all dimensions, all major sources cross-referenced, source-per-fact, explicit gaps, related entities) | due diligence, will-act-on-it cases |

## Default behavior

- **Confirm the entity** is unambiguous before describing; invoke `find` first if needed.
- **Source-attribute every fact** inline or in footnotes.
- **Surface contradictions** explicitly — never harmonize them into a smooth narrative.
- **Name gaps** explicitly — never fill them with inference dressed as fact.

## Default output file

The profile in [[Profile]] (`~/ob/kmr/Topic/Search/Profile/`):

- Title: `# <Entity Name> — <tier>`
- Results table at top (per RRR convention)
- Body sections by noun-dimension (per the pair file)
- Contradictions surfaced inline
- Gaps named explicitly
- Sources with full URLs at end

## User rules

(Empty — user adds in `SRC rules/describe.md` to override these defaults.)
