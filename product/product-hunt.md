# product-hunt — Product Category Research

Research and compare products across a category. Find the best options, understand the key dimensions, and present a structured comparison.

# Example Entry Format

```markdown
## 2026-03-01 — Ski Face Mask / Balaclava with Breathing Hole
**Goal:** Face mask for skiing that covers nose, has a breathing hole/vent to prevent goggle fog, comfortable under helmet.

| Top | Product                        | Price  | Breathing System                                             | Anti-Fog                                    | Warmth        | Material                           | Helmet Fit                      | Best For                      |
| --- | ------------------------------ | ------ | ------------------------------------------------------------ | ------------------------------------------- | ------------- | ---------------------------------- | ------------------------------- | ----------------------------- |
| 1   | **[BlackStrap Hood](https://blackstrap.com/products/hood-balaclava-solids)** | $35-40 | Hinged face panel — flip down to breathe, up for warmth      | Excellent — hinge eliminates fog            | Moderate      | TREO synthetic, UPF 50+            | Excellent — seamless, thin      | All-around resort skiing      |
| 2   | **[NAROO Z9H](https://naroomask.com/product/z9h/)** | $60    | 3D Air-Room chamber + zip valve — fabric never touches mouth | Best on market — rigid frame diverts breath | Very warm     | Synthetic with EX-BONE frame       | Good                            | Cold days, anti-fog priority  |

### Top 5 Recommendations

1. **BlackStrap Hood ($35-40)** — Best overall. Brief rationale here.
2. **NAROO Z9H ($60)** — Best anti-fog technology. Brief rationale here.

### Review Sites Consulted

1. https://example.com/review-site-1
2. https://example.com/review-site-2

### Key Dimensions

- **Price** — cost range
- **Breathing System** — how it handles airflow
- **Anti-Fog** — effectiveness at preventing goggle fogging
```

### Format Notes

- **H2 header** — `## YYYY-MM-DD — Product Category Name` — date + em-dash + descriptive name
- **Goal line** — one-line bold summary of what the user is looking for
- **Comparison table** — `Top` column is rank (1-10), `Product` is bold with a purchase/product-page link (`**[Name](url)**`), remaining columns are the key dimensions identified during research. Column names vary per product category.
- **Top 5 Recommendations** — numbered list, each entry is `**Product (Price)** — Category label. Brief rationale.`
- **Review Sites Consulted** — numbered list of full URLs (not markdown links)
- **Key Dimensions** — named list explaining what each column means. This section goes at the bottom.
- New entries are inserted at the top of the file (below the dispatch header), making the page a reverse-chronological log.

## Usage

```
/product-hunt <product description>    # e.g., "ski face mask with breathing hole"
```

## Workflow

### Phase 1: Understand the Product

Ask the user what product they're looking for. Gather any constraints or preferences (budget, specific features, use case).

### Phase 2: Find Review Sites

Search the web for review and comparison sites covering this product category. Target **10 review sites** by default. Read each one to understand:
- What products are recommended
- What dimensions/attributes reviewers consider important
- Price ranges and value tiers

### Phase 3: Identify Key Dimensions

From the review sites, determine the **most important comparison dimensions** for this product category. These become the columns of the comparison table. Typical dimensions include:
- Price
- Key feature ratings (varies by product)
- Pros / Cons
- Best for (use case)

### Phase 4: Build Comparison Table

Select the **top 10 products** based on review consensus. Create or update the Product Hunt page with:

1. A new entry at the TOP of the page (reverse chronological) with:
   ```
   ## YYYY-MM-DD — Product Category Name
   ```
2. A comparison table with products as rows and key dimensions as columns
3. A **Top 5 recommendation** with brief rationale for each
4. A mitten/glove compatibility note or equivalent domain-specific concern if relevant

### Phase 5: Surf Everything

Open in the user's browser:
- All review site URLs
- Buy/product pages for the top 10 products

Use `open "<url>"` via Bash to surf each page.

## Product Hunt Page

The product hunt log is stored at: **[[Product Hunt]]**

Location: `/Users/oblinger/ob/kmr/SYS/SYS Topic/Product Hunt/Product Hunt.md`

Each hunt is appended at the top as a new H2 entry (below the dispatch header), creating a reverse-chronological log of all product research. The dispatch header line (`.[[Product Hunt]].  >[[SYS Topic]]`) must always remain at the top of the file — new entries go after the header and the `---` separator.

## Defaults

- **Products**: 10 (top 10)
- **Review sites**: 10
- User can override: `/product-hunt 5 products, 5 reviews — wireless earbuds`
