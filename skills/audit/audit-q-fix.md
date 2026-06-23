---
name: audit-q-fix
description: >
  Two modes. `/audit q-fix` (in an anchor): pick up the local `B-QFix [Ready]`
  row and drive its sub-bullets to zero under the 100%-fix discipline. `/audit
  q-fix all` (anywhere): broadcast routing — run vault-wide audit + auto-fix +
  routing so every anchor with outstanding warnings has an up-to-date `B-QFix`
  row on its backlog. Does NOT edit other anchors' feature docs (no
  cross-anchor agent-judgment edits); each owning Pilot drives their own row
  to zero on the next `/crank` or `/triage`.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# audit-q-fix — Address audit residuals (per F076 Q5)

Sub-action of `/audit`. Two modes distinguished by argument:

| Invocation | What it does |
|---|---|
| `/audit q-fix` (no args, inside an anchor) | Pick up THIS anchor's `B-QFix [Ready]` row and drive its sub-bullets to zero with agent judgment. The single-anchor mode. |
| `/audit q-fix all` | Broadcast routing — run vault-wide `audit-q.py --fix` so every anchor with outstanding warnings gets a current `B-QFix [Ready]` row on its backlog. Does NOT do the cross-anchor sub-bullet-driving; that's each owning Pilot's job on their own `/crank` or `/triage`. The vault-wide setup mode. |

Spec: `[[F009 — audit q — Q.md constraint validator]]` § 4.5.

## When to use

- `/audit q-fix` — user invokes inside an anchor that has a `B-QFix` row to clear. Common after a `/audit q-fix all` broadcast routes findings; rare otherwise because `/audit q` handles most non-mechanical cases inline.
- `/audit q-fix all` — user wants to refresh every anchor's `B-QFix` row from a current vault-wide audit. Typical flow: glance Q.md, see trailing `{N}` counts on several anchors, invoke `/audit q-fix all` to ensure routing is current, then `/crank` each anchor in turn to address its sub-bullets.

## Runbook — single anchor (`/audit q-fix`)

1. **Locate the QFix entry.** Walk up from `cwd` to find `.anchor`. Read `{NAME} Backlog.md`. Search for a row with identifier `B-QFix` (singleton; should be at top of `## Ready`).
   - If absent → exit. Print: `/audit q-fix — no B-QFix entry; nothing to do`.

2. **For each sub-bullet (finding) in the B-QFix entry**, apply a fix using agent judgment per the 100%-fix discipline (see `[[audit-q]]` § 5 for the per-C-code action map):
   - **C9 missing Recommendation** → write one; `**Recommendation:** None — <one-line reason>` after honest effort is acceptable.
   - **C12 missing `Naturally exercised by:` rationale** → write the plausible-exercise sentence, or rebracket if no exercise can be named.
   - **C22 broken link** → near-match rewrite OR remove OR add the marker at the target.
   - **C25 missing `[Designing]` next-action** → write the next-action OR rebracket to `[Questions]` / `[Ready]`.
   - **Finding genuinely needing user-private input** → leave on the row for the next pass.

3. **Re-run `/audit q`** (the local skill — fixes by default) to regenerate `B-QFix` from the fresh state.

4. **Check the result:**
   - `B-QFix` gone → done; loop exits cleanly. Print summary.
   - `B-QFix` exists with **different** findings → progress made; loop back to step 1.
   - `B-QFix` exists with the **same** findings as previous iteration → stalled. Exit with "user input needed" report listing what couldn't be auto-fixed.

5. **Termination cap: ≤3 iterations.** Even if findings change each iteration, exit after 3 passes to prevent runaway loops. Surface the remaining `B-QFix` as a normal `[Ready]` backlog item for user attention.

## Runbook — vault-wide (`/audit q-fix all`)

The broadcast-routing mode. Does NOT drive any anchor's sub-bullets to zero — that's each owning Pilot's job. This mode ensures every anchor with outstanding warnings has a current `B-QFix` row pinned at the top of `## Ready` (and the Q.md banner trailing `{N}` reflects the current count) so the user can see at a glance which anchors need a `/crank`.

1. **Run vault-wide audit + fix + routing.**
   ```bash
   ~/.claude/skills/audit/scripts/audit-q.py --fix
   ```
   The script applies its mechanical auto-fixes (bracket rewrites, H2 moves, stale-Done migration, block-ID appends) AND routes every non-mechanically-fixable residual to its owning anchor's `B-QFix` row (via `route_findings_to_qfix`). The agent doing the invocation does NOT write Recommendations or rebrackets in other anchors' feature docs — only the per-anchor `B-QFix` rows get edited (and the script's own mechanical fixes).

2. **Print per-anchor summary.** Read the script's stdout, surface to the user:
   ```
   /audit q-fix all — vault-wide routing complete:
     A2X:     B-QFix has 1 sub-bullet(s)  → /crank A2X to address
     ATL:     B-QFix has 2 sub-bullet(s)  → /crank ATL
     DKT:     B-QFix has 10 sub-bullet(s) → /crank DKT
     DMUX:    B-QFix has 1 sub-bullet(s)  → /crank DMUX
     HA:      B-QFix has 5 sub-bullet(s)  → /crank HA
     LRN TPM: B-QFix has 6 sub-bullet(s)  → /crank LRN TPM
     MUX:     B-QFix has 2 sub-bullet(s)  → /crank MUX
     SYS:     B-QFix has 1 sub-bullet(s)  → /crank SYS
   ```
   The `{N}` trailing counts on Q.md banners also reflect this state.

3. **Stop.** This skill does NOT drive sub-bullets to zero in this mode. The owning Pilot's next `/crank`, `/triage`, or local `/audit q-fix` handles that. The audit-fixes-everything-itself anti-pattern is the principle violation this mode is designed to avoid (per user direction 2026-06-04 — auditing agent does NOT do agent-judgment edits in other anchors' feature docs).

## Cross-references

- `[[F009 — audit q — Q.md constraint validator]]` § 4.5 — design.
- `[[audit-q]]` — the audit this skill loops back to.
- `[[audit]]` § Governing principle — the 100%-fix discipline.
- `skills/audit/scripts/audit-q.py` — the underlying validator + router.
