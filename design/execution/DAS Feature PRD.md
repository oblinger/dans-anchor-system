---
description: "product requirements"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[skill-docs]] → [[SKL Drive]] → [[DAS Feature]] → [[DAS Feature Design]]
# Feature PRD

The current skill spec lives at [[feature/SKILL\|SKILL.md]]. User docs live at [[DAS Feature]].

**From:** [[F199 — F-Number Cross-Anchor Collision Guard]]

## Overview

`/feature` manages a feature from idea through design, agreement, implementation, and completion. One design concern has been distilled here from its feature history: cross-anchor F-number collisions.

## Goals

- Catch duplicate feature titles at creation time, not weeks later when a wiki-link silently misfires (F199).

## Non-Goals

- No global vault-wide F-numbering — each anchor keeps a local F-namespace.
- No renaming of existing feature docs to anchor-prefixed names; no auto-fix of historical collisions.

## User Stories

- As the user, when I `/feature` a title that already exists in another anchor, I get one inline heads-up at creation with rename-or-proceed options.

## Key decisions (F199)

- F-numbers are **per-anchor namespaces**; the same `F<n> — Title` filename can recur across anchors. `/feature` runs a creation-time vault grep for a matching H1: zero matches → proceed; cross-anchor match → single inline yes/no (rename vs. proceed-with-qualified-links); same-anchor match → block creation.
- **Wiki-link convention:** within-anchor links to feature docs are bare `[[F<n> — Title]]` (Obsidian proximity resolves them); cross-anchor links must be path-qualified or aliased. Q.md / Triage only link to `[[ANCHOR]]`, never directly across anchors, so they are unaffected.

*(Note: this design predates the F193/D10 move to a single unified SKA-level F-space; the collision guard remains relevant for any remaining per-anchor-tracked project anchors.)*
