---
description: "the format of a repo's `manifest.txt` snapshot record"
---

# ESR Manifest
The Manifest facet — the fixed shape of the `manifest.txt` a snapshot writes beside its bundle.

| -[[ESR Manifest]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[ESR]] → [[ESR Facets]] → [ESR Manifest](hook://p/ESR%20Manifest)<br>: example doc-structural facet spec |
| --- | --- |
| Related | [[ESR Facets]] (parent section),  [[ESR Snapshot]] (the skill that writes it),   |

## What it is

A `manifest.txt` is the small record a snapshot bundle carries so a later restore knows exactly what state it captured. It is a structural facet: a fixed set of key/value lines, one per fact, machine-parseable and human-readable.

## Rules

- **One fact per line** — `key: value`, keys lower-case, no blank lines inside the block.
- **Required keys** — `label`, `commit`, `branch`, `created` (ISO-8601) must all be present.
- **Bundle-relative paths** — any path recorded is relative to the bundle directory, never absolute.
