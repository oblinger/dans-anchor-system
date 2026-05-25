---
name: audit-q-fix
description: >
  Pick up a singleton `QFix [Ready]` backlog entry (filed by an earlier `/audit q`
  run), work through its findings with agent judgment, then re-run `/audit q`
  until the QFix entry disappears (converged) or the findings stall (user input
  needed). ≤3 iteration cap. Rarely invoked because `/audit q` handles most
  non-mechanical cases inline.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# audit-q-fix — Pick up a QFix backlog entry and work through it (per F076 Q5)

Sub-action of `/audit`. Spec: `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]` § 4.5.

## When to use

- User invokes `/audit q-fix`.
- Rare — `/audit q` handles most non-mechanical cases inline during its own run; this skill is for the residue.

## Runbook

1. **Locate the QFix entry.** Walk up from `cwd` to find `.anchor`. Read `{NAME} Backlog.md`. Search for a row with identifier `QFix` (singleton; should be at top of `## Ready`).
   - If absent → exit. Print: `/audit q-fix — no QFix entry; nothing to do`.

2. **For each sub-bullet (finding) in the QFix entry**, apply a fix using agent judgment:
   - **Stale wiki-link** with near-match candidate → rewrite.
   - **`[Questions]` bracket / target Q-marker mismatch** → hoist or rebracket.
   - **Missing block-id at target** → add the marker.
   - **Finding genuinely needing user input** → hold for the next iteration's QFix entry (don't claim to fix).

3. **Re-run `/audit q`** to regenerate the QFix entry from the fresh state.

4. **Check the result:**
   - QFix entry gone → done; loop exits cleanly. Print summary.
   - QFix entry exists with **different** findings → progress made; loop back to step 1.
   - QFix entry exists with the **same** findings as previous iteration → stalled. Exit with "user input needed" report listing what couldn't be auto-fixed.

5. **Termination cap: ≤3 iterations.** Even if findings change each iteration, exit after 3 passes to prevent runaway loops. Surface the remaining QFix as a normal `[Ready]` backlog item for user attention.

## Cross-references

- `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]` § 4.5 — design.
- `[[audit-q]]` — the audit this skill loops back to.
- `skills/audit/scripts/audit-q.py` — the underlying validator.
