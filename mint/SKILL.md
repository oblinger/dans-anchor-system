---
name: mint
description: >
  Execute the agentic action — take what's ready and make it real.
  For code: read the feature/spec, write code, test, verify, commit.
  Use when the user says: "mint it", "mint the feature", "go ahead and build it",
  "implement this", "make it happen", "do it".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Mint

Take what's ready and make it real. Orchestrate the implementation phase — spec, code, test, review, verify, commit.

## Runbook

### 0. Wire to bucket PRD(s) — pre-condition (per [[F083 — Cross-Linking]])

Before reading the spec for implementation, wire the F-doc into the planning hierarchy. **Only applies to anchors using the federated bucket-PRD structure** — for anchors that don't, this step is a no-op.

1. **Check whether this anchor uses federated bucket PRDs.** Does `{anchor}/Docs/Plan/` contain bucket subfolders with `{Bucket} PRD.md` files (e.g., `SKA Plan/Hygiene/Hygiene PRD.md`)? If NO → **skip this step entirely** (anchor not yet on the federated structure). Proceed to step 1.
2. **Read the F-doc's `bucket:` frontmatter.** Multi-value supported (`bucket: [hygiene, code]`). If absent → default to `bucket: unlinked` (wire to `Unlinked PRD.md`).
3. **For each named bucket, locate the bucket PRD** at `{anchor}/Docs/Plan/{Bucket}/{Bucket} PRD.md`. If the named PRD is missing (but other bucket PRDs exist), **fail with a clear message** — `bucket: <name>` in F-doc but `<Name> PRD.md` doesn't exist; either fix the F-doc frontmatter or create the bucket PRD. Don't silently skip.
4. **Find the `## Feature Docs` H2 section** in that PRD and the 3-column table within it (`| F-doc | Status | Summary |`).
5. **Append a row** with:
   - F-doc link: `[[F{N} — {Title}]]`
   - Current status bracket from the F-doc's backlog row in `{NAME} Backlog.md` (e.g., `[Agreed]`)
   - One-line summary from the F-doc's frontmatter `description:` field
6. **Idempotence:** if a row for this F-doc already exists in the table, *update* its Status column if the bracket has changed; don't duplicate the row.
7. **Verify:** `/audit features` (see [[audit-features]]) confirms the wiring landed across all named buckets.

Only after all named bucket PRDs are wired (or step 0 was skipped because no federated structure exists), proceed to step 1.

### 1. Assess

- Read the feature doc or spec that defines what to build
- Confirm the feature is in "Agreed" or "Ready" state — all questions answered, no decisions pending
- If not agreed, stop and tell the user: "This feature hasn't been agreed yet. Run `/feature` to complete the design."

### 2. Pipeline (per milestone)

| Step | Action | What it does |
|------|--------|-------------|
| 1 | Spec | Write implementation spec for the milestone (if not already written) |
| 2 | Code | Implement according to the spec |
| 3 | Test | Write and run tests |
| 4 | Review | Check code quality and spec compliance |
| 5 | Verify | Run full test suite, produce completion proof |
| 6 | Commit | Commit and push |

### 3. Modes

**Solo** — The pilot executes the full pipeline sequentially for each milestone. Simplest flow — one agent, one branch.

**Workers** — The pilot specs milestones and dispatches them to worker agents. The pilot's job becomes: spec upcoming milestones, review completed PRs, unblock workers, merge approved work.

**Parallel** — Multiple workers run simultaneously on independent milestones. The pilot manages the dispatch queue and resolves conflicts.

Default to solo mode unless the user specifies workers or parallel.

### 4. Execution Loop

Always work on the highest-priority item that has actionable work, then re-evaluate:

1. **Unblock Workers** — review PRs, merge, dispatch new workers on fully-specced items
2. **Legwork** — autonomous tasks: integrate user feedback, update roadmap, doc fixes
3. **Spec Work** — write specs for upcoming roadmap items whose dependencies are met
4. **Rescan** — check design consistency: docs vs code, intended vs actual

### 5. Git Protocol

Commit after each well-defined piece of activity. Before pausing:
1. Commit any uncommitted work
2. Push all local commits
3. Merge ready PRs
4. Verify `git status` is clean

### 6. Stat Updates

```bash
skl-stat update <S#> "Implementing" "Starting implementation"
skl-stat update <S#> "Testing" "Implementation complete, running tests"
skl-stat update <S#> "Done" "Feature complete and tested"
```

### 7. Q.md update post-condition (per F075)

After the mint completes and the backlog row's text/bracket has been updated to reflect the new state (e.g., `[Ready]` → `[Active]` → `[Done]`), regenerate the anchor's per-anchor section in `~/ob/kmr/Q.md` per `[[triage]]` § 6 — walk the backlog, compute the section, remove any existing section for this anchor, insert at the top of Q.md's body (bubble-to-top). **The backlog file is NOT reordered** — source order is preserved (per F075 Q2). Bubble-to-top is a Q.md-only behavior.
**Then invoke `/audit q` to verify (per F076 Q6 auto-wiring).** The audit's fix-by-default behavior catches any drift introduced by this skill's edits — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (rare) files a `QFix [Ready]` backlog entry the user can address later. Surfacing any QFix entry is part of this skill's "done" criteria.

### 8. On Completion

On `/mint`: assess the roadmap, find the next milestone, and enter the pipeline.
