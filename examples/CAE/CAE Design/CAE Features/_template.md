---
description: {one-line summary of what this feature does}
---

# [[CAE]] · F### — {Feature Name}
## Open Questions

- **Q1 — {short question}** — {context, options, what you're leaning toward}.

### Resolved

_None yet — questions move here once answered, with the resolution and where it landed in the design._



## Summary

{One or two paragraphs. What this feature does, why it exists, what user-visible problem it solves.}

## Interface

```rust
// {API surface — function signatures, types, public structs.
// Omit the section entirely if the feature is not API-shaped.}
```

## Requirements

- {Requirement 1 — observable behavior, not implementation.}
- {Requirement 2 — …}

## Design

{The shape: how the requirements are met. Integration points, data flow, trade-offs that matter to readers. Cross-link to [[CAE PRD]] and [[CAE Architecture#Component diagram|CAE Architecture § Component diagram]] where relevant.}

## Status

Designing — awaiting question resolution.



---

# About this template

This folder holds dated/numbered feature specs for [[CAE]]. The exemplar above shows the canonical shape every feature file takes; the spec below describes the rules.

## File-naming

- **Filename:** `F### — Feature Name.md` — zero-padded to three digits, em-dash separator (U+2014).
- **F-numbers are durable.** Never recycled. Pick the next unused integer across this folder and the [[CAE Backlog]].
- Use the literal em-dash character `—`, not a hyphen `-` or two hyphens `--`.

## Structure

- **YAML frontmatter** with a one-phrase `description:` field at the top.
- **`## Open Questions`** block ABOVE the H1 — pre-document material per the [[SKA ask]] discipline. The `### Resolved` subsection accumulates answered questions with their resolutions; never delete a resolved question, just move it.
- **H1:** `# [[{ANCHOR}]] · F### — {Feature Name}` — the wiki-link to the parent anchor and the F-number make the file self-locating.
- **Body sections** vary by feature; common ones include `## Summary`, `## Interface`, `## Requirements`, `## Design`, `## Status`. Add or omit as the feature shape dictates.
- **`## Status`** line at the end. One of: `Designing` / `Agreed` / `Implementing` / `Testing` / `Done`. Tracks lifecycle position; the `[[SKA feature]]` skill drives transitions.

## Cross-references

Wiki-link freely to [[CAE PRD]], [[CAE Architecture#Component diagram|CAE Architecture § Component diagram]], [[CAE Roadmap]], [[CAE Decisions]], and other features. Use the alias form `[[CAE Decisions#D01 — One Queue, One Clock (sampled)\|D01]]` when citing a specific rule.

## Convention

This file is itself an instance of the **Template** convention — see [[CAB Template]] for the general specification (when to use, file structure, divider convention, naming). (Filename note: per the modern convention this file should be renamed `_Feature Template.md` to follow `_{Name} Template` naming; deferred for organic migration since the bare `_template.md` form is still referenced from existing docs.)
