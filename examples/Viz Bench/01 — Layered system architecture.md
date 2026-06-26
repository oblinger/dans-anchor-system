---
description: "Real-time analytics platform — ingest → process → serve layers over a shared Kafka bus, with a config service fanning out to every component."
---
# 01 — Layered system architecture

**Diagram kind:** Layered system architecture (C4-container-style).
**Layout challenge:** Multiple horizontal layers (ingest / process / serve / ops) where most flow is monotone top-to-bottom, BUT one node (the message bus) is a central shared store that many nodes on different layers read from and write to (in-layer and cross-layer hub edges), and one node (config service) fans out a dashed control edge to nearly every component. The engine must keep the layered reading order legible while routing the hub's many edges and the broadcast fan-out without crossings or tunneling.

**Domain:** A real-time product-analytics platform: clickstream and order events are ingested, normalized through a Kafka bus, enriched and aggregated by stream processors, materialized into a serving store, and exposed via an API to dashboards — with a central config service and a metrics collector observing the whole system.

## Nodes
- `web-sdk` — Web/Mobile Event SDK (emits clickstream events) [external system]
- `order-svc` — Order Service (emits order/checkout events) [external system]
- `ingest-gw` — Ingestion Gateway (HTTP collector, validates + batches) [container]
- `kafka-bus` — Kafka Event Bus (central shared message store / topics) [shared datastore]
- `enrich-proc` — Enrichment Processor (joins events with user profiles) [container]
- `agg-proc` — Aggregation Processor (windowed rollups, sessionization) [container]
- `profile-db` — User Profile DB (Postgres, lookup source for enrichment) [datastore]
- `serving-store` — Serving Store (ClickHouse, materialized aggregates) [datastore]
- `query-api` — Analytics Query API (serves aggregates to clients) [container]
- `dashboard` — Analytics Dashboard (web UI for analysts) [external system]
- `config-svc` — Config Service (feature flags, topic + sampling config) [container]
- `metrics-col` — Metrics Collector (Prometheus-style, scrapes health) [container]

12 nodes.

## Edges
- `web-sdk` → `ingest-gw` : "click events (HTTPS)" [solid]
- `order-svc` → `ingest-gw` : "order events (HTTPS)" [solid]
- `ingest-gw` → `kafka-bus` : "publish raw events" [solid]
- `kafka-bus` → `enrich-proc` : "consume raw topic" [solid]
- `enrich-proc` → `profile-db` : "lookup profile" [solid]
- `enrich-proc` → `kafka-bus` : "publish enriched topic" [solid]
- `kafka-bus` → `agg-proc` : "consume enriched topic" [solid]
- `agg-proc` → `serving-store` : "write aggregates" [solid]
- `query-api` → `serving-store` : "read aggregates" [solid]
- `dashboard` → `query-api` : "query (REST)" [solid]
- `config-svc` → `ingest-gw` : "config (sampling rules)" [dashed]
- `config-svc` → `enrich-proc` : "config (join rules)" [dashed]
- `config-svc` → `agg-proc` : "config (window sizes)" [dashed]
- `config-svc` → `query-api` : "config (feature flags)" [dashed]
- `metrics-col` → `ingest-gw` : "scrape /metrics" [dashed]
- `metrics-col` → `enrich-proc` : "scrape /metrics" [dashed]
- `metrics-col` → `agg-proc` : "scrape /metrics" [dashed]
- `metrics-col` → `query-api` : "scrape /metrics" [dashed]

18 edges.

## Groups / lanes / cardinality
- **Layers (top → bottom):** Sources (`web-sdk`, `order-svc`) → Ingest (`ingest-gw`) → Bus (`kafka-bus`) → Process (`enrich-proc`, `agg-proc`, with `profile-db` as a side datastore) → Serve (`serving-store`, `query-api`) → Clients (`dashboard`). `config-svc` and `metrics-col` are cross-cutting ops components that touch multiple layers.
- **Hub:** `kafka-bus` is the central shared store — it has 4 incident edges (one in from `ingest-gw`, one out to `enrich-proc`, one in from `enrich-proc`, one out to `agg-proc`). Do not collapse or reroute these into a single line; each is a distinct topic flow.
- **Two fan-outs:** `config-svc` → 4 dashed control edges; `metrics-col` → 4 dashed scrape edges. Both target the four internal containers (`ingest-gw`, `enrich-proc`, `agg-proc`, `query-api`). They do NOT target external systems or datastores.
- **Visual encoding:** solid = data flow; dashed = control/observability flow. `config-svc` and `metrics-col` edges are the only dashed ones (8 total). Keep the two dashed fan-outs visually distinguishable (e.g. by source proximity / label), not merged.
- **Cardinality:** `ingest-gw` receives from 2 sources; `kafka-bus` is the shared hub; each fan-out source touches exactly 4 internal containers. No edge labels are optional — every edge above is labeled.

## Acceptance
- Fidelity: the render contains exactly these 12 nodes and 18 edges (count + labels match); none added or dropped. In particular all 4 `kafka-bus` topic edges, all 4 `config-svc` dashed edges, and all 4 `metrics-col` dashed edges must be present and distinct; the solid/dashed split must hold (10 solid, 8 dashed).
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
