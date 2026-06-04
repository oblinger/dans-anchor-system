---
name: groom
description: >
  Convergent maintenance operator over the anchor's backlog (and optionally
  roadmap or a named section). Each invocation moves the artifact toward a
  defined groomed state — promotes items to Ready where possible, parks
  questions in feature docs, repairs link integrity, enforces invariants.
  Safe to call anytime. Never interrupts the user mid-run. Ends with the
  first blocked-on-questions doc opened for the user, then a roster, then
  optionally one final trivial inline question. Use when the user says
  "groom", "groom the backlog", "/groom", "/groom roadmap", "/groom
  milestone {N}", "tidy the backlog".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Groom — Convergent Backlog Maintenance

Walk the current anchor's backlog and move it toward the **groomed state** — a state that satisfies the invariants documented in [[CAB Backlog]] (numbering, status well-formed, link integrity, section coverage, ordering, Definition of Ready). Items that can be promoted to Ready are promoted; items with open questions get parked in feature docs; broken links get repaired or flagged.

Convergent — not strictly idempotent. Safe to call anytime. May leave partial state when user input is needed; a follow-up call after the user resolves questions will continue from there.

DMUX trigger: **`groom`** (prefix-trigger; whatever you dictate after becomes the argument). Slash invocation: `/groom`, `/groom roadmap`, `/groom milestone {N}`, `/groom F{n}` (single-item).


## Top-level vs sub-skill invocation

`/groom` behaves differently based on **who invoked it**:

- **Top-level (user typed `/groom`, said `groom`, or asked for the backlog to be cleaned up)**: after the cleanup work is done, end by invoking `/triage` so the user sees the resulting state of the anchor. The /triage step is implicit — the user expects to see what changed.
- **Sub-skill (another skill's runbook invokes `/groom` as part of its chain — e.g., `/crank`'s no-action fallback)**: do the cleanup work, **stop**. Don't run `/triage`, don't glance anything, don't print the post-groom UX. The parent skill is orchestrating; it'll surface state if it wants to.

The agent determines top-level vs sub-skill from conversation context: if the user's most recent message was `/groom` (or a natural-language request to groom), it's top-level. If `/groom` is being invoked as part of another skill's runbook, it's a sub-skill call.

**Default when ambiguous: top-level.** Better to end with `/triage` once when not strictly needed than to skip it when the user expected it.


**Question format when parking**: when `/groom` creates a feature doc with `## Open Questions`, the questions follow the [[ask-format]] discipline.

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
| **Ready** | Bullet is under `## Ready` H2 | Skip — already ready. |
| **Active** | Bullet is under `## Active` H2 | Skip — actively being worked. |
| **Blocked on questions** | Bracket `[Questions]` and bullet text contains a `→ [[Feature Doc]]` or `→ [[Open Questions]]` link | Skip — only the user can resolve those. |
| **Blocked (other)** | Bracket `[Blocked]` (generic, body explains) or `[Blocked F<NNN>]` (chained on another feature) | Skip — the blocker is external. When the chained `F<NNN>` reaches `[Done]`, /groom may rebracket on a future sweep. |
| **Unset / Upcoming** | Bullet is under a horizon H2 (`## Now`, `## Next`, `## Later` per [[SKA backlog-horizons]]) — or the legacy `## Upcoming` — or `## Legwork`, with bracket `[ ]` / `[Designing]` / absent, AND has no link to active open questions | **Process** — try to ready it. |
| **Verify**, **Done** | Bullet under those H2s | Skip — out of scope. |

The `→ [[X]]` link convention is documented in [[CAB Backlog]].


## Invocation

| Invocation | Scope |
| --- | --- |
| `/groom` | All Unset / Upcoming items across the whole backlog. Default. |
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

Walk every bullet in scope. For each bullet, derive its status (per § Item Status). Filter to status **Unset / Upcoming**.

If scope was provided as an argument, narrow to bullets in that section only.

### 2a. Bracket reassessment — rewrite stale/non-standard brackets (per F061)

