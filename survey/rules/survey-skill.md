---
description: Default rules for surveying agent skills — ships with the skill. User overrides in SRC rules/. Migrated from legacy /research skill.
---
# survey-skill — default rules

Default rules for `survey` on noun-type **skill** — comparing agent skills (Claude Code skills, MCP servers, agentic toolings) that do similar work. Ships with the skill; user overrides in `[[SRC rules/survey-skill|SRC rules/]]`.

Subsumes the legacy `/research skill` action. Applies when the survey population is **agent skills** ("survey architect skills", "compare PRD writer skills", "what's the landscape of feature-design skills").

Distinct from generic [[survey/SKILL|survey]] because the domain (skill repos), the columns (output / trigger / scope axes), and the required analysis (choice points + groupings, not just enumeration) are all pre-baked.

## Trigger phrases

- *"survey skills that do X"*
- *"compare skills for Y"*
- *"is anyone doing a good Z skill"*
- *"what skills exist for doing W"*
- *"I'm thinking of building a skill that does V — what's already out there"*

## Default workflow (specialized)

1. **Clarify the skill concept** — confirm what *function* the user is researching (the work the skill does, not a specific implementation). Pin down: what's the output artifact? what's the trigger? what stage of work? Example targets: "architect — produces architecture docs"; "feature lifecycle management"; "PRD writer"; "deep-investigation dossier producer".

2. **Search the skill ecosystem** — cast a wide net:
   - **anthropics/anthropic-skills** — the official Anthropic skills repo (highest signal)
   - **GitHub code search** for `filename:SKILL.md` and `path:skills` to find personal repos
   - **awesome-claude / awesome-skills** community-curated lists
   - **claude.ai skill marketplace** if applicable
   - **Personal repos** by known practitioners (search by author when surfaced)

3. **Read the actual SKILL.md** for each candidate — *not* just the README or repo description. The interesting differences are in the runbook, not the description line. A 3-line description can hide a fundamental architectural choice.

4. **Extract dimensions** — for each skill, identify where it sits on the standard axes:
   - **Output artifact** — doc / code / table / plan / spec / dispatch-page
   - **Output shape** — single file / folder-doc / appended-to-existing
   - **Trigger** — user-invoked / chained from another skill / autonomous-loop
   - **Scope** — per-anchor / per-project / vault-wide / global
   - **User involvement** — high-touch (questions throughout) / autonomous / parking-mode-friendly
   - **Workflow phase** — planning / executing / verifying / maintenance
   - **State persistence** — stateless / accumulates artifacts / hooks into state machine
   - **Sub-action shape** — single verb / family of actions

5. **Identify choice points** — the high-level architectural decisions baked into each skill. *These are the most valuable output of this entire workflow:* "these 3 skills all assume X; these 2 assume not-X; you need to pick which side you're on before adopting any of them." Examples for an architect skill:
   - "Single architecture doc OR folder with subsystem sub-docs?"
   - "Driven by code reading OR by user dialogue?"
   - "Output is documentation OR an executable design (modules + interfaces)?"

6. **Group by approach** — bucket skills by which *combination* of choices they made. Name each group descriptively. ("Code-first introspection", "Dialogue-driven design narrative", "Module-list emitters", etc.)

7. **Synthesize recommendation** — given the user's stated direction, which existing skill is closest to their target shape, and what specifically to borrow vs. discard?

## Default dimensions table

Pre-baked columns for the survey table:

| # | Skill | Source | Output | What it does | Notable choice point |
|---|---|---|---|---|---|
| 1 | [Top pick](URL) | anthropics-official | Architecture doc | Top-down decomposition with subsystem tables | Dialogue-driven, no code introspection |
| ... | ... | ... | ... | ... | ... |

- **Skill** column is the skill name as a markdown link directly to the SKILL.md (or repo-root if SKILL.md isn't web-visible).
- **Rank** by relevance to the user's stated target, highest first.
- **Visual separator row** (empty) between top-tier candidates and the rest (per RRR convention in [[survey/rules/survey|survey.md]]).

## Default report sections (in order, on top of RRR convention)

1. **Results table** (above) — always first.

2. **Choice points** — H2 named for each axis. For each: which skills go which way, and what the consequences are.

   ```markdown
   ## Choice points

   ### Output: single doc vs folder of sub-docs
   - Single doc: [Skill A], [Skill B]
   - Folder: [Skill C], [Skill D], [Skill E]
   - Trade-off: single doc is easier to grok; folder scales better when subsystems grow.
   ```

3. **Approach groups** — descriptive names for combinations of choices, with members + when each makes sense.

4. **Recommendation** — given the user's target, which existing skill is closest and what to borrow vs. adapt vs. discard.

5. **Sources** — full URLs (per RRR convention).

## Default sources (authority order)

1. **anthropics/anthropic-skills** — highest signal; the official patterns.
2. **GitHub** `filename:SKILL.md` searches — personal repos, often more experimental.
3. **awesome-claude / awesome-skills** — community-curated lists; secondary discovery.
4. **claude.ai skill marketplace** — when applicable.
5. **Known practitioners' repos** — search by author when prior work surfaces.

## Gotchas

- **Don't trust the description line** — read the SKILL.md runbook. Architectural differences hide there.
- **A skill's choice point may be implicit** — sometimes the most interesting decision isn't stated, it's just the shape of the runbook. Surface it.
- **Skill ecosystems move fast** — note publication dates; a skill from a year ago may have been superseded by a refinement in the same repo.
- **"Awesome lists" are often stale** — verify each candidate still exists and is maintained.

## User rules

(Empty — user adds in `SRC rules/survey-skill.md` to override these defaults.)
