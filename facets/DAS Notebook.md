---
description: "the Notebook facet — a per-activity folder of numbered dash-entries (docs, data, figures) plus a namesake narrative that replays the experiment top-to-bottom"
group: folder
---

| -[[DAS Notebook]]- | → [[DAS]] → [[FCT]] → [DAS Notebook](hook://p/DAS%20Notebook)  |
| --- | --- |
| Related | [[DAS Log]],  [[DAS Subs]],  [[DAS Backlog]],   |
| Examples | [[A2X012 - Game Breaks\|A2X012 - Game Breaks (first live instance)]],   |
| Script | [[skills/notebook/scripts/nb\|nb]] — the facet's one write surface (`nb append`, `nb mint`) |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Notebook
Facet spec for experiment notebooks — an append-only folder of numbered artifacts with a single narrative doc a human reads top-to-bottom, written through one script.

**TLDR** — A notebook is the ordered artifact stream of one activity: every figure, data file, and finding an agent produces, appended as numbered **dash-entries**. Notebooks live in a per-anchor stream folder `{slug} Notebook/`, one folder per notebook named `{PREFIX} - {Title}`, where `{PREFIX}` is a fresh `{SLUG}{NNN}` number from the anchor's **shared number namespace** (features, subprojects, and notebooks all draw from one pool; numbers are never reused — `nb mint` prints the first available). The folder's namesake doc is the narrative: one H2 per entry, machine-written by `nb append`. It is ordered like a Jupyter notebook, but it is just files in a folder.

## Shape

```
{slug} Notebook/                       <- the anchor's stream of notebooks
  A2X012 - Game Breaks/                <- one notebook: {PREFIX} - {Title}
    A2X012 - Game Breaks.md            <- namesake narrative (sorts first: space < hyphen)
    A2X012-001 first pass.md           <- entry 001's own doc
    A2X012-001 leaderboard.png         <- entry 001's data / figures
    A2X012-002 second pass.md
```

- **Dash-entries** are three-digit, zero-padded, monotonic (`-001` … `-999`); every file of an entry carries the same `{PREFIX}-NNN` prefix, so the folder listing orders and groups itself.
- Each entry **always has a title and its own doc**; optionally a summary (1–3 sentences) and any number of data files. **Figures** are data files that additionally embed inline in the narrative.
- The **narrative** (namesake doc, marked `<!-- notebook -->`) carries one block per entry: an H2 whose text is `NNN — Title` and whose link target is the entry doc, the summary sentences, then figure embeds. Reading it top-to-bottom replays the experiment.
- **Entry blocks are electric** — `nb append` regenerates a block wholesale on every touch. Durable prose belongs in the entry's own doc, never hand-typed into the narrative.

## The script — `nb`

`nb append` is the entire write surface; there is no init verb (first append creates folder + narrative) and no render verb (the narrative is maintained incrementally).

```
nb append <notebook-dir> [--num NNN] [--title T] [--summary S]
          [--body notes.md] [--data f ...] [--fig f ...]
nb mint <path-inside-anchor>
```

- Omit `--num` → the next entry number is minted; give `--num` → that entry is extended.
- **Keyword-overwrite semantics**: `--title` / `--summary` / `--body` replace (a title change renames the entry doc); `--data` / `--fig` accumulate, same basename overwrites. A new entry requires `--title`; everything else is optional on any call.
- **Figure sizing by count**: one figure → full width; two → `|1000` each; three or more → `|500` each, three per row. The script annotates display width only — generating scripts should render sources at roughly 3000 / 1000 / 500 px wide for the three cases.
- `--data` markdown files are unsupported in v1 (they would collide with entry docs); fold such content into `--body`.
- `nb mint` walks up to `.anchor`, reads the declared `slug:`, scans backlog F/T row numbers plus every `{SLUG}NNN`-named file or folder in the tree, and prints max+1.

## Boundaries

- **Notebook vs [[DAS Log|Log]]**: a Log is the anchor's dated session narrative (one per anchor, keyed by day); a Notebook is the artifact stream of one *activity* (many per anchor, keyed by entry number). Findings prose can live in both; data lives in the notebook.
- A notebook folder is **not a sub-anchor** — it takes no functional `.anchor` and no dispatch table, exactly like Backlog folders; the `<!-- notebook -->` marker on the namesake is the machine-readable discriminator (the [[R-doc-structure]] scanner lesson).
- No per-anchor index of notebooks beyond the stream folder itself; the owning work item's doc links its notebook.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec is the body above; the write surface is [[skills/notebook/scripts/nb|nb]]; the first worked example is [[A2X012 - Game Breaks]].)*

- **The script is the spec's enforcement** — there is deliberately no R-notebook ruleset yet (soak first). If prose and `nb`'s behavior diverge, the divergence is a bug in one of them; fix the pair, never document around it.
- **Entry blocks are electric** — never "repair" a narrative block by hand and never teach anyone to; every block regenerates on the next `nb append` touching that entry. Durable prose goes in the entry's own doc.
- **Numbering is shared and never reused** (Dan's ruling, 2026-08-16, [[TINK334 - Notebook facet - append-only experiment notebooks|F334]] Q2): a `{SLUG}{NNN}` may be a feature doc, a subproject, or a notebook, and `nb mint` computes first-available across all of them plus backlog F/T rows. Do not add a notebook-private sequence.
- **No `.anchor`, no dispatch table** in notebook folders — the `<!-- notebook -->` marker on the namesake is the discriminator, mirroring the state:backlog stamp lesson; if HookAnchor starts minting `.anchor` files here, extend the audit-plan discriminators rather than deleting markers.
