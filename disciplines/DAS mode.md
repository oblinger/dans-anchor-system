---
name: mode
description: >
  Operating-mode discipline. Pre-decides recurring "more thorough vs faster"
  trade-offs so the agent doesn't have to ask each time. Cited by other skills;
  not directly user-invocable.
user_invocable: false
---

# Mode Discipline

Operating-mode discipline that pre-decides recurring "more thorough vs faster" trade-offs so the agent doesn't have to ask each time.

A **mode** is a setting that shapes how the agent makes recurring trade-off decisions. Different anchors have different risk profiles — a freshly-built tool with no users tolerates aggressive forward motion; a deployed app with thousands of users needs more caution per change. Mode is the declaration of which posture is appropriate.

Anchor page: [[Mode]]


## The metric — outcome per interaction

The agent optimizes:

> **outcome per interaction**

with this cost structure for the denominator:

- **Heavy weight** — each content-full batch (any session where the user must read, think, and respond).
- **Lighter weight** — each round-trip within a batch (back-and-forth Q&A inside one active session).
- **Lightest weight** — each `/crank` press (no content but still attention).

The numerator is **capability produced** — features shipped, decisions resolved, working code committed, design questions answered, technical debt paid.

The whole posture follows from this metric: **minimize content-full batches first, round-trips within them second, crank presses third.** Tokens are not in the denominator at all.


## Modes-as-flat-list (per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]])

Modes are **compositional traits**, not points on a single axis. A pilot runs with one or more modes active at the same time; compatibility is documented here (not enforced by an axis schema). The default pair is **Drive + Git Standard** — Drive shapes how the agent makes trade-off decisions; Git Standard shapes how the agent handles git boundaries within those decisions. They are orthogonal and compose cleanly.

Available modes (the flat list):

| Mode | What it shapes | Doc |
|---|---|---|
| **Drive** | Trade-off posture — agent-driven, optimistic, minimum-interruption | § Drive (below) |
| **Lean** | Counterpart to Drive — invoked via `/fortify` for distrust-the-foundation work (older docs call this "Cautious"; `Lean` is the canonical trait name) | [[SKA fortify]] |
| **Commit** | Git boundaries — commit on logical breaks (never ask), terse messages, never auto-push, new-commit-on-top (never amend) | § Git Commit (below) |
| **PR** | Git boundaries — every state-touching commit gated through PR review on its own branch | § Git PR (below); [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in\|F077]] design |

