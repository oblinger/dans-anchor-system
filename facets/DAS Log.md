---
description: "the Log facet — dated entries capturing what happened on what day, in folder or single-file form"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Track]] → [FCT Log](hook://p/DAS%20Log)
# FCT Log
Facet spec defining the standardized format for an anchor's running narrative — dated entries capturing what happened on what day, in either folder form (default) or single-file form (minimal).

**Related:** [[FCT Backlog]],  [[DAS Roadmap]],  [[DAS Anchor Page]],  [[DAS Track]]
**Examples:** [[Disk Log\|folder-form (conformant)]],  [[SV Log\|folder-form (mixed-format entries)]]

| Table of Contents |  |
|---|---|
| [[#Two forms — folder (default) and single-file (minimal)]] |  |
| [[#Location]] |  |
| [[#Dispatch page shape (folder form)]] |  |
| [[#What this is]] |  |
| [[#Sibling references]] |  |
| [[#Entry shape (the dated files)]] |  |
| [[#What happened]] |  |
| [[#Decisions]] |  |
| [[#Outstanding]] |  |
| [[#Related]] |  |
| [[#Naming conventions]] |  |
| [[#What does NOT belong in a Log]] |  |
| [[#Trait applicability]] |  |
| [[#Audit]] |  |
| [[#See also]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — The Log facet standardizes how any anchor records its running history. Instances live at `{slug} Log/` (folder form, default) or `{slug} Log.md` (single-file, minimal). **Cardinality: one per anchor** — each anchor has at most one Log. Folder form uses a `{slug} Log.md` dispatch page (entries newest-first); single-file form inlines entries as H2s. Entry filenames are ISO-date-prefixed (`YYYY-MM-DD <topic>.<ext>`). Logs capture what *happened*; spec/convention content belongs in dedicated facets.

description:: the Log facet — dated entries capturing what happened on what day

The Log facet specifies the format for an anchor's running narrative of work done over time. **Many anchors have a Log** — Disk, MED, SV, RR, Topic/BUY, Topic/COM, Topic/Doc/AWS, etc. — and the format is standardized across all of them so a reader who knows one knows them all.

A Log captures **what happened on what day**: per-session plans + outcomes + decisions, in chronological order. It is **not** a spec, a convention, a roadmap, a backlog, or a synthesis surface. Those belong in their own facets and are linked-to from log entries, not restated there.

**Cardinality: one per anchor** — each anchor has at most one Log (in either folder or single-file form).

## Two forms — folder (default) and single-file (minimal)

### Folder form (default for active logs)

```
{slug} Log/
├── .anchor                                            ← folder-anchor marker (optional)
├── {slug} Log.md                                      ← dispatch page (this facet)
├── YYYY-MM-DD <short topic>.md                        ← one entry per session
├── YYYY-MM-DD <other topic>.md
├── YYYY-MM <topic>.docx                               ← non-markdown artifacts OK
└── YYYY-MM-DD <topic>.pdf
```

The dispatch page `{slug} Log.md` is a thin index — header dispatch table, then one row per entry, **newest first**. The actual narrative lives in the dated entry files.

### Single-file form (small / dormant logs)

```
{slug} Log.md                                          ← all entries inline
```

Used when an anchor has very few log-worthy moments — entries become H2s inside one file. Migrate to folder form on the first multi-entry day.

**Migration is one-way:** once an anchor goes folder-form, it stays folder-form (don't fold back). Folder form is the canonical reference shape.

## Location

`{slug}/{slug} Log/` or `{slug}/{slug} Log.md` — directly under the anchor root, alongside Backlog, Design, Track, etc. Logs in sub-folders (e.g., `Topic/MED/MED Log/`) belong to *that* sub-anchor; each anchor scope has its own Log.

## Dispatch page shape (folder form)

The `{slug} Log.md` file itself is body-only — no YAML frontmatter. First lines:

```markdown
# {slug} Log
description:: dated entries — what happened on what day in the {Full Name} anchor.

| -[[{slug} Log]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Log](hook://p/FCT%20Log)<br>: <tagline> |
| --- | --- |
| [[YYYY-MM-DD <topic>]] | <one-line summary> |
| [[YYYY-MM-DD <topic>]] | <one-line summary> |
| ... |  |

## What this is

One paragraph — what this log covers and what *doesn't* belong here.

## Sibling references

- [[{slug} Conventions]] — anchor-local conventions (if any)
- [[{slug} Backlog]] — open work items
- [[{slug} <other peer facets>]]
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

- **Specs / conventions / standards** — those live in `{slug} Conventions.md`, `{slug} Spec.md`, or the relevant CAB facet doc. Logs link to them; they don't restate them.
- **Cross-session synthesis** — "here's what we learned over the last 3 months." Synthesis goes in dedicated synthesis docs, backlog notes, or roadmap commentary.
- **Open work items / TODOs** — those go in `{slug} Backlog.md`. A log entry may *mention* what's outstanding, but the canonical list lives in the backlog.
- **Long-running tracking** — anything you'd update over multiple days. Log entries are immutable-after-write narratives; living tracking belongs in a tracking doc.
- **Briefs about how Logs work** — those rules live in this facet, not embedded as a Brief on every per-anchor Log.md.

## Trait applicability

Any anchor that benefits from a running narrative of dated work. Most active anchors carry one; pure spec anchors (e.g., a frozen reference) usually don't.

## Audit

`/audit log` (future) would flag the rules captured in `R-log` below — entry filename pattern, dispatch row presence, entries-don't-duplicate-spec, etc.

## See also

- [[DAS Backlog]] — sibling facet (open work, not narrative)
- [[DAS Roadmap]] — sibling facet (forward plan, not past narrative)
- [[DAS Anchor Page]] — the anchor's home; should link to `[[{slug} Log]]`
- [[Disk Log]] — worked example (folder form, multiple entries)
- [[SV Log]] — worked example (mixed-format entries: .md / .docx / .pptx)

# RULESET R-log
include::
where:: `{anchor}/**/* Log.md`
description:: Structural rules for the {slug} Log facet — folder shape, entry filename pattern, dispatch dispatch, content scope.

Embedded ruleset for the Log facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via `R-facet` umbrella.

### RULE R-log-01 — Log path is `{slug} Log/` or `{slug} Log.md` (checked)
check:: log_path_exists

The log lives at `{slug}/{slug} Log/` (folder form) or `{slug}/{slug} Log.md` (single-file form). Not under Track, not under Docs, not at the vault root.

**Check pattern:** `ls "{anchor}/{slug} Log"` resolves to a directory or `.md` file; no other location qualifies.

**Why:** Logs are anchor-scoped peers of Backlog and Roadmap; location predictability matters for the agent's discoverability and for users browsing anchor folders.

### RULE R-log-02 — Folder-form has a `{slug} Log.md` dispatch file (checked)
check:: log_dispatch_file_present

When the log is folder-form, the folder contains a `{slug} Log.md` whose H1 is `# {slug} Log`.

**Check pattern:** if `{anchor}/{slug} Log/` is a directory, then `{anchor}/{slug} Log/{slug} Log.md` exists and starts with `# {slug} Log`.

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

The `{slug} Log.md` dispatch table lists entries with the **newest entry at top**, working backwards in time.

**Check pattern:** parse dispatch-row wiki-links to extract dates from `[[YYYY-MM-DD ...]]`; assert monotonically non-increasing.

**Why:** the reader's primary query is "what happened recently?" Reverse-chronological ordering puts the answer first; chronological ordering buries it.

### RULE R-log-06 — Dispatch table is append-only (stated)

Once a row is added to the dispatch table for an entry, it stays. Don't delete rows even if the entry was wrong. Supersession is noted *inside* the entry body, not by removing the row.

**Check pattern:** git history — entries that disappear from the dispatch table without the underlying file being moved are suspect.

**Why:** Logs are historical record. Deleted rows are revisionist; they make it impossible to reconstruct what was thought when.

### RULE R-log-07 — No `Brief` carrying log-format rules (checked)
check:: regex_absent ^#\s+BRIEF

The `{slug} Log.md` dispatch page does NOT contain a `# BRIEF` second-H1 (or `Brief` sidecar file) that restates how Logs work. The rules for how Logs work live in this facet (CAB Log), not on every per-anchor Log dispatch page.

**Check pattern:** grep `{slug} Log.md` for `^# BRIEF` or `^# Brief`. If present and its body contains general log-format prescriptions (filename pattern, body convention, "don't duplicate spec content"), flag for migration to point at [[DAS Log]] instead.

**Why:** the Brief discipline is for anchor-specific operational content, not for restating shared facet rules. Per-anchor restatement of facet rules drifts when the facet evolves.

### RULE R-log-08 — Anchor page links to `[[{slug} Log]]` (sampled)
check:: log_anchor_page_link

The anchor's main page (`{slug}.md`) carries a dispatch row pointing at `[[{slug} Log]]`.

**Check pattern:** grep `{anchor}/{slug}.md` for `\[\[{slug} Log\]\]`.

**Why:** without it, the Log is one click further from anchor-page-as-router; readers miss it.

### RULE R-log-09 — Sub-anchor logs are scoped to their sub-anchor (stated)

A sub-anchor with its own Log uses the sub-anchor's name (e.g., `MED Heart Log/`, `MED Heart Log.md`), not the parent's. Logs do not cross anchor boundaries.

**Check pattern:** for each `* Log.md` found, walk up to the nearest `.anchor` file; assert the log's `{slug}` prefix matches that anchor's name (or its slug).

**Why:** Logs are anchor-scoped. A sub-anchor entry inside a parent's log loses its scoping and is harder to find later.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the co-located ruleset is `RULESET R-log`; worked examples are [[Disk Log]] / [[SV Log]].)*

- **Two artifacts, keep aligned** — the facet prose (top) and `RULESET R-log` (bottom, embedded per F133) must stay in sync: a prose shape change requires the matching `R-log-NN` change, and vice versa.
- **Inclusion test for new rules** — a rule belongs in `R-log` only if it is structural and applies to *every* anchor's Log (filename pattern, dispatch ordering, location, dispatch-page presence); anchor-local conventions (entry style, custom H2s) stay out, and per-anchor Brief restatements of these rules are forbidden by R-log-07.
- **Load-bearing rules** — R-log-06 (append-only dispatch) and R-log-07 (no per-anchor Brief restating Log rules) are the two most commonly violated by well-meaning edits; don't relax without an explicit feature ticket. The `description::` field near the top is required for facet indexing — don't move or delete it.
- **Conventions** — rules are numbered `R-log-NN` (zero-pad only past 9); link worked examples from *See also* rather than copying entry shapes inline.
