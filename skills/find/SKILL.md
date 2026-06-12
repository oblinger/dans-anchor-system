---
name: find
description: Locate one specific instance matching criteria from many candidates. Use for finding a person, company, product, GitHub repo, or other concrete online entity. Returns identifier + canonical URL + 1-line context + confidence (high/medium/low) + sources consulted. Disambiguates when multiple candidates score evenly rather than silently picking one. Supports Quick / Standard / Deep tiers — specify in the request. Output lands in `~/ob/kmr/Topic/Search/Find/` as `YYYY-MM-DD <short-name>.md`. For specific entity types (person / corp / product), loads type-specific rules. NOT for broad category research (use survey) or one-entity dossiers (use profile).
user_invocable: true
---

# /find

Locate **one specific match** for the criteria the user provides. Return an identifier + sources + confidence. Disambiguate before answering.

## What loads at invocation (per [[skill-search-rules]])

1. **This SKILL.md** — methodology (the runbook below).
2. `find/rules/find.md` — default verb rules (ships with skill).
3. `find/rules/find-<noun>.md` — default pair rules with entity knowledge baked in (ships with skill).
4. `SRC rules/find.md` — user's verb-level overrides (if present).
5. `SRC rules/<noun>.md` — user's noun-level overrides, cross-verb (if present).
6. `SRC rules/find-<noun>.md` — user's pair-level overrides (most specific, wins all).

Layers 1-3 ship with the skill; 4-6 are user overrides loaded from [[SRC rules]] at `~/ob/kmr/Topic/Search/SRC rules/`.

## Runbook

1. **Restate the criteria** as a queryable spec. Surface ambiguity early; don't paper over it.
2. **Identify the noun-type** from the criteria. If known (person / corp / product / …), load the matching pair-rules file (`find/rules/find-<noun>.md`) for entity-specific dimensions, sources, and disambiguation. If unknown, fall through to general methodology and ask the user for relevant dimensions if needed.
3. **Query** the type's primary sources (per the pair file).
4. **Score candidates** — match strength × source quality.
5. **Disambiguate** when top candidates score close: pull a tiebreaker attribute, ask the user, or return all ranked.
6. **Verify** the top match against a second independent source before returning.
7. **Write the lookup file** to `~/ob/kmr/Topic/Search/Find/YYYY-MM-DD <short-name>.md` with: identifier, canonical URL, 1-line context, confidence (high/medium/low), sources, and any ambiguity notes.
8. Return the identifier + a pointer to the saved lookup file.

## Depth tiers

User specifies in request ("find me X, quick" / "go deep"). Per-tier rules live in `rules/find.md` § Depth.

| Tier | Sources | Verification | When |
|---|---|---|---|
| Quick | 1 | minimal | obvious matches you just need confirmed |
| Standard | 2-3 | brief cross-check | default |
| Deep | broad | full chain | due diligence, will-act-on-it cases |

## Escalation

- Multiple candidates scoring within ~10% → ask the user with the disambiguating attribute.
- No candidate clears the confidence floor → return "not found" with what was searched.
- Source disagreement on identity-level fact → return both with the discrepancy noted.
- Privacy concern (private individual, PII compilation) → push back before complying (see `rules/find-person.md`).

## Output

Lands in `~/ob/kmr/Topic/Search/Find/` as a markdown file with the identifier, canonical URL, sources, confidence, and any ambiguity / verification notes. The [[Find|Find]] anchor lists results newest-first.

## Anti-patterns

- Returning the first plausible match without a tiebreaker check.
- Hiding ambiguity behind a confident-sounding summary.
- Inventing identifiers when search came up empty.

## Related

- User reference: [[SKL [[Find|Find]]
- Overview of how it all combines: [[SKL Search Overview]]
- Rules trait: [[skill-search-rules]]
- User overrides: [[SRC rules]]
