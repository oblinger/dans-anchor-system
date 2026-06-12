---
description: Default rules for surveying people — ships with the skill. User overrides in SRC rules/.
---
# survey-person — default rules

Default rules for `survey` on noun-type **person**. Ships with the skill; user overrides in `[[SRC rules/survey-person|SRC rules/]]`.

Applies when comparing multiple individuals — candidates for a role, researchers in a domain, founders in a sector, speakers at a conference.

## Default dimensions (table columns)

Standard survey-of-people columns:

- **Name** (first column, with link to primary source)
- **Current role + org**
- **Location / region**
- **Relevant expertise** (one phrase)
- **Key public work** (1-2 most-cited / most-viewed)
- **Years in domain**
- **Notable affiliations**

## Default sources for the population

- LinkedIn search (work-history filter)
- Domain-specific registries (e.g., scholar for academics, GitHub for engineers)
- Conference speaker lists
- "Who's who in X" articles + their citations
- Curated lists if available (e.g., AI100, Forbes 40-under-40)

## Default disambiguation

When several candidates share a name in your population, disambiguate per [[find-person]] tiebreakers (current org + role, location, time period, topical area).

## Privacy

**Survey-of-people is public-figures and public-roles ONLY by default.** A "survey of private individuals" is almost always a misuse — push back before running. If the user confirms a legitimate use (academic study, talent-mapping for an open job listing), still confine to publicly-self-published data.

## Sub-types and column variations

- **Researcher survey** — add h-index + most-cited paper.
- **Candidate survey** — add current-org tenure (years), prior role count, public portfolio link.
- **Speaker survey** — add talks given, conferences, topic focus.
- **Founder survey** — add current venture, prior exits.

## Gotchas

- Name collisions; pin organization to disambiguate.
- LinkedIn-only data is soft; cross-check controlled sources where possible.
- Lurking gender / nationality / age proxies in selection criteria — surface them; don't let them ride invisibly.

## User rules

(Empty — user adds in `SRC rules/survey-person.md` to override these defaults.)
