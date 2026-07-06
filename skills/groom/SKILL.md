---
name: groom
description: >
  Frontier-planning operator over the anchor's backlog (and optionally
  roadmap or a named section). Purpose: get every task that could be next
  for execution — the groom frontier (Now + Next horizons + the next unmet
  roadmap milestone) — fully ready to be executed: plan it, declare its
  next step, promote to Ready, or park its blocking questions. Also repairs
  link integrity and enforces backlog invariants. Safe to call anytime.
  Asks the user NOTHING — every residual question is parked in the queries
  doc, never raised in chat (per Query PRD R1). Use when the user says
  "groom", "groom the backlog", "/groom", "/groom roadmap", "/groom
  milestone {N}", "tidy the backlog".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Groom — Frontier Planning + Backlog Maintenance

**The purpose of groom is to get all tasks that could be next for execution fully ready to be executed.** Those tasks are the **groom frontier** (per [[Query PRD]] § The groom frontier, F228): rows in the **`## Now` / `## Next` horizons** plus items **soon on the relevant roadmaps** (the next unmet milestone of `{NAME} Roadmap.md`, when one exists). Grooming is *planning*, not just rebracketing: each frontier task leaves groom either genuinely executable — `[Ready]` with a declared `- **Next:**` step — or honestly parked behind its named `[Questions]` / `[Blocked]` / `[Waiting]` / `[Watching]` state. `/query` then asks the user about the frontier's residue; `/crank` executes what groom readied.

Alongside the planning, groom drives the backlog toward the **groomed state** — the invariants documented in [[CAB Backlog]] and the `R-backlog` ruleset (numbering, status well-formed, link integrity, section coverage, ordering, Definition of Ready, frontier rows planned + bracket-resolved).

Convergent — not strictly idempotent. Safe to call anytime. May leave partial state when user input is needed; a follow-up call after the user resolves questions will continue from there. `## Later` and the icebox are *not* frontier — they are groomed only on explicit invocation.

> ## ⚠️ Groom asks the user NOTHING — not even one trivial question
>
> Per [[Query PRD]] R1/R2, groom is the backlog half of the **resolution layer**: it plans, resolves, rebrackets, promotes, and **parks every residual question into the queries surface** — and it raises **zero** questions in chat. There is no exception, no "one short yes/no." Even a one-word question goes into the queries doc as a numbered entry; the determination ladder ([[SKA query]] / [[Query PRD]]) decides whether it even survives to the user or the agent just resolves it. A groom (or a triage that grooms) that ends with a question in chat is the cardinal violation.

## Groom's three activities

Groom does three things, in order. Everything in the runbook serves one of them.

### 1. Every work activity has a unique identifier

The first thing groom guarantees is that **no work is anonymous** — every piece of tracked work carries a unique handle that lives on the backlog or roadmap:

- **`F<n>` — a feature.** Backed by a feature doc under `{NAME} Design/{NAME} Features/`; the backlog row links to it (`→ [[F<n> — Title]]`).
- **`T<n>` — a task.** A unit of work with **no** feature doc — the backlog row itself is the spec. A task typically *operates on other documents*: its body carries wiki-links to the design-doc sections, files, or artifacts it acts on. The `T<n>` handle is unique on the backlog and is what every reference to the work (questions, `Q.md`, cross-links) points at.
- **`M<n>` — a milestone.** A roadmap entry in `{NAME} Roadmap.md` (hierarchical: `M1`, `M1.2`, `M1.2.3`).

You *achieve* the identity by linking: a row links to its feature doc (`F<n>`), or is itself the task record (`T<n>`), or names a roadmap milestone (`M<n>`). **A feature doc that isn't linked from the backlog/roadmap has no place in the system** — groom gives it one (mint/point a row) rather than leaving it an orphan. (Numbering policy: [[Backlog|FCT Backlog]] § Numbering.)

### 2. Identify the executable frontier

The **frontier** is everything that could be executed *soon*:

- roadmap milestones that could **plausibly be executed soon if fully specified**;
- backlog rows under **`## Now`** or **`## Next`**;
- feature docs linked from a Now/Next row.

A feature doc not listed anywhere is not on the frontier — and per activity 1 it needs a place, so give it one. (`## Later` and the icebox are **not** frontier; they are touched only on explicit `/groom later` / `/groom icebox`.)

### 3. Groom the frontier — plan each item to a known state

For every frontier item, plan it out so you know, as concretely as possible, **how you would execute it**. Grooming drives each item to exactly one of three explicit exit states:

