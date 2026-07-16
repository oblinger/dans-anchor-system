---
description: "the current technical-architecture document for a software project anchor"
---

# DAS System Design
Facet spec for `{slug} System Design.md` — the current technical-architecture document (components, data model, decisions) for a software project anchor.

| -[[DAS System Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS System Design](hook://p/DAS%20System%20Design) |
| --- | --- |
| Related | [[DAS PRD]],  [[DAS Decisions]],  [[DAS Discussion]],  [[DAS UX Design]],   |
| Examples | [[SKA System Design\|real anchor example]],   |
| Rules | [[R-fct-system-design]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** One per anchor. `{slug} System Design.md` lives in `{slug} Docs/{slug} Plan/` and records the *current* technical architecture — components, data model, APIs, and architectural decisions. Not a history log; rationale and alternatives belong in [[DAS Discussion]].

**Cardinality: one per anchor** — a software project anchor has exactly one System Design document at any given time.

The System Design document (`{slug} System Design.md`) specifies the technical architecture, component boundaries, data models, and APIs for a software project. It contains the current design — not the history of how it was reached.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE System Design.md` — System Design.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE System Design

| -[[CAE System Design]]- |  |
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

`{slug} System Design.md` lives in `{slug} Docs/{slug} Plan/`.

## Top of doc (canonical, per F060)

Every System Design opens with the standard top-of-doc format: YAML frontmatter + `# {slug} System Design` H1 + dispatch-table placeholder. The **TOC**, **Components**, **Data Model**, and **Decisions** tables are all topic tables (the doc's payload) — they stay as distinct tables BELOW the dispatch table per F060 § Q5.

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
A numbered table recording architectural decisions with rationale. Each decision is a short statement with a one-line justification. Extended analysis belongs in [[DAS Discussion]].

## Lifecycle

- **Create** after the PRD and Open Questions have stabilized enough to design against
- **Update** when architecture changes — this is the current spec, not a historical log
- **Decisions table** grows over time as new architectural choices are made
- **Current spec only** — rationale and alternatives belong in Discussion

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative shape is the body + `RULESET R-fct-system-design` above; the inline reference example is illustrative scaffolding only.)*

- **Spec, not an instance** — don't pile real architecture, decisions, or component tables here; those live in per-anchor `{slug} System Design.md` files (e.g. the CAE working example). Inclusion test: content belongs here only if it specifies *how System Design docs are shaped vault-wide* — section names, ordering, table formats, lifecycle, top-of-doc conventions. Anchor-local rules go in `{slug} Rules.md` / `{slug} Decisions.md`; rationale-and-alternatives narrative goes in [[DAS Discussion]] (cite, don't inline).
- **The load-bearing constraints are read by auditors and tooling** — the `{slug} Docs/{slug} Plan/` location, the four canonical H2s (Architecture Overview / Components / Data Model / Decisions), the F060 top-of-doc rule, and the current-spec-only discipline — so don't reorder, rename, or merge them without a coordinated update to CAE and any tooling that scans for these sections.
- **Sibling boundaries:** PRD → [[DAS PRD]]; cross-cutting decisions and rationale → [[DAS Decisions]] / [[DAS Discussion]]; user-facing UX → [[DAS UX Design]]. Link sideways, don't restate.
- **Working example is the ground truth for shape disputes** — when the inline reference example and `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE System Design.md` drift, update both in the same edit; CAE is the live exemplar this spec points readers at.
