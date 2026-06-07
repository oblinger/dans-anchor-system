---
description: Default rules for the survey skill, applied across all noun types. Ships with the skill. User overrides in SRC rules/.
---
# survey — default rules

Default verb-level rules for `survey`. Ships with the skill; user overrides in `[[SRC rules/survey|SRC rules/survey.md]]`.

Pair files (`survey-person.md`, `survey-corp.md`, `survey-product.md`, `survey-skill.md`, …) carry noun-specific defaults and augment these.

## Default output shape — RRR convention

Every survey follows the **Research-Report Convention** (migrated from legacy `/research survey`):

1. **Results table at the top** — at-a-glance comparable facts. First column is the entity name as a markdown link to its primary URL (no separate "Name" + "URL" columns). Entries ranked by value to the user, with a blank separator row between top-tier and the rest.
2. **Body** — overview, analysis, recommendations (only when asked).
3. **Sources** section at the end with full URLs.

## Default depth tiers

| Tier | Population | Dimensions | When |
|---|---|---|---|
| **Quick** | top 5-10 | 3 most-important | orientation |
| **Standard** | full population (within bound) | 5-7 | default |
| **Deep** | full population | 10+, multi-source per cell, footnotes | thorough comparison |

## Default behavior

- **Define the population** — state the inclusion bound; don't quietly truncate.
- **Pick dimensions deliberately** — from the pair file or via meta-survey; don't invent in a vacuum.
- **Source-attribute each cell**.
- **Normalize** — units, dates, naming; note where normalization is lossy.
- **Surface gaps + outliers** — missing cells, surprising values, entities that don't fit.
- **Include interpretive notes** — value is in the comparison, not the rows alone.

## Meta-survey (sub-pattern)

Use when the population is novel or the right dimensions aren't obvious:

1. Survey **how others have surveyed this kind of thing** — ranking pages, "best X for Y" articles, academic taxonomies, comparison sites.
2. Extract the dimension union/intersection across those surveys.
3. Pick dimensions from that union, weighted by frequency of appearance.
4. Proceed with normal survey from step 3 above.

## Specialized variant — skill survey

When the survey population is **agent skills that do similar work** ("survey architect skills"), full default rules live at [[survey/rules/survey-skill|survey-skill.md]]. Pre-baked search loci (anthropic-skills, GitHub `filename:SKILL.md`), pre-baked columns, mandatory choice-point + approach-group analysis sections — see that file.

Trigger phrases: *"survey skills that do X"*, *"compare skills for Y"*, *"is anyone doing a good Z skill"*.

## Default output file

The survey in [[Survey]] (`~/ob/kmr/Topic/Search/Survey/`):

- Title: `# <Survey topic> Survey`
- Results table at top (per RRR convention)
- Scope note immediately after the table (population, bound, dimensions, generation date)
- Body: overview → analysis → (recommendation if asked)
- Sources at end with full URLs

## User rules

(Empty — user adds in `SRC rules/survey.md` to override these defaults.)
