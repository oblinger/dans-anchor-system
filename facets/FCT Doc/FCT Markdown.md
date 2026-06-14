---
description: "a document IS a markdown file — how the markdown text is written"
---

# FCT Markdown
The most basic document facet: every authored doc *is* a markdown file, and this facet owns how that markdown text is written — table escapes, fence rules, wiki-links over bare backticks, named lists, the `RULE`/`RULESET` sentinels. Sibling to [[FCT Doc Structure]] (which owns *what goes where* in a doc); Markdown owns *how the text itself is written*.

| -[[FCT Markdown]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Doc]] → [FCT Markdown](hook://p/FCT%20Markdown)<br>: a document IS a markdown file — how the markdown text is written |
| --- | --- |
| Related | [[DSC markdown]] (the discipline this specializes),  [[R-markdown]] (the ruleset),  [[FCT Doc Structure]] (sibling — doc layering),  [[md]] (utility skill) |
| Examples | [[CAE Minimal Facet\|minimal — short doc, no table]],  [[FCT Doc Structure\|fuller — tables + embedded ruleset]],  [[HBR\|anchor page — masthead + escaped table links]],   |

**TLDR.** Markdown is the *root* document facet — beneath every other facet (Brief, Ruleset, Discussion, Doc Structure) sits a plain markdown file, and its text must render correctly and read consistently. The canonical rules live in the [[DSC markdown]] discipline and the [[R-markdown]] ruleset (cited vault-wide, no per-anchor opt-in); this facet is their document-level *view* — the spec that says "this document is a markdown file, shaped this way." It does not restate the rules.

## Overview
Two disciplines specialize, at the document level, into two sibling Doc facets:

- [[DSC progressive-disclosure]] → **[[FCT Doc Structure]]** — the canonical top-to-bottom *layering* of a document (H1 → summary → table → TLDR → body).
- [[DSC markdown]] → **FCT Markdown** — the *text*: how each line of markdown is written so it renders right and reads consistently.

Doc Structure answers *what section goes where*; Markdown answers *how do I write this line of markdown correctly*. Every authored `.md` file carries both, simultaneously — they don't conflict, they sit at different levels.

**Cardinality: one per document.** Every authored `.md` file is exactly one markdown document; the facet applies to each file independently across an anchor.

## The rules — where they live
This facet deliberately holds **no embedded ruleset of its own** — markdown rules are vault-wide and already canonical in one place. Follow the link rather than maintaining a second copy:

- **[[R-markdown]]** — the catalog ruleset (10 rules). Body is embedded in [[DSC markdown#RULESET R-markdown|the discipline]] per the [[F133 — Rulesets folder convention + facet embedding|F133]] convention.
  - **Mechanical (5)** — pipe-escape in table wiki-links, blank line around tables, no markdown inside fenced code blocks, em-dash character, dataview `::` collision.
  - **Authoring (5)** — vault refs are wiki-links not bare backticks, body-only preference, no wiki-link form for code identifiers, named-list shape, per-anchor docs don't restate facet rules.
- **[[DSC markdown]]** — the discipline spec; contains the embedded RULESET body and the mechanical-vs-authoring framing.
- **[[md]]** — the user-invokable utility skill (`/md toc`, `/md file-tree`) that *produces / maintains* markdown artifacts.

## Relationship to other facets
- **[[FCT Doc Structure]]** — sibling document facet; owns layering (*what goes where*) while this owns the text (*how it's written*).
- **[[FCT Brief]] / [[FCT Ruleset]] / [[FCT Discussion]]** — regions authored *inside* a markdown document; each is itself written in conformant markdown, so they all sit atop this facet.

# BRIEF
- **This is the root / most-basic document facet** — every other doc facet presupposes a well-formed markdown file underneath it. Listed in the [[FCT Doc]] group alongside its sibling [[FCT Doc Structure]].
- **No embedded ruleset by design** — the markdown rules are vault-wide and canonical in [[DSC markdown]] / [[R-markdown]]; this facet *links*, it does not duplicate (duplicating would violate the very single-source rule it points at). R-facet-spec-18 is satisfied by the linked `[[R-markdown]]`.
- **This is the spec, not an instance** — never paste a real markdown document here; the Examples row points at real instances.
- **Don't absorb [[FCT Doc Structure]]** — keep the boundary crisp: text-how-written here, layering-what-goes-where there. The two specialize two different sibling disciplines.
