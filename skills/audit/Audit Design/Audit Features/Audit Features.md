---
description: "Feature design records for the Audit skill — the per-feature design docs that define V2 audit (migrated + renumbered from SKA)."
---
# Audit Features

| -[[Audit Features]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[Audit]] → [[Audit Design]] → [Audit Features](hook://p/Audit%20Features)<br>: feature design records defining V2 audit |
| --- | --- |
| [[F001 — Rule-driven audit engine — resolve, run, judge]] | The engine: resolve applicable rules per target, run mechanical by script, judge the rest by agent; content-hash cached. |
| [[F002 — Audit fix-by-default + Python rule functions]] | Fix-by-default + leveled automation; rules carry Python checks distilled into a merged module. |
| [[F003 — On-write rule hook + test workflow]] | The on-write path: distilled per-hook script, where::-relevance-gated assert + judgment reminder, one test workflow. |
| [[F004 — Audit-on-write hook — closed-off E2E slice]] | First buildable slice: PostToolUse hook auto-fixes mechanical findings, messages subjective ones. Shipped. |
| [[F005 — Doc audit-on-write — vault-wide rollout + safety guard]] | Vault-wide rollout + the alphanumeric-subsequence no-delete safety guard. Shipped, verified across 507 docs. |
| [[F006 — Rule triggering — when the agent attends to rules]] | Discipline for when/how the agent attends to rules at write-time. |
| [[F007 — Backtick all where expressions — parser swap]] | Backtick-wrap every where:: expression; coordinated parser swap gated by a green test suite. |
| [[F008 — audit markdown — markdown hygiene rule library]] | The rules-as-markdown hygiene library + loader/runner. Shipped (v1 core). |
| [[F009 — audit q — Q.md constraint validator]] | Q.md constraint validator with mechanical-fix mode; the three-tier fix flow. |
| [[F010 — audit-q bracket-H2 consistency rules]] | Bracket-to-H2 placement consistency rules (C13-C18). Shipped. |
| [[F011 — audit-q — Designing requires justification]] | Present-time invariant: [Designing] rows must carry a next-action justification (C25). Shipped. |
| [[F012 — audit-q recognize H3-form Open Questions]] | Q-parser recognizes H3-form Open Questions in addition to bullet form. Shipped. |
| [[F013 — audit-q ask.md ↔ feature-doc drift check]] | C35 cross-checks ask.md claimed-pending Qs against the linked feature doc's real Q-state. Shipped. |
| [[F014 — audit-q ask.md coverage + backtick-filepath link]] | ask.md joins Q.md as an audit surface; C36 rewrites backtick-filepaths to links. |
| [[F015 — Audit architecture]] | Architecture-doc validation: diagram-then-table shape + wiki-link integrity. Shipped, auto-run by /architect. |
| [[F016 — Migrate lint to audit]] | Retire /lint into /audit: hard rename, 1:1 subaction map, vault-wide reference sweep. |

## Provenance

These features were authored on the SKA backlog, then relocated here and renumbered to an Audit-local namespace (2026-06-15) so the Audit skill carries a self-contained record of what defines it. Their **tracking** rows remain on the SKA backlog under their original SKA F-numbers (SKA owns tracking for the skills ecosystem, per [[SKA Decisions|D08]]); only the **design docs** moved and renumbered. Old → new:

| SKA (tracking id) | Audit (design doc) |
| --- | --- |
| F161 | [[F001 — Rule-driven audit engine — resolve, run, judge\|F001]] |
| F166 | [[F002 — Audit fix-by-default + Python rule functions\|F002]] |
| F167 | [[F003 — On-write rule hook + test workflow\|F003]] |
| F177 | [[F004 — Audit-on-write hook — closed-off E2E slice\|F004]] |
| F179 | [[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]] |
| F134 | [[F006 — Rule triggering — when the agent attends to rules\|F006]] |
| F172 | [[F007 — Backtick all where expressions — parser swap\|F007]] |
| F081 | [[F008 — audit markdown — markdown hygiene rule library\|F008]] |
| F076 | [[F009 — audit q — Q.md constraint validator\|F009]] |
| F089 | [[F010 — audit-q bracket-H2 consistency rules\|F010]] |
| F106 | [[F011 — audit-q — Designing requires justification\|F011]] |
| F123 | [[F012 — audit-q recognize H3-form Open Questions\|F012]] |
| F124 | [[F013 — audit-q ask.md ↔ feature-doc drift check\|F013]] |
| F126 | [[F014 — audit-q ask.md coverage + backtick-filepath link\|F014]] |
| F092 | [[F015 — Audit architecture\|F015]] |
| F078 | [[F016 — Migrate lint to audit\|F016]] |
