---
description: "example discipline — a cross-cutting spec"
---
# FEX Retention
The Retention discipline — the cross-cutting rule for how long snapshot bundles live before they are swept.

| -[[FEX Retention]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [FEX Retention](hook://p/FEX%20Retention)<br>: example discipline — a cross-cutting spec |
| --- | --- |
| Related | [[FEX]],  [[FCT Doc\|Document facets]],   |

Retention governs the lifetime of snapshot bundles so the `snapshots/` directory does not grow without bound. The default policy keeps every bundle for 30 days, then keeps one bundle per month indefinitely as a long-tail archive. Any bundle the user pins is exempt from the sweep. The discipline is read by the snapshot skill at capture time and by a periodic sweep that prunes expired bundles — both consult the same rule so the two never disagree.
