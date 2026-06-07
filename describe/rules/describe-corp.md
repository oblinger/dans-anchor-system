---
description: Default rules for describing an organization — ships with the skill. User overrides in SRC rules/.
---
# describe-corp — default rules

Default rules for `describe` on noun-type **corp**. Ships with the skill; user overrides in `[[SRC rules/describe-corp|SRC rules/]]`.

## Default dimensions

| Dimension | Notes |
|---|---|
| Canonical legal name + DBAs | Holdings vs operating entity; parent vs subsidiary |
| Founding year + founders | And any major re-foundings / mergers |
| HQ + key locations | City, country; remote-first? |
| Sector / category | Industry + sub-segment |
| Product / service | One-line + 1-2 sentence description |
| Stage / funding | Seed → growth → public; total raised; last round + lead |
| Size | Headcount range, revenue (estimate if private, exact if public) |
| Leadership | CEO, founders still active, exec team |
| Customers | Notable named customers, scale |
| Competitors | 3-5 most-named alternatives |
| Recent material events | Funding, M&A, exec change, product launch, regulatory (last ~12 months) |
| Public profile | Site, careers, regulatory filings if public, news rotation |

## Default sources (authority order)

1. The company's own site (`/about`, `/team`, careers, blog) — primary for self-framing.
2. Crunchbase / PitchBook — funding, headcount, leadership for private companies.
3. SEC EDGAR / equivalent regulator — public companies, primary for financials and material events.
4. Wikipedia — vetted but lags real-time.
5. News (TechCrunch / Bloomberg / industry trade press) — recent material events.
6. LinkedIn (company page + employee count) — soft headcount, growth velocity proxy.
7. G2 / Capterra / Gartner — for B2B; positioning, competitors.
8. Glassdoor / Levels.fyi — culture, compensation, internal context.

## Default output shape

- **Identity card** — legal name, DBAs, founding year, HQ, sector.
- **Product / service** — what they sell / do.
- **Stage / funding** — public/private; key numbers.
- **Size** — headcount + revenue ranges (or point if public).
- **Leadership** — CEO, founders, notable execs.
- **Market** — customers (named where notable), competitors, position.
- **Recent material events** — last ~12 months.
- **Risks / notes** — anything material.
- **Sources** — full URLs.

## Public vs private

- **Public**: SEC filings (10-K, 10-Q, 8-K) are ground truth. Most other sources are downstream.
- **Private**: triangulate Crunchbase / PitchBook / news / employee proxies. Numbers are softer; note ranges, not point values.
- **Nonprofits**: 990 filings (US) are the public analog.

## Default disambiguation

- **Brand vs legal entity** — default to brand; flag if legal matters (M&A, contracts).
- **Holding vs subsidiary** — default to operating brand unless corporate-structure work.
- **Same name different sectors** — pin sector + locale.
- **Past names** — track aliases.

## Sub-type variants

Startup (stage, cap-table-relevant, growth velocity) · public company (SEC-driven, analyst coverage) · nonprofit (990-driven, mission-driven) · government / agency.

## Gotchas

- LinkedIn headcount is soft; triangulate.
- Funding totals double-count debt/SAFEs sometimes.
- "Number of customers" on company sites is usually marketing inflation.
- Conglomerates: the org may be a brand 3 levels deep in a holding structure.

## User rules

(Empty — user adds in `SRC rules/describe-corp.md` to override these defaults.)
