# Topic Anchor

The Topic Anchor trait — a no-code, evergreen anchor that lives inside the Obsidian vault and serves as a routing hub for sub-topics or content pages.

Follows [[CAB Base]] with these deltas:

## When to Use

System configuration, knowledge domains, reference areas — anything that is evergreen, has many supporting files, but is not a code project.

## Deltas from Base

- **No repository** — no `.git/`, no `code:` key in `.anchor`, no CLAUDE.md
- **Child anchors** — may contain sub-topic folders that are anchors themselves
- **Routing hub** — anchor page links to sub-topics or content pages rather than containing content directly
- Lives within the Obsidian vault

## Structure

```
{CAB Folder}/
├── {CAB Folder}.md                  marker file
├── {NAME}.md                        anchor page (routing hub)
├── {NAME} Docs/                     planning docs (optional)
├── {Sub-Topic}/                     child anchors (optional)
├── {Sub-Topic}/
└── ...
```

## Example

SYS — system setup and configuration:

```
SYS/
├── SYS.md
├── SYS Docs/
│   └── SYS Plan/
├── Claudifier/                      child anchor (CLF)
├── personal-curation/               child anchor (PC)
└── DictaMUX/                        child anchor (DMUX)
```

## Audit

Type-specific structure checks for Topic Anchors.

### Required files
- `{NAME} Docs/` folder with dispatch page
- `{NAME} Docs/{NAME} Plan/` folder with planning docs

### Conditional structure
- Create `{NAME} Dev/` folder only when another trait requires it (e.g., Code trait)
- Create `{NAME} User/` folder only when another trait requires it (e.g., Code trait)
- Add a `code:` key to `.anchor` only when the anchor gains the `code` trait

## Anchor-page example

Anchor-page kinds catalog: [[FCT Anchor Page]]. Synthetic example: [[Knots]]; real instances: [[Life]], [[Food]], [[Legal]].

# BRIEF

*(Maintainer note — cautions for whoever edits this trait spec.)*

- **Inclusion test** — content belongs here only if it applies to *every* Topic Anchor (or to the trait-application decision). A one-anchor rule → that anchor's `{NAME} Rules.md` / `{NAME} Decisions.md`; an all-anchor rule → [[CAB Base]]. Document deltas from Base only — don't restate Base. Not a catalog: don't list individual Topic Anchor instances (SYS, MY, etc.) beyond the one illustrative Example block.
- **Don't regress the load-bearing deltas** — "No repository" (no `.git/`, no `code:` key, no CLAUDE.md) and "lives within the Obsidian vault" are what distinguish Topic from Code; breaking either silently reclassifies the anchor. The Audit § Conditional structure rules guard against accidental Code-trait drift.
- **Linking convention** — this trait is referenced by name ("Topic Anchor") from `.anchor` config and from [[CAB Base]] / [[TRT]] dispatch tables; rename only via a coordinated rewire across CAB.
