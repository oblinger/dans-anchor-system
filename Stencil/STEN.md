---
description: Stencil — the pattern language the anchor system is written in
---
# Stencil
The pattern language the anchor system is written in — one notation that both generates a document and tests whether a document fits.

| -[[STEN]]- | : Stencil — the pattern language the anchor system is written in — one notation that both generates a document and tests whether a document fits<br>→ [[DAS]] → [STEN](hook://p/STEN)  |
| --- | --- |
| [[STEN Track\|Track]]  | [[STEN Backlog\|Backlog]],   |
| Language | [[STEN Language\|Language]] — the grammar: three constructs, four defaults |
| Spec | [[TINK303 - Template DSL - one pattern language for facets, templates, and sections\|F303]] — the commissioning feature; the corpus is [[Template Examples]]  |
| ... | [[STEN Restated Corpus\|Restated Corpus]],   |

## Overview

**Stencil** is the pattern language that facets, templates, and sections are all written in. A stencil states the shape of a document once, and that single statement runs in both directions: **generate** a conforming document from it, and **match** an existing document against it to test whether it fits. The bidirectionality is the point — today the same shape is stated twice, once as a template that scaffolds and once as a ruleset that checks, and the two drift.

The language is Stencil; the artifacts written in it are **anchor templates** ([[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] Q2, 2026-08-04).

## Where it lives, and why here

Stencil is a **child anchor of [[DAS]]**, on the [[Warden]] precedent — it ships inside `dans-anchor-system` because the repository depends on it, and it may be spun out later once it stands on its own.

The notation belongs to the standard rather than to any engine. A stencil is authored in the corpus as markdown, exactly as a ruleset is, and an agent with no engine present can read one and act on it — that path is the **baseline**, not a degraded mode. [[Warden]] is a *consumer*: it gains a matcher and an instantiate action, the same relationship it already has to rulesets, which are authored in DAS and merely compiled by Warden.

## Status

Created 2026-08-07. The corpus (M1) is complete and the grammar did not grow under it; **M2 landed the same day** as [[STEN Language]] — three constructs, four defaults, one nesting rule, with variable extent recommended but not ratified. Work is tracked in [[STEN Backlog]]; the design record remains on [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] until it earns its own design folder.
