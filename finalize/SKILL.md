---
name: finalize
description: >
  Wrap up after minting — verify, commit, update docs and status, close out the feature.
  Use when the user says: "finalize", "wrap it up", "finish this", "close it out",
  "we're done", "ship it".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Finalize

Wrap up after minting. Verify everything works, commit all outstanding changes, update docs and status, close out the feature.

## Runbook

### 1. Verify

- Run the full test suite — all tests must pass
- Check for uncommitted changes — nothing should be left unstaged
- Check for untracked files that should be committed

### 2. Commit

- Stage and commit all remaining work
- Push to remote
- Merge any open PRs related to this feature

### 3. Update Feature Doc

- Set the feature doc's Status section to "Done"
- Remove or resolve any remaining Open Questions
- Add a brief "What shipped" summary if the implementation differs from the design

### 4. Update Stat

```bash
skl-stat update <S#> "Done" "Feature complete and verified"
```

### 5. Update Docs

- If implementation changed public APIs: update module docs
- If implementation added new files: update Files.md and Dev dispatch
- If implementation changed architecture: update Architecture doc

### 6. Clean Up

- Delete any temporary branches
- Close related issues if applicable
- Verify `git status` is clean
- Verify the dev server / build still works

### 7. Report

Tell the user what was finalized:
- Feature name and S-number
- Files changed
- Tests passing
- Any docs updated
