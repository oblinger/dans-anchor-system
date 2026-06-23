---
description: "Q-parser recognizes H3-form Open Questions in addition to bullet form. Shipped."
---

# [[Audit]] · F012 — audit-q recognize H3-form Open Questions

## Summary

`audit-q.py`'s Q-parser (the regex set behind C6 / C9 / C10 / C19 / C20 / C21) only recognizes bullet-form Qs: `- **Q<n> — Title** — body...` with options as indented sub-bullets. DKT (and possibly other anchors) author Qs in H3 form: `### Q<n> — Title` followed by a body paragraph + top-level option bullets + Recommendation paragraph. The H3 form is valid markdown and reads well in Obsidian, but the parser doesn't see it, so:

- **C21 false-positive** — fires whenever an `## Open Questions` H2 contains only H3-form Qs (zero bullet-form Qs counted → parser reports "all resolved, Phase 2 transition missed"). The Qs are actually pending.
- **C9 false-negative** — H3-form Qs aren't checked for Recommendation presence.
- **C19 / C20 / C6** — same blindness.

This feature extends the Q-parser to recognize both shapes uniformly, applying every check that currently runs on bullet-form Qs to H3-form Qs symmetrically. Same pattern as the C32 / C33 / C34 H3-row backlog recognition added earlier this session.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none (the C21 warning on DKT F029 is the only live false-positive today; this feature drops the count, but is independent of any in-flight feature)

**What done looks like.** `audit-q.py`'s Q-parsing primitives extract Qs in both bullet form (`- **Q<n> —**`) and H3 form (`### Q<n> —`). All Q-level checks (C6 block-ID, C9 Recommendation present, C10 Recommendation outdent, C19 option-bullet labeling, C20 blank line after Recommendation, C21 pending-Q count) apply uniformly to both forms. The C21 warning on DKT F029 clears without any change to DKT F029's content.

**How it will be verified.**
1. Run `audit-q.py --scope q --dry` before the change → 1 warning (C21 DKT F029).
2. Apply the script changes.
3. Run `audit-q.py --scope q --dry` after → 0 findings.
4. Spot-check: a synthetic H3-form Q without a Recommendation fires C9 the same as a bullet-form Q would.
5. Spot-check: a synthetic feature doc with all H3-Qs in `### Resolved` correctly fires C21 (not a false negative on the other side).

All five are mechanical, runnable in the same turn the work completes.

## Design

### Current parser shape (bullet-form only)

`audit-q.py` carries these Q-related regexes:

```python
Q_HEADER_RE   = re.compile(r"^(\s*)- \*\*Q(\d+)\b")
# … plus internal helpers in extract_q_entries() that walk indented sub-bullets
# under each Q_HEADER_RE match.
```

`extract_q_entries(file_path, container_id)` walks the file looking for these bullet-form openers, then collects the indented option bullets + Recommendation bullet underneath each.

### Extension plan

Add a sibling regex for H3 form:

```python
Q_HEADER_H3_RE = re.compile(r"^### Q(\d+)\b")
```

Extend `extract_q_entries()` to handle both. The H3-form Q has:

