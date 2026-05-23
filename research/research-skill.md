# Skill Survey — Compare Skills in the Ecosystem

Specialized survey for the **agent-skill domain**. The target is not a topic in general but a *skill concept* (e.g., "architect", "PRD writer", "feature designer") — find skills others have built that do this kind of work, surface their approaches and choice points, and produce a comparison + recommendation report.

This is what you reach for when you're considering **building or rebuilding a skill** and want to learn from what's already been tried. Distinct from `/research survey` because the domain (skill repos), the columns (output / trigger / scope axes), and the required analysis (choice points + groupings, not just enumeration) are all pre-baked.

## Workflow

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

5. **Identify choice points** — the high-level architectural decisions baked into each skill. These are the most valuable output of this entire workflow: *"these 3 skills all assume X; these 2 assume not-X; you need to pick which side you're on before adopting any of them."* Examples for an architect skill:
   - "Single architecture doc OR folder with subsystem sub-docs?"
   - "Driven by code reading OR by user dialogue?"
   - "Output is documentation OR an executable design (modules + interfaces)?"

6. **Group by approach** — bucket the skills by which *combination* of choices they made. Name each group descriptively. ("Code-first introspection", "Dialogue-driven design narrative", "Module-list emitters", etc.)

7. **Synthesize recommendation** — given the user's stated direction, which existing skill is closest to their target shape, and what specifically to borrow vs. discard?

8. **Produce report** — write to RRR (Report Output below).

9. **Log it** — prepend a row to [[RRR]] with link + one-line description.

## Report Output

Same RRR location as other research actions:

```
RRR/
└── {YYYY-MM-DD} Skill Survey — {concept}/
    ├── {YYYY-MM-DD} Skill Survey — {concept}.md   Main report
    └── ...                                         Supporting files (optional)
```

## Report Sections (in order)

1. **Results Table** — ALWAYS first. Columns specific to the skill domain:

   | # | Skill | Source | Output | What it does | Notable choice point |
   |---|---|---|---|---|---|
   | 1 | [Top pick](URL) | anthropics-official | Architecture doc | Top-down decomposition with subsystem tables | Dialogue-driven, no code introspection |
   | ... | ... | ... | ... | ... | ... |
   | 5 | [Last top pick](URL) | ... | ... | ... | ... |
   |   |   |   |   |   |   |
   | 6 | [Next tier](URL) | ... | ... | ... | ... |

   - **Skill** column is the skill name as a markdown link directly to the SKILL.md (or repo-root if SKILL.md isn't web-visible)
   - **Rank** by relevance to the user's stated target, highest first
   - **Visual separator row** (empty) between top-tier candidates and the rest, per [[research-survey]] convention

2. **Choice points** — H2 named for each axis. For each: which skills go which way, and what the consequences are.

   ```markdown
   ## Choice points

   ### Output: single doc vs folder of sub-docs
   - Single doc: [Skill A], [Skill B]
   - Folder: [Skill C], [Skill D], [Skill E]
   - Trade-off: single doc is easier to grok; folder scales better when subsystems grow.
   ```

3. **Approach groups** — H2 for each grouping. For each: members, what they share, when this approach makes sense.

4. **Recommendation** — given the user's stated direction, the recommended starting point and specifically what to adopt / adapt / discard.

5. **Sources** — full URLs to every SKILL.md read. Pages opened in the user's browser also listed here.

## How this differs from `/research survey`

| | `/research survey` | `/research skill` |
|---|---|---|
| Domain | Any topic | Agent-skill repos and catalogs |
| Source emphasis | Generic web | SKILL.md files (read in full) |
| Columns | Whatever fits the topic | Pre-baked: output / trigger / scope / choice point |
| Mandatory analysis | Trends + gaps | Choice points + approach groupings |
| Goal | "What's the landscape?" | "Should I build/rebuild this, and how?" |

If the user wants a flat list of what's out there, use `/research survey`. If they want to know *how to think about the choices* baked into existing skills, use `/research skill`.
