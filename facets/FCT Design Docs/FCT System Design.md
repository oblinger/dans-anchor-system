---
description: architecture and system design
---
# FCT System Design

Facet spec for `{NAME} System Design.md` — the current technical-architecture document (components, data model, decisions) for a software project anchor.

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} System Design.md`


The System Design document (`{NAME} System Design.md`) specifies the technical architecture, component boundaries, data models, and APIs for a software project. It contains the current design — not the history of how it was reached.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE System Design.md` — System Design.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE System Design

| -[[CAE System Design]]- | |
| --- | --- |
| --- | |


| TOC |  |
| --- | --- |
| 1 | Architecture Overview |
| 2 | Components |
| 3 | Data Model |
| 4 | Decisions |



## 1 Architecture Overview

CAE example uses a single-process, multi-threaded architecture. The CLI parses commands and delegates to the Scheduler, which manages a priority queue and a fixed-size thread pool.

```
CLI → Scheduler → PriorityQueue → WorkerPool → TaskResult
                       ↑
                  RetryManager (requeues failed tasks)
```



## 2 Components

| Component | Responsibility | Module |
|-----------|---------------|--------|
| **CLI** | Parse commands, format output | `cli.py` |
| **Scheduler** | Coordinate queue, pool, retries | `scheduler.py` |
| **WorkerPool** | Execute tasks in threads | `worker.py` |
| **RetryManager** | Backoff logic, dead-letter list | `retry.py` |
| **Clock** | Time source (injectable for tests) | `clock.py` |

### Scheduler
The scheduler is the central dispatch engine. It owns the priority queue and worker pool. All task submission, cancellation, and draining flows through the scheduler.

### RetryManager
On task failure, the retry manager computes the next deadline using exponential backoff capped at `3 × task_duration` for short tasks. After `retry_limit` attempts, the task moves to the dead-letter list.



## 3 Data Model

```python
@dataclass
class Task:
    id: str
    command: str
    deadline: datetime
    priority: int = 0
    attempt: int = 0

@dataclass
class TaskResult:
    task_id: str
    exit_code: int
    stdout: str
    duration: float
```



## 4 Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Thread pool over async | Shell subprocesses don't benefit from async; threads are simpler |
| D2 | UTC internally | Avoids timezone bugs; CLI handles local↔UTC conversion |
| D3 | Fixed pool size | Dynamic sizing adds complexity without measurable benefit at target scale |

---



# Format Specification

## Location

`{NAME} System Design.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Top of doc (canonical, per F060)

Every System Design opens with the standard top-of-doc format: YAML frontmatter + `# {NAME} System Design` H1 + dispatch-table placeholder. The **TOC**, **Components**, **Data Model**, and **Decisions** tables are all topic tables (the doc's payload) — they stay as distinct tables BELOW the dispatch table per F060 § Q5.

## Document Structure

### TOC
A table of contents at the top linking to major sections.

### Architecture Overview
High-level description of the system with an ASCII diagram showing component relationships and data flow.

### Components
A summary table listing each component, its responsibility, and its source module. Followed by H3 subsections for components that need detailed explanation.

### Data Model
Key data structures shown as code blocks (dataclasses, schemas, or equivalent).

### Decisions
A numbered table recording architectural decisions with rationale. Each decision is a short statement with a one-line justification. Extended analysis belongs in [[FCT Discussion]].

## Lifecycle

- **Create** after the PRD and Open Questions have stabilized enough to design against
- **Update** when architecture changes — this is the current spec, not a historical log
- **Decisions table** grows over time as new architectural choices are made
- **Current spec only** — rationale and alternatives belong in Discussion

# BRIEF

- **This file is the CAB facet spec for `{NAME} System Design.md`** — it defines the canonical shape (location, top-of-doc, TOC + Architecture Overview + Components + Data Model + Decisions sections) that every per-anchor System Design must conform to. Edits here propagate to every project anchor's design doc.
- **Spec, not an instance.** Do NOT pile real architecture content, real decisions, or real component tables here — those belong in per-anchor `{NAME} System Design.md` files (e.g. the CAE working example). The reference example shown inline is illustrative scaffolding only.
- **Inclusion test:** content belongs on this page only if it specifies *how System Design docs are shaped vault-wide* — section names, ordering, table formats, lifecycle rules, top-of-doc conventions. Anchor-local rules go in `{NAME} Rules.md` / `{NAME} Decisions.md`; rationale-and-alternatives narrative goes in [[FCT Discussion]] (cite, don't inline).
- **Load-bearing constraints:** the `{NAME} Docs/{NAME} Plan/` location, the four canonical H2 sections (Architecture Overview / Components / Data Model / Decisions), the F060 top-of-doc rule (YAML + H1 + dispatch-table placeholder above the topic tables), and the current-spec-only discipline (no historical log) — readers/auditors depend on each. Don't reorder, rename, or merge them without a coordinated update to CAE and any tooling that scans for these sections.
- **Sibling boundaries:** PRD belongs in [[FCT PRD]]; cross-cutting decisions and their rationale belong in [[FCT Decisions]] / [[FCT Discussion]]; user-facing UX belongs in [[FCT UX Design]]. Link sideways instead of restating their content here.
- **Working example is the ground truth for shape disputes** — when the inline reference example and `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE System Design.md` drift, update both in the same commit; CAE is the live exemplar this spec points readers at.
