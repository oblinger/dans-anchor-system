---
description: PR Trait — every state-touching commit gated through a pull request with user review before further work continues. For high-blast-radius repositories. Composable capability trait.
---

# PR

The Git-aspect Trait spec declaring that every state-touching commit on the anchor is gated through a pull request on its own branch, paused for user review before further work continues.

## What it is

**PR declares that every state-touching commit on this anchor goes through a pull request — opened on its own branch, surfaced for user review, paused until merged.** It is the Git-aspect mode for any anchor where the cost-of-merge-mistake is high — production code with users, shared libraries with many consumers, deployed infrastructure.

The agent reuses the [[SKA pr-flow|/pr-flow]] methodology — same branching, same PR creation, same wait-for-review semantics. PR mode just declares that this is the default for *every* state-touching commit in this anchor, not opt-in per skill invocation.

PR is **orthogonal to identity traits**. `Code + Track + PR` is the canonical "production code project with a backlog and PR-gated git" combination.

## How it's detected

- **Trait:** `PR` appears in the anchor's `.anchor` `traits:` list (one-line lookup; no file inference per [[CAB Aspects]]).
- An anchor with `NoGit` declared takes no Git-aspect mode.
- Default when no Git-aspect trait is declared (and the anchor has `Code`): falls back to [[Commit]] mode — explicit `PR` declaration is **required** to enter PR mode; it is not the default.

## The four load-bearing rules

(Authoritative agent-facing form will land in `role-pilot.md` POST-COMPACT RELOAD when [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] v1 mints. Full user-facing spec at [[SKL Mode Git PR]]. The rules in summary:)

1. **PR per unit of work — never commit directly to protected branches.** Each `/mint`-ed feature, each landed `/feature`, each bug-fix gets its own branch + PR. The agent does NOT push to `main` / `master` / `develop` / any protected branch.
2. **Hard gate at the PR — pause for user review before next unit.** After opening a PR, the agent stops and surfaces it. The next unit of work does not start until the PR is reviewed (merged or rejected).
3. **Always new commit on top within a PR — never amend.** Corrections are *additional* commits within the PR branch. The user may squash on merge.
4. **Auto-push within feature branches is OK; never to protected branches.** PR mode reverses the Commit-mode "never auto-push" rule for *feature branches* (push is required to open the PR), but maintains it absolutely for protected branches.

## Wiring an anchor for PR

1. **Declare the trait.** Add `PR` to the `.anchor` `traits:` list, e.g. `traits: [Code, Track, PR]`. (Replace any prior `Commit` declaration — they're mutually exclusive.)
2. **Configure protected branches.** GitHub branch protection rules (or equivalent) should enforce no-direct-push to the protected branches; the agent's rules complement the platform's enforcement.
3. **No structural changes required.** PR is a *behavioral* trait — it shapes how the agent acts at commit boundaries, not what the anchor folder contains.
4. **The PR rules now apply.** When F077 v1 mints, the resolution mechanism (anchor walk-up + Trait check) will route the Pilot into PR-mode behavior automatically for PR-declared anchors.

## Format

PR is a behavioral mode, not a structural one. Compositional expectations:

- **Co-requires a code repository.** PR only applies to anchors that have one — i.e., anchors with the `Code` identity trait or a top-level `code:` key in `.anchor`.
- **Co-requires a repository host with PR-capable workflow** — GitHub, Bitbucket, GitLab. Local-only or self-hosted git without PR tooling cannot satisfy PR mode.
- **Mutually exclusive with Commit and NoGit** — exactly one Git-aspect mode at a time.

## Constraints

- **Cardinality: at most one Git-aspect trait** per anchor. `PR` + `Commit` together is illegal; `PR` + `NoGit` together is illegal.
- **Composition.** Legal with `Code`, `Skill`, `Track`, `Paper`, `Drive`, `Lean`. **Excludes `Commit`** and **`NoGit`** (the three Git-aspect traits are mutually exclusive). See composability matrix in [[CAB Aspects]].
- **Co-requires Code.** Declaring `PR` on an anchor without `Code` (no repo) is illegal.
- **Co-requires PR-capable host.** Anchors using vanilla `git init` without a PR-tooled remote can't satisfy PR mode; audits should flag the mismatch.

## Expected Usage

- **Most common pairing: `Code + Track + PR`** — a production code project with a backlog and PR-gated git. Examples (planned): MuxUX, DictaMUX, Sports Vision production pipeline.
- **Why the hard gate:** the whole point of PR mode is "every state-touching commit through human review." Soft-preference variants (where the agent decides what's "substantive enough" for a PR) re-introduce the discipline-failure-mode problem F077 Q3 explicitly rejected.
- **Switch from PR to Commit mode when:** the project's blast radius drops (no longer has users, deprecated, or moved to internal-only). Edit the `.anchor` `traits:` list.
- **Does NOT auto-merge.** Even when the user reviews and approves, the merge is the user's action (via GitHub UI, CLI, or explicit instruction to the agent). PR mode is gate-and-pause, not gate-and-rubber-stamp.

## Triggers

(Per [[F091 — Trigger discipline]]. Declared `compact` trigger — when this Trait is active on the cwd anchor, the prose below is what the agent reads at POST-COMPACT reload.)

### compact

- **Git Mode — PR.** Every state-touching commit on this anchor goes through a pull request — opened on its own branch, surfaced for user review, paused until merged.
  - **PR per unit of work — never commit directly to protected branches.** Each `/mint`-ed feature, each landed `/feature`, each bug-fix gets its own branch + PR. The agent does NOT push to `main` / `master` / `develop` / any protected branch.
  - **Hard gate at the PR — pause for user review before next unit.** After opening a PR, the agent stops and surfaces it. The next unit of work does not start until the PR is reviewed (merged or rejected).
  - **Always new commit on top within a PR — never amend.** Corrections are *additional* commits within the PR branch. The user may squash on merge.
  - **Auto-push within feature branches is OK; never to protected branches.** PR mode reverses the Commit-mode "never auto-push" rule for *feature branches* (push is required to open the PR), but maintains it absolutely for protected branches.
  - **Mechanism:** reuse the [[SKA pr-flow|/pr-flow]] methodology — same branching, same PR creation, same wait-for-review semantics. PR mode just declares that this is the default for *every* state-touching commit, not opt-in per skill invocation.
  - Full user-facing spec: [[SKL Mode Git PR]]. Mode framework: [[SKL Mode]].

## Skills and audits that attach

- **Affects every skill that produces a commit on a PR-declared anchor.** Each gets its work into a feature branch + PR; surfaces the PR for review; pauses.
- **Reuses `/pr-flow`** as the underlying mechanism for PR creation + review-wait.
- **Audit:** `/audit aspects` (proposed, F090 Phase 6) will check the `PR` ⇒ `Code` co-requirement, the Git-aspect mutual exclusivity, and the PR-capable-host requirement.
- **Discipline:** [[SKL Mode Git PR]] (user-facing spec); compact-trigger prose above is the source-of-truth for POST-COMPACT inlining.

## Status

**PR-mode spec is in flight** per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in]]. Q12 (agreement gate) resolved 2026-06-01 — design is agreed. v1 mint deliverables: this Trait spec (this file), the [[Commit]] sibling, the [[NoGit]] sibling, the [[CAB Aspects]] composability matrix extension, F077 design-body rewrite to reflect Trait-list activation, and `/pr-flow` wiring to defer to PR-mode rules. Until v1 mints into the resolution mechanism, no anchor is in PR mode by default; the spec above describes the agreed design.

