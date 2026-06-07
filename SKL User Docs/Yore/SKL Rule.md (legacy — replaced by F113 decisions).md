---
description: How to manage project rules — creating rules, checking violations, grading exceptions, driving fixes
---

# SKL Rule Guide (Skill: [[rule/SKILL]])

The Rule skill manages declarative constraints for a project — code patterns, architecture decisions, naming conventions, documentation standards. Rules are defined in a project's rules file, and the agent validates code against them, finding violations and tracking exceptions.

The core loop is: create rules that express your project's standards, run check to find violations, triage exceptions to grade their severity, and fix the ones worth fixing. Each exception gets an EX number, a letter grade (A through F), and a For/Against justification explaining why it exists and what the alternative would be.

Rules are not aspirational — they describe how the code should work right now. Exceptions are not failures — they are documented, graded deviations. An A-grade exception is something you intentionally keep. An F-grade exception should be removed.

## Commands

| Command | Description |
|---------|-------------|
| `/rule create` | Design rules for a project — discuss architecture, propose categories, draft declarations |
| `/rule check` | Find violations — scan code, analyze, add to rules file. Use `--all` for full audit |
| `/rule triage` | Adversarial re-evaluation — challenge grades, find missed violations |
| `/rule fix` | Execute a fix spec via `/code bugfix` |
| `/rule sync` | Reconcile rules file with code after changes land |
| `/rule consider` | Recommend standard rule sets for a project, then apply approved ones |

## Key Concepts

- **Rule numbering** — Every rule gets an R-prefixed number (R01, R02, ...). Numbers are flat, global, never renumbered, never reused
- **RULE: declaration** — Each rule heading is followed by a `RULE:` line stating the constraint declaratively. This is what the agent checks against
- **Exception (EX)** — A numbered violation (EX001, EX002, ...) with a `// EX0xx` comment in source code
- **Grades** — A (necessary, keep), B (reasonable), C (tolerable), D (weak, needs redesign), F (remove). Optional +/- modifiers
- **For/Against** — Each exception documents Purpose, Keep rationale, Alternative (concrete spec), and Gain/Loss assessment
- **Rules file** — Located via `cab-config get rules`. Contains H2 category sections, H3 rules with RULE: declarations, and exception tables
- **Standard rule sets** — `/rule consider` recommends pre-built rule categories appropriate for your project type
- **Triage is adversarial** — `/rule triage` deliberately challenges existing grades, looking for exceptions that are graded too generously
