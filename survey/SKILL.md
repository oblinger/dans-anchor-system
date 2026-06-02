---
name: survey
description: Build a multi-dimensional comparison table across many entities — products, companies, software, tools, papers, agent skills. Returns a markdown table + interpretive notes. Use when the user wants a comparison ("survey project management SaaS", "compare CRMs for a 20-person team", "what's the landscape of X"). Includes a meta-survey sub-pattern — lightweight form (survey-of-surveys for deriving dimensions) and full form `/survey meta <noun>` (three composed surveys: sources, dimensions, items; cells annotated for certainty `***★★★*** … ???value???`) for high-stakes comparisons. Supports Quick / Standard / Deep tiers. Output lands in `~/ob/kmr/Topic/Search/Survey/` as `YYYY-MM-DD <survey-name>.md`. NOT for one-entity profiles (use describe) or single-instance lookups (use find).
user_invocable: true
---

# /survey

Build a **multi-dimensional comparison table** over many entities, plus interpretive notes about what's notable, where coverage is sparse, and what follow-up surveys might be useful.

## What loads at invocation (per [[SKA skill-trait search-rules]])

1. **This SKILL.md** — methodology (the runbook below) + meta-survey sub-pattern.
2. `survey/rules/survey.md` — default verb rules (ships with skill); includes RRR output convention and the skill-survey specialized variant.
3. `survey/rules/survey-<noun>.md` — default pair rules with entity knowledge baked in (ships with skill).
4. `SRC rules/survey.md` — user's verb-level overrides (if present).
5. `SRC rules/<noun>.md` — user's noun-level overrides, cross-verb (if present).
6. `SRC rules/survey-<noun>.md` — user's pair-level overrides (most specific, wins all).

Layers 1-3 ship with the skill; 4-6 are user overrides loaded from [[SRC rules]] at `~/ob/kmr/Topic/Search/SRC rules/`.

## Runbook

1. **Define the population** — criteria + inclusion bound. State the bound; don't quietly truncate.
2. **Pick the dimensions** — from the pair-rules file (`survey/rules/survey-<noun>.md`) + user rules if known. **If dimensions aren't obvious, run § Meta-survey first** (don't pick dimensions in a vacuum).
3. **Collect rows** — one entity at a time; record source per cell.
4. **Normalize** — units, dates, naming. Note where normalization is lossy.
5. **Sort + sectionize** — by a primary key the user can act on.
6. **Surface gaps + outliers** — missing cells, surprising values, entities that don't fit.
7. **Write the report** to `~/ob/kmr/Topic/Search/Survey/YYYY-MM-DD <survey-name>.md`.
8. Return path + the 2-3 most notable findings.

## Meta-survey (sub-pattern)

Two forms — pick by stake:

**Lightweight meta-survey** (default when dimensions aren't obvious): one survey of *how others organized the comparison*, used purely to derive the dimension set.

1. Survey **how others have surveyed this kind of thing** — ranking pages, "best X for Y" articles, academic taxonomies, comparison sites.
2. Extract the dimension union/intersection across those surveys.
3. Pick dimensions from that union, weighted by frequency of appearance.
4. Proceed with normal survey from step 3 of the runbook above.

This bottoms out quickly because at the meta level the dimensions are stable.

**Full meta-survey** (`/survey meta <noun> — <topic>`): three composed surveys plus cell-certainty notation, for high-stakes comparisons. Runs a **source survey** (Stage 1 — rate the trustworthiness / accuracy / completeness of candidate information sources), a **dimension survey** (Stage 2 — rank candidate dimensions by source-coverage / source-prominence / discriminative power / user-fit / measurability), and an **item survey** (Stage 3 — the standard comparison, with every cell annotated for certainty: `***value*** ★★★` down to `???value???`). Full runbook + certainty notation: [[survey/meta-survey|meta-survey.md]].

Use the lightweight form when the standard `/survey` runbook just needs better dimensions. Use the full form when the user is about to commit (purchase, adopt, hire, publish), the domain is contested, or sources disagree.

## Depth tiers

| Tier | Population | Dimensions | When |
|---|---|---|---|
| Quick | top 5-10 | 3 most-important | orientation |
| Standard | full (within bound) | 5-7 | default |
| Deep | full | 10+, multi-source per cell, footnotes | thorough comparison |

## Escalation

- Population is unbounded ("survey all SaaS") → tighten bound with the user before starting.
- Dimensions aren't obvious → run meta-survey explicitly; surface result before row-filling.
- More than ~30% of cells would be missing → ask "this survey is fundamentally sparse, re-scope?"

## Output shape

A markdown report with:

- **Results table** (RRR convention): rows × dimensions. First column is the entity name as a markdown link to its source URL.
- **Scope note** — population, bound, dimensions, when generated.
- **Interpretive notes** — what's notable, gaps, outliers.
- **Sources** — full URLs at end.

Per the RRR convention, value is in the comparison, not the rows — interpretive notes are required.

## Output

Lands in `~/ob/kmr/Topic/Search/Survey/` as a markdown file. The [[Survey]] anchor lists surveys newest-first.

## Anti-patterns

- Picking dimensions privately before checking how others have organized the comparison.
- Quiet truncation of the population without naming the bound.
- A survey table with no interpretive notes — the value is the analysis.

## Related

- User reference: [[SKL Survey]]
- Overview of composition: [[SKL Search Overview]]
- Rules trait: [[SKA skill-trait search-rules]]
- User overrides: [[SRC rules]]
- Legacy: this skill subsumes `/research survey`, `/research skill` (as a specialized variant in `rules/survey.md`), and the broad-research phase of `/product hunt` (in `rules/survey-product.md`).
