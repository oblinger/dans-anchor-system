---
description: "the Pin facet definition"
---

| -[[FEX Pin]]- | : the Pin facet definition<br>→ [[DAS]] → [[FEX]] → [[FEX Repo]] → [FEX Pin](hook://p/FEX%20Pin)  |
| --- | --- |
| Anchor | [[FEX Repo]] (parent) |
| Related |  |
| [[FEX Retention]]  | honors it |
| [[FEX Bundle]]  | what it protects |
| [[DAS Facet]]  | the facet spec |
| ... | [[FEX Manifest]],  [[FEX Snapshot]],  [[R-fex-manifest]],   |

# FEX Pin
The Pin facet — a marker that keeps one snapshot bundle forever. A worked example of a **single-file, cardinality-many** facet (the filename is the key).

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

# RULESET R-fex-pin
include::
where:: `pins/*`
description:: The rules every pin marker must satisfy — the filename is the bundle label, and it names a real bundle.

This inline ruleset is the **embedded** form — the rules live in the facet page itself; contrast the linked-sibling ruleset of [[FEX Manifest]].

### RULE R-fex-pin-01 — filename is a valid bundle label
description:: A pin file's basename must match the bundle-label format YYYY-MM-DD-HHMM with no extension; the filename is the key that identifies which bundle is pinned.
when:: write:*
if:: `re.search(r'^\d{4}-\d{2}-\d{2}-\d{4}$', file.name) is None`
The pin filename is not a valid bundle label — it must match `YYYY-MM-DD-HHMM` with no extension. Rename it to exactly the label of the bundle it protects.

**Why:** the filename IS the key — the label it pins; a malformed name pins nothing.

### RULE R-fex-pin-02 — names an existing bundle
description:: A pin's filename must match a real bundle directory under snapshots/; a pin for an absent bundle is a dangling marker the retention sweep cannot honor.
if:: `not (anchor.root / 'snapshots' / file.name).is_dir()`
The bundle named by this pin does not exist under `snapshots/` — this pin is dangling and the retention sweep cannot honor it. Remove the pin file or restore the missing bundle.

**Why:** a pin for an absent bundle is a dangling marker the retention sweep can't honor.