**Compatibility:** Drive and Lean are mutually exclusive (you're in one or the other). Commit and PR are mutually exclusive (a pilot has exactly one Git-aspect mode active at a time). Drive composes with either Git mode; Lean composes with either Git mode. The default for new anchors is **Drive + Commit**.

**Naming history:** the Commit mode was originally called "Git Standard" (per F085). Renamed to bare-noun `Commit` per F077 Q7's resolved naming convention (`Drive`/`Lean`/`PR`/`Commit`/`NoGit`). Legacy references to "Git Standard" mean Commit mode.

## Current mode — Drive

Drive shapes the trade-off posture: agent-driven, optimistic, minimum-interruption. The load-bearing rules are inlined in `role-pilot.md` POST-COMPACT RELOAD and in [[Drive|traits/Drive]] so they prime the agent on every session start; the full-prose assertions live there and in this section.

Drive's core assertions, in clipped agent-facing form:

- **Tokens are NOT the constraint; user-interruption cost and quality ARE.** When in doubt, pick the more complete option unless there's a real risk/performance/deployment-safety issue.
- **Add tests for plausibly-reachable edge cases without asking.**
- **Adjacent cleanup is silent** — fix inline or skip; don't make a question of it.
- **Don't ask about token / PR / commit size.** Right-size for the work; commit on transitions.
- **Sweep cross-references for consistency by default.** Drift is a slow-burn problem.
- **Memory updates on surprise.** Not for routine work.
- **Docs ship with code in the same commit.**
- **DO ask** when there's a genuine safety / performance / deployment-risk / design-direction trade-off OR genuinely ambiguous user intent. Threshold: "real consequence of wrong choice," not "two plausible options exist."
- **Per-turn override:** "just do the simple thing" / "quick fix" / "minimal" → lean mode for that turn. "Be thorough about X" → reaffirms Drive.

The failure mode Drive constrains: asking about every trade-off where the wrong answer doesn't actually hurt anything. That's friction, not collaboration. Decide and move.


## Git Commit mode (per [[F085]]; renamed from "Git Standard" per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7)

**Commit** is one of the two Git-aspect modes. **Default for new anchors; default for SKA.** Paired with Drive in the canonical setup. The other Git-aspect mode is **PR** (next section).

Commit mode shapes how the agent handles git boundaries inside a mint or skill execution. The agent commits at logical breaks — *it does not ask permission*. Asking "want me to commit?" is itself a Commit-mode violation; commit IS the default at every boundary.

**Four load-bearing rules:**

1. **Commit at logical boundaries — never ask permission.** A boundary is one of (hybrid per F085 Q1):
   - **Per-skill-exit** — when a skill finishes its main work (e.g., `/feature` finishes commissioning, `/mint` finishes implementation, `/groom` finishes the sweep, `/atlas add` lands an entry).
   - **Per-state-transition** — when a backlog item flips state (`[Active]` → `[Verify]`, `[Verify]` → `[Done]`, `[Ready]` → `[Active]`).
   - **Per-judgment-collapse** — when two or three rapid sequential edits naturally belong together (don't fragment into trivial commits; use judgment to bundle).
   The agent does NOT ask "should I commit now?" / "want me to commit?" — those questions are themselves the failure mode. Commit is the default at any of these moments.
2. **Always new commit on top — never amend.** When the agent needs to extend or correct prior work, it adds a new commit; it does not `git commit --amend`. Multiple closely-related commits can be **squashed locally by the user before push** if they prefer a tidier history — but the agent's job is to commit freely; squashing is a user-initiated cleanup, not an agent default. Per global `~/.claude/CLAUDE.md`: pre-commit-hook failures still create new commits (NEVER amend after hook failure).
3. **Terse commit messages — no boilerplate.** Short subject line. No "Generated by Claude" / "Co-Authored-By" trailers unless explicitly opted in. Body adds context when the change is substantial; tiny edits get subject-only commits. In kmr-flavored vaults (per memory), terse-or-blank messages are acceptable.
4. **Never auto-push.** The agent commits freely but does NOT push to remotes unless the user explicitly says so. Auto-push crosses the [[F068 — Assume-and-announce discipline (Drive mode)|F068]] irreversibility threshold; auto-commit does not (history can be rewritten locally).

**Composition with `/pr-flow` (per F085 Q2):** Commit mode yields to PR-mode semantics **only during** an active `/pr-flow` invocation. Outside of `/pr-flow`, Commit is in effect; inside `/pr-flow`, the PR-mode rules (next section) take over until `/pr-flow` exits.

**Why no auto-push (per F085 Q3):** push is visible to others, hard to reverse, and crosses the F068 irreversibility threshold ("invisible OR high recoverability cost OR irreversible — always ASK"). Commit-only auto-behavior keeps the user in control of when work becomes public.

**Agent-facing summary** (the same load-bearing rules in clipped form for inclusion in `role-pilot.md` POST-COMPACT RELOAD):

- **Commit on logical boundary — don't ask.** Skill-exit, state-transition, judgment-collapsed rapid edits. "Want me to commit?" is itself a violation.
- **Always new commit on top — never amend.** Squashing is the user's call before push, not the agent's default.
- **Terse subject-only when small; body when substantial. No boilerplate.**
- **Never auto-push.** Ask explicitly before any `git push`.
- **Inside `/pr-flow`** → defer to PR-mode rules until /pr-flow exits.

## Git PR mode (per [[F077]]; design in flight, Q12 = agreement gate)

**PR** is the other Git-aspect mode. Activated when an anchor needs every state-touching commit to be gated through pull-request review before the work continues. Used for high-blast-radius repositories (production code with users, shared infrastructure).

PR mode shapes git boundaries differently: instead of committing freely against the working branch, the agent opens a PR for each unit of work, pauses for user review, and resumes on the next unit only after merge. Reuses the `/pr-flow` methodology.

**Four load-bearing rules:**

1. **PR per unit of work — never commit directly to main/protected branches.** Each `/mint`-ed feature, each landed `/feature`, each bug-fix gets its own branch + PR. The agent does NOT push to `main` / `master` / `develop` / any protected branch.
2. **Hard gate at the PR — pause for user review before next unit.** After opening a PR, the agent stops and surfaces it. The next unit of work does not start until the PR is reviewed (merged or rejected). PR mode is the explicit "every state-touching commit through human review" posture.
3. **Always new commit on top within a PR — never amend.** Same rule as Commit mode: corrections are additional commits within the PR branch, not amends. The user may squash on merge if they want a single commit per PR.
4. **Auto-push within feature branches is OK; never to protected branches.** PR mode reverses the Commit-mode "never auto-push" rule for *feature branches* (push is required to open the PR), but maintains it absolutely for protected branches.

**When to use PR mode:** repositories where the cost-of-merge-mistake is high (production code with users, shared libraries, deployed infrastructure). Anchors declare it by listing `PR` (instead of `Commit`) in their `traits:`.

**Agent-facing summary** (clipped for POST-COMPACT RELOAD):

- **PR per unit of work.** Each feature / mint / bug-fix → its own branch + PR. Never commit to protected branches.
- **Hard gate at PR — pause for user review.** Surface the PR; do not start the next unit until merged.
- **Always new commit on top within the PR — never amend.**
- **Auto-push to feature branches OK; never to protected.**

**Status:** PR-mode spec is in flight per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] (Q12 = agreement gate; v1 mint lands when user accepts). Until v1 mints, no anchor is in PR mode by default; the section above describes the agreed v2 design.


## How mode is currently resolved

**v1 (current):** the system-wide mode is declared inline in `role-pilot.md` § POST-COMPACT RELOAD, where it primes the agent every session.

**v2 (eventual, gated on F034 Q3 resolution):** per-anchor mode declared via `mode:` field in `.anchor` config; system-wide default in `~/.claude/CLAUDE.md`. Anchor-specific override wins. A future `/mode` slash command will support inspection (`/mode` reports current) and switching (`/mode set drive` rewrites the declaration).


## Cited by

- `role/role-pilot.md` § POST-COMPACT RELOAD — inlines Drive's + Commit's load-bearing rules.
- `/crank`, `/mint`, `/feature`, `/ask`, `/groom`, `/code` — should consult mode when making recurring trade-off decisions (per F034 § Affected surfaces).


## Cross-references

- **[[F034 — Operating Mode]]** — design discussion (open questions for v2).
- **[[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in]]** — PR-mode design + Trait-list activation architecture.
- **[[F085]]** — Git Standard mode (now Commit) original design + load-bearing rules.
- **`role/role-pilot.md`** — the inlined POST-COMPACT copy.

## Mode framework history

- **2026-05-04** — Mode framework established. **Drive** defined as the first mode and rolled out as the system default; per-anchor switching deferred until ≥2 modes exist. (Original capture: the `SKL Mode` / `SKL Mode Drive` reading docs, since folded into this discipline doc.)
- **2026-05-24** — **Git Standard** mode added per [[F085]]. Three load-bearing rules (commit on logical boundary, terse messages, never auto-push). Composed with Drive as the canonical pair.
- **2026-06-01** — **Renamed Git Standard → Commit** per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7 (bare-noun naming convention `Drive`/`Lean`/`PR`/`Commit`/`NoGit`). Added explicit "never ask permission to commit" rule and "always new commit on top — never amend" rule. Commit-mode bullets inlined into `role-pilot.md` POST-COMPACT RELOAD — closes the gap where F085's rules existed in `mode/SKILL.md` but didn't prime the Pilot at session start (the cause of the observed "agent keeps asking to commit" symptom).

## Considering these — Drive-mode tightening log

Ideas for Drive-mode tightening, parked while we collect agent-failure data to validate them. We tighten Drive iteratively — observed agent friction (typically a screenshot or log) becomes evidence for a sharper rule. Adoption is reactive (failure-evidenced), not speculative.

**Pending validation:**

- *Recommendations aren't pre-asks; never ask a Q whose answer is already known.* — **Failure observed 2026-05-19** (DMUX triage agent): the agent noticed two backlog rows were already resolved in prior chat (B1, B2 — user had answered "A: DMUX owns" and "C: hybrid"), correctly reasoned that the right action was `[Questions] → [Done]` + the small follow-up edits, *and then asked* "Reply close B1+B2 to land both immediately." The ask was redundant — every necessary input was already in chat or in the row text. **The pattern this misses:** existing rules cover *"shouldn't ask"* (assume-and-announce, no-confirmation-menu, what's-next-→-pick-AND-execute), but the failure framing isn't "menu-asking" or "trade-off-asking" — it's *"polite confirmation of an action my own analysis already specified."* Agent rationalizes it as collaboration; from the user it lands as friction with a "should I do what we both know to do?" shape. **Proposed rule (clipped form):** *If you've just stated the right action — in rules, in chat, or in your own recommendation a sentence ago — execute it. "Should I X?" / "Want me to X?" / "Recommendation X — proceed?" are still asks even when X is correct. Recommendations are decisions; cut the question, execute, bold-announce if the four gates apply.* Validate against the next observed instance (or counter-instance: a case where this rule would have caused harm) before promoting to live + POST-COMPACT.

**Promoted (no longer parked):**

- *Define success criteria. Loop until verified.* — Adopted as a top-level pilot constant in `role-pilot.md` (2026-05-06). Reinforces the proactive test-then-loop discipline; mode-agnostic, so not duplicated under Drive sub-bullets.

**Rejected with reason:**

- *Don't assume. Don't hide confusion. Surface tradeoffs.* — "Surface tradeoffs" directly conflicts with the "no confirmation menu" rule above (it *is* the Path A vs Path B failure mode). "Don't assume" is ambiguous — could mean "don't pretend you have context you don't" (good) or "always verify before acting" (counter-Drive). "Don't hide confusion" is salvageable if rephrased to not invite menu-asking.
- *Minimum code that solves the problem. Nothing speculative.* — Already covered in `~/.claude/CLAUDE.md`: "Don't add features, refactor, or introduce abstractions beyond what the task requires… A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper. Don't design for hypothetical future requirements." Adding here would duplicate.
- *Touch only what you must. Clean up only your own mess.* — Directly counter to Drive's "Adjacent cleanup is silent" and "Cross-references swept by default." This is a Lean-mode discipline; if Lean ever gets its own doc, it lives there, not in Drive or pilot.
