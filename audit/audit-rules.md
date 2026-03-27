# Rules — Audit Code Against Project Rules

Check the codebase for rule violations. This is a thin wrapper that delegates to `/rule check --all`.

## Workflow

1. Verify the project has a rules file (`cab-config get rules`)
2. If no rules file exists, report "No rules configured — skip" and return
3. Run `/rule check --all` — full scan of all source files against all rules
4. The rule check skill handles grading, exception management, and posting to stat
