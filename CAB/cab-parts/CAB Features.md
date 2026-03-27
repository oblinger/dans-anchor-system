# CAB Features

Individual feature specifications, each in a dated file inside a Features subfolder.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

```
TSK Docs/TSK Plan/
└── TSK Features/
    ├── TSK Features.md                  ← feature index
    ├── 2026-03-15 Retry Logic.md
    └── 2026-04-02 Recurring Tasks.md
```

**TSK Features.md** (index, reverse chronological):

```markdown
- [[2026-04-02 Recurring Tasks]] — Cron-style recurring task schedules [proposed]
- [[2026-03-15 Retry Logic]] — Automatic retry with exponential backoff [done]
```

**2026-03-15 Retry Logic.md** (individual feature):

```markdown
## Summary

When a task fails, TSK automatically retries it using exponential backoff
with jitter. This eliminates manual re-queuing for transient failures
(network timeouts, resource contention). The user configures max retries
and base delay per task or globally.

## Requirements

- Max retry count configurable per task (default: 3)
- Exponential backoff: delay = base * 2^attempt + jitter
- Tasks marked `failed` after exhausting retries
- Retry history visible in `tsk status <id>`

## Design

Retry state stored in the task record: attempt count, next retry time,
last error. The scheduler checks retry-eligible tasks each tick and
re-enqueues them at the computed delay.
```

---



## Features Folder Structure

Features are documented in their own subfolder within `{NAME} Docs/`:

```
{NAME} Docs/
└── {NAME} Features/
    ├── {NAME} Features.md               ← feature index (reverse chronological)
    ├── 2026-01-15 User Auth.md          ← individual feature
    ├── 2026-01-22 Dark Mode.md
    └── 2026-02-03 Export CSV.md
```

## Features Index Page

The `{NAME} Features.md` page lists all features in reverse chronological order (newest first):

```markdown
- [[2026-02-03 Export CSV]] — Export data to CSV format [proposed]
- [[2026-01-22 Dark Mode]] — Theme support for dark mode [in progress]
- [[2026-01-15 User Auth]] — User authentication via OAuth [done]
```

- **FILE NAME** - Each feature is a dated file using the format `YYYY-MM-DD Feature Name.md`, with the date indicating when the feature was introduced or documented.
- **FEATURE STATUS** - Status (`proposed` | `in progress` | `done` | `cut`) is tracked on the features index page, not in the feature document itself.


## Feature Document Format

Each feature document is a mini PRD. Start with only the mandatory sections; add optional sections as the feature grows in complexity.

**Mandatory:**
- **Summary** — What the feature does and why it exists (1-2 paragraphs)

**Optional (add as needed, H2 sections headings in document order):**
- **Open Questions** --
- **Roadmap** — Execution plan, phases, milestones.   (See [[CAB Roadmap]] for details.)
- **Summary** -- This is the mandatory summary section.  Below this is the spec, above this is for execution.
- **Interface** -- Description of external interface (API, CLI, config, user, etc.)
- **Requirements** — Specific acceptance criteria or constraints
- **Design** — Technical approach, architecture decisions, trade-offs
- **Dependencies** — What this feature depends on or what it blocks
- **Notes** — Open questions, working notes, research

---
