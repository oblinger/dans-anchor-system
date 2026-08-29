---
description: "fixture — a groomed backlog satisfying the F228 frontier invariants"
---
# FX5 Backlog

## Ready

- **F001 — Ship the widget exporter** [Ready] — exporter is specced in the design doc; all questions resolved.
  - **Next:** implement `export_widget()` per the design doc's § Export API, then run the exporter test suite.

## Now

- **F002 — Fix the flaky importer retry** [Questions] — the importer sometimes double-retries on timeout. → [[F002 — Fix the flaky importer retry]]

- **F003 — Panel reopen fix** [Verify] — fix shipped 2026-07-01; panel state now persists across restarts.
  - **Verify:** close the panel, restart the app, reopen the panel — did it restore to its pre-restart position? **yes/no** · *why-user: passive-use observation — whether the restored position feels right is only visible in ordinary use*

## Later

- **F004 — Someday: dark-mode theming** — parked until the design system lands.
