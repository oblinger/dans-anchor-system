---
name: land
description: >
  Bounded crank. Finish *every* activity that is currently in flight (usually
  one, sometimes several when the session got distracted), commit, clean up,
  report done, and stop. Land everything that's open; start nothing new — items
  on the backlog that have not been started are out of scope. Triggered by
  `/land` or by `.` (a single period as the entire message). Unlike crank, land
  has a built-in stopping rule — the runway. Unlike fortify, land does not pivot
  posture; it just brings the open threads down cleanly.
user_invocable: true
---

# Land — Bounded Crank

Three execution-pattern peers:

| Trigger | Mode | Stops when |
|---|---|---|
| `crank` / `'` | Keep going indefinitely; finish current thread, then pick up new work from backlog/roadmap | Genuinely nothing actionable |
| `fortify` / `"` | Skeptical crank — distrust the foundation, fortify it, then continue | Foundation firm, hypothesis re-derived; resumes crank |
| **`land`** / **`.`** | **Bounded crank — finish *every* activity that is currently in flight, then stop. Do not pick up new work from the backlog.** | **All in-flight activities are committed, clean, and reported done** |

## Trigger

- Slash: **`/land`**
- Punctuation: **`.`** (a single period as the entire message)

The word "land" by itself does **not** trigger this skill. It is a common English word and the user uses it in normal sentences. The trigger is the period, the slash, or the explicit invocation. There is no DMUX prefix wiring.

## Posture

Land borrows crank's autonomy rules wholesale — the agent works without unnecessary interruption, makes its own low-risk decisions, and only escalates costly-to-reverse choices. The single difference is **scope**: land closes only *in-flight* work and never opens *new* work. When everything that was already started is committed, clean, and reported, the agent **stops** instead of pulling the next item off the backlog.

This is the "wrap up everything that's open and put it all down" command. It is not the "I'm done with this codebase" command; it is the "close every thread that is already pulled" command.

## The in-flight / not-started cut

Land's bright line:

- **In flight = land it.** Anything that has been started, regardless of how far along — a partially edited file, a half-written commit, an unfinished refactor, a bug being hunted, a feature being built, a doc partially regenerated. All of it gets driven to completion in this invocation. Usually there will be only one such item, but there can be several when the session got distracted; land closes all of them.
- **Not started = leave it alone.** Items that are listed on the backlog, mentioned in a roadmap, or sketched in a feature doc but where no work has actually begun do **not** get touched. Land does not promote backlog items into activity.

If the cut is ambiguous on a specific item — e.g. "we wrote a feature doc but haven't coded against it" — apply this rule: if there is **uncommitted output, edits, or runtime state** tied to it, treat it as in-flight and land it. If nothing exists yet beyond the backlog entry, leave it alone.

## Identifying the in-flight activities

Before doing anything else, enumerate everything currently open:

1. **What was the agent just working on?** Read the most recent assistant turns and tool calls. Identify each concrete deliverable in flight — feature, bug fix, doc edit, migration step, refactor.
2. **What's uncommitted in the repo?** Check `git status` for unstaged or untracked work that belongs to in-flight activities. Each cluster of related changes is a candidate landing target.
3. **What's "done" for each?** Tests pass, docs match code, commit pushed, status updated, no dangling state.
4. **State the list back to the user in one line each** so the user can correct scope before commit. Example: "Landing: (1) OBU Files alignment fix — driving test green; (2) Land skill plurality update — staging and committing. Then halting."

If activities are entangled (the same files have edits belonging to two different threads), state the entanglement and ask the user once how to split them. Do not guess at the split.

If everything is already clean and there is nothing in flight, report that in one line and stop — there is no work for land to do.

## Runbook

Once the in-flight list is named, work autonomously to bring each item down. Process them sequentially — finish, commit, and verify one before moving to the next, so a partial interruption leaves clean items behind cleanly.

For **each** in-flight activity:

