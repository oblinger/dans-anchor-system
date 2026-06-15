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
- [[ABP]] *(Alien Biology Paper — the canonical paper project)*
- [[ASP]] *(Alienbio Safety Paper — legacy-formatted, version table TBD)*

*(Only ~1–2 genuine paper projects exist in the vault. The giveaway is a `## Version history` **version table** with `s1, s2, s3 …` per-section markup (per [[Paper Anchor]]) — NOT promotable from research reports or paper collections.)*

### SKA sub-project
- [[FCT Code Repository]]
- [[FCT Naming]]
- [[DSC verification]]
- [[DSC Linked Mode]]
- [[SKL Doc]]

### Container
- [[Log]] *(grouped — many entries per row)*
- [[SV]] *(list — `---` auto-generates one row per entry)*
- [[RR]] *(list — `---` auto, one row per entry)*
- [[Roots]] *(list)*
- [[Journal]] *(chronological)*

**TLDR** — **Cardinality: one per anchor.** Every anchor has exactly one `{slug}.md` entry page. It opens with YAML `description:` frontmatter, then H1 → one-line summary → optional figure → dispatch table (breadcrumb + Related + kind-specific rows). The embedded `R-anchor-page` ruleset (23 shared rules + five kind deltas — Topic / Code / Paper / SKA sub-project / Container) is the auditable contract; `/audit anchor` and `/create anchor` cite it. Member groups appear only on Container anchors; a Topic carries a `...` auto-summary of its contents.



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

### RULE R-anchor-page-18 — List = one row per member; grouped = many per row (sampled)

A **list** member zone puts **one member per row** (a `| --- | |` auto-list generates exactly that); a **grouped** zone puts **many members per row** under labeled `+` group rows. The split is **structural** (rows-per-member), not a count — though a flat list is usually grouped once it grows past ~15 ([[DSC granularity]]).

**Check pattern:** rows-per-member — one-per-row (list) vs many-per-row / `+` groups (grouped). ([[DSC granularity]])

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

### RULE R-anchor-page-23 — Track row, and Status-triggered full scaffolding (checked)

Parallel to the Design row (R-anchor-page-13): a **`Track` row** is present iff `{NAME} Track/` exists — it links the track dispatch `[[{NAME} Track\|Track]]`, members in the fixed order **Backlog → Status → Messages → Discussion → Inbox → Icebox → Log → ask**. (Roadmap + Features are *design* artifacts — they live in the Design row, not here, per the 2026-06-10 restructure.)

**The status document is the full-scaffolding signal.** When `{NAME} Status.md` exists, the anchor is a **fully-scaffolded** project and MUST carry the **complete** design + track doc set:

- **Every design document exists** (created even if empty), in `{NAME} Design/`, listed in the `{NAME} Design` dispatch, and surfaced as the **full Design row** in the PRD-first order of R-anchor-page-13: PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features.
- **Every track document exists** (created even if empty), in `{NAME} Track/`, listed in the `{NAME} Track` dispatch, and surfaced as the **full Track row** in the order above.
- **Each doc is linked in all three places** — its folder's dispatch page (the Design anchor / the Track anchor) **and** the matching masthead row. The two folders and the two masthead rows must agree.

Absent a Status doc, the Design / Track rows may be **partial** — listing only the docs that actually exist. The Status doc is what flips a project from partial to full. **This holds for most Code projects.**

**Check pattern:** `{NAME} Status.md` exists ⇒ assert (a) every design doc + every track doc exists (empty allowed), (b) each is listed in its dispatch page, (c) the masthead Design + Track rows carry the full sets in the fixed orders. ([[SKA Decisions|D07]], [[FCT Design Dispatch]], [[FCT Track Dispatch]])

## Kind-specific rules

Each anchor-page **kind** layers a small delta over the shared chassis (R-anchor-page-01…23) plus the [[FCT Dispatch Table]] form. The kind is read from `traits:`; a page is audited as **chassis + its kind's delta**. There are five kinds, each one-to-one with its dispatch-table shape (HookAnchor computes the table from the `.anchor`, so there is exactly one page — and one table kind — per anchor). The deltas are thin; each may graduate to its own `include::` sub-ruleset file once it grows.

