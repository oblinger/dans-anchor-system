---
description: "Anchor Page facet — the format of an anchor's {slug}.md entry point"
---
# FCT Anchor Page
The entry page every anchor opens with — its `{slug}.md`.

| -[[FCT Anchor Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [FCT Anchor Page](hook://p/FCT%20Anchor%20Page)<br>: the `{slug}.md` entry-page format                                  |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Related               | [[FCT]],  [[DSC Dispatch Table]],  [[DSC progressive-disclosure]],  [[FEX]],                                                                                          |
| Design                |                                                                                                                                                                       |
| Examples              | [[HBR\|project]],  [[HBR Components\|grouped]],  [[HBR Ingest\|sub-folder]],  [[FEX Snapshot\|skill]]                                                                 |
|                       |                                                                                                                                                                       |
| OLD Examples          | [[FEX]] — [[Snapper Dapper\|skill]],  [[Espresso\|list]],  [[Harbor Components\|grouped]],  [[Glossary\|facet]],  [[Harbor\|project]],  [[Harbor Ingest\|sub-folder]] |

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
- **Dispatch table** — the masthead (+ a member zone for a [[Collection]] anchor). The table's *form* is [[DSC Dispatch Table]]; its row *placement* is [[SKA Decisions|D07]].

# RULESET R-anchor-page
include::
where:: anchor
description:: The {slug}.md entry-page format — identity, top-of-page order, dispatch table, member zone, naming.

What `/audit anchor` checks every `{slug}.md` against. All anchor-page kinds (skill / list / grouped / project root / sub-folder) share this set; worked instances of each kind live in [[FEX]]. Audit a page by reading these rules **or** by diffing it against the matching example. Format of this set: [[FCT Ruleset]].

## Identity & frontmatter

### RULE R-anchor-page-01 — `.anchor` declares slug + traits (checked)
check:: anchor_has slug traits

The anchor folder carries a non-empty `.anchor` file declaring `slug:`, `title:`, and `traits:`.

**Check pattern:** the folder has a `.anchor`; parse it and confirm non-blank `slug:` and `traits:` keys.

**Why:** an empty `.anchor` makes breadcrumb inference skip the anchor and jump to its grandparent (the DAS incident).

### RULE R-anchor-page-02 — Page filename equals the slug (checked)
check:: entry_page_matches_slug

The entry page is named `{slug}.md` — the filename matches the `.anchor` slug (the H1's readable name may differ).

**Check pattern:** `basename(page) == slug + ".md"`.

### RULE R-anchor-page-03 — YAML `description:` present (checked)
check:: frontmatter_has description

The page opens with YAML frontmatter carrying a one-line `description:`.

**Check pattern:** frontmatter parses; `description` key present and non-empty. Inline `desc::` is a violation (deprecated → migrate to YAML).

### RULE R-anchor-page-04 — `traits:` declares the kind (stated)

`traits:` names the anchor kind (`[Code]`, `[skill]`, `Collection`, …); the kind gates which rules below apply (design row, member zone, no-track-row).

### RULE R-anchor-page-05 — H1 is `{slug} - {Full Name}` (checked)
check:: h1_matches_slug

The H1 leads with the slug, then ` - `, then the readable name. Bare-name anchors (no short slug) use just the name.

**Check pattern:** first H1 matches `^{slug} - .+` (or equals the bare name for slugless anchors).

**Why:** the H1 must both cement the jump-key and name the page ([[SKA Decisions|D06]]).

## Top of page (fixed order)

### RULE R-anchor-page-06 — One-sentence summary under the H1 (stated)

A single sentence saying what the page *is*, at the broadest stroke. Deeper detail goes in an optional `## Overview`, never above the dispatch table.

### RULE R-anchor-page-07 — No blank line after the H1 (checked)
check:: no_blank_after_h1

The summary sits on the line **immediately** after the H1 — no blank between them.

**Check pattern:** the line following the H1 is non-blank prose, not an empty line.

**Why:** the glue makes the summary read as part of the heading; blank lines precede only the figure and the table.

### RULE R-anchor-page-08 — Figure optional, no heading above it (stated)

A figure is optional; when present it follows the summary directly, with no heading line above it.

### RULE R-anchor-page-09 — Page order is H1 → summary → (figure) → dispatch (checked)

Those elements appear in that order with nothing else between them.

**Check pattern:** token order from the H1 down is H1, summary line, optional `![[…]]` embed, then the dispatch table.

**Why:** progressive disclosure — broadest view first, navigation last ([[DSC progressive-disclosure]]).

## Dispatch table — masthead

### RULE R-anchor-page-10 — Table follows the Dispatch Table spec (sampled)

The dispatch table conforms to [[DSC Dispatch Table]] — a breadcrumb row then category rows.

**Check pattern:** delegate to `/audit dispatch`.

### RULE R-anchor-page-11 — First row is the breadcrumb cell (checked)
check:: breadcrumb_row

Row one is the breadcrumb: a title cell `-[[This Page]]-`, then the parent-chain path ending in the page's `hook://` link + a one-line description.

**Check pattern:** row 1 matches `\| -\[\[.+\]\]- \| → .+\(hook://.+\)`.

**Why:** the breadcrumb carries the [[DSC anchor-dag]] up-edge.

### RULE R-anchor-page-12 — `Related`: lateral links only, first, omit-if-empty (checked)

`Related` is the first masthead row after the breadcrumb (when it has content), and is **omitted entirely when empty** — never left blank. It carries **only links that ordinary navigation cannot already reach**: NOT the anchor's own contents (reach those by going *in / down*), NOT its ancestors (reach those via the breadcrumb, going *up*), and NOT anything reachable from a parent anchor (you'd arrive there *through* the parent). `Related` is reserved for genuinely **lateral / cross-cutting** links none of those paths surface — e.g. a sibling project, a spec in another tree.

**Check pattern:** if present, `Related` has content and precedes other category rows; **none of its links is a breadcrumb ancestor, a member listed below, or the parent anchor** (those are redundant — drop them). ([[SKA Decisions|D07]])

### RULE R-anchor-page-13 — `Design` row present iff a design folder exists (checked)
check:: design_row_iff_folder

If `{NAME} Design/` exists, a `Design` row is present as the second masthead row, members in the fixed order PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features.

**Check pattern:** `{NAME} Design/` exists ⇔ a `Design` row exists; verify member order. ([[SKA Decisions|D07]])

### RULE R-anchor-page-14 — Masthead is minimal (stated)

The masthead carries only breadcrumb + Anchor + Design (if any) + Related — no ad-hoc rows the breadcrumb already covers (no `Repo` row). Anything enumerable drops to the member zone.

### RULE R-anchor-page-15 — No `Track` row on skill-ecosystem anchors (checked)

A skill / facet / discipline / example anchor carries no `Track` row.

**Check pattern:** if `traits` ∈ {skill, facet, discipline, example}, assert no `Track` row.

**Why:** their tracking is centralized in SKA ([[SKA Decisions|D08]]).

### RULE R-anchor-page-16 — Wiki-links in cells escape the pipe (checked)

In-cell wiki-links use `[[target\|alias]]`.

**Check pattern:** no `[[…|…]]` inside a table cell with an unescaped `|`.

## Member zone — Collection anchors only

### RULE R-anchor-page-17 — Only a Collection enumerates members (stated)

Members are listed below the masthead only on a [[Collection]] anchor; every other kind is masthead-only.

### RULE R-anchor-page-18 — List ≤ ~15, groups past ~15 (sampled)

A flat member list up to ~15 members; member groups (labeled `+` rows) beyond that.

**Check pattern:** member count vs. layout (flat list vs. group rows). ([[DSC granularity]])

### RULE R-anchor-page-19 — Group labels link down; `+` marks expandable (sampled)

Each group-row label is a link *down* to that group's own container page; a trailing `+` marks the label as an expandable container, not a leaf.

**Check pattern:** every group row's label cell is a wiki-link and carries `+`.

### RULE R-anchor-page-20 — Member zone ends with an electric marker (checked)

A Collection's member zone ends with `...` (compact auto), `| --- | |` (auto-list), or trailing `+` group rows.

**Check pattern:** the last member-zone row matches one of those markers.

**Why:** newly-added children need a defined place to land.

## Naming & exceptions

### RULE R-anchor-page-21 — Files and folders are `{NAME}`-prefixed (checked)

Every file and folder inside the anchor is prefixed `{NAME}` (`{NAME} PRD.md`, `{NAME} Docs/`, nested too).

**Check pattern:** list the anchor tree; assert each entry name starts with `{NAME}`. (See [[FCT Naming]] / `R-naming`.)

### RULE R-anchor-page-22 — Simple anchors may carry no table (stated)

A simple / leaf anchor may have no dispatch table at all — frontmatter + H1 + summary suffice.

## Kind-specific rules

Rules that apply only to **one kind** of anchor page (skill / list / grouped / project root / sub-folder). None yet — when a kind accumulates its own rules they live here at the tail, graduating to a dedicated sub-ruleset (e.g. `R-anchor-page-project`) pulled in via `include::` once there are enough.

# BRIEF

- **This file is the spec for the anchor entry page (`{slug}.md`)** — the `.anchor` + page **template**, the **parts**, and the **ruleset** `R-anchor-page`. Format *authority*: `/create anchor`, `/rewire`, `/tidy`, `/audit anchor`, and the audit scripts cite it.
- **Don't inline what belongs elsewhere.** Dispatch-table *mechanics* → [[DSC Dispatch Table]]; row *placement / order* → [[SKA Decisions|D07]]; the naming prefix → [[FCT Naming]]; sub-folder dispatch pages have their own facets. Link, don't duplicate.
- **Examples are never instantiated here** — they live in the `examples/` gallery ([[FEX]]); the masthead `Examples` row links to them by kind. This page carries the template + parts + the ruleset only. If the spec changes, fix the examples — never retrofit the spec to a stale copy.
