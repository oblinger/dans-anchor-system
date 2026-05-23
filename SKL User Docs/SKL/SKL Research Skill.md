# /research skill

Specialized survey for **comparing agent skills** that do similar work. You give it a concept ("architect", "feature designer", "PRD writer"), it finds skills others have built that address it, and produces a comparison report with **choice-point analysis** and a recommendation.





# Details

## When to use

When you're considering **building or rebuilding a skill** and want to learn from what's already been tried, not just enumerate what's out there. Concrete examples:

- "I'm not happy with my architect skill — what have other people done?"
- "What skills exist for managing the feature lifecycle?"
- "Is anyone doing a good PRD-writer skill I could borrow from?"

If you just want a flat list of what's out there, use `/research survey`. Use `/research skill` when you want to know **how to think about the choices** baked into existing skills.

## What you get

A report at `~/ob/kmr/RR/RR Research Reports/{date} Skill Survey — {concept}/`:

1. **Results table** at the top — clickable links to every found SKILL.md, with columns for *what it outputs*, *what it does*, and its *notable architectural decision* (one keyword phrase per skill).
2. **Choice points** section — high-level architectural decisions baked into the skills, with which skills go which way for each axis. *This is where you decide which side you're on before committing to an approach.* Example: "Single architecture doc OR folder with subsystem sub-docs?" — followed by which 3 skills do single-doc and which 4 do folder.
3. **Approach groups** — skills bucketed by which *combination* of choices they made, each group named ("Code-first introspection", "Dialogue-driven design narrative", etc.). For each group: members + when this approach makes sense.
4. **Recommendation** — given your stated target shape, which existing skill is closest and what specifically to borrow vs. adapt vs. discard.

## How it differs from `/research survey`

`/research survey` is general-purpose — any topic, any space. `/research skill` pre-bakes everything specific to the skill ecosystem:

- **Where to search** — Anthropic's official skills repo, GitHub `filename:SKILL.md` searches, community catalogs
- **What columns to emit** — output / trigger / scope axes, consistent across skill survey reports
- **What analysis is mandatory** — choice points and groupings, not just enumeration

The defining feature is that **the report's value is in the reasoning, not the list**. A flat list of 12 architect skills isn't useful; "these 5 do code-introspection-first, these 4 do dialogue-first, these 3 emit modules-and-interfaces — your existing target leans dialogue, start with group 2 and steal the table layout from group 3" is.

## Invocation

```
/research skill architect
/research skill "PRD writer"
/research skill feature-lifecycle
```

For the agent runbook, see [[research-skill]].
