---
description: "Clickstream ETL pipeline — raw events ingested, validated, enriched, aggregated, and loaded into a warehouse + dashboard, with a dead-letter side path."
---
# 02 — Linear data pipeline (ETL)

**Diagram kind:** Linear data pipeline (ETL) — a directed source→…→sink processing chain.
**Layout challenge:** a long mostly-linear chain of stages that must NOT render as one illegible ultra-wide horizontal strip; the engine must wrap or fold the chain (serpentine / multi-row / column-stacked) to hold an aspect ratio near square while keeping flow direction unambiguous, and must place the short side-branch (dead-letter quarantine) without breaking the main line's readability.

**Domain:** A web analytics company's daily clickstream ETL — raw page-view and click events land in object storage, are ingested and validated, bad records are quarantined, good records are enriched and sessionized, aggregated into daily rollups, and loaded into a warehouse that feeds a BI dashboard.

## Nodes
- src — Raw event files (S3 landing bucket) [source]
- ingest — Ingestion job (Airflow-triggered loader) [process]
- validate — Schema validation & dedup [process]
- dlq — Dead-letter / quarantine bucket (invalid records) [sink]
- enrich — Enrichment (geo-IP + user-agent parse) [process]
- sessionize — Sessionization (group events into sessions) [process]
- aggregate — Daily aggregation (rollups by page/session) [process]
- qc — Data-quality check (row-count & null gates) [process]
- load — Warehouse load (Snowflake COPY) [process]
- warehouse — Analytics warehouse (Snowflake `events_daily`) [datastore]
- dashboard — BI dashboard (Looker daily report) [sink]

## Edges
- src → ingest : "raw JSON files" [solid]
- ingest → validate : "parsed records" [solid]
- validate → dlq : "rejected records" [dashed]
- validate → enrich : "valid records" [solid]
- enrich → sessionize : "enriched events" [solid]
- sessionize → aggregate : "sessions" [solid]
- aggregate → qc : "daily rollups" [solid]
- qc → load : "passed rollups" [solid]
- load → warehouse : "COPY INTO" [solid]
- warehouse → dashboard : "query / refresh" [solid]

## Groups / lanes / cardinality
- No swimlanes. Single main flow `src → ingest → validate → enrich → sessionize → aggregate → qc → load → warehouse → dashboard`.
- One side-branch: `validate → dlq` (dashed) is an error/quarantine offshoot, not part of the happy path; it terminates immediately at `dlq` (no return edge).
- All edges are 1:1 between adjacent stages; no fan-out except the single split at `validate` (to `enrich` and `dlq`).

## Acceptance
- Fidelity: the render contains exactly these 11 nodes and 10 edges (count + labels match); none added or dropped. The `validate → dlq` dashed branch in particular must be present and rendered distinct from solid happy-path edges.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6 (the chain must be folded/wrapped, not laid out as a single wide strip); no overlaps; per [[R-diagram]].
