---
description: "ER model of an e-commerce store: customers, orders, products, payments, and reviews with crow's-foot cardinalities"
---
# 05 — Entity-relationship

**Diagram kind:** Entity-relationship (ER) diagram.
**Layout challenge:** placing entity boxes (each carrying an attribute list) so that relationship lines stay short and uncrossed, while every relationship's cardinality (1—1, 1—N, N—M) reads clearly at both ends; associative/junction entities must sit between the two entities they bridge.
**Domain:** the data model behind a mid-sized online retail store, covering customers, addresses, orders, line items, products, categories, payments, shipments, and product reviews.

## Nodes
- CUSTOMER — entity [customer_id (PK), email, full_name, created_at]
- ADDRESS — entity [address_id (PK), customer_id (FK), line1, city, postal_code, country]
- ORDER — entity [order_id (PK), customer_id (FK), shipping_address_id (FK), status, placed_at]
- ORDER_ITEM — associative entity [order_item_id (PK), order_id (FK), product_id (FK), quantity, unit_price]
- PRODUCT — entity [product_id (PK), sku, name, price, stock_qty]
- CATEGORY — entity [category_id (PK), name, slug]
- PRODUCT_CATEGORY — associative/junction entity [product_id (FK), category_id (FK)]
- PAYMENT — entity [payment_id (PK), order_id (FK), method, amount, paid_at]
- SHIPMENT — entity [shipment_id (PK), order_id (FK), carrier, tracking_no, shipped_at]
- REVIEW — entity [review_id (PK), product_id (FK), customer_id (FK), rating, body, created_at]

## Edges
- CUSTOMER → ADDRESS : "has" [solid] — cardinality 1 — N (one customer, many addresses)
- CUSTOMER → ORDER : "places" [solid] — cardinality 1 — N (one customer, many orders)
- ADDRESS → ORDER : "ships to" [solid] — cardinality 1 — N (one address used by many orders)
- ORDER → ORDER_ITEM : "contains" [solid] — cardinality 1 — N (one order, many line items)
- PRODUCT → ORDER_ITEM : "ordered as" [solid] — cardinality 1 — N (one product appears in many line items)
- PRODUCT → PRODUCT_CATEGORY : "classified in" [solid] — cardinality 1 — N (one product, many junction rows)
- CATEGORY → PRODUCT_CATEGORY : "groups" [solid] — cardinality 1 — N (one category, many junction rows)
- ORDER → PAYMENT : "paid by" [solid] — cardinality 1 — N (one order, one-or-more payments)
- ORDER → SHIPMENT : "fulfilled by" [solid] — cardinality 1 — N (one order, one-or-more shipments)
- PRODUCT → REVIEW : "reviewed in" [solid] — cardinality 1 — N (one product, many reviews)
- CUSTOMER → REVIEW : "writes" [solid] — cardinality 1 — N (one customer, many reviews)

## Groups / lanes / cardinality
- No swimlanes or visual containers.
- Cardinality is the load-bearing semantic and MUST render at both ends of each line (crow's-foot or 1/N/M notation): the "1" side at the parent entity, the "many" side at the child entity.
- ORDER_ITEM resolves the many-to-many between ORDER and PRODUCT; it must sit between those two entities.
- PRODUCT_CATEGORY resolves the many-to-many between PRODUCT and CATEGORY; it must sit between those two entities. Logically PRODUCT ↔ CATEGORY is N—M, realized through the two 1—N edges to PRODUCT_CATEGORY enumerated above.
- Logically ORDER ↔ PRODUCT is N—M, realized through the two 1—N edges to ORDER_ITEM enumerated above.
- PK/FK markers in each entity's attribute list must be preserved (they encode the relationship endpoints).

## Acceptance
- Fidelity: the render contains exactly these 10 nodes and 11 edges (count + labels + cardinalities match); none added or dropped. Each entity keeps its full attribute list with PK/FK markers.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
