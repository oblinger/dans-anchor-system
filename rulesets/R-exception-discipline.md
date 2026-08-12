# RULESET R-exception-discipline
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* Exceptions.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog — a `DAS <Name>.md` is the SPEC for a facet, not an instance (the form [[R-backlog]] and [[R-prd]] use).
description:: Accepted rule-violations are catalogued as numbered, graded exceptions with a stated justification — the audit engine reads that table, and a corpus's suppressions are counted on every run.

Every checked rule needs an escape, because a rule that admits none gets weakened the first time it is genuinely wrong — and a weakened rule stops catching the cases it was right about. The escape is a numbered row in the anchor's `{slug} Track/{slug} Exceptions.md`, scoped to a named target, graded, and justified.

Recurs in HA + MUX + the R-ob enforcement idiom. HA: "Exceptions are numbered (EX001, EX002, …) with grades and For/Against justification"; every accepted site carries an inline `EX<n>` comment. MUX: "Scanner … Exception table destructively rewritten each run" with High/Medium/Low graded findings. [[R-ob-observability]]-01 already requires it per-rule ("listed in an Exceptions table with a grade + justification"); this family generalizes the idiom so any adopted ruleset can lean on it.

> **The selector was written five times and inherited zero times, which cost 112 of TINK's 911 judgment tasks — [[TINK Backlog#^T212|T212]], 2026-08-11.** Five rules (`-01`, `-02`, `-04`, `-05`, `-09`) each carried an identical `where::` line; the set itself declared none, so the other four inherited `always` — every markdown file in every anchor. Those four are the `(stated)` ones, and each says in its own Check pattern that **no document can evidence it**: *"asserted about the engine rather than about a file"*, *"a file's content cannot evidence it"*. So an LLM was being asked, of all 28 TINK documents, whether the audit report prints `except N`. The selector is now declared once at the set level and every rule inherits it — the effective scope of the five wired rules is byte-identical, and the four judged rules go from 28 targets to the anchor's one exception table.
>
> **The residue is a real gap and not this row's to close.** `-03`, `-06`, `-07` and `-08` are verified by `test-f314-exceptions.py`, and `where::` has no way to say *"a test verifies this, not a target"* — so their honest scope is *no target at all*, which the grammar cannot express any more than it can express T218's trait gate. They are the only four rules in the corpus whose Check pattern says this. Scoped to the exception table because that is the narrowest true-ish thing available; filed as [[TINK Backlog#^T220|T220]].

**Rules -01 through -03 were correct and unread from 2026-07-06 to 2026-08-08.** [[Warden Exceptions]] recorded three real architectural deviations against them and nothing consumed the file: `audit-plan.py` had no exception concept anywhere in 6,626 lines. Rules -04 through -09 are the enforcement surface that closes that, added by [[TINK314 - Exceptions: a graded, user-approved escape from any checked rule|F314]]; the table is now the thing the engine reads, not a thing the engine documents.

### RULE R-exception-discipline-01 — Accepted violations live in a numbered exception table (checked)
check:: exceptions_table_wellformed

Each anchor's accepted deviations are enumerated in an exceptions table with per-anchor-unique numbers (EX001…), monotonic and never recycled. A violation neither fixed nor listed is an open finding, not an exception.

**Check pattern:** the table's `EX` cells match `^EX\d{3,}$`.

### RULE R-exception-discipline-02 — Every exception carries a grade + justification (checked)
check:: exceptions_table_wellformed

Each entry is graded `A`–`F` with a one-line justification for NOT taking the strict fix. Ungraded exceptions are unreviewed debt, and here that is literal: an ungraded row suppresses nothing.

**Check pattern:** each row's grade cell is one of `A`–`F` (graded) or `?` (proposed), and its justification cell is non-empty. What each grade *does* is `-08`.

### RULE R-exception-discipline-03 — Audits re-run mechanically and fail on ungraded regressions (stated)

The rules an exception covers keep running. A finding that matches no approved row fails the audit rather than silently growing the pile.

**Check pattern:** `execute_plan` rewrites a `fail` to `except` only where an approved row matches both the rule id and the target; every other failure stands. Asserted about the engine rather than about a file, so its guard is `skills/audit/scripts/test-f314-exceptions.py`, not a `check::` — there is no document whose content could carry the evidence.

### RULE R-exception-discipline-04 — One path, and it is `{slug} Track/{slug} Exceptions.md` (checked)
check:: exceptions_table_wellformed

The anchor's exception table lives at `{slug} Track/{slug} Exceptions.md` — visible, slug-named, reachable from the Track dispatch page. There is no search order and no second location.

**Check pattern:** the file the engine reads is `{slug} Track/{slug} Exceptions.md`; any other exception table in the anchor is not read and is reported as such.

**Why:** two other spellings existed and neither had ever held a file — `cab-audit.py` read `.skl/lint/exceptions.md`, the audit skill's docs cited `.anchor.d/lint/exceptions.md`, and **neither directory appeared anywhere in the vault**. Keeping either as a fallback would preserve ambiguity over paths with no instances behind them. The chosen path is the one [[Warden Exceptions]] already occupied. **`cab-audit.py`'s loader was deleted 2026-08-08 (TINK T167)** rather than routed here: its rule ids are a separate namespace (`field-undocumented`, not `R-*`), its second path pointed at `~/.claude/skills/cab/`, a directory that does not exist, and the whole mechanism had suppressed nothing since it was written. There is now one exception surface, not a preferred one.

### RULE R-exception-discipline-05 — The table's five columns, and Target is never blank (checked)
check:: exceptions_table_wellformed

The table is `| EX | Rule | Target | Grade | Justification |`. **Rule** is one rule id per row, so each deviation grades and retires on its own. **Target** is a path glob relative to the anchor root and is never blank — an anchor-wide exception writes `**` explicitly.

**Check pattern:** every `EX`-handled row parses with a rule id matching `^R-[a-z0-9-]+-\d{2}$`, a non-empty target, a valid grade, and a non-empty justification; a malformed row is reported by name.

**Why:** `cab-audit.py` made an empty cell mean "everything", then needed a hardcoded list of rules for which blanket suppression is refused — a special case that existed only because the default was dangerous. Requiring the glob makes a wide exception a visible act, and removes the reject-list entirely.

### RULE R-exception-discipline-06 — Grade `?` is a proposal and suppresses nothing (stated)

An agent may write an exception row at any time, graded `?` — except against a rule marked `confirm:: user` (`-09`), where it asks first. The row is durable and reviewable in the anchor's own tree, and it **suppresses nothing** — the finding still fails. Grading it is the user's act, and that column is the whole approval gate.

**Check pattern:** a row graded `?` never rewrites a verdict; only `A`–`F` does. An engine assertion, guarded by `test-f314-exceptions.py` on both the `--run` and the on-write paths, since a file's content cannot evidence it.

**Why:** the system should be free to *record* an accepted deviation the moment it decides one, without that recording being self-granted permission. Nothing mechanically stops an agent typing `A`, and nothing should try — a gate that hard would just redirect the same pressure into weakening the rule, which is what this whole family exists to prevent. The real defense is that the table is visible and the suppressions are counted. `-09` adds friction, not a lock: on a `confirm:: user` rule the ungraded row goes red, so the proposal has to be resolved rather than parked, and a forged grade is still a forged grade sitting in a file with the user's name on the column.

### RULE R-exception-discipline-07 — Suppressions and stale rows are counted on every run (stated)

Every audit report prints `except N` unconditionally, lists the suppressed findings in their own section, and names any row that suppressed nothing this run.

**Check pattern:** the verdict counts carry an `except` key at all times, and `render_report` emits the accepted-deviations section whenever exceptions, stale rows, or malformed rows exist. An engine assertion, guarded by `test-f314-exceptions.py`.

**Why:** a corpus with forty accepted deviations must never read like one with none, and a row that has outlived the document it was written for is how the table decays into a pile nobody trusts. An instrument that reports nothing when it found nothing is indistinguishable from one that never ran.

### RULE R-exception-discipline-08 — Only `A`–`C` suppresses; `D` or lower is a recorded refusal (stated)

The grade is a scale, not a rubber stamp. `A`–`C` suppress the finding. `D`, `E` and `F` are grades the user can give and they mean *"I read this deviation and it is not good enough"* — the finding goes on failing while the row survives as the durable record of that judgment. `?` is the ungraded proposal and suppresses nothing (`-06`).

**Both a `fail` and a `warn` are suppressed; an `error` never is.** The rule originally said *"the finding"* with no severity carve-out while the engine rewrote only `fail`, so a row aimed at a warning read as perfectly valid and did nothing. That cost a real acceptance: [[ATT|Atticus]] wrote a well-formed `A` row against `R-spine-07` on `Staff/Atticus/Atticus.md` — a deviation Dan had personally graded — watched the engine report it as *stale*, and withdrew it rather than leave a row that reads as coverage while suppressing nothing. Widened 2026-08-11 on Dan's answer to [[TINK Backlog#^T201|T201]] Q1: *"audit grades A through C should suppress warnings, because we've already decided that that exception is okay."* The reason it belongs at the warning tier rather than despite it: the judgment calls live there (`R-rocks-05`, `R-spine-07`, `R-rocks-04`'s expansion half), so the tier most likely to hold a genuine acceptance was the one tier that could not record one.

**`error` stays unsuppressable, and that is not a leftover.** A crashed checker is a bug, not a deviation; a table that could hide one would be a way to make bugs invisible by hand. A row aimed at an errored rule is reported as *the rule errored — fix the checker*, never as stale, which is the same misdiagnosis-avoidance the warn case needed before it became suppressible.

**Check pattern:** `load_exceptions` admits a row only where its grade is in `ABC`; every other well-formed row is returned as *declined* and reported by name in the verdicts, the on-write output and the report's accepted-deviations section. An engine assertion, guarded by `test-f314-exceptions.py`, which asserts each of the six letters individually rather than one representative — a floor that held for `D` but leaked on `F` would be invisible to a single-letter test.

**Why:** before the floor, every letter did the same thing, which made the column a binary wearing a scale's clothes. The user had no way to say *"recorded, and no"* short of deleting the row — which loses why the deviation was ever proposed, so the next agent to meet the same violation proposes it again. A refusal that survives is what stops that loop, and it is deliberately **not** reported as stale: it did exactly what it says.

### RULE R-exception-discipline-09 — A rule may demand a conversation before it can be excepted (checked)
check:: exceptions_table_wellformed

A rule (or a whole ruleset) declares `confirm:: user` when the agent may not accept a deviation from it unaided. For those rules the agent asks first and records the grade it is given; an ungraded `?` row against one **fails the exception table** until the grade arrives.

**Check pattern:** `chk_exceptions_table_wellformed` resolves each row's rule id to its ruleset, reads `effective_confirm` (rule > ruleset > none), and fails the table naming every `?` row whose rule requires confirmation. A graded row passes — including a refusal, because the conversation happened and the answer was no.

**Why:** the grade is the user's act, so requiring one *is* the confirmation gate — no second approval channel, and nothing new for an author to keep in sync. Making the pending proposal red rather than merely visible is the load-bearing part: a `?` row that audits clean is a permanent "pending" nobody has to resolve, which is how "ask me first" degrades into a sentence that reads identically whether or not anyone obeys it. Applied where deviations should be rare — the spine rules `R-spine-01`, `-03`, `-04`, per Dan 2026-08-08: *"it should ask me before it puts an exception in because I think there shouldn't be that many exceptions to the rule."* Left off elsewhere, because a rule that gates every proposal behind the user turns the proposal mechanism back into the chat conversation it exists to replace.

## Position in the catalog

Sits under [[R-process]]. Adopted by any anchor that runs checked rules; the table is created on first use and absent otherwise, so its presence is itself the signal that the anchor has accepted deviations.

## See also

- [[Warden Exceptions]] — the first instance, and until F314 the only one.
- [[TINK314 - Exceptions: a graded, user-approved escape from any checked rule|F314]] — the feature that made the table readable by the engine.
