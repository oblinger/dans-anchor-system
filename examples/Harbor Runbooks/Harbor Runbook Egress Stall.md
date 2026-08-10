---
description: "S1 — traffic stopped at the egress hop; open with the rollback"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Egress Stall](hook://p/Harbor%20Runbook%20Egress%20Stall)
# Harbor Runbook — Egress Stall
S1 — traffic stopped at the egress hop; open with the rollback

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Incident action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
