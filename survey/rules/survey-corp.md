---
description: Default rules for surveying organizations — ships with the skill. User overrides in SRC rules/.
---
# survey-corp — default rules

Default rules for `survey` on noun-type **corp**. Ships with the skill; user overrides in `[[SRC rules/survey-corp|SRC rules/]]`.

Applies when comparing multiple organizations — vendors in a market, startups in a sector, public competitors, M&A target shortlists, hiring landscape.

## Default dimensions (table columns)

- **Name** (first column, link to primary source)
- **Sector / sub-segment**
- **Stage / funding total**
- **Headcount range**
- **Founded year**
- **Notable leadership** (founder still active?)
- **1-line differentiator**
- **Recent material event** (last meaningful funding / earnings / exec change)

## Default sources for the population

- **Public companies**: SEC EDGAR + Yahoo Finance / Bloomberg sector lists.
- **Private companies**: Crunchbase / PitchBook sector filters; YC / Techstars batch lists for early stage.
- **B2B vendors**: G2 / Capterra category pages, Gartner / Forrester category reports.
- **Sector trades**: industry trade publications' annual rankings.

## Public vs private — handling mixed populations

When the population mixes public and private companies, **note the data-fidelity asymmetry** in the scope note: point values for public, ranges/estimates for private. Don't silently average over the difference.

## Default disambiguation

Per [[find-corp]]: brand vs legal entity, holding vs subsidiary, same-name-different-sector. For survey purposes, default to brand; flag if legal entity matters.

## Sub-type variations

- **Startup landscape** — emphasize stage, runway signals.
- **Public competitor set** — emphasize market cap, revenue growth, segment financials.
- **Vendor shortlist (B2B)** — emphasize pricing model, lock-in risk, integration surface.
- **M&A targets** — emphasize ownership structure, recent strategic changes.

## Gotchas

- LinkedIn headcount is soft; triangulate.
- "Customer logos" on company sites are often inflated.
- Funding totals double-count debt/SAFEs.
- Past names / rebrands cause entities to be double-counted.

## User rules

(Empty — user adds in `SRC rules/survey-corp.md` to override these defaults.)
