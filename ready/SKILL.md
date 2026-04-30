---
name: ready
description: >
  Walk the current anchor's backlog (or roadmap, or named section) and promote
  every item it can to Ready — the rest get parked in feature docs with their
  open questions. Never interrupts the user mid-run. Ends with the first
  blocked-on-questions doc opened for the user, then a roster, then optionally
  one final trivial inline question. Use when the user says "make ready",
  "ready up the backlog", "/ready", "ready everything", "promote the upcoming items".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Ready — Batch Backlog Readiness

Walk the current anchor's backlog and try to make as many items as possible **Ready**. An item is Ready when *you believe you know how to do this task without further involvement of the user*. Items that don't clear that bar get a feature doc with the questions captured; the user resolves the questions on their own time.

DMUX trigger: **`make ready`** (two words). Slash invocation: `/ready`.


## When to Use

- User says `make ready`, `/ready`, `ready up the backlog`, or asks for the backlog to be promoted.
- After the user has answered questions in a feature doc and wants the next round of items processed.
- Whenever the backlog has accumulated enough Upcoming items that hand-promotion is too slow.


## Definition of Ready

> **An item is Ready when you believe you know how to do this task without further involvement of the user.**

Sharper than "design questions resolved." If the task still hides any "wait, what about X?" that the user would have to answer, it's **not** Ready — it's blocked on questions, and `/ready` should park those questions in a feature doc rather than promote the bullet.

(Authoritative wording lives in [[CAB Backlog]] § Definition of Ready.)


## Item Status — How to Read It

Every backlog item has one of these statuses, derived from where the bullet sits and what it links to:

| Status | How to recognize | What `/ready` does |
| --- | --- | --- |
| **Ready** | Bullet is under `## Ready` H2 | Skip — already ready. |
| **In Progress** | Bullet is under `## In Progress` H2 | Skip — actively being worked. |
| **Blocked on questions** | Bullet text contains a `→ [[Feature Doc]]` or `→ [[Open Questions]]` link | Skip — only the user can resolve those. |
| **Unset / Upcoming** | Bullet is under `## Upcoming`, `## Legwork`, or any other non-terminal section, AND has no link to active open questions | **Process** — try to ready it. |
| **Testing**, **Completed** | Bullet under those H2s | Skip — out of scope. |

The `→ [[X]]` link convention is documented in [[CAB Backlog]].


## Invocation

| Invocation | Scope |
| --- | --- |
| `/ready` | All Unset / Upcoming items across the whole backlog. Default. |
| `/ready upcoming` | Only items under `## Upcoming`. |
| `/ready legwork` | Only items under `## Legwork`. |
| `/ready roadmap` | Operate on the roadmap's next milestone instead of the backlog. |
| `/ready roadmap <milestone>` | Operate on a named roadmap milestone. |
| `/ready <Q-number>` | Single item, by Q-number. |
| `/ready <item name>` | Single item, by name match. |


## Runbook

### 1. Locate the source

- Walk up from `cwd` to find `.anchor`. If none, say so and stop.
- For backlog modes: read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`.
- For roadmap mode: read `{NAME} Docs/{NAME} Plan/{NAME} Roadmap.md`.
- If the source file is missing, report and stop.

### 2. Enumerate candidates

Walk every bullet in scope. For each bullet, derive its status (per § Item Status). Filter to status **Unset / Upcoming**.

If scope was provided as an argument, narrow to bullets in that section only.

### 3. For each candidate, in source order

**Investigate quietly.** Read related docs, infer answers from context, draft a spec, run lightweight planning. You may quietly invoke any of: research, plan, architect, spec, replan, open-questions discipline. Do not prompt the user for anything during investigation.

**Decide:**

- **Bullet is Ready as-is** — the description (plus any inference from related docs) tells you how to do the task without further user involvement. Move the bullet to `## Ready`, preserving its Q-number and text. Done with this item.

- **Has questions** — anything you'd need the user to clarify. Two sub-paths:

  1. **Inline-deferred slot is empty AND this is exactly ONE genuinely trivial question** (one short sentence, one yes/no, one short answer): hold it in the inline-deferred slot. Mark the item for revisit when the user answers — for now, leave the bullet where it is.
  2. **Otherwise** — create a dated feature doc at `{NAME} Docs/{NAME} Plan/{NAME} Features/YYYY-MM-DD <Item Name>.md` with the standard `## Open Questions` block above the H1 (per `/feature` § 1). Capture the questions there. **This is parking mode** (per [[open-questions]] § Active vs Parking) — do NOT glance the new feature doc. The user invoked `/ready` as a *batch* operation specifically to defer per-item engagement; glancing each created doc would interrupt the very deferral they asked for. Replace the backlog bullet's description with `→ [[YYYY-MM-DD <Item Name>]]` (preserve the Q-number and bullet name). The item is now blocked-on-questions; the doc surfaces only at end-of-run via § 5 (the *first* one, not all).

**Inline-deferred slot rules.**
- At most ONE item across the whole run may use the inline slot.
- The question must be genuinely short — one sentence, fits on one line.
- If a second item would qualify, it goes to a feature doc instead.
- The slot is *only* surfaced at the very end of the run, after the roster (see § 7).

### 4. Build the report

Print a summary table:

```markdown
## /ready — <anchor>

| Outcome | Count | Items |
| --- | --- | --- |
| Promoted to Ready | N | Q3, Q7, … |
| Promoted to feature doc | N | Q5 → 2026-04-29 X, Q12 → 2026-04-29 Y |
| Deferred inline | 0 or 1 | Q9 |
| Skipped | N | <reasons summarized> |
```

### 5. Open the first blocked-on-questions doc

Find the **first newly-created** feature doc (in source order through the backlog). If none were created this run, fall back to the **first pre-existing** blocked-on-questions doc encountered. Open it:

```bash
open "<path to that feature doc>"
```

This gives the user one concrete next action: answer those questions. If there are no blocked items at all (e.g. everything readied cleanly), skip this step.

### 6. Run roster

Invoke `/roster` to print the post-`/ready` state of the backlog (counts of In Progress / Ready / Backlog / Icebox, plus the bullets above the count line).

### 7. Ask the deferred inline question (if any)

If the inline-deferred slot is filled, print the question now — on the line **after** the roster. This pins it to the bottom of the screen so it survives scrolling.

If the slot is empty, say nothing further; the run is done.


## Design Principle — Minimize User Back-and-Forth

`/ready` follows a workflow principle that applies to all batch operations against the backlog:

> **Process the entire batch autonomously before involving the user.** Never interrupt mid-run to ask. Route every emerging question to its feature doc's `## Open Questions` block, then surface the first blocked doc at the end as the user's single next action. Each round-trip with the user costs scrollback context and stalls the batch — design every workflow to require *one* round-trip per pass, not N.

(Authoritative statement lives in [[CAB Backlog]] § Design Principle — Minimize User Back-and-Forth.)


## Idempotence

`/ready` is safe to run repeatedly. Items already in `## Ready`, `## In Progress`, `## Testing`, `## Completed`, `## Legwork`, or marked blocked-on-questions are skipped. Running twice in a row should produce no diff on the second pass if no new info has come in.


## Failure Modes

- **No anchor found** — say "No anchor found from `<cwd>` upward." and stop.
- **No backlog file (or roadmap file, in roadmap mode)** — say "No `<expected file>` at `<expected path>`." and stop.
- **Empty section** — print a one-line "Nothing to process in <scope>" and call `/roster` so the user still sees state.
