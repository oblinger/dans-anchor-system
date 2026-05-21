
# EXP Experiment Flow

The lifecycle of a single experiment, from idea to integration. For the overall research cycle process, see [[EXP Master Flow]]. For worker-specific instructions, see [[EXP Worker Instructions]].

## Roles

- **Lead** — the main Claude session working with the user. Designs experiments, delegates to workers, reviews results, integrates into writeup, owns the roadmap.
- **Worker** — a Claude session on a remote GPU machine. Executes experiments: checks dependencies, writes code, runs it, writes up raw results.

## Experiment Naming Convention

Experiments are numbered by question: `Q1_01_name`, `Q2_01_name`, etc. The letter prefix is project-specific (Q, J, K, D, etc.) — pick one per project and use it consistently. Within each question group, sub-numbers are chronological. This groups related experiments together in the folder listing and appendix.

## Key Rules

- **Lead never executes experiments.** The lead designs, delegates, reviews, and integrates — but never runs `exp exe` or `python` to produce experiment results. Even if the lead does interactive exploration (e.g., iterating on a visualization approach with the user), the formal run and results writeup must be delegated to a worker via `exp zap`.
- **If the lead does run something** (e.g., a quick local sanity check), the lead is responsible for writing up the Results section in the experiment spec. Leaving Results empty after execution is not acceptable.
- **Error bars where appropriate.** When a metric is estimated from a subsample or could vary with different data (correlations, CKA, per-class stats on small N), add bootstrap CIs — it's cheap and adds rigor. Don't add error bars to deterministic metrics computed on the full dataset (overall accuracy, counts). Skip if it would noticeably slow the experiment. The lead should flag this in the spec when designing; the worker should add bootstrap when it's a few lines of code and won't slow the run.

## Lifecycle

### 1. Design — *Lead*
- Create spec from experiment template, resolve all open questions
- `peep` the spec so the user can review
- Update `ROADMAP.md` — add experiment, mark `[ ]`

### 2. Delegate — *Lead*
- `exp zap` the experiment to a worker
- Update `ROADMAP.md` — mark `[>]` (running)

### 3. Run & Results — *Worker*

Full instructions: [[EXP Worker Instructions]]. Summary:

- Read spec and project context
- Check and push dependencies to remote
- Write `code.py` if needed, run on remote via `exp exe`
- **Verify results were pulled locally** (check `output/` dir — re-pull if needed)
- Fill in Results, Key Findings, Discussion in the spec
- Include all figures inline in the spec
- **Complete `_EXECUTION.md`** in `output/` — fill in the completion fields, signals done to health system
- Do NOT open figures locally or update the roadmap

### 4. Review — *Lead* reviews results with user

One experiment at a time. Do not mix experiments.

1. `peep` the experiment spec — figures are inline, so the user reads results and sees figures in one document
2. Discuss findings — what does it show, does it make sense, any surprises
3. Note any follow-up experiments
4. Update `ROADMAP.md` — mark `[x]`, add result summary, update Key Findings
5. Check off in the "Review figures" To Do list

### 5. Integrate — *Lead*
- Pull key findings into `writeup.md` — Summary, relevant Q section, tables, discussion

## Roadmap Updates

The **lead** owns the roadmap. Update it at every lifecycle transition — not as a batch task. Workers don't touch the roadmap.

| Step | Owner | Roadmap action |
|------|-------|---------------|
| Design | Lead | Add experiment, mark `[ ]` |
| Delegate | Lead | Mark `[>]` (running) |
| Run | Worker | *(no roadmap update)* |
| Review | Lead | Mark `[x]`, add result summary, update Key Findings |
| Integrate | Lead | *(roadmap already updated)* |

## Experiment Updates / Reruns

When an experiment has already been run but needs to be changed and rerun:

1. **Lead edits the spec** — update the Approach, Config, Expected Outcomes, or any other section to reflect the new design
2. **Clear the Results section** — replace with `*To be completed by worker.*`
3. **Re-zap to a worker** — `exp zap` with the experiment folder. The worker reads the spec fresh and treats it as a new experiment. It does not need to know about the previous run.
4. **Update `ROADMAP.md`** — mark `[>]` again

The worker will see existing code in the folder and can modify it or rewrite it. Old output files get overwritten by the new run. No "Experiment Update" section or changelog is needed — the spec IS the current truth.
