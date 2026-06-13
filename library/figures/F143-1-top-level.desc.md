# F143-1 — Key system parts (top-level)
description:: Stated intent for `F143-1-top-level.svg`. Maintained alongside the SVG by `/viz diagram`; rewritten as the user clarifies (never appended).

## What it conveys

Single figure that names **Dan's Anchor System** and the **four kinds of system parts** the user organizes work around — **Skills, Facets, Disciplines, Rulesets** — and the gist of how they relate. Targets a first-time reader of `skills.md` who needs to grasp the system structure at a glance. Not exhaustive — that's what figures 2–4 are for.

Importance order the user stated (not necessarily the visual hierarchy):
1. Skills (most important)
2. Facets
3. Rules
4. Disciplines

## Layout

- **Top row** of three peers, left → right: **Skills** (blue), **Facets** (green, deliberately shorter), **Disciplines** (yellow).
- **Bottom band** spanning full width: **Rulesets** (orange, thin).
- **Facets is deliberately shorter** than Skills + Disciplines — that is the geometric trick that lets the `modifies` arrow from Disciplines pass over the top of Facets without tunneling or bending. Do not equalize Facets height with Skills/Disciplines.
- Skills + Disciplines are matched-size siblings (same width 180px, same height 160px). Facets is wider (260px) and shorter (125px).
- Rulesets band is thin (48px tall) — a horizontal stripe, not a fourth peer-shaped box. "Rulesets" words on the left, *directives and constraints* alongside on the right (parallel, single row). The thinness is editorial: a ruleset is a different *kind* of thing, and the band shape signals that visually.

## Per-element content

Each top box has three rows: sans bold title, italic-Palatino script subtitle, small sans descriptor.

| Box | Sans title (22pt) | Script subtitle (32pt italic Palatino) | Small descriptor (11pt) |
|---|---|---|---|
| Skills | Skills | *verbs* | Actions taken |
| Facets | Facets | *nouns* | Docs created |
| Disciplines | Disciplines | *adjectives* | Systematic behaviors |

The Rulesets band is a single row: `Rulesets` (sans bold, 22pt) on the left + *directives and constraints* (italic Palatino, 22pt) alongside on the right.

Horizontal alignment is load-bearing:
- All three **script subtitles** sit on the same y-baseline (currently y=183) — they read as a single typographic gesture.
- All three **small descriptors** sit on the same y-baseline (currently y=215).

The script font (italic Palatino, "script with serifs") sets *verbs / nouns / adjectives / directives and constraints* apart from the sans-serif body text — those four words are the figure's linguistic spine.

## Arrows

| Arrow | Label | Style |
|---|---|---|
| Skills → Facets | *creates* | italic blue, 13pt |
| Disciplines → Skills (across the top, over the shorter Facets) | *modifies* | italic blue, 13pt |
| Disciplines → Facets (short, right side) | unlabeled | — |
| Rules → Skills | unlabeled | — |
| Rules → Facets | unlabeled | — |
| Rules → Disciplines | unlabeled | — |

Style: thin stroke (2pt), small arrowhead marker (5×5) — more stylized than the viz-svg default. **Smaller / more stylized** is intentional; do not revert to the heavier default arrows.

The unlabeled arrows convey direction + relationship through context. The two labeled arrows (`creates`, `modifies`) are the ones whose meaning is not obvious from direction alone.

## What it does NOT contain

These are deliberate omissions — as load-bearing as the inclusions:

- **No example lists** in any box. Earlier versions had `/design · /feature · /viz · /crank` in Skills, `R-prd · R-testing · R-markdown · R-diagram` in Rules, etc. The user removed them: a reader who does not know what those identifiers are gets no value from them, and a reader who already knows doesn't need the figure.
- **No caption** at the bottom. The title at the top is the only meta-text.
- **No labels on the four obvious arrows** (Disciplines → Facets + the three Rules arrows). Direction is enough.
- **No category breakdowns or sub-clusters**. Those are for figures 2–4.

## Conceptual nuances the agent should remember

- **Skills produce Facets** is the primary relationship (`creates` arrow).
- **Disciplines are cross-cutting** — "halfway between facets and skills." They apply across many skills AND many facets. Hence the `modifies` arrow spans the top and points at Skills (with the symmetric short `Disciplines → Facets` arrow on the right).
- **Rules apply directly to Skills, Facets, AND Disciplines** — most rules apply to a skill or a facet; a minority apply to a discipline. Earlier drafts had Rules → Disciplines only, which understated the truth and was wrong.
- **Disciplines are not rules**, but disciplines have rules. The `Rules` band underneath all three top boxes captures this — rules constrain each of the three peers individually, not via disciplines.
- **The figure is intentionally simple.** Subjective rule: if a reader needs in-vault context to understand it, cut it.

## Audit posture

- **R-c4-01 (every arrow has a label)** is deliberately relaxed — 4 of 6 arrows are unlabeled per the simplicity discipline. This is an editorial decision, not a missing label.
- **R-tufte-data-ink-01 (sibling box-sizing consistency)**: Skills + Disciplines are matched; Facets is deliberately different (shorter + wider). The size variation **encodes meaning** (Facets shorter is the geometric trick for `modifies`) — Tufte's rule allows size that encodes meaning, so this is in spec.
- **R-sugiyama-03 (monotone flow direction)**: the figure is a relationship graph, not a flow diagram — relaxed by intent.
- All **R-diagram-geometry** rules (the six hard-fails) pass. No overlap, every arrow endpoint anchored, no tunneling, text fits, label-target unambiguous, no label-label collision.
- All **R-svg-hygiene** rules pass: validates as XML, stable IDs on every element, no orphan `<defs>` entries.
- Net: 21 of 22 strict pass + 1 deliberately relaxed (R-c4-01).

## Title

`Dan's Anchor System` — sans bold, 22pt, centered above the figure. The only meta-text on the canvas. (The figure names the system; the bottom band is labeled **Rulesets**.)

## Color palette (locked across figures 1–4 in this family)

- `#bac8ff` (pale blue) — Skills
- `#ebfbee` (pale green) — Facets
- `#fff9db` (pale yellow) — Disciplines
- `#ffe8cc` (pale orange) — Rules
- `#1e1e1e` (near-black) — text, box strokes, arrows
- `#1971c2` (italic blue) — arrow labels

Same color → same meaning across figures 2, 3, 4. Do not reassign.
