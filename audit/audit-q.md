---
name: audit-q
description: >
  `~/ob/kmr/Q.md` constraint validator. Fixes by default (script-vs-skill split
  per F076 Q4): underlying Python script is read-only + `--fix` flag; this skill
  always passes `--fix`. Four checks: link existence (C1), Q-marker existence
  at target (C2), stale-`[Done]`-rows auto-moved to `## Done` (C4), Q.md
  per-anchor banner derivation (D1). Three-tier fix flow: mechanical (Python) →
  agent-inline-judgment (this skill, during run) → singleton `QFix [Ready]`
  backlog entry for the rare intractable cases. Auto-wired into the F075
  participating skills as a post-condition.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# audit-q — Q.md constraint validator (per F076)

Sub-action of `/audit`. Spec: `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]`.

## Runbook

1. **Invoke the Python script with `--fix`:**
   ```bash
   python3 ~/ob/kmr/SYS/Bespoke/Skill\ Agent/skills/audit/scripts/audit-q.py --fix
   ```
   (For preview without writing: append `--dry` instead of `--fix`.)

2. **Read the script's stdout.** It lists:
   - Mechanical fixes applied (C4 backlog moves, D1 banner rewrites).
   - Remaining findings the script couldn't fix mechanically — these become the agent's work.

3. **For each remaining finding, apply inline-judgment fix where safe** (this is the F076 Q5 three-tier flow's Tier 2 — most non-mechanical cases land here):
   - **Broken wiki-link with a near-match candidate** in the vault → rewrite the link to the corrected form.
   - **`[Questions]` bracket whose target has zero `Q<n>` markers** → either hoist informal Qs in the target row to numbered `Q1` / `Q2` form, OR rebracket the row to a state it actually satisfies (e.g., `[Designing]` if the row body has unanswered design questions but no enumerated Qs).
   - **Missing `^block-id` at a target row** → add the marker to the target.
   - **Stale link form** (e.g., `[[Old Name]]` after a rename, where the new name is clearly identifiable) → rewrite to the new form.

4. **Re-run the script** if any inline-judgment fixes were applied, to confirm the audit is clean.

5. **Every residual finding gets a sub-bullet on the singleton `QFix` row — no threshold, no "rare" gate.** The catalog IS the residual; an empty catalog is the only "clean." This is the strict invariant per F076 + the post-condition rule landed 2026-06-04: `/triage` and `/groom` exit honestly only when (a) zero residual or (b) every residual appears on `QFix`. Silent residual is a spec violation.

   For each unresolved finding (any C-code the Python script didn't auto-fix and that step 3 didn't safely rewrite), write/update the singleton `QFix [Ready]` backlog entry via `backlog-edit.py` (per [[SKA workflow]] § Mutation API). The row uses the B-slug form `B-QFix` as a stable singleton key — subsequent runs of `/audit q` with new unresolved findings re-write the **same row** (not a new F-number):

   ```bash
   ~/.claude/skills/workflow/scripts/backlog-edit.py {NAME} Ready B-QFix Ready \
       "QFix" "audit q findings needing user input or non-mechanical agent judgment — see sub-bullets"
   ```

   Renders as `- **B-QFix — QFix** [Ready] — audit q findings ... ^B-QFix`. The `^B-QFix` block-ID lets `/triage` and [[audit-q-fix]] target the row uniquely.

   Append each unresolved finding as a sub-bullet below the row via direct `Edit` (sub-bullet content is within-row, not a row-level mutation). Format per finding: `  - **C<N>** {file}:{line} — {short description from the audit output}`. **Cross-anchor findings (audit-q is vault-wide) catalog as sub-bullets too, but only for cwd anchor's `QFix` row** — each anchor's `QFix` carries only its own anchor's findings; cross-anchor findings live on the owning anchor's `QFix`. (Implementation: route findings by their `surface_file` path to the matching anchor's `QFix` row.)

   **Never write agent-guessed content into a user-facing feature doc to clear a residual.** Missing `Recommendation:` bullets (C9), missing `Naturally exercised by:` rationale (C12), `[Designing]`-without-justification (C25) all need user-authored prose — stub-to-clear is worse than the residual. These go to QFix; the user (or `/audit q-fix`) supplies the real text.

## When to use

- User says `/audit q`, `audit q`, "validate Q.md", "check Q", "audit the queue".
- **Auto-wired post-condition** — invoked by `/triage`, `/groom`, `/mint`, `/finalize`, `/feature` after state-touching writes (per F076 Q6 + F075 Q2). The participating skill calls `/audit q` after its Q.md update post-condition runs.

## Cross-references

- `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]` — design spec.
- `[[audit-q-fix]]` — companion skill for picking up a `QFix` backlog entry (rare).
- `skills/audit/scripts/audit-q.py` — the underlying Python script.
- `[[SKA audit]]` — parent audit skill family.
