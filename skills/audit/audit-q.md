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

5. **100% of warnings must go to zero on every audit pass.** No "user input needed" carve-out, no QFix catalogue of unfixable residuals. The discipline (per user direction 2026-06-04, replacing the prior "mechanical-only never agent-guessed" rule): **every C-code on the audit's surface has an agent-side fix path; the agent's job is to take it.**

   For each remaining finding (any C-code the Python script didn't auto-fix and that step 3 didn't safely rewrite), pick the matching action below — do not file QFix entries for things the agent CAN address:

   - **C9 missing Recommendation** — write one. The Recommendation is the *agent's* field, not the user's. Read the linked Design section, conversation history, prior similar decisions, memory, the user's stated preferences. Form a **Strong** / **Lean** when there's a clear answer. If honest effort produces no basis for even a Lean, write `**Recommendation:** None — <one-line reason naming what specifically the agent doesn't know>`. **`None` is a real answer** — it's the agent declaring, after work, that this decision belongs to the user. Empty Recommendation = agent didn't try.
   - **C12 missing `Naturally exercised by:` rationale** — write the plausible-exercise sentence based on what the row is verifying (e.g., "next anchor that adopts a `markdown-write` trigger"). If genuinely no natural exercise exists, the row probably shouldn't be `[Verify-by]` in the first place — rebracket to `[Verify]` or `[Watching N d]` as honest.
   - **C25 `[Designing]` w/o justification** — write the next-action sentence (either as `## Status` H2 in the linked feature doc, or as inline `- **Status:** Designing — <next-action>` sub-bullet under the backlog row). If no honest next-action exists, the row isn't really `[Designing]` — rebracket to `[Questions]` (if questions need to be drafted) or `[Ready]` (if design is complete).
   - **C19, C20, C21, C22, C7, C8** — agent reformat / link rewrite / Phase-2 migration. All structural, all agent-doable.
   - **Genuinely-stuck-on-user cases — RARE.** Reserve `QFix` for cases where the agent has tried and the answer truly requires user-specific knowledge (e.g., user-private preferences, external facts the agent can't reach). These should be rare; most C-codes have an honest agent action. File via `state task update` (B-QFix is a named singleton — update creates it if absent, mirroring `backlog-edit.py`'s semantics for named row-ids):

     ```bash
     ~/.claude/skills/workflow/scripts/state --anchor {NAME} task update B-QFix --horizon Ready --status Ready \
         --title "QFix" --body "audit q findings genuinely requiring user-private input — see sub-bullets"
     ```

     Renders as `- **B-QFix — QFix** [Ready] — audit q findings ... ^B-QFix`. The `^B-QFix` block-ID lets `/triage` and [[audit-q-fix]] target the row uniquely. Each finding goes as `  - **C<N>** {file}:{line} — {description + one line on why the agent can't supply the answer alone}`. Cross-anchor findings route by `surface_file` path to the matching anchor's `QFix` row.

   **The cultural rule:** agents are lazy by default — given any escape hatch, they leave warnings open. The 100%-go-away rule closes the hatch: every warning is somebody's work, and the auditing agent is the somebody. `None` is acceptable but only after honest effort; the empty bullet is not. **If you find yourself reaching for QFix on C9 / C12 / C25 because "the user needs to decide" — stop. Try harder. Write `None — <specific reason>` rather than skip.**

## When to use

- User says `/audit q`, `audit q`, "validate Q.md", "check Q", "audit the queue".
- **Auto-wired post-condition** — invoked by `/triage`, `/groom`, `/mint`, `/finalize`, `/feature` after state-touching writes (per F076 Q6 + F075 Q2). The participating skill calls `/audit q` after its Q.md update post-condition runs.

## Cross-references

- `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]` — design spec.
- `[[audit-q-fix]]` — companion skill for picking up a `QFix` backlog entry (rare).
- `skills/audit/scripts/audit-q.py` — the underlying Python script.
- `[[SKA audit]]` — parent audit skill family.