- **Executable** → declare the concrete **`- **Next:**`** step(s) the agent will take with zero user involvement; promote to `[Ready]`.
- **Has questions** → **enumerate** them and encode each via `/query` into the queries surface (following the question bar below); bracket the row `[Questions]`.
- **Blocked** → name **specifically what it is blocked on** — `[Blocked …]` / `[Waiting …]` / `[Watching …]` with the body stating the exact obstacle or awaited event. A vague blocker is not a groomed state.

After grooming, **nothing on the frontier is in an unknown state**: each item is executable (with next steps), questioned (with enumerated questions), or blocked (with a named blocker).

> **The question bar — every question groom parks MUST satisfy all five (enforced by `/query`).** A parked question is worthless unless the user can answer it in one shot. Each carries:
> 1. **its work-item identifier** — the `[[F<n>]]` / `[[T<n>]]` / `[[M<n>]]` it belongs to, so the user knows *what task* is asking;
> 2. **a specific question** — the concrete fork being decided/assessed (not "which families?" but the exact choice);
> 3. **labeled options** — `**(A)** / **(B)** / **(C)**`, each on its own line;
> 4. **a recommendation** — `Lean (A)` or `None`, always present;
> 5. **direct wiki-links to every artifact** the user must look at to answer — if the question is about a doc/file/output, the link is *in* the question; if it's about the behavior/performance of something, it names and links the specific thing being assessed.
>
> A `[Questions]` row missing these — no identifier, no links, no specific ask, no options, no recommendation — is a failure all the way around (see the anti-pattern in [[SKA query]] / [[Query PRD]]).

DMUX trigger: **`groom`** (prefix-trigger; whatever you dictate after becomes the argument). Slash invocation: `/groom`, `/groom roadmap`, `/groom milestone {N}`, `/groom F{n}` (single-item).


## Top-level vs sub-skill invocation

`/groom` behaves differently based on **who invoked it**:

- **Top-level (user typed `/groom`, said `groom`, or asked for the backlog to be cleaned up)**: after the cleanup work is done, end by invoking `/triage` so the user sees the resulting state of the anchor. The /triage step is implicit — the user expects to see what changed.
- **Sub-skill (another skill's runbook invokes `/groom` as part of its chain — e.g., `/crank`'s no-action fallback)**: do the cleanup work, **stop**. Don't run `/triage`, don't glance anything, don't print the post-groom UX. The parent skill is orchestrating; it'll surface state if it wants to.

The agent determines top-level vs sub-skill from conversation context: if the user's most recent message was `/groom` (or a natural-language request to groom), it's top-level. If `/groom` is being invoked as part of another skill's runbook, it's a sub-skill call.

**Default when ambiguous: top-level.** Better to end with `/triage` once when not strictly needed than to skip it when the user expected it.


**Question format when parking**: when `/groom` creates a feature doc with `## Open Questions`, the questions follow the [[DSC ask-format]] discipline.

## When to Use

- User says `groom`, `/groom`, `groom the backlog`, `tidy the backlog`, or asks for the backlog to be promoted/cleaned.
- After the user has answered questions in a feature doc and wants the next round of items processed.
- Whenever the backlog has accumulated enough Upcoming items that hand-promotion is too slow.
- Whenever invariants might have drifted (broken `→ [[X]]` links, missing F-numbers, items in wrong sections).


## Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

Sharper than "design questions resolved." If the task still hides any "wait, what about X?" that the user would have to answer, it's **not** Ready — it's blocked on questions, and `/groom` should park those questions in a feature doc rather than promote the bullet.

(Authoritative wording lives in [[CAB Backlog]] § Definition of Ready.)


## Item Status — How to Read It

Every backlog item has one of these statuses, derived from where the bullet sits and what it links to:

| Status | How to recognize | What `/groom` does |
| --- | --- | --- |
| **Ready** | Bullet is under `## Ready` H2 | Check the plan: a `[Ready]` row without a `- **Next:**` sub-bullet is not really ready — write the next autonomous step (or rebracket honestly). Otherwise skip. |
| **Active** | Bullet is under `## Active` H2 | Skip — actively being worked. |
| **Blocked on questions** | Bracket `[Questions]` and bullet text contains a `→ [[Feature Doc]]` or `→ [[Open Questions]]` link | Skip — only the user can resolve those. |
| **Blocked (other)** | Bracket `[Blocked]` (generic, body explains) or `[Blocked F<NNN>]` (chained on another feature) | Skip — the blocker is external. When the chained `F<NNN>` reaches `[Done]`, /groom may rebracket on a future sweep. |
| **Unset / Upcoming** | Bullet is under a horizon H2 (`## Now`, `## Next`, `## Later` per [[SKA backlog]]) — or the legacy `## Upcoming` — or `## Legwork`, with bracket `[ ]` / `[Designing]` / absent, AND has no link to active open questions | **Process** — try to ready it. |
| **Verify**, **Done** | Bullet under those H2s | Skip — out of scope. |

