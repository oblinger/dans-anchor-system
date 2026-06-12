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

The user-invocable skill that executes a Ready feature end-to-end — wiring it into bucket PRDs, integrating its content into target docs, gating on planning state, then running the spec → code → test → review → verify → commit pipeline.

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

Only after all named bucket PRDs are wired (or step 0 was skipped because no federated structure exists), proceed to step 0.5.

### 0.5. Integrate feature content into target docs (per [[F083 — Cross-Linking]] amendment)

The link-row appended in step 0 is a **tracking marker** that promises the feature's content has been integrated into the body of the target documents. Step 0.5 fulfills that promise.

**Core semantic:** at the end of this step, the target docs (PRD + Design + Architecture, wherever each exists) **reflect the content** of the feature. Linking is **never a substitute** — feature documents are commissioning artifacts, not part of the design.

**Procedure (per feature):**

1. **Identify the target docs.** For each bucket named in `bucket:` frontmatter, locate the target docs that exist:
   - `{anchor}/Docs/Plan/{Bucket}/{Bucket} PRD.md` (always wired in step 0)
   - `{anchor}/Docs/Plan/{Bucket}/{Bucket} Design.md` (if exists)
   - `{anchor}/Docs/User/Architecture/Architecture.md` (if exists)

2. **For each target doc, single LLM call with full context.** Pass to the LLM:
   - The feature doc (full content)
   - The current target doc body
   - The integration prompt: *"Identify content in the feature that affects this document type (product / design / architecture concerns respectively). For each piece of feature content that belongs in this document, either append a new section or edit an existing section to incorporate the content. The target document must stand on its own — do not write 'see the feature doc for details.' If the feature has no content that affects this document, return 'no integration needed' and make no edits."*
   - **Strict rule:** never link back to the feature doc as a substitute for content. The Feature Docs row in the PRD is the only acceptable link; the body of the doc must contain the actual content.

3. **Apply the LLM's proposed edits** to the target doc. Each edit is announced inline: `**Integrating <feature> into <doc>: <action summary>.**`

4. **Idempotence:** if integration was previously done (content already present in target doc), the LLM should report "already integrated" and make no edits.

5. **If the feature truly has no content for a particular target doc**, the LLM returns "no integration needed" for that doc. That's a valid outcome — don't force-fit content.

**Per-rename behavior** inherits [[F068 — Assume-and-announce discipline (Drive mode)|F068]] amendment: visible + low recoverability cost → auto-decide. Subsystem-level renames and interface-touching renames (CLI names, public API surfaces) are interface-sticky → ASK.

**Failure mode to watch for:** the LLM produces an edit that just appends *"See [[F{N} — {Feature}]] for details"* without actual content. **This is forbidden.** If the agent detects this in the proposed edit, reject and re-prompt.

Only after step 0.5 lands across all target docs, proceed to step 0.7.

### 0.7. Planning gate (F130) — Code-trait anchors only

Before reading the feature spec, check the planning-status gate. **Applies only to Code-trait anchors** (read `.anchor` `traits:` list). For non-Code anchors (Skill, Content, etc.), skip this step.

Run:
```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} status show
```

Read the cells for `prd`, `architecture`, `testing`. If **any** of them is `none`, the gate is not satisfied. Surface a three-way prompt:

```
Planning gate not satisfied — these facets are at `none`:
  - <facet1>
  - <facet2>
Options:
  (A) abort — run /design first  [Recommended]
  (B) proceed once — re-warn on next /mint
  (C) silence permanently — promote blocked facets to MVP-user with note "provisional"
```

Wait for the user's choice (`A` / `B` / `C`).

- **(A)** Stop the mint. Suggest `/design` to address the blocked facets.
- **(B)** Proceed to step 1 with no state change. Next `/mint` invocation will warn again.
- **(C)** For each blocked facet, run:
  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} status set <facet> MVP-user --note "provisional — proceeding without full planning; revisit"
  ```
  Then proceed to step 1. Future mints won't warn for these facets until the user explicitly re-grades them.

**No per-feature bypass record.** The `Status.md` git-history already captures what state the facets were in when the feature was minted — per-feature bypass stamps would add no signal that history doesn't already carry. (Per F130 Q1 → D.)

**Tamper-resistance note:** until F131's hook framework ships, an agent could bypass the gate by directly editing `Status.md` to flip cells. The prompt above is honored at the `/mint` flow level; F131-M1 makes the fence tamper-resistant.

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

### 7. Bracket transitions + Q.md refresh — via `state task update`

State transitions on the backlog row are mandatory and go through the workflow skill's `state` — no direct backlog edits:

```bash
# At mint start (Ready → Active):
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Active --horizon Active

# At mint completion, if verification is needed (Active → Verify):
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Verify

# Or if no verification is needed (Active → Done):
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Done --horizon Done
```

`state task update` preserves the row's title and body (omit those flags) and auto-refreshes the anchor's per-anchor section in `~/ob/kmr/Q.md` (by shelling out to `audit-q.py --scope backlog --anchor {NAME} --fix`). **The backlog file is NOT reordered** — source order is preserved (per F075 Q2). Bubble-to-top is a Q.md-only behavior.

The audit's fix-by-default behavior catches any drift introduced — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (rare) files a `QFix [Ready]` backlog entry. **Surfacing any QFix entry is part of this skill's "done" criteria** — read the script's output for QFix lines and surface them to the user.

### 8. Crank wall-clock timer write (per [[F088]])

**On every successful mint completion**, update the crank wall-clock timer file so `/crank`'s fatigue-gate (per [[SKA crank]] § Wall-clock gate) can tell that real progress just happened:

```bash
mkdir -p ~/.cache && date +%s > ~/.cache/crank-last-mint.txt
```

This is a one-line write at the *end* of every successful mint — after commit, after Q.md regen, after audit-q post-condition. Skip the write on failed mints (the agent stopped without producing a commit / Done bracket); the timer file should reflect *successful mints only*, not turn count. Migrates to F080's `~/.config/ob-skills/crank/last-mint` namespace when F080 ships.

### 9. On Completion

On `/mint`: assess the roadmap, find the next milestone, and enter the pipeline.
