# FCT Log

Facet spec defining the standardized format for an anchor's running narrative — dated entries capturing what happened on what day, in either folder form (default) or single-file form (minimal).

description:: log facet — `{NAME} Log/` folder of dated entries documenting what happened on what day; dispatch page lists entries newest-first.

The Log facet specifies the format for an anchor's running narrative of work done over time. **Many anchors have a Log** — Disk, MED, SV, RR, Topic/BUY, Topic/COM, Topic/Doc/AWS, etc. — and the format is standardized across all of them so a reader who knows one knows them all.

A Log captures **what happened on what day**: per-session plans + outcomes + decisions, in chronological order. It is **not** a spec, a convention, a roadmap, a backlog, or a synthesis surface. Those belong in their own facets and are linked-to from log entries, not restated there.

## Two forms — folder (default) and single-file (minimal)

### Folder form (default for active logs)

```
{NAME} Log/
├── .anchor                                            ← folder-anchor marker (optional)
├── {NAME} Log.md                                      ← dispatch page (this facet)
├── YYYY-MM-DD <short topic>.md                        ← one entry per session
├── YYYY-MM-DD <other topic>.md
├── YYYY-MM <topic>.docx                               ← non-markdown artifacts OK
└── YYYY-MM-DD <topic>.pdf
```

The dispatch page `{NAME} Log.md` is a thin index — header dispatch table, then one row per entry, **newest first**. The actual narrative lives in the dated entry files.

### Single-file form (small / dormant logs)

```
{NAME} Log.md                                          ← all entries inline
```

Used when an anchor has very few log-worthy moments — entries become H2s inside one file. Migrate to folder form on the first multi-entry day.

