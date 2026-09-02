# RULESET R-stacked-table
import:: skills/audit/scripts/audit-plan.py
where:: `sentinel: ^\|[^|]*<br/>.*\|$`
description:: Rules for stacked tables ([[DAS stacked-table]]) — header-declared arity, the structural/cosmetic break polarity, no literal newlines.

Ruleset for the stacked-table slot facet ([[DAS stacked-table]]). The selector matches a table header row carrying a structural `<br/>`; the rules govern that table's body.

### RULE R-stacked-table-01 — Cell arity matches the header (checked)

Every body cell in a stacked column carries exactly as many structural `<br/>` separators as that column's header cell declares. Cosmetic `<br>` breaks are excluded from the count.

**Check pattern:** for each table whose header row contains `<br/>`: per column, count `<br/>` in the header cell; assert every body cell in that column matches. Report file, line, column, expected vs found.

**Why:** a wrong count silently shears sub-values into the wrong sub-row — the corruption renders plausibly and is invisible until someone reads the wrong dose off the wrong line.

### RULE R-stacked-table-02 — Polarity: `<br/>` structural, `<br>` cosmetic (agent-judged)

Structural separators are spelled `<br/>`; soft wraps are spelled `<br>`. An editor-added `<br>` (Obsidian Shift+Return) is legal where it wraps within a sub-cell; an agent finding a bare `<br>` sitting where a sub-row boundary belongs reclassifies it to `<br/>`.

**Why:** the casual keystroke must be the spelling that cannot corrupt structure; only deliberate authors declare schema.

### RULE R-stacked-table-03 — Missing sub-values are `—` (checked)

An unknown or absent sub-value is an em-dash, never an empty string — emptiness is indistinguishable from a forgotten entry, and it collapses the arity count's usefulness as a completeness signal.

**Check pattern:** flag a stacked cell whose structural split yields a zero-length sub-value.
