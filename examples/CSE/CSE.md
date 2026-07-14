---
description: Common Skill Example — reference anchor — a fully-wired example of a DAS skill anchor
---
# CSE — Common Skill Example

A self-contained reference anchor demonstrating the canonical DAS skill-trait anchor structure — sibling to [[HBR]] for the Code trait.

| -[[CSE]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[examples]] → [CSE](hook://p/CSE)<br>: Common Skill Example — reference anchor — a fully-wired example of a DAS skill anchor |
| --- | --- |
| Skill | [[CSE/SKILL\|SKILL.md]],  [[SKL CSE\|User Docs]],   |
| [[CSE Design\|Design]] | [[CSE PRD\|PRD]],   |
| [[CSE Track\|Track]] | [[CSE Backlog\|Backlog]],  [[CSE Features\|Features]],  [[CSE queries\|queries]],   |



## Overview

CSE is the **Common Skill Example** — a self-contained reference anchor demonstrating the canonical DAS skill-anchor structure. Companion to [[HBR]] (the general anchor example).

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
        ├── CSE queries.md                  queries inbox (agent-owned)
        └── CSE Features/
            └── F001 — Example Feature.md   feature design doc (changes to the skill)
```



## How a skill anchor differs from a general anchor

A skill anchor follows the same DAS structure as any other anchor — same `Docs/Plan/Features/` hierarchy, same dispatch tables, same feature-doc convention. Two structural deltas:

- **No code repo, no Dev dispatch.** `SKILL.md` *is* the code. The skill's action files (`cse-demo.md` etc.) live alongside it at the anchor root in kebab-case. There is no separate `Code/` directory and no `{slug} Docs/{slug} Dev/` doc folder.
- **No User dispatch — user docs live in the DAS docs tree.** User-facing documentation for the skill lives at `docs/<domain>/DAS <Name>.md` at the repo root, not under `{slug} Docs/{slug} User/`. This keeps every skill's user docs together in one place, regardless of which anchor they describe.

The dispatch table's first row reflects both deltas: a `skill` row carries the two surfaces — the skill spec (`SKILL.md`) and the user-facing doc (`DAS CSE`) — instead of separate Dev / User rows. This is the canonical first-row shape for a skill anchor.



## Feature docs live with the skill

Design discussions and feature specs for changes to a skill live in *that skill's* `{slug} Features/` folder, not in a global features pile. As a skill evolves over time, its full design history accrues to it — opening the skill folder shows everything ever proposed or shipped for that skill.

Cross-skill features (touching 2+ skills) and meta-anchor features (about SKA itself) still belong in the SKA-level Features folder. Skill-specific features belong with the skill.

F-numbers stay anchor-wide and zero-padded triple-digit (`F001`…`F999`, per the [[SKA feature]] skill's convention) — `F042` is unique within an anchor regardless of which folder its doc lives in. The folder is a *location*, not a *namespace*.



## About the content

CSE describes a fictional skill `/cse` with one example action `/cse demo`. The skill itself is illustrative; what matters is the shape of the files. PRD, Plan dispatch, Backlog, Queries, and the example feature doc all show what a real skill anchor looks like in working form.

# BRIEF

*(Maintainer note — exemplar-specific cautions for whoever edits this anchor. CSE follows the CAB Skill-trait specs; the normative shapes live there, not here.)*

- **Not a working skill** — the `/cse` skill and its `demo` action are illustrative placeholders; don't wire CSE into real workflows or treat it as a dependency.
- **Inclusion test for changes** — add or change content here only when it makes the example more faithful to the canonical Skill-trait shape per current CAB specs. Code-trait examples belong in [[HBR]]; a change that would teach a new general rule (or cross-trait / generic CAB content) belongs in the relevant ~~[[DAS]]~~ facet, then gets reflected here.
- **Keep aligned with live CAB specs** — when Skill-trait conventions change (dispatch row shape, folder layout, SKL location), update CSE in the same pass; a stale exemplar misleads readers more than a missing one.
- **The dispatch first row is cited as the reference** — other docs point at the `skill` row (§ How a skill anchor differs) as the canonical first-row shape for skill anchors; don't split it into separate Dev/User rows or rename it.
