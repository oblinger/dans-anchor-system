---
description: "S4 — monthly review of per-tenant egress quotas"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Quota Review](hook://p/Harbor%20Runbook%20Quota%20Review)
# Harbor Runbook — Quota Review
S4 — monthly review of per-tenant egress quotas

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Routine action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
