---
description: Default rules for surveying products — ships with the skill. User overrides in SRC rules/. Migrated from the legacy /product hunt action.
---
# survey-product — default rules

Default rules for `survey` on noun-type **product**. Ships with the skill; user overrides in `[[SRC rules/survey-product|SRC rules/]]`.

Subsumes the broad-research phase of legacy `/product hunt`. Applies when comparing multiple products in a category — "best CRMs for a 20-person sales team," "DSLR cameras under $1500," "Pomodoro apps for Mac."

## Default dimensions per sub-type

**Consumer physical goods**: Name (link), maker, MSRP, current street price, key specs (3-5), aggregate rating + distribution shape, pro-reviewer take (Wirecutter / RTINGS / etc.), notable issues / recalls.

**B2B software / SaaS**: Name (link), category, pricing (published + real if known), target persona, key feature differentiator, G2/Capterra rating, top 3 alternatives, lock-in / data portability note.

**Consumer software / apps**: Name (link), platform, free tier?, subscription tier(s), rating (recency-weighted), key differentiator, last major update.

**Large purchases (cars / appliances)**: Name (link), MSRP, key specs, reliability score (Consumer Reports), warranty + repair cost, total cost of ownership estimate.

## Default sources per sub-type

- **Consumer physical**: Wirecutter / Consumer Reports / RTINGS / DPReview / category-specific reviewers FIRST (independent). Then retailer listings for availability/price. Then category subreddits for long-term ownership signal.
- **B2B SaaS**: G2 / Capterra / TrustRadius for the category roster. Then Gartner / Forrester for enterprise positioning. HN / r/SaaS for adoption signals.
- **Consumer apps**: App Store / Play Store category browsing + recent reviews. Then category-specific subreddits.

## Default behavior

- **Include both aggregate rating AND distribution shape** — bimodal 4.5 is not a centered 4.5.
- **For SaaS, distinguish published vs real pricing** where the gap matters.
- **For consumer goods, lead with independent reviewers**; relegate generic listicle rankings to a footnote.
- **Include "last meaningful update" / "release date"** — stale products are often quietly EOL.

## Default population + review-site counts (from legacy /product hunt)

- **Products**: 10 (top 10) by default. User can override (`/survey 5 products — wireless earbuds`).
- **Review sites consulted**: 10 by default. Read each to extract candidate products + dimension consensus.

## Workflow specifics (from legacy /product hunt)

1. **Understand the product** — gather constraints (budget, features, use case).
2. **Find ~10 review sites** covering this category. From each, harvest: which products are recommended, which dimensions reviewers emphasize, price tiers.
3. **Identify key dimensions** — from review-site consensus; these become comparison-table columns.
4. **Select top 10 products** based on review consensus.
5. **Phase 4.5 — resolve a purchasable link for each product (REQUIRED)** — see below.
6. **Write the report** — RRR shape (per [[survey/rules/survey|survey.md]]) plus `## Key Dimensions` (explain columns) and `## Review Sites Consulted` (full URLs) sections.
7. **Surf everything** — open in browser: all review URLs + all top-10 purchase pages (`open "<url>"`).

## Phase 4.5 — Purchasable-link verification (REQUIRED)

For every product in the comparison table, the URL in the first column MUST point to a page where the user can actually buy the item — a page that:

- Renders a price.
- Shows an active "Add to Cart" / "Buy Now" button.
- Is **not** marked "Sold Out" / "Out of Stock" / "Notify Me" / "Currently Unavailable."

Acceptable link types, in order of preference:

1. **Manufacturer's own shop page (in stock)** — best when available.
2. **Major retailer purchase page (in stock)** — REI, Amazon, Backcountry, B&H, Walmart, Target, etc.
3. **Manufacturer product/info page (no Buy button)** — fallback ONLY when no live purchase page exists for that exact SKU anywhere. Annotate `(info page — out of stock at time of writing)`.

Verification — for each product, before locking in the link:

- Use `WebFetch` (or `open` + read page title) to confirm price + active purchase action + not out of stock.
- If the planned page is out of stock, fall through the preference order (manufacturer → REI → Amazon → Backcountry → …).
- If genuinely unavailable everywhere, either (a) swap for a comparable in-stock alternative, or (b) keep + annotate.

This rule supersedes any instinct to link to "the canonical manufacturer page" when that page isn't a shop. Goal: enable a purchase decision, not present a brochure.

## Hunt-before-find (workflow note)

Per the legacy `/product hunt` convention: surveying a category broadly (this skill) should precede pinning a specific SKU ([[find-product]]). Output: "based on the survey, the top candidate is X (link to find for SKU details)."

## Meta-survey for novel categories

For a product category not surveyed before, **run meta-survey first** (per [[describe/SKILL|skill methodology]]). Look at how Wirecutter / RTINGS / category reviewers organize their comparisons — borrow their dimension set rather than inventing in a vacuum.

## Gotchas

- Manufacturer specs **omit failure modes** — those live in reviews/forums.
- Aggregate ratings hide **distribution shape**.
- "Best of" listicles are heavily monetized; prefer independent reviewers.
- SaaS list prices often differ materially from real pricing.
- Product naming churns; anchor to capability.

## User rules

(Empty — user adds in `SRC rules/survey-product.md` to override these defaults.)
