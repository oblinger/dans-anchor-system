# Consider — Recommend and Apply Standard Rule Sets

Analyze a project's codebase, recommend which standard rule sets apply, and apply the approved ones. This is a single workflow: recommend → user approves → apply.

## When to Use

When setting up rules for a new project, or when new standard rule sets have been created and you want to evaluate whether they apply to an existing project.

## Workflow

### 1. Load Available Rule Sets

Read all files in `~/.claude/skills/rule/rulesets/`. Each has:
- `description:` in frontmatter — what the rule set covers
- `applies-when:` in frontmatter — conditions for applicability

### 2. Analyze the Project

Read the project's codebase to understand:
- Languages and frameworks used
- Architecture patterns (event-driven, async, client-server, CLI, etc.)
- Configuration approach (XDG, dotfiles, embedded, etc.)
- Existing rules file (if any) — what's already covered

### 3. Generate Recommendation Table

For each rule set, assess whether it applies and produce a table:

| Rule Set | Recommendation | Rationale |
|----------|---------------|-----------|
| xdg-config | **Apply** | Uses ~/.config/skl/ for configuration |
| async-coordination | **Apply** | Multi-threaded speech engines, event stream |
| no-heuristics | **Already present** | Custom version exists — verify alignment |
| markdown-standards | **Skip** | Not documentation-heavy |

**Recommendation values:**
- **Apply** — rule set is relevant, should be added
- **Already present** — project has equivalent custom rules; note for user to verify alignment
- **Skip** — rule set doesn't apply to this project
- **Consider** — might apply, needs user judgment

Present the table to the user and discuss. The user approves, rejects, or adjusts each recommendation.

### 4. Apply Approved Rule Sets

For each approved rule set:

1. Find the project's rules file (via `cab-config get rules`)
2. If no `## Standard Rule Sets` section exists, create one at the bottom of the file
3. Add an Obsidian embed reference: `![[ruleset-name]]`
4. Add an empty exception table below it with the Rule column:

```markdown
![[xdg-config]]

| EX | Grade | Location | Rule | Description |
|-----|-------|----------|------|-------------|
```

The exception table starts empty — exceptions will be added as `/rule check` finds violations against the standard rules.

### 5. Post to Stat

```bash
skl-stat add "Done" "rule sets" "Applied 3 standard rule sets: xdg-config, async-coordination, error-handling"
```

## Notes

- Standard rule sets use set-prefixed R-numbers (R-XDG01, R-AC02) that are stable across projects
- The exception table for standard rules has a **Rule column** tying each exception to the specific rule it violates
- Groups (rule sets that reference other rule sets via `![[other-set]]`) are expanded recursively
- Applying a rule set is just adding the reference — the rules themselves live in the rulesets folder and are shared
