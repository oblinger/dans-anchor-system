---
description: "system-architecture story — modules, data flow"
---

# Audit Architecture

The audit system is two things: the **rule sets** it runs over, and the **components** — skills and scripts — that run over them. This page is the structural overview; the detailed per-audit pipeline is a subdocument.

![[Audit Architecture.svg|2400]]

## Rule sets — the base

Everything audit does is defined by rule sets, so the organization of the rules *is* the architecture. A rule set is a `# RULESET R-<name>` block whose rules each carry `check::` (detect), optional `fix::` (repair), `where::` (which targets it applies to), and a tier (`checked` / `sampled` / `stated` / `tracked`). See [[FCT Ruleset]]. Rules live with the specs that own them, in three families:

- **Facets** — one structural spec per artifact kind (anchor page, PRD, architecture, dispatch table, …), each embedding its ruleset (`R-anchor-page`, `R-prd`, …). This is the bulk of the corpus.
- **Disciplines** — vault-wide text practices that cut across artifact kinds (`R-markdown`, `R-dated-entry-stream`, `R-file-association`).
- **Skills** — the skill-anchor specs (`skill-spec`, `skill-doc`, `skill-script`, `skill-config`).

Rule sets **contain** other rule sets via `include::` (an umbrella like `R-doc` or `R-anchor` pulls in the per-facet sets), and each rule **binds** to its targets via `where::`. Resolving a target to its applicable rules is just walking these two relations.

## Components

The skills and scripts of the system — boxes, not a flow:

| Component | What it is |
|---|---|
| **Audit skills** | The `/audit` orchestrator + its actions (`structure · doc · q · architecture · markdown · dispatch · …`). The user-facing surface and the per-surface runbooks. |
| **Rule-set scripts** | `audit-plan.py` — resolves rule sets, walks `include::` containment, runs mechanical checks, judges, and fixes. Plus the per-surface checkers (`audit-q.py`, `audit-architecture.py`, `audit-markdown.py`). |
| **Distillation → hook** | `/distill` merges the applicable rule bodies into one fast module; the **on-write hook code** (`~/.config/ob-skills/hooks/`) runs that module on every write. |
| **Safety guard** | `aow-safety.py` gates every fix — a repair that would drop a letter or digit is reverted to a flag (the mechanical floor under the never-delete invariant, [[F005 — Doc audit-on-write — vault-wide rollout + safety guard\|F005]]). |

## Two consumers, one corpus

The components run over the **same rule sets** through two triggers: the on-demand `/audit` pass (thorough backstop) and the distilled on-write hook (always-on guardrail). They share one `where::` selector vocabulary; they differ only in trigger and automation level ([[Audit PRD]] § Automation scale).

## The per-audit pipeline (subdocument)

How a *single* audit executes — **resolve → run → judge → fix**, with the four automation levels as a parameter on the fix stage — is the detailed flow, not the system structure. It lives in [[Audit System Design]]. In one line: resolve the target's rules, run the mechanical ones by script (verdict-cached), judge the rest by agent, apply the level-appropriate fixers, re-run to convergence.
