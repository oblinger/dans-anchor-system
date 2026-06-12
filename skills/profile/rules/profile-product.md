---
description: Default rules for describing a product — ships with the skill. User overrides in SRC rules/.
---
# profile-product — default rules

Default rules for `profile` on noun-type **product**. Ships with the skill; user overrides in `[[SRC rules/profile-product|SRC rules/]]`.

## Default dimensions

| Dimension | Notes |
|---|---|
| Canonical name + variants | SKU, model number, regional names |
| Maker | The corp behind it |
| Category + sub-category | Product taxonomy slot |
| Price + price model | One-time vs subscription; tiers; current vs MSRP |
| Key specs | The 3-5 dimensions that actually differentiate within the category |
| Target use / persona | Who it's for; what problem it solves |
| Competitors / alternatives | 3-5 most-considered alternatives |
| Reviews summary | Pro reviewers + user reviews; aggregate + thematic |
| Availability | Channels, regional |
| Warranty / support | Length, scope, escalation |
| Issues / recalls | Known problems, regulatory actions, common defects |
| Release / refresh cycle | When current version shipped; expected next refresh |

## Default sources (by category)

**Consumer physical goods**: manufacturer site → Wirecutter / Consumer Reports / RTINGS / DPReview / category reviewers → Amazon / Best Buy / retailer listings → Reddit / category forums → YouTube reviews.

**B2B software / SaaS**: vendor site (skeptically) → G2 / Capterra / TrustRadius → Gartner / Forrester → HN / r/SaaS / category subreddits → pricing pages + sales calls.

**Consumer software / apps**: App Store / Play Store recent reviews → app site + changelog → Reddit / Discord / category forum.

## Default output shape

- **Identity card** — name, SKU/model, maker, category.
- **Specs that matter** — the 3-5 differentiating dimensions.
- **Price + price model** — with region note.
- **Reviews summary** — aggregate + distribution shape.
- **Availability** — channels, regions.
- **Issues / recalls** — known problems.
- **Alternatives** — 3-5 competitors with one-line differentiators.
- **Verdict** (Deep only, only when asked).
- **Sources** — full URLs.

## Buy-decision factors (when used for recommendations)

Hard constraints first (compatibility, region, regulatory, budget) → soft preferences (reviews, brand, ecosystem, repairability) → risk factors (recalls, EOL rumors, vendor stability) → lock-in cost (especially SaaS).

## Default disambiguation

- **Versioning** — pin the year/model for ambiguous names.
- **Regional naming** — same product, different markets.
- **Bundled vs standalone** — clarify which tier.
- **OEM / white-label** — surface the OEM when relevant.

## Sub-type variants

Consumer physical (Wirecutter-style) · B2B SaaS (G2-style, contract-driven) · consumer apps (review-driven, churn-fast) · large purchases (warranty, repair, total cost of ownership).

## Gotchas

- Manufacturer specs **omit failure modes** — those live in reviews and forums.
- Aggregate ratings hide **distribution** — bimodal 4.5 ≠ centered 4.5.
- "Best of" listicles are heavily monetized; prefer independent reviewers.
- SaaS list prices are often floors; real pricing is negotiated.
- Product naming churns; anchor to capability, not name.

## User rules

(Empty — user adds in `SRC rules/profile-product.md` to override these defaults.)
