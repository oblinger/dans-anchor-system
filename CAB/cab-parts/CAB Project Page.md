# CAB Project Page

A lightweight public-facing splash page for an anchor, published to the personal website (oblinger.github.io). Built via the `/code publish` skill.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

```
Task Runner/
└── website/
    ├── index.md
    └── deploy.sh
```

**index.md:**

```markdown
---
layout: cayman
title: Task Runner
description: CLI tool for scheduling and running deferred shell tasks
permalink: /gitproj/task-runner/
---

# Task Runner

Schedule shell commands to run later with priority queuing, automatic retry,
and a simple CLI interface.

## Install

pip install task-runner

## Quick Start

tsk add "python train.py" --at "2026-04-01 02:00" --pri 8
tsk list
tsk status 1
```

**deploy.sh:**

```bash
#!/bin/bash
set -euo pipefail
DEST="$HOME/ob/proj/oblinger.github.io/gitproj/task-runner"
mkdir -p "$DEST"
cp -r . "$DEST/"
cd "$DEST/.." && git add task-runner && git commit -m "Update task-runner page" && git push
```

---



## When to Use

- Any anchor with a code repository that should have a public presence
- Projects that need a landing page but don't warrant a full documentation site
- Open source projects, portfolio pieces, tools shared with others

## Location

The project page lives in a `website/` directory inside the anchor (vault side, not repo side):

```
{CAB Folder}/
├── {NAME}.md
├── CLAUDE.md
├── {NAME} Docs/
├── Code -> ~/ob/proj/...
└── website/                      project page source
    ├── index.md                  splash page with Jekyll front matter
    ├── [additional .md]          extra pages (if any)
    ├── [assets/]                 images, PDFs (if any)
    └── deploy.sh                 copy to website repo and push
```

## Jekyll Front Matter

Each `.md` file uses the cayman layout:

```yaml
---
layout: cayman
title: {PROJECT NAME}
description: {ONE-LINER}
permalink: /gitproj/{SLUG}/
---
```

## Publishing

Published to `oblinger.github.io/gitproj/{SLUG}/` and linked from the projects hub at `/gitproj/`. See [[code-publish]] for the full workflow, questions checklist, and deploy steps.

## Dispatch Table Entry

The project page URL appears in the **External** row of the anchor's dispatch table:

```markdown
| External | [Repo](https://github.com/oblinger/{repo}), [Project Page](https://oblinger.github.io/gitproj/{SLUG}/) |
```

## Relationship to Documentation Site

- **Project Page** — simple splash, one or a few pages, Jekyll/cayman
- **[[CAB Documentation Site]]** — full doc site with navigation, search, API docs (MkDocs/Material)

An anchor can have both: a project page for the public landing, and a documentation site for detailed reference.