Before promotion work, walk every bullet in scope and **reassess any non-standard or stale bracket**, rewriting to the correct standard bracket per `[[SKA workflow]]`. This is the structural home for the rebracketing discipline; `/triage` enforces honesty at render-time, `/groom` is where the actual rewrites land. The bracket-reassessment runs lazily — `/crank`'s cascade (per `[[SKA crank]]` § 2a) only invokes `/groom` when the Ready queue runs dry, so most cycles don't pay the cost.

**Mutation discipline — all rewrites go through `backlog-edit.py`.** Do not edit `{NAME} Backlog.md` directly. Each "rewrite to `[X]`" below maps to:

```bash
~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} same <row-id> <X>     # bracket-only; preserves title+body
~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} Done <row-id> Done    # rewrite + move (e.g., stale [Done] in horizon H2)
```

`same` keeps the row in its current H2; an explicit horizon name moves it. Title and body are preserved when omitted (the script reads the existing row). The script auto-refreshes `~/ob/kmr/Q.md`, so § 5's post-condition is satisfied for free.

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
- **`[Verify-by YYYY-MM-DD]` past its date** (per [[ask-format]] § Deferred-by-use Verify) — default: move the row to `## Done` with note *"Auto-Done <today> — `[Verify-by <date>]` window expired with no failure surfaced"*. Optional alternative: if the agent has evidence the change wasn't actually exercised since the row was filed (e.g., the relevant skill hasn't run, no usage observed), extend the bracket to `[Verify-by <new-date>]` with a body note *"Extended — no usage observed yet"*. Default is auto-Done; extension is the rare case.
- **Lazy-Blocked / Lazy-Waiting / Lazy-Watching** (body doesn't name what makes the state honest) — rewrite per `[[SKA triage]]` § Lazy states (usually `[Ready]` or `[Questions]` in disguise).
- **Bracket-H2 mismatch** — a row under `## Ready` H2 with a `[Questions]` / `[Blocked]` / `[Waiting]` / `[Watching]` bracket is misplaced (H2 implies state; bracket carries state). Either rewrite the bracket if state changed (the H2 was right) or move the row to a horizon H2 carrying the bracket (the bracket was right). The body usually disambiguates.

This reassessment is **the** primary value `/groom` adds beyond promotion: without it, `[Blocked]` / `[Waiting]` / `[Watching]` becomes a write-only graveyard and stale `[Ready]` rows mislead `/crank`.

### 3. For each candidate, in source order

**Investigate quietly.** Read related docs, infer answers from context, draft a spec, run lightweight planning. You may quietly invoke any of: research, plan, architect, spec, replan, `/ask` (in parking mode). Do not prompt the user for anything during investigation.

**Decide:**

- **Bullet is Ready as-is** — the description (plus any inference from related docs) tells you how to do the task without further user involvement. Promote via `backlog-edit.py`:

  ```bash
  ~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} Ready <row-id> Ready
  ```

  F-number, title, and body are preserved. Done with this item.

- **Has questions** — anything you'd need the user to clarify. Two sub-paths:

  1. **Inline-deferred slot is empty AND this is exactly ONE genuinely trivial question** (one short sentence, one yes/no, one short answer): hold it in the inline-deferred slot. Mark the item for revisit when the user answers — for now, leave the bullet where it is.
  2. **Otherwise** — create a feature doc at `{NAME} Docs/{NAME} Plan/{NAME} Features/F{n} — {Item Name}.md` (using the backlog row's F-number; per [[CAB Backlog]] § Numbering policy) with the standard `## Open Questions` block below the H1 (per `/feature` § 1 and [[SKA ask]] § When a file is involved). Capture the questions there. **This is parking mode** (per [[SKA ask]] § Active vs Parking) — do NOT glance the new feature doc. The user invoked `/groom` as a *batch* operation specifically to defer per-item engagement; glancing each created doc would interrupt the very deferral they asked for. Update the backlog row via `backlog-edit.py` to set the wiki-link body and switch the bracket to `Questions`:

     ```bash
     ~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} same <row-id> Questions "{Item Name}" "→ [[F<n> — {Item Name}]]"
     ```

     The item is now blocked-on-questions; the doc surfaces only at end-of-run via § 5 (the *first* one, not all).

**Inline-deferred slot rules.**
- At most ONE item across the whole run may use the inline slot.
- The question must be genuinely short — one sentence, fits on one line.
- If a second item would qualify, it goes to a feature doc instead.
- The slot is *only* surfaced at the very end of the run, after the roster (see § 7).

### 4. Build the report

Print a summary table:

```markdown
## /groom — {anchor}

| Outcome | Count | Items |
| --- | --- | --- |
| Promoted to Ready | N | F3, F7, … |
| Promoted to feature doc | N | F5 → [[F005 — X]], F12 → [[F012 — Y]] |
| Deferred inline | 0 or 1 | F9 |
| Skipped | N | {reasons summarized} |
```

### 5. Q.md update post-condition — automatic via `backlog-edit.py`

Every `backlog-edit.py` invocation in § 2a / § 3 automatically regenerates the anchor's per-anchor section in `~/ob/kmr/Q.md` (by shelling out to `audit-q.py --scope backlog --anchor {NAME} --fix`). The backlog file is NOT reordered — source order is preserved (per F075 Q2). Bubble-to-top is a Q.md-only behavior.

The audit's fix-by-default behavior catches any drift introduced — broken links, stale brackets, banner mismatches, stale `[Done]` rows — and either repairs them mechanically OR (per the audit-q.md step 5 invariant, 2026-06-04) **files every non-mechanical residual as a sub-bullet on the singleton `B-QFix` row** in `{NAME} Backlog.md`. There is no "rare" gate on QFix — every residual that `--fix` didn't repair lands on the catalog.

**Loop until clean** (same discipline as `/triage` § 6, landed 2026-06-04):

```
loop (max 3 iterations):
  run `/audit q`   # auto-invoked by backlog-edit.py per § 2a / § 3
  if residual == 0:
    break
  if residual unchanged from prev iteration:
    break          # stalled — non-mechanical residue; on QFix
  # else: loop again to catch second-order drift
```

After the loop, **before exiting**, read `{NAME} Backlog.md` for the `B-QFix` row. If present, append its sub-bullet list to chat output verbatim as *"audit-q residual — N findings outstanding (see B-QFix)."* **No silent exit when residual > 0.**

### Three guards on the loop (per the 2026-06-04 design discussion)

1. **Mechanical-only.** Auto-apply only what `audit-q.py --fix` handles + audit-q skill step 3's safe inline-judgment rewrites (link near-match, bracket-from-state, block-ID-on-target, stale-rename). Never write agent-guessed prose into feature docs to clear an error — C9 missing Recommendation, C12 missing rationale, C25 Designing-without-justification all need user-authored text and go to QFix.
2. **Iteration cap = 3.** Matches `audit-q-fix.md` 3-pass cap. On cap, residual is on QFix and surfaced.
3. **Anchor-local.** Loop iterates only on findings under the cwd anchor's tree. Cross-anchor findings catalog as `QFix` sub-bullets on their owning anchor (audit-q routes by `surface_file` path).

### 6. (Top-level only) Hand off to `/triage`

**If sub-skill invocation: stop here.** The parent skill will surface state.

**If top-level invocation:**
- Invoke `/triage` (which regenerates the anchor's Q.md section per `[[SKA triage]]` § 6 and glances `~/ob/kmr/Q.md` per `[[SKA triage]]` § 7). This is the user's "what just happened?" view. (Step 5's Q.md regen is redundant when `/triage` follows immediately — `/triage` rewrites the same section. Either run idempotently produces the same result; keep both because sub-skill invocations don't fire step 6.)
- If the inline-deferred slot is filled (per § Step 3 inline-deferred slot rules), print the question on the line **after** /triage's output, pinning it to the bottom of the screen.

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
