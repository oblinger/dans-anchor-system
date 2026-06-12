
# EXP Lead Flow — Research Cycle Process

The lead agent's process for a research cycle. The lead works WITH the user — the user is the researcher, the lead is the hands. Every decision about framing, approach, and interpretation is collaborative. Each experiment follows the [[EXP Experiment Flow]]. For dispatch and monitoring mechanics (zap, health, clear-task), see [[EXP Orchestrator Flow]]. For the deliverable format, see [[EXP Write Up Template]].


## Phase 1: Frame

Read the problem statement together. Do not write code yet.

### Step 1: Lead Pre-populates the Writeup

As soon as the problem statement arrives, the lead reads it and immediately drafts a full writeup skeleton — not a blank template, but a populated first draft with:

- **Draft executive summary** — 2-3 sentences stating our initial hypotheses and what we think the story is. This will be wrong. That's the point — it gives us a concrete stake to react to and revise.
- **Approach section** — Conceptual framing, sub-questions, planned experiment sequence, what we're NOT investigating. All filled in with the lead's best first take.
- **Each finding section** — Not results (we don't have any yet), but the key question restated, what data we'll use, what analysis we'll run, and what we expect to find.

The goal: give the user something concrete to react to, edit, and redirect — not a blank page.

### Step 2: Collaborative Discussion

Walk through the pre-populated writeup together. The user reacts, redirects, adds angles the lead missed.

- **Is the framing right?** Did the lead identify the right sub-questions? Is there a better way to carve up the problem?
- **Is the approach right?** For each question — is this the best way to answer it? What would the user do differently?
- **What's the interesting story?** What jumps out from the numbers? What's surprising? The user's intuitions shape the narrative.
- **Revise the draft** — Update the writeup based on the discussion. The exec summary, approach, and per-question framing should all reflect the agreed plan.

### Step 3: Set Up Supporting Documents

1. **Create the roadmap** — `ROADMAP.md` with planned experiments, checkboxes, time budget. Link from `README.md`.
2. **Start the experiment log** — In the writeup appendix.

**Output:** A writeup with a draft executive summary, agreed Approach, per-question framing with planned analyses, and TBD result placeholders. A roadmap with prioritized experiments.

**Critical:** After framing, the lead does NOT run off and fill in results autonomously. The writeup is a shared document. Every finding gets discussed before it goes in.


## Phase 2: Execute + Capture

Run experiments in priority order. Each experiment follows the [[EXP Experiment Flow]] (design → delegate → run → review → integrate).

### The loop

1. **Discuss the next experiment** — What question does it answer? What do we expect? (Brief — 1-2 min.)
2. **Run it** — Lead writes and runs the analysis code.
3. **Review results together** — What did we find? Does it match expectations? What's the interpretation?
4. **Update the writeup together** — Lead drafts the finding into the appropriate section. User reviews. Each finding follows the template: result → evidence → interpretation → confidence.
5. **Decide what's next** — Does this result change our plan? Do we need a follow-up experiment or move to the next question?

After each experiment lands:
- **Record raw results** in the experiment log (chronological, full data)
- **Note confidence level** — How much does this result tell us? Single seed? Multiple runs?
- **Note surprises or new questions** — Did this suggest an experiment we hadn't planned?

**Critical rule:** Never let results accumulate without updating the writeup. Each experiment should be reflected in the main body within minutes of completion.


## Pulse Checks

Structured pauses at planned intervals through the cycle. Do not skip these.

### Pulse Check Questions
- What questions have we answered? With what confidence?
- What's still open?
- Did any results surprise us or suggest a new question?
- Are we answering the right questions, or should we re-vector?
- What's the highest-value next experiment given remaining time?
- Is the writeup coherent so far, or are there gaps?
- Does the executive summary draft still reflect our understanding, or does it need updating?

### Early check
First results should be in. Confirm the framing still makes sense. Adjust experiment priority if needed. Update executive summary draft.

### Midpoint check
Most important check. Are we on track to answer the main question? Are there gaps that need filling? This is the last good chance to pivot.

### Improvements Check (CRITICAL)

**This is the last chance to run experiments.** Walk through the writeup against the quality criteria and identify gaps that need *computation* to fix. Do not skip this.

**Error bars and statistical rigor:**
- Does every key number have a confidence interval or bootstrap CI?
- If not, design and dispatch quick experiments to compute them (bootstrap is usually <1 min)
- Key numbers that typically need CIs: accuracy differences, correlation coefficients, ratios, per-digit breakdowns
- Flag any number that's presented as precise but is actually single-seed

**Confounds and validity:**
- For each finding, list the confounds explicitly — could anything else explain this result?
- Check for train/test leakage: are any comparisons crossing the train/test boundary without noting it?
- Are baselines adequate? Could a simpler explanation account for the result?
- Scan experiment code for bugs: wrong tensor dimensions, off-by-one, incorrect labels

**Completeness:**
- *Experimental Velocity:* Have we run enough experiments? Are there obvious gaps?
- *Conceptual Understanding:* Does the writeup tell a clear mechanistic story? Does the reader understand *why*, not just *what*?
- *Correctness/Validity:* Any cherry-picking? Is the experiment log complete, including dead ends?
- *Reasoning Transparency:* Can the reader tell how much to trust each result?

**Dispatch any quick experiments** needed for CIs, additional baselines, or validation checks. These should be fast (<10 min each). Then shift to writing.


### Late check
Final experiments should be wrapping up. Shift focus from running experiments to polishing the writeup. Identify any quick experiments that could fill remaining gaps.


## Phase 3: Polish

The writeup should already be mostly written from Phase 2. This phase is for:

1. **Rewrite the executive summary** — Now that you have all results, rewrite the 2-3 paragraph summary. The draft from Phase 1 was a hypothesis; the final version tells the actual story with confidence levels. **Remove any "(draft)" tags.**
2. **Write the Discussion** — Synthesize across experiments. Confounds, limitations, what you'd do with more time.
3. **Ensure every claim has a confidence level** — Scan the Key Findings sections. Add calibrated language wherever it's missing.
4. **Signal importance** — Make sure the most important findings are visually and textually prominent. The reader should know within 30 seconds what matters most.
5. **Check the appendix** — Is the experiment log complete? Are all plots and tables included?
6. **Methodology section** — Fill in hardware, seeds, hyperparameters, package versions.
7. **Final read-through** — Read the executive summary and Key Findings as if you're the reviewer. Is it clear? Do confidence levels make sense? Would you trust this?
8. **Build and verify** — Run `exp-build` to assemble the deliverable bundle. Open the README, writeup, and PDF to verify everything renders correctly. Check image links, experiment links, and that no data is missing.

### Write-up Final Checking

A second pass through the improvements checklist, now focused on *text* rather than computation. Run this even if the 180-min check went well — text added during the writeup phase may have introduced new issues.

**Links and navigation:**
- Every key finding links to the supporting experiment spec(s) — reader can always dig deeper
- All figure paths resolve correctly (test by rendering the markdown)
- Experiment log entries link to experiment folders

**Caveats and confidence:**
- Every quantitative claim has a confidence qualifier (high/moderate/low) with justification
- Single-seed results are explicitly flagged
- Confounders are named proactively — don't wait for a reviewer to find them
- Cross-set comparisons (e.g., training soft labels vs test errors) are noted as limitations
- Multiple comparisons: if many statistical tests, note Bonferroni or equivalent

**Conclusions audit:**
- Re-read each conclusion and ask: is this justified by the evidence presented?
- Check for overstated claims — "proves" vs "suggests", "causes" vs "is consistent with"
- Ensure causal language is used only where the experiment design supports it
- Verify that no finding relies on a single number without corroboration from another analysis
- Check that the executive summary accurately reflects the findings (not the Phase 1 draft)
- Remove all "(draft)" and "TBD" markers

**Text consistency:**
- Do the numbered findings in the exec summary match the Key Findings section headings?
- Are experiment references consistent (same experiment numbers, same stats cited)?
- Do figures have descriptive alt text and are they referenced in the surrounding text?
- Has any new text been added without proper experiment links or confidence qualifiers?


## Building the Deliverable

```bash
source helpers/exp.sh
exp-build
```

This assembles the deliverable from the working directory:
- Copies `writeup.md` + all `NNN_*` experiment folders (code, results, plots — no checkpoints)
- Generates `README.md` index with links to writeup and each experiment
- Converts `writeup.md` → `writeup.pdf` via pandoc (inline images, clickable links)
- Creates a timestamped ZIP in `_builds/`
- Each build is a full backup — previous versions are preserved

Run `exp-build` periodically (at each pulse check) so you always have a recent snapshot. If a last-minute edit goes wrong, you can fall back to an earlier build.


## Phase Summary

| Phase | Focus |
|-------|-------|
| Frame | Read, discuss, agree on framing, draft exec summary |
| Execute round 1 | First experiments |
| Pulse #1 | Check direction, update exec summary draft |
| Execute round 2 | Core experiments |
| Pulse #2 | Midpoint re-vector |
| Execute round 3 | Fill gaps, emergent experiments |
| **Improvements Check** | **Quality audit — dispatch CI/validation experiments while there's still time** |
| Execute round 4 | Quick CI experiments, final gap-filling |
| Pulse #3 | Shift to polish |
| Polish | Rewrite exec summary, Discussion, fill methodology |
| **Final Check** | **Text consistency, links, caveats, conclusions audit** |
| Build + verify | exp-build, render check, finalize |
