# Features — Audit Feature-Doc Cross-Linking + Content Integration

Verify every F-doc is **content-integrated** into the planning hierarchy (PRD + Design + Architecture bodies, where each exists). **Corrective by default** — when an unlinked F-doc is found, execute the same content-integration discipline that `/mint` runs (per [[F083 — Cross-Linking]] § Q4 resolution). Subject to the chunking cap (§ 5).

Per [[F083 — Cross-Linking]] — the invariant is: every F-doc's content has been integrated into the target docs' bodies (linking is NEVER a substitute for content inclusion). F-docs whose only inbound link is from `Unlinked PRD.md` count as satisfying the invariant; F-docs with NO inbound PRD link are findings AND get integrated by this skill.

## Modes

- **Default mode** (`/audit features`) — cheap link-check. Scans for unlinked F-docs. For each unlinked F-doc, runs the content-integration discipline (executes /mint's step 0 + step 0.5 on that F-doc). Subject to chunking cap.
- **`--force` mode** (`/audit features --force`) — deep content-integrity check. For every linked F-doc, re-verifies that the feature's content is actually present in the target doc bodies (not just listed in the Feature Docs table). Re-runs integration if content is missing or has drifted. Expensive; opt-in.
- **`--dry` mode** — emit findings without executing integration or writing a backlog entry. Substring match anywhere in args.

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

### 5. Build the findings table + chunking cap

| # | F-doc | Issue | Severity |
|---|---|---|---|
| 1 | [[F042 — Some feature]] | bucket: hygiene named but Hygiene PRD doesn't reference it | medium |
| 2 | [[F051 — Old chore]] | no bucket frontmatter + not in Unlinked PRD | high |
| 3 | [[F067 — Foo]] | bucket: nonexistent (broken frontmatter) | high |
| … | … | … | … |

Print the table to the console. **If `dry` substring is in args**, stop here — no execution and no backlog entry.

**Chunking cap (per [[F083]] Q3 resolution):**

Set `N = 3` (configurable; start here, tune by experience). Count the findings that warrant content integration (i.e., the corrective work — `no bucket frontmatter`, `bucket: hygiene named but unreferenced`, `bucket: unlinked but Unlinked PRD doesn't reference`, etc. — but NOT `bucket: nonexistent` which is broken-frontmatter and needs user fix).

- **If integration-eligible findings ≤ N**: proceed to § 6 — execute integration inline for all of them.
- **If integration-eligible findings > N**: proceed to § 6 — execute integration inline for the first N (ordered: high severity first, then by F-number ascending). File a backlog item with the remaining findings so they can be cranked through later.

### 6. Execute integration (default mode) OR re-verify (--force mode)

**Default mode** — for each integration-eligible finding (subject to chunking cap):
1. Run `/mint` step 0 (link tracking) — this wires the F-doc into the bucket PRD's Feature Docs table.
2. Run `/mint` step 0.5 (content integration) — this integrates the feature's content into PRD + Design + Architecture bodies.
3. Announce the integration inline: `**Integrated <F-doc> into <bucket>: <summary>.**`

After processing the inline batch (up to N features), if there are remaining unprocessed integration-eligible findings, write a backlog entry (§ 7) listing them.

For findings that are NOT integration-eligible (broken frontmatter — `bucket: nonexistent`), do not auto-fix — file them in the backlog entry only. User repairs frontmatter manually, then re-runs `/audit features`.

**`--force` mode** — additionally, for every linked F-doc (those already referenced from some PRD's Feature Docs table), run a content-presence check:
1. For each target doc type (PRD / Design / Architecture) where the F-doc could integrate, read the body
2. Compare against the feature spec for content presence — does the doc body reflect the feature's content, or is the integration empty/drifted?
3. If content is missing or has drifted, re-run /mint step 0.5 (integration) for that F-doc + target doc

`--force` is the deep-integrity check; default audit is cheap. Run `--force` when you suspect content drift after long edit cycles, or after `/mint` runs that may have skipped step 0.5.

### 7. Write the backlog entry (only when overflow or non-eligible findings exist)

Two cases trigger a backlog entry:

1. **Chunking overflow** — integration-eligible findings exceeded N; remainder needs to be cranked through later.
2. **Non-eligible findings** — broken frontmatter that requires user fix before audit can re-run cleanly.

Locate `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md`. Find the lowest unused B-number per [[CAB Backlog]] § Format. Append under `## Now` (or `## Ready` if all entries are immediately actionable):

```
- **B<n> — Features audit: <K> integrations pending + <M> needs-fix (<YYYY-MM-DD>)** [Ready] — work surfaced by `/audit features` exceeded chunking cap (N=3). Sub-bullets list remaining work.
  - [[F<n> — <title>]]: integration pending (bucket: <X>) — <severity>
  - ...
  - [[F<m> — <title>]]: NEEDS FIX — broken frontmatter (bucket: <bad-name>)
  - ...
```

Group sub-bullets by category (integration-pending first, then needs-fix), then by severity, then by F-number.

If there are zero remaining findings (everything was integrated inline AND no broken frontmatter), do **not** write an entry — print `features: clean — N integrated inline, no overflow` and stop.

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
