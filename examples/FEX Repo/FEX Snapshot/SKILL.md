---
name: snapshot
description: "Capture the repository's current state into a dated, restorable bundle. Use when the user says /snapshot, snapshot the repo, take a snapshot, checkpoint this, save the current state."
user_invocable: true
---

# Snapshot — checkpoint the repo into a dated bundle
Capture the working tree into a restorable, dated bundle so any later state can be rolled back to this point.

## When to Use

Invoke when the user says "/snapshot", "snapshot the repo", "checkpoint this", or asks to save the current state before a risky change. Not for routine commits — this is a heavier, restorable checkpoint that captures untracked and ignored working state a commit would miss.

## Runbook

1. Resolve the repo root and confirm it is the intended target.
2. Build a dated label `YYYY-MM-DD-HHMM` and create `snapshots/<label>/`.
3. Archive the working tree (tracked + untracked, honoring an opt-in for ignored paths) into the bundle.
4. Record the current commit SHA and branch alongside the bundle as `manifest.txt`.
5. Report the bundle path and the one-line restore command back to the user.
