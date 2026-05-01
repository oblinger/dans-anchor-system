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
| **Blocked on questions** | Bullet text contains a `→ [[Feature Doc]]` or `→ [[Open Questions]]` link | Skip — only the user can resolve those. |
| **Unset / Upcoming** | Bullet is under a horizon H2 (`## Now`, `## Next`, `## Later` per [[backlog-horizons]]) — or the legacy `## Upcoming` — or `## Legwork`, with bracket `[ ]` / `[Designing]` / absent, AND has no link to active open questions | **Process** — try to ready it. |
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
| `/groom icebox` | Walk `{NAME} Icebox.md` instead of the backlog. Useful for thawing iced items back into the backlog or reviewing what's parked. Default scope (bare `/groom`) excludes the icebox per `[[workflow]]` § Active-work invariant. |
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

### 3. For each candidate, in source order

**Investigate quietly.** Read related docs, infer answers from context, draft a spec, run lightweight planning. You may quietly invoke any of: research, plan, architect, spec, replan, ask-questions discipline. Do not prompt the user for anything during investigation.

**Decide:**

- **Bullet is Ready as-is** — the description (plus any inference from related docs) tells you how to do the task without further user involvement. Move the bullet to `## Ready`, preserving its F-number and text. Done with this item.

- **Has questions** — anything you'd need the user to clarify. Two sub-paths:

  1. **Inline-deferred slot is empty AND this is exactly ONE genuinely trivial question** (one short sentence, one yes/no, one short answer): hold it in the inline-deferred slot. Mark the item for revisit when the user answers — for now, leave the bullet where it is.
  2. **Otherwise** — create a feature doc at `{NAME} Docs/{NAME} Plan/{NAME} Features/F{n} — {Item Name}.md` (using the backlog row's F-number; per [[CAB Backlog]] § Numbering policy) with the standard `## Open Questions` block below the H1 (per `/feature` § 1 and [[ask-questions]] § When a file is involved). Capture the questions there. **This is parking mode** (per [[ask-questions]] § Active vs Parking) — do NOT glance the new feature doc. The user invoked `/groom` as a *batch* operation specifically to defer per-item engagement; glancing each created doc would interrupt the very deferral they asked for. Replace the backlog bullet's description with `→ [[F{n} — {Item Name}]]` and update the bracket to `[Questions]`. The item is now blocked-on-questions; the doc surfaces only at end-of-run via § 5 (the *first* one, not all).

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
| Promoted to feature doc | N | F5 → [[F5 — X]], F12 → [[F12 — Y]] |
| Deferred inline | 0 or 1 | F9 |
| Skipped | N | {reasons summarized} |
```

### 5. Open the first blocked-on-questions doc

Find the **first newly-created** feature doc (in source order through the backlog). If none were created this run, fall back to the **first pre-existing** blocked-on-questions doc encountered. Open it:

```bash
open "{path to that feature doc}"
```

This gives the user one concrete next action: answer those questions. If there are no blocked items at all (e.g. everything readied cleanly), skip this step.

### 6. Run roster

Invoke `/roster` to print the post-`/groom` state of the backlog (counts of Active / Ready / Backlog / Icebox, plus the bullets above the count line).

### 7. Ask the deferred inline question (if any)

If the inline-deferred slot is filled, print the question now — on the line **after** the roster. This pins it to the bottom of the screen so it survives scrolling.

If the slot is empty, say nothing further; the run is done.


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
