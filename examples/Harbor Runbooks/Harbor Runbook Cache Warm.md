---
description: "S4 — pre-warm the auth cache ahead of a deploy"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Cache Warm](hook://p/Harbor%20Runbook%20Cache%20Warm)
# Harbor Runbook — Cache Warm
S4 — pre-warm the auth cache ahead of a deploy

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Routine action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
