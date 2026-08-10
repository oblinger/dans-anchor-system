---
description: "S2 — rebuild the route index from the source of truth"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Rebuild Index](hook://p/Harbor%20Runbook%20Rebuild%20Index)
# Harbor Runbook — Rebuild Index
S2 — rebuild the route index from the source of truth

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Recovery action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
