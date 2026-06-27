---
description: "The minimal-facet capsule — the leanest complete file set for a CAB facet, with a live worked instance. Lazy, no empty stubs."
---

# CAE Minimal Facet

| -[[CAE Minimal Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Minimal Facet](hook://p/CAE%20Minimal%20Facet)<br>: the leanest complete file set for a facet, with a live instance |
| --- | --- |
| Anchor | [[CAE]] (reference anchor) |
| Related | [[CAE Minimal Skill]],  [[DSC Dispatch Table]] (the live instance),  [[CAB Facets]] |

The **minimal-facet capsule**: the smallest file set that fully captures a facet *and its design thinking*, with **nothing empty**. Every file below exists only when it carries real content — the structure is uniform (you always know where a piece *would* go), but a piece that has nothing to say is simply absent, not a stub. This is the antidote to the legacy dozen-doc scaffold (see [[CAB Dispatch Table Design]] § Standing decisions).

## The capsule

| File | Role | When it exists |
|---|---|---|
| `{Facet}.md` | **Spec** — *what* the facet is (the form, the rules). Carries the masthead + (if it enumerates anything) a member zone. | Always. |
| `{Facet} Design.md` | **Design** — *why* it's this way: standing decisions (decided X / considered Y / rejected because Z) + an index of the feature docs that shaped it. | Lazily — created the moment the first real decision lands. |
| (shared) `{Anchor} Features/F<n> …` | **Features** — the chronological design detail. Live in the anchor's shared Features pile; the Design doc **links** them, never copies. | Already exist from `/feature`. |

**Not in the capsule:** no Backlog, no UX, no PRD/principles/architecture stubs. A facet is a spec, not a project. If a facet ever genuinely needs a backlog, it has outgrown "facet" and should be reconsidered.

The Design doc is the *synthesis* (standing decisions, one place to look); the feature docs are the *detail* (chronological, per-decision). Same synthesis-vs-detail split as [[FCT Brief]] — linking, not duplication ([[atlas]] § routing-not-duplication is the same principle).

## Live instance — [[DSC Dispatch Table]]

The Dispatch Table facet is the worked example. Click through to see the capsule rendered:

| Piece | Where |
|---|---|
| Spec | [[DSC Dispatch Table]] — masthead (Anchor / Design / Related) + a member zone (its four live examples) |
| Design | [[CAB Dispatch Table Design]] — five standing decisions + the F155 / F156 index |
| Features | [[F155 — Dispatch-table structure spec + CAE worked examples\|F155]], [[F156 — Dispatch-table rollout pilot + Dispatch Table anchor promotion\|F156]] (linked from the Design doc) |

That's the whole facet: **two files** + links to shared features. No stubs.
