---
name: product
description: >
  Product research and purchasing — hunt for products in a category, find where to buy, execute purchases.
  Use with an action argument: /product hunt, /product find, /product buy, /product reorder.
tools: Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep
user_invocable: true
---

# Product — Research & Purchase

Product research, comparison, and purchasing workflows.


| ACTIONS            | File               | Description                                              |
| ------------------ | ------------------ | -------------------------------------------------------- |
| `/product hunt`    | [[product-hunt]]   | Research a category, compare top 10, surf review sites   |
| `/product find`    | [[product-find]]   | Pin down exact SKU, compare retailers, find best price   |
| `/product buy`     | [[product-buy]]    | Navigate to purchase page for checkout                   |
| `/product reorder` | [[product-reorder]]| Reorder a previously purchased consumable                |


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, show the actions table above
