# RULESET R-exception-discipline
include::
import:: skills/audit/scripts/audit-plan.py
description:: Accepted rule-violations are catalogued as numbered, graded exceptions with a stated justification — the audit engine reads that table, and a corpus's suppressions are counted on every run.

Every checked rule needs an escape, because a rule that admits none gets weakened the first time it is genuinely wrong — and a weakened rule stops catching the cases it was right about. The escape is a numbered row in the anchor's `{slug} Track/{slug} Exceptions.md`, scoped to a named target, graded, and justified.

Recurs in HA + MUX + the R-ob enforcement idiom. HA: "Exceptions are numbered (EX001, EX002, …) with grades and For/Against justification"; every accepted site carries an inline `EX<n>` comment. MUX: "Scanner … Exception table destructively rewritten each run" with High/Medium/Low graded findings. [[R-ob-observability]]-01 already requires it per-rule ("listed in an Exceptions table with a grade + justification"); this family generalizes the idiom so any adopted ruleset can lean on it.

**Rules -01 through -03 were correct and unread from 2026-07-06 to 2026-08-08.** [[Warden Exceptions]] recorded three real architectural deviations against them and nothing consumed the file: `audit-plan.py` had no exception concept anywhere in 6,626 lines. Rules -04 through -07 are the enforcement surface that closes that, added by [[TINK314 - Exceptions: a graded, user-approved escape from any checked rule|F314]]; the table is now the thing the engine reads, not a thing the engine documents.

### RULE R-exception-discipline-01 — Accepted violations live in a numbered exception table (checked)
check:: exceptions_table_wellformed
where:: `file:{anchor}/**/* Exceptions.md, !**/DAS *.md`

Each anchor's accepted deviations are enumerated in an exceptions table with per-anchor-unique numbers (EX001…), monotonic and never recycled. A violation neither fixed nor listed is an open finding, not an exception.

**Check pattern:** the table's `EX` cells match `^EX\d{3,}$`.

### RULE R-exception-discipline-02 — Every exception carries a grade + justification (checked)
check:: exceptions_table_wellformed
where:: `file:{anchor}/**/* Exceptions.md, !**/DAS *.md`

Each entry is graded `A`–`F` with a one-line justification for NOT taking the strict fix. Ungraded exceptions are unreviewed debt, and here that is literal: an ungraded row suppresses nothing.

**Check pattern:** each row's grade cell is one of `A`–`F` (approved) or `?` (proposed), and its justification cell is non-empty.

### RULE R-exception-discipline-03 — Audits re-run mechanically and fail on ungraded regressions (stated)

The rules an exception covers keep running. A finding that matches no approved row fails the audit rather than silently growing the pile.

**Check pattern:** `execute_plan` rewrites a `fail` to `except` only where an approved row matches both the rule id and the target; every other failure stands. Asserted about the engine rather than about a file, so its guard is `skills/audit/scripts/test-f314-exceptions.py`, not a `check::` — there is no document whose content could carry the evidence.

### RULE R-exception-discipline-04 — One path, and it is `{slug} Track/{slug} Exceptions.md` (checked)
check:: exceptions_table_wellformed
where:: `file:{anchor}/**/* Exceptions.md, !**/DAS *.md`

The anchor's exception table lives at `{slug} Track/{slug} Exceptions.md` — visible, slug-named, reachable from the Track dispatch page. There is no search order and no second location.

**Check pattern:** the file the engine reads is `{slug} Track/{slug} Exceptions.md`; any other exception table in the anchor is not read and is reported as such.

**Why:** two other spellings existed and neither had ever held a file — `cab-audit.py` reads `.skl/lint/exceptions.md`, the audit skill's docs cited `.anchor.d/lint/exceptions.md`, and **neither directory appears anywhere in the vault**. Keeping either as a fallback would preserve ambiguity over paths with no instances behind them. The chosen path is the one [[Warden Exceptions]] already occupied.

### RULE R-exception-discipline-05 — The table's five columns, and Target is never blank (checked)
check:: exceptions_table_wellformed
where:: `file:{anchor}/**/* Exceptions.md, !**/DAS *.md`

The table is `| EX | Rule | Target | Grade | Justification |`. **Rule** is one rule id per row, so each deviation grades and retires on its own. **Target** is a path glob relative to the anchor root and is never blank — an anchor-wide exception writes `**` explicitly.

**Check pattern:** every `EX`-handled row parses with a rule id matching `^R-[a-z0-9-]+-\d{2}$`, a non-empty target, a valid grade, and a non-empty justification; a malformed row is reported by name.

**Why:** `cab-audit.py` made an empty cell mean "everything", then needed a hardcoded list of rules for which blanket suppression is refused — a special case that existed only because the default was dangerous. Requiring the glob makes a wide exception a visible act, and removes the reject-list entirely.

### RULE R-exception-discipline-06 — Grade `?` is a proposal and suppresses nothing (stated)

An agent may write an exception row at any time, graded `?`. It is durable and reviewable in the anchor's own tree, and it **suppresses nothing** — the finding still fails. Grading it `A`–`F` is the user's act, and that column is the whole approval gate.

**Check pattern:** a row graded `?` never rewrites a verdict; only `A`–`F` does. An engine assertion, guarded by `test-f314-exceptions.py` on both the `--run` and the on-write paths, since a file's content cannot evidence it.

**Why:** the system should be free to *record* an accepted deviation the moment it decides one, without that recording being self-granted permission. Nothing mechanically stops an agent typing `A`, and nothing should try — a gate that hard would just redirect the same pressure into weakening the rule, which is what this whole family exists to prevent. The real defense is that the table is visible and the suppressions are counted.

### RULE R-exception-discipline-07 — Suppressions and stale rows are counted on every run (stated)

Every audit report prints `except N` unconditionally, lists the suppressed findings in their own section, and names any row that suppressed nothing this run.

**Check pattern:** the verdict counts carry an `except` key at all times, and `render_report` emits the accepted-deviations section whenever exceptions, stale rows, or malformed rows exist. An engine assertion, guarded by `test-f314-exceptions.py`.

**Why:** a corpus with forty accepted deviations must never read like one with none, and a row that has outlived the document it was written for is how the table decays into a pile nobody trusts. An instrument that reports nothing when it found nothing is indistinguishable from one that never ran.

## Position in the catalog

Sits under [[R-process]]. Adopted by any anchor that runs checked rules; the table is created on first use and absent otherwise, so its presence is itself the signal that the anchor has accepted deviations.

## See also

- [[Warden Exceptions]] — the first instance, and until F314 the only one.
- [[TINK314 - Exceptions: a graded, user-approved escape from any checked rule|F314]] — the feature that made the table readable by the engine.
