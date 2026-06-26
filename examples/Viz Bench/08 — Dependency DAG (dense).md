---
description: "Build dependency graph for a microservices monorepo — 14 packages, many cross-edges"
---
# 08 — Dependency DAG (dense)

**Diagram kind:** Dependency DAG (dense).
**Layout challenge:** many nodes with many cross-cutting directed edges — the engine must minimize edge crossings, respect topological ordering (no back-edges; the graph is acyclic), and keep dense fan-in/fan-out hubs legible without tangling.
**Domain:** the build dependency graph of a Node monorepo for a food-delivery platform, where each node is an internal package and each edge means "depends on (imports) at build time".

## Nodes
- logger — `@plat/logger` — structured logging utility [leaf package]
- config — `@plat/config` — env + runtime config loader [leaf package]
- types — `@plat/types` — shared TypeScript type definitions [leaf package]
- db — `@plat/db` — Postgres connection + query layer
- cache — `@plat/cache` — Redis client wrapper
- http — `@plat/http` — HTTP client + retry middleware
- auth — `@plat/auth` — JWT issue/verify + session
- users — `@svc/users` — user accounts service
- restaurants — `@svc/restaurants` — restaurant catalog service
- menu — `@svc/menu` — menu + pricing service
- orders — `@svc/orders` — order lifecycle service
- payments — `@svc/payments` — payment + refund service
- notifications — `@svc/notifications` — email/SMS/push fan-out
- gateway — `@app/gateway` — public API gateway [root / app entry]

## Edges
- db → logger : "depends on" [solid]
- db → config : "depends on" [solid]
- db → types : "depends on" [solid]
- cache → logger : "depends on" [solid]
- cache → config : "depends on" [solid]
- http → logger : "depends on" [solid]
- http → config : "depends on" [solid]
- auth → types : "depends on" [solid]
- auth → cache : "depends on" [solid]
- auth → db : "depends on" [solid]
- users → db : "depends on" [solid]
- users → auth : "depends on" [solid]
- users → types : "depends on" [solid]
- restaurants → db : "depends on" [solid]
- restaurants → cache : "depends on" [solid]
- restaurants → types : "depends on" [solid]
- menu → db : "depends on" [solid]
- menu → cache : "depends on" [solid]
- menu → restaurants : "depends on" [solid]
- menu → types : "depends on" [solid]
- orders → db : "depends on" [solid]
- orders → users : "depends on" [solid]
- orders → menu : "depends on" [solid]
- orders → payments : "depends on" [solid]
- orders → types : "depends on" [solid]
- payments → db : "depends on" [solid]
- payments → http : "depends on" [solid]
- payments → auth : "depends on" [solid]
- payments → types : "depends on" [solid]
- notifications → http : "depends on" [solid]
- notifications → users : "depends on" [solid]
- notifications → orders : "depends on" [solid]
- notifications → config : "depends on" [solid]
- gateway → auth : "depends on" [solid]
- gateway → users : "depends on" [solid]
- gateway → restaurants : "depends on" [solid]
- gateway → menu : "depends on" [solid]
- gateway → orders : "depends on" [solid]
- gateway → payments : "depends on" [solid]
- gateway → notifications : "depends on" [solid]
- gateway → http : "depends on" [solid]

## Groups / lanes / cardinality
- No explicit containers required. The graph is a DAG (acyclic, all edges point toward dependencies). Three nodes are pure leaves (logger, config, types — no outgoing edges); gateway is the sole root (no incoming edges). Edges are uniform "depends on" (solid); the labels may be elided into a single legend if the renderer prefers, but every directed edge must remain present and distinct.

## Acceptance
- Fidelity: the render contains exactly these 14 nodes and 41 edges (count + labels match); none added or dropped. Direction of every edge is preserved (source depends on target).
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; crossings minimized; per [[R-diagram]].
