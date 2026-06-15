---
description: "CAE Testing — strategy + proposed-tests overview"
status:: drafting
---
# CAE Testing
How the CAE Example CLI is verified: the kinds of test, how much of each, and the concrete inventory consistent with that strategy.

| -[[CAE Testing]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [[CAE Design]] → [CAE Testing](hook://p/CAE%20Testing)<br>: test strategy + proposed tests |
| --- | --- |
| Anchor | [[CAE Design]] (parent) |
| Related | [[CAE PRD]],  [[CAE Architecture]],  [[CAE Decisions]],  [[DSC verification]],   |

**TLDR**
- **Heavy unit + integration** — modest e2e, property-based for two load-bearing invariants. No smoke, perf, or fuzz in v1.
- **Determinism by design** — single-process scheduler; `Clock` is injectable (D01, D03), no test reads wall time.
- **Unit bar** — every public function in `src/execution/`, `src/retry/`, `src/store/`, `src/clock/` has a golden-path test.
- **Integration bar** — every subsystem boundary from [[CAE Architecture]] has a test (4 boundaries → 4 tests).
- **E2E bar** — exactly one per user story in [[CAE PRD]] (3 stories → 3 tests).

## Overview

CAE is a single-process CLI scheduler with four small subsystems (Scheduler, TaskStore, RetryManager, Clock) and a SQLite-backed coordination surface. The testing posture is **heavy unit + integration, modest e2e**: the subsystems are pure enough to unit-test exhaustively, integration tests cover the four subsystem boundaries, and one e2e per user story exercises the CLI surface end-to-end. Determinism is bought once — via the injectable `Clock` trait (D01, D03) — and reused everywhere; no test depends on wall-clock timing.

## Strategy

### Test Kinds

- **Unit** — pure-function or single-component tests with no I/O beyond an in-memory SQLite or `TestClock`. The default kind; most tests are here.
- **Integration** — exercise the boundary between two or more subsystems with real internal dependencies (real SQLite, real `RetryManager`) and a `TestClock` for time. Run in CI.
- **End-to-end** — invoke the `cae` binary as a subprocess, write to a real (tmpdir) SQLite database, observe stdout/stderr/exit-code. One per user story; the only kind that touches the actual built artifact.
- **Property-based** — for the priority-queue invariants and the retry-backoff schedule. Runs `proptest` against the pure logic in `CAE-Scheduler` and `CAE-Retry`.

The four kinds above are the full inventory. CAE deliberately does NOT use: smoke tests (the e2e suite covers smoke), performance tests (sub-second granularity is a non-goal per PRD § Non-Goals — there's nothing to optimize against), or fuzz tests (the input surface is a shell-command string + a deadline; not fuzz-worthy in v1).

### Completeness Targets

- **Unit** — **Strong.** Every public function in `src/execution/`, `src/retry/`, `src/store/`, `src/clock/` has at least one unit test exercising its golden path. Edge cases are added as bugs surface; not pre-targeted.
- **Integration** — **Strong.** Every subsystem boundary in [[CAE Architecture]] has at least one integration test:
  - Scheduler ↔ TaskStore
  - Scheduler ↔ RetryManager
  - Scheduler ↔ Worker Pool
  - RetryManager ↔ TaskStore (dead-letter persistence)
- **End-to-end** — **Bounded.** Exactly one e2e per user story in [[CAE PRD]] § User Stories. Three e2e tests total at v1; grows as new user stories are added.
- **Property-based** — **Bounded.** Two properties, both load-bearing for correctness claims:
  - Scheduler picks the highest-priority Ready task at all times (age-promotion preserved).
  - Retry delay sequence is monotonically non-decreasing up to the configured cap.

### Responsibilities

- **Unit tests** — agent on `/mint`. Every feature mint that touches `src/` writes the unit tests as part of the mint.
- **Integration tests** — agent on `/mint` for any feature that crosses a subsystem boundary. The boundary inventory above is the trigger list.
- **End-to-end tests** — author-curated. The user signs off on each e2e because they are the user-story spec turned into executable form; agent assists by drafting.
- **Property-based tests** — author-curated initially; agent extends as new invariants are codified.
- **CI** — runs unit + integration + e2e + property-based on PR open and `main` push. No optional tiers; the full suite must pass.

### Tier Mapping

Per [[DSC verification]]:

- **Tier 1 (agent-immediate)** — satisfied by unit + integration + property-based tests, all of which run in CI in under a minute. The default tier for CAE features.
- **Tier 2 (agent-over-time)** — satisfied by the e2e suite running on every push and the property-based suite running with a high case count nightly. Drift in CI surfaces within a day.
- **Tier 3 (user-passive)** — satisfied by the author dogfooding `cae` against their own deferred-task workflow. CAE is small enough that real-use signal is fast.
- **Tier 4 (user-explicit)** — fallback only. No CAE feature currently lands at Tier 4.

## Proposed Tests

### Unit

| Test                                       | Exercises                                                    | Spec                          |
| ------------------------------------------ | ------------------------------------------------------------ | ----------------------------- |
| `test_scheduler_priority_ordering`         | Scheduler picks highest-priority Ready task                  | [[CAE-Scheduler]] § Tests     |
| `test_scheduler_deadline_respected`        | Task not dispatched before its deadline                      | [[CAE-Scheduler]] § Tests     |
| `test_scheduler_age_promotion`             | Low-priority task ages into higher band after N seconds      | [[CAE-Scheduler]] § Tests     |
| `test_retry_backoff_exponential`           | Retry delay doubles up to configured cap                     | [CAE-Retry § Tests]           |
| `test_retry_dead_letter_after_max_attempts` | Task moves to dead-letter after `max_attempts` failures      | [CAE-Retry § Tests]           |
| `test_store_save_and_load_roundtrip`       | Task written to store loads back identical                   | [CAE-Store § Tests]           |
| `test_store_mark_done_idempotent`          | Marking the same task done twice is a no-op                  | [CAE-Store § Tests]           |
| `test_clock_test_clock_advances_on_demand` | `TestClock::advance(d)` moves time by exactly `d`            | [CAE-Clock § Tests]           |
| `test_clock_wall_clock_monotonic`          | `WallClock::now()` calls produce non-decreasing instants     | [CAE-Clock § Tests]           |

### Integration

| Test                                       | Exercises                                                       | Spec                          |
| ------------------------------------------ | --------------------------------------------------------------- | ----------------------------- |
| `test_schedule_dispatch_complete_flow`     | Scheduler ↔ TaskStore ↔ Worker Pool boundary; one task to done  | [CAE Dev Docs/CAE-Boundary]   |
| `test_failed_task_retries_then_dead_letter` | Scheduler ↔ RetryManager ↔ TaskStore; failure → retry → dead    | [CAE-Retry § Integration]     |
| `test_concurrent_submitters_no_lost_tasks` | Multiple threads call `submit()` on shared TaskStore; all land  | [CAE-Store § Concurrency]     |
| `test_drain_blocks_until_queue_empty`      | `drain()` returns only after every pending task has terminated  | [[CAE-Scheduler]] § Tests     |

### End-to-end

| Test                                  | Exercises (User Story)                                | Spec                  |
| ------------------------------------- | ----------------------------------------------------- | --------------------- |
| `e2e_schedule_a_task`                 | US-CAE-1: `cae schedule "<cmd>" --at <time>` lands a task | [CAE E2E § US-CAE-1]      |
| `e2e_monitor_task_status`             | US-CAE-2: `cae status` groups Pending/Running/Done    | [CAE E2E § US-CAE-2]      |
| `e2e_failed_task_retries_then_visible` | US-CAE-3: failing task retries, shows in `cae history` | [CAE E2E § US-CAE-3]      |

### Property-based

| Property                              | Exercises                                                  | Spec                       |
| ------------------------------------- | ---------------------------------------------------------- | -------------------------- |
| `prop_scheduler_picks_highest_priority` | At every step, dispatched task is the highest-priority Ready | [[CAE-Scheduler]] § Tests |
| `prop_retry_delays_monotonic_to_cap`   | Generated delay sequence non-decreasing, bounded by cap     | [CAE-Retry § Tests]        |

Bare-bracket entries (`[CAE-Retry § Tests]`) mark proposed-but-unwritten low-level specs. Each becomes a `[[wiki-link]]` once the module doc gets a `## Tests` block.

## See also

- [[CAE PRD]] — user stories that drive the e2e inventory.
- [[CAE Architecture]] — subsystem boundaries that drive the integration inventory.
- [[CAE Decisions]] — D01 / D03 / D5 are the architectural choices that make CAE deterministically testable.
- [[CAE-Scheduler]] — the only subsystem doc currently authored; carries its own `## Tests` block.
- [[DSC verification]] — four-tier verification discipline mapped above.
