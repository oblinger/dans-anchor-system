---
description: Default rules for the find skill, applied across all noun types. Ships with the skill. User overrides in SRC rules/.
---
# find — default rules

Default verb-level rules for `find`. Ships with the skill; user overrides in `[[SRC rules/find|SRC rules/find.md]]`.

Pair files (`find-person.md`, `find-corp.md`, `find-product.md`) carry noun-specific defaults and augment these.

## Default behavior

- **Disambiguate** when candidates score close — return ranked alternatives or ask, rather than picking one.
- **Verify** the top match against a second independent source before returning high confidence.
- **Surface ambiguity** in the saved lookup — flag it, don't hide it behind a confident-sounding summary.
- **Never invent** an identifier when the search came up empty — return "not found" with what was searched.

## Default depth tiers

| Tier | Sources | Verification | When |
|---|---|---|---|
| **Quick** | 1 | minimal | obvious matches you just need confirmed |
| **Standard** | 2-3 | brief cross-check | default |
| **Deep** | broad | full verification chain | due diligence, will-act-on-it cases |

## Default output (the saved Find file)

- Identifier (the thing found)
- Canonical URL
- 1-line context
- Confidence (high / medium / low)
- Sources consulted (numbered, full URLs)
- Any ambiguity or alternate candidates

## User rules

(Empty — user adds in `SRC rules/find.md` to override these defaults.)
