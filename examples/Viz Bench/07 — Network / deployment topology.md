---
description: "Production deployment topology for a SaaS app — edge, app, and data tiers with cross-tier service calls and ports"
---
# 07 — Network / deployment topology

**Diagram kind:** Network / deployment topology.
**Layout challenge:** hosts + services + ports grouped into tier clusters, with cross-cluster links (north-south request flow plus east-west data calls) that must route between containers without overlapping the cluster boxes or each other.
**Domain:** the production deployment of "Bookstack", a multi-tier SaaS web application running across an edge tier, an application tier, and a data tier inside a single VPC.

## Nodes
- INET — Public Internet [external actor / cloud]
- CDN — Cloudflare CDN edge [edge node]
- LB — AWS ALB load balancer, :443 [edge node]
- WAF — AWS WAF web-application firewall [edge node]
- WEB1 — Web/API host web-1, :8080 [app host]
- WEB2 — Web/API host web-2, :8080 [app host]
- WORKER — Background worker host worker-1 [app host]
- REDIS — Redis cache/queue, :6379 [data node]
- PG_PRIMARY — Postgres primary db-primary, :5432 [data node]
- PG_REPLICA — Postgres read replica db-replica, :5432 [data node]
- S3 — S3 object storage (assets bucket) [data node]
- SES — AWS SES email service [external service]

## Edges
- INET → CDN : "HTTPS :443" [solid]
- CDN → WAF : "HTTPS :443" [solid]
- WAF → LB : "HTTPS :443" [solid]
- LB → WEB1 : "HTTP :8080" [solid]
- LB → WEB2 : "HTTP :8080" [solid]
- WEB1 → REDIS : "session/cache :6379" [solid]
- WEB2 → REDIS : "session/cache :6379" [solid]
- WEB1 → PG_PRIMARY : "read/write :5432" [solid]
- WEB2 → PG_PRIMARY : "read/write :5432" [solid]
- WEB1 → PG_REPLICA : "read-only :5432" [dashed]
- WEB2 → PG_REPLICA : "read-only :5432" [dashed]
- WEB1 → S3 : "asset GET/PUT" [solid]
- WEB2 → S3 : "asset GET/PUT" [solid]
- PG_PRIMARY → PG_REPLICA : "streaming replication" [dashed]
- WORKER → REDIS : "consume queue :6379" [solid]
- WORKER → PG_PRIMARY : "write :5432" [solid]
- WORKER → SES : "send email" [solid]

## Groups / lanes / cardinality
- Three tier clusters: **Edge tier** {CDN, LB, WAF}, **Application tier** {WEB1, WEB2, WORKER}, **Data tier** {REDIS, PG_PRIMARY, PG_REPLICA, S3}.
- INET and SES are external (outside the VPC); they sit outside all three tier clusters.
- Cardinality: two interchangeable web hosts (WEB1, WEB2) both fan out identically to the data tier; one Postgres primary with one read replica (replication is one-directional primary→replica).

## Acceptance
- Fidelity: the render contains exactly these 12 nodes and 17 edges (count + labels match); none added or dropped.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
