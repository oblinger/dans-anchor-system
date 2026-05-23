# Finalize Discipline

The **finalize discipline** is the closing ceremony for a unit of work — the sequence of small steps that catch the things commonly forgotten when something "is done." Verify tests pass, commit, push, merge, update Status, regenerate any drifted docs, clean up branches, post the result.

This is a discipline (`user_invocable: false`) — you don't invoke it directly. Other skills run it when they reach a "this is done — wrap it up" moment. Consumers today: `/land`, `/crank`, and any future `/ship` / `/code release` style skill.

## Why this exists — the problem it solves

Without a shared closing ceremony, every skill that wraps work up reinvents the sequence — and inevitably each one forgets a different step. One commits without pushing. Another pushes without updating Status. A third skips docs regeneration so the system docs drift from the implementation.

Centralizing the ceremony as a discipline means every consumer follows the same sequence, and changes to the ceremony (e.g., adding a "regenerate TOC" step) propagate to every consumer automatically.

## When it runs

A consumer skill invokes the discipline when:

- A feature has been minted and reaches end-of-lifecycle (`/land` finishing a feature; `/crank` finishing one before continuing).
- A milestone or release point is reached.
- A deliverable has been verified and the agent is about to either stop or pick up new work.

Not for: mid-implementation commits (use ordinary commit discipline); closing a backlog item that was never a "feature" (no Status field to update).

## What it does — the sequence

| Step | What happens |
|---|---|
| **1. Verify** | Run the relevant test suite. All tests must pass before any other step. Check `git status` for unstaged or untracked work that belongs to this commit. |
| **2. Commit** | Stage by specific path (never `git add -A`); brief message; no boilerplate. Push to remote if the branch tracks one. Merge any open PRs (after CI green). |
| **3. Update Feature Doc** | If the work has a feature doc: set Status to **Done — finalized YYYY-MM-DD**. Resolve any stragglers in `## Open Questions`. |
| **4. Update Status / Stat** | Post a Done update via `skl-stat`. Move any backlog item to `## Done` with PR/commit cross-reference. Mark any roadmap milestone complete. |
| **5. Update Docs to Match Reality** | Public-API changes → update module doc. New files → update `{NAME} Files.md` and Dev dispatch. Architecture change → update System Design. |
| **6. Clean Up** | Delete merged branches. Close satisfied issues. Verify `git status` is clean. Verify any dev server still works. |
| **7. Report** | The consumer skill formats the report; the discipline supplies the substance — work-unit name + identifier, files changed, tests passing, docs updated. |

Steps that don't apply (no feature doc, no module docs, no roadmap milestone) are skipped, but the order of the rest is preserved.

## When you'll notice this

- After `/land` completes, you see a per-item summary line: `B12 — Foo: tests green, committed (abc123), Status → Done, docs updated`. That summary comes from this discipline.
- After `/crank` finishes a feature mid-stream, you see the same shape of summary before it picks up the next item.
- The branch you were working on disappears (cleanup), the PR shows merged, and Status on the feature doc is "Done."

## Workflow position

The finalize discipline transitions a unit of work from `[Verify]` → `[Done]` (per the [[SKL Workflow|workflow discipline]]). It is the gate between "implementation looks done" and "this is actually closed and recorded."

## What it does NOT do

- **It doesn't pick the next thing.** That's the consumer skill's job (`/land` stops, `/crank` continues).
- **It doesn't fabricate Done status.** If pending Open Questions remain, the work isn't actually done — the discipline halts and surfaces to you rather than mark it Done anyway.
- **It doesn't auto-resume.** Closing is a discrete moment; the consumer decides whether to keep going.
