---
description: "canonical breadcrumb-spine exemplar — a leaf whose primary entity is a table"
---
:>> [[DAS]] → [[examples]] → [Harbor Latency Budget](hook://p/Harbor%20Latency%20Budget) 
# Harbor Latency Budget
The per-hop millisecond budget a Harbor request is allowed to spend, and who owns each hop.

| Hop | Budget | Owner | Breaches this quarter |
|---|---|---|---|
| TLS handshake | 40 ms | [[Devtools Observe\|Observe]] | 0 |
| Auth lookup | 25 ms | [[Espresso]] | 3 |
| Route resolve | 15 ms | [[Knots]] | 0 |
| Payload assembly | 60 ms | [[Snap]] | 11 |
| Egress | 20 ms | [[Bridges Studio\|Studio]] | 1 |
| **Total** | **160 ms** | — | **15** |

> [!info] Canonical breadcrumb spine
> This page is a **leaf** — nothing hangs under it — so its spine points only *upward*: a `:>>` breadcrumb as the whole spine, above the H1, with no dispatch table anywhere.
> - **The spine is everything before the H1** — here, one breadcrumb line. Then the H1, then one sentence saying what the page is, with no blank line between them.
> - **The budget table is the [[DAS spine#The heart|heart]]** — the entire reason the page exists. It sits *directly* under that sentence, above the fold, so the reader lands on it without scrolling. The explanation lives below it, never above.
> - **The heart is content, not navigation.** A primary data table on a leaf is not a dispatch table and does not make this page a hub — exactly the distinction a reader must make on sight. Compare [[Bridges]], where a table of the same visual weight *is* the routing surface.
>
> The live counterpart is [[LUMEN Nudge]]: breadcrumb, H1, one sentence, then the table it exists for.

## Why the budget is 160 ms

Anything above 200 ms is perceptible on the Harbor console's live view, and the console repaints on every response. The 40 ms of headroom absorbs a retried auth lookup without crossing the perceptible line — which is why [[Espresso]]'s three breaches this quarter did not produce a single user report, while [[Snap]]'s eleven did.
