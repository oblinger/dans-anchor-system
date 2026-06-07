---
description: Default rules for finding a person — ships with the skill. User overrides in SRC rules/.
---
# find-person — default rules

Default rules for `find` on noun-type **person**. Ships with the skill; user overrides in `[[SRC rules/find-person|SRC rules/]]`.

When finding a person, the goal is identifying a *specific* individual matching criteria — not building a profile (that's [[describe/SKILL|describe]]).

## Default sources for identification (authority order)

1. The person's own site / handle they control (GitHub, scholar, personal) — primary for confirming identity.
2. LinkedIn — work history; first place to look for org + role match.
3. GitHub / scholar / professional registries — domain-specific authority.
4. Wikipedia — only for notable subjects.
5. News mentions for recent role-change announcements.

## Default disambiguation tiebreakers

Common names are the default failure mode. Try in order:

1. **Current org + role** (most useful — "John Smith at Acme as VP Engineering").
2. **Location** (city, region).
3. **Time period** (active years, especially for historical).
4. **Topical area** (subject of recent publications/talks).
5. **A specific known fact** the user provided.

If top two candidates can't be separated on these → return both with the disambiguating attribute each is missing.

## Default verification

Before returning a confidence-high identifier, cross-check against at least one source the person controls (their own site, GitHub, scholar profile) — not LinkedIn alone.

## Default output (the saved lookup)

- Canonical name + handle/URL
- Current role + org
- 1-line context (what they're known for)
- Confidence + disambiguation note
- Sources (full URLs)
- Alternate candidates (if confidence is medium or lower)

## Privacy

- **Public figures**: standard sources fine.
- **Private individuals**: push back before any compilation that crosses PII-aggregation territory. Never include home address, phone, family, even if requested.
- Never breach data, scraped private data, dark web.

## Gotchas

- LinkedIn dates soft; verify dated facts with a controlled source.
- Name-collision rate high in tech.
- Recent role changes lag on LinkedIn; check Twitter/news.

## User rules

(Empty — user adds in `SRC rules/find-person.md` to override these defaults.)
