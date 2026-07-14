# RULESET R-fct-system-design
include::
where:: `file: **/{slug} Docs/{slug} Plan/{slug} System Design.md`
description:: Rules every `{slug} System Design.md` instance must satisfy — location, top-of-doc shape, required sections, and currency discipline.

### RULE R-fct-system-design-01 — Location is `{slug} Docs/{slug} Plan/` (checked)
The System Design file lives at `{slug} Docs/{slug} Plan/{slug} System Design.md` — not at the anchor root, not under `{slug} Docs/` directly.
**Check pattern:** file path matches `*/{slug} Docs/{slug} Plan/{slug} System Design.md`.
**Why:** consistent location allows skills and audits to find and link the doc without per-anchor config.

### RULE R-fct-system-design-02 — Top-of-doc shape: YAML + H1 + dispatch table (checked)
The file opens with YAML frontmatter, then `# {slug} System Design`, then a dispatch-table placeholder — in that order, before any topic tables (TOC, Components, Data Model, Decisions).
**Check pattern:** the first three structural blocks are frontmatter → H1 → a `| … | … |` table row.
**Why:** F060 top-of-doc convention; topic tables below the dispatch table per F060 § Q5.

### RULE R-fct-system-design-03 — Required sections present (checked)
The document contains at minimum four H2 sections: `Architecture Overview`, `Components`, `Data Model`, and `Decisions`.
**Check pattern:** all four headings are present (exact names or close paraphrases); none are empty.
**Why:** these four sections are the load-bearing structure of a System Design; omitting one leaves the design incomplete.

### RULE R-fct-system-design-04 — Current-spec-only discipline (stated)
The document records the *current* architecture, not a changelog. Historical decisions belong in [[DAS Discussion]] (rationale) or [[DAS Decisions]] (decision log). The Decisions table records *what was decided*, not the deliberation.
**Check pattern:** no `## History` or changelog section; the Decisions table rows are statements, not thread summaries.
**Why:** mixing current spec with historical narrative makes the doc unreliable as a reference for the active design.
