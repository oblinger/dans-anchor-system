---
description: "`/dupes` sweeps the vault for duplicate `.md` filenames — files with the same basename in two or more places — and emits a confidence-ranked **edit list** (`E1`, `E2`, ...) of proposed fixes: delet…"
---
# /Dupes
`/dupes` sweeps the vault for duplicate `.md` filenames — files with the same basename in two or more places — and emits a confidence-ranked **edit list** (`E1`, `E2`, ...) of proposed fixes: delete this stale copy, merge these two, rename to disambiguate, or leave alone. It reads the actual content of each pair (not just paths) before recommending anything, so the suggestion comes with a one-line characterization like "byte-identical," "one is empty," "one looks like a later version," or "different content, same name (coincidental)."

| -[[SKL Dupes]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Hygiene]] → [SKL Dupes](hook://p/SKL%20Dupes)<br>: the SKL Dupes doc |
| --- | --- |
| Related | [[skills/dupes/SKILL.md\|SKILL]],   |
| [[SKL Dupes Design\|Design]] |  |

You reply in plain English — "do all high," "E5 option C," "E12 leave alone," "X is also expected" — and the skill executes. Common false-positives (`SKILL.md`, `README.md`, deliberate per-anchor copies) are suppressed via two allowlist files; if you mark a specific group "reviewed-OK," the exact path set is remembered so it won't re-surface unless the files change. Useful for catching misplaced copies, partial moves, and accidental file duplication across the vault. Add `--dry` to see the list without executing anything.
