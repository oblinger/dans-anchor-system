---
description: "canonical breadcrumb-spine exemplar — a leaf whose primary entity is a table"
---
:>> [[DAS]] → [[examples]] → [FEX Breadcrumb Spine](hook://p/FEX%20Breadcrumb%20Spine) 
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

> **Canonical breadcrumb spine.** This page is a **leaf** — nothing hangs under it — so its spine points only *upward*: a `:>>` breadcrumb as the first body line, no dispatch table anywhere. Read the shape:
> - **Line 1 is the breadcrumb**, line 2 the H1 with **no blank line between them**, line 3 one sentence saying what the page is.
> - **Line 5 is the overview entity** — the budget table, which is the entire reason the page exists. It sits *directly* under the summary; the explanation lives below it, never above.
> - **The table is content, not navigation.** A primary data table on a leaf is not a dispatch table and does not make this page a hub — which is exactly the distinction a reader has to be able to make on sight. Compare [[FEX List Dispatch]], where a table of the same visual weight *is* the routing surface.
>
> The live counterpart is [[LUMEN Nudge]]: breadcrumb, H1, one sentence, then the table it exists for.

## Why the budget is 160 ms

Anything above 200 ms is perceptible on the Harbor console's live view, and the console repaints on every response. The 40 ms of headroom absorbs a retried auth lookup without crossing the perceptible line — which is why [[Espresso]]'s three breaches this quarter did not produce a single user report, while [[Snap]]'s eleven did.
