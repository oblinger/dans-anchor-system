---
description: "the `{{PLACEHOLDER}}` system shared by file and folder templates"
---
# FCT Template Variables
The `{{PLACEHOLDER}}` system shared by file and folder templates — how each variable is defined, what to do when there is no data, and the structural-vs-cumulative distinction.

| -[[FCT Template Variables]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [[FCT Primitives]] → [FCT Template Variables](hook://p/FCT%20Template%20Variables)<br>: the `{{PLACEHOLDER}}` system shared by file and folder templates |
| --- | --- |
| Related | [[FCT Template]] (umbrella),  [[FCT Template Files]],  [[FCT Template Folders]] |
| Examples | [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|file]],  [[_{{DISK_LABEL}} Template\|folder]] (both show the two placeholder forms) |

## Two placeholder forms — distinguished by case

Every `{{…}}` is **bare** in the exemplar (no fence, no backticks) so it stays a literal find-and-replace target. Two forms, told apart by **case**:

| Form | Meaning | Defined? |
|---|---|---|
| **`{{UPPER_SNAKE}}`** | a **variable** — reused across sites or structural (filename, key) | **yes** — named once in the definition list above the notes; referenceable |
| **`{{Mixed Case description}}`** | a **one-off** — appears once, self-explanatory | **no** — the placeholder text *is* its description, in place |

The case is the detector (all-caps → variable). The point: a value that repeats or builds the filename earns a named, defined variable; a field that appears once is lighter described in place than mapped to a list (R-template-02).

**Single-line vs multi-line.** An **inline** placeholder holds one line (`{{event title}}`); **braces spanning their own lines** hold a block — `{{` on a line, the content, `}}` on a line (R-template-09).

## Defining a variable — no-data handling

In the definition list (above the notes — below the `template notes` cut-line; see [[FCT Template Files]]), each `{{UPPER_SNAKE}}` variable (and each in-place description) states two things:

1. **What to put** — the meaning of the field.
2. **What to do when there is no data** — fill it, **delete the line**, or **delete the whole section**.

The second half is the load-bearing one. It is what lets an instantiator (LLM or human) finish with **zero leftover `{{}}`**: instead of leaving an empty placeholder or inventing fake content, they follow the stated empty-case behavior. A leftover `{{}}` in an instance is therefore a *tooling failure*, not an unavoidable artifact (R-template-02).

A variable that is **always present** (a key — `{{HOSTNAME}}`, `{{DISK_LABEL}}`, often also the filename) is marked so; it has no delete case.

## Structural placeholder vs repeating section

Two kinds of content need opposite treatment — the most common template mistake is conflating them:

| Kind | The form has this content… | Treatment |
|---|---|---|
| **Structural placeholder** | …**at creation** (the instantiator HAS the data — a computer's CPU, a disk's capacity) | keep as a placeholder with its no-data behavior. |
| **Repeating section** | …**only after creation**, one block per event (a `# LOG`, a change history) | ship **one variableized entry-pattern** + a **`...` repeat-marker at the repeating unit's level** — e.g. `### ...` below a `### {{date}} — …` entry. |

A *filled* fake entry (`### 2026-06-29 — Bought RAM`) invites the instantiator to leave it or invent another (pollution). A *variableized* pattern + a level-marked `### ...` instead shows the **shape** and **what repeats** — the `### ` level says the whole entry recurs, not the detail line — without inviting a fake row (R-template-03). The filename analog: a member file whose name carries an **unbound** variable repeats, one per value (R-template-10).

## Why this lives across both kinds

Variables work identically in a [[FCT Template Files|file template]] and in the marker of a [[FCT Template Folders|folder template]] — the exemplar/Variables contract is the same artifact-shape in both. Factoring it here keeps one definition; Files and Folders pages cite it rather than restating it.

# BRIEF

*(Maintainer note.)* Part-view of the [[FCT Template]] facet — the model and the `R-template` ruleset live on the umbrella, so edit them there, not here. This page is the readable spec for the variable mechanics **R-template-02** (two placeholder forms by case + no-data handling), **R-template-03** (repeating structure = pattern + `### ...`), and **R-template-09** (multi-line = spanning braces) enforce.