## History

- **2026-05-XX** — Original PR-mode concept (then "PR" hyphenated as `pr` cadence trait) introduced as part of [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] design.
- **2026-05-25** — v2 redesign: flows ARE Traits (not separate `agent_modes:` field); bare-noun naming (`PR` / `Commit` / `NoGit`) per F077 Q7.
- **2026-06-01** — F077 Q12 resolved A (agreed); Trait spec promoted to first-class CAB Trait (this file).

# BRIEF

- **This file is the canonical Trait spec for PR — the Git-aspect mode "every commit through a PR."** Edits here change the semantics for every anchor that declares `PR` in its `.anchor` `traits:` list.
- **NOT for per-anchor PR policy or per-skill PR mechanics.** Per-anchor declarations live in each anchor's `.anchor` file; the underlying PR-creation/branch-waiting mechanics live in [[SKA pr-flow]]; the user-facing mode prose lives in [[SKL Mode Git PR]]. This file is the *Trait-level* contract that ties those together.
- **Inclusion test for content here:** does it describe what declaring `PR` as a Trait *means* for any anchor — detection, the four load-bearing rules, composability with other Traits, wiring steps, audits? If yes, it belongs. Mechanism-specific detail (how `/pr-flow` branches, how the gh CLI is invoked) does NOT belong — link to the skill instead.
- **Load-bearing: the four rules + the compact-trigger block must stay aligned.** § The four load-bearing rules and § Triggers > compact both enumerate the same four rules; when one is edited the other must be updated in lockstep — the compact block is what gets inlined into POST-COMPACT RELOAD per [[F091 — Trigger discipline]].
- **Load-bearing: mutual exclusivity with `Commit` and `NoGit`.** The three Git-aspect Traits are exactly-one-per-anchor; any edit that softens this (e.g. "PR can coexist with Commit for certain branches") breaks the resolution mechanism in [[CAB Aspects]]. Don't weaken without a coordinated CAB Aspects update.
- **Cross-references to keep in sync when editing:** [[CAB Aspects]] composability matrix, [[Commit]] and [[NoGit]] sibling specs, [[SKL Mode Git PR]] user-facing spec, [[SKA pr-flow]] mechanism, F077 design body.
- **Naming/formatting conventions:** Trait name is the bare noun `PR` (no hyphen, no "PR-mode" suffix) per F077 Q7; the four rules are presented as a numbered list in § The four load-bearing rules and as a bulleted list in § Triggers > compact — preserve both shapes.
