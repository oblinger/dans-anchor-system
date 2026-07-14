# DAS Disciplines Brief

Editing-and-maintenance brief for [[DAS Disciplines]]. Read before adding a new discipline, restructuring the catalog, or auditing what belongs here.

| -[[DAS Disciplines Brief]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Disciplines Brief](hook://p/DAS%20Disciplines%20Brief) |
| --- | --- |
| Related | [[DAS Disciplines]],  [[DAS Brief]],  [[DAS Facets]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[facets/DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS Plan Dispatch]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS Track Dispatch]],  [[DAS TSK User Guide]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

*Conceptual source: [[PKM]] (under [[THREADS]]) — disciplines codify the anchoring / hook-naming / local-global patterns.*

## What a discipline is

A **discipline** is a constrained way of working — a pattern we follow because we agreed it's how we organize things. The word is shared with skill-level disciplines ([[DAS Disciplines]]) because the meaning is the same; only the scope differs:

- **Anchor disciplines** govern *anchor maintenance and structure* — how we organize files, surface meta-content, manage modes across an anchor.
- **Skill disciplines** govern *skill use* — how we ask questions, verify work, navigate active vs parking modes.

The catalog is `disciplines/`; the word stays the same because the concept is the same.

## Why this is a top-level anchor-system thing

The anchor system has three top-level conceptual groupings:

- **Facets** (`facets/`) — narrow, usually file-based aspects of an individual anchor (Backlog, Decisions, Architecture, Rules, …).
- **Disciplines** (`disciplines/`) — cross-anchor patterns for how we work (this folder).
- **Skills** — operations the agent performs (catalog lives at `~/.claude/skills/`; the system references them, doesn't own them).

Traits remain a separate orthogonal axis (broad paradigms declared in `.anchor`); see [[DAS Aspects]] for the umbrella model.

## When to add a new discipline

A discipline earns a spot in this catalog when:

- The pattern applies across *multiple anchors* (it's not anchor-local).
- It's *operational* — a constraint on how we work, not a defining property of an anchor.
- It has enough substance to warrant its own spec page (more than a one-paragraph rule).

Examples of patterns that earn a discipline entry: how to surface per-file editing rules (Brief), how to declare an external code repo (Linked Mode), the dispatch-table convention.

Examples of patterns that don't: a single project-wide rule (belongs in CLAUDE.md), a single rule about markdown rendering (belongs in `R-md`), a property of one specific anchor (belongs in `{slug} Decisions.md`).

## How to add a discipline

1. Create `disciplines/DAS <name>.md`.
2. Use the standard discipline-spec shape — H1 + `description::` frontmatter + sections covering: *What it is*, *When it applies*, *How it's surfaced*, *Constraints*, *Worked example*, *Related*. (Stubs are fine when the pattern is new and still firming up; mark unfinished sections "TBD.")
3. Add a wiki-link to the appropriate row in the [[DAS Disciplines]] dispatch table — usually the *Anchor-level disciplines* row.
4. Update CLAUDE.md or other surface-level docs only if the discipline needs to fire reflexively (most don't).

## Related

- [[DAS Disciplines]] — the catalog itself.
- [[DAS Brief]] — the Brief discipline (this file is its worked example).
- [[DAS Facets]] — sibling catalog (file-based aspects of an individual anchor).
