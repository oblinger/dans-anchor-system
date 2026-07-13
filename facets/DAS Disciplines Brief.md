# DAS Disciplines Brief

Editing-and-maintenance brief for [[DAS Disciplines]]. Read before adding a new discipline, restructuring the catalog, or auditing what belongs here.

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
