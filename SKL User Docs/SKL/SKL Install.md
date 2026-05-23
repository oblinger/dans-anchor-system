# /Install

`/install` is the one-time setup skill for getting CAB command-line tools (`cab-scan`, `cab-config`, `skl-stat`, `cab-maintain`, `cab-lint`) onto a fresh machine. It creates `~/bin/` if it doesn't exist, symlinks the scripts from `~/.claude/skills/` into it, and verifies each one runs. After this you can use the `cab-*` and `skl-stat` commands from any shell.

You run it once when setting up a new machine, and again whenever a new CAB script is added to the toolkit. It's strictly a system-level wiring step — no anchor work, no edits to your projects.
