---
description: "Anchor Page facet — the format of an anchor's {slug}.md entry point"
---
# FCT Anchor Page
The entry page every anchor opens with — its `{slug}.md`.

| -[[FCT Anchor Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [FCT Anchor Page](hook://p/FCT%20Anchor%20Page)<br>: the `{slug}.md` entry-page format |
| --- | --- |
| Related | [[FCT]],  [[CAB Dispatch Table]],  [[DSC progressive-disclosure]],  [[FEX]],   |
| Examples | [[FEX]] — [[Snap\|skill]],  [[Bridges\|list]],  [[Devtools\|grouped]],  [[Clarifier\|project]],  [[Clarifier Track\|sub-folder]] |

## Template

The shape of an anchor page, top to bottom — H1 → summary → optional figure → dispatch table:

```
---
description: one-line description of the anchor
traits: [Code]
---

# {slug} - {Full Name}
{one-sentence summary — what the page is, at the broadest stroke; NO blank line above this line}

![[{NAME} figure.svg]]                ← optional; no heading above it

| -{NAME}- | → [[kmr]] → … → [{NAME}](hook://p/{NAME})<br>: short description |
| --- | --- |
| Related | … |
| {structural / member rows} | … |
| ... | |
```

## The pieces

- **Frontmatter** — `description:` (one line) + `traits:` (the anchor kind). Inline `desc::` is deprecated; migrate to `description:` in YAML.
- **H1** — `{slug} - {Full Name}`: the slug leads (the jump-key), the readable name follows. Bare-name anchors use just the name.
- **Summary** — one sentence on the **very next line** (no blank after the H1); says what the page *is*. More detail goes in an optional `## Overview` later, never above the dispatch table.
- **Figure** — optional; embedded right after the summary with **no heading above it** — the big-picture visual before the navigation.
- **Dispatch table** — the masthead (+ a member zone for a [[Collection]] anchor). The table's *form* is [[CAB Dispatch Table]]; its row *placement* is [[SKA Decisions|D07]].

## Rule Set

The **one rule set for anchor pages** — what `/audit anchor` checks every `{slug}.md` against. All anchor-page *kinds* (skill / list collection / grouped collection / facet / project root / sub-folder) share this set today; if a kind ever needs its own rules, add a second `## Rule Set` below scoped to that kind. Worked instances of each kind live in [[FEX]] — audit by reading these rules **or** by eyeballing the matching example.

- RULE (h1-form): H1 is `{slug} - {Full Name}` — slug first (cements the jump-key), readable name after. ([[SKA Decisions|D06]])
- RULE (top-of-page-order): the page opens **H1 → summary → (figure) → dispatch table**, with **no blank line after the H1** (summary glued to the heading; blanks *do* precede the figure and table). ([[DSC progressive-disclosure]])
- RULE (name-prefix): every file and folder inside the anchor is prefixed `{NAME}` (`{NAME} PRD.md`, `{NAME} Docs/`, nested files too) to stay collision-free in the shared Obsidian namespace. ([[FCT Naming]])
- RULE (dispatch-conforms): the dispatch table follows [[CAB Dispatch Table]] — `Related` is the 1st masthead row; `Design` is the 2nd **iff** the anchor has a design facet (members in the fixed D07 order); a skill-ecosystem anchor has **no `Track` row** ([[SKA Decisions|D08]]); a [[Collection]]'s member zone ends with an electric-list marker.
- RULE (optional-table): a simple anchor may carry **no** dispatch table at all — frontmatter + H1 + summary are sufficient.

## Examples

Worked examples live in **[[FEX]]** (the `examples/` gallery), not instantiated here — reference, don't copy:

- [[Snap]] — a **skill** anchor page (`SKILL.md`: `name` / `user_invocable` frontmatter, masthead = `Related` only).
- [[Bridges]] — a **list collection** (≤ 15, flat member list, ends in `...`).
- [[Devtools]] — a **grouped collection** (> 15, `+` group rows linking *down*).
- [[Clarifier]] — a **project root** (the `Design` / `Track` rows in D07 order); [[Clarifier Track]] is a **sub-folder dispatch**.

If the spec changes, fix the examples; never retrofit the spec to a stale inline copy.

# BRIEF

- **This file is the spec for the anchor entry page (`{slug}.md`)** — frontmatter, H1, summary, optional figure, and the dispatch table it carries. Format *authority*: `/create anchor`, `/rewire`, `/tidy`, `/audit anchor`, and the audit scripts cite it.
- **Don't inline what belongs elsewhere.** Dispatch-table *mechanics* → [[CAB Dispatch Table]]; row *placement / order* → [[SKA Decisions|D07]]; the naming prefix → [[FCT Naming]]; sub-folder dispatch pages have their own facets. Link, don't duplicate.
- **Examples are never instantiated here** — they live in [[FEX]] (the `examples/` gallery: [[Snap]], [[Bridges]], [[Devtools]], [[Clarifier]]). Keep those the single source of the worked form; this page carries only the Template skeleton + the pieces + the rule set.
-[[{NAME}]]-`; pipe-escape wiki-link aliases in cells (`[[target\|alias]]`).
