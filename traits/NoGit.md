---
description: NoGit Trait — anchor has no git repository; the agent does not perform git operations on it. The default Git-aspect mode for anchors without code. Composable capability trait.
---

# NoGit

The Git-aspect Trait declaring that an anchor has no per-anchor git repository and the agent performs no git operations on it.

## What it is

**NoGit declares that the anchor has no git repository and the agent should not perform any git operations on it.** Reading and editing files is fine; `git add`, `git commit`, `git push`, branch operations — none of these apply.

NoGit is the Git-aspect mode for anchors that *aren't code projects* — documentation-only anchors, planning anchors, reference compendia, the user's knowledge tree without per-anchor version control. It declares the absence of a repository, distinguishing "no commits because the user wants no commits" from "no commits because the agent forgot."

The kmr vault is a special case (it's a backup repo at the vault root, but individual anchors inside it don't have their own repos). For an anchor *inside* a kmr-style backup repo, the kmr-root commit discipline applies; the anchor itself doesn't take a Git-aspect mode.

## How it's detected

- **Trait:** `NoGit` appears in the anchor's `.anchor` `traits:` list (one-line lookup; no file inference per [[CAB Aspects]]).
- **Default fallback:** when no Git-aspect trait is declared AND the anchor does **not** have the `Code` identity trait (no repo), the agent defaults to NoGit mode. Explicit declaration is recommended once an anchor's mode is settled.
- An anchor with `Code` (has a repo) cannot take NoGit — `Code + NoGit` is a contradiction.

## The rule

NoGit is the simplest of the Git-aspect traits — one rule:

1. **No git operations.** The agent does not run `git add`, `git commit`, `git push`, `git branch`, or any other state-touching git command on this anchor's files. Reading via `git log` / `git blame` for context is fine; mutating actions are not. If the agent finds itself in a NoGit anchor with a `.git/` directory, that's a config mismatch — surface it, don't proceed.

(Anchors inside a parent git repo — like a typical kmr vault — inherit the parent's commit discipline. NoGit on the anchor doesn't mean the parent's repo can't see its files; it means the agent doesn't manage a *per-anchor* repo here.)

## Wiring an anchor for NoGit

1. **Declare the trait.** Add `NoGit` to the `.anchor` `traits:` list, e.g. `traits: [Topic, NoGit]` or `traits: [Simple, NoGit]`.
2. **Don't `git init` here.** A NoGit-declared anchor that has a `.git/` directory is a contradiction; if one exists from prior work, decide whether to keep it (in which case re-declare as `Code + Commit` or `Code + PR`) or remove it.
3. **No structural changes required.** NoGit is a behavioral trait — it constrains the agent's actions, not the folder's contents.

## Format

NoGit imposes no on-disk structural requirements. Compositional expectations:

- **Mutually exclusive with the Code identity trait.** `Code + NoGit` is a contradiction.
- **Mutually exclusive with Commit and PR.** Exactly one Git-aspect mode at a time.

## Constraints

- **Cardinality: at most one Git-aspect trait** per anchor. `NoGit` + `Commit` is illegal; `NoGit` + `PR` is illegal.
- **Composition.** Legal with `Simple`, `Topic`, `Paper`, `Track`, `Drive`, `Lean`. **Excludes `Code`** (you can't have a repo and declare NoGit). **Excludes `Skill`** (Skills are runtime code anchors and inherit git from the wider skills repo). See composability matrix in [[CAB Aspects]].
- **Excludes Code.** Declaring `NoGit` on a `Code` anchor is illegal — they directly contradict.

## Expected Usage

- **Most common pairings:** `Topic + NoGit` (a knowledge area without its own repo), `Simple + NoGit` (a minimal folder marker without git), `Paper + NoGit` (a writing project whose versioning is handled by the document not by git).
- **Special case — kmr vault.** Anchors inside `~/ob/kmr/` are governed by the kmr vault's own git discipline (terse commits, no elaborate messages, per memory). NoGit on an inner anchor doesn't override the vault's outer git; it just declares that the anchor isn't managing its own per-anchor repo. Most kmr-internal anchors are effectively `NoGit` even without explicit declaration.
- **Don't use to silence agents.** If the user wants to *suppress* committing temporarily, that's a session-level direction ("don't commit while we iterate") — not a permanent NoGit trait. NoGit means "this anchor doesn't have its own repo," not "stop committing for now."

## Triggers

(Per [[F091 — Trigger discipline]]. Declared `compact` trigger — when this Trait is active on the cwd anchor, the prose below is what the agent reads at POST-COMPACT reload.)

### compact

- **Git Mode — NoGit.** This anchor has no per-anchor git repository; the agent does not perform git operations on it.
  - **No git operations.** No `git add`, `git commit`, `git push`, `git branch`, or any other state-touching git command on this anchor's files. Reading via `git log` / `git blame` for context is fine; mutating actions are not.
  - **Mismatch handling.** If the agent finds a `.git/` directory in a NoGit-declared anchor, that's a config mismatch — surface it, don't proceed silently. Either re-declare the anchor as `Code + Commit` (or `Code + PR`), or remove the stray `.git/`.
  - **Parent-repo inheritance.** Anchors inside a parent git repo (typical kmr-vault case) inherit the parent's commit discipline. NoGit on the inner anchor doesn't mean the parent repo can't see its files; it means the agent doesn't manage a *per-anchor* repo here.

## Skills and audits that attach

- **Constrains every skill that ends with a commit boundary.** On a NoGit anchor, those skills finish their work and stop — no commit step.
- **Audit:** `/audit aspects` (proposed, F090 Phase 6) will check the `NoGit ⊕ Code` exclusion (contradiction) and the Git-aspect mutual exclusivity.

## History

- **2026-05-25** — `NoGit` cadence option introduced as part of [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] v2 redesign (bare-noun naming).
- **2026-06-01** — Promoted to first-class CAB Trait (this file) alongside `Commit` and `PR`.

# BRIEF

- **This is the spec for one Git-aspect Trait.** Edits here change the rule for every NoGit-declared anchor across the vault — treat as load-bearing.
- **Not a catalog of NoGit anchors.** Do not list individual anchors that carry the trait; the `.anchor` `traits:` field is the source of truth, not a roster maintained here.
- **Scope guard — Git-aspect only.** Only mutual-exclusivity, detection, and behavioral rules about the *agent's git actions* belong here. Identity-trait content (Code, Topic, Simple) belongs in those Trait files; composability matrix belongs in [[CAB Aspects]]; do not duplicate either upward into this file.
- **Mutual-exclusivity is load-bearing.** `NoGit ⊕ Code`, `NoGit ⊕ Commit`, `NoGit ⊕ PR` — these exclusions are cited by `/audit aspects` and by sibling Trait files. If the rule changes, update [[CAB Aspects]] and the sibling files ([[Commit]], [[PR]], [[Code]]) in lockstep.
- **POST-COMPACT `compact` trigger is consumed by the role loader.** The `### compact` subsection under `## Triggers` is read verbatim at reload — keep it self-contained (no required wiki-link chase) and aligned with the body rule. If the rule changes, change both.
- **Don't inline session-level direction.** "Stop committing for now" is a runtime instruction, not a trait — note the distinction (already covered in § Expected Usage) but do not expand this file into session-control guidance.
- **History entries are dated bullets, terse.** Append only when the trait's spec materially changes; don't pile general CAB history here.
