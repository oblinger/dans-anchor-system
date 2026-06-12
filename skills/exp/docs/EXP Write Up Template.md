
# EXP Write Up Template — Deliverable Template

The structure and format of the write-up document produced at the end of a research cycle. For the process of producing it, see [[EXP Master Flow]].


## Writeup Document Structure

```markdown
# [Title — The Research Question]

{{executive summary — 2-3 narrative paragraphs, no header}}

## Approach
{{conceptual framing → sub-questions → experiment design → what was NOT investigated}}

## Key Findings

### Q1: [question]
{{result, evidence, interpretation, confidence}}

### Q2: [question]
{{result, evidence, interpretation, confidence}}

### Q3: [emergent question, if one arose]
{{result, evidence, interpretation, confidence}}

## Discussion & Conclusions
{{synthesis, surprises, confounds, limitations, next steps, conclusion}}

---   {{BRs and HR to separate reference material below}}

## Methodology
{{reproducibility: hardware, software, seeds, hyperparameters}}

## Experiment Log
{{chronological record of ALL experiments including failures}}
```

---



### Executive Summary
2-3 narrative paragraphs. Self-contained — if the reader reads nothing else, they get the full story. This is the single most important section of the document. No per-question enumeration here — that's what the Findings section is for.

**Paragraph 1: Question and headline answer.** Restate the research question in your own words, then give the answer. Not a teaser — the actual finding. "We investigated [question]. The central finding is [result], which suggests [interpretation]."

**Paragraph 2: The story arc.** How the investigation unfolded — what you expected, what you found, what surprised you. This is where conceptual understanding shows through naturally. "We hypothesized [X] because [mechanism]. Our experiments confirmed [Y] but revealed an unexpected [Z], which suggests [interpretation]."

**Paragraph 3: Confidence and what's next.** How much to trust the results, what the main limitation is, what you'd do with more time. "We're confident in [X] (replicated across N seeds) but [Y] remains preliminary. With more time we would [Z]."

Draft this first to guide your work. Rewrite it last based on what you actually found.



### Approach
This section does double duty: it shows **conceptual understanding** through how you frame the problem, and **experimental velocity** through your research taste.

**Open with conceptual framing** — not textbook definitions, but your understanding of why the question matters and what mechanisms are at play. "Distillation transfers knowledge from teacher to student via [mechanism]. The interesting question is [X] because [reason]." This is where understanding lives — woven into the narrative, not in its own box.

**Break the question into sub-questions** — "To answer the main question, we need to know: (1) ... (2) ... (3) ..." This shows you understood the structure of the problem.

**Describe the experiment sequence and rationale** — what you ran, in what order, and why each experiment followed from the previous one. "We started with [baseline] to establish [ground truth]. That result led us to test [X]. The surprise in [X] motivated [Y]."

**Name what you did NOT investigate** — and why. This shows the scope was deliberate, not accidental.

**The question:** Does the reader see a purposeful investigation, or a random walk?



### Key Findings
Detailed evidence organized by question, not by chronology. Each sub-section (Q1, Q2, ...) is the ONE place that question gets its full treatment — figures, tables, interpretation, confidence. The executive summary tells the story; this section shows the evidence.

Each question section follows this structure:

- **Result:** The answer — one clear sentence with confidence language.
- **Evidence:** Figure, table, or key numbers. Inline — the reader sees the evidence as they read the claim.
- **Interpretation:** What does this mean? How does it connect to the broader question?
- **Confidence and caveats:** Why we believe this (N seeds, effect size, consistency). What could undermine it (confounds, single seed, limited conditions).
- **Experiment links:** End each finding with links to the supporting experiment specs (e.g., "See [J1_02](J1_02_noise_vs_bias/J1_02_noise_vs_bias.md) for details."). The reader should never be frustrated that they can't dig deeper — every claim links to its evidence.

**Figures:** Lead with them. A figure with a clear caption communicates faster than text. Use `figsize=(10, ...)`, 150 DPI. Compose related panels as subplots. Tables for quantitative comparisons. Bold the most important numbers.

