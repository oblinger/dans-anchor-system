---
description: Group related tasks into named collections so operators can pause, drain, or query the entire group as one unit
---

# [[CAE]] · F002 — Task Groups

## Open Questions

- **Q1 — Group membership: static at submit time or dynamic via tags?** — context: do tasks declare their group when submitted (static), or do groups select tasks by tag-match (dynamic)? ^F002-Q1
  - (A) Static — `submit(task, group="ingest")`; immutable after submit. Simple, predictable.
  - (B) Dynamic — `group_define(name, filter)`; tasks with matching tags appear in the group. More flexible.
  - (C) Both — explicit group plus optional dynamic tag-filter overlay.
- **Recommendation:** Lean (A). Static is simpler; the dynamic case has historically been a yak-shave in similar systems.

- **Q2 — Pause semantics for groups: pause new dispatch only, or include in-flight cancellation?** — parallel to F001 Q2 for the global pause; do groups inherit the same semantics or have their own? ^F002-Q2
  - (A) Same as F001 — pause new dispatch, in-flight runs to completion. Operator opts into hard-stop separately if needed.
  - (B) Group-pause is harder — pause + cancel in-flight tasks belonging to the group.
- **Recommendation:** Lean (A). Match F001 for consistency; "harder pause" is a separate feature if it ever shows up.

- **Q3 — Visibility: should `status()` decompose by group, or expose only aggregate?** — operators may want per-group queue depth. ^F002-Q3
  - (A) Aggregate only — `status()` returns total queue depth; per-group is via `group_status(name)`.
  - (B) Decomposed — `status()` returns a map keyed by group.
- **Recommendation:** Strong (A). Aggregate stays cheap; group-level callers ask explicitly.

- **Q4 — UI rendering of task groups in `cae list`** — how does the CLI display grouped tasks? ^F002-Q4
  - (A) Flat list with a `Group` column.
  - (B) Nested by group with a tree-style indent.
  - (C) Filtered view: `cae list --group=ingest` (default flat, opt-in filter).
- **Recommendation:** Lean (C). Default is flat; users opt into per-group filter.


## Summary

Add named groups so multiple related tasks can be controlled and observed as one unit — pause an entire group, drain it before maintenance, query its queue depth.

## Interface (proposed; pending Q1)

```rust
impl TaskScheduler {
    pub fn submit(&self, task: Task) -> TaskId;
    pub fn submit_to_group(&self, task: Task, group: &str) -> TaskId;
    pub fn group_pause(&self, group: &str);
    pub fn group_resume(&self, group: &str);
    pub fn group_status(&self, group: &str) -> GroupStatus;
}
```

## Status

Designing — 4 open questions. Cannot move to Agreed until Q1 (membership model) is locked.
