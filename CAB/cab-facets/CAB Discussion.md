---
description: design discussions and decisions
---
# CAB Discussion

The Discussion file (`{NAME} Discussion.md`) captures extended reasoning about design choices, trade-offs, and redesign decisions. Unlike the other design documents (PRD, UX Design, System Design), this file is a log — it records the "why" and "what we considered," not the current spec.

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

# TSK Discussion

This document captures design reasoning, exploration, and analysis that shaped TSK's architecture and interface. Each section records a specific design conversation with the problem, options considered, and final decision.



## 2026-02-26 — Thread Pool vs Async for Task Execution

### The Problem
TSK needs to run shell commands concurrently. The two standard approaches are thread pools (one thread per running task) and async I/O (event loop with subprocess management).

### Options Considered
- **A. Thread pool** — Simple, well-understood. Each worker thread calls `subprocess.run()`. Blocking is fine because each thread is dedicated to one task.
- **B. Async with asyncio** — Non-blocking subprocess management via `asyncio.create_subprocess_exec()`. More scalable in theory but adds complexity for shell command management.

### Decision
Thread pool (Option A). At our target scale (10-50 concurrent tasks), threads are simpler and the async overhead buys nothing. Shell subprocesses are inherently process-bound — async's advantage is in I/O-bound workloads.

### Why This Works
- `subprocess.run()` is the simplest, most debuggable way to run shell commands
- Thread pool size is fixed at construction — no dynamic scaling complexity
- Testing is straightforward with injectable Clock and mock subprocesses



## 2026-02-20 — Deadline Representation: UTC vs Local

### The Problem
Users think in local time ("run at 2am tonight") but storing local times creates timezone bugs, especially across DST transitions.

### Decision
Store all deadlines as UTC internally. The CLI accepts local time input and converts on ingestion. Display always shows local time. This is the standard approach and avoids every known timezone pitfall.

---



# Format Specification

## Location

`{NAME} Discussion.md` lives in `{NAME} Docs/{NAME} Plan/`.

## Document Structure

### Header
One paragraph explaining what this document captures.

### Entries
Each discussion is an H2 dated section: `## YYYY-MM-DD — Topic Title`

Each entry includes:
- **The Problem** — What question or tension prompted the discussion
- **Options Considered** — Lettered alternatives with brief descriptions
- **Decision** — What was chosen
- **Why This Works** (optional) — Additional rationale when the decision is non-obvious

### Relationship to Other Docs
- Decisions made here get reflected in the relevant spec doc (System Design, UX Design, PRD)
- Open Questions that spark extended analysis get a Design Discussion entry
- The Discussion file links back to the resolved question or updated spec

## Lifecycle

- **Create** when the first design question requires more analysis than fits in Open Questions
- **Append** new entries in reverse chronological order (newest first)
- **This is a log** — entries are never edited after the decision is made, unlike the spec documents which always reflect current state
- **Optional** — small projects may not need this file if Open Questions captures enough context
