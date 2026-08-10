---
description: "S2 — drain and replay the dead-letter queue after an incident"
---
:>> [[DAS]] → [[examples]] → [HRUN](hook://HRUN) → [Harbor Runbook Replay Queue](hook://p/Harbor%20Runbook%20Replay%20Queue)
# Harbor Runbook — Replay Queue
S2 — drain and replay the dead-letter queue after an incident

| Step | Action | Stop if |
|---|---|---|
| 1 | Confirm the symptom against [[Harbor Latency Budget]] | the hop is inside budget |
| 2 | Take the Recovery action for this class | a second operator is already engaged |
| 3 | Record the outcome in [[Harbor Releases]] if a release caused it | no release in the window |