The `→ [[X]]` link convention is documented in [[CAB Backlog]].


## Invocation

| Invocation | Scope |
| --- | --- |
| `/groom` | **The frontier** — items under `## Ready` / `## Now` / `## Next` (+ the next unmet roadmap milestone, when the anchor has a roadmap). Default. |
| `/groom all` | Every Unset / Upcoming item across the whole backlog, `## Later` included. |
| `/groom now` | Only items under `## Now`. |
| `/groom next` | Only items under `## Next`. |
| `/groom later` | Only items under `## Later`. |
| `/groom upcoming` | Only items under legacy `## Upcoming` (alias for `/groom now` on migrated anchors). |
| `/groom legwork` | Only items under `## Legwork`. |
| `/groom icebox` | Walk `{NAME} Icebox.md` instead of the backlog. Useful for thawing iced items back into the backlog or reviewing what's parked. Default scope (bare `/groom`) excludes the icebox per `[[SKA workflow]]` § Active-work invariant. |
| `/groom roadmap` | Operate on the roadmap's next milestone instead of the backlog. |
| `/groom roadmap {milestone}` | Operate on a named roadmap milestone. |
| `/groom {F-number}` | Single item, by F-number. |
| `/groom {item name}` | Single item, by name match. |


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say so and stop.
- For backlog modes: read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`.
- For roadmap mode: read `{NAME} Docs/{NAME} Plan/{NAME} Roadmap.md`.
- If the source file is missing, report and stop.

### 2. Enumerate candidates

Walk every bullet in scope — **default scope is the frontier** (`## Ready` / `## Now` / `## Next`, plus the next unmet roadmap milestone when a `{NAME} Roadmap.md` exists). For each bullet, derive its status (per § Item Status). Candidates for planning are status **Unset / Upcoming** plus any `[Ready]` row missing its `- **Next:**` sub-bullet.

If scope was provided as an argument (`all`, `now`, `later`, …), narrow or widen accordingly.

### 2a. Bracket reassessment — rewrite stale/non-standard brackets (per F061)

Before promotion work, walk every bullet in scope and **reassess any non-standard or stale bracket**, rewriting to the correct standard bracket per `[[SKA workflow]]`. This is the structural home for the rebracketing discipline; `/triage` enforces honesty at render-time, `/groom` is where the actual rewrites land. The bracket-reassessment runs lazily — `/crank`'s cascade (per `[[SKA crank]]` § 2a) only invokes `/groom` when the Ready queue runs dry, so most cycles don't pay the cost.

