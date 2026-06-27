# CAB Disciplines Brief

Editing-and-maintenance brief for [[CAB Disciplines]]. Read before adding a new discipline, restructuring the catalog, or auditing what belongs here.

## What a discipline is

A **discipline** is a constrained way of working — a pattern we follow because we agreed it's how we organize things. The word is shared with skill-level disciplines ([[SKL Discipline]]) because the meaning is the same; only the scope differs:

- **CAB disciplines** govern *anchor maintenance and structure* — how we organize files, surface meta-content, manage modes across an anchor.
- **Skill disciplines** govern *skill use* — how we ask questions, verify work, navigate active vs parking modes.

The catalog locations disambiguate (`CAB Disciplines/` vs `SKL Discipline/`); the word stays the same because the concept is the same.

## Why this is a top-level CAB thing

CAB has three top-level conceptual groupings:

- **Facets** (`CAB/CAB Facets/`) — narrow, usually file-based aspects of an individual anchor (Backlog, Decisions, Architecture, Rules, …).
- **Disciplines** (`CAB/CAB Disciplines/`) — cross-anchor patterns for how we work (this folder).
- **Skills** — operations the agent performs (catalog lives at `~/.claude/skills/`; CAB references them, doesn't own them).

Traits remain a separate orthogonal axis (broad paradigms declared in `.anchor`); see [[CAB Aspects]] for the umbrella model.

## When to add a new discipline

A discipline earns a spot in this catalog when:

- The pattern applies across *multiple anchors* (it's not anchor-local).
- It's *operational* — a constraint on how we work, not a defining property of an anchor.
- It has enough substance to warrant its own spec page (more than a one-paragraph rule).

Examples of patterns that earn a discipline entry: how to surface per-file editing rules (Brief), how to declare an external code repo (Linked Mode), the dispatch-table convention.

Examples of patterns that don't: a single project-wide rule (belongs in CLAUDE.md), a single rule about markdown rendering (belongs in `R-md`), a property of one specific anchor (belongs in `{NAME} Decisions.md`).

## How to add a discipline

1. Create `CAB Disciplines/CAB <Name>.md`.
2. Use the standard discipline-spec shape — H1 + `description::` frontmatter + sections covering: *What it is*, *When it applies*, *How it's surfaced*, *Constraints*, *Worked example*, *Related*. (Stubs are fine when the pattern is new and still firming up; mark unfinished sections "TBD.")
3. Add a wiki-link to the appropriate row in the [[CAB Disciplines]] dispatch table — usually the *Anchor-level disciplines* row.
4. Update CLAUDE.md or other surface-level docs only if the discipline needs to fire reflexively (most don't).

## Related

- [[CAB Disciplines]] — the catalog itself.
- [[FCT Brief]] — the Brief discipline (this file is its worked example).
- [[CAB Facets]] — sibling catalog (file-based aspects of an individual anchor).
- [[SKL Discipline]] — sibling catalog at skill level.
