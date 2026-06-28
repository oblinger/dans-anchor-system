---
description: "worked examples of every rule-execution mode (start here)"
---
# Warden Examples

One worked ruleset, four rules — each a different **execution mode**. A Warden rule isn't always run the same way: some are decided by a cheap script, some need the LLM to read and reason, and some combine the two. This page walks through all of them.

![[Warden Examples Ruleset.svg]]

*One ruleset, four modes.* ✎ [regenerate](../Warden%20Design/warden-rule-figures.py)

## The four modes

| # | Mode | Tier | Who decides it | Cost | Use it when |
|---|---|---|---|---|---|
| 01 | **Mechanical** | `checked` | a **script** (`check::` primitive) | ~free | the rule is a deterministic pattern — a regex, a required field, a structural fact |
| 02 | **Judgment** | `stated` | the **LLM** reads + reasons | tokens | the rule needs *understanding*, not a pattern ("does the summary match the body?") |
| 03 | **Script-assisted** | `stated` + `check::` | a **script narrows the input**, then the LLM judges the slice | reduced tokens | a cheap script can extract or detect the relevant part first, so the LLM reasons over a page, not the whole file |
| 04 | **Judgment, gated** | `stated` + `rerun::` | the LLM — but **only when the edit is significant** | amortized | an expensive rule that shouldn't re-run on every typo (the re-evaluation economy, below) |

### 01 · Mechanical — `R-ex-01`

`check:: regex_present ^description::` is a deterministic primitive. The script answers pass/fail with zero LLM involvement, and the verdict is content-hash cached. Most structural rules are mechanical — they're effectively free, so run them everywhere.

### 02 · Judgment — `R-ex-02`

"The `## Summary` faithfully reflects `## Design`" can't be a regex — it needs reading and reasoning. So it's a `stated` rule: the LLM reads both sections and judges, returning pass/fail + reason. Judgment rules cost tokens, so Warden batches and caches them (a verdict is reused until the file changes).

### 03 · Script-assisted — `R-ex-03`

The expensive part of a judgment rule is usually *reading the whole file*. `R-ex-03` puts a cheap script in front: `check:: extract_section "## Open Questions"` pulls just that section, and the LLM reasons over **only that slice** — "are these items still open given the rest of the doc?". The script narrows the LLM's input, so a rule that would have cost a full-file read costs a paragraph. This is the bridge between the two pure modes: **script prepares, LLM judges.**

### 04 · Judgment, gated — `R-ex-04` (the re-evaluation economy)

Here's the problem this mode solves. `R-ex-04` is an expensive LLM rule — "does the architecture figure still match the prose?". Its `when:: write:markdown` means it *could* fire on every edit to an architecture doc. But re-reading the whole doc and re-reasoning on every keystroke-scale edit would **exhaust the agent and burn tokens** for no benefit — the diagram didn't become wrong because you fixed a typo.

So the rule adds `rerun:: significant`: after the first evaluation, the expensive body **re-runs only when the file has changed *significantly*** since it last passed. A cheap gate (a script measuring the change) decides "significant?" before any LLM tokens are spent. The first check is full; subsequent tiny edits are skipped; a real structural edit re-triggers it.

> [!info] Status — `rerun::`, `extract_section`, and `significant` are *designed, not yet built*
> Modes 01 and 02 work today. The script-assisted hook (`check::` feeding the judgment), the `rerun::` re-evaluation gate, and what counts as a "significant" edit are on the [[Warden Roadmap]] — the design is [[F215 — Re-evaluation economy — the significant-edit gate|F215]]. v1 measures significance by **diff magnitude** (lines / % changed); a later milestone adds **semantic update levels** (a cheap classifier rating an edit typo → structural, so only meaningful edits re-trigger expensive rules). The syntax above is the intended form.

## Rule of thumb

Reach for the cheapest mode that can express the rule: **mechanical if a script can decide it; script-assisted if a script can at least narrow it; pure judgment only when it genuinely needs the model.** And gate any expensive rule that fires on writes with `rerun:: significant`, so Warden can instrument almost every edit without exhausting the agent.
