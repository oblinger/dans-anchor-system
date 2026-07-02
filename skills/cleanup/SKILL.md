---
name: cleanup
description: >
  Sweep every git worktree on the machine, classify each by what it would cost
  to delete, remove the safe ones, and CERTIFY whether the current worktree is
  safe to abandon — so you can run `/cleanup`, then exit and confirm the
  "delete worktree?" prompt with zero risk of stranding unchecked-in work.
  Removes empty/clean unattached worktrees and prunes dead registrations; never
  deletes uncommitted content; never kills a live agent. Triggered by
  `/cleanup`. Slash-only — "cleanup" is too common a word to be a trigger.
user_invocable: true
---

# cleanup — sweep, classify, and certify git worktrees

The job: make it safe to walk away from an agent's worktree and **never look back**. You run `/cleanup`, it cleans every stray worktree, tells you the current one is safe (or makes it safe), and you exit confident nothing uncommitted was lost.

## The one principle everything rests on

**Committed work survives worktree deletion. Only *uncommitted* working-tree changes are lost.** Commits live in the shared `.git` object store; deleting a worktree directory removes a checkout, not history (the branch ref persists). So "is this worktree safe to delete?" reduces entirely to **"is `git status` clean?"** That is the certification this skill performs.

## When to use

- Before exiting an agent that runs in a worktree (`claude --worktree <name>`), to guarantee no unchecked-in work is stranded.
- Periodically, to clear the accumulation of stray/abandoned worktrees across all repos.
- Any time the user says `/cleanup`, "clean up the worktrees", "sweep the trees".

## Procedure

### 1. Discover every worktree on the machine

```bash
repos=$(find ~/ob ~/.claude -maxdepth 8 -name .git \( -type d -o -type f \) 2>/dev/null | sed 's:/\.git$::' | sort -u)
printf '%s\n' "$repos" | while IFS= read -r r; do
  [ -z "$r" ] && continue
  git -C "$r" worktree list --porcelain 2>/dev/null | awk -v root="$r" '
    /^worktree /{wt=substr($0,10)} /^branch /{br=substr($0,8)}
    /^$/{ if(wt!="" && wt!=root) print wt" :: "br; wt="";br="" }
    END{ if(wt!="" && wt!=root) print wt" :: "br }'
done | sort -u
```

(Scope is the work areas — `~/ob` and `~/.claude` — never a bare `~` scan, per the home-scan rule. Ignore `.git/modules/*` paths: those are submodule gitdirs, not worktrees.)

### 2. Identify live agents — these are sacrosanct

```bash
ps aux | grep "[c]laude --worktree" | awk '{for(i=1;i<=NF;i++) if($i=="--worktree") print $(i+1)}'
```

Any worktree with a live `claude --worktree` process attached is **never touched**. If its directory is already gone (a stranded process holding a deleted cwd), **report it** — do not kill the process (investigate-then-surface; never blind-pkill).

### 3. Classify each worktree

Only **linked** worktrees are ever removal candidates — never a repo's **primary** working tree (the one whose path equals the repo root; `git worktree list` prints it first). A primary checkout like `~/ob/kmr` or a project's main clone is left alone even if it carries uncommitted daily work — that work is the user's, not a stray.

For each **linked** worktree that is **not** the current one and **not** live-agent-attached:

```bash
[ -d "$wt" ] || echo "STALE-REG"                                   # dir gone → prune registration only
unc=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l)          # uncommitted = LOST on delete
```

- **Missing directory** → stale registration; prune it (metadata only, zero content).
- **`unc == 0` (clean)** → safe to remove: `git worktree remove`. Keep the branch (its commits survive); delete the branch too only if it has 0 commits beyond the trunk.
- **`unc > 0` (uncommitted)** → **SURFACE, do not delete.** Show the files. Offer to commit them to a `wip/<branch>` commit so they are parked-not-lost. Only remove after the user decides.
- **Not an agent stray** (a deliberate project checkout, e.g. a paired dev worktree) → leave it; mention it.

### 4. Execute the safe cleanup

```bash
# prune dead registrations across all repos (git's default expiry is ~3 months — force it)
printf '%s\n' "$repos" | while IFS= read -r r; do git -C "$r" worktree prune --expire=now 2>/dev/null; done
# remove each clean, unattached worktree dir; delete its branch if fully merged
git -C "$owner_repo" worktree remove "$wt"
git -C "$owner_repo" branch -D "$branch"   # only if rev-list --count trunk..branch == 0
```

### 5. Certify the CURRENT worktree

A worktree **cannot delete itself** while you are standing in it (git refuses; the shell cwd is inside it, the process holds it). So instead of deleting, **certify**:

```bash
cd "$CURRENT_WORKTREE"
out=$(git status --porcelain)
ahead=$(git rev-list --count <trunk>..HEAD 2>/dev/null)
```

- If `out` is empty → print: **"✅ This worktree is CLEAN — exit and confirm the delete prompt; nothing will be lost."** (If `ahead > 0`, note those commits survive deletion on their branch but suggest merging if wanted.)
- If `out` is non-empty → either commit it (if it's real work), or note it's discardable junk (`__pycache__/`, lockfiles), then re-certify. Never tell the user it's safe while uncommitted real work remains.

(Optional true self-removal: spawn a detached watcher that waits for the agent's PID to exit, then `git worktree remove --force` + prune. More moving parts; the certify-then-exit path is simpler and equally safe.)

### 6. Report

End with a crisp ledger:
- **Removed:** the worktrees deleted + registrations pruned.
- **Left alive (with reason):** live agents, the current worktree, deliberate project checkouts.
- **Current worktree verdict:** the certification line from step 5.

## Hard safety rules

- Never delete a worktree with uncommitted changes without surfacing first — committed work survives, uncommitted does not.
- Never kill a live agent process; surface stranded ones instead.
- Never `git clean` inside a worktree as part of cleanup.
- Scope discovery to `~/ob` and `~/.claude`; never a bare-home recursive scan.

## Related

- Operating standard this complements: [[SKA cleanup]] (the SKA anchor) and the commit-before-done discipline — agents that commit their work before finishing make every worktree disposable.
