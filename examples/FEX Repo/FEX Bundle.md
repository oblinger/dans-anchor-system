---
description: "the Bundle facet definition"
---
# FEX Bundle
The Bundle facet — one snapshot, captured as a dated directory. A worked example of a **folder-detected, cardinality-many** facet (the facet is a directory, not a file).

| -[[FEX Bundle]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [[FEX Repo]] → [FEX Bundle](hook://p/FEX%20Bundle)<br>: the Bundle facet definition |
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

# RULESET R-fex-bundle
include::
where:: `snapshots/*/`
description:: The rules every snapshot bundle directory must satisfy — a dated-label name and exactly one manifest.

### RULE R-fex-bundle-01 — directory named with a valid dated label
description:: A bundle directory under snapshots/ must be named with the YYYY-MM-DD-HHMM label format.
if:: `not re.search(r'^\d{4}-\d{2}-\d{2}-\d{4}$', file.name)`
This bundle directory's name is not a valid dated label — rename it to `YYYY-MM-DD-HHMM` so restore and retention operations can sort it correctly.

**Why:** the label is the bundle's identity and sort key; a malformed name breaks restore + retention ordering.

### RULE R-fex-bundle-02 — contains exactly one manifest
description:: A bundle directory must contain exactly one manifest.txt, co-required with the Manifest facet.
if:: `fex_bundle.manifest_count(file) != 1`
This bundle directory does not contain exactly one `manifest.txt` — add or remove copies until exactly one is present so restore can identify what it is restoring.

**Why:** restore reads the manifest to know what it is restoring; zero or duplicate manifests make the bundle unrestorable or ambiguous.

# BRIEF

- **This is the Bundle facet definition** — a snapshot stored as a dated directory. The worked **folder-detected, many-per-anchor** facet example: detection is **folder-existence**, not the default file-existence.
- **Embedded ruleset** — instance rules are the inline `# RULESET R-fex-bundle`. The non-default (directory) detection is stated explicitly per [[FCT Facet]] R-facet-spec-09.
- **Co-requires [[FEX Manifest]]** — every bundle carries exactly one `manifest.txt`; that co-requirement lives in the ruleset (R-fex-bundle-02), not just prose.
