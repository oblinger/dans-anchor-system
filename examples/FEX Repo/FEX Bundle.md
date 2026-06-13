---
description: "the Bundle facet definition"
---
# FEX Bundle
The Bundle facet — one snapshot, captured as a dated directory. A worked example of a **folder-detected, cardinality-many** facet (the facet is a directory, not a file).

| -[[FEX Bundle]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FEX Repo]] → [FEX Bundle](hook://p/FEX%20Bundle)<br>: the Bundle facet definition |
| --- | --- |
| Anchor | [[FEX Repo]] (parent) |
| Related | [[FEX Snapshot]] (creates it),  [[FEX Manifest]] (it carries),  [[FEX Pin]] (protects it),  [[FCT Facet]] (the facet spec), |

## What it is
A single restorable snapshot of the repo, stored as its own directory.

## How it's detected
**Folder-existence** (not a file) — a `snapshots/<label>/` directory, where `<label>` is `YYYY-MM-DD-HHMM`. **Cardinality: many** — a repo accumulates many bundles over time. (This is the case the default file-existence rule does *not* cover; the facet spec overrides detection to "directory exists.")

## Format
A directory named with the dated label, containing the archived working tree plus exactly one [[FEX Manifest|manifest.txt]]. No other required entries.

## Constraints
- The directory name must be a valid `YYYY-MM-DD-HHMM` label.
- Every bundle contains exactly one [[FEX Manifest|manifest.txt]] (co-requirement with the Manifest facet).

## Expected Usage
Created by [[FEX Snapshot|Snapshot]]; pruned by the [[FEX Retention|Retention]] sweep unless [[FEX Pin|pinned]].

## Skills and audits that attach
[[FEX Snapshot]] creates bundles; the retention sweep prunes them; restore reads them.
