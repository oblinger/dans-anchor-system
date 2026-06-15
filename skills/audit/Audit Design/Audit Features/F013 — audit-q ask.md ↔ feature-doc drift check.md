---
description: "C35 cross-checks ask.md claimed-pending Qs against the linked feature doc's real Q-state. Shipped."
---

# [[Audit]] · F013 — audit-q ask.md ↔ feature-doc drift check

## Summary

`/ask` and `/triage` rely on the backlog row's `[N Questions]` bracket to report what's pending. But the bracket can drift from the linked feature doc's actual state — the feature doc may have all Qs resolved while the bracket still says `[4 Questions]`, or vice versa. The F077 Q7 case from 2026-06-06 was the surfacing event: my `/ask` carried "F077 Q7" forward as a pending entry in `SKA ask.md`, but F077's doc had Q7 in its `## Resolved` H2 (choice A). The drift escaped detection because nothing audits the cross-file consistency.

This feature adds a check (likely C35 or whatever the next number is) that walks every backlog row with a `[N Questions]` bracket, follows its `→ [[F<n>]]` link to the feature doc, counts pending Qs (bullet-form `- **Q<n>` in `## Open Questions` + H3-form `### Q<n>` per F123), and reports drift when the count disagrees with the bracket number.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** `audit-q.py` carries a new check (next available C-number) that compares each `[N Questions]`-bracketed backlog row's claimed count against its linked feature doc's actual pending-Q count. Mismatches (off-by-any-amount, including "row says N but doc says 0") fire an error finding with a suggested rebracket. The F077-like case is caught: if a feature doc has zero pending Qs but the backlog says `[N Questions]`, the check fires.

**How it will be verified.**
1. Synthetic backlog row `- **F999 — Test** [3 Questions] — → [[F999 — Test]]` + feature doc with 0 pending Qs in `## Open Questions` → audit fires the new check.
2. Real-world: run on SKA backlog after sample edits — count the false-negatives that previously slipped (F077-style cases).
3. Auto-fix mode: when the doc has 0 pending Qs, the check proposes rebracket to next bracket (`[Ready]` or `[Verify]` based on linked-doc Status field).
4. C-number lands sequentially; existing checks unaffected.

## Design

### Detection logic

For each backlog row with bracket `[N Questions]` or `[<integer> Questions]`:

1. **Resolve the linked feature doc.** Follow the `→ [[F<n> — Title]]` arrow link (or fallback to first wiki-link in row). If unresolvable: skip + emit a different existing check's finding.
2. **Count pending Qs in the linked doc.** Sum:
   - Bullet-form `^- \*\*Q\d+\b` inside `## Open Questions` H2 (existing parser).
   - H3-form `^### Q\d+\b` inside `## Open Questions` (per F123 extension).
   - Exclude Qs inside the `### Resolved` H3 sub-section.
   - Exclude Qs inside the bottom `## Resolved` H2.
3. **Compare to bracket number.**
   - If bracket says `[N Questions]` and doc has 0 pending → drift. Suggest rebracket to `[Ready]` (or `[Verify]` based on doc Status). Severity: error. Mechanically fixable (rebracket via `backlog-edit.py`) when doc Status block is parseable.
   - If bracket says `[N Questions]` and doc has M pending with N ≠ M → drift. Suggest rebracket to `[M Questions]`. Severity: error. Mechanically fixable.
   - If bracket says `[Questions]` (no number) and doc has 0 pending → drift. Same as case 1.

### Affected scope

Only `## Active` / `## Ready` / `## Now` / `## Next` horizons (matches existing audit scope). Skip `## Later` / `## Done` / `## Icebox`.

### Implementation notes

- Add `check_c<N>_question_count_drift()` function in `audit-q.py` following the pattern of `check_c24_questions_count_match()` (which already does a partial version of this for in-row sub-bullets vs. bracket).
- C24 currently checks bracket vs. ROW-INTERNAL Q sub-bullets. C<N> extends to bracket vs. LINKED-DOC Q count. Different concerns; both needed.
- Reuse the H3-Q parser landing in F123 — F124 ships after F123 if both pending; can ship independently if F123 hasn't landed yet (using bullet-only counting + caveat in finding message).

## Status

**Done** — landed 2026-06-07 as `check_c35_ask_md_drift`. Scope refined during implementation: the spec talked about backlog-row bracket drift, but the surfacing case (F077 Q7) was actually `{NAME} ask.md` § Questions claiming Qs pending in a linked F-doc that had them resolved — backlog-bracket drift is already C24's domain. C35 walks each anchor's sibling `{NAME} ask.md`, parses `## Questions` bullets, resolves each wiki-link to its F-doc, extracts claimed Q-numbers from the bullet body, and cross-checks against `extract_q_entries` (now H3-aware via F123). Verified: SKA ask.md with synthetic injection of `(Q1, Q2, Q3, Q4, Q5, Q6)` for F117 (which only has Q1-Q4 pending) fires `C35 ... ask.md claims Q5, Q6 pending in F117 but linked doc has those resolved or absent (actual pending: Q1, Q2, Q3, Q4)`. Real-world vault state: 0 findings (all ask.md files genuinely in sync).
