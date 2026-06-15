---
description: "Anchor Page facet — the format of an anchor's {slug}.md entry point"
---
# FCT Anchor Page
The entry page every anchor opens with — its `{slug}.md`.

| -[[FCT Anchor Page]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Anchor]] → [FCT Anchor Page](hook://p/FCT%20Anchor%20Page)<br>: the `{slug}.md` entry-page format |
| --- | --- |
| Related | [[FCT]],  [[FCT Dispatch Table]],  [[DSC progressive-disclosure]],  [[FEX]],   |
| Design |  |
| Examples | [[HBR\|Code project]],  [[FCT Anchor Page\|Sub-project · facet]],  [[DSC progressive-disclosure\|Sub-project · discipline]],  [[SKL Mint\|Sub-project · skill-doc]],  [[SKL\|Container · grouped]],  [[SKA Access\|Container · list]],  [[HBR Log\|Container · chronological]],  [[Life\|Topic]],   |
| Rulesets |  |
|  |  |
| OLD Examples | [[FEX]] — [[Snapper Dapper\|skill]],  [[Espresso\|list]],  [[Harbor Components\|grouped]],  [[Glossary\|facet]],  [[Harbor\|project]],  [[Harbor Ingest\|sub-folder]] |

| Kind                      | Anchor Page Taxonomy     |
| ------------------------- | ------------------------ |
| Topic                     |                          |
| Project                   |                          |
| - Code project            |                          |
| - Paper project           |                          |
| - SKA sub-project            | Skill, Facet, Discipline |
| Container                 |                          |
| - Grouped Container       |                          |
| - List Container          |                          |
| - Chronological Container |                          |


## Worked example sets — five real vault instances per kind

Real anchor pages found in the vault and brought to conformance, so the spec can be judged against actual instances (not the gallery). Five per kind:

### Topic
- [[Life]]
- [[Courses]]
- [[Food]]
- [[Legal]]
- [[SRC]]

### Code project
- [[HA]]
- [[SKD]]
- [[MUX]]
- [[CMP]]
- [[DMUX]]

### Paper project
- [[2026-03-18 AI Model Pricing]]
- [[2026-05-22 Architect Skill Survey]]
- [[2026-04-13 Drone Comparison]]
- [[2026-03-14 Personal Skill Trees and Project Organization Survey]]
- [[2026-03-04 Mukesh Murugan Dossier]]

*(promoted from RR Research Reports — no native Paper anchors existed)*

### SKA sub-project
- [[FCT Code Repository]]
- [[FCT Naming]]
- [[DSC verification]]
- [[DSC Linked Mode]]
- [[SKL Doc]]

### Container
- [[Log]] *(grouped)*
- [[SV]] *(grouped)*
- [[RR]] *(grouped)*
- [[Roots]] *(list)*
- [[Journal]] *(chronological)*

**TLDR** — **Cardinality: one per anchor.** Every anchor has exactly one `{slug}.md` entry page. It opens with YAML `description:` frontmatter, then H1 → one-line summary → optional figure → dispatch table (breadcrumb + Related + kind-specific rows). The embedded `R-anchor-page` ruleset (22 shared rules + five kind deltas — Topic / Code / Paper / SKA sub-project / Container) is the auditable contract; `/audit anchor` and `/create anchor` cite it. Member groups appear only on Container anchors; a Topic carries a `...` auto-summary of its contents.



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
{one-sentence summary — the essence: what the page is/does at its core, not incidental detail; NO blank line above this line}

| -{SLUG}- | → [[kmr]] → … → [{NAME}](hook://p/{NAME})<br>: short description |
| --- | --- |
| Related | … |
| {structural / member rows} | … |
| ... |  |

## Anchor Page Parts

- **Frontmatter** — `description:` (one line) + `traits:` (the anchor kind). Inline `desc::` is deprecated; migrate to `description:` in YAML.
- **H1** — `{slug} - {Full Name}`: the slug leads (the jump-key), the readable name follows. Bare-name anchors use just the name.
- **Summary** — one sentence on the **very next line** (no blank after the H1); states the **essence** — what the page *is* or *does* at its core, not incidental detail (per R-anchor-page-06). More goes in an optional `## Overview` later, never above the dispatch table.
- **Figure** — optional; embedded right after the summary with **no heading above it** — the big-picture visual before the navigation.
- **Dispatch table** — the masthead (+ a member zone for a [[Collection]] anchor). The table's *form* is [[FCT Dispatch Table]]; its row *placement* is [[SKA Decisions|D07]].

# RULESET R-anchor-page
include::
where:: anchor
description:: the `{slug}.md` entry-page format

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

### RULE R-anchor-page-06 — First sentence states the essence (stated)

A single sentence that states the **essence** — the core of what the page *is* or *does*, in one stroke. It answers "what is this, fundamentally?", not "what are its features, mechanisms, or edge cases". Lead with the essence; a little qualifying detail is fine, but a grab-bag of incidental facts is the failure. Everything that isn't the essence goes in an optional `## Overview` (or the body), never in this line and never above the dispatch table.

**Why:** this is the one line every reader — and every dispatch table that links the page — sees first; if the essence is buried under incidental detail, the reader must dig for what the thing fundamentally is. E.g. a skill page leads with the essence — *`/feature` creates a new feature document specifying work to be done* — not with a lead-in about collision-handling or status mechanics.

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

The dispatch table conforms to [[FCT Dispatch Table]] — a breadcrumb row then category rows.

**Check pattern:** delegate to `/audit dispatch`.

### RULE R-anchor-page-11 — First row is the breadcrumb cell (checked)
check:: breadcrumb_row

-[[This Page]]-`, then the parent-chain path ending in the page's `hook://` link + a one-line description.

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

### RULE R-anchor-page-22 — Every anchor carries a dispatch table (checked)

An anchor page is **never table-less** — it always carries a dispatch table whose first row is the breadcrumb (which carries the [[DSC anchor-dag]] up-edge, so every anchor needs it). A leaf / topic anchor with no hand-authored rows still carries **breadcrumb + a `...` auto-summary row**. Only **non-anchor** documents may omit the table.

**Check pattern:** every `{slug}.md` has a dispatch table with a breadcrumb row 1 (per R-anchor-page-11). ([[FCT Doc Structure]] § Top table states the same rule at the document layer.)

## Kind-specific rules

Each anchor-page **kind** layers a small delta over the shared chassis (R-anchor-page-01…22) plus the [[FCT Dispatch Table]] form. The kind is read from `traits:`; a page is audited as **chassis + its kind's delta**. There are five kinds, each one-to-one with its dispatch-table shape (HookAnchor computes the table from the `.anchor`, so there is exactly one page — and one table kind — per anchor). The deltas are thin; each may graduate to its own `include::` sub-ruleset file once it grows.

### R-anchor-page-code — Code project (stated)

A code/software project anchor (`traits: [Code]`).
- **Masthead roster:** breadcrumb + Anchor + **Design** (design flow present) + **Track** (**required**) + Related.
- **Member zone:** none — a switchboard masthead only.
- **Example:** [[HBR]].

### R-anchor-page-paper — Paper project (stated)

A paper / writeup project anchor (`traits: [Paper]`).
- **Masthead roster:** breadcrumb + Anchor + **Design** (outline / draft folder, if present) + Related.
- **Member zone:** none — switchboard masthead.
- **Example:** *(TBD — no paper anchor wired yet).*

### R-anchor-page-subproject — SKA sub-project: facet / discipline / skill-doc (checked)

A single skill-ecosystem spec page — a **facet**, a **discipline**, or a **skill-doc** (the documentation page for a skill; *not* the skill folder's `SKILL.md` runbook, which is out of scope).
- **Masthead roster:** breadcrumb + Anchor + **Design** (only if a `{NAME} Design/` folder exists) + Related.
- **No `Track` row** — tracking is centralized in SKA (this is R-anchor-page-15 in kind terms).
- **Member zone:** none.
- **Content** differs by sub-kind (facet spec vs. discipline vs. skill-doc) but the page *structure* is shared — one ruleset, three example flavors.
- **Examples:** facet → [[FCT Anchor Page]]; discipline → [[DSC progressive-disclosure]]; skill-doc → [[SKL Mint]] *(currently a thin doc with no masthead — the bring-up target, tracked separately; do not treat as compliant).*

### R-anchor-page-container — Container: grouped / list / reverse-dated (sampled)

A [[Collection]] anchor whose body enumerates **homogeneous members** (a features folder of feature docs, a log folder of log entries, the `SKL` catalog of skill-docs).
- **Masthead roster:** breadcrumb + Anchor + Related (minimal).
- **Member zone required** — the generic member rules R-anchor-page-17…20 apply. Layout variant (one axis, three values):
  - **grouped** — `+` group rows past ~15 members. Example: [[SKL]], [[FCT]].
  - **list** — a flat list ≤ ~15 members. Example: [[SKA Access]].
  - **chronological (reverse-dated)** — a [[DSC dated-entry-stream]]; newest-first, ISO-prefixed member names. Example: [[HBR Log]].
- Member zone ends with an electric marker (R-anchor-page-20) so new children have a place to land.

### R-anchor-page-topic — Topic (stated)

A topic / domain-of-life folder page — a hub that routes to the pages within the topic.
- **Masthead roster:** breadcrumb + optional Related.
- **`...` auto-summary required** — the member zone is a single compact `...` row (`| ... |  |`) that auto-enumerates the topic's contents (HookAnchor fills it). Every topic page carries it, so the whole topic is summarized and new children have a place to land. A topic is thus a compact auto-listing container.
- **Table required** — like every anchor (R-anchor-page-22), a topic page always has a dispatch table; the minimum is breadcrumb + `...`. Never table-less.
- **Example:** [[Life]].

# BRIEF

- **This file is the spec for the anchor entry page (`{slug}.md`)** — the `.anchor` + page **template**, the **parts**, and the **ruleset** `R-anchor-page`. Format *authority*: `/create anchor`, `/rewire`, `/tidy`, `/audit anchor`, and the audit scripts cite it.
- **Don't inline what belongs elsewhere.** Dispatch-table *mechanics* → [[FCT Dispatch Table]]; row *placement / order* → [[SKA Decisions|D07]]; the naming prefix → [[FCT Naming]]; sub-folder dispatch pages have their own facets. Link, don't duplicate.
- **Examples are never instantiated here** — they live in the `examples/` gallery ([[FEX]]); the masthead `Examples` row links to them by kind. This page carries the template + parts + the ruleset only. If the spec changes, fix the examples — never retrofit the spec to a stale copy.
