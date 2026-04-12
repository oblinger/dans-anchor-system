# /Finalize

`/finalize` — performs all cleanup and bookkeeping for an activity. Once complete, no further actions needed.

- **Verify tests pass** — all tests green, no skipped or ignored tests from this feature
- **Verify code committed** — no uncommitted changes related to this feature
- **Update stat** — set status to Done, update activity description with outcome
- **Propagate design changes** — if the feature changed architecture or interfaces, update System Design, Module Docs, and Files.md to match the implemented reality
- **Clean feature doc** — move implementation details out of the feature doc into the proper system docs; the feature doc becomes a historical record, not the source of truth
- **Update Dev dispatch** — new modules linked, stale links removed
- **Run audit-docs** — verify docs match source (`audit-docs.py`); fix any name mismatches
- **Archive stat entry** — if the feature is fully done and reviewed
