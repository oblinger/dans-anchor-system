# Rewire

Idempotent structural repair for any anchor. Ensures all files are linked, dispatch tables are wired, and the skeleton is consistent. Safe to run anytime — only adds, never deletes.

## Steps

1. Detect anchor type from `.anchor/config.yaml` or frontmatter `cab-type:`
2. Read the compiled checklist: `~/.claude/skills/code/code-rewire.compiled.md`
3. Execute the **All Types** section
4. Execute the section for this anchor's type (Code, Topic, or Skill)
5. Execute the **Universal Rules** section
6. Report what was fixed

## What Rewire Does NOT Do

- Does not create missing files — only links existing ones
- Does not modify file content — only touches dispatch tables and links
- Does not delete anything — purely additive
