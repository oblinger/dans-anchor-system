# RULESET R-fct-claude
include::
where:: `**/CLAUDE.md`
description:: The rules every anchor-level `CLAUDE.md` instance must satisfy — location, shape, and agentic-project header discipline.

### RULE R-fct-claude-01 — File sits at the anchor root
description:: A CLAUDE.md file must live at the anchor folder root (depth 0), not inside a subfolder — the harness only auto-loads from the opened folder.
when:: write:markdown
if:: `file.path != anchor.root.rstrip('/') + '/CLAUDE.md'`
This `CLAUDE.md` is not at the anchor root — move it to `{anchor-root}/CLAUDE.md` so the Claude Code harness finds it on startup.

**Why:** the harness only auto-loads `CLAUDE.md` from the folder it's opened in; a misplaced file is silently ignored.

### RULE R-fct-claude-02 — Pilot role declaration appears first, or is absent
description:: When a Pilot declaration is present it must start on line 1; no content may precede it.
when:: write:markdown
if:: `'You are the Pilot' in file.text and not file.lines[0].startswith('You are the Pilot')`
A Pilot role declaration was found but it does not start on line 1 — move it to the very first line(s) of `CLAUDE.md`. The harness reads top-to-bottom; text before the Pilot declaration is missed by context-compaction logic.

**Why:** the harness reads `CLAUDE.md` top-to-bottom on startup; a Pilot declaration buried after other text is missed by context-compaction logic.

### RULE R-fct-claude-03 — Mission section is present
description:: Every CLAUDE.md carries a ## Mission section with at least one non-empty paragraph explaining the agent's job.
when:: write:markdown
if:: `not file.section('Mission') or not file.section('Mission').strip()`
This `CLAUDE.md` is missing a `## Mission` section, or the section is empty — add one with at least a short paragraph explaining what the agent's job is in this folder.

**Why:** the mission is the agent's primary orientation; without it the agent infers from context and often draws the wrong scope.

### RULE R-fct-claude-04 — No F060 dispatch-table at the file top
description:: CLAUDE.md is consumed by the Claude Code harness, not by anchor-doc readers — the F060 dispatch-table rule does not apply; no breadcrumb or dispatch table belongs here.
when:: write:markdown
if:: `bool(re.search(r'^:>>', file.text, re.M))`
This `CLAUDE.md` opens with a `:>>` breadcrumb — remove it. `CLAUDE.md` is consumed by the Claude Code harness, not by anchor-doc readers, so the F060 dispatch-table rule does not apply. The file top belongs to the Pilot declaration or mission.

**Why:** a dispatch table in `CLAUDE.md` would confuse the harness and occupy the slot that belongs to the Pilot declaration or mission.
