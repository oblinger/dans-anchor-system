---
name: rule
description: >
  Project rule management — define semantic rules, check code against them, triage exceptions,
  and drive fixes. Rules are declarative constraints (code patterns, architecture, naming,
  documentation standards) that the agent validates. Exceptions are numbered (EX001, EX002, ...)
  with grades and For/Against justification.
  Use when the user says: "check the rules", "are there any violations", "retriage",
  "the grades are too generous", "audit the code against rules",
  "add a rule", "grade this exception", "what rules should this project have",
  "design rules for this", "create rules", "sync the rules",
  "fix the rules", "make beneficial rule fixes".
  Subcommands: /rule create, /rule check, /rule triage, /rule fix, /rule sync.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Rule — Project Rule Management

Define semantic rules, validate code against them, manage exceptions, and drive fixes.

## Actions

| Action | Runner | Description |
|--------|--------|-------------|
| [[rule-create\|/rule create]] | Pilot + User | Design rules for a project — discuss architecture, propose categories, draft RULE: declarations |
| [[rule-check\|/rule check]] | Project agent | Find and grade violations — scan, analyze, add to rules file, post to Now (`--all` for full audit) |
| [[rule-triage\|/rule triage]] | Pilot | Adversarial re-evaluation — challenge grades, find missed violations, demand better alternatives |
| [[rule-fix\|/rule fix]] | Project agent | Execute a fix spec via `/code bugfix` |
| [[rule-sync\|/rule sync]] | Either | Reconcile the rules file with code after changes land — add, remove, or regrade exceptions |
| [[rule-consider\|/rule consider]] | Pilot + User | Recommend standard rule sets for a project, then apply approved ones |

## Concepts

**Rules file** — A project document (found via `cab-config get rules`) containing H2 category sections, H3 rules with `RULE:` declarations, and exception tables. See [[DMUX Rules]] for the reference example.

**Rule numbering** — Every rule gets an R-prefixed number: R01, R02, etc. Format: `### R07 — Sensors and Effectors Must Be Logic-Free`. Numbers are flat, global, never renumbered, never reused.

**RULE: declaration** — Every rule heading is followed by a line beginning `RULE:` that states the constraint declaratively. This is what the agent checks against.

**Exception (EX)** — A numbered, documented violation of a rule. Each has:
- **EX number** — Global flat sequence (EX001, EX002, ...) with a corresponding `// EX0xx` comment in source code
- **Grade** — Letter grade with optional +/- (A, B+, B, B-, C+, C, C-, D+, D, D-, F). A = necessary/keep, B = reasonable, C = tolerable, D = weak/needs redesign, F = remove
- **Location** — `Module<br>.method()` identifying where in the code
- **Description** — Five parts: summary, **Purpose:** (what it accomplishes), **Keep:** (why leave it), **Alternative:** (concrete spec for what you'd do instead, or "None"), **Gain/Loss** or **Loss/Gain** (what you get and what you pay by switching — order encodes net assessment)

**Untagged exception** — A code pattern that looks like a rule violation but has no `// EX` comment. This is the primary thing `/rule check` looks for.

## Rules File Format

The rules file structure is:

```
## Category Name                        ← H2 grouping (no number)

### R01 — Rule Name                     ← H3 rule with R-number
RULE: Declarative constraint statement.
Explanatory text about why this rule exists.

| EX | Grade | Location | Description |  ← exception table (no heading above it)
|-----|-------|----------|-------------|
| ... | ...   | ...      | ...         |
```

**Critical formatting rules:**
- Exception tables go directly in the rule section — **no H4 heading** above them (no `#### Exceptions`)
- Blank line before and after each table
- Fixed exception tables also go directly in the section — **no H4 heading** (no `#### Fixed`)
- The table is simply part of the rule's content, not a separate subsection

## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file and execute its workflow
4. If no argument, show the Actions table above
