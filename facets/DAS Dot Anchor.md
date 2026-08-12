---
description: the `.anchor` file — the YAML declaration at an anchor's root (slug, traits, code, parents, …); the field set lives here, per-field rules route to their facets
group: file
---

| -[[DAS Dot Anchor]]- | → [[DAS]] → [[FCT]] → [DAS Dot Anchor](hook://p/DAS%20Dot%20Anchor)  |
| --- | --- |
| Related | [[DAS Folder]],  [[DAS Naming]],  [[DAS Traits]],  [[DAS Code Repository]],  [[DAS anchor-dag]],   |
|  | [[ANC Standard\|Anchor Standard]],   |
| Rules | [[R-dot-anchor]],   |
| Examples | [[DAS\|dans-anchor-system .anchor (traits form)]],  [[OBU\|ob-utils .anchor (code: form)]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Dot Anchor
The `.anchor` file — the small YAML declaration at an anchor's root that carries the anchor's metadata. (The same keys may instead live in a page's YAML frontmatter; `.anchor` is the canonical, page-independent home — frontmatter is the inline alternative.)

**TLDR** — `.anchor` is a YAML file at the anchor root. Its **presence makes the folder an anchor** ([[DAS Folder]]); its **fields** declare the anchor's metadata. **No field is required** — presence alone is the declaration; `slug` in particular is optional, and an anchor without one is addressed by its basename. This facet is the **field-set index** — each field's detailed rule lives in its owning facet (single source of truth). Managed with `cab-config`. **Cardinality: one per anchor.**

## What it is

A YAML file named `.anchor` at the root of an anchor folder. Two jobs: (1) its mere existence declares the folder an anchor (the marker role — [[DAS Folder]]); (2) its keys declare the anchor's metadata. The identical key set may appear in a page's YAML frontmatter instead (e.g. a `{slug}.md` carrying `traits:` up top) — `.anchor` is the canonical declaration that doesn't depend on any one page; frontmatter is the inline shortcut for small anchors.

## Fields — and who owns each rule

| Field | Meaning | Rule owner |
|---|---|---|
| `slug` | short canonical id (`DKT`, `MUX`) — **optional**; absent → addressed by basename. Matches `^[A-Z0-9]+$`, and is declared only when it is a genuine short handle (a prefix, a moniker, or both) — never a restatement of the basename | [[DAS Naming]] |
| `traits` | the anchor's traits (`code`, `skill`, `paper`, `topic`, …) | [[DAS Traits]] |
| `traits-` | traits the anchor opts OUT of, including the implicit ones every anchor carries | [[DAS Traits]] |
| `description` | one-line description (mirrors the anchor page's) | this facet |
| `parents` | up-edges in the anchor DAG | [[DAS anchor-dag]] |
| `feeds` | the anchors this one draws work from — in-edges of the **feed** DAG, a second graph over the same nodes. Declared only by the consumer; out-edges are computed by inverting | [[DAS feed]] |
| `code` | path to the associated code repository | [[DAS Code Repository]] |
| `mirror` | doc-mirror routes (`here:`/`there:`/`direction:`) — local two-folder sync, independent of `code` | [[DAS Code Repository]] |
| `now` / `backlog` / `inbox` / `rules` | paths to work-surface files | [[DAS Track]] |
| *(file presence)* | the folder is an anchor | [[DAS Folder]] |

**Every key is optional**, added only when the anchor needs it. Paths are relative to the anchor root unless absolute.

### No field is required — DAS follows [[ANC Standard]] here, and the reconciliation is deliberate

This facet said `slug` was **required** while [[ANC Standard]] — the upstream spec DAS builds on — makes it optional, with the *basename* as the anchor's durable identity and an **implied slug** (explicit slug when declared, otherwise the basename verbatim) computed for consumers that need one. DAS could legitimately have been the stricter of the two. It is not, and the reason is that the stricter rule was never a policy DAS held — it was a false description of DAS's own behaviour (T068, measured 2026-08-02):

- **DAS's own tooling already implements the implied-slug fallback.** `audit-plan.py`'s `_anchor_name` reads `slug:` from `.anchor` and *falls back to the folder name* when it is absent — which is ANC's implied slug, arrived at independently. Every `where:: {slug}` selector in the ruleset corpus resolves through it.
- **The corpus never obeyed the strict rule.** Of **1,332 `.anchor` files in the vault, 1,147 — 86% — declare no `slug` at all.** A requirement violated by six anchors in seven, enforced by no checker, is not a stricter standard; it is drift with a confident sentence in front of it.

**The same held for `traits:`, and it went the same way the same day.** `R-anchor-page-01` — the one live rule asserting either field — was wired `check:: anchor_has slug traits`. Dropping `slug:` (T104) cleared 125 of its 1,210 failures; the other 1,085 were `traits:`, so T105 dropped that too and the rule now asserts nothing. The justification for keeping it did not hold up on inspection: it claimed an empty `.anchor` makes breadcrumb inference skip to the grandparent, but the [[audit-anchor]] checklist attaches that incident to **`slug:`**, and it does not reproduce — **720 `.anchor` files in the vault are zero-byte**, and 182 of the 232 child docs beneath them name their empty anchor in the breadcrumb correctly.

So the two specs and the enforcement now agree, on ANC's reading, for every field. Two things this reconciliation does **not** erase. Where a consumer needs to tell a *declared* slug from a *defaulted* one, it reads the `slug` field directly rather than the implied value. And a *declared* field may still oblige another — `traits:` containing `code` requires a `code:` path ([[R-code-repository]]-01). That conditional shape is the correct one: absence of a field is a default, presence of one can carry consequences.

## Getting to the code

The `code:` field is how an anchor points at its repo. Resolve it to an absolute path with **`cab-config path code`** (run from the anchor root). To jump to an arbitrary project's code:

```
cd "$(dirname "$(ha -p '<project>')")"   # the anchor folder
cd "$(cab-config path code)"             # its code repo
```

(Open in an editor instead: `cursor "$(cab-config path code)"`.) Detail: [[DAS Code Repository]].

## Tooling

`cab-config` manages the file: `cab-config show` (display), `cab-config get <key>` / `set <key> <value>`, and `cab-config path <key>` (resolve a path-valued key to an absolute path).

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; per-field rules live in the facets named in § Fields.)*

- **New field → add a row to § Fields and route** to its owning facet; never restate a field's rule here (R-dot-anchor-02).
- **Keep both framings** — `.anchor` file and page-frontmatter carry the same key set; don't let the doc drift into treating them as two mechanisms.
- **Sibling boundary** — [[DAS Folder]] owns the *marker/presence* role (folder → anchor, one-per-root); this facet owns the *field set inside the file*. Keep that split.
