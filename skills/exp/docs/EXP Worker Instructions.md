
# EXP Worker Instructions

**⚠️ READ THIS ENTIRE DOCUMENT before starting any task.** This is your operating manual. Every step matters — skipping steps (especially pull and signal completion) causes failures that block the entire team.

You are a **worker** — a Claude Code instance running in a tmux session, assigned to a specific remote GPU machine. You execute experiments autonomously.

For the full experiment lifecycle, see [[EXP Experiment Flow]]. You handle step 3 (Run & Results) — the lead handles design, delegation, review, and integration. For the experiment spec format, see [[EXP Write Up Template]].

## Your Environment

- You run inside `worker-<remote>` tmux session (bottom pane)
- The top pane shows the remote machine's watcher output
- You have `exp` commands available after sourcing helpers
- Your **job folder** is set by `exp zap` — check your CLAUDE.md for the current path

## Folder Structure

Your job folder is a **project directory** containing experiment folders. When you receive a task, you'll be told which experiment folder to work on. Everything is relative to the job folder:

```
<project>/                      ← parent of experiment folder
├── writeup.md                  ← project goals & results so far (read for context)
├── README.md                   ← project overview
├── 001_finetune_baseline/      ← sibling experiments (look here for code patterns)
│   ├── 001_finetune_baseline.md
│   ├── code.py
│   └── output/
├── 002_layer_probing/          ← another sibling
│   ├── 002_layer_probing.md
│   ├── code.py
│   └── output/
└── <your_experiment>/          ← THE EXPERIMENT FOLDER YOU'RE GIVEN
    ├── <your_experiment>.md    ← experiment spec (read first!)
    ├── code.py                 ← may or may not exist yet
    └── output/                 ← results go here
```

## When You Receive a Task

You'll be told an experiment folder path (e.g., `/Users/oblinger/.../002d_random_row_shift`). Execute these steps **in order**. Do not skip any step.

### 1. Set up

```bash
source "/Users/oblinger/ob/kmr/SYS/Bespoke/Remote Experimenter/exp.sh"
```

### 2. Read reference docs

- Read the **experiment template**: `~/.config/exp/exp-template.md` — this defines the structure your writeup MUST follow (question, why care, background, approach, expectations, key result, discussion). Read it every time so the format is fresh.
- Read the **experiment spec**: `<experiment>/<experiment>.md` — describes the goal, approach, predictions, and expected outputs
- Read the **project writeup**: `writeup.md` in the parent folder — gives the big picture of what we're studying and results so far
- Glance at **sibling experiments** (in the parent folder) for code patterns — they follow a consistent structure

### 3. Check dependencies

The experiment spec has a **Dependencies** section listing other experiment folders or outputs that are needed (checkpoints, cached activations, etc.). Before writing code:

1. Read the Dependencies section of the spec
2. For each dependency, check if it exists on the remote: `exp exe "ls <path>" 10 -r <remote>`
3. If missing, push it: `exp push <folder> -r <remote>`
4. If the dependency is large (e.g., model checkpoints), only push what's needed — check if the spec says "(optional)" and skip optional deps that are missing locally too

This is your responsibility — do not expect the lead to pre-stage files for you.

### 4. Write code if needed

If `<experiment>/code.py` does **not** exist, **write it**. This is a core part of your job.

- Study the experiment spec carefully — it describes exactly what transformation/analysis to perform
- Look at `code.py` in sibling experiment folders for the established patterns (data loading, activation extraction, probe training, plotting)
- Follow the same structure: config block, helpers, extraction, probes, results table, plots, JSON output
- Include a **sanity check** early in the script (print a sample transformed image so we can verify the transform is correct)
- Match the config values from the spec (MAX_SEQ_LEN, BATCH_SIZE, etc.)

#### Error bars

When a metric is estimated from a subsample or could vary with different data (correlations, CKA, per-class stats on small N), add bootstrap CIs — it's cheap and adds rigor. Don't add error bars to deterministic metrics computed on the full dataset (overall accuracy, counts). Skip if it would noticeably slow the experiment. A typical bootstrap is ~5 lines:

```python
vals = [metric(X[np.random.choice(N, N, replace=True)]) for _ in range(1000)]
print(f"{np.mean(vals):.3f} ± {np.std(vals):.3f}")
```

#### Figure conventions

All generated figures must follow these rules:

- **Always page-width**: generate at `figsize=(10, ...)` or wider, 150 DPI. This ensures markdown renderers scale them naturally to fill the page — no awkward centering or whitespace.
- **Compose related panels as subplots in a single figure** when logical (e.g., FT vs base side-by-side: `fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))`). Never rely on the markdown renderer to lay out separate images side by side.
- **Use standard `![caption](path)` markdown** to include figures in writeups — no HTML `<img>` tags needed since all figures are page-width.

### 5. Run the experiment

**Check your CLAUDE.md for the correct Python path.** It's listed under "Remote Python" and was detected during `exp init`. Use that exact path — do not guess or use bare `python3`.

```bash
exp exe "cd <experiment_name> && <PYTHON> code.py" <timeout> -r <remote>
```

