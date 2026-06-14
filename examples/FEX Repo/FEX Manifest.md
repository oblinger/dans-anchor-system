---
description: "the Manifest facet definition"
---
# FEX Manifest
The Manifest facet — the fixed key/value record written into every snapshot bundle. A worked example of a **single-file, cardinality-one, fixed-format** facet.

| -[[FEX Manifest]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FEX Repo]] → [FEX Manifest](hook://p/FEX%20Manifest)<br>: the Manifest facet definition |
| --- | --- |
| Anchor | [[FEX Repo]] (parent) |
| Related | [[FEX Snapshot]] (writes it),  [[R-fex-manifest]] (its rules),  [[FEX Bundle]] (carries it),  [[FCT Facet]] (the facet spec), |

## What it is
The single record a snapshot bundle carries so a later restore knows exactly what state it captured.

## How it's detected
File-existence — a `manifest.txt` directly inside a `snapshots/<label>/` bundle. **Cardinality: one** per bundle.

## Format
One `key: value` per line, keys lower-case; required keys `label`, `commit`, `branch`, `created`; any path bundle-relative. A real one — `snapshots/2026-06-13-0300/manifest.txt`:

```
label:     2026-06-13-0300
commit:    a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
branch:    main
created:   2026-06-13T03:00:00Z
tracked:   1428
bytes:     53221904
restore:   snapshot restore 2026-06-13-0300
```

## Constraints
Formalized as the [[R-fex-manifest]] ruleset: one fact per line; required keys present; no absolute paths.

## Expected Usage
Written by [[FEX Snapshot|Snapshot]] at capture; read by restore and by the [[FEX Retention|Retention]] sweep. Removed with its bundle — no tombstone.

## Skills and audits that attach
[[FEX Snapshot]] writes it; `/audit` checks it against [[R-fex-manifest]].

# BRIEF

- **This is the Manifest facet definition** — the `manifest.txt` written into every snapshot bundle. The worked **one-per-anchor** (cardinality-one, single-file) facet example. Its instance rules live in the **linked sibling** [[R-fex-manifest]] (which doubles as [[FCT Ruleset]]'s standalone-ruleset example) — the linked form, contrast the embedded rulesets in [[FEX Pin]] / [[FEX Bundle]].
- **Detection = file-existence** (`manifest.txt` inside `snapshots/<label>/`); **cardinality = one** per bundle. Keep both explicit — they drive how the audit binds.
- **Defines the facet only** — write/read behavior belongs to [[FEX Snapshot]]; don't grow this into a how-to.
