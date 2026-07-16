---
description: the `.anchor` file — the YAML declaration at an anchor's root (slug, traits, code, parents, …); the field set lives here, per-field rules route to their facets
---
# DAS Dot Anchor
The `.anchor` file — the small YAML declaration at an anchor's root that carries the anchor's metadata. (The same keys may instead live in a page's YAML frontmatter; `.anchor` is the canonical, page-independent home — frontmatter is the inline alternative.)

| -[[DAS Dot Anchor]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Dot Anchor](hook://p/DAS%20Dot%20Anchor) |
| --- | --- |
| Related | [[DAS Folder]],  [[DAS Naming]],  [[DAS Traits]],  [[DAS Code Repository]],  [[DAS anchor-dag]],   |
| Rules | [[R-dot-anchor]],   |
| Examples | [[DAS\|dans-anchor-system .anchor (traits form)]],  [[OBU\|ob-utils .anchor (code: form)]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track Dispatch]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**TLDR** — `.anchor` is a YAML file at the anchor root. Its **presence makes the folder an anchor** ([[DAS Folder]]); its **fields** declare the anchor's metadata. `slug` is the only required field. This facet is the **field-set index** — each field's detailed rule lives in its owning facet (single source of truth). Managed with `cab-config`. **Cardinality: one per anchor.**

## What it is

A YAML file named `.anchor` at the root of an anchor folder. Two jobs: (1) its mere existence declares the folder an anchor (the marker role — [[DAS Folder]]); (2) its keys declare the anchor's metadata. The identical key set may appear in a page's YAML frontmatter instead (e.g. a `{slug}.md` carrying `traits:` up top) — `.anchor` is the canonical declaration that doesn't depend on any one page; frontmatter is the inline shortcut for small anchors.

## Fields — and who owns each rule

| Field | Meaning | Rule owner |
|---|---|---|
| `slug` | short canonical id (`DKT`, `MUX`) — **required** | [[DAS Naming]] |
| `traits` | the anchor's traits (`code`, `skill`, `paper`, `topic`, …) | [[DAS Traits]] |
| `description` | one-line description (mirrors the anchor page's) | this facet |
| `parents` | up-edges in the anchor DAG | [[DAS anchor-dag]] |
| `code` | path to the associated code repository | [[DAS Code Repository]] |
| `mirror` | doc-mirror routes (`here:`/`there:`/`direction:`) — local two-folder sync, independent of `code` | [[DAS Code Repository]] |
| `now` / `backlog` / `inbox` / `rules` | paths to work-surface files | [[DAS Track]] |
| *(file presence)* | the folder is an anchor | [[DAS Folder]] |

All keys except `slug` are optional, added only when the anchor needs them. Paths are relative to the anchor root unless absolute.

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
