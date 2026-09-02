# RULESET R-stacked-table
import:: skills/audit/scripts/audit-plan.py
where:: `sentinel: ^\|\s*\[=\]`
description:: Rules for [=]-declared stacked tables ([[DAS stacked-table]]) — visible corner marker, first-column stack, whole-table arity, no empty sub-values.

Ruleset for the stacked-table slot facet ([[DAS stacked-table]]). The selector is the visible `[=]` marker opening the table's first header cell — Dan 2026-09-01: a selector living only in ordinary cell content dies silently when the cell is edited; the marker is content, on screen, and its deletion is a deliberate visible act.

### RULE R-stacked-table-01 — The first column draws the stack; its length is the table's arity (checked)
check:: stacked_table

A stacked table's header first cell begins `[=]` and carries `[=] ` at the start of every sub-row line; the number of those lines is THE arity for the whole table. Every cell in every row splits on structural `<br/>` into exactly that many sub-values; every first-column sub-line carries `[=] `; a missing sub-value is `—`, never empty. Bare `<br>` is a cosmetic wrap (what Obsidian's Shift+Return emits) and is ignored by every count. Violations are reported per row, column and cell so the writing agent can fix without guessing; the intended end state is that a nonconforming write is REFUSED (warden PreToolUse), pointing the agent at [[DAS stacked-table]].

**Check pattern:** `chk_stacked_table` — find each table whose header first cell starts `[=]`; arity = sub-lines of that cell; validate every cell's `<br/>` split count, the first column's `[=] ` prefixes, and non-emptiness.

**Why:** a wrong count silently shears sub-values into the wrong sub-row — the corruption renders plausibly and is read as the wrong dose off the wrong line. The visible stack in column one is both the declaration and the reader's key to the whole table.

### RULE R-stacked-table-02 — Polarity: `<br/>` structural, `<br>` cosmetic (stated)

Structural separators are spelled `<br/>`; soft wraps are spelled `<br>`. An editor-added `<br>` (Obsidian Shift+Return) is legal where it wraps within a sub-cell; an agent finding a bare `<br>` where a sub-row boundary belongs reclassifies it to `<br/>`.

**Why:** the casual keystroke must be the spelling that cannot corrupt structure; only deliberate authors declare schema.
