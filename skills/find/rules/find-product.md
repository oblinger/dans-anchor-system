---
description: Default rules for finding a product (SKU-level identification, retailer comparison) — ships with the skill. User overrides in SRC rules/. Migrated and extended from the legacy /product find skill.
---
# find-product — default rules

Default rules for `find` on noun-type **product** — pinning a specific SKU, comparing retailers, identifying the canonical purchase URL. Ships with the skill; user overrides in `[[SRC rules/find-product|SRC rules/]]`.

Subsumes the legacy `/product find` action from [[SKL Purchase]].

## Default sources for identification

**Consumer physical**: manufacturer site (canonical SKU) → Amazon / Best Buy / target retailers → price-tracking aggregators (camelcamelcamel, PriceSpy).

**B2B SaaS**: vendor pricing page → G2 / Capterra for plan reality → re-sellers if applicable.

**Consumer software / apps**: App Store / Play Store listing.

## Default behavior

- **Pin the exact SKU** before returning. Variants (color, capacity, region) frequently differ in URL and price; ambiguity at the SKU level is unacceptable for a find.
- **Compare retailers** before returning a canonical URL — when the same SKU is sold at multiple places, list at least 3 with current prices and flag the best price.
- **Note availability** in the saved lookup: in stock / backorder / discontinued.
- **Note region** explicitly — pricing and availability are region-specific.

## Default disambiguation

- **Versioning**: "iPhone" without a number is ambiguous → pin year/model.
- **Regional naming**: same product, different markets.
- **Bundled vs standalone**: clarify which tier.
- **OEM / white-label**: surface the OEM when relevant.

## Default output (the saved lookup)

- Canonical product name + SKU/model
- Maker
- Best-price retailer + URL + current price
- 2-3 alternate retailer URLs + prices (when meaningfully different)
- Availability + region
- Notable issues / recalls if any

## When to escalate to a different verb

If the user asks "what's the best X for purpose Y" — that's not a `find`, it's a `describe` (one-product profile) or `survey` (multi-product comparison). Push back: "want a profile or a comparison instead?"

## Hand-off to purchase

This skill **identifies** the SKU and the cheapest URL — it doesn't execute purchase. For purchasing, see the legacy [[SKL Purchase]] skill (`/product buy`).

## User rules

(Empty — user adds in `SRC rules/find-product.md` to override these defaults.)
