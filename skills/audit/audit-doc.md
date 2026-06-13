# /audit doc — audit one document against the doc rule set

Takes a single markdown document and checks it against the **`R-doc` umbrella** — the doc-level facet rule sets ([[FCT Document]]: markdown hygiene, file-association, rule-set form, brief, discussion, log, messages). The doc-mode sibling of [[audit-anchor|/audit anchor]]: same [[F161 — Rule-driven audit engine — resolve, run, judge|F161]] engine, smaller facet set, targets are *regions within the file* rather than files in a tree.

## When to use

- `/audit doc <file>` — audit one named document.
- `/audit doc <file> dry` — report findings without writing the backlog row (per the `/audit` `dry` convention).
- Use for a standalone doc that isn't an anchor entry page — a spec, a brief, a rule-set page, a log. (An anchor's own documents are already covered when you run `/audit anchor`, which folds `R-doc` in for every doc it contains.)

## Mechanism — the F161 audit engine

Like `/audit anchor`, this skill does not hand-walk checks — it **drives `audit-plan`** in document mode, which resolves the `R-doc` umbrella's rules, binds them to the file, runs the mechanical ones by script, and emits the judgment residue for the agent.

Script: `~/.claude/skills/audit/scripts/audit-plan.py`.

```bash
P=~/.claude/skills/audit/scripts/audit-plan.py
"$P" <file> --mode doc --report --model <model-id>   # combined view (mechanical + residue count)
"$P" <file> --mode doc --run                         # mechanical verdicts only
"$P" <file> --mode doc --judge --model <model-id> --json   # the agent-judgment task manifest
"$P" --record-verdict --key <K> --status pass|fail --detail "…"   # persist one judged verdict
```

(`--mode doc` is auto-selected when the target is a `.md` file, so it can be omitted; pass it explicitly to force doc-level audit of a path the resolver might read as an anchor.)

## Runbook

1. **Resolve the document** — use the argument (a path). If it isn't a readable `.md` file, report and stop.
2. **Mechanical pass** — `audit-plan <file> --mode doc --run`; collect fail/error verdicts (the deterministic findings).
3. **Judgment pass** — `audit-plan <file> --mode doc --judge --model <model-id> --json` for the manifest of rules needing agent judgment. For each task: read its rule body (`flat_file` / `check_pattern` / `why`) and the document, decide pass/fail + a one-line reason, then persist with `audit-plan --record-verdict --key <task.key> --status <s> --detail "<reason>"`. For a large residue, dispatch tasks to workers (Agent tool, `subagent_type=general-purpose`); the verdict cache (rule + target + model) makes re-runs free.
4. **Report + backlog row** — `audit-plan <file> --mode doc --report` gives the combined summary. Per the `/audit` default (**audit reports, doesn't fix**), file the findings as state-clustered backlog rows per [[audit|SKILL.md]] § Backlog entry format — **unless `dry`**:
   - **Mechanical fail-verdicts → one `[Ready]` row** (spec-clear). Sub-bullets = each failed `(rule, region)` with the verdict detail.
   - **Judgment fail-verdicts needing user input → `[Questions]` row(s)** linking a feature doc holding the parked Qs.
   - All rows minted via `state task create` (never direct-edit the backlog), default horizon `Next`.

## Distinction from siblings

- **[[audit-anchor]]** audits a whole anchor (`R-anchor`, which *includes* `R-doc` for every document in the tree). `/audit doc` is scoped to one standalone file.
- **[[audit-markdown]]** runs the standalone markdown-hygiene rules library on arbitrary files; `/audit doc` runs the full `R-doc` facet set (hygiene is one part of it) through the F161 engine.

## Related

- Engine: [[F161 — Rule-driven audit engine — resolve, run, judge|F161]]; planner script `audit-plan.py`.
- Umbrella: `R-doc` (see [[FCT Document]] / the doc-facet `# RULESET` blocks).
- Anchor-level sibling: [[audit-anchor]].
