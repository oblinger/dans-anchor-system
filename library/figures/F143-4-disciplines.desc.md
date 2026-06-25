# F143-4 — Disciplines detail (grouped by what they govern)

description:: Stated intent for `F143-4-disciplines.svg`. Maintained alongside the `.d2` source by `/viz diagram`; rewritten as the user clarifies (never appended).

## What it conveys

The **disciplines** — cross-cutting behaviors the agent reads — grouped by *what they govern*, so a reader drilling into the Disciplines peer (F143-1) sees that disciplines partition into a few domains of concern. Selective, not exhaustive.

## Layout

Four horizontal cluster bands, left → right:

- **Writing form**: markdown · ask-format · technical-answer · dated-entry-stream — how the agent writes.
- **Workflow & verification**: verification · progressive-disclosure — how work is validated and revealed.
- **Anchor organization**: anchor-dag · file-association · granularity · Linked Mode — how the folder graph is structured.
- **Operation**: role · mode — how the agent operates (role-pilot, drive modes).

No connector arrows — disciplines are cross-cutting peers, not a sequence; the grouping itself is the content.

## Color

All cluster zones use the **Disciplines** color `#fff9db` (pale yellow), locked across figures 1–4. Same color → same meaning: everything here is a *discipline*.

## What it does NOT contain

- **Not every discipline file** — names the recognizable members of each `disciplines/` subfolder (DSC authoring / DSC work / DSC anchor / DSC operation).
- **No skill / facet / ruleset content** — those are figures 2 / 3 (and the rulesets band in figure 1).
- **No rules** — disciplines have rules, but the rules themselves are the rulesets band in F143-1, not shown here.

## Source

`F143-4-disciplines.d2` (D2). Regenerate exports with `d2 F143-4-disciplines.d2 F143-4-disciplines.svg` and `d2 F143-4-disciplines.d2 F143-4-disciplines.png`.