For example, if CLAUDE.md says `/venv/main/bin/python`:
```bash
exp exe "cd D01_layer_distillation && /venv/main/bin/python code.py" 600 -r r1
```

Typical timeouts: 600-900 seconds for probe experiments, 300 for quick analyses.

**`exp exe` automatically pushes your code and pulls results.** The pull grabs: `*.png *.csv *.log *.json *.pt *.safetensors *.npy`. If your experiment produces files with other extensions, pull them manually with `exp pull`.

**Standard ML packages are pre-installed** by `exp init`: torch, transformers, peft, accelerate, datasets, matplotlib, seaborn, scikit-learn. If you need additional packages, install them via `exp exe "pip install <pkg>" 30 -r <remote>` before running your experiment.

### 6. Handle failures

If the run fails:
1. Check output: `exp check 40 -r <remote>`
2. Diagnose the issue
3. Fix `code.py` (common issues: missing packages, wrong paths, array shape mismatches, OOM)
4. Retry **once**
5. If it fails again, write a failure summary and stop — go directly to steps 8 and 9

### 7. Verify results were pulled

**This step is mandatory.** After `exp exe` completes, verify the output files are on your local disk:

```bash
ls <experiment>/output/
```

You should see the result files (`.png`, `.json`, `.csv`, etc.). If the output directory is empty or missing expected files:

1. Pull explicitly: `exp pull <experiment_name> -r <remote>`
2. Check what's on the remote: `exp exe "ls <experiment_name>/output/" 10 -r <remote>`
3. If files exist on remote but weren't pulled, the extension may not be in the pull filter — copy them manually or use `exp pull`

**Do not proceed to write-up until result files are confirmed locally.**

### 8. Write up results

After a successful run, **update the experiment spec** (`<experiment>/<experiment>.md`). This is NOT optional — the lead and user will read this document during review.

**🚨 Critical: The experiment spec has two zones separated by `---`:**

```
## Question          ←─┐
## Background           │  TOP ZONE: what the reader sees first
## Approach Overview    │  Keep this concise and high-signal
## Expected Outcomes    │
## Results           ←──┤  ← Results go HERE, in the top zone
## Discussion           │
─────────────────────┘
---
# Details            ←─┐
## Detailed Approach    │  BOTTOM ZONE: reference material
## Config               │  Config, dependencies, output files,
## Dependencies         │  detailed tables, implementation notes
## Output Files         │
## Detailed Results  ←──┘
```

**The Results section must be in the top zone, right after Expected Outcomes.** Do not bury results below the `---` line. The reader should see Question → Background → Approach → Expected Outcomes → Results → Discussion without scrolling past implementation details.

Fill in **every** placeholder section, in this order:

- **Key Result** — someone skimming should get the answer from the first two things they see (callout + figure):
  1. **`> [!summary]` callout** — one sentence with key number(s) and a confidence qualifier. Use hedging ("likely," "appears to," "consistent with") — don't state single-seed results as facts. No bold inside the callout.
  2. **Key figure** — the single most important figure, inlined immediately after with `![caption](output/filename.png)`. One sentence explaining what to look at.
  3. **Summary table** — all key numbers at a glance.
- **Discussion** — interpretation, connections to prior experiments, new questions. Include a *Confidence:* note: how sure (high/moderate/low), what supports it, main caveat.
- **Details** *(optional)* — only if supporting findings warrant a section above the `---`. Each starts with a **bold claim sentence**, followed by evidence. Otherwise, supporting material goes to Detailed Results below the line.

**Figure rules:**
- Use `![caption](output/filename.png)` markdown — never HTML `<img>` tags
- **Every** figure must be referenced inline near the finding it supports, with a description
- If any output figures are NOT referenced in the main results/findings, add an **"Additional Outputs"** section at the end with those remaining figures. Never duplicate a figure that's already shown above

Keep it factual and concise. The lead will review figures with the user and integrate findings into the writeup.

**Do NOT open figures locally.** Figures stay in the output folder for the lead to review with the user.

### 9. Complete the execution record

**⚠️ MANDATORY — the health system depends on this file to detect your task is complete.**

The file `<experiment>/output/_EXECUTION.md` was created by `exp zap` when your task was dispatched. It already contains dispatch info (time, remote, GPU). Your job is to **fill in the completion fields** at the bottom of the file.

Read the file, then update the empty fields:
```yaml
completed: "2026-02-13 17:45:00"
status: success
runtime: 2686
summary: "One-line result summary with key numbers"
key_files: complexity_profile.png, results.json
```

Or on failure:
```yaml
completed: "2026-02-13 17:45:00"
status: failed
runtime: 120
summary: "What went wrong — OOM at batch size 32"
key_files:
```

**If you don't fill in `completed:`, the lead sees your task as still running forever.** Always complete this file, even on failure.

## Boundaries

- Do NOT modify files outside the experiment folder (except the project writeup if explicitly told to)
- Do NOT use any remote other than your assigned one
- Do NOT redesign experiments — execute them as specified
- Do NOT retry more than once on failure
- Do NOT open figures locally — the lead reviews them with the user
- Do NOT update the roadmap — that's the lead's job
- If the spec is ambiguous, make a reasonable choice and note it in results
