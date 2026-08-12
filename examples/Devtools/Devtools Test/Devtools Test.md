---
description: "Devtools Test — what decides whether the artifact is allowed to proceed"
---

| -[[Devtools Test]]- | : what decides whether the artifact is allowed to proceed<br>→ [[DAS]] → [[examples]] → [DVT](hook://DVT) → [Devtools Test](hook://p/Devtools%20Test)  |
| --- | --- |
| Related | [[Devtools]] (parent),  [[DAS spine]],  [[FEX Spine Examples]], |
| [[Devtools Unit\|Unit]]  | fast, hermetic, run on every save; the only tier permitted to block the watch loop |
| [[Devtools E2E\|E2E]]  | the artifact exercised as a user would; slow, and the tier that catches wiring rather than logic |
| [[Devtools Coverage\|Coverage]]  | the ratchet — compares against the previous release and refuses a decrease |
| [[Devtools Fuzz\|Fuzz]]  | runs continuously off the critical path; findings become Unit cases rather than gates |
| ... |  |

# Devtools Test
What decides whether the artifact is allowed to proceed — four tools, and the gate they exist to hold.

Coverage may not fall below the previous release — the one gate here that is a ratchet rather than a threshold.

Reached from [[Devtools]] as a `+`-marked group row: the members previewed there are pinned by hand, and this page is where the full set lives. That split is the whole point of the two-level shape — a preview that drifts is a cosmetic problem, while a missing child is a real one, which is why the catch-all above is kept even though every tool is named.
