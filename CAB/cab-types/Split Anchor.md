# Split Anchor

Follows [[CAB Base]] with these deltas:

## When to Use

Projects with both documentation in the Obsidian vault and a code repository that should not be inside the vault.

## Deltas from Base

- **`Code` symlink** — always named `Code`, points to the repo regardless of its actual name
- **Repo outside vault** — lives under `~/ob/proj/`, not in the vault
- **CLAUDE.md** — present at anchor root (in vault)
- **Doc sync** — `{NAME} User/` and `{NAME} Dev/` sync-pushed to the repo's `docs/` via pre-commit hook

## Structure Additions

```
~/ob/kmr/prj/{CAB Folder}/       ← in vault
├── ...                              (base structure)
├── {NAME} Inbox.md
├── CLAUDE.md
└── Code -> ~/ob/proj/{project}/{repo}

~/ob/proj/{project}/{repo}/          ← outside vault
├── .git/
├── README.md
├── docs/
│   ├── user/
│   └── dev/
└── src/
```

## Setup Checklist (additions to base)

1. Create `Code` symlink → repo path
2. Register sync-push targets if User/ or Dev/ docs exist
3. Add pre-commit hook to repo for doc sync
