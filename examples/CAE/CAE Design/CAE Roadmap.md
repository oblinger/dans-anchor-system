## Open Questions

### Q1 {{add example here; if no questions this section is removed}}


# CAE Roadmap
description:: sequencing-design — milestones + ordering (moved from Track 2026-06-10)


## [ ] M-Store — Persistence Layer

**Status:** In progress — M-Store.1 + M-Store.2 merged; M-Store.3 active; M-Store.4 deferred to M-Polish window.

**Reference:** [[CAE Architecture]] § TaskStore + § RetryManager subsystems

**Tests:** unit tests for SQLite layer + WAL append; integration test for recovery loader (pending M-Store.3)

### [x] M-Store.1 — SQLite schema + migrations  [F050]

Foundation for durable task storage. Schema accommodates priority queue + state machine + dead-letter list.

- [x] Define `tasks` table with priority, state, scheduled_at, payload columns
- [x] Migration 0001 — initial schema with index on (state, scheduled_at)
- [x] Migration 0002 — dead-letter column for terminal failures
- [x] Migration runner integrated with `cae` startup (idempotent)

### [x] M-Store.2 — WAL append path  [F052]

Every enqueue/dequeue/state-change is durable before being acknowledged.

- [x] WAL file rotation on size threshold (default 16 MB)
- [x] `fsync` after each write; configurable via `--store-durability` flag
- [x] Crash-test recovery (simulated SIGKILL mid-write)
- [x] Replay path validated against committed-state expectations

### [ ] M-Store.3 — Recovery loader  [F055]

Replays the WAL on top of the last SQLite snapshot at startup. Depends on M-Store.1 + M-Store.2 (both merged).

- [x] Read last committed LSN from SQLite header
- [ ] Replay WAL entries newer than committed LSN
- [ ] Reject WAL entries with bad checksums (and surface as named errors)
- [ ] Integration test: kill mid-enqueue, restart, observe replay completes

### [~] M-Store.4 — Snapshot rotation  (Deferred — see M-Polish.2)

WAL truncation + periodic SQLite checkpoint. Pulled to M-Polish window because benchmarks aren't blocked on it.

### .

## [ ] M-CLI — Command-Line Interface

**Status:** Not started — committed for next milestone after M-Store ships.

**Reference:** [[CAE UX Design]] (command surface, output shapes, error voice); [[CAE CLI]] (exhaustive reference)

**Tests:** e2e tests per user story in [[CAE Testing]] (US-CAE-1, US-CAE-2, US-CAE-3)

### [ ] M-CLI.1 — `schedule` command  [F057]

Implement US-CAE-1. Parses time specs, enqueues task, returns task ID.

- [ ] Parse absolute time format (`2026-03-01 02:00`)
- [ ] Parse relative offsets (`+30m`, `+2h`, `+1d12h`)
- [ ] Optional `--priority high|normal|low` flag
- [ ] Return task ID on success; non-zero exit on parse failure

### [ ] M-CLI.2 — `status` and `history` commands  [F058]

Implement US-CAE-2. Group output by lifecycle state.

- [ ] `cae status` groups PENDING / RUNNING / DONE / FAILED with counts header
- [ ] `cae history --limit N` returns reverse-chronological terminal tasks
- [ ] Both commands respect `--json` flag for machine-readable output

### [ ] M-CLI.3 — Output formatting (text + JSON)  [F059]

Cross-cutting: `--json` flag everywhere applicable.

- [ ] Shared formatter module reads `--json` once, dispatches all commands
- [ ] Human format respects terminal width; truncates command strings
- [ ] JSON format passes JSON-schema validation (`cae schema status > schema.json`)

### [ ] M-CLI.3.5 — Implement CLI Core Statements  [F060]

Sub-command dispatch + arg parsing skeleton. Lands before M-CLI.1-3 fill in command bodies.

### [ ] M-CLI.4 — Error voice + exit codes  [F061]

Named errors per UX5; `sysexits.h` conventions.

- [ ] All errors include task ID + named cause + actionable next step
- [ ] Exit codes: 0 success / 64 usage / 65 data / 70 internal / 75 transient
- [ ] Error → log entry mapping (errors always go to stderr; logs to file)

### .

## [ ] M-Test — Test Suite Infrastructure

**Status:** Not started — pending M-Store + M-CLI shape settling.

- [ ] M-Test.1 — Unit harness setup  [F063]
- [ ] M-Test.2 — Integration test scaffolding  [F064]
- [ ] M-Test.3 — e2e binary harness  [F065] — drives `cae` subprocess; observes stdout / stderr / exit-code
- [ ] M-Test.4 — Property-based test framework  [F066] — `proptest` for the two load-bearing invariants

### .

## [ ] M-Polish — Quality and Polish

**Status:** Not started — final milestone before v1 release.

- [ ] M-Polish.1 — Performance benchmarks  [F068]
- [ ] M-Polish.2 — Snapshot rotation  [F069] — pulled in from M-Store.4 deferral
- [ ] M-Polish.3 — Documentation pass  [F070]
- [ ] [F049 — WAL compaction strategy]  (bare-bracket — spinoff from F017's internal roadmap; will be authored when M-Store.3 recovery-loader bottleneck surfaces)

### .
