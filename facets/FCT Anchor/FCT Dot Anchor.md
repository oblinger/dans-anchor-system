---
description: the `.anchor` file — the YAML declaration at an anchor's root (slug, traits, code, parents, …); the field set lives here, per-field rules route to their facets
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Dot Anchor](hook://p/FCT%20Dot%20Anchor)

# FCT Dot Anchor
The `.anchor` file — the small YAML declaration at an anchor's root that carries the anchor's metadata. (The same keys may instead live in a page's YAML frontmatter; `.anchor` is the canonical, page-independent home — frontmatter is the inline alternative.)

**Related:** [[FCT Folder]], [[FCT Naming]], [[TRT]], [[FCT Code Repository]], [[DSC anchor-dag]].

**TLDR** — `.anchor` is a YAML file at the anchor root. Its **presence makes the folder an anchor** ([[FCT Folder]]); its **fields** declare the anchor's metadata. `slug` is the only required field. This facet is the **field-set index** — each field's detailed rule lives in its owning facet (single source of truth). Managed with `cab-config`. **Cardinality: one per anchor.**

## What it is

A YAML file named `.anchor` at the root of an anchor folder. Two jobs: (1) its mere existence declares the folder an anchor (the marker role — [[FCT Folder]]); (2) its keys declare the anchor's metadata. The identical key set may appear in a page's YAML frontmatter instead (e.g. a `{NAME}.md` carrying `traits:` up top) — `.anchor` is the canonical declaration that doesn't depend on any one page; frontmatter is the inline shortcut for small anchors.

## Fields — and who owns each rule

| Field | Meaning | Rule owner |
|---|---|---|
| `slug` | short canonical id (`DKT`, `MUX`) — **required** | [[FCT Naming]] |
| `traits` | the anchor's traits (`code`, `skill`, `paper`, `topic`, …) | [[TRT]] |
| `description` | one-line description (mirrors the anchor page's) | this facet |
| `parents` | up-edges in the anchor DAG | [[DSC anchor-dag]] |
| `code` | path to the associated code repository | [[FCT Code Repository]] |
| `now` / `backlog` / `inbox` / `rules` | paths to work-surface files | [[FCT Track]] |
| *(file presence)* | the folder is an anchor | [[FCT Folder]] |

All keys except `slug` are optional, added only when the anchor needs them. Paths are relative to the anchor root unless absolute.

## Getting to the code

The `code:` field is how an anchor points at its repo. Resolve it to an absolute path with **`cab-config path code`** (run from the anchor root). To jump to an arbitrary project's code:

```
cd "$(dirname "$(ha -p '<project>')")"   # the anchor folder
cd "$(cab-config path code)"             # its code repo
```

(Open in an editor instead: `cursor "$(cab-config path code)"`.) Detail: [[FCT Code Repository]].

## Tooling

`cab-config` manages the file: `cab-config show` (display), `cab-config get <key>` / `set <key> <value>`, and `cab-config path <key>` (resolve a path-valued key to an absolute path).

# RULESET R-dot-anchor
include::
where:: file: **/.anchor
description:: the `.anchor` file — anchor metadata declaration

### RULE R-dot-anchor-01 — `.anchor` is valid YAML carrying a slug (checked)
The `.anchor` file parses as YAML and declares a non-empty `slug`.
**Check pattern:** the file loads as YAML and contains a `slug:` key with a non-empty value.
**Why:** the slug is the anchor's canonical identifier; every other field is optional, but without a slug the anchor cannot be referenced.

### RULE R-dot-anchor-02 — Per-field rules live in their owning facet (stated)
Beyond valid-YAML + slug, each field's rules are owned by its facet (§ Fields): `traits` → [[TRT]], `code` → [[FCT Code Repository]], `parents` → [[DSC anchor-dag]], `slug`/naming → [[FCT Naming]]. Do not restate those rules here — this facet is the field-set index, not a second source.
**Why:** single source of truth — duplicating a field's rule here would drift from its facet.

# BRIEF

- **This is the consolidated spec for the `.anchor` file** — the field set, the format, the `cab-config` tooling, and the code-access path. It is the index; per-field rules live in the facets named in § Fields.
- **Not a second copy of the per-field rules** — `slug`/naming, `traits`, `code`, `parents` each have their own facet (single source of truth). Add a field row to § Fields and route; never restate the rule.
- **`.anchor` vs frontmatter** — the same keys may live in a page's YAML frontmatter; keep both framings here so neither is treated as a separate mechanism.
- **Sibling boundary** — [[FCT Folder]] owns the *marker/presence* (folder → anchor, one-per-root); this facet owns the *field set inside the file*. Keep that split.
