---
description: "made-up definition-list heart — a concept page whose facts are sentences, not cells"
---
:>> [[DAS]] → [[FEX]] → [Harbor Tenancy Model](hook://p/Harbor%20Tenancy%20Model) 
# Harbor Tenancy Model
How Harbor divides one deployment among many customers — the five terms every other Harbor page uses without defining.

- **Tenant:** one paying customer, identified by a tenant id that every request carries from the [[Harbor Hops|TLS handshake]] onward; nothing is shared across the boundary except the binary itself.
- **Tier:** the contract a tenant is on — standard or enterprise — which fixes its rate ceiling, its [[Harbor Latency Budget|latency budget]] headroom, and whether an [[Harbor Runbook Auth Storm|auth storm]] pages a human or just sheds load.
- **Depot:** a tenant's physical site, each with its own egress route; a tenant has one or many, and the [[Harbor Account Northwind|Northwind]] expansion is exactly two more of these.
- **Pool:** the connection pool a depot draws from, sized per tier since [[Harbor Releases|4.2]]; a depot never borrows from another tenant's pool, which is the isolation guarantee the whitepaper sells.
- **Quota:** the monthly request allowance per tenant, reviewed on the [[Harbor Runbook Quota Review|quota-review]] cadence; exceeding it degrades to the standard tier's rate ceiling rather than refusing traffic.

## Overview

**Isolation is by tenant, capacity is by depot, and the two never cross.** That single sentence resolves most of the questions this page gets asked: a noisy depot cannot starve its sibling (they share a tenant, not a pool), and a noisy tenant cannot touch anyone else at all. The cost is fragmentation — an enterprise tenant with twelve depots holds twelve pools, most of them idle — which is why [[Harbor Runbook Cache Warm]] exists.

## Why this page is an example
Every bullet is a fact about *this* subject, so it is a heart — but each fact is a clause with a dependent phrase, not a value that fits a cell, which is what makes it a **definition list** rather than a fact card. The term ends in a colon (`**Tenant:**`), not the em-dash the vault's prose definition lists use. Specified at [[DAS heart]] § Definition list.
