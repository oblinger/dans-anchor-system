---
cssclasses:
  - monospace
description: repository file tree
---

:>> [[CAE]] → [[CAE Docs]] → [[CAE Dev]]

# CAE Files

File tree for the example-project repository with descriptions.


example-project/                          [[CAE Rollup]]
├── Cargo.toml                            Workspace config + dependencies
├── Cargo.lock                            Dependency lockfile
├── justfile                              Build, test, check recipes        → [[CAB Repository Structure]]
├── [[CAB Claude\|CLAUDE.md]]                             Claude Code configuration
│
├── src/                                  Library crate
│   ├── [[CAE Rollup\|lib.rs]]                            Crate root, module exports (rollup)
│   ├── cli.rs                            CLI argument parsing (clap)
│   ├── execution/
│   │   ├── mod.rs                        Subsystem entry point
│   │   ├── [[CAE Scheduler\|scheduler.rs]]                  Priority queue engine
│   │   └── worker.rs                     Thread pool lifecycle
│   ├── retry.rs                          Exponential backoff logic
│   ├── store.rs                          SQLite TaskStore
│   ├── clock.rs                          Injectable Clock trait
│   └── models.rs                         Task, TaskResult structs
│
└── tests/                                Integration tests
    ├── scheduler.rs                      Scheduler integration tests
    └── cli.rs                            CLI end-to-end tests
