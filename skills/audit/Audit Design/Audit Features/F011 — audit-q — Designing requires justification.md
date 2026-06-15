---
description: "Present-time invariant: [Designing] rows must carry a next-action justification (C25). Shipped."
---

# [[Audit]] · F011 — audit-q — Designing requires justification

## Summary

User observed 2026-06-02 that HA's `### BUG — Description writer ...` row was bracketed `[Designing]` in `## Now`, but the row had no status justification anywhere. F102 explicitly says: any row marked `[Designing]` must carry a justification including a next-action line. The current enforcement runs only when `backlog-edit.py` transitions a row through `verify_status_block` — hand-edited rows and H3-style rows in HA-flavored backlogs escape.

The contract the user wanted is universal: **at every audit-q pass, every backlog row whose bracket is `[Designing]` is checked for justification, and reported as a finding if it lacks one**. That's the fix — move enforcement from "edit-time guard" to "present-time invariant."

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** An audit-q rule (new code, e.g. C25) scans every live row in every backlog reachable from Q.md. For each row bracketed `[Designing]`:
- **Bullet row with a `→ [[F<n>]]` link:** read the feature doc's `## Status` H2. Must contain `**Designing**` and a next-action line. If missing → finding.
- **Bullet row with no feature link:** must have inline justification on the row itself (a sub-bullet starting `- **Status:** Designing — <next-action>`). If missing → finding.
- **H3 row (HA-style):** the row body has no separate feature doc; must have a sub-bullet `- **Status:** Designing — <next-action>` under the H3. If missing → finding.

Running `audit-q --fix` on HA's backlog after F106 lands surfaces the BUG row as a finding (no inline status sub-bullet), and the user sees it in the standard audit output. After they (or the agent) add the justification, the finding clears.

**How it will be verified.** Tier 1 / agent-immediate. After F106 lands:
- (a) Run `audit-q --fix` on HA's backlog; confirm the BUG row surfaces as a C25 finding.
- (b) Add an inline `- **Status:** Designing — <next-action>` sub-bullet to the BUG row; re-run audit-q; confirm the finding clears.
- (c) Vault-wide pass; confirm no spurious findings on rows that legitimately have justifications.

## Design

### The new rule — C25 (Designing requires justification)

In `audit-q.py` § Rules, after the existing F102-related checks, add `check_c25_designing_justification(entries, vault_index)`:

1. For each `BacklogEntry` in the live set whose `status` is `Designing`:
   - **Case A — entry has a resolvable link (`entry.link.target_resolves`):** read the linked feature doc. Look for a `## Status` H2 whose first non-blank line starts with `**Designing**` (bolded leading token per F102) and whose body contains a "next action" / "next step" line (case-insensitive match for `next action` or `next step`).
     - All conditions met → no finding.
     - `## Status` missing OR leading token wrong OR no next-action line → finding.
   - **Case B — entry has no resolvable link (B-row inline, H3 row):** look for an inline justification under the row. For bullet rows, the next-line sub-bullet starting with `- **Status:** Designing —` (any indent ≥ 2 spaces); for H3 rows, the same sub-bullet form anywhere between the H3 line and the next H3 / H2. The sub-bullet text after the em-dash must contain `next` (case-insensitive, "next action" / "next step" / "next move").
     - Inline sub-bullet present with next-action → no finding.
     - Missing → finding.

Severity: **error** (not warning) — per user's "must, must, must" framing.

Message: `Row [Designing] has no status justification. Per F102: must carry **Designing** + next-action line (in linked doc's ## Status H2, or inline sub-bullet on/below the row).`

No auto-fix — this is a content gap; the agent or user must write the justification.

### Where the rule runs

Per audit-q's `--scope q` / `--scope backlog` / `--scope all` dispatch, C25 fires whenever the relevant backlog is in scope:

- `--scope q` (default) — fires on every anchor backlog reachable from Q.md.
- `--scope backlog --anchor X` — fires on anchor X's backlog only.
- `--scope all` — fires vault-wide.

The `backlog-edit.py verify_status_block` enforcement stays as the **transition-time guard** (per F102 original spec). C25 is the **invariant-time enforcement** that catches rows that bypassed the guard.

### What the rule does NOT do

- **Does not check non-Designing brackets.** F102 says only Designing requires a next-action; the other statuses (Active / Ready / Verify / Done) have looser justification requirements. Only Designing fires C25.
- **Does not run on Done / Icebox rows.** Only live horizons (Active / Ready / Now / Next / Later / Verify).
- **Does not require a specific format for "next action."** The audit just looks for the case-insensitive token "next" near where the status sub-bullet's body sits. Stricter format would catch real misses but also generate false positives; keep loose for v1.

## Status

**Done** — C25 added to `audit-q.py`; HA BUG row surfaces as a C25 finding.

### Verification (Tier 1 / agent-immediate)

- (a) Ran `audit-q --fix` on HA's backlog after F106 landed → BUG row surfaces as C25 finding with the expected message. ✅
- (b) Will be re-verified when the BUG row's justification is added (separate task).
- (c) Vault-wide pass with `audit-q --fix` → no spurious C25 findings on legitimate rows.

## Resolved

### Why an audit-q rule rather than tightening backlog-edit.py
**Choice:** Add a present-time audit rule (C25); leave the backlog-edit.py transition guard as-is.

The backlog-edit.py guard is necessary but not sufficient — it only fires when rows transition through the script. Hand-edited rows, H3 rows in HA-flavored backlogs, and any row created outside the script entirely escape the guard. The user's contract ("must, must, must") is universal, so the enforcement must be present-time, not transition-time. audit-q is the natural place for present-time invariants — it's already the script that fires on every backlog touch via the F104 D1 mechanism.

### Why H3 rows get inline-sub-bullet treatment
**Choice:** H3 rows must have a sub-bullet `- **Status:** Designing — <next-action>` since they have no separate feature doc.

HA-style H3 rows don't get feature docs by default — the row body lives inline as paragraph text + sub-bullets. The ## Status H2 contract doesn't apply structurally. Requiring an inline status sub-bullet is the row-level equivalent.
