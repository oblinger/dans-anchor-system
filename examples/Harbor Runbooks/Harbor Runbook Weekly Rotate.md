---
description: "S4 — rotate signing keys, Thursdays in the maintenance window"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Weekly Rotate](hook://p/Harbor%20Runbook%20Weekly%20Rotate)
# Harbor Runbook — Weekly Rotate
S4 — rotate signing keys, Thursdays in the maintenance window

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Routine action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
