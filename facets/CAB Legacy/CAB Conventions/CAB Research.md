---
description: Research folder layout, paper structure, citation handling
---
# CAB Research

Conventions for research-oriented anchors — folder layout, paper section/log/appendix naming, and reference files.

Rules for research-oriented anchors. See also [[Paper Anchor]].

## Research Folder
- `{NAME} Research/` — Contains research materials
- `{NAME} References.md` — Bibliography and reference links
- `{NAME} Related Work.md` — Analysis of related work

## Paper Structure (if writing papers)
- Section files: `{NAME} 1 Introduction.md`, `{NAME} 2 Methods.md`, etc.
- Log files for each section: `{NAME} 1 Introduction Log.md`
- Appendix files: `{NAME} A1 - Topic.md`
- Experiment series: `{NAME} B1 - Experiment Name.md`

# BRIEF

- **This is a CAB convention spec for research-flavored anchors** — it defines the canonical folder layout, paper section filename pattern, and reference-file names that research anchors are expected to follow. Edits here change what the curator audits/applies across all research anchors.
- **NOT for** anchor-instance content, individual paper drafts, project-specific research backlogs, or bibliography entries — those live in the actual research anchor under `{NAME} Research/`. Keep this file purely as the rule, never as an instance of the rule.
- **Inclusion test:** a thing belongs here if it is a *naming / structural convention* that applies to every research-flavored anchor (Paper trait or research subsystem). One-off project quirks do not belong; they go in the anchor's own `{NAME} Rules.md` or `{NAME} Decisions.md`.
- **Naming convention is load-bearing** — `{NAME} <number> <Title>.md` for sections, `{NAME} <number> <Title> Log.md` for logs, `{NAME} A<n> - <Topic>.md` for appendix, `{NAME} B<n> - <Name>.md` for experiments. Tooling (TOC generation, audits, dispatch tables) may key off these patterns; do not introduce alternative shapes without updating consumers.
- **Cite, do not inline,** related CAB facets — `[[Paper Anchor]]` is the trait spec; deeper structural rules (dispatch tables, TLDR, Brief) live in their own CAB facets and must not be duplicated here.
- **Keep the body lean** — a short bulleted catalog of file/folder names is the right shape. Resist promoting this file into a tutorial on how to write papers; that is out of scope.
