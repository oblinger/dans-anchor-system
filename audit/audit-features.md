# Features — Audit Feature-Doc Cross-Linking

Verify every F-doc in `SKA Features/` is referenced from at least one bucket PRD's `## Feature Docs` table. **Reports findings only.** Fix work goes into a backlog entry; no F-docs or PRDs are modified.

Per [[F083 — Cross-Linking]] — the invariant is: every F-doc must be reachable from the planning hierarchy. F-docs whose only inbound link is from `Unlinked PRD.md` count as satisfying the invariant; F-docs with NO inbound PRD link are findings.

## Workflow

### 1. Detect the anchor + federated structure

Walk up from `cwd` to find `.anchor`. If none, say so and stop. Then check:

- **Features folder exists?** Locate `{anchor}/Docs/Plan/{NAME} Features/` (or `{anchor}/{NAME} Docs/{NAME} Plan/{NAME} Features/`). Missing → report `features: no Features folder — skip` and stop.
- **Federated bucket PRDs exist?** Look for any `{anchor}/Docs/Plan/<Bucket>/<Bucket> PRD.md` files. If NONE exist → report `features: anchor not on federated PRD structure — skip` and stop. This anchor hasn't adopted [[F083 — Cross-Linking]]; the audit doesn't apply.

Both gates must pass before proceeding.

### 2. Enumerate F-docs

List every `F<NNN> — *.md` file in the Features folder. For each, extract:
- F-number
- Title (from the H1 or the filename after the `— `)
- `bucket:` frontmatter value (single string or list; absent → treat as `unlinked`)

### 3. Enumerate bucket PRDs

List every `{Bucket} PRD.md` under `{anchor}/Docs/Plan/{Bucket}/` (e.g., `SKA Plan/Hygiene/Hygiene PRD.md`). For each PRD:
- Read the `## Feature Docs` H2 section
- Parse the table within it
- Extract the F-doc wiki-links referenced (the link in the first column of each non-empty row)

Build a map: `bucket_name → set of F-numbers referenced`.

### 4. Check the invariant — for each F-doc

For each F-doc enumerated in step 2:
- **Bucket-listed but unreferenced.** If the F-doc names `bucket: hygiene` but `Hygiene PRD.md`'s Feature Docs table doesn't reference it → finding (severity: medium).
- **No bucket frontmatter AND not in Unlinked PRD.** Finding (severity: high — fully orphaned).
- **Bucket frontmatter names a bucket that doesn't exist.** E.g., `bucket: nonexistent` → finding (severity: high — broken frontmatter).
- **Bucket frontmatter `unlinked` but Unlinked PRD doesn't reference it.** Finding (severity: medium — wiring incomplete).

### 5. Build the findings table

| # | F-doc | Issue | Severity |
|---|---|---|---|
| 1 | [[F042 — Some feature]] | bucket: hygiene named but Hygiene PRD doesn't reference it | medium |
| 2 | [[F051 — Old chore]] | no bucket frontmatter + not in Unlinked PRD | high |
| 3 | [[F067 — Foo]] | bucket: nonexistent (broken frontmatter) | high |
| … | … | … | … |

Print the table to the console. **If `dry` substring is in args**, stop here — print "dry-run — no backlog entry written."

### 6. Write the backlog entry

Locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Find the lowest unused B-number per [[CAB Backlog]] § Format. Append under `## Upcoming`:

```
- **B<n> — Features audit: <N> findings (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit features`. Sub-bullets are candidate splits if this needs to be broken up.
  - [[F<n> — <title>]]: <issue> — <severity>
  - …
```

Group sub-bullets by severity (high → medium), then by F-number ascending.

If there are zero findings, do **not** write an entry — print `features: clean — no entry written` and stop.

## Stat post

```bash
skl-stat add "Review" "[[{NAME}]]" "Audit: features — <N> findings"
```

Use `Done` + `Audit: features — clean` if zero findings.

## Notes on idempotence

Re-running `/audit features` after fixes should produce **strictly fewer findings** (or zero). If new findings appear that weren't there before, an F-doc was added or a PRD wiring was undone since the last run.

## Relationship to `/audit q`

`/audit features` is **orthogonal to `/audit q`**:
- `/audit q` verifies the Q.md dashboard is internally consistent (banner counts, link integrity, bracket-section coherence). Output is Q.md.
- `/audit features` verifies feature docs are woven into the planning narrative (PRDs reference them). Output is the planning hierarchy.

These are different invariants over different artifacts; don't merge them.
