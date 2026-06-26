---
description: "CI/CD pipeline from push to production, with test/approval gates, a rollback branch, a merge, and a flaky-test retry loop."
---
# 09 — Flowchart with decisions

**Diagram kind:** Flowchart with decisions.
**Layout challenge:** routing diamond decision nodes with multiple labeled out-edges, a branch that splits and later merges back, a backward loop-back edge (retry) that must not tangle with the forward flow, and a terminal failure branch — all kept legible without crossing edges piling up.
**Domain:** A CI/CD pipeline that takes a developer's `git push` through build, automated tests (with a flaky-test retry), manual approval, deploy, smoke check, and either promotion to production or automatic rollback.

## Nodes
- start — "Developer pushes commit" [start / terminator (rounded)]
- build — "Build & compile artifact" [process]
- build_ok — "Build succeeded?" [decision (diamond)]
- unit_tests — "Run unit + integration tests" [process]
- tests_pass — "Tests pass?" [decision (diamond)]
- flaky_check — "Failure flaky?" [decision (diamond)]
- approval — "Await manual approval" [process]
- approved — "Approved?" [decision (diamond)]
- deploy_staging — "Deploy to staging" [process]
- smoke — "Run smoke tests" [process]
- smoke_ok — "Smoke tests pass?" [decision (diamond)]
- promote — "Promote to production" [process]
- rollback — "Auto-rollback staging" [process]
- notify_fail — "Notify team of failure" [process]
- done_success — "Pipeline complete (deployed)" [end / terminator (rounded)]
- done_fail — "Pipeline failed (no deploy)" [end / terminator (rounded)]

## Edges
- start → build : "" [solid]
- build → build_ok : "" [solid]
- build_ok → unit_tests : "yes" [solid]
- build_ok → notify_fail : "no" [solid]
- unit_tests → tests_pass : "" [solid]
- tests_pass → approval : "yes" [solid]
- tests_pass → flaky_check : "no" [solid]
- flaky_check → unit_tests : "yes — retry" [dashed]
- flaky_check → notify_fail : "no" [solid]
- approval → approved : "" [solid]
- approved → deploy_staging : "yes" [solid]
- approved → notify_fail : "no" [solid]
- deploy_staging → smoke : "" [solid]
- smoke → smoke_ok : "" [solid]
- smoke_ok → promote : "yes" [solid]
- smoke_ok → rollback : "no" [solid]
- rollback → notify_fail : "" [solid]
- promote → done_success : "" [solid]
- notify_fail → done_fail : "" [solid]

## Groups / lanes / cardinality
- No swimlanes. Single connected flow with one entry (`start`) and two terminal sinks (`done_success`, `done_fail`).
- `notify_fail` is a shared merge point: four distinct failure edges converge on it (`build_ok` no, `flaky_check` no, `approved` no, `rollback`), then one edge proceeds to `done_fail`.
- `flaky_check → unit_tests` is the single backward loop-back (retry) edge; it is the only edge that flows against the overall forward direction. Drawn dashed to mark the retry semantics.
- Each diamond has exactly the out-edges enumerated (build_ok: 2, tests_pass: 2, flaky_check: 2, approved: 2, smoke_ok: 2); no implicit defaults.

## Acceptance
- Fidelity: the render contains exactly these 16 nodes and 19 edges (count + labels match); none added or dropped. All five decision diamonds keep their exact branch labels (yes/no, "yes — retry"); the four-way merge into `notify_fail` and the single dashed loop-back edge are both present.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
