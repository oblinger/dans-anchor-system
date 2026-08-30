# RULESET R-brief
include::
where:: `sentinel: ^#+ BRIEF\b`
import:: skills/audit/scripts/audit-plan.py
description:: agent-facing per-file editing-and-maintenance content paired with a source file

Embedded ruleset for the Brief facet, co-located per [[F133 — Rulesets folder convention + facet embedding|F133]]. `where::` is the inline-`# BRIEF` sentinel; the sidecar rule (R-brief-02) targets `* Brief.md`.

### RULE R-brief-01 — Inline brief is a bottom `# BRIEF` H1 (checked)
check:: brief_is_last_h1

The Phase-1 form is a single all-caps `# BRIEF` H1 at the bottom of the source file.

The set's `^#+ BRIEF\b` sentinel admits `## BRIEF` as well as `# BRIEF`, and that is deliberate rather than sloppy: an H2 spelling is precisely the violation this rule exists to correct, so a sentinel that only admitted the correct form would select exactly the files with nothing wrong. Wired 2026-08-11 ([[Tink Backlog#^T349|T349]]) — **8 findings across the 509 files carrying the sentinel**, against 509 LLM judgments before.

**Check pattern:** at most one `^# BRIEF$` heading, and it is the last H1 in the file.

### RULE R-brief-02 — Sidecar is `<Source> Brief.md` with matching H1 (checked)
where:: `file:{anchor}/**/* Brief.md, !**/DAS *.md`
check:: brief_h1_matches_name

The Phase-2 form is a sidecar `<Source Name> Brief.md` whose H1 is `# <Source Name> Brief`.

**Check pattern:** a `* Brief.md` file's H1 equals its basename.

**Why this rule needs a selector of its own, and had none until 2026-08-11** ([[Tink Backlog#^T349|T349]]). The set is scoped by the `^#+ BRIEF\b` sentinel — the *inline* form — and a sidecar does not carry that heading: its H1 is `# <Source> Brief`, which is the whole subject of this rule. Measured across the vault: **7 sidecar files exist and the sentinel reaches exactly 1 of them**, so this rule was being asked about 509 files that are not sidecars and 1 file that is. Its checker sat unwired and would have answered *"not a Brief.md file"* 508 times had anyone wired it — which is why the orphan looked like dead code and was not. The rule-level `where::` above is the repair; `!**/DAS *.md` keeps the facet spec out, for the reason `-06` records.

### RULE R-brief-03 — Surfaced from the source (stated)

The source points at its brief: a `Related` row listing the Brief **first**, or a `(See …)` line under the H1 when the source has no dispatch table.

**Check pattern:** the source's `Related` cell leads with `~~[[<Source> Brief\|Brief]]~~`, or a `(See ~~[[… Brief]]~~)` line follows the H1.

### RULE R-brief-04 — Agent-facing only (stated)

A Brief carries *how to maintain this file* (editing rules, inclusion tests, traps) — not user-facing orientation, which lives in the source's one-line TLDR / optional `## Overview`.

### RULE R-brief-05 — No duplication of higher-level rules (stated)

A Brief carries only file-specific operational content — never project-wide (CLAUDE.md), markdown ([[R-markdown]]), facet/trait, or anchor-local (`{slug} Rules.md`) rules.

### RULE R-brief-06 — Briefs don't nest (checked)
where:: `file:{anchor}/**/* Brief.md, !**/DAS *.md`
check:: brief_not_nested

A brief is a sidecar to exactly one source; a brief has no brief of its own.

**Check pattern:** no `* Brief Brief.md` file, and no `# BRIEF` heading inside a `* Brief.md`.

**The facet spec is excluded, and the collision is worth naming.** Facet specs are named `DAS <Kind>.md`, so the spec for *this* facet is `DAS Brief.md` — a filename ending ` Brief.md`, matched by the glob, and not a sidecar at all. It carries a live `# BRIEF` H1 at its foot, which is its own inline brief and is exactly what `R-brief-01` asks of it. Without the exclusion this rule reads that as a brief nested in a brief and reports the file for obeying a sibling rule. Wired 2026-08-11 ([[Tink Backlog#^T349|T349]]) with the exclusion, and it then finds **0** across the vault's 7 sidecars — the sole finding it produced without one was that false positive. Same shape as `plan_one`'s glob exemption for `DAS Decisions.md`, one layer down: a *rule's* glob can be fooled by a filename just as a *ruleset's* can.

### RULE R-brief-07 — Opens with a labeled maintainer-note lead-in (checked)

A Brief begins with an italic `*(Maintainer note — …)*` lead-in naming what the note covers and pointing at where the normative content lives, so an outside reader immediately sees the section is maintainer guidance, not spec.

**Check pattern:** the first non-blank line after the `# BRIEF` heading (or after the sidecar's H1) matches `*(Maintainer note — …)*`.

### RULE R-brief-08 — Only genuine maintainer notes; no spec, no generic advice (stated)

A Brief holds only non-obvious, file-specific maintainer guidance. Normative spec content lives in the source's body or RULESET — never only in the Brief; generic doc-advice is a one-link cite to its governing discipline, never a restatement; content already obvious from the body is dropped. If nothing genuine remains after distilling, the file carries **no** Brief at all.

### RULE R-brief-09 — Distill by relocation, never deletion (stated)

When trimming or distilling a Brief, any non-obvious content is relocated (into the source's body/ruleset, or to the governing discipline) — never silently deleted. Before dropping a bullet, confirm its content already exists in the body/ruleset or is genuinely obvious-from-context.
