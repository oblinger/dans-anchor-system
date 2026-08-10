---
description: "S2 — a leaf certificate inside 72 hours of expiry"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Cert Expiry](hook://p/Harbor%20Runbook%20Cert%20Expiry)
# Harbor Runbook — Cert Expiry
S2 — a leaf certificate inside 72 hours of expiry

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Incident action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
