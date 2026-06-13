---
description: "example doc facet — an actual manifest"
---
# FEX Manifest
An actual `manifest.txt` — the record the [[FEX Snapshot|Snapshot]] skill writes beside every bundle so a later restore knows exactly what state it captured.

| -[[FEX Manifest]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[FEX Repo]] → [FEX Manifest](hook://p/FEX%20Manifest)<br>: example doc facet — an actual manifest |
| --- | --- |
| Related | [[FEX Repo]],  [[FEX Snapshot\|Snapshot]] (writes it),  [[FEX Retention\|Retention]] (expires it), |

The literal file `snapshots/2026-06-13-0300/manifest.txt`:

```
label:     2026-06-13-0300
commit:    a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
branch:    main
created:   2026-06-13T03:00:00Z
tracked:   1428
untracked: 7
ignored:   excluded
bytes:     53221904
restore:   snapshot restore 2026-06-13-0300
```

That is the whole facet — there is no prose body, because a manifest *is* the file, not a description of one. One `key: value` per line; keys lower-case; any path is bundle-relative; `label` / `commit` / `branch` / `created` are always present.
