---
description: skill-script — facet defining the scripts/ folder of a Skill Anchor. Python (preferred) or Bash; shebang + docstring; CLI args via argparse; logging to stderr.
applies-when-trait: Skill Anchor
location: ~/.claude/skills/<skill-folder>/scripts/
---

# CAB skill-script

The skill-script facet specifies *how a Skill Anchor packages and invokes its scripts — a `scripts/` folder under the skill directory, Python (preferred) or Bash, each script self-documenting, CLI args via argparse, logging to stderr.* What distinguishes a conformant script surface from one-off shell snippets:

- **Standard location** — `~/.claude/skills/<skill-folder>/scripts/<name>.py` (or `.sh`).
- **Python preferred** — when complexity exceeds 50 lines, Bash gives way to Python. The `audit-q.py`, `backlog-edit.py`, `triage-section.py` precedents are the model.
- **Self-documenting** — shebang first line; module-level docstring explaining purpose and inputs; argparse for CLI args; `--help` works.
- **stdout = result, stderr = log** — the script's verdict / output goes to stdout; progress, warnings, and informational messages go to stderr. Composable in pipelines.
- **Non-zero exit on failure** — script exits 0 only when its core task succeeds.
- **Read-only by default; mutations behind a flag** — scripts that modify state require `--fix` / `--apply` / equivalent; default invocation is dry-run / report-only.

This is a CAB facet of the Skill trait. The scripts/ folder lives at the runtime location (skill folder), not under the anchor's filesystem folder.


## Layout

```
~/.claude/skills/<skill>/scripts/
├── <name>.py            Python scripts (preferred for >50-line complexity)
├── <name>.sh            Bash scripts (preferred for thin OS-call wrappers)
└── __pycache__/         (auto-generated; gitignored)
```


## Conventions

- **Python shebang**: `#!/usr/bin/env python3` (uses system python3).
- **Bash shebang**: `#!/usr/bin/env bash`.
- **Module docstring** — describes purpose, inputs, outputs, side effects. Read by `--help` and by future maintainers.
- **`argparse`** for CLI args — no `sys.argv` manual parsing. Every flag has a help string.
- **Logging via `print(..., file=sys.stderr)` or `logging` module** — never to stdout when stdout is the result channel.
- **Default to dry-run** — mutation flags are opt-in (`--fix`, `--apply`).
- **Non-destructive on early exit** — partial work is rolled back or never committed.


## Reference instances

- `~/.claude/skills/audit/scripts/audit-q.py` — multi-rule auditor; canonical large Python script
- `~/.claude/skills/workflow/scripts/backlog-edit.py` — backlog mutator; canonical CLI tool
- `~/.claude/skills/md/md-toc.py` — TOC regenerator; canonical single-purpose script


## Conformance

A Skill Anchor carries this facet when it has a `scripts/` folder with at least one conforming script. Optional — most skills are pure runbook + no scripts; complex skills (audit, workflow, md) have scripts.


## Migration note (F116)

Reserved by the prior `skill-trait/` planning (`SKA skill-trait script` was a planned-but-empty entry). F116 v1 ships this as a populated facet spec.
