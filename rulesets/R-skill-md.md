# RULESET R-skill-md
include::
where:: `file:{anchor}/SKILL.md`
description:: the `SKILL.md` entry-point structure for a Claude Code skill

What `/audit` checks on a skill's `SKILL.md` entry point. Cardinality: one per skill anchor. Format of this set: [[DAS Ruleset]].

### RULE R-skill-md-01 — Frontmatter declares name / description / tools / user_invocable (checked)

`SKILL.md` opens with YAML frontmatter carrying the required fields `name`, `description`, `tools`, and `user_invocable`.

**Check pattern:** frontmatter parses; all four keys are present and non-empty.

### RULE R-skill-md-02 — Sections appear in the fixed order (checked)

The body follows the fixed sequence: Title (`# {slug} — {Full Name}`) → Brief → optional dispatch table → Actions → Reference → optional Topics → optional Scripts → Dispatch protocol.

**Check pattern:** the H1/H2 sequence is a subsequence of that fixed order; no foreign top-level section interleaves.

### RULE R-skill-md-03 — Ends with the 4-step dispatch protocol (checked)

`SKILL.md` ends with the standard dispatch protocol: parse the argument, look up the file in the Actions table, read + execute it, else show the dispatch table.

**Check pattern:** a `## Dispatch` section is the final section and enumerates the 4 steps.

### RULE R-skill-md-04 — Action files are lowercase-hyphenated `{name}-{action}.md` (checked)

Each action referenced in the Actions table is its own file named `{name}-{action}.md` (lowercase, hyphenated); reference-data files keep their original names — the casing distinguishes actions from reference data.

**Check pattern:** every Actions-table target resolves to a `{name}-*.md` file in the skill root.

### RULE R-skill-md-05 — A discipline (`user_invocable: false`) ships a parallel user doc and a no-slash H1 (checked)

A discipline carries `user_invocable: false`, no Actions table, a parallel user-facing doc at `docs/<domain>/DAS <Name>.md`, and a `# Name Discipline` user-doc H1 (no slash — a slash would imply it's invocable).

**Check pattern:** if `user_invocable: false`, assert the parallel `DAS <Name>.md` exists under `docs/` and its H1 is `# {Name} Discipline`.
