# F143-2 — Skills detail (the major clusters)

description:: Stated intent for `F143-2-skills.svg`. Maintained alongside the `.d2` source by `/viz diagram`; rewritten as the user clarifies (never appended).

## What it conveys

The major **skill clusters**, expressed as pictures rather than a flat list. A reader who has grasped the top-level "three things" (F143-1) drills into Skills here and sees that the dozens of skills organize into a handful of clusters — two of which are *sequences* (loops) and three of which are *bags* of sibling verbs. Selective, not exhaustive — ~5 clusters, ~15 named items.

## Layout

- **Design loop** (left, vertical sequence): PRD → UX → API → Architecture → Testing → Roadmap. The canonical design phases as an ordered flow.
- **Feature flow loop** (bottom, vertical sequence): Designing → Agreed → Implementing → Testing → Done. The workflow-state graph a feature walks.
- **Drive cluster** (mid-right band): crank · land · fortify · triage · query — the outer-loop autonomous-progress operators.
- **Viz cluster** (top-mid band): excalidraw · matplot · diagram — visual-artifact verbs.
- **Search cluster** (top-right band): find · profile · survey — locate / dossier / compare verbs.

Two connector arrows carry the only editorial relationships: **Design loop → Feature flow loop** (*design then build*) and **Drive cluster → Feature flow loop** (*advances* — the drive operators push features through their states).

## Color

All cluster zones use the **Skills** color `#bac8ff` (pale blue), locked across figures 1–4. Same color → same meaning: everything here is a *skill*.

## What it does NOT contain

- **Not every skill.** The repo carries ~60 skill folders; this names the load-bearing clusters only. The catalog below `skills.md` is for exhaustive lookup.
- **No facet / discipline / ruleset content** — those are figures 3 / 4 (and the rulesets band in figure 1).
- **No per-skill descriptions** — the cluster framing is the value; identifiers a reader doesn't know get no caption here.

## Source

`F143-2-skills.d2` (D2). Regenerate exports with `d2 F143-2-skills.d2 F143-2-skills.svg` and `d2 F143-2-skills.d2 F143-2-skills.png`.
