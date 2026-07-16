---
description: The Brief doc facet — agent-facing per-file editing-and-maintenance content paired with a source file (the `# BRIEF` section / sidecar). Briefs are for the agent about to edit the file, NOT for the user reading it.
---

# DAS Brief
A **Brief** is a **document facet** — agent-facing per-file editing-and-maintenance content paired with a source file (inline `# BRIEF` section in Phase 1; `<Name> Brief.md` sidecar in Phase 2).

| -[[DAS Brief]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Brief](hook://p/DAS%20Brief) |
| --- | --- |
| Related | [[DAS Discussion]],  [[DAS progressive-disclosure]],  [[DAS file-association]],  [[Briefs]],   |
| Examples | [[SV Roots\|inline # BRIEF (Phase 1)]],  [[SV Roots Brief\|sidecar Brief.md (Phase 2)]],   |
| Rules | [[R-brief]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

> [!note] Classification — doc facet, peer to [[DAS Discussion]]
> Brief is a **doc facet** (a content container attached to a document), not a discipline. It lives in `CAB Facets/Doc Facet/` alongside [[DAS Discussion]]. As a doc facet it *cites* three disciplines:
> - **[[DAS file-association]]** — *how it attaches*. Brief is a **non-dated, typically-single** typed association: method 1 (inline `# BRIEF`, default), method 2 (sidecar `{Parent} Brief.md`), escalating to method 3 (a `{Parent} Briefs/` folder) only if a parent accumulates many. This is the exact parallel to Discussion, which attaches via file-association's **dated** specialization [[DAS dated-entry-stream]]; Brief cites the umbrella directly because it adds no dated rules (per [[DAS granularity]]).
> - **[[DAS progressive-disclosure]]** — *reader-zone layering*. The TLDR → Overview → Body → Brief zones below are progressive disclosure by audience/depth.
> - **[[DAS markdown]]** — how the prose is written.

> [!important] Audience: agent, not user
> A Brief is something an agent reads **before editing** the source file. Users glancing at the file should NOT need to read the Brief to understand what the file is — that's what the one-sentence TLDR (and optional Overview) at the top of the source are for. See § Audience — three reader zones.

> [!info] Phase 1 — inline `# BRIEF` H1 (2026-06-10)
> Until the read-hook is built that auto-surfaces a sidecar brief to the agent, briefs live **inline** as a `# BRIEF` (ALL CAPS) H1 section at the **bottom** of the source file. The agent reads the file → sees the section → uses it. No tooling required.
>
> When the read-hook ships, briefs migrate mechanically to **Phase 2 — sidecar files** (`<Source Name> Brief.md` in the same folder, surfaced via the `Related` row in the source's dispatch table or a `(See ...)` line beneath the H1). The migration is purely mechanical — split the source on `# BRIEF`, write the brief content to the sidecar, add the `Related` row or `(See …)` line — and is scriptable vault-wide in one pass. The Phase 2 form is described in the rest of this spec for forward reference.
>
> A vault-wide registry of files carrying inline briefs lives at [[Briefs]].

> [!info] Renamed 2026-06-09
> Previously called "Guide." Renamed to "Brief" to disambiguate from `<App> User Guide.md` (product documentation for end-users). A brief is *operational content for the agent/maintainer about to edit a file*; a user guide is *how-to-use-the-app content for end-users*. Two different audiences, two different jobs — different words.

**Cardinality: many per anchor** — each source file may have its own Brief; a project accumulates as many Briefs as there are source files that carry one.

## Audience — three reader zones in every source file

Every source file the user owns has three concentric reader zones, each with a different audience and a different content shape:

| Zone | Audience | Length | Content |
| --- | --- | --- | --- |
| **TLDR** — one sentence immediately under the H1 | **User**, glance-readers, link-followers | One sentence | What this file IS, in plain language. Should usually be enough; user clicks through to the body only if they need more. |
| **Overview** — optional H2 section after the dispatch table | **User**, deeper-readers | A few sentences to a short paragraph | Only added when the one-sentence TLDR genuinely isn't enough. Skip it if the body opens with self-explanatory content. |
| **Body** | User + agent | As long as the content needs | The actual catalog / rules / state / content the file holds. |
| **Brief** (`# BRIEF` at bottom, or sidecar in Phase 2) | **Agent only** | Tight — 4-7 bullets typical | How to maintain the body. Editing rules, inclusion tests, naming conventions, "don't pile X here" guards. |

**Authoring discipline for the agent writing a Brief:**

- The Brief is the place for *how to edit this file correctly*. The user-facing zones (TLDR, optional Overview, body) handle *what this file is* and *what it contains*.
- **Body discipline: less is more.** Give the user just enough basic orientation that they know what the file is for. The TLDR usually carries that load by itself; an Overview is added only when one sentence genuinely isn't enough. Don't pad the body with content the user wouldn't actively want to read.
- **It's fine for detail to live only in the Brief.** The Brief can hold editing-rule context — including some incidentally-factual content — that doesn't appear elsewhere in the source. If a user wants that detail, they click through to the Brief; the Brief is a *click away*, not a separate file.

## What belongs in a Brief

**Distillation policy (F223, ratified).** A Brief holds **only genuine file-specific maintainer notes** — non-obvious guidance for whoever edits the source: inclusion tests, don't-regress cautions, tooling-consumed identifiers, cross-reference-integrity obligations. Because specs and their Briefs are read by outside readers (the DAS repo is published), a Brief opens with a **slim, clearly-labeled lead-in** — an italic `*(Maintainer note — …)*` line naming what the note covers and pointing at where the normative content lives — as piloted on [[DAS Template]]. Three consequences:

- **Normative spec never lives only in a Brief.** Rules, models, and constraints a reader must follow belong in the source's body or its RULESET; the Brief may at most point at them.
- **Generic doc-advice is a one-link cite.** Guidance true of all documents (progressive disclosure, no-fence, lead-with-example) belongs to its governing discipline ([[DAS markdown]], [[DAS progressive-disclosure]]) and is cited, never restated.
- **Most files need no Brief at all.** After distilling out spec, generic advice, and body-redundant content, if nothing genuinely file-specific remains, carry no `# BRIEF` section — never pad one into existence.

Per-file operational content **for the agent**. Concretely:

- "What this page is for / NOT for" — phrased as an *editing rule* (e.g. "don't pile cross-anchor content here") rather than as content (e.g. "this page lists X, Y, Z").
- "The inclusion test — when does a thing belong here?"
- "How to add a row — naming conventions, link format, grouping rules."
- "Local-vs-remote shape — how the format differs by row kind."
- Examples of legal and illegal entries.
- Load-bearing maintenance traps ("don't rename without updating Keyboard Maestro bindings", "the inline brief is what the registry tracks; don't delete the H1 marker").

## What does NOT belong in a Brief

- **Normative spec content** (rules, models, constraints a reader must follow) → the source's body or its RULESET. Spec may never live *only* in a Brief.
- **Generic doc-advice** (true of all docs — progressive disclosure, no-fence, lead-with-example) → the governing discipline ([[DAS markdown]], [[DAS progressive-disclosure]]), cited with one link, never restated.
- **Project-wide rules** → `CLAUDE.md`.
- **Markdown-rendering rules** → [[R-markdown]].
- **Facet-shape conventions** (every Backlog has horizons, every Rules file is a RULESET) → `CAB <Facet>.md`.
- **Trait-wide rules** (every Skill anchor has X) → `CAB <Trait>.md`.
- **Anchor-local rules** that apply to many files in the anchor → `{slug} Rules.md` or `{slug} Decisions.md`.
- **End-user documentation** (how to use the application) → `<App> User Guide.md`. Briefs are for editors; user guides are for end-users.

The brief is for rules truly specific to one source file.

## When to write a Brief

The trigger: the source file would otherwise carry a `## Design` (or equivalent) H2 that takes up most of the file with prose explaining how to maintain the table or list above. That prose is what extracts into a Brief.

**And when not to:** most files need no Brief. Write one only when genuine file-specific maintainer notes exist after the distillation policy is applied (§ What belongs in a Brief); an empty or padded Brief is worse than none.

## File location and naming

- **Location:** same folder as the source file.
- **Naming:** `<Source Name> Brief.md` — exactly the wiki-link the source uses to point at the brief.

Example: `~/ob/kmr/SV/SV Roots/SV Roots.md` ↔ `~/ob/kmr/SV/SV Roots/SV Roots Brief.md`.

## How it's surfaced from the source file

Two cases — pick by whether the source has a dispatch table.

### Case 1 — Source has a dispatch table

Add a `Related` row to the dispatch table (or use an existing one) listing the brief first:

```markdown
| Related | ~~[[<Source Name> Brief\|Brief]]~~,  …other related links… |
```

The Brief always goes first in the Related cell. Other related items follow, comma-separated.

### Case 2 — Source has no dispatch table

Add a single `(See …)` line immediately under the H1, before any other content:

```markdown
# My Page

(See ~~[[My Page Brief]]~~)

[…rest of content…]
```

For multiple related links: `(See ~~[[<X> Brief]]~~, ~~[[Y]]~~, ~~[[Z]]~~)` — all wiki-links comma-separated, all inside one set of parens. No colon after "See".

## File structure

The brief file is just normal markdown. No frontmatter required. Both forms (inline `# BRIEF` and sidecar) open with the italic `*(Maintainer note — …)*` lead-in, followed by a tight bullet list; H2/H3 sub-sections appear only when the source genuinely needs them. Common sidecar shape:

```markdown
# <Source Name> Brief

Editing-and-maintenance brief for ~~[[<Source Name>]]~~. Read before adding rows, restructuring, or auditing.

## What this page is for
…

## What this page is NOT for
…

## The test for inclusion
…

## How to add an entry
…
```

The H1 of the brief matches the file basename. No further structural constraints.

## Constraints

- A brief is a sidecar to *exactly one* source file. If two source files share maintenance content, factor it to a higher-level brief (e.g., a DAS facet spec) and link from both.
- Briefs do not nest. A brief does not have its own brief.
- Briefs do not duplicate DAS facet specs, trait specs, or project-wide CLAUDE.md content. They carry only file-specific operational content.
- The wiki-link in the Related row (Case 1) or the `(See …)` line (Case 2) uses the exact basename of the brief file — no aliasing or renaming.
- Distinct from `<App> User Guide.md` — different audience (end-users vs. editors), different content (how-to-use-the-app vs. how-to-edit-the-source).
- **Briefs are agent-facing only.** User-facing orientation belongs in the one-sentence TLDR under the source's H1, with optional `## Overview` as the second tier. See § Audience — three reader zones.
- **Body discipline: less is more.** The body should give a user basic orientation, not mirror every detail the Brief carries. Detail that only the agent (or a click-through curious user) needs lives in the Brief; the body stays lean.
- **Opens with the labeled lead-in.** Every Brief begins with an italic `*(Maintainer note — …)*` line framing the content for outside readers (§ What belongs in a Brief).
- **Distill by relocation, never deletion.** When trimming a Brief, non-obvious content moves — into the source's body/ruleset, or to the governing discipline — it is never silently dropped.

## Worked example

[[SV Roots]] / [[SV Roots Brief]] — first realized example, established 2026-06-09. The source's dispatch table carries `| Related | [[SV Roots Brief\|Brief]], … |`; the design prose previously inline at the bottom of `SV Roots.md` lives in `SV Roots Brief.md`.

## Related

- ~~[[Doc Facet]]~~ / [[DAS Facets]] — parent catalog (Brief is a doc facet, peer to [[DAS Discussion]]).
- [[DAS progressive-disclosure]] — the discipline Brief cites for its TLDR → Overview → Body → Brief reader-zone layering.
- [[Briefs]] — vault-wide registry of files carrying inline `# BRIEF` H1 sections (Phase 1 form).
- [[SV Roots Brief]] — worked example of the Phase 2 sidecar form.
- F133 — tracking feature for the rule-system migration that surfaced the Brief discipline.
- F134 — Rule triggering (the read-hook mechanism that surfaces a brief when its source is read or written).
- F223 — the distillation sweep that ratified the maintainer-note policy (§ What belongs in a Brief) for the published DAS repo.

# BRIEF

*(Maintainer note — cautions for whoever edits this facet spec. The normative spec — including the distillation policy and the R-brief ruleset — is the body above.)*

- **This file is the rule, not an instance of the rule** — don't add per-source-file brief content here; discussion of *what a Brief is* belongs in the body.
- **Keep the two surface forms aligned** — Phase 1 inline `# BRIEF` and Phase 2 sidecar are one discipline; a spec change (e.g. Phase 2 shipping, the H1 convention evolving) must update both descriptions AND the worked examples ([[SV Roots Brief]] for Phase 2; the [[Briefs]] registry for Phase 1).
- **The "What does NOT belong" list is canonical in the body** — other specs and rules cite it; don't restate or fork it here or elsewhere.
