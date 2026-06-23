---
description: "`/snapshot` — capture a labeled, restorable snapshot bundle of the repo"
traits: [Skill]
---

# FEX Snapshot - /snapshot
Captures the repository's current state into a labeled, restorable **snapshot bundle** under `snapshots/<label>/`, writing the [[FEX Manifest|Manifest]] record so a later restore knows exactly what it captured. The worked **skill** example — the skill-doc page that fronts its `SKILL.md` runbook.

| -[[FEX Snapshot]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FEX Repo]] → [FEX Snapshot](hook://p/FEX%20Snapshot)<br>: example skill — the `/snapshot` capture skill |
| --- | --- |
| Anchor | [[FEX Repo]] (parent) |
| Related | [[FEX Snapshot/SKILL\|SKILL]] (the runbook),  [[FEX Manifest]] (what it writes),  [[FEX Retention]] (what sweeps its bundles),  [[FCT Skill]] (the skill spec), |

## What it does

`/snapshot [label]` records a restore point: it resolves the current commit and branch, copies tracked state into `snapshots/<label>/`, and writes a `manifest.txt` ([[FEX Manifest]]) carrying `label`, `commit`, `branch`, `created`, and counts. With no label it stamps one from the timestamp (`YYYY-MM-DD-HHMM`).

## When to use

Before a risky operation, or on a schedule, when you want a labeled point you can name in a later `restore`. Old bundles are reaped by the [[FEX Retention]] discipline — `/snapshot` never deletes.
