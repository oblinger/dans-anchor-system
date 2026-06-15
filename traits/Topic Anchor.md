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

Anchor-page kinds catalog: [[FCT Anchor Page]]. Synthetic Topic example: *(none yet)*; real instances: [[Life]], [[Food]], [[Legal]].

# BRIEF

- **This file is the spec for the Topic Anchor trait** — it defines what a Topic Anchor IS (no-code, evergreen, vault-resident, routing-hub-shaped) and how it deltas from [[CAB Base]]. Edits here change the trait contract for every anchor that carries it.
- **NOT a catalog of topic anchors** — do not list individual Topic Anchor instances (SYS, MY, etc.) here beyond the one Example block. The Example is illustrative, not exhaustive; new instances go in the vault, not in this spec.
- **Inclusion test for content on this page**: does the rule apply to *every* Topic Anchor (or to the trait-application decision)? If yes, it belongs here. If it applies to only one anchor, it belongs in that anchor's `{NAME} Rules.md` / `{NAME} Decisions.md`. If it applies to all anchors regardless of trait, it belongs in [[CAB Base]].
- **Deltas-only discipline** — only document differences from [[CAB Base]]. Do NOT restate Base rules. If a section would just duplicate Base, omit it.
- **Load-bearing constraints**: the "No repository" delta (no `.git/`, no `code:` key, no CLAUDE.md) and the "lives within the Obsidian vault" constraint are what distinguish Topic from Code/Project traits — breaking either silently reclassifies the anchor. The Audit § Conditional structure rules guard against accidental Code-trait drift.
- **Linking convention**: this trait is referenced by name ("Topic Anchor") from `.anchor` config and from [[CAB Base]] / [[CAB Traits]] dispatch tables; rename only via a coordinated rewire across CAB.
