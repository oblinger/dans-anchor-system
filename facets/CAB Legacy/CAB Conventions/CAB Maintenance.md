---
description: Validation checklist — what an anchor should look like at rest
---
# CAB Maintenance

The at-rest validation checklist for an anchor — what an inspector confirms to certify the anchor is properly wired.

Checklist for validating an anchor is properly set up:

- **ANCHOR PAGE** — Ensure all documentation is correctly linked from the anchor page
- **ROADMAP** — Contains only high-level descriptions, not detailed content
- **LINK TABLE** — All rows populated with valid links
- **slug INDEX** — If anchor has slug, verify it's in the slug index table

# BRIEF

- **This file is the at-rest validation checklist** for any anchor — the conditions an inspector confirms to certify the anchor is properly wired. Add a checklist item only when it is a property that must hold once setup is complete.
- **NOT for setup procedure / how-to** — flow-of-work (rewire, tidy, scan) lives in the corresponding skill runbooks (`/rewire`, `/tidy`, `/lint`, etc.). This page describes the end state, not the steps.
- **Inclusion test** — a bullet belongs here only if it is (1) checkable by inspection, (2) applies to every anchor that has the relevant trait, and (3) is not already implied by a more specific CAB facet spec (Backlog, Architecture, Rules, etc.).
- **Bullet shape** — `**ALL CAPS LABEL** — one-sentence assertion about the at-rest condition`. Keep each bullet a single condition; do not pack multi-step procedure into one row.
- **Load-bearing** — this page is cited by audit/lint skills; reordering or renaming the labels can desynchronize tooling. Add to the bottom of the list rather than reshuffling existing rows.
- **Trait-conditional bullets** state the condition gate** explicitly ("If anchor has slug, ..."), so a checklist consumer can skip rows that don't apply to a given anchor's traits.
