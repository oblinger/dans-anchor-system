
# EXP Experiment Template

Standard format for individual experiment specs. Each experiment lives in its own folder (`Q1_02_name/Q1_02_name.md`) alongside its `code.py` and `output/` directory. The spec serves two audiences: the **worker** who runs it (reads top-down before the experiment) and the **reviewer** who reads results (reads the overview, then jumps to Results).


## Experiment Document Structure

```markdown
## Open Questions                          {{delete this section when all are resolved}}
---
# Q1_02 — Experiment Title

*{{one specific, answerable question}}*

*Why care?* {{1-2 sentences: what decision or understanding depends on this result}}

## Background
{{what we know, prior experiments, the gap this addresses}}

## Approach
{{bullet summary: data, model, measurement, analysis}}

## Expectations
{{what you expect and why; what would change your mind}}

## Key Result

> [!summary] {{headline sentence with key number(s), with confidence qualifier}}

{{key figure → summary table}}

## Discussion
{{interpretation, confidence, connections to prior experiments, new questions}}

### Details                                   {{optional — only if supporting findings warrant it}}
{{supporting findings with additional figures; otherwise move to Detailed Results below the line}}

---

## Detailed Approach
{{step-by-step code description, concrete examples}}

## Config
{{parameters, values, and why}}

## Dependencies
{{checkpoints, prior experiment outputs needed}}

## Output Files
{{list of files produced with descriptions}}

## Detailed Results
{{raw tables, per-layer breakdowns, anything too granular for above}}



# Additional Figures
{{figures not featured in Key Result — one-line description each, reviewer can promote}}
{{Use H1 and blank lines above for strong visual separation from the reference material}}
```

---



### Open Questions
A design-phase gate. Lives ABOVE the title. Each entry is an unresolved design decision. When all are answered, delete the entire section and the HR below it — the experiment is ready to run.

```markdown
## Open Questions
1. Should we test both FT and base, or just FT?
2. What alpha value for the ridge probe?
---
```



### Overview Paragraph
One paragraph immediately after the title, before any spec sections. Filled in AFTER the experiment runs (leave blank in the spec). This is the 30-second version — a reviewer who reads only this paragraph gets the headline finding, the key number, and the confidence level.

Example from Q1_02:
> "To put rigorous error bars on the 98.4% accuracy from Q1_01, we ran two complementary analyses: bootstrap resampling of the test set and retraining with 5 different random seeds. The headline result: **98.0% ± 0.47pp across seeds**, with a 95% CI of [97.1%, 99.0%]."

This is NOT a summary of the spec — it's a summary of the RESULT. Leave it blank until the experiment completes.



### Question (italic line after title)
One specific, answerable question in italics, immediately after the title — no H2 header. Not a topic, not a goal — a question with a measurable answer. Frame it so you'll know when you've answered it.

Good: *At which layer does digit identity become linearly decodable?*
Bad: *Investigate how layers encode information.*

**Italic prefix signposts** — sparingly, use a short italic prefix to orient the reader when the structure isn't self-evident: *Why care?* before motivation, *The surprise:* before an unexpected finding, *We found:* before a headline result. These read as a researcher signposting their thinking. If every paragraph has one, it's a template — use them only where they genuinely help.



### *Why care?*
Optional italic signpost, not a heading. Use when Background alone doesn't make the stake obvious. 1-2 sentences answering: what decision or understanding depends on this result? Example: "*Why care?* If the gap shrinks, most of E00's benefit was regularization in disguise, not dark knowledge."



### Background
What motivates this experiment. 2-4 bullets:
- What do prior experiments tell us? (reference by number)
- What gap or open question does this address?
- Why does this matter for the broader research question?

This is context for the worker AND for the reviewer. A reader seeing this experiment for the first time should understand why it exists.



### Approach
Bullet summary of what the code does — enough for the worker to understand the experiment without reading the detailed approach. 4-6 bullets:
- What data transformation (if any)?
- What model(s) — fine-tuned, base, or both?
- What is extracted — hidden states, attention, behavioral output?
- What analysis — probes, statistics, visualization?



### Expectations
Predictions BEFORE seeing results. Sets up the narrative payoff in "Which outcome matched?" A short paragraph or a couple of bullets — no fixed categories. Two things matter:

- **What you expect and why** — the mechanism reasoning. "We expect accuracy to plateau by layer 8 because that's where D01 showed digit identity becoming linearly separable." The *because* clause is where understanding lives.
- **What would change your mind** — the key alternative. "If accuracy keeps climbing through layer 20, that would suggest the later layers encode something beyond identity." Only include this if there's a genuinely meaningful alternative — don't invent one to fill a slot.

Sometimes there's only one prediction. Sometimes there are three real alternatives. Let the experiment dictate the shape, not a template.



### Key Result
The worker fills this in after the experiment runs. The core principle: **headline first, then evidence.** Someone skimming should get the answer from the first two things they see — the callout and the key figure.

**Structure:**

1. **Headline in a `> [!summary]` callout** — one sentence with key number(s) and a confidence qualifier. Use hedging that reflects actual certainty ("likely," "appears to," "consistent with") — don't state single-seed results as established facts. No bold inside the callout.

2. **Key figure** — the single most important figure, immediately after. One sentence saying what to look at.

3. **Summary table** — all key numbers at a glance.

```markdown
> [!summary] Distillation likely reshapes internal representations. CKA is 0.552 vs 0.445 (+0.107 gap), large and consistent with E02, but single-seed.

![CKA alignment](output/cka_results.png)

| Metric | Hard | Distilled | Gap |
|--------|------|-----------|-----|
| CKA with teacher | 0.445 | 0.552 | +0.107 |
```

### Discussion
Interpretation and synthesis — NOT a restatement of key results. Three things to cover:
- How does this connect to prior experiments?
- What's the most interesting or unexpected thing?
- What new questions does this raise?

Include a *Confidence:* note: how sure (high/moderate/low), what supports it (effect size, sample count, consistency), and the main caveat (single seed, no significance test, etc.). Whether expectations were confirmed or surprised, weave that in naturally.

### Details (optional)
Only include this section above the `---` if supporting findings warrant it (e.g., per-class breakdowns, temperature curves). Otherwise, supporting material goes to **Detailed Results** below the line. Each finding starts with a **bold claim sentence**, then evidence. Figures immediately followed by their interpretation.

**Figure triage** — figures that don't make the cut go to **Additional Figures** below the HR. Each gets a one-line description so the reviewer can promote any that deserve elevation.



### Below the HR — Reference Material
Everything below the `---` is for auditing, not for narrative reading.

- **Detailed Approach** — step-by-step code description. Include concrete examples of data transformations. Enough for someone to reimplement.
- **Config** — parameter values with brief justification: `ALPHA: 1.0 (ridge default, no tuning needed for 10K samples)`
- **Dependencies** — file paths to checkpoints and prior experiment outputs needed
- **Output Files** — list of actual files produced, with one-line descriptions
- **Detailed Results** — raw tables, per-layer breakdowns, anything too granular for the main Results section
- **Additional Figures** — uses `# Additional Figures` (H1) with 2-3 blank lines above it for strong visual separation. Contains figures the worker generated but chose not to feature in Key Result. Each gets a one-line description. The reviewer scans this section and promotes any that deserve a spot in the narrative. Keeps the Key Result section focused while ensuring nothing is lost.
