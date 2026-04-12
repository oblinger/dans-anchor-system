---
description: How to research and purchase products — hunt, find, buy, reorder
---

# SKL Product Guide (Skill: [[product/SKILL]])

The Product skill handles the full purchasing lifecycle: researching a product category, narrowing down to a specific item, executing the purchase, and reordering consumables. It uses web search and browser automation to gather information and navigate to purchase pages.

The workflow moves through four stages. Hunt is the broad research phase — surveying a category, comparing top options, reading reviews. Find narrows to a specific SKU and compares retailers for the best price. Buy navigates to the purchase page for checkout. Reorder handles repeat purchases of consumables you have bought before.

## Commands

| Command | Description |
|---------|-------------|
| `/product hunt` | Research a category — compare top 10, surf review sites |
| `/product find` | Pin down exact SKU, compare retailers, find best price |
| `/product buy` | Navigate to purchase page for checkout |
| `/product reorder` | Reorder a previously purchased consumable |

## Key Concepts

- **Hunt before find** — Start with `/product hunt` to explore a category broadly before narrowing down
- **Web-driven** — Uses web search and WebFetch to gather pricing, reviews, and availability
- **Browser handoff** — `/product buy` navigates to the purchase page; you complete checkout manually
- **Reorder memory** — `/product reorder` works for items you have purchased before, looking up past details
