---
description: "The minimal-skill capsule — the leanest complete file set for a skill, keeping design thinking out of the published repo. Lazy, no empty stubs."
---

# CAE Minimal Skill

| -[[CAE Minimal Skill]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Minimal Skill](hook://p/CAE%20Minimal%20Skill)<br>: the leanest complete file set for a skill, with a live instance |
| --- | --- |
| Anchor | [[CAE]] (reference anchor) |
| Related | [[CAE Minimal Facet]],  [[SKL]],  [[granularity]],   |

The **minimal-skill capsule**: the smallest file set that fully captures a skill *and its design thinking*, with **nothing empty**. Same lazy discipline as [[CAE Minimal Facet]] — uniform structure, files exist only when they carry content. The one structural difference from a facet: a skill's **spec is its runbook, and the runbook lives in the published repo** ([[SKL]] / `ob-skills` on GitHub), so the design thinking is kept *out* of the published repo and lives in the parallel SKA design tree.

## The capsule

| File | Where it lives | Role | When it exists |
|---|---|---|---|
| `{name}/SKILL.md` | **published repo** (`~/.claude/skills/`, symlinked from [[SKL]]) | **Spec / runbook** — *what* the skill does + how to run it. | Always. |
| `{Name}.md` | **SKA tree** (e.g. `Utility/SKA {name}/`) | **Design-home anchor page** — masthead: Spec (→ the runbook) / Design / Features. | Always (the design home). |
| `{Name} Design.md` | SKA tree | **Design** — *why*: standing decisions + index of the feature docs that shaped it. | Lazily — when the first real decision lands. |
| `{Name} Story.md` | SKA tree | one representative **user story**, if it illuminates intent. | Optional, only when it adds something. |
| (shared) `{Anchor} Features/F<n> …` | SKA tree | **Features** — chronological detail; the Design doc **links** them, never copies. | Already exist from `/feature`. |

**Not in the capsule:** no Backlog, no UX, no prd/principles/architecture stubs. The published runbook stays clean (spec + any helper code only); all rationale lives in the SKA design tree.

## Why the split matters

The published `SKILL.md` is consumed by anyone who installs the skill — it must stay a clean runbook. The *why we built it this way* (rejected alternatives, standing decisions) would be noise there, but is exactly what keeps the system from relitigating itself. So it lives one tree over, in `SKA {name}/`, linked from the runbook's `Related`. Single source of truth ([[atlas]] § routing-not-duplication): the Design doc references the runbook; it never restates it.

## Live instance

A simple single-runbook skill such as [[snip]] is the shape: its spec is `skills/snip/SKILL.md` (published); its design home is `SKA snip` in the SKA tree, where a `SKA snip Design.md` is added the first time a real decision needs recording. Most skills are at the "spec only" stage today — the Design doc is the lazy piece the per-skill migration fills in *as decisions happen*, not up front. The facet side is already fully worked: see [[CAE Minimal Facet]] → [[DSC Dispatch Table]].
