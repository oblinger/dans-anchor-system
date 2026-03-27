# Topic Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

System configuration, knowledge domains, reference areas — anything that is evergreen, has many supporting files, but is not a code project.

## Deltas from Base

- **No repository** — no `.git/`, no `Code` symlink, no CLAUDE.md
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

### Not expected
- No `{NAME} Dev/` folder (topics don't have code)
- No `{NAME} User/` folder
- No `Code` symlink