1. **Finish the work.**
   - Drive any in-progress code change to a working state.
   - Run the relevant tests; resolve failures that are clearly part of this activity.
   - Update the touched docs (module docs, Files.md, dispatch tables, system design) to match the implemented reality, per the activity's scope.
   - Make low-risk decisions yourself; only escalate costly-to-reverse ones (architecture, user-facing design, production code refactoring).

2. **Commit.**
   - Stage the relevant files (specific paths, not `git add -A`).
   - Write a brief commit message — what changed and why, no boilerplate.
   - Push if the branch tracks a remote.

3. **Verify clean.**
   - `git status` is clean for this activity's files (no dangling unstaged or untracked entries).
   - Tests still green.
   - Stat / status records updated if applicable (feature lifecycle status, backlog item closed, etc.).

After **all** in-flight activities are landed:

4. **Report done in one block.**
   - One line per activity in the format `<Activity name> — completed and committed.`
   - End with `Nothing more to do.` on its own line.

5. **Always run `/roster` after the report — even when nothing was landed.**
   - This gives the user the post-`/land` state of the backlog as the closing view.
   - When the user invoked `/land` and there was actually nothing in flight, the roster is *especially* useful — it confirms the user's mental model is in sync with reality and shows what could come next without typing anything more.
   - Do **not** check the backlog to *pick a next task*. Do **not** start another thread. Roster is the read-only view; the agent stops after it prints.

6. **Wait for user input.** No auto-resume.

## Principles

- **Land is bounded by definition.** The whole point is that it stops. If "stop" feels wrong, the agent picked the wrong word — `crank` was the right command. Reach back to the user before continuing.
- **Land everything that's open; start nothing new.** All in-flight items get closed in one invocation. Backlog items, roadmap items, and feature docs without started work are out of scope — land does not promote them.
- **Don't expand scope while landing.** If new work appears mid-land (a related bug, a tempting cleanup), note it for the backlog and stay on the named in-flight items. Land does not absorb adjacent work.
- **Minimize interruptions, like crank.** Make the call yourself on low-risk decisions; only ask the user when the choice is genuinely costly to reverse.
- **Commit discipline is the same as everywhere else.** Specific file paths, brief message, no "generated by claude" boilerplate.

## Relationship to neighboring skills

- **`/crank` (`'`)** — Land is crank with a stopping rule baked in. Use crank when you want continuous progress; use land when you want the current thread closed and then silence.
- **`/fortify` (`"`)** — Fortify is the *posture* command (skeptical, foundation-rebuilding). Land is the *scope* command (bounded). Fortify can land into a stop; land does not enter fortify mode.
- **[[finalize]] discipline** — Finalize is not a user-invocable skill; it's a *discipline* that consumer skills delegate to. When an in-flight activity is a feature/milestone wrap-up, land runs the finalize discipline (`skills/finalize/SKILL.md`) as a sub-routine: verify tests, commit by path, push, merge PRs, update feature-doc Status, post stat, regenerate any drifted module docs, clean branches. Land owns the *halt*; finalize owns the *ceremony*.
- **`/mint`** — Mint executes a spec autonomously to completion. Mint produces a working deliverable; land is what you say after the deliverable exists, when you want the agent to clean up and stop.

## Anti-patterns

- **Reading the backlog.** Land is the one execution-pattern command that explicitly does *not* look for the next thing. If the agent reaches for the backlog after landing the in-flight items, it has misunderstood the command.
- **Promoting backlog items.** Land never starts work that wasn't already started. A roadmap entry, a feature doc with no code yet, an idea in a discussion log — all out of scope.
- **Landing only one when several are open.** If two or three threads are in flight, all of them get landed in this invocation. The user does not have to invoke `.` once per thread.
- **Half-landing.** "I've committed but the docs aren't updated." That's not landed. An activity is done when it is *clean*, not just when it is committed.
- **Renaming or rescoping silently.** Land applies to what was in flight when the user said `.`. If scope shifts silently, the user's stop signal has been lost. State the in-flight list back and proceed; if a real rescope is needed, ask once and then stop or proceed.
- **Auto-resuming.** After the final "Nothing more to do." line, the agent waits. It does not resume cranking unless the user explicitly invokes crank again.