### R-anchor-page-code — Code project (stated)

A code/software project anchor (`traits: [Code]`).
- **Masthead roster:** breadcrumb + Anchor + **Design** (iff `{NAME} Design/` — R-anchor-page-13) + **Track** (iff `{NAME} Track/` — R-anchor-page-23) + Related.
- **Full scaffolding when a Status doc exists** — `{NAME} Status.md` present ⇒ the complete design + track doc set exists (even empty) and is linked into both dispatch folders and the masthead Design + Track rows (R-anchor-page-23). True for most Code projects.
- **Member zone:** none — a switchboard masthead only.
- **Example:** [[HBR]].

### R-anchor-page-paper — Paper project (stated)

A long-form writeup anchor (`traits: [Paper]`) — a paper / whitepaper that goes through revision cycles. **Signature / giveaway:** a `## Version history` **version table** of dated drafts with `s1, s2, s3 …` per-section markup (track-changes HTML per section). Full trait spec: [[Paper Anchor]].
- **Masthead roster:** breadcrumb + a **Drafts** row (dated versions, newest = Current) + **Research** + optional **External** (published landing) + Related; ends with `...`.
- **Member zone:** the version table under `## Version history` (the dated-draft × section-markup grid).
- **Example:** [[ABP]].

### R-anchor-page-subproject — SKA sub-project: facet / discipline / skill-doc (checked)

A single skill-ecosystem spec page — a **facet**, a **discipline**, or a **skill-doc** (the documentation page for a skill; *not* the skill folder's `SKILL.md` runbook, which is out of scope).
- **Masthead roster:** breadcrumb + Anchor + **Design** (only if a `{NAME} Design/` folder exists) + Related.
- **Owns Design, not Track** — every SKA sub-project anchor (skill / facet / discipline / example) **owns its own design but never its own tracking**. Per [[SKA Decisions|D08]] all activity-tracking for the skills ecosystem lives on the **shared SKA surface** (`SKA Backlog` / `SKA Features` / `SKA Messages` / …); a per-anchor `{NAME} Track/` is forbidden for these kinds.
- **No `Track` row** — follows from the above (this is R-anchor-page-15 in kind terms).
- **Minimum shape** — a dispatch table + a `{NAME} Design/` folder that may hold **only its `.anchor` marker** (no design docs yet). It grows by adding `{NAME} PRD.md` and other design docs as the anchor earns them — many skills / facets need little design. The Design row (R-anchor-page-13) appears once the folder holds linkable docs.
- **Flat layout** — `{NAME} Design/` sits **directly under the anchor root**, with **no `{NAME} Docs/` wrapper** (the wrapper is for large project anchors; SKA sub-projects stay flat).
- **Member zone:** none.
- **Content** differs by sub-kind (facet spec vs. discipline vs. skill-doc) but the page *structure* is shared — one ruleset, three example flavors.
- **Examples:** facet → [[FCT Anchor Page]]; discipline → [[DSC progressive-disclosure]]; skill-doc → [[SKL Mint]] *(currently a thin doc with no masthead — the bring-up target, tracked separately; do not treat as compliant).*

### R-anchor-page-container — Container: grouped / list / reverse-dated (sampled)

A [[Collection]] anchor whose body enumerates **homogeneous members** (a features folder of feature docs, a log folder of log entries, the `SKL` catalog of skill-docs).
- **Masthead roster:** breadcrumb + Anchor + Related (minimal).
- **Member zone required** — the generic member rules R-anchor-page-17…20 apply. The layout split is **structural — rows-per-member — not a count** (one axis, three values):
  - **list** — **one row per member** (each row is a single entry). A `| --- | |` separator auto-generates exactly this: HookAnchor emits one row per child. Count is irrelevant — a 30-entry auto-list is still a list. Examples: [[SV]], [[RR]], [[Roots]], [[SKA Access]].
  - **grouped** — **each row is a group holding many members** (a category row, often `+`-expandable, carrying several links). Typically chosen once a flat list grows past ~15 ([[DSC granularity]], R-anchor-page-18), but the defining mark is **many-members-per-row**. Examples: [[Log]], [[FCT]], [[SKL]].
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
