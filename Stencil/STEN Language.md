---
description: "the Stencil language — three constructs and four defaults"
---

# Stencil Language
The whole language: three constructs, four defaults, and one nesting rule.

| construct | reads as |
| --- | --- |
| `{{NAME}}` | a **variable** — binds when matching, is filled when generating |
| `# ... LOG` | an **anchor** — a heading matching `LOG` at **this depth or deeper** |
| `# == LOG` | an **anchor** — a heading matching `LOG` at **exactly this depth** |

| default | means | so there is no marker for |
| --- | --- | --- |
| **open world** | a stencil says what is present, never what is absent | "and anything else" |
| **exactly one** | an unmarked member appears once | `[1]` |
| **many-by-variable** | a pattern holding a **free** variable matches once per binding | `[0+]` |
| **whole document** | a stencil with no anchor marker governs the whole file | a "this is a file template" marker |

**Anchors nest, and every depth is relative to the nearest enclosing anchor.** An anchor marker may sit on a heading *inside* a stencil, not only on its first line; below it, depth is read against that heading rather than against the file.

| -[[STEN Language]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[STEN]] → [STEN Language](hook://p/STEN%20Language)<br>: the Stencil language — three constructs and four defaults |
| --- | --- |
| Corpus | [[Template Examples]] — the seven cases every construct is derived from |
| Spec | [[TINK303 - Template DSL - one pattern language for facets, templates, and sections\|F303]] — the commissioning feature |
| ... | [[STEN Track]],   |

## Overview

A **stencil** states the shape of a document once, and that single statement runs in both directions: **generate** a conforming document from it, and **match** an existing document against it to test whether it fits. The bidirectionality is the whole point — today the same shape is stated twice, once as a template that scaffolds and once as a ruleset that checks, and the two drift.

The language is deliberately tiny, and its smallness is not an aesthetic preference — it is a measured result. Seven cases were worked through in [[Template Examples]] and **the language did not grow under any of them**. The two constructs that were expected to be forced — a partial-match notion and a nested-stencil reference — were each refused by the very case that was supposed to demand it.

## Why the tables are this short — the defaults are doing the work

Every default replaced a construct that an early case proposed and that was then cut. Reading them as *absences* misses the point: each one is a decision about what the common case is, paid for by making the uncommon case unsayable.

- **Open world** — a stencil is a statement about what a document *has*, never about what it lacks. This is the largest of the four, and it is what removes the need for a trailing "and anything else" marker: silence already means it. Its consequence is that a stencil alone can never reject a document for containing something extra; if that is wanted, it is a rule, not a shape.
- **Exactly one** — an unmarked member appears once. Cardinality markers exist in every template language that has them because they were added before anyone measured how rarely the non-default is needed.
- **Many-by-variable** — a pattern holding a **free** variable matches once per binding. This is the sharp one: multiplicity is a *consequence* of whether a variable is bound, not a property declared alongside it. `## {{YYYY-MM-DD}} {{DAY}}` matches every dated entry under its anchor because the dates are free, and nothing had to say so.
- **Whole document** — a stencil with no anchor marker governs the whole file. A file-scope template needs no declaration that it is one.

## The two anchor forms, and why both are needed

An anchor binds a stencil to a position in a document rather than to the document's start. `...` matches **this depth or deeper**; `==` matches **exactly this depth**.

Both are needed because the same named section genuinely sits at different depths in different files, and those files must not be rewritten to suit a matcher. `# LOG` appears at H1 in two different person-pages while its entries are H2 in one and H3 in the other — so a stencil written as "one deeper than LOG" is right for one file and wrong for the other, while the floating form is right for both. `==` exists for the opposite need: a shape that must *not* drift, where matching a deeper heading would be a false positive.

## Variable extent — recommended, not yet ratified

How far a variable reaches is the one grammar question the corpus left open. The distinction is real — a matcher must know whether `{{one-line description}}` binds part of a line or swallows the next forty — but **position alone does not draw it**: `{{one-line description}}` and `{{dispatch table}}` both sit alone on their lines, and one is a single line while the other is genuinely several.

**Recommended: a variable reaches until the next literal the stencil names.** `# ` and ` Backlog` bound `{{slug}}` to part of a line; a blank line bounds `{{one-line description}}` to what precedes it; a variable with nothing after it reaches to the end of its section. This is the same move that made cardinality a default — extent is a *consequence* of what surrounds the variable, exactly as multiplicity is a consequence of whether it is free.

The cost is honest and worth stating: this cannot **require** one-line-ness. A stencil that must insist a value is exactly one line is expressing a constraint on a bound variable, and that belongs in the rules layer rather than in the grammar.

**One shape is ambiguous under any reading** — two unbounded variables adjacent with no literal between them. No case in the corpus does this. When one appears the answer is most likely *"that stencil is malformed"* — a checkable defect, like two stencils claiming one anchor — rather than a new construct.

## What is deliberately not in the language

- **No closed-world marker.** T7, the reflexive case that was predicted to demand one, passes without it.
- **No partial-match construct.** T4 was built to force one and shrank on contact with its instances: two of its four spellings turned out not to be entry headers at all, but pasted correspondence inside an entry body, which open world already covers.
- **No nested-stencil reference.** `{{dispatch table}}` is not a variable awaiting a value; it is a placeholder for a sub-shape governed by another stencil, and that is a genuinely different construct. T6 was the case for it and is expressible with existing constructs — what distinguishes a curated dispatch row from a machine-owned one is **ownership, not shape**, so the distinction does not belong in a shape language. Named here so it is not silently absorbed into `{{NAME}}`.
- **No cardinality markers, and no "anything else" marker.** Both are covered by the defaults above.

## The cut line is not a Stencil construct

`✂ ──── {label} ──── ✂` marks the point where a file's governed region ends and commentary about it begins — live in 20 `_{{…}} Template.md` files, with `{label}` naming what the file is (`template notes`, `example notes`).

It belongs to files that **carry** stencils, not to the language: a stencil never matches across it, because the region below is not content. It earns its mention here because it is the finer instrument that the alternative — excluding whole specimen-bearing files from whole rules — is too blunt to replace. With a cut line the exclusion reads *"rules do not apply below the cut"* rather than *"rules do not apply to this file"*, so a template's own body stays checkable and only its notes are exempt.

## Evidence discipline

Every construct in this document traces to a real case in [[Template Examples]], and every case there cites a real file. A shape with no vault instance is not admitted, so a hypothetical can never justify a construct. This is the rule that kept the language at three constructs: each time a case was authored to force a fourth, the instances refused it.

## Status

Authored 2026-08-07 as [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M2, from the M1 corpus. The grammar is complete and closed except for **variable extent**, recommended above and not yet ratified. Remaining F303 milestones — how a Stencil-bearing file declares itself to Warden (M6), and the matcher and instantiate actions themselves — are tracked on F303 and [[STEN Backlog]].
