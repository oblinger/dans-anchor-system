---
description: "the Pin facet definition"
---
# FEX Pin
The Pin facet — a marker that keeps one snapshot bundle forever. A worked example of a **single-file, cardinality-many** facet (the filename is the key).

| -[[FEX Pin]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [[FEX Repo]] → [FEX Pin](hook://p/FEX%20Pin)<br>: the Pin facet definition |
| --- | --- |
| Anchor | [[FEX Repo]] (parent) |
| Related | [[FEX Retention]] (honors it),  [[FEX Bundle]] (what it protects),  [[FCT Facet]] (the facet spec), |

## What it is
A small marker the user drops to keep a bundle forever, regardless of its age.

## How it's detected
File-existence — a file in the repo's `pins/` directory whose **name is the bundle label** it protects (`pins/2026-06-13-0300`). **Cardinality: many** — a repo can pin any number of bundles.

## Format
An empty file, or a one-line reason as its body; the load-bearing part is the **filename** (the label it pins). No frontmatter.

## Constraints
- The label in the filename must match an existing bundle under `snapshots/`.
- At most one pin per bundle (the filename is the key — duplicates are impossible).

## Expected Usage
Created by `snapshot pin <label>`, removed by `snapshot unpin <label>`; read by the [[FEX Retention|Retention]] sweep, which skips any pinned bundle.

## Skills and audits that attach
[[FEX Snapshot]] writes and removes pins; the retention sweep reads them; `/audit` flags a pin whose bundle no longer exists.
