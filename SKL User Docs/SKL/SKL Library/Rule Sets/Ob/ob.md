---
description: LEGACY — split into R-ob-state-mgt.md and R-ob-observability.md 2026-06-08 as part of the rules-vs-decisions vocabulary split. Content below preserved for the markdown / commit-discipline / em-dash rules (kmr-flavored, not yet split into rule sets). For the structured Ob rule sets, see [[R-ob-state-mgt]] and [[R-ob-observability]].
applies-when: every project Dan owns (cross-cutting, not trait-scoped).
set-id: OB
---

> [!warning] Legacy file
> This file's content is being progressively split into individual rule sets under `Rule Sets/Ob/` per [[F132 — Rules Migration]]. Already split:
> - [[R-ob-state-mgt]] — was the data-singleton + no-hardcoded rules.
> - [[R-ob-observability]] — was the no-silent-fallbacks + OS-bridge-logging rules.
>
> Still in this file: the markdown-validity / kmr-commit-discipline / em-dash-policy rules. They'll move into their own `R-ob-*` rule sets in a follow-on pass.


# Ob/ob — Dan's personal cross-project decisions

A small canonical set of decisions Dan applies to *every* project he owns. Not trait-scoped (a personal-Code-anchor and a personal-Skill-anchor both pull this in); not domain-scoped (applies to docs, code, configs alike). Naming "ob" mirrors the `ob-` prefix used elsewhere in Dan's tooling (`ob-skills`, `ob-utils`, vault root `~/ob/`). Rename if a better umbrella name surfaces later.


### D-OB01 — Markdown must be valid for Obsidian (checked)

All markdown files Dan owns render correctly in Obsidian. Two concrete sub-rules:

**Sub-rule 1: No raw angle brackets without surrounding whitespace.**

Obsidian interprets `<word>` as an HTML tag attempt and breaks rendering. Use angle brackets only when separated from adjacent text by whitespace, OR escape them, OR fence the content in a code block.

**Why:** observed breakage in past docs where `<foo>` placeholders got swallowed by the Obsidian renderer; the content disappeared from the rendered view with no visible error.

**Check pattern:** grep for `\S<[A-Za-z_]` or `[A-Za-z_]>\S` outside code fences. Both are leading/trailing-whitespace-less angle brackets and should fail. Acceptable forms: `<verb>` inside backticks, `< verb >` with whitespace, `&lt;verb&gt;` escaped.

**Sub-rule 2: Blank lines before and after every markdown table.**

Tables without surrounding blank lines either fail to render as tables or merge into adjacent paragraphs in Obsidian's renderer.

**Why:** Obsidian's table parser requires blank-line delimiters; without them, the pipe-syntax bleeds into prose and the table either renders broken or as raw text.

**Check pattern:** for every table (line starting with `|` followed by another line starting with `|---`), verify the line immediately before the table-header is blank AND the line immediately after the table-end is blank. Failing rows produce a `tables: needs blank line` finding.
