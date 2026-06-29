---
description: Conventions — the standardized practices shared across anchors.
---

| -[[CAB Conventions]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[CAB Legacy]] → [CAB Conventions](hook://p/CAB%20Conventions)<br>: Conventions — the standardized practices shared across anchors. |
| --- | --- |


# What is a Convention

A **convention** is a standardized practice that recurs across anchors. Conventions cover everything from how files are named to how dispatch tables are formatted to how Rust crates should be structured. They're spec documents that humans and agents read and follow.

Conventions differ from **facets** (which are named roles an anchor *carries* — Backlog, PRD, Architecture) in that conventions describe *how to do something* rather than *what kind of thing exists*. A convention can apply to many facets, or to no facet at all (e.g., a folder in `Templates/` that adopts the [[CAB Template File]] convention has nothing to do with anchor structure).

A few conventions are wired into automated checks (`/audit`, `/rule check`, lint scripts); most are prose. The distinction is presentational, not categorical — a convention is a convention regardless of whether it's currently enforced by tooling.


# Conventions

| Convention | Description |
|---|---|
| [[CAB Naming Conventions]]      | Slugs, the `{NAME}` prefix rule, file/folder naming, auxiliary commands |
| [[CAB Page Conventions]]        | Anchor page format — description field, breadcrumb, dispatch table conventions |
| [[CAB Markdown Formatting]]     | Vertical spacing, named lists, file trees, table of contents, dispatch tables, cards, track changes |
| [[CAB Docs Conventions]]        | Standard documents — PRD, Roadmap, Backlog, etc. — and the formats each follows |
| [[CAB Documentation Publishing]]| Private vs user docs, MkDocs setup, generators, where published docs live |
| [[CAB Repository Structure]]    | Key repo files, `justfile`, `site/` folder, doc-sync layout |
| [[CAB Integrations]]            | Git, GitHub Pages, Claude Code, tmux — how external tools wire in |
| [[CAB Research]]                | Research folder layout, paper structure, citation handling |
| [[CAB Rust Rules]]              | Workspace layout, shared util crate, Cargo conventions |
| [[CAB Maintenance]]             | Validation checklist — what an anchor should look like at rest |
| [[CAB Defined Terms]]           | Glossary — dated folders, dated sections, vocabulary used across CAB |
| [[CAB Template File]]           | Template file at the head of a homogeneous folder — exemplar above, spec below |

# BRIEF

- **This page is the umbrella catalog for CAB conventions** — standardized practices (naming, formatting, repo structure, etc.) that recur across anchors. Each row in the Conventions table links to a sibling `CAB <X>.md` spec.
- **NOT a place for the convention content itself.** Each convention has its own dedicated `CAB <X>` page; only the row + one-line description lives here. Do not inline spec prose into this catalog.
- **Inclusion test:** a thing belongs in the Conventions table if it is a *how-to-do-something* practice (format, layout, naming) that may apply across multiple anchors or facets. *What kind of thing exists* (named roles like Backlog, PRD) belongs under [[CAB Facets]], not here.
- **Row format:** `| [[CAB <Name>]] | one-line description |`. Use the exact basename of the sibling spec page as the wiki-link; keep the description short enough to fit one table row.
- **Keep alphabetical-ish-by-category order intact** — naming/page/markdown/docs cluster first, then publishing/repo/integrations, then domain-specific (research, rust), then maintenance/glossary/template. New rows slot into the matching cluster, not appended blindly at the bottom.
- **Load-bearing distinction from facets**: conventions describe *how to do something*; facets describe *what kind of thing exists*. If a candidate row reads as "every anchor has one of these," it is a facet — move it to [[CAB Facets]] instead.
