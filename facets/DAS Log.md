---
description: "the Log facet — dated entries capturing what happened on what day, in folder or single-file form"
---

# DAS Log
Facet spec defining the standardized format for an anchor's running narrative — dated entries capturing what happened on what day, in either folder form (default) or single-file form (minimal).

| -[[DAS Log]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Log](hook://p/DAS%20Log)  |
| --- | --- |
| Related | [[templates/log/{slug} Log.md\|log template (folder form)]],  [[templates/log/{{YYYY-MM-DD}} — {{short topic}}.md\|entry template]],  [[templates/log.md\|log template (single-file)]],  [[DAS Backlog]],  [[DAS Roadmap]],  [[DAS Anchor Page]],  [[DAS Track]],   |
| Examples | [[Disk Log\|folder-form (conformant)]],  [[SV Log\|folder-form (mixed-format entries)]],   |
| Rules | [[R-log]],  [[R-stream]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — The Log facet standardizes how any anchor records its running history. Instances live at `{slug} Log/` (folder form, default) or `{slug} Log.md` (single-file, minimal). **Cardinality: one per anchor** — each anchor has at most one Log. Folder form uses a `{slug} Log.md` dispatch page (entries newest-first); single-file form inlines entries as H2s. Entry filenames are ISO-date-prefixed with an em-dash (`YYYY-MM-DD — <topic>.<ext>`, per [[DAS stream]]). Logs capture what *happened*; spec/convention content belongs in dedicated facets.

description:: the Log facet — dated entries capturing what happened on what day

The Log facet specifies the format for an anchor's running narrative of work done over time. **Many anchors have a Log** — Disk, MED, SV, RR, Topic/BUY, Topic/COM, Topic/Doc/AWS, etc. — and the format is standardized across all of them so a reader who knows one knows them all.

A Log captures **what happened on what day**: per-session plans + outcomes + decisions, in chronological order. It is **not** a spec, a convention, a roadmap, a backlog, or a synthesis surface. Those belong in their own facets and are linked-to from log entries, not restated there.

**Cardinality: one per anchor** — each anchor has at most one Log (in either folder or single-file form).


**Site-specific extensions.** A vault may specialize this facet for its own user in that vault's agent-conventions page, in a section keyed to this facet's exact name. Nothing here assumes one exists; when it does, it refines this spec and never overrides a declared pointer. In this vault that page is [[Agent Conventions]] § DAS Log.

## Two forms — folder (default) and single-file (minimal)

### Folder form (default for active logs)

```
{slug} Log/
├── .anchor                                            ← folder-anchor marker (optional)
├── {slug} Log.md                                      ← dispatch page (this facet)
├── YYYY-MM-DD — <short topic>.md                      ← one entry per session
├── YYYY-MM-DD — <other topic>.md
├── YYYY-MM — <topic>.docx                             ← non-markdown artifacts OK
└── YYYY-MM-DD — <topic>.pdf
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

| -[[{slug} Log]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Track]] → [DAS Log](hook://p/DAS%20Log)<br>: <tagline> |
| --- | --- |
| [[YYYY-MM-DD — <topic>]] | <one-line summary> |
| [[YYYY-MM-DD — <topic>]] | <one-line summary> |
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

- **Entry filename:** ISO date prefix + em-dash + title — `YYYY-MM-DD — <short topic>.<ext>`. The pattern is owned by [[DAS stream]] § Dated entry-file naming (this facet cites, does not re-spell); the ISO prefix forces chronological sort. *Legacy space-separated instances (`YYYY-MM-DD <topic>` — e.g. [[Disk Log]], [[SV Log]]) are grandfathered and migrate on next touch (Q1 → A, 2026-07-17).*
- **Topic:** 3–7 words capturing the dominant theme of the session.
- **Ambiguous date precision:** `YYYY-MM — <topic>.<ext>` when only month is known; `YYYY — <topic>.<ext>` when only year is known.
- **Extension:** `.md` default; other formats (`.docx`, `.pptx`, `.pdf`, `.jpeg`) allowed when the artifact IS the entry.

## What does NOT belong in a Log

- **Specs / conventions / standards** — those live in `{slug} Conventions.md`, `{slug} Spec.md`, or the relevant DAS facet doc. Logs link to them; they don't restate them.
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

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the ruleset is [[R-log]]; worked examples are [[Disk Log]] / [[SV Log]].)*

- **Two artifacts, keep aligned** — the facet prose (top) and [[R-log]] (extracted 2026-07-12) must stay in sync: a prose shape change requires the matching `R-log-NN` change, and vice versa.
- **Inclusion test for new rules** — a rule belongs in `R-log` only if it is structural and applies to *every* anchor's Log (filename pattern, dispatch ordering, location, dispatch-page presence); anchor-local conventions (entry style, custom H2s) stay out, and per-anchor Brief restatements of these rules are forbidden by R-log-07.
- **Load-bearing rules** — R-log-06 (append-only dispatch) and R-log-07 (no per-anchor Brief restating Log rules) are the two most commonly violated by well-meaning edits; don't relax without an explicit feature ticket. The `description::` field near the top is required for facet indexing — don't move or delete it.
- **Conventions** — rules are numbered `R-log-NN` (zero-pad only past 9); link worked examples from *See also* rather than copying entry shapes inline.
