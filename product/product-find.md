# product-find — Find Where to Buy a Specific Product

Given a product the user wants to buy, pin down the exact SKU and find the best place to purchase it.


## Step 1: Disambiguate the Product

Before searching retailers, verify the user has specified a single product — not a product line or category.

**Common ambiguity signals:**
- Product name maps to multiple sizes, colors, versions, or generations
- Model number is missing or refers to a family (e.g., "AirPods" vs "AirPods Pro 2nd Gen")
- The product has regional variants

**If ambiguous:** Present the variants to the user and ask them to select. Show key differences (price, specs, release date) to help them choose. Do not proceed until pinned to one SKU.

**If clear:** Confirm the exact product name, model, and any variant details before searching.


## Step 2: Search Retailers

Search for the product across retailers, prioritized by the user's preferences.

### Retailer Priority

1. **Amazon** — preferred default. Check price, Prime availability, delivery estimate.
2. **Major retailers** — Target, Costco, Walmart. Faster delivery in some cases, good return policies.
3. **Specialty/direct** — manufacturer's store, category-specific retailers (B&H for electronics, REI for outdoor, etc.)
4. **Other** — eBay, refurbished sources, international retailers if domestic is unavailable or overpriced.

### Product-Specific Retailer Notes

*This section grows over time with non-obvious sourcing knowledge.*

- **Electronics** — B&H Photo, Adorama often match or beat Amazon; no tax in some states
- **Outdoor/sport** — REI has excellent return policy; Backcountry for deals


## Step 3: Build Comparison Table

Present a table of purchase options:

| Retailer | Price | Shipping | Delivery Est. | Return Policy | Link |
|----------|-------|----------|---------------|---------------|------|

Include:
- At least 3 retailers if available
- Note if any are out of stock
- Flag significant price differences (>15%) — could indicate wrong variant or gray market
- Note coupon codes or current promotions found during search


## Step 4: Recommend

Recommend the best option based on:
1. Price (including shipping/tax)
2. Delivery speed
3. Return policy reliability
4. Retailer trustworthiness

Present the recommendation and surf the top option for the user:
```bash
ctrl surf "<purchase_url>"
```

Surf additional options if the user wants to compare.
