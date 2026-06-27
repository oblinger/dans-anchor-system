---
description: F017 — Standard Rule Sets
---
:>> [[SKA]] → [[SKA Track]] → [[SKA Features]] → [Standard Rule Sets](hook://p/2026-03-21%20Standard%20Rule%20Sets)

# [[Warden]] · F017 — Standard Rule Sets

Reusable libraries of rules that can be selectively applied to projects. Rule sets are maintained centrally and included by reference — changes to a standard rule set propagate to all projects that use it.

## Open Questions

1. **Obsidian embed syntax** — `![[xdg-config]]` works in Obsidian but agents need to resolve these programmatically. Should we use a different marker that's easier to parse (e.g., `@ruleset xdg-config`)?

2. **Rule renumbering** — Standard rules use set-prefixed numbers (R-XDG01). When checking, do we keep these numbers or renumber into the project's R-sequence? Keeping them means exceptions reference stable IDs across projects. Renumbering means cleaner project-local numbering but breaks cross-project references.

3. **Version pinning** — Should projects pin to a version of a rule set, or always use latest? Always-latest is simpler but a rule set change could break a project's exception tables.

## Proposed CLI

```
rule consider                              Analyze project, recommend rule sets
rule consider --show                       Show all available rule sets
rule apply <ruleset> [<ruleset>...]        Add rule set reference(s) to project rules file
rule catalog                               List all standard rule sets with descriptions
```

## Architecture

### Rule set folder

```
~/.claude/skills/rule/rulesets/
  rulesets.md              # dispatch page — lists all rule sets and groups
  xdg-config.md            # rules for ~/.config/ conventions
  async-coordination.md    # rules for async/threaded systems
  no-heuristics.md         # no fallbacks, magic numbers, timeouts
  event-driven.md          # event stream purity, listener behavior
  api-boundaries.md        # module encapsulation, no internal access
  naming-conventions.md    # naming patterns
  error-handling.md        # fail loud, no silent swallowing
  markdown-standards.md    # formatting rules
  testing-discipline.md    # red-green, test categories
  state-ownership.md       # single writer, explicit ownership
  cli-code-standard.md     # GROUP: xdg-config + no-heuristics + error-handling + naming
```

### Rule set file format

Each rule set has an H1 title, frontmatter with `description` and `applies-when`, and H3 rules with set-prefixed R-numbers:

```markdown
---
description: Rules for systems with async threads or event loops
applies-when: Project uses async/await, threads, dispatch queues
---

# Async Coordination

### R-AC01 — No Timeout-Based Coordination
RULE: Use sequence numbers and events to coordinate async work.

### R-AC02 — Main Thread Serialization
RULE: All state mutations must happen on a single designated thread.
```

### Group files (DAG)

A group is a rule set that references other rule sets:

```markdown
---
description: Standard rules for code anchors with CLI tools
applies-when: Code anchor that ships a CLI
---

# CLI Code Standard

![[xdg-config]]
![[no-heuristics]]
![[error-handling]]
![[naming-conventions]]
```

Activating a group activates all referenced sets recursively.

### Including rule sets in a project

The project's rules file uses Obsidian embed syntax to reference standard rule sets:

```markdown
# DMUX Rules

## Project-Specific Rules

### R01 — Only CommandProcessor mutates SystemState
RULE: ...

| EX | Grade | Location | Description |
|-----|-------|----------|-------------|
| ... |

## Standard Rule Sets

![[xdg-config]]

| EX | Grade | Location | Rule | Description |
|-----|-------|----------|------|-------------|
| EX061 | B | stat.py<br>.load_config() | R-XDG04 | Defaults hardcoded in two places<br>**Purpose:** ... |
```

**Key difference:** Exception tables for referenced rule sets have a **Rule column** that ties each exception to the specific rule it violates. This column is unnecessary for project-specific rules (where the table sits right under the rule) but required for referenced sets (where the rules are defined elsewhere).

### Exception table with Rule column

For referenced rule sets, the exception table adds a Rule column:

| EX | Grade | Location | Rule | Description |
|-----|-------|----------|------|-------------|
| EX061 | B | stat.py<br>.load_config() | R-XDG04 | Defaults hardcoded<br>**Purpose:** ...<br>**Keep:** ...<br>**Alternative:** ...<br>**Gain:** ... **Loss:** ... |

The Rule column contains the set-prefixed rule number (R-XDG04) so the agent knows which rule this exception violates.

## `/rule consider` workflow

1. Read all rule set files from `~/.claude/skills/rule/rulesets/`
2. Read the project's codebase — languages, architecture, patterns
3. Read the project's existing rules file (if any)
4. For each rule set, evaluate:
   - Does the `applies-when` condition match this project?
   - Does the project already have equivalent custom rules?
   - Would these rules catch real issues in this codebase?
5. Generate recommendation table:

```
| Rule Set | Recommendation | Rationale |
|----------|---------------|-----------|
| xdg-config | Apply | Uses ~/.config/skl/ for config storage |
| async-coordination | Apply | Multi-threaded speech engines |
| no-heuristics | Already present | Custom version exists — verify alignment |
| markdown-standards | Skip | Not documentation-heavy |
```

6. User reviews and approves
7. `/rule apply` adds the approved references

## Design Principles

- **Include by reference** — rule sets are not copied into the project. Changes to the standard set propagate automatically.
- **Exceptions are local** — the exception table lives in the project's rules file, not in the standard rule set. Each project has its own exceptions.
- **Rule column for linkage** — exceptions for referenced rule sets include a Rule column tying them to the specific standard rule.
- **DAG grouping** — groups are just rule sets that embed other rule sets. No special machinery.
- **Set-prefixed R-numbers** — R-XDG01, R-AC02, etc. Stable across projects. Never renumbered.
- **Agent-driven consideration** — the agent analyzes the project and recommends, rather than requiring the user to browse a catalog.

## Status

Design in progress. XDG config rule set created as first example. Remaining rule sets TBD.
