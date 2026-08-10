---
description: "How the search skill family combines knowledge and rules — the mental model behind find/profile/survey."
---
# DAS Search Overview
The mental model behind the **search skill family** (`find`, `describe`, `survey`) — how the pieces fit together so you know how to ask, where to find rules, and where results land.

| -[[DAS Search Overview]]- | : How the search skill family combines knowledge and rules — the mental model behind find/profile/survey.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Search Overview](hook://p/DAS%20Search%20Overview)  |
| --- | --- |
| ... |  |

## The two axes

Search is described along **two axes**:

- **Verb (action)** — *what kind of search*: [[DAS Find|find]], [[DAS Profile|describe]], [[DAS Survey|survey]].
- **Noun (entity)** — *what kind of thing*. Grouped categorically: **People** ([[DAS Person|person]], [[DAS Corp|corp]]) · **Things** ([[DAS Product|product]], [[DAS Book|book]]) · **Digital content** ([[DAS Software|software]], [[DAS Skill|skill]]). Extended over time as patterns emerge.

A request like *"survey project management SaaS tools"* invokes the `survey` skill with the noun-type *product*.

## Loading order at invocation

When a search verb runs (e.g. `survey products`), the agent loads in this order:

| Layer | Where | What |
|---|---|---|
| **1. Methodology** | `<skill>/SKILL.md` | invariant runbook — how to do this verb |
| **2. Default verb rules** | `<skill>/rules/<verb>.md` | ships with skill |
| **3. Default pair rules** | `<skill>/rules/<verb>-<noun>.md` | ships with skill — entity knowledge built in |
| **4. Your verb rules** | [[SRCH rules]] `/<verb>.md` | overrides default for this verb |
| **5. Your noun rules** | [[SRCH rules]] `/<noun>.md` | overrides default for this noun, any verb |
| **6. Your pair rules** | [[SRCH rules]] `/<verb>-<noun>.md` | most specific, wins all |

Layers 1-3 ship with the skill → it works out of the box on a fresh install. Layers 4-6 are yours → custom behavior. More-specific wins on conflict.

## Where outputs land

Each verb writes to a folder under [[SRCH|the Search anchor]]:

| Verb | Output folder | Filename pattern |
|---|---|---|
| survey | [[Survey]] (`~/ob/kmr/Topic/Search/Survey/`) | `YYYY-MM-DD <survey-name>.md` |
| describe | [[Profile]] (`~/ob/kmr/Topic/Search/Profile/`) | `YYYY-MM-DD <entity-name>.md` |
| find | [[Find]] (`~/ob/kmr/Topic/Search/Find/`) | `YYYY-MM-DD <short-name>.md` |

Each anchor's dispatch lists newest first.

## Picking a verb

- **Find** — you want *one specific match*. ("Find the GitHub repo for X.") → ID + sources + confidence.
- **Describe** — you have *one entity* and want a structured profile. ("Describe Acme Corp.") → a profile.
- **Survey** — you want a *comparison table across many entities*. ("Survey project management SaaS.") → table + interpretive notes.

If you're not sure: `find` returns identifiers, `describe` returns one profile, `survey` returns rows × columns. Pick by what you want at the end.

## Depth

Each verb has Quick / Standard / Deep tiers — specify in the request (*"survey X, go deep"*). Tier definitions live in each skill's default verb-rules file.

## Adding rules

To set a preference for *all* surveys: edit [[SRCH rules/survey|SRCH rules/survey.md]]. To set a preference for *all product searches regardless of verb*: edit [[SRCH rules/product|SRCH rules/product.md]]. To set a preference for *surveys of products specifically*: create [[SRCH rules/survey-product|SRCH rules/survey-product.md]] (it wins on conflict).

Standard: [[skill-search-rules]].