Naming: `Q1_01_name`, `Q1_02_name`, etc. Each experiment folder contains its code, output, and a spec with inline results.



### Discussion & Conclusions
Synthesis and honesty. This is where **reasoning transparency** peaks. Does NOT restate individual findings — synthesizes ACROSS them.

- **Synthesis** — What's the big picture across all findings? Do they tell a coherent story? Where do findings from different questions converge or conflict?
- **Most important finding** — Explicitly state which result matters most and why. Don't treat all findings equally.
- **Surprises** — What went against expectations? How did you respond? Explaining why something surprised you demonstrates deeper understanding than reporting expected results.
- **Confounds** — What systematic issues could affect results? Name them proactively.
- **Limitations** — What didn't you test? Why not? Single seed? Single dataset? Limited hyperparameter search?
- **Next steps** — What would you do with more time?
- **Conclusion** — The final paragraph(s). The takeaway. If the conclusion is strong enough, it can be its own `## Conclusions` section — but only if it earns the weight.



### Methodology
Serves **correctness and validity**. This section does more than list hyperparameters — it demonstrates awareness of what could go wrong.

**Models and Training** — Table format: model, architecture, training details, key hyperparameters. Make it scannable.

**Data Splits and Evaluation Boundaries** — Explicitly state:
- Which data split each quantity comes from (train vs test)
- Where any comparison crosses the train/test boundary, and why it's noted in the text
- How baselines were constructed to ensure fair comparison (same architecture, same optimizer, same data — only the variable of interest changes)

This is not boilerplate — it shows the reader you're aware of leakage and have thought about it per-comparison, not just globally.

**Reproducibility** — Enough for someone to rerun your work:
- Hardware (GPU model, VRAM)
- Software (Python version, PyTorch version, key packages with versions)
- Random seeds used (list all of them)
- Key hyperparameters (lr, epochs, batch size, optimizer, scheduler)
- Experiment folder structure and how to rerun from cached artifacts

**Experiments Not Featured** — List experiments you ran but did not include in the Key Findings, with a brief explanation of why each was orthogonal or inconclusive. This serves two purposes:
1. Shows you didn't cherry-pick — the reader can see everything you tried
2. Shows research taste — you made deliberate choices about what to feature

Format: one paragraph per experiment, linking to the full spec, explaining the result and why it wasn't featured.


### Experiment Log
Chronological record of ALL experiments — including failures, dead ends, things that didn't work. This is your insurance against cherry-picking concerns.

For each experiment:
- **Time** (relative to start, e.g., "0:45")
- **Question addressed** (Q1, Q2, etc.)
- **What we tested and why**
- **Result** (raw numbers)
- **What we concluded / what it led to**
- **Link to experiment folder**

Include experiments that were orthogonal or not featured — mark them as such. The main body draws from this, but the reader can audit everything here.


## README Structure

```markdown
# [Title]

- [writeup.md](writeup.md) — Main writeup
- [ROADMAP.md](ROADMAP.md) — Internal working notes

## Questions
1. [Q1: question](writeup.md#q1-anchor)
2. [Q2: question](writeup.md#q2-anchor)

## Experiments
- [Q1_01_name](Q1_01_name/) — description
- [Q1_02_name](Q1_02_name/) — description
- [Q2_01_name](Q2_01_name/) — description

## Setup
- **Model:** ...
- **Hardware:** ...
```

## ROADMAP Structure

Internal working notes — checkboxes, status tracking, key findings as they land. Shows how the investigation unfolded but is NOT part of the formal deliverable.

```markdown
# Backlog
- [ ] Experiment idea — one sentence

# Ready
- [ ] Q1_03_name — spec written, ready to run

# Running
- [>] Q2_01_name — on r1

# Review
- [ ] Q1_02_name — results in, needs review

# Key findings so far
1. **Finding** — brief summary
2. **Finding** — brief summary
```

| Event | From | To |
|-------|------|-----|
| Spec written | Backlog | Ready |
| `exp zap` sent | Ready | Running |
| Worker done | Running | Review |
| Reviewed | Review | (integrate into writeup) |