**Migration is one-way:** once an anchor goes folder-form, it stays folder-form (don't fold back). Folder form is the canonical reference shape.

## Location

`{NAME}/{NAME} Log/` or `{NAME}/{NAME} Log.md` — directly under the anchor root, alongside Backlog, Design, Track, etc. Logs in sub-folders (e.g., `Topic/MED/MED Log/`) belong to *that* sub-anchor; each anchor scope has its own Log.

## Dispatch page shape (folder form)

The `{NAME} Log.md` file itself is body-only — no YAML frontmatter. First lines:

```markdown
# {NAME} Log
description:: dated entries — what happened on what day in the {NAME} anchor.

| -[[{NAME} Log]]- | : <tagline><br>→ <breadcrumb> → [{NAME} Log](hook://p/{NAME}%20Log) |
| --- | --- |
| [[YYYY-MM-DD <topic>]] | <one-line summary> |
| [[YYYY-MM-DD <topic>]] | <one-line summary> |
| ... | ... |

## What this is

One paragraph — what this log covers and what *doesn't* belong here.

## Sibling references

- [[{NAME} Conventions]] — anchor-local conventions (if any)
- [[{NAME} Backlog]] — open work items
- [[{NAME} <other peer facets>]]
```

Dispatch rows are **newest-first**. Append-only — never delete a row even if the entry was wrong; mark the entry as superseded inside its own body if needed.

## Entry shape (the dated files)

```markdown
# YYYY-MM-DD — <short topic>

<free-form body. No required H2s. Common shape:>

## What happened
Chronological narrative of the session.

## Decisions
What we decided to do (and why).

## Outstanding
What's next / unresolved.

## Related
Links to peer docs, features, backlog items.
```

H2s above are **suggestions, not required**. The body is freeform; the only invariant is "this captures what happened that day."

## Naming conventions

- **Entry filename:** `YYYY-MM-DD <short topic>.<ext>` — ISO date prefix forces chronological sort.
- **Topic:** 3–7 words capturing the dominant theme of the session.
- **Ambiguous date precision:** `YYYY-MM <topic>.<ext>` when only month is known; `YYYY <topic>.<ext>` when only year is known.
- **Extension:** `.md` default; other formats (`.docx`, `.pptx`, `.pdf`, `.jpeg`) allowed when the artifact IS the entry.

## What does NOT belong in a Log

- **Specs / conventions / standards** — those live in `{NAME} Conventions.md`, `{NAME} Spec.md`, or the relevant CAB facet doc. Logs link to them; they don't restate them.
- **Cross-session synthesis** — "here's what we learned over the last 3 months." Synthesis goes in dedicated synthesis docs, backlog notes, or roadmap commentary.
- **Open work items / TODOs** — those go in `{NAME} Backlog.md`. A log entry may *mention* what's outstanding, but the canonical list lives in the backlog.
- **Long-running tracking** — anything you'd update over multiple days. Log entries are immutable-after-write narratives; living tracking belongs in a tracking doc.
- **Briefs about how Logs work** — those rules live in this facet, not embedded as a Brief on every per-anchor Log.md.

## Trait applicability

Any anchor that benefits from a running narrative of dated work. Most active anchors carry one; pure spec anchors (e.g., a frozen reference) usually don't.

## Audit

`/audit log` (future) would flag the rules captured in `R-log` below — entry filename pattern, dispatch row presence, entries-don't-duplicate-spec, etc.

## See also

- [[CAB Backlog]] — sibling facet (open work, not narrative)
- [[FCT Roadmap]] — sibling facet (forward plan, not past narrative)
- [[FCT Anchor Page]] — the anchor's home; should link to `[[{NAME} Log]]`
- [[Disk Log]] — worked example (folder form, multiple entries)
- [[SV Log]] — worked example (mixed-format entries: .md / .docx / .pptx)


# RULESET R-log
include::
where:: {ANCHOR}/**/* Log.md
description:: Structural rules for the {NAME} Log facet — folder shape, entry filename pattern, dispatch dispatch, content scope.

Embedded ruleset for the Log facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-log-01 — Log path is `{NAME} Log/` or `{NAME} Log.md` (checked)
check:: log_path_exists

The log lives at `{NAME}/{NAME} Log/` (folder form) or `{NAME}/{NAME} Log.md` (single-file form). Not under Track, not under Docs, not at the vault root.

**Check pattern:** `ls "{anchor}/{NAME} Log"` resolves to a directory or `.md` file; no other location qualifies.

**Why:** Logs are anchor-scoped peers of Backlog and Roadmap; location predictability matters for the agent's discoverability and for users browsing anchor folders.

### RULE R-log-02 — Folder-form has a `{NAME} Log.md` dispatch file (checked)
check:: log_dispatch_file_present

When the log is folder-form, the folder contains a `{NAME} Log.md` whose H1 is `# {NAME} Log`.

**Check pattern:** if `{anchor}/{NAME} Log/` is a directory, then `{anchor}/{NAME} Log/{NAME} Log.md` exists and starts with `# {NAME} Log`.

**Why:** the dispatch file is the entry point — without it, the folder is a directory listing with no index.

### RULE R-log-03 — Entry filename matches `YYYY-MM-DD <topic>` (sampled)
check:: log_entry_filenames

Every entry file (any extension) matches one of these patterns:
- `^\d{4}-\d{2}-\d{2} .+\.(md|docx|pptx|pdf|jpeg|jpg|png|txt)$` (full date)
- `^\d{4}-\d{2} .+\.(md|...)$` (year-month only, allowed when day unknown)
- `^\d{4} .+\.(md|...)$` (year only, allowed when month unknown)

**Check pattern:** enumerate non-dispatch files in the log folder; assert each matches one of the three patterns.

**Why:** ISO-date prefix forces chronological sort; descriptive topic suffix makes the file self-identifying without opening. Logs without dates become unbrowsable as they grow.

### RULE R-log-04 — Entries don't restate spec / convention content (stated)

Log entries describe what *happened* on the day. They do not contain spec definitions, conventions, rules, or standards that belong in their own facet docs (Conventions, Spec, Backlog, etc.).

**Check pattern:** manual review. Future: heuristic flag when an entry contains an H2 like `## Convention`, `## Spec`, `## Rules`, `## Format` — those headers usually indicate displaced spec content.

**Why:** specs evolve and need to be the single source of truth. If a Log entry restates a spec, the entry becomes silently stale when the spec changes.

### RULE R-log-05 — Dispatch table is newest-first (sampled)
check:: log_dispatch_newest_first

The `{NAME} Log.md` dispatch table lists entries with the **newest entry at top**, working backwards in time.

**Check pattern:** parse dispatch-row wiki-links to extract dates from `[[YYYY-MM-DD ...]]`; assert monotonically non-increasing.

**Why:** the reader's primary query is "what happened recently?" Reverse-chronological ordering puts the answer first; chronological ordering buries it.

### RULE R-log-06 — Dispatch table is append-only (stated)

Once a row is added to the dispatch table for an entry, it stays. Don't delete rows even if the entry was wrong. Supersession is noted *inside* the entry body, not by removing the row.

**Check pattern:** git history — entries that disappear from the dispatch table without the underlying file being moved are suspect.

**Why:** Logs are historical record. Deleted rows are revisionist; they make it impossible to reconstruct what was thought when.

### RULE R-log-07 — No `Brief` carrying log-format rules (checked)
check:: regex_absent ^#\s+BRIEF

The `{NAME} Log.md` dispatch page does NOT contain a `# BRIEF` second-H1 (or `Brief` sidecar file) that restates how Logs work. The rules for how Logs work live in this facet (CAB Log), not on every per-anchor Log dispatch page.

**Check pattern:** grep `{NAME} Log.md` for `^# BRIEF` or `^# Brief`. If present and its body contains general log-format prescriptions (filename pattern, body convention, "don't duplicate spec content"), flag for migration to point at [[FCT Log]] instead.

**Why:** the Brief discipline is for anchor-specific operational content, not for restating shared facet rules. Per-anchor restatement of facet rules drifts when the facet evolves.

### RULE R-log-08 — Anchor page links to `[[{NAME} Log]]` (sampled)
check:: log_anchor_page_link

The anchor's main page (`{NAME}.md`) carries a dispatch row pointing at `[[{NAME} Log]]`.

**Check pattern:** grep `{anchor}/{NAME}.md` for `\[\[{NAME} Log\]\]`.

**Why:** without it, the Log is one click further from anchor-page-as-router; readers miss it.

### RULE R-log-09 — Sub-anchor logs are scoped to their sub-anchor (stated)

A sub-anchor with its own Log uses the sub-anchor's name (e.g., `MED Heart Log/`, `MED Heart Log.md`), not the parent's. Logs do not cross anchor boundaries.

**Check pattern:** for each `* Log.md` found, walk up to the nearest `.anchor` file; assert the log's `{NAME}` prefix matches that anchor's name (or its slug/RID).

**Why:** Logs are anchor-scoped. A sub-anchor entry inside a parent's log loses its scoping and is harder to find later.

# BRIEF

- **This is the canonical Log facet spec.** Authority for how `{NAME} Log/` folders and `{NAME} Log.md` files are shaped across every anchor in the vault — edits here change the rules for all anchors that carry a Log.
- **Two artifacts in one file** — the facet prose (top half) and `RULESET R-log` (bottom half, embedded per F133). Keep both halves aligned: when prose changes a shape rule, the corresponding `R-log-NN` rule must also update, and vice versa.
- **What does NOT belong here:** per-anchor log content (lives in `{NAME} Log/`), Brief-style restatements of these rules on per-anchor dispatch pages (forbidden by R-log-07), or convention/spec material that belongs in sibling facets like [[CAB Backlog]] or [[FCT Roadmap]].
- **Inclusion test for new rules:** a rule belongs in `R-log` only if it is structural and applies to *every* anchor's Log — filename pattern, dispatch ordering, location, dispatch-page presence. Anchor-local conventions (entry style, custom H2s) stay out.
- **Naming / linking conventions** — refer to anchors as `{NAME}` placeholder in prose and rule text; link worked examples via `[[Disk Log]]` / `[[SV Log]]` style wiki-links; rules are numbered `R-log-NN` with zero-padding only if the set exceeds 9 (currently single-digit).
- **Load-bearing constraints** — R-log-06 (append-only dispatch) and R-log-07 (no per-anchor Brief restating Log rules) are the two rules most commonly violated by well-meaning edits; don't relax them without an explicit feature ticket. The `description::` Dataview field on line 2 is required for facet indexing — don't move or delete it.
- **Don't pile worked examples inline** — link to `[[Disk Log]]`, `[[SV Log]]`, etc. from the *See also* section rather than copying entry shapes into this file.
