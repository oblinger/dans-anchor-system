---
description: "*Language* — the grammar: three constructs, four defaults"
---

| -[[STEN Language]]- | : the Stencil language — three constructs and four defaults<br>→ [[DAS]] → [[STEN]] → [STEN Language](hook://p/STEN%20Language)  |
| --- | --- |
| [[Template Examples]]  | *Corpus* — the seven cases every construct is derived from |
| [[Tink303 - Template DSL - one pattern language for facets, templates, and sections\|F303]]  | *Spec* — the commissioning feature |
| [[STEN Language Discussions\|Discussions]]  | *Discussion* — dated trade-off threads behind the grammar |
| ... | [[STEN Restated Corpus\|Restated Corpus]],  [[STEN Track\|Track]],   |

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


## Overview

A **stencil** states the shape of a document once, and that single statement runs in both directions: **generate** a conforming document from it, and **match** an existing document against it to test whether it fits. The bidirectionality is the whole point — today the same shape is stated twice, once as a template that scaffolds and once as a ruleset that checks, and the two drift.

The language is deliberately tiny, and its smallness is not an aesthetic preference — it is a measured result. Seven cases were worked through in [[Template Examples]] and **the language did not grow under any of them**. The two constructs that were expected to be forced — a partial-match notion and a nested-stencil reference — were each refused by the very case that was supposed to demand it.

## Why the tables are this short — the defaults are doing the work

Every default replaced a construct that an early case proposed and that was then cut. Reading them as *absences* misses the point: each one is a decision about what the common case is, paid for by making the uncommon case unsayable.

- **Open world** — a stencil is a statement about what a document *has*, never about what it lacks. This is the largest of the four, and it is what removes the need for a trailing "and anything else" marker: silence already means it. Its consequence is that a stencil alone can never reject a document for containing something extra; if that is wanted, it is a rule, not a shape.
- **Exactly one** — an unmarked member appears once. Cardinality markers exist in every template language that has them because they were added before anyone measured how rarely the non-default is needed.
- **Many-by-variable** — a pattern holding a **free** variable matches once per binding. This is the sharp one: multiplicity is a *consequence* of whether a variable is bound, not a property declared alongside it. `## {{YYYY-MM-DD}} {{DAY}}` matches every dated entry under its anchor because the dates are free, and nothing had to say so. **Read as `[0+]` it is too strong, and M3 measured by how much:** if a free-variable pattern may match *zero* times, it can never fail, and **six of the fifteen pairs the corpus says must not match become matches** — including `T4.A × T4.c`, the pair T4's whole verdict rests on. So the count is *one or more* for an item inside a document, and genuinely *zero or more* only for a folder member, where the filesystem supplies the boundary. The distinction was invisible until something tried to run it.
- **Whole document** — a stencil with no anchor marker governs the whole file. A file-scope template needs no declaration that it is one.

## The two anchor forms, and why both are needed

An anchor binds a stencil to a position in a document rather than to the document's start. `...` matches **this depth or deeper**; `==` matches **exactly this depth**.

Both are needed because the same named section genuinely sits at different depths in different files, and those files must not be rewritten to suit a matcher. `# LOG` appears at H1 in two different person-pages while its entries are H2 in one and H3 in the other — so a stencil written as "one deeper than LOG" is right for one file and wrong for the other. `==` exists for the opposite need: a shape that must *not* drift, where matching a deeper heading would be a false positive.

**One sentence of the argument above does not survive M3, and it is worth correcting rather than quietly dropping.** The floating form was said to be *right for both* files. Run against them, it is not: the second page's entries read `### 2022-12-19  Summary of email for Nick.` — no direction, no kind, no em-dash — so the entry pattern fails on **text**, not only on depth, and re-anchoring it changes nothing. Depth was never the only difference between those two files; it was only the difference anyone had looked at. The two anchor forms are still both needed, on the depth argument alone. What M3 removes is the belief that anchoring the entry heading reconciles those two pages, and what it leaves in its place is a genuine second spelling that no single stencil covers.

## Variable extent — settled by the matcher, 2026-08-08

How far a variable reaches was the one grammar question the corpus left open, and M3 was commissioned to settle it: a matcher either needs the distinction or it does not. **It needs it**, and the recommendation as written does not supply it.

**The rule: a variable reaches until the next literal the stencil names, and the end of a line that carries any literal text is one of those literals.** Equivalently, and this is the form to implement: a stencil line holding any literal text is matched line-wise, with its variables bounded within that line; a line that is *nothing but* a variable is a multi-line hole, running until whatever follows it matches.

The second clause is not a refinement, it is load-bearing. Read without it — a variable reaching until the next literal *anywhere later in the stencil* — a trailing variable swallows the lines beneath it, and **six of the thirty stencil-versus-document pairs in the corpus flip from match to no-match**: `T3.A × T3.a`, `T3.B × T3.a`, `T4.A × T3.a`, `T7.A × T7.b`, and both pairs against the live correspondence log the corpus cites. Three specimens force it individually — `# DAS {{FACET_NAME}}` in T7.A, `Subject: {{SUBJECT}}` in T4.A, and `{{KIND}}` closing T3.A's entry heading — each a variable at the end of a line whose value is manifestly that line and no more. The measurement is in `Stencil/engine/test_sten_match.py`, experiment 1.

So the two options the corpus posed were not equivalent after all. Option (B) — *alone on a line ⇒ multi-line* — turns out to be right about **what** the answer is; option (A) is right about **why**, and remains the better statement because it derives the rule from surrounding literals rather than declaring a property. Extent stays a consequence, exactly as multiplicity is; the correction is only that a line ending is a literal too.

The cost is unchanged and worth restating: this cannot **require** one-line-ness. A stencil that must insist a value is exactly one line is expressing a constraint on a bound variable, and that belongs in the rules layer rather than in the grammar.

**One shape is ambiguous under any reading** — two unbounded variables adjacent with no literal between them. The earlier draft of this section said no case in the corpus does this; **that is wrong, and the counterexample is quoted in the corpus itself.** T5.a, `SYS/SYS Catalog/Computer/_Computer {{NICKNAME}} Template.md`, carries the line `- **My nickname / short reference:** {{NICKNAME}}{{, phonetic hint if non-obvious — delete otherwise}}` — two variables, no literal between them. The verdict the section reached still stands: *that stencil is malformed*, a checkable defect rather than a new construct. What changes is that it is a live defect in a shipped template rather than a hypothetical, so the matcher reports it as a parse note instead of waiting for a first instance.

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

## The matcher

The match direction is implemented at `Stencil/engine/sten_match.py`, with its suite beside it at `Stencil/engine/test_sten_match.py`. It runs standalone — `python3 test_sten_match.py` — and takes no dependencies. Nothing in it generates; generate is M4.

**Its verification standard is the corpus, not fixtures.** Every stencil and every specimen it is tested against is lifted verbatim out of `design/Template Examples.md` by `sten_corpus.py`, or read from the real vault file that case cites; each of the 33 scored pairs carries the verdict a human reading it would give and the sentence in the corpus that supplies it. As of 2026-08-08 the matrix is **17 true matches, 16 true refusals, no false positives, no false negatives**, with one pair unscored because its verdict turns on section ordering, which T1 already flagged as unstated. Nine further probes mutate real corpus bytes by one character class each — an em-dash to a hyphen, a double space to a single, a row's second space removed — and every one flips the verdict, so the clean matrix is not the result of a matcher that says yes to everything.

Three implementation properties are worth naming because they are not grammar and the grammar should not grow them:

- **Whitespace is normalized before literals are compared** — NFC, every Unicode space to U+0020, trailing whitespace stripped, internal runs preserved. T4 found that the two live LOG spellings differ by a U+00A0 pasted out of Apple Mail and a trailing space; a matcher comparing what they look like on screen matches neither. Runs must survive because T3.A's entry heading separates fields by a *double* space.
- **Open world permits skipping before the first item, not only between items** — every real target has a preamble the stencil does not name (YAML frontmatter, a LinkedIn URL, a `#pp` tag line). Without it, no whole-document stencil matches anything in the vault.
- **A match reports bindings, not a boolean.** This is what T4 said reconciliation needs, and it is what makes `T4.A × T4.c` useful rather than merely negative: the match fails, `SUBJECT` binds, `TO` does not, and *that* is the reconciliation answer.

## Status

Authored 2026-08-07 as [[Tink303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M2, from the M1 corpus. **M3 landed 2026-08-08** and closed the one thing this document left open: variable extent is settled above, on measurement rather than preference, and the matcher's two other grammar findings — that `[0+]` is the wrong reading of many-by-variable inside a document, and that the corpus does contain the adjacent-variable shape — are folded into the sections that made the claims. Remaining F303 milestones — the generator (M4), restating the corpus (M5), and how a Stencil-bearing file declares itself to Warden (M6) — are tracked on F303 and [[STEN Backlog]].
