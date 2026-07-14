---
description: Subsystem design for the Hygiene group — rules declared once, checked everywhere (Warden on-write + /audit sweeps), and repaired to zero via the 100%-fix discipline.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Hygiene Design](hook://p/DAS%20Hygiene%20Design)
# DAS Hygiene Design — the design of the Hygiene subsystem
Hygiene keeps the vault conformant: rules are declared once in ruleset files, compiled into one corpus, fired on every write and on demand, and every finding is driven to zero — fixed mechanically where possible, repaired by the structural verbs where not.

![[DAS Hygiene Design.svg|3000]]

| **Skills**                       |                                                                                                                     |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| [[DAS Audit\|/audit]]            | Sweep an anchor or doc against the rules and report findings — **audit never fixes** (exception: `/audit q` fixes by default). |
| [[DAS Tidy\|/tidy]]              | Validate + correct one anchor's folder structure against the spec.                                                  |
| [[DAS Rewire\|/rewire]]          | Idempotent structural repair — files linked, dispatch tables wired, skeleton consistent.                            |
| [[DAS Dupes\|/dupes]]            | Duplicate-basename scan → confidence-ranked edit list; user instructs, agent executes.                              |
| [[DAS Slug Scan\|/slug-scan]]    | Discover new slugs, sync the slug index.                                                                            |
| [[DAS Maintain\|/maintain]]      | Standing sync orders — derived files regenerate when their sources change.                                          |
|                                  |                                                                                                                     |
| **Facets**                       |                                                                                                                     |
| [[DAS Ruleset\|Ruleset]]         | The `R-<name>.md` shape — `where::` selector, tier (checked / sampled / stated / tracked), check pattern, why.      |
|                                  |                                                                                                                     |
| **Traits**                       |                                                                                                                     |
| *(per-anchor rule selection)*    | An anchor's `.anchor` `traits:` select which rulesets apply to it; `anchor-base` (incl. `audit-on-write`) rides every anchor. |
|                                  |                                                                                                                     |
| **Library**                      |                                                                                                                     |
| [[Warden]]                       | The rule engine — `warden compile` builds the corpus (`~/.warden`); the daemon fires it on every write (deny + audit-on-write) via the PreToolUse/PostToolUse hooks; python + rust engines held in differential parity. |
| **`audit-plan.py` / `audit-q.py`** | The checker/fixer registries `/audit` and the on-write doc-fire share; `audit-q` renders queues and routes residuals to `B-QFix` rows. |
| **Warden Corpus**                | The blessed fixture corpus — differential ground truth for both engines; re-blessed only on reviewed semantic change. |
| Rulesets                         | [[R-ruleset]] governs the rule files themselves; the catalog spans ~116 rulesets / 550+ rules, authored group-by-group at the F234 profile passes. |

## Overview

Hygiene's contract: **declare once, check everywhere, fix to zero.** A rule is written once as a ruleset entry (`where::` selector + tier + check + why); `warden compile` flattens the catalog into the live corpus; from there it fires on three paths — the **on-write doc-fire** (every Edit/Write, warm in the daemon, mechanical fixes auto-applied), the **PreToolUse deny** (hard vetoes like R-code-mirror and R-pathguard, steering the agent before damage), and the **on-demand `/audit` sweeps** (doc / anchor / q scopes). Findings follow the **100%-fix discipline**: what a fixer can repair mechanically is repaired on the spot; what it can't is filed as a `B-QFix` residual on the owning anchor's backlog and worked to zero — never accumulated. The structural verbs (`/tidy`, `/rewire`) repair shape; the identity verbs (`/dupes`, `/slug-scan`) keep names and slugs unambiguous; `/maintain` keeps derived files from drifting.

Boundaries: **rules are authored by the subsystem that owns the constraint** (the tracking group's R-backlog/R-query landed at its profile pass; each group follows at its own) — Hygiene owns the *engine, the corpus, and the repair verbs*, not the rules' content. **Audit reports, downstream fixes** — `/audit`'s never-fix posture keeps sweeps safe to run anytime; `/audit q` is the deliberate exception. **The queues are Tracking's surface** — audit-q writes findings into Tracking's backlog/queries machinery rather than inventing its own.

## Coordinated examples

Hygiene is illustrated by the live corpus itself — the [[Warden]] anchor's `Warden Corpus/` fixtures are real audited-and-blessed anchors at both the clean and dirty ends of each rule family's range.

## Design record

- [[DAS Audit Design]] · [[DAS Dupes Design]] · [[DAS Maintain Design]] · [[DAS Rewire Design]] · [[DAS Slug Scan Design]] · [[DAS Tidy Design]] — per-verb design docs.
- [[Warden]] — the rule engine's own anchor (design, features, corpus harness).
- **Engine ruling (2026-07-14, T018):** on-write doc-fires resolve the file's real anchor root, so `where::` semantics are identical on-write and on-sweep.
- Shape follows the paradigm [[DAS Tracking Design]] (two-column table per the 2026-07-14 revision; one profile per group, linked off [[DAS]]).
- Figure source: same-basename `DAS Hygiene Design.excalidraw` beside the SVG (user edits in ExcalidrawZ; re-export with `python3 ~/.claude/skills/viz/excalidraw_to_svg.py`).
