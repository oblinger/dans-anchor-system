---
name: profile
description: Build a thorough structured description of one specific entity (person, company, product, book). Returns a markdown profile with source-attributed facts; Quick tier is a summary card, Standard is a full profile, Deep is a complete dossier ("Dig" — multi-source synthesis, contradictions surfaced, gaps named). For one entity at a time — use survey for comparing many, use find for just identifying one. Output lands in `~/ob/kmr/Topic/Search/Profile/` as `YYYY-MM-DD <entity-name>.md`. Loads type-specific rules for person / corp / product.
user_invocable: true
---

# /profile

Build a **thorough structured description of one entity**. The user provides an entity (or has it identified via [[find]]), the skill produces a structured profile sized to the depth tier.

The Deep tier is what users sometimes call **"dig"** — full dossier, multi-source synthesis, contradictions surfaced, gaps named.

## What loads at invocation (per [[skill-search-rules]])

1. **This SKILL.md** — methodology (the runbook below).
2. `profile/rules/profile.md` — default verb rules (ships with skill).
3. `profile/rules/profile-<noun>.md` — default pair rules with entity knowledge baked in (ships with skill).
4. `SRC rules/profile.md` — user's verb-level overrides (if present).
5. `SRC rules/<noun>.md` — user's noun-level overrides, cross-verb (if present).
6. `SRC rules/profile-<noun>.md` — user's pair-level overrides (most specific, wins all).

Layers 1-3 ship with the skill; 4-6 are user overrides loaded from [[SRC rules]] at `~/ob/kmr/Topic/Search/SRC rules/`.

## Runbook

1. **Confirm the entity** is unambiguous. If not, invoke [[find]] first.
2. **Identify the noun-type** (person / corp / product / …). Load matching pair-rules file (`profile/rules/profile-<noun>.md`) for entity dimensions, sources, output shape.
3. **Pick the dimension set** for this type at this depth (from the pair file + user rules).
4. **Collect** from each source named in the pair file; record source per fact.
5. **Synthesize** — dimensions filled, contradictions flagged with sources, gaps named (not filled with inference).
6. **Write the profile** to `~/ob/kmr/Topic/Search/Profile/YYYY-MM-DD <entity-name>.md`.
7. Return the path to the saved profile + a 2-sentence summary.

## Output shape

A markdown profile:

- **Title line** with the entity name + tier label.
- **Results table at top** (per legacy RRR convention) — at-a-glance facts.
- **Body sections** organized by the noun's standard dimensions; facts source-attributed inline or in footnotes.
- **Contradictions** — surfaced explicitly, never harmonized away.
- **Gaps** — explicit "no source coverage for X" section in Deep; doesn't get filled by inference.
- **Sources** section with full URLs (so links work outside Obsidian).

## Depth tiers

| Tier | Output | When |
|---|---|---|
| Quick | summary card (3-5 facts, single source) | lightweight context for a conversation |
| Standard | full profile (10-15 facts, 2-3 sources, contradictions flagged) | default |
| Deep ("Dig") | full dossier (all dimensions, all sources, source-per-fact, gaps named, related entities) | due diligence, will-act-on-it cases |

## Escalation

- Entity not unambiguous → run [[find]] first.
- Sources contradict on identity-level facts → return both with the discrepancy noted; don't pick.
- Major dimension has no source coverage → name the gap; don't infer.
- Privacy-sensitive subject (private individual) → guard-rail question first (see `rules/profile-person.md`).

## Output

Lands in `~/ob/kmr/Topic/Search/Profile/` as a markdown file. The [[Profile]] anchor lists profiles newest-first.

## Anti-patterns

- Filling gaps with inference dressed as fact.
- Burying contradictions in a harmonized narrative.
- Treating Quick as "lazy Deep" — Quick is a different artifact, not a worse one.

## Related

- User reference: [[SKL Profile]]
- Overview of composition: [[SKL Search Overview]]
- Rules trait: [[skill-search-rules]]
- User overrides: [[SRC rules]]
- Legacy: this skill subsumes the per-entity actions of the legacy [[research/SKILL|/research]] family (`/research dig`, `/research person`, `/research book`).
