# RULESET R-fct-outputs
include:: [[R-stream]]
where:: `file:{anchor}/**/* Outputs.md, !**/DAS *.md`
where-note:: **Deliberately location-independent** (repaired 2026-08-05, [[Tink Backlog#^T373|T373]]). The selector previously encoded the retired location and so matched **0** files vault-wide — including the one live instance it was written to govern. See the same note on [[R-fct-system-design]]: the selector finds the doc, R-01 judges its location.
description:: The rules every Outputs folder and its dispatch page must satisfy — location, naming, dispatch-page shape, and individual output-file format.

### RULE R-fct-outputs-01 — Outputs live under `{slug} Track/` (checked)
The Outputs folder lives at `{slug} Track/{slug} Outputs/`, not at the anchor root or elsewhere. Outputs are produced work, so they file with tracking rather than with design — which is where the live instances already sat when `{slug} Docs/` was retired ([[Tink Backlog#^T514|T514]]).
**Check pattern:** the dispatch page path matches `*/{slug} Track/{slug} Outputs/{slug} Outputs.md`.
**Why:** consistent location lets skills and audits find the zone without per-anchor config. Worked instance: `MUX Track/MUX Outputs/MUX Outputs.md`.

### RULE R-fct-outputs-02 — Individual output files use `{YYYY-MM-DD} {Name}.md` (checked)
Each output file uses `YYYY-MM-DD` as the date prefix and no slug prefix; the name follows the date.
**Check pattern:** filenames inside `{slug} Outputs/` (other than the dispatch page) match `^\d{4}-\d{2}-\d{2} .+\.md$`.
**Why:** the date provides uniqueness within the folder; a slug prefix is redundant and would break the `stat` command's naming contract.

### RULE R-fct-outputs-03 — Dispatch page is H1 + placeholder + reverse-chrono table (sampled)
`{slug} Outputs.md` contains: an H1 (`# {slug} Outputs`), the standard F060 dispatch-table placeholder, then a reverse-chronological table with `Date | Output | Status` columns.
**Check pattern:** the dispatch page has an H1, the two-row placeholder table, and a `| Date |` table.
**Why:** the shape is prescriptive so the `stat` command can reliably update the table and agents can parse it consistently.

### RULE R-fct-outputs-04 — Individual output files carry top-of-doc header (sampled)
Each output file opens with the standard top-of-doc header (a `# {date} {name}` H1, then the two-row dispatch placeholder — a `| -[[{date} {name}]]- | |` row + separator row) before the report body.
**Check pattern:** the first non-empty lines of each output file are an H1 followed by a two-row table.
**Why:** standard top-of-doc navigation — consistent with all other anchor pages.
