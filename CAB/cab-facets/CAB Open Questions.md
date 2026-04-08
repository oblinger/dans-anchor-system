---
description: unresolved decisions and questions
---
# CAB Open Questions

The Open Questions file (`{NAME} Open Questions.md`) tracks unresolved questions that block or inform design decisions. Questions are numbered, analyzed with options, and resolved with a recorded decision.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK Open Questions



## Active

### 7. Should retry backoff be linear or exponential for short tasks?
**Source:** [[TSK Inbox#2026-02-28]]

Tasks under 10 seconds feel over-penalized by exponential backoff. A 2-second task that fails waits 4s → 8s → 16s, which is disproportionate.

**Options:**
- **A. Cap exponential** — Keep exponential but cap at `min(backoff, 3 × task_duration)`. Simple, preserves existing behavior for long tasks.
- **B. Linear for short tasks** — Use linear backoff when estimated duration < 10s. Adds a threshold parameter.
- **C. Configurable per-task** — Let the user specify backoff strategy per task. Most flexible but most complex.

**Recommendation:** Option A — minimal change, addresses the specific complaint.



## Resolved

### 1. Thread pool or async?    `RESOLVED → System Design`
**Decision:** Thread pool. Async adds complexity for shell subprocess management with no meaningful throughput benefit at our scale. See [[TSK System Design#Thread Pool Sizing]].

### 2. How to handle timezone-aware deadlines?    `RESOLVED → PRD US-1`
**Decision:** All deadlines are UTC internally. CLI accepts local time and converts on input. See [[TSK PRD#US-1]].

---



# Format Specification

## Location

`{NAME} Open Questions.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Document Structure

### Sections
- **Active** — Questions currently under consideration
- **Resolved** — Questions that have been decided (kept as a record)

### Question Format
Each question is an H3 with a sequential number and descriptive title:
`### 7. Should retry backoff be linear or exponential?`

Active questions include:
- **Source** — Where the question originated (link to Inbox, Design Discussion, etc.)
- **Context** — 1-2 sentences explaining why this matters
- **Options** — Lettered alternatives (A, B, C) with brief pros/cons
- **Recommendation** — Which option is preferred and why

Resolved questions include:
- **Decision** — What was decided and a link to where the decision is reflected

### Numbering
Questions are numbered sequentially and never renumbered. Gaps in the Active section are normal — they indicate resolved questions that moved down.

## Lifecycle

- **Create** early in the design process, after the initial PRD draft
- **Add questions** as unknowns surface during design
- **Resolve** by recording the decision and moving the question to the Resolved section
- Questions that spark extended discussion get a dedicated entry in [[CAB Discussion]]
