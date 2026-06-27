---
description: Common Skill Example — reference anchor — a fully-wired example of a CAB skill anchor
---
# CSE — Common Skill Example

A self-contained reference anchor demonstrating the canonical CAB skill-trait anchor structure — sibling to [[CAE]] for the Code trait.

| -[[CSE]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [CSE](hook://p/CSE)<br>: Common Skill Example — reference anchor — a fully-wired example of a CAB skill anchor |
| --- | --- |
| Skill | [[CSE/SKILL\|SKILL.md]],  [[SKL CSE\|User Docs]],   |
| ~~[[CSE Plan\|Plan]]~~ | [[CSE PRD\|PRD]],  [[CSE Backlog\|Backlog]],  [[CSE Features\|Features]],  ~~[[CSE Triage\|Triage]]~~,   |
| Research | — |



## Overview

CSE is the **Common Skill Example** — a self-contained reference anchor demonstrating the canonical CAB skill-anchor structure. Companion to [[CAE]] (the general anchor example).

Where CAE shows a Code-trait anchor — module docs, code repo, dev dispatch — CSE shows a Skill-trait anchor: `SKILL.md` at the root *is* the code, user docs live in the parallel SKL tree, and the Plan folder holds design docs and feature specs for changes to the skill.

CAE shows what an anchor looks like in general. CSE shows what an anchor looks like *when it is also a skill*.



## Structure

```
CSE/                                        ← anchor root (slug: CSE, trait: skill)
├── SKILL.md                                the skill itself — agent-loaded entry point
├── .anchor                                 anchor config
├── CSE.md                                  anchor page — this file
├── cse-demo.md                             example action file (kebab-case)
└── CSE Docs/
    └── CSE Plan/
        ├── CSE Plan.md                     plan dispatch
        ├── CSE PRD.md                      product requirements (the design of the skill)
        ├── CSE Backlog.md                  deferred work
        ├── CSE Triage.md                   triage inbox (agent-owned)
        └── CSE Features/
            └── F001 — Example Feature.md   feature design doc (changes to the skill)
```



## How a skill anchor differs from a general anchor

A skill anchor follows the same CAB structure as any other anchor — same `Docs/Plan/Features/` hierarchy, same dispatch tables, same feature-doc convention. Two structural deltas:

- **No code repo, no Dev dispatch.** `SKILL.md` *is* the code. The skill's action files (`cse-demo.md` etc.) live alongside it at the anchor root in kebab-case. There is no separate `Code/` directory and no `{NAME} Docs/{NAME} Dev/` doc folder.
- **No User dispatch — user docs live in SKL.** User-facing documentation for the skill lives in the **SKL user-docs tree** at `skills/SKL User Docs/SKL Skills/SKL <Name>.md`, not under `{NAME} Docs/{NAME} User/`. This keeps every skill's user docs together in one place at the skills repo root, regardless of which anchor they describe.

The dispatch table's first row reflects both deltas: a `Skill` row carries the two surfaces — the skill spec (`SKILL.md`) and the user-facing doc (`SKL CSE`) — instead of separate Dev / User rows. This is the canonical first-row shape for a skill anchor.



## Feature docs live with the skill

Design discussions and feature specs for changes to a skill live in *that skill's* `{NAME} Features/` folder, not in a global features pile. As a skill evolves over time, its full design history accrues to it — opening the skill folder shows everything ever proposed or shipped for that skill.

Cross-skill features (touching 2+ skills) and meta-anchor features (about SKA itself) still belong in the SKA-level Features folder. Skill-specific features belong with the skill.

F-numbers stay anchor-wide (per the [[SKA feature]] skill's convention) — `F042` is unique within an anchor regardless of which folder its doc lives in. The folder is a *location*, not a *namespace*.



## About the content

CSE describes a fictional skill `/cse` with one example action `/cse demo`. The skill itself is illustrative; what matters is the shape of the files. PRD, Plan dispatch, Backlog, Triage, and the example feature doc all show what a real skill anchor looks like in working form.

# BRIEF

- **This anchor is a reference exemplar, not a working skill.** CSE exists to *show* the canonical CAB skill-trait anchor shape; the `/cse` skill and its `demo` action are illustrative placeholders. Don't wire CSE into real workflows or treat it as a dependency.
- **Scope is the Skill trait only.** CSE demonstrates skill-anchor structure (SKILL.md as code, action files at root, SKL user-docs, Plan folder for design). Code-trait examples belong in [[CAE]]; cross-trait or generic CAB content belongs in [[CAB]] facets, not here.
- **Inclusion test for changes.** Add or change content here only when it makes the example more faithful to the canonical Skill-trait shape per current CAB specs. If a change would teach a new general rule rather than illustrate one, it belongs in the relevant CAB facet (then reflect it here).
- **Keep structure aligned with live CAB specs.** When CAB Skill-trait conventions change (dispatch row shape, folder layout, SKL location), update CSE in the same pass — a stale exemplar misleads readers more than a missing one.
- **Dispatch first row is load-bearing.** The `Skill` row with `[[CSE/SKILL|SKILL.md]]` + `[[SKL CSE|User Docs]]` is the canonical first-row shape for skill anchors; don't split into separate Dev/User rows or rename — other docs cite this as the reference.
- **F-numbers are anchor-wide, zero-padded.** `F001`...`F999` unique across the whole CSE anchor regardless of which Features subfolder the doc sits in. The folder is location, not namespace.
- **Don't pile cross-anchor or meta-SKA content here.** Meta-anchor features (about SKA itself) and cross-skill features belong at the SKA-level Features folder, not in CSE.
