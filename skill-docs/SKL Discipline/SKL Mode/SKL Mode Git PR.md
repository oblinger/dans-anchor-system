---
description: PR mode — every state-touching commit gated through pull-request review. For repositories where merge-mistakes are expensive.
---

# SKL Mode Git PR

**PR mode** is one of the two Git-aspect modes (the other is [[SKL Mode Git Commit|Commit]]). It shapes how the agent handles git boundaries when the cost-of-merge-mistake is high.

The headline: **every state-touching commit goes through a pull request with user review before further work continues**. PR mode is the explicit gate — the agent opens a PR for each unit of work, surfaces it, and pauses for review before starting the next unit.

For SKA (a curation project) and most personal anchors, PR mode is overkill. Switch to PR mode when working in:
- Production code with users.
- Shared libraries with many consumers.
- Deployed infrastructure where a bad merge is hard to recall.

An anchor declares PR mode by listing `PR` (not `Commit`) in its `traits:`.

## The four load-bearing rules

- **PR per unit of work — never commit directly to protected branches.** Each `/mint`-ed feature, each landed `/feature`, each bug-fix gets its own branch + PR. The agent does NOT push to `main` / `master` / `develop` / any protected branch.

- **Hard gate at the PR — pause for user review before next unit.** After opening a PR, the agent stops and surfaces it. The next unit of work does not start until the PR is reviewed (merged or rejected). PR mode is the explicit "every state-touching commit through human review" posture.

- **Always new commit on top within a PR — never amend.** Same rule as Commit mode: corrections are *additional* commits within the PR branch, not amends. You may squash on merge if you want a single commit per PR — that's the merge-time decision, not the agent's.

- **Auto-push within feature branches is OK; never to protected branches.** PR mode reverses the Commit-mode "never auto-push" rule for *feature branches* (push is required to open the PR), but maintains it absolutely for protected branches.

## When PR mode applies

The anchor's `traits:` list controls this:

```yaml
traits: [Code, Drive, PR]   # PR-mode anchor
traits: [Code, Drive, Commit]   # Commit-mode anchor (default for new anchors)
```

(Per F077's resolved design — Trait-list activation. v1 mints when F077 Q12 = agreed.)

## Status

**PR mode spec is in flight** per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in]]. All 11 design Qs are resolved; Q12 (agreement gate) is the final question — the next step is user acceptance and v1 mint. Until v1 mints, no anchor is in PR mode by default; this doc describes the agreed v2 design.

## Composition with /pr-flow

PR mode reuses the [[SKA pr-flow|/pr-flow]] methodology — same branching, same PR-creation, same surfacing, same wait-for-review semantics. The mode just declares that this is the default for every state-touching commit in this anchor (not opt-in per skill invocation).

## POST-COMPACT (Agent-Facing)

When PR mode v1 mints (F077 Q12 = A), this section will land in `role-pilot.md` POST-COMPACT RELOAD for any session driving a PR-mode anchor. Draft form:

```
- **Git Mode — PR.** Active for this anchor (per its `traits:` list). Every state-touching change goes through a PR. Concretely:
  - **PR per unit of work.** Each feature / mint / bug-fix → its own branch + PR. Never commit to protected branches.
  - **Hard gate at PR — pause for user review.** Surface the PR; do not start the next unit until merged.
  - **Always new commit on top within the PR — never amend.** User may squash on merge if desired.
  - **Auto-push to feature branches OK; never to protected.**
  - Full user-facing spec: `[[SKL Mode Git PR]]`. Mode framework: `[[SKL Mode]]`.
```

## Cross-references

- [[SKL Mode]] — the mode framework.
- [[SKL Mode Drive]] — composes with PR (both Drive + PR = PR mode in a Drive-style anchor).
- [[SKL Mode Git Commit]] — the alternative Git-aspect mode (default for SKA).
- [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in]] — full design + Trait-list activation.
- [[SKA pr-flow|/pr-flow]] — the PR-creation + review-wait methodology PR mode reuses.
