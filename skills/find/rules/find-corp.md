---
description: Default rules for finding an organization — ships with the skill. User overrides in SRC rules/.
---
# find-corp — default rules

Default rules for `find` on noun-type **corp**. Ships with the skill; user overrides in `[[SRC rules/find-corp|SRC rules/]]`.

Goal: identify the *specific* organization matching criteria — not profile it (that's [[profile/SKILL|/profile]]).

## Default sources for identification

1. The company's own site — primary for confirming brand identity.
2. Crunchbase (private) / SEC EDGAR (public) — canonical entity records.
3. Wikipedia — vetted for notable orgs.
4. LinkedIn company page — confirms recent existence + brand-to-employees match.
5. News mentions for recent material events.

## Default disambiguation

- **Brand vs legal entity** — default to the brand for everyday questions (Google vs Alphabet); flag if legal entity matters (M&A, contracts, litigation).
- **Holding vs subsidiary** — same-name collisions; default to the operating brand.
- **Same name, different sectors** — pin sector + locale.
- **Past names** — companies rebrand; track aliases.

## Default verification

Cross-check the identified org against the company's own site (canonical brand) AND a third-party source (Crunchbase / Wikipedia / SEC) before returning high confidence.

## Default output (the saved lookup)

- Canonical name (brand + legal entity if different)
- 1-line description (what they do)
- Stage / public-or-private status
- HQ
- Canonical URL (company site)
- For public companies: ticker + exchange
- Confidence + disambiguation note
- Sources (full URLs)

## Gotchas

- Brand may be 3 levels deep in a holding structure.
- LinkedIn employee count is soft; don't rely on it for "is this still active?"
- Acquired / merged companies may have a 3+ year gap between rebrand and Wikipedia catching up.

## User rules

(Empty — user adds in `SRC rules/find-corp.md` to override these defaults.)
