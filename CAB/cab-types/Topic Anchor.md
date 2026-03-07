# Topic Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

System configuration, knowledge domains, reference areas — anything that is evergreen, has many supporting files, but is not a code project.

## Deltas from Base

- **No repository** — no `.git/`, no `Code` symlink, no CLAUDE.md
- **Child anchors** — may contain sub-topic folders that are anchors themselves
- **Routing hub** — anchor page links to sub-topics or content pages rather than containing content directly
- Lives within the Obsidian vault

## Structure Additions

Beyond the base structure, a Topic Anchor may contain child anchor folders:

```
{CAB Folder}/
├── ...                              (base structure)
├── {Sub-Topic}/                     child anchors
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
