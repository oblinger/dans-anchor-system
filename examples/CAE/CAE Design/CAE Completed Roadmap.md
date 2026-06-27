# CAE Completed Roadmap
description:: companion to CAE Roadmap; preserved migrated milestones with their structure; newest-on-top.


## Completed standalone features (since 2026-06-01)

- [x] [[F042 — Add retry budget cap]] — (Done 2026-06-08) — global ceiling on max-retries per task
- [x] [[F045 — Verbose status output]] — (Done 2026-06-05) — `--verbose` flag on `cae status`
- [x] [[F046 — Cancel-by-prefix matching]] — (Done 2026-06-04) — `cae cancel T-04*` matches by prefix

## [x] M-Core — Core Scheduler Engine (migrated 2026-06-01)

**Status:** Complete — priority queue + worker pool + retry + drain all shipped. 4 of 4 sub-items.

**Reference:** [[CAE Architecture]] § Scheduler + § Worker Pool

**Tests:** 18 unit tests added (priority ordering, deadline respect, age-promotion); 1 integration test (`test_schedule_dispatch_complete_flow`)

- [x] [[F003 — M-Core.1: Priority queue implementation]]
- [x] [[F006 — M-Core.2: Worker thread pool]]
- [x] [[F009 — M-Core.3: Retry logic with exponential backoff]]
- [x] [[F011 — M-Core.4: Cancellation and drain]]

## Completed standalone features (between M-Core and M-Boot)

- [x] [[F020 — Status output color]] — (Done 2026-05-22) — TTY detection + ANSI coloring for `cae status`

## [x] M-Boot — Initial Boot Sequence (migrated 2026-05-15)

**Status:** Complete — anchor scaffolded, repo initialized, CI green on day one. 5 of 5 sub-items.

**Reference:** Bootstrap milestone — no architecture doc dependency

**Tests:** smoke test that the binary builds + runs `--help` without errors

- [x] [[F001 — M-Boot.1: Initialize CAE Cargo workspace]]
- [x] [[F002 — M-Boot.2: Scaffold src/ folder structure per Architecture]]
- [x] [[F004 — M-Boot.3: Wire CI pipeline (cargo test on PR)]]
- [x] [[F005 — M-Boot.4: Establish injectable Clock trait + WallClock impl]]
- [x] [[F007 — M-Boot.5: Establish TaskStore trait + InMemoryStore stub]]
