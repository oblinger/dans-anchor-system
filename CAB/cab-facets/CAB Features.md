---
description: dated feature design specs
---
# CAB Features

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Features/   (folder; one dated file per feature)`


Individual feature specifications, each in a dated file inside a Features subfolder.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Features/2026-04-21 Scheduler Pause.md` — demonstrates the Open-Questions-above-H1 convention.

Below is a condensed reference example.

# Reference Example
---

```
CAE Docs/CAE Plan/
└── CAE Features/
    ├── CAE Features.md                  ← feature index
    ├── 2026-03-15 Retry Logic.md
    └── 2026-04-02 Recurring Tasks.md
```

**CAE Features.md** (index, reverse chronological):

```markdown
- [[2026-04-02 Recurring Tasks]] — Cron-style recurring task schedules [proposed]
- [[2026-03-15 Retry Logic]] — Automatic retry with exponential backoff [done]
```

**2026-03-15 Retry Logic.md** (individual feature):

```markdown
---
description: Automatic retry with exponential backoff
---

## Open Questions

Blocking decisions. The feature cannot move from Designing → Agreed while
this list is non-empty.

- **Q2 — cap on max-retries?** — should there be an absolute upper bound,
  or can users set arbitrarily high values? Options: 100 absolute, user-configurable, no cap.

### Resolved

- **Q1 — jitter strategy?** — **Resolution:** full-jitter (delay * rand(0,1)).
  Incorporated into Design § Backoff.



# Retry Logic

## Summary

When a task fails, CAE automatically retries it using exponential backoff
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

## Status

Designing — awaiting resolution of Q2.
```

**Note the layout:** `## Open Questions` sits ABOVE the `# Retry Logic` H1. It is pre-document material — the first thing the user sees when opening the file. Resolved questions move to the H3 `### Resolved` subsection; they never get deleted.

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

The feature document has **two zones**:

1. **Pre-document zone (above the H1)** — `## Open Questions` and its `### Resolved` subsection. This is blocking material that must be visible the moment the user opens the file. It exists on every feature doc, even if empty.
2. **Document zone (H1 and below)** — the feature spec proper: Summary, Design, etc.

### Pre-document zone — always present

| Section | Level | Required | Purpose |
|---------|-------|----------|---------|
| `## Open Questions` | H2 above H1 | Always | Blocking decisions; feature cannot leave Designing while non-empty |
| `### Resolved` | H3 under Open Questions | Always (can be empty) | Answered questions move here with the resolution; never deleted |

When Open Questions is empty, leave the H2 with a one-liner placeholder (e.g. `_None — design is clean._`) — preserve the structure so the convention is visible.

**Workflow note:** every time an agent edits Open Questions — adds a question, resolves one, moves one to Resolved — it immediately runs `open "<path to this file>"` so the doc surfaces on the user's screen. The `/feature` skill's Runbook step 1a enforces this.

### Document zone — H1 and below

Start with only the mandatory sections; add optional sections as the feature grows in complexity.

**Mandatory:**
- **H1 `# [[{NAME}]] · F{n} — {Feature Name}`** — anchor-slug breadcrumb (wiki-link to anchor page) + F-number + title. The leading `[[{NAME}]]` lets the reader (a) jump back to the anchor page and (b) immediately see which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them. Filename matches without the `[[]]` brackets: `F{n} — {Feature Name}.md`.
- **Summary** — What the feature does and why it exists (1-2 paragraphs)
- **Status** — lifecycle state (Designing / Agreed / Implementing / Testing / Done)

**Optional (add as needed, H2 headings in document order):**
- **Interface** — Description of external interface (API, CLI, config, user, etc.)
- **Requirements** — Specific acceptance criteria or constraints
- **Design** — Technical approach, architecture decisions, trade-offs
- **Dependencies** — What this feature depends on or what it blocks
- **Roadmap** — Execution plan, phases, milestones. (See [[CAB Roadmap]] for details.)
- **Notes** — Working notes, research

---
