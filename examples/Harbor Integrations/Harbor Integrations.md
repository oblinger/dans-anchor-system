---
description: "the third-party systems Harbor talks to — one page per integration, rostered below"
---

| -[[Harbor Integrations]]- | : the third-party systems Harbor talks to — one page per integration, rostered below<br>→ [[DAS]] → [[FEX]] → [Harbor Integrations](hook://p/Harbor%20Integrations)  |
| --- | --- |
| Related | [[Harbor Tenancy Model]],  [[Harbor Latency Budget]],  [[HRUN\|Harbor Runbooks]],  [[Harbor Releases]],   |
| Docs | [[FEX Architecture\|Architecture]],  [[FEX API Design\|API]],  [[Harbor Whitepaper\|Whitepaper]],   |
| Owners | [[Espresso]],  [[Snap]],  [[Knots]],  ~~[[Devtools Observe\|Observe]]~~,   |
| Pinned | [[Harbor Runbook Egress Stall]],  [[Harbor Account Northwind]],   |
| ... | [[Harbor Integration Cloudflare]],  [[Harbor Integration Okta]],  [[Harbor Integration PagerDuty]],  [[Harbor Integration S3]],  [[Harbor Integration Stripe]],   |

# Harbor Integrations
The systems outside Harbor that a request touches on its way through — five integrations, each with its own page.

| Integration | Direction | Owner | What it does for a request |
|---|---|---|---|
| [[Harbor Integration Okta\|Okta]] | inbound | [[Espresso]] | answers the auth lookup; its cache is what an [[Harbor Runbook Auth Storm\|auth storm]] exhausts |
| [[Harbor Integration Stripe\|Stripe]] | outbound | [[Espresso]] | meters quota against the tenant's plan at month end; never on the request path |
| [[Harbor Integration PagerDuty\|PagerDuty]] | outbound | ~~[[Devtools Observe\|Observe]]~~ | receives every S1/S2 page from [[HRUN\|Harbor Runbooks]] |
| [[Harbor Integration Cloudflare\|Cloudflare]] | inbound | [[Knots]] | terminates TLS ahead of the ~~[[Harbor Hops\|handshake hop]]~~ for tenants that front through it |
| [[Harbor Integration S3\|S3]] | outbound | [[Snap]] | where payload assembly fetches large attachments; the 60 ms budget is mostly this |

## Overview

**Two integrations are on the request path and three are not, and the runbooks only ever mention the two.** Okta and Cloudflare can make a request slow or fail; Stripe, PagerDuty and S3 (for small payloads) only ever run beside it. That split is what the *Direction* column is really recording.

## Why this page is an example
The five pages rostered here are this folder's own children, which the spine could carry — but the spine is already six rows of structure, and a roster with a sentence per member would not fit a masthead. So the children move below the H1 as the heart, written by hand, and the `...` above stays empty on purpose: the catch-all omits any child the page links in its body. Ruled legal by Dan 2026-08-29; specified at [[DAS heart]] § Roster.