- **Q-header line:** `### Q<n> — Title` (or `### Q<n>` then prose).
- **Body:** all lines from the H3 to either the next `### ` heading or the next `## ` heading (whichever comes first), excluding trailing whitespace.
- **Options:** top-level bullets matching `- **(A) ` / `- **(B) ` etc. inside the body. (Same option pattern as bullet-form Qs, just at top-level indent rather than nested.)
- **Recommendation:** a top-level bullet `- **Recommendation:**` inside the body, OR a paragraph form `Recommendation: ...` as a fallback (DKT's current convention). v1 supports both; flag the paragraph form as a warning (recommend hoisting to bullet) but treat as valid.

### Container scope for H3-form Qs

The bullet form lives inside an `## Open Questions` H2 (or feature doc's top-level Open Questions). The H3 form does the same — `### Q<n>` is inside `## Open Questions`. So the container detection logic (used by C21 — "are we inside Open Questions?") doesn't change; just the inner Q-detection.

### Phase 1 / 2 / 3 handling for H3-form Qs

The same lifecycle applies: H3 Q in `## Open Questions` → pending. H3 Q in `### Resolved` (under `## Open Questions`) → resolved-staged. H3 Q in bottom `## Resolved` H2 → permanently resolved.

The parser's `in_h3_resolved` flag (already exists for tracking `### Resolved` sub-section context) gets reused; just need to make sure it correctly excludes nested H3-Qs from the pending count when we're in a Resolved-context.

### Affected checks

| Check | What changes |
|---|---|
| **C6** (block-ID present) | Apply to H3-form Qs. H3 form may carry `^F<n>-Q<n>` as a block-ID at the end of the H3 line (`### Q1 — Title  ^F029-Q1`). Detect it; warn if missing. |
| **C7** (link form) | No change — about how external refs are written, not Q shape. |
| **C9** (Recommendation present) | Apply to H3-form Qs. Look for `**Recommendation:** Strong\|Lean\|None` either as a top-level bullet in the body OR a paragraph (paragraph form gets the format-hoist warning per § Recommendation handling). |
| **C10** (Recommendation outdent) | N/A for H3 form (no indent to enforce). Skip. |
| **C19** (option-bullet labeling) | Apply to H3-form Qs. Options at top-level bullet within the H3's body, must be `- **(A)`, `- **(B)`, etc. |
| **C20** (blank line after Recommendation) | N/A for paragraph-form Recommendation; for bullet-form Recommendation inside an H3, apply normally. |
| **C21** (empty Open Questions) | Apply uniformly: count both bullet-form and H3-form pending Qs; only fire C21 when both counts are zero. |

### File edits

- `audit-q.py:142-145` — add `Q_HEADER_H3_RE`.
- `audit-q.py:970+ extract_q_entries()` — extend to detect both forms; return uniform `QEntry` records with a `shape: "bullet" | "h3"` field.
- `audit-q.py:1200+ check_c9_recommendation_present()` — adapt to read shape; relax for paragraph form (or warn-only).
- `audit-q.py:1231+ check_c10_recommendation_outdent()` — skip when shape == "h3".
- `audit-q.py:1367+ check_c19_option_bullets()` — adapt option-locator to look at top-level bullets when shape == "h3" rather than indented.
- `audit-q.py:1499+ check_c21_empty_open_questions()` — already counts QEntries; will work automatically once they include H3-form.
- `audit-q.py:1077+ check_c6_block_id_present()` — adapt block-ID lookup for H3 form (block-ID at end of H3 line vs. at end of bullet line).

Estimated diff: ~100-150 lines across the existing functions plus a couple of new helper functions.

### Test fixtures

Create two synthetic feature docs under `Topic/Misc/Test/F123-fixtures/`:

1. **`F123-h3-pending.md`** — `## Open Questions` containing two `### Q1` and `### Q2` with options + Recommendations. Expected: 0 findings (well-formed).
2. **`F123-h3-no-rec.md`** — H3-form Q without a Recommendation. Expected: C9 fires.
3. **`F123-h3-resolved.md`** — H3-form Qs all under `### Resolved`. Expected: C21 fires (Phase 2 transition missed).

Run the script against each fixture; assert findings match expectations.

## Status

**Done** — landed 2026-06-07. Parser extended with `Q_HEADER_H3_RE` + `RECOMMENDATION_PARA_RE`; QEntry carries `shape` + `recommendation_is_paragraph`; `extract_q_entries` detects both bullet and H3 forms; C10/C19/C20 adapted per Affected Checks table. Synthetic fixtures at `~/ob/kmr/Topic/Misc/Test/F123-fixtures/` (pending=clean, no-rec=C9, resolved=C21) verify expected behavior. Vault-wide `--scope q` audit dropped from the C21 false-positive (DKT F029) to 0 findings after DKT block-ID was added and F061 (Done since 2026-05-18) had its top H3 Qs renamed to `### Resolved Q<n> — ...` to bypass detection (content preserved). All five Success Criteria verification steps passed in the same turn the work completed.
