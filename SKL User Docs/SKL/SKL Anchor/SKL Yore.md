---
description: "`/yore` archives a folder or file to **Yore**, the standard archival location."
---
# /Yore

`/yore` archives a folder or file to **Yore**, the standard archival location. It zips the target (excluding `.git/`, build artifacts, and `DerivedData/`), names the archive `{CREATION_DATE} {Original Name}.zip` (date prefix uses the *creation* date of the folder, not today's), drops it in the appropriate parent `Yore/` subfolder (creating one if missing), removes the original, and cleans up references — HookAnchor commands, broken symlinks in user-installed tool locations, and dispatch table entries. Use it when you say "yore it," "archive this," or "archive to yore."

Reach for archive vs delete based on whether the content might be useful later: when in doubt, archive — storage is cheap and lost work is expensive. Build artifacts, temp files, and pure duplicates can be deleted outright; everything with reference value, history, or restore potential should go to Yore.
