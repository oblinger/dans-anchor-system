---
description: "the `{{PLACEHOLDER}}` system shared by file and folder templates"
---
# FCT Template Variables
The `{{PLACEHOLDER}}` system shared by file and folder templates — how each variable is defined, what to do when there is no data, and the structural-vs-cumulative distinction.

| -[[FCT Template Variables]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template Variables](hook://p/FCT%20Template%20Variables)<br>: the `{{PLACEHOLDER}}` system shared by file and folder templates |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Files]],  [[FCT Template Folders]] |
| Examples | [[_Computer Template\|file]],  [[_Disk Template\|folder]] (both show Variables sections) |

## What a variable is

A **variable** is a bare `{{UPPER_SNAKE_CASE}}` token in the exemplar where live data goes. It is **bare** — no code fence, no backticks around it in the exemplar — so the exemplar stays copyable and the placeholder is a literal find-and-replace target. The set of `{{…}}` tokens in the exemplar is the contract; every one must be accounted for in the `## Variables` section.

## The Variables section — definition + no-data handling

Below the `---` divider, a `## Variables` section carries **one bullet per distinct placeholder**, and each bullet states two things:

1. **What to put** — the meaning of the field.
2. **What to do when there is no data** — fill it, **delete the line**, or **delete the whole section**.

The second half is the load-bearing one. It is what lets an instantiator (LLM or human) finish with **zero leftover `{{}}`**: instead of leaving an empty placeholder or inventing fake content, they follow the stated empty-case behavior. A leftover `{{}}` in an instance is therefore a *tooling failure*, not an unavoidable artifact (R-template-02).

A variable that is **always present** (a key — `{{HOSTNAME}}`, `{{DISK_LABEL}}`, often also the filename) is marked so; it has no delete case.

## Structural placeholder vs cumulative section

Two kinds of content need opposite treatment — the most common template mistake is conflating them:

| Kind | The form has this content… | Treatment |
|---|---|---|
| **Structural placeholder** | …**at creation** (the instantiator HAS the data — a computer's CPU, a disk's capacity) | keep as `{{VARIABLE}}`; define it in Variables with its no-data behavior. |
| **Cumulative section** | …**only after creation** (it accrues over time — a `# LOG`, a change history) | **header only** — no placeholder entry underneath. |

Shipping a fake `### {{YYYY-MM-DD}}  {{TOPIC}}` under a `# LOG` invites the instantiator to either leave it (polluting the new record) or invent a fake event (also polluting). The empty `# LOG` header invites *real* entries when real events occur (R-template-03). In the worked examples, `# LOG` is header-only and `## Notes` is an empty structural section with no placeholder.

## Why this lives across both kinds

Variables work identically in a [[FCT Template Files|file template]] and in the marker of a [[FCT Template Folders|folder template]] — the exemplar/Variables contract is the same artifact-shape in both. Factoring it here keeps one definition; Files and Folders pages cite it rather than restating it.

# BRIEF

- **This page is the variables part of the [[FCT Template]] facet** — the `{{PLACEHOLDER}}` + `## Variables` system shared by [[FCT Template Files]] and [[FCT Template Folders]].
- **The two load-bearing rules:** every placeholder is defined **with explicit no-data handling** (R-template-02 — this is what kills leftover `{{}}`), and **cumulative sections are header-only** (R-template-03 — structural vs cumulative is the classic mistake). Keep both sharp.
- **Bare placeholders, no fences** — `{{UPPER_SNAKE}}` tokens sit in the live exemplar bare (no backticks, no fence); they are find-and-replace targets, so never fence the exemplar (R-template-01).
- **Rules live on the umbrella's `R-template`** — this page is the readable spec for the variable mechanics R-template-02/-03 enforce; cite, don't duplicate the ruleset.