**Mutation discipline — all rewrites go through `state task update`.** Do not edit `{NAME} Backlog.md` directly. Each "rewrite to `[X]`" below maps to:

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status <X>                       # bracket-only; preserves title+body
~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Done --horizon Done       # rewrite + move (e.g., stale [Done] in horizon H2)
```

Omitting `--horizon` keeps the row in its current H2; passing `--horizon Active|Done|Ready|...` moves it. Title and body are preserved when omitted (the script reads the existing row). The script auto-refreshes `~/ob/kmr/Q.md`, so § 5's post-condition is satisfied for free.

Cases to detect and rewrite:

- **`[Partial — N of M done]`** (or any `[Partial …]` variant) — NOT a valid bracket per `[[CAB Backlog]]` § Status brackets. Reassess by reading the row body + sub-bullets + linked feature doc:
  - All remaining sub-bullets are mechanical and unblocked → rewrite to `[Ready]`. Move partial-progress count to the row body if useful.
  - All remaining sub-bullets need user input → rewrite to `[Questions]`, add a `→ [[F<n> — Title]]` link to the feature doc (creating one with the Qs parked if needed, per § 3 below).
  - Mixed heterogeneous sub-bullets → **pre-split the row** per `[[CAB Backlog]]` aggregate-row treatment: one `[Ready]` row for the mechanical sub-bullets, one or more `[Questions]` rows for the user-gated ones. Drop any Done sub-bullets entirely.
- **`[Designing]` with no open Qs** in the linked feature doc — rewrite to `[Ready]` if Definition of Ready is met, else `[Questions]` if the design surfaced new Qs.
- **`[Done]`-bracketed row in a horizon H2** — move the row to `## Done`. (Stale; `/triage` skips it, `/groom` migrates it.)
- **`[Blocked]` whose blocker has resolved** — rewrite to `[Ready]` (or `[Designing]` if more design work is needed). Read the body to identify the blocker; check whether the named actor's action has landed or the chained F<NNN> has reached `[Done]`.
- **`[Waiting]` whose awaited event has occurred** — rewrite to `[Verify]` (event happened, needs checking) or `[Active]` (event happened, work can resume).
- **`[Watching Nd]` whose soak expired with no recurrence** — rewrite to `[Verify]` so the user can confirm the fix held and close to `[Done]`.
- **`[Watching]` with recurrence during the soak** — rewrite to `[Active]` or `[Designing]` (the fix didn't hold; resume work).
- **`[Verify-by YYYY-MM-DD]` past its date** (per [[DSC ask-format]] § Deferred-by-use Verify) — default: move the row to `## Done` with note *"Auto-Done <today> — `[Verify-by <date>]` window expired with no failure surfaced"*. Optional alternative: if the agent has evidence the change wasn't actually exercised since the row was filed (e.g., the relevant skill hasn't run, no usage observed), extend the bracket to `[Verify-by <new-date>]` with a body note *"Extended — no usage observed yet"*. Default is auto-Done; extension is the rare case.
- **Lazy-Blocked / Lazy-Waiting / Lazy-Watching** (body doesn't name what makes the state honest) — rewrite per `[[SKA triage]]` § Lazy states (usually `[Ready]` or `[Questions]` in disguise).
- **Bracket-H2 mismatch** — a row under `## Ready` H2 with a `[Questions]` / `[Blocked]` / `[Waiting]` / `[Watching]` bracket is misplaced (H2 implies state; bracket carries state). Either rewrite the bracket if state changed (the H2 was right) or move the row to a horizon H2 carrying the bracket (the bracket was right). The body usually disambiguates.

This reassessment is **the** primary value `/groom` adds beyond promotion: without it, `[Blocked]` / `[Waiting]` / `[Watching]` becomes a write-only graveyard and stale `[Ready]` rows mislead `/crank`.

### 3. For each candidate, in source order — PLAN it to Ready

**Investigate quietly.** Read related docs, infer answers from context, draft a spec, run lightweight planning. You may quietly invoke any of: research, plan, architect, spec, replan, `/query` (in parking mode). Do not prompt the user for anything during investigation.

**Plan.** The exit bar for a frontier candidate is *fully ready to be executed*: the row states what will be done, and a `- **Next:**` sub-bullet declares the first concrete step the agent will take with zero user involvement. Planning is groom's core work — a promotion without a plan just moves the un-readiness downstream to `/crank`.

**Decide:**

- **Bullet is Ready (or plannable to Ready)** — the description plus your investigation tells you how to do the task without further user involvement. Write the `- **Next:**` sub-bullet (the plan's first step; add 1–3 more plan sub-bullets when the approach needs stating), then promote via `state task update`:

  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Ready --horizon Ready
  ```

  F-number, title, and body are preserved. Done with this item.

- **Has questions** — anything you'd need the user to clarify. Create a feature doc at `{NAME} Docs/{NAME} Plan/{NAME} Features/F{n} — {Item Name}.md` (using the backlog row's F-number; per [[CAB Backlog]] § Numbering policy) with the standard `## Open Questions` block (per `/feature` § 1 and [[SKA queries]] § When a file is involved). Capture the questions there — **every** question goes to the doc; there is no inline-question slot (retired per [[Query PRD]] R1). **This is parking mode** (per [[SKA queries]] § Active vs Parking) — do NOT glance the new feature doc. The user invoked `/groom` as a *batch* operation specifically to defer per-item engagement; glancing each created doc would interrupt the very deferral they asked for. Update the backlog row via `state task update` to set the wiki-link body and switch the bracket to `Questions`:

  ```bash
  ~/.claude/skills/workflow/scripts/state --anchor {NAME} task update <row-id> --status Questions --body "→ [[F<n> — {Item Name}]]"
  ```

  The item is now blocked-on-questions; it surfaces through the queries doc at end-of-run via § 5.

- **Blocked on something other than the user** — bracket it honestly (`[Blocked …]` / `[Waiting …]` / `[Watching …]`) with the body naming the specific blocker/event per § 2a. A named obstacle is a groomed state; an unbracketed frontier row is not.

### 4. Build the report

Print a summary table:

```markdown
## /groom — {anchor}

| Outcome | Count | Items |
| --- | --- | --- |
| Planned to Ready | N | F3, F7, … |
| Parked on questions | N | F5 → [[F005 — X]], F12 → [[F012 — Y]] |
| Bracketed (Blocked/Waiting/Watching) | N | F9 |
| Skipped | N | {reasons summarized} |

```

### 5. Q.md update post-condition — automatic via `state`

Every `state` invocation in § 2a / § 3 automatically regenerates the anchor's per-anchor section in `~/ob/kmr/Q.md` (by shelling out to `audit-q.py --scope backlog --anchor {NAME} --fix`). The backlog file is NOT reordered — source order is preserved (per F075 Q2). Bubble-to-top is a Q.md-only behavior.

The audit's fix-by-default behavior catches any drift introduced — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (per the audit-q.md step 5 invariant, 2026-06-04) **files every non-mechanical residual as a sub-bullet on the singleton `B-QFix` row** in `{NAME} Backlog.md`. There is no "rare" gate on QFix — every residual that `--fix` didn't repair lands on the catalog.

**Loop until clean** (same discipline as `/triage` § 6, landed 2026-06-04):

```
loop (max 3 iterations):
  run `/audit q`   # auto-invoked by state per § 2a / § 3
  if residual == 0:
    break
  if residual unchanged from prev iteration:
    break          # stalled — non-mechanical residue; on QFix
  # else: loop again to catch second-order drift
```

After the loop, **before exiting**, read `{NAME} Backlog.md` for the `B-QFix` row. If present, append its sub-bullet list to chat output verbatim as *"audit-q residual — N findings outstanding (see B-QFix)."* **No silent exit when residual > 0.**

### Three guards on the loop (per the 2026-06-04 design discussions — original "mechanical-only" rule replaced by the 100%-fix principle)

1. **100% of warnings go to zero each pass — `None` is an acceptable Recommendation.** The agent's job, in every loop iteration, is to drive the residual to zero. For C9 missing Recommendation, the agent writes the Recommendation — including `**Recommendation:** None — <one-line reason>` when honest effort produces no Lean. For C12 missing rationale, the agent writes the plausible-exercise sentence (or rebrackets). For C25 missing Designing justification, the agent writes the next-action (or rebrackets). Every C-code has an agent-side fix path; **`QFix` is reserved for the rare cases where the answer genuinely requires user-private information**, not for "user might prefer something different." See `[[audit-q]]` § 5 for the per-C-code action map.
2. **Iteration cap = 3.** Matches `audit-q-fix.md` 3-pass cap. On cap, the (rare) genuinely-stuck residual is filed as QFix and surfaced.
3. **Anchor-local.** Loop iterates only on findings under the cwd anchor's tree. Cross-anchor findings route to the owning anchor's `QFix` row by `surface_file` path; the owning anchor's next `/triage` or `/groom` addresses them under the same 100%-fix rule.

### 6. (Top-level only) Hand off to `/triage`

**If sub-skill invocation: stop here.** The parent skill will surface state.

**If top-level invocation:**
- Invoke `/triage` (which regenerates the anchor's Q.md section per `[[SKA triage]]` § 6 and glances `~/ob/kmr/Q.md` per `[[SKA triage]]` § 7). This is the user's "what just happened?" view. (Step 5's Q.md regen is redundant when `/triage` follows immediately — `/triage` rewrites the same section. Either run idempotently produces the same result; keep both because sub-skill invocations don't fire step 6.)

The earlier per-step UX (open the first blocked-on-questions doc, separate `/roster` invocation) is subsumed by `/triage` — Q.md shows the inbox of items waiting on user input, including the newly-parked feature docs.


## Design Principle — Minimize User Back-and-Forth

`/groom` follows a workflow principle that applies to all batch operations against the backlog:

> **Process the entire batch autonomously before involving the user.** Never interrupt mid-run to ask. Route every emerging question to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end as the user's single next action. Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N.

(Authoritative statement lives in [[CAB Backlog]] § Design Principle — Minimize User Back-and-Forth.)


## Idempotence

`/groom` is safe to run repeatedly. Items already in `## Ready`, `## Active`, `## Verify`, `## Done`, `## Legwork`, or marked blocked-on-questions are skipped. Running twice in a row should produce no diff on the second pass if no new info has come in.


## Failure Modes

- **No anchor found** — say "No anchor found from `{cwd}` upward." and stop.
- **No backlog file (or roadmap file, in roadmap mode)** — say "No `{expected file}` at `{expected path}`." and stop.
- **Empty section** — print a one-line "Nothing to process in {scope}" and call `/roster` so the user still sees state.
