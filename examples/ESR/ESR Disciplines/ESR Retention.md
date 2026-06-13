---
description: "how long snapshot bundles are kept before they are swept"
---

# ESR Retention
The Retention discipline — the cross-cutting rule for how long snapshot bundles live before they are swept.

| -[[ESR Retention]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[ESR]] → [[ESR Disciplines]] → [ESR Retention](hook://p/ESR%20Retention)<br>: example cross-cutting discipline spec |
| --- | --- |
| Related | [[ESR Disciplines]] (parent section),  [[ESR Snapshot]] (the skill it governs),   |

Retention governs the lifetime of snapshot bundles so the `snapshots/` directory does not grow without bound. The default policy keeps every bundle for 30 days, then keeps one bundle per month indefinitely as a long-tail archive. Any bundle the user pins is exempt from the sweep. The discipline is read by the snapshot skill at capture time and by a periodic sweep that prunes expired bundles — both consult the same rule so the two never disagree.
