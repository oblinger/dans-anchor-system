---
description: Per-task priority levels so dispatch is not strictly FIFO — higher-priority tasks jump the queue
---

# F4 — Priority Levels

## Open Questions

- **Q1 — Priority scale: ordinal (low/normal/high) or numeric (0-100)?** — context: ordinal is simpler; numeric is more flexible but invites bikeshedding over magic numbers.
  - (A) Ordinal — three or five buckets.
  - (B) Numeric 0-100 — fully ordered.
  - (C) Numeric with named constants (`Priority::HIGH = 200`, etc.).
  - **Recommendation:** Lean (A). Three buckets (low / normal / high) covers documented use cases; we can split later if needed.

- **Q2 — Starvation handling: aging or strict?** — strict priority can starve low-priority tasks indefinitely. Aging promotes a low-priority task after a wait threshold.
  - (A) Strict — high always wins; low may starve indefinitely.
  - (B) Aging — low-priority task ages up after waiting N seconds at the queue front.
  - **Recommendation:** Strong (B). Strict starvation is operationally surprising; aging is a small cost for predictability.

- **Q3 — Dispatch fairness across groups vs priority?** — when F2 Task Groups land, does priority-within-group win, or group-level fairness override priority?
  - (A) Priority within group — each group dispatches by priority internally; round-robin across groups.
  - (B) Global priority — high-priority task in any group jumps every queue.
  - (C) Defer this question — F2 not yet shipped; return when groups are in.
  - **Recommendation:** Strong (C). Don't design the cross-product before the components ship.

- **Q4 — API form: per-task field or per-submit method?** — submit signature.
  - (A) `submit(task, priority=Priority::HIGH)` — keyword argument with `Normal` default.
  - (B) `submit_with_priority(task, priority)` — separate method.
  - (C) Field on `Task` itself — `task.priority = Priority::HIGH; submit(task)`.
  - **Recommendation:** Lean (A). Keyword fits Rust idiom; keeps single submit signature with default.

- **Q5 — Should priority be observable in `status()` and the CLI `cae list` output?** — operators may want to see "5 high-priority tasks queued, 200 normal."
  - (A) Yes — extend `SchedulerStatus` with `queue_by_priority: HashMap<Priority, usize>`; `cae list` adds a `Pri` column.
  - (B) No — priority is an internal scheduling concern; visibility is yagni.
  - **Recommendation:** Lean (A). Operators have asked for this in similar systems; cheap to add at the same time we build dispatch.


## Summary

Allow tasks to declare a priority so urgent work doesn't sit behind routine work in the queue. Add a priority field to dispatch and a comparator-aware queue under the hood.

## Status

Designing — 5 open questions. Q3 explicitly defers until F2 ships.
