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

5. **For findings genuinely too ambiguous to fix safely** (the rare Tier 3 case) → write/update the singleton `QFix [Ready]` backlog entry at the top of `## Ready` in the cwd anchor's backlog. Include each unresolved finding as a sub-bullet. The user (or `/audit q-fix`) picks it up later.

## When to use

- User says `/audit q`, `audit q`, "validate Q.md", "check Q", "audit the queue".
- **Auto-wired post-condition** — invoked by `/triage`, `/groom`, `/mint`, `/finalize`, `/feature` after state-touching writes (per F076 Q6 + F075 Q2). The participating skill calls `/audit q` after its Q.md update post-condition runs.

## Cross-references

- `[[F076 — audit q — Q.md constraint validator with mechanical-fix mode]]` — design spec.
- `[[audit-q-fix]]` — companion skill for picking up a `QFix` backlog entry (rare).
- `skills/audit/scripts/audit-q.py` — the underlying Python script.
- `[[audit]]` — parent audit skill family.
