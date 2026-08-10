---
description: "S1 — auth lookups saturating; cache cold after a deploy"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Auth Storm](hook://p/Harbor%20Runbook%20Auth%20Storm)
# Harbor Runbook — Auth Storm
S1 — auth lookups saturating; cache cold after a deploy

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Incident action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
