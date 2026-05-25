# product-hunt — Product Category Research

Research and compare products across a category. Find the best options, understand the key dimensions, and present a structured comparison. Each hunt is saved as its own dated report under [[PHUNT]].

## Output location

All hunts land under **`~/ob/kmr/Log/PHUNT/`** as flat dated markdown files:

```
PHUNT/
├── PHUNT.md                                       (umbrella + recent-hunts index)
├── _PHUNT Template.md                             (file template)
├── 2026-05-07 Bankruptcy.md
├── 2026-05-05 iPhone SE 3rd Generation Case.md
└── ...
```

Filename pattern: `YYYY-MM-DD <Title>.md`. Slashes in titles get rewritten to ` or ` (e.g., "Markers / Toppers" → "Markers or Toppers") to avoid path conflicts.

## Report file format

Each hunt's `YYYY-MM-DD <Title>.md` follows this shape:

```markdown
# PHUNT — <Title>

**Date:** YYYY-MM-DD
**Goal:** one-line bold summary of what the user is looking for

| Top | Product                  | Price  | Dimension A    | Dimension B   | ... | Best For                      |
| --- | ------------------------ | ------ | -------------- | ------------- | --- | ----------------------------- |
| 1   | **[Name](url)**          | $35-40 | ...            | ...           | ... | All-around resort skiing      |
| 2   | **[Name](url)**          | $60    | ...            | ...           | ... | Cold days, anti-fog priority  |

## Top 5 Recommendations

1. **Name ($35-40)** — Best overall. Brief rationale here.
2. **Name ($60)** — Best for X. Brief rationale here.

## Review Sites Consulted

1. https://example.com/review-site-1
2. https://example.com/review-site-2

## Key Dimensions

- **Price** — cost range
- **Dimension A** — what this column means
- **Dimension B** — what this column means
```

**Format notes:**

- **H1** — `# PHUNT — <Title>`. Single file per hunt; H1 (not H2) since the file is standalone. Filename carries the date; H1 doesn't repeat it.
- **Date line** — `**Date:** YYYY-MM-DD` near the top.
- **Comparison table** — `Top` column is rank (1–10), `Product` is bold with a purchase / product-page link (`**[Name](url)**`), remaining columns are the key dimensions identified during research. Column names vary per product category.
- **Top 5 Recommendations** — numbered list, each entry is `**Product (Price)** — Category label. Brief rationale.`
- **Review Sites Consulted** — numbered list of full URLs (not markdown links).
- **Key Dimensions** — named list explaining what each column means.

## Usage

```
/product hunt <product description>    # e.g., "ski face mask with breathing hole"
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

From the review sites, determine the **most important comparison dimensions** for this product category. These become the columns of the comparison table.

### Phase 4: Build Comparison

Select the **top 10 products** based on review consensus.

### Phase 5: Write the Report

1. **Compute the filesystem-safe title** — sanitize `/` to ` or `, leave commas and parens alone.
2. **Write the report** at `~/ob/kmr/Log/PHUNT/YYYY-MM-DD <Title>.md` using the format above. No wrapping folder — one flat file per hunt.
3. **Prepend to the umbrella index** at `~/ob/kmr/Log/PHUNT/PHUNT.md`:
   - Find the `## Recent hunts` H2.
   - Insert a new bullet at the TOP of that list: `- [[YYYY-MM-DD <Title>|YYYY-MM-DD — <Title>]]`.

### Phase 6: Surf Everything

Open in the user's browser:
- All review site URLs
- Buy/product pages for the top 10 products

Use `open "<url>"` via Bash to surf each page.

## Defaults

- **Products**: 10 (top 10)
- **Review sites**: 10
- User can override: `/product hunt 5 products, 5 reviews — wireless earbuds`

## Migration notes

**2026-05-10** — Previously, all hunts lived as H2 sections in a single file at `~/ob/kmr/SYS/SYS Topic/Product Hunt/Product Hunt.md`. That file is now a redirect stub; the existing hunts were split into per-hunt dated folders under `~/ob/kmr/Log/PHUNT/`. The `[[Product Hunt]]` wiki-link still resolves to the redirect for back-compat; new hunts use `[[PHUNT]]`.

**2026-05-18** — Flattened from per-hunt folders (`YYYY-MM-DD <Topic>/PHUNT <Topic>.md`) to flat files (`YYYY-MM-DD <Topic>.md`). Each hunt is a single file; the wrapping folder added zero structure since each hunt held only one document. Template changed from a folder template (`_PHUNT Template/_PHUNT Template.md`) to a file template (`_PHUNT Template.md`).
