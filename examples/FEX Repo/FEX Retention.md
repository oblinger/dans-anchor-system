---
description: "example discipline — the retention rule"
---
# FEX Retention
The cross-cutting rule for how long a snapshot bundle lives before the sweep removes it.

| -[[FEX Retention]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[FEX Repo]] → [FEX Retention](hook://p/FEX%20Retention)<br>: example discipline — the retention rule |
| --- | --- |
| Related | [[FEX Repo]],  [[FEX Snapshot\|Snapshot]] (reads it),  [[FEX Manifest\|Manifest]], |

A snapshot bundle is retained as follows:

- **First 30 days** — keep every bundle, however many there are.
- **After 30 days** — keep exactly one bundle per calendar month (the earliest in each month); delete the rest.
- **Pinned bundles** — a bundle the user pins with `snapshot pin <label>` never expires, regardless of age.

Both the [[FEX Snapshot|Snapshot]] skill (at capture) and the periodic sweep (at prune) read this one rule, so the two never disagree about which bundles survive. When a bundle is removed, its `manifest.txt` goes with it — there is no tombstone.
