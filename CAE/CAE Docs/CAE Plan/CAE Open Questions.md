---
description: unresolved decisions
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Plan]]

# CAE Open Questions

Unresolved decisions. Each gets an ID; answered questions are moved to the **Resolved** section with the outcome and which design doc it updated.


## Open

### Q3 — Task persistence format

**Question:** Should the TaskStore use SQLite or a simpler JSON-lines file?

**Context:** SQLite gives us transactions and concurrent reads. JSONL is simpler and easier to inspect but requires a file lock.

**Blocking:** M4 milestone.


### Q4 — Max retry limit as default?

**Question:** What is a reasonable default for `retry_limit` when the caller doesn't specify?

**Options:**
- `3` — safe default, matches common patterns
- `0` — retries must be opt-in (safer, but requires callers to think)
- `None` — no default, force explicit choice at submit time

**Leaning:** Force explicit. Defaulting to 3 hides retry policy from the caller.



## Resolved

### Q1 — Thread pool or async runtime?

**Resolution:** Thread pool. Tasks are shell commands, not I/O-bound Rust code. Async would add complexity without benefit.

**Recorded in:** [[CAE System Design]] D2.


### Q2 — Single queue or per-priority-level queues?

**Resolution:** Single queue with age-based promotion. Recorded as rule [[CAE Rules#R01 — One Queue, One Clock\|R01]].

**Recorded in:** [[CAE System Design]] D3, [[CAE Rules]] R01.
