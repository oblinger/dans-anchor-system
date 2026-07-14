# RULESET R-brief
include::
where:: `sentinel: ^#+ BRIEF\b`
description:: agent-facing per-file editing-and-maintenance content paired with a source file

Embedded ruleset for the Brief facet, co-located per [[F133 — Rulesets folder convention + facet embedding|F133]]. `where::` is the inline-`# BRIEF` sentinel; the sidecar rule (R-brief-02) targets `* Brief.md`.

### RULE R-brief-01 — Inline brief is a bottom `# BRIEF` H1 (checked)

The Phase-1 form is a single all-caps `# BRIEF` H1 at the bottom of the source file.

**Check pattern:** at most one `^# BRIEF$` heading, and it is the last H1 in the file.

### RULE R-brief-02 — Sidecar is `<Source> Brief.md` with matching H1 (checked)

The Phase-2 form is a sidecar `<Source Name> Brief.md` whose H1 is `# <Source Name> Brief`.

**Check pattern:** a `* Brief.md` file's H1 equals its basename.

### RULE R-brief-03 — Surfaced from the source (stated)

The source points at its brief: a `Related` row listing the Brief **first**, or a `(See …)` line under the H1 when the source has no dispatch table.

**Check pattern:** the source's `Related` cell leads with `~~[[<Source> Brief\|Brief]]~~`, or a `(See ~~[[… Brief]]~~)` line follows the H1.

### RULE R-brief-04 — Agent-facing only (stated)

A Brief carries *how to maintain this file* (editing rules, inclusion tests, traps) — not user-facing orientation, which lives in the source's one-line TLDR / optional `## Overview`.

### RULE R-brief-05 — No duplication of higher-level rules (stated)

A Brief carries only file-specific operational content — never project-wide (CLAUDE.md), markdown ([[R-markdown]]), facet/trait, or anchor-local (`{slug} Rules.md`) rules.

### RULE R-brief-06 — Briefs don't nest (checked)

A brief is a sidecar to exactly one source; a brief has no brief of its own.

**Check pattern:** no `* Brief Brief.md` file, and no `# BRIEF` heading inside a `* Brief.md`.

### RULE R-brief-07 — Opens with a labeled maintainer-note lead-in (checked)

A Brief begins with an italic `*(Maintainer note — …)*` lead-in naming what the note covers and pointing at where the normative content lives, so an outside reader immediately sees the section is maintainer guidance, not spec.

**Check pattern:** the first non-blank line after the `# BRIEF` heading (or after the sidecar's H1) matches `*(Maintainer note — …)*`.

### RULE R-brief-08 — Only genuine maintainer notes; no spec, no generic advice (stated)

A Brief holds only non-obvious, file-specific maintainer guidance. Normative spec content lives in the source's body or RULESET — never only in the Brief; generic doc-advice is a one-link cite to its governing discipline, never a restatement; content already obvious from the body is dropped. If nothing genuine remains after distilling, the file carries **no** Brief at all.

### RULE R-brief-09 — Distill by relocation, never deletion (stated)

When trimming or distilling a Brief, any non-obvious content is relocated (into the source's body/ruleset, or to the governing discipline) — never silently deleted. Before dropping a bullet, confirm its content already exists in the body/ruleset or is genuinely obvious-from-context.
