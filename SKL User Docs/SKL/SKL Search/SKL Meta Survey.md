---
description: "high-rigor three-stage form of /survey for high-stakes comparisons"
---
# SKL Meta Survey

| -[[SKL Meta Survey]]- | → [[SKL Search]] → [SKL Meta Survey](hook://p/SKL%20Meta%20Survey)<br>: high-rigor three-stage form of /survey for high-stakes comparisons |
| --- | --- |
| Runbook | [[survey/meta-survey\|meta-survey.md]],   |
| Standard /survey | [[SKL Survey]],   |

**Meta-survey** is the high-rigor form of `/survey`. Reach for it when the user is about to commit (purchase, adopt, hire, publish), the domain is contested or rapidly changing, sources disagree, or "we got it wrong" has a real cost.

## Three composed surveys

| Stage | What it surveys | Output |
|---|---|---|
| **1. Source survey** | The information sources for this domain — rated on **trustworthiness** (business model, community reputation, track record), **accuracy** (effort signal, cross-checkability, past calls), **completeness** (coverage, freshness, gaps). | Ranked source roster. |
| **2. Dimension survey** | The candidate dimensions for the comparison — rated on **source coverage**, **source prominence**, **discriminative power**, **user-fit**, **measurability**. | Ranked dimension list → Stage 3 columns. |
| **3. Item survey** | The actual comparison, rows × dimensions, sourced from Stage 1 — with **every cell annotated for certainty** (see below). | The user's main deliverable. |

## Cell-certainty notation

Markdown-friendly. Wraps the cell value, not the cell itself.

| Level | Notation | Meaning |
|---|---|---|
| Definitive | `***value*** ★★★` | Multiple primary-source confirmations. |
| Very high | `***value*** ★★` | Multiple top-tier sources agree exactly. |
| High | `***value*** ★` | One top-tier source, no contradictions. |
| Confident | `**value**` | Single trustworthy source; not contradicted. |
| Baseline | `value` | Adequate sourcing — implicit standard. |
| Slight doubt | `?value?` | Thin sourcing OR minor disagreement. |
| Significant doubt | `??value??` | Conflicting sources. |
| Speculative | `???value???` | Rumor, single low-tier source, or no live sourcing. |

`—` (em-dash) is **empty cell** — distinct from low certainty. Em-dash means *the agent looked and found nothing*, not *the claim is weak*.

A row of `***bold-italic***` cells with stars is one the user can act on. A row of `???vague???` cells is one to push back on. The format makes that visible at a glance, without reading footnotes.

## Invoke

- `/survey meta <noun> — <topic>` — explicit (recommended): `/survey meta software — feature-flag libraries for Go services`
- Natural language: *"meta-survey project management SaaS for a 50-person team"* / *"do a thorough survey of observability tools — I'm about to commit"*

## When NOT to use

- Quick orientation, not a commit decision → standard [[SKL Survey]].
- Well-established sources, well-known dimensions → standard `/survey`, optionally with the *lightweight* meta-survey sub-pattern (survey-of-surveys to derive dimensions only).
- Single entity, not a comparison → [[SKL Profile]].
- Single-instance lookup → [[SKL Find]].

Skill methodology: [[survey/SKILL|survey/SKILL.md]] · Full runbook: [[survey/meta-survey|meta-survey.md]] · Composition: [[SKL Search Overview]].
