---
description: "Anchor Page facet — the format of an anchor's {slug}.md entry point"
---
# FCT Anchor Page
The entry page every anchor opens with — its `{slug}.md`.

| -[[FCT Anchor Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [FCT Anchor Page](hook://p/FCT%20Anchor%20Page)<br>: the `{slug}.md` entry-page format |
| --- | --- |
| Related | [[FCT]],  [[CAB Dispatch Table]],  [[DSC progressive-disclosure]],  [[FEX]],   |
| Examples | [[FEX]] — [[Snap\|skill]],  [[Bridges\|list]],  [[Devtools\|grouped]],  [[Glossary\|facet]],  [[Clarifier\|project]],  [[Clarifier Track\|sub-folder]] |

## Anchor Page Template

An anchor is **two files**: the `.anchor` spec (what makes the folder an anchor) and the `{slug}.md` entry page that renders inside it.

**`.anchor`** — the anchor spec (YAML; consumed by HookAnchor):

```yaml
slug: {SLUG}
title: {Full Name}
traits: [Code]
```

**`{slug}.md`** — opens with YAML frontmatter…

```yaml
description: one-line description of the anchor
traits: [Code]
```

…then the body, which renders **live** (markdown is never shown in back-ticks — it does not render there):

# {SLUG} - {Full Name}
{one-sentence summary — what the page is, at the broadest stroke; NO blank line above this line}

| -{SLUG}- | → [[kmr]] → … → [{NAME}](hook://p/{NAME})<br>: short description |
| --- | --- |
| Related | … |
| {structural / member rows} | … |
| ... |  |

## Anchor Page Parts

- **Frontmatter** — `description:` (one line) + `traits:` (the anchor kind). Inline `desc::` is deprecated; migrate to `description:` in YAML.
- **H1** — `{slug} - {Full Name}`: the slug leads (the jump-key), the readable name follows. Bare-name anchors use just the name.
- **Summary** — one sentence on the **very next line** (no blank after the H1); says what the page *is*. More detail goes in an optional `## Overview` later, never above the dispatch table.
- **Figure** — optional; embedded right after the summary with **no heading above it** — the big-picture visual before the navigation.
- **Dispatch table** — the masthead (+ a member zone for a [[Collection]] anchor). The table's *form* is [[CAB Dispatch Table]]; its row *placement* is [[SKA Decisions|D07]].

# RULESET R-anchor-page

The **one rule set for anchor pages** — what `/audit anchor` checks every `{slug}.md` against. All anchor-page *kinds* (skill / list collection / grouped collection / facet / project root / sub-folder) share this set; if a kind ever diverges, add a second ruleset below scoped to that kind. Worked instances of each kind live in [[FEX]] — audit by reading these rules **or** by eyeballing the matching example.

### Identity & frontmatter
- **R-anchor-file** — the folder carries a `.anchor` declaring `slug:`, `title:`, and `traits:`. An **empty `.anchor` is invalid** — breadcrumb inference then skips the anchor and jumps to its grandparent (the OBSK incident).
- **R-filename** — the entry page is named `{slug}.md` (filename = the `.anchor` slug); the H1's readable name may differ from the slug.
- **R-frontmatter** — the page opens with YAML frontmatter carrying `description:` (one line). Inline `desc::` is deprecated → migrate to YAML.
- **R-traits** — `traits:` declares the anchor kind (e.g. `[Code]`, `[skill]`, `Collection`); the kind drives which rules below apply (design facet, collection member zone, …).
- **R-h1-form** — H1 is `{slug} - {Full Name}` — slug first (cements the jump-key), readable name after. Bare-name anchors use just the name. ([[SKA Decisions|D06]])

### Top of page (fixed order)
- **R-summary** — a one-sentence summary says what the page *is*, at the broadest stroke; deeper detail goes in an optional `## Overview`, never above the table.
- **R-no-blank-after-h1** — **no blank line between the H1 and the summary** (summary glued to the heading). Blanks *do* precede the figure and the table.
- **R-figure** — a figure is optional; if present it sits right after the summary with **no heading above it** — the big-picture visual before the navigation.
- **R-order** — the page opens **H1 → summary → (figure) → dispatch table**, in that order. ([[DSC progressive-disclosure]])

### Dispatch table — masthead
- **R-dispatch-form** — the table follows [[CAB Dispatch Table]]: a breadcrumb row, then category rows.
- **R-breadcrumb** — the first row is the breadcrumb cell — a title cell `-[[This Page]]-` plus the parent-chain path ending in the page's `hook://` link + a one-line description. It carries the [[DSC anchor-dag]] up-edge.
- **R-related-first** — `Related` is the **1st** masthead row; **omit it entirely when empty — never leave it blank**. ([[SKA Decisions|D07]])
- **R-design-second** — if the anchor has the design facet (`{NAME} Design/` exists), a `Design` row is present as the **2nd** row, members in the fixed order PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features. ([[SKA Decisions|D07]])
- **R-masthead-minimal** — the masthead is **only** breadcrumb + Anchor + Design (if any) + Related; no ad-hoc rows the breadcrumb already covers (no `Repo` row). Anything *enumerable* drops to the member zone.
- **R-no-track-row** — a skill-ecosystem anchor (skill / facet / discipline / example) has **no `Track` row** — its tracking is centralized in SKA. ([[SKA Decisions|D08]])
- **R-pipe-escape** — wiki-links inside table cells escape the pipe: `[[target\|alias]]`.

### Member zone — Collection anchors only
- **R-member-zone** — only a [[Collection]] anchor enumerates members (below the masthead); a non-collection page is masthead-only.
- **R-list-vs-grouped** — a flat member list for ≤ ~15 members; member groups (labeled `+` rows) past ~15. ([[DSC granularity]])
- **R-grouped-links-down** — each group-row label is a link *down* to that group's own page (a container with its own table); `+` marks the label as an expandable container, not a leaf.
- **R-ends-electric** — a Collection's member zone **ends with an electric-list marker** — `...` (compact auto), `| --- | |` (auto-list), or trailing `+` group rows — so newly-added children have a defined place to land.

### Naming & exceptions
- **R-name-prefix** — every file and folder inside the anchor is prefixed `{NAME}` (`{NAME} PRD.md`, `{NAME} Docs/`, nested files too) to stay collision-free in the shared Obsidian namespace. ([[FCT Naming]])
- **R-optional-table** — a simple anchor may carry **no** dispatch table at all — frontmatter + H1 + summary are sufficient.

# BRIEF

- **This file is the spec for the anchor entry page (`{slug}.md`)** — the `.anchor` + page **template**, the **parts**, and the **rule set** `R-anchor-page`. Format *authority*: `/create anchor`, `/rewire`, `/tidy`, `/audit anchor`, and the audit scripts cite it.
- **Don't inline what belongs elsewhere.** Dispatch-table *mechanics* → [[CAB Dispatch Table]]; row *placement / order* → [[SKA Decisions|D07]]; the naming prefix → [[FCT Naming]]; sub-folder dispatch pages have their own facets. Link, don't duplicate.
- **Examples are never instantiated here** — they live in the `examples/` gallery ([[FEX]]); the masthead `Examples` row links to them by kind. This page carries the template + parts + the rule set only. If the spec changes, fix the examples — never retrofit the spec to a stale copy.
