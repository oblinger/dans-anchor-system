# RULESET R-fct-outputs
include::
where:: `file: **/{slug} Docs/{slug} Plan/{slug} Outputs/{slug} Outputs.md`
description:: The rules every Outputs folder and its dispatch page must satisfy — location, naming, dispatch-page shape, and individual output-file format.

### RULE R-fct-outputs-01 — Outputs live inside the Plan subtree (checked)
The Outputs folder lives at `{slug} Docs/{slug} Plan/{slug} Outputs/`, not at the anchor root or elsewhere.
**Check pattern:** the dispatch page path matches `*/{slug} Docs/{slug} Plan/{slug} Outputs/{slug} Outputs.md`.
**Why:** the Outputs zone is part of the planning documentation tree; placing it elsewhere breaks the `stat` command's path assumptions.

### RULE R-fct-outputs-02 — Individual output files use `{YYYY-MM-DD} {Name}.md` (checked)
Each output file uses `YYYY-MM-DD` as the date prefix and no slug prefix; the name follows the date.
**Check pattern:** filenames inside `{slug} Outputs/` (other than the dispatch page) match `^\d{4}-\d{2}-\d{2} .+\.md$`.
**Why:** the date provides uniqueness within the folder; a slug prefix is redundant and would break the `stat` command's naming contract.

### RULE R-fct-outputs-03 — Dispatch page is H1 + placeholder + reverse-chrono table (sampled)
`{slug} Outputs.md` contains: an H1 (`# {slug} Outputs`), the standard F060 dispatch-table placeholder, then a reverse-chronological table with `Date | Output | Status` columns.
**Check pattern:** the dispatch page has an H1, the two-row placeholder table, and a `| Date |` table.
**Why:** the shape is prescriptive so the `stat` command can reliably update the table and agents can parse it consistently.

### RULE R-fct-outputs-04 — Individual output files carry top-of-doc header (sampled)
-[[{date} {name}]]-` + separator row) before the report body.
**Check pattern:** the first non-empty lines of each output file are an H1 followed by a two-row table.
**Why:** standard top-of-doc navigation — consistent with all other anchor pages.
