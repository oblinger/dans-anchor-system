# cab-yore — Archiving to Yore

Archive anchors, folders, or files that are no longer needed. Yore is the standard archival location.

## Yore Location

Every grouping folder can have a `Yore/` subfolder for archived content. Place the archive in the Yore folder of the **parent** that contained the archived item:

```
~/ob/kmr/SYS/Bespoke/Yore/          ← archives from Bespoke projects
~/ob/kmr/prj/PP/Yore/               ← archives from PP projects
~/ob/proj/Yore/                      ← archives from code repos
```

If no `Yore/` folder exists, create one.

## Archive Naming

```
{CREATION_DATE} {Original Name}.zip
```

- **CREATION_DATE** — the creation date of the folder being archived (not today's date), in `YYYY-MM-DD` format. Use `stat -f "%SB" <folder>` on macOS to find it.
- **Original Name** — the folder name as it was before archiving

Example: `2025-08-20 WhisperFlow.zip`

## Workflow

1. **Zip** the folder, excluding `.git/` and build artifacts:
   ```bash
   zip -r archive.zip FolderName/ -x "FolderName/.git/*" "FolderName/build/*" "FolderName/DerivedData/*"
   ```

2. **Move** the zip to the appropriate `Yore/` folder with the date-prefixed name

3. **Remove** the original folder

4. **Update references**:
   - Remove or update HookAnchor commands (`ha -d`)
   - Remove broken symlinks in `~/bin/`
   - Update any dispatch tables that referenced the archived item

## When to Archive vs Delete

- **Archive** when: the content might be useful for reference, has history worth preserving, or the user might want to restore it
- **Delete** when: the content is truly disposable (build artifacts, temp files, duplicates)
- When in doubt, archive — storage is cheap, lost work is expensive
