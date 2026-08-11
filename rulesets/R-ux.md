# RULESET R-ux
include::
description:: facet spec for the human user-facing surface doc

Embedded ruleset for the UX Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. **Not armed.** [[R-facet]] names it, and that umbrella is outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so no rule in this set has ever entered a plan (measured 2026-08-11, [[TINK Backlog#^T208|T208]]). Arming it means naming it in [[R-doc]] or [[R-anchor]] — and measuring the blast radius before doing so, per [[R-doc]]'s own record of what activating a dormant set costs.

### RULE R-ux-01 — Preface zone carries TLDR + figure (checked)

The doc opens with a dispatch table, then a TLDR (3–8 single-line bullets), then a representative figure (annotated session transcript, screen mockup, or interaction snippet) — in that order — before the first body H2.

**Check pattern:** read the doc; assert dispatch table → TLDR → figure precede the first non-preface H2.

**Why:** the human reading a UX spec needs an at-a-glance pitch (TLDR) and a concrete instance (figure) before paragraphs. Abstract description alone is the failure mode.

### RULE R-ux-02 — Audience declared explicitly (stated)

The first body H2 is `## Audience` and names who the human consumer is, the context they're in, and what they're trying to do. One paragraph, not a list of personas.

**Check pattern:** assert `## Audience` exists as the first body H2; body is prose (not just a bulleted persona list); body names context (terminal / GUI / Obsidian / web) + intent.

**Why:** every downstream decision (output shape, error voice, naming) depends on the audience. Leaving it implicit forces the reader to reverse-engineer it.

### RULE R-ux-03 — Entry-points table is the spine (checked)

A `## Entry-points` H2 carries a single canonical table listing every human-invocable surface entry-point: name, one-line purpose, source story (`US-<slug>-<N>`) or link to its feature doc. No entry-point lives only in prose; every one is in the table.

**Check pattern:** parse the doc; gather all command-like or screen-like identifiers from H3s + prose; assert each appears in the spine table.

**Why:** the spine table is the contract surface — what the user can do. Prose-only entries are invisible to grep, to dispatch generation, and to audits.

### RULE R-ux-04 — Output shapes named both human + structured (stated)

The `## Output shapes` H2 names both forms with a realistic example for each: (a) human-readable default (what the user sees with their eyes), (b) structured / machine-readable opt-in (`--json`, `--csv`, exportable payload). Even a single-shape surface declares the absence of the other explicitly.

**Check pattern:** assert `## Output shapes` exists; assert two named sub-shapes (default + structured) OR an explicit statement "no structured output — human only" with rationale.

**Why:** scriptability and pipe-ability are first-class affordances of a CLI; assuming the human-readable form is "the output" silently breaks every downstream `jq` / `grep` consumer. Naming the structured opt-in upfront forces the decision.

### RULE R-ux-05 — Error voice declared once at top (sampled)

The `## Error voice` H2 opens with a one-line declaration of tone (terse / friendly / instructive) + the standard error envelope (prefix, exit code or alert pattern), then enumerates the named error situations with their messages.

**Check pattern:** assert `## Error voice` exists; first paragraph names tone + envelope; subsequent rows enumerate named failures.

**Why:** consistency in error voice IS the UX — switching between terse and verbose, between "error:" and "ERROR:", between exit 1 and exit 2 fragments the user's mental model.

### RULE R-ux-06 — Discovery mechanism named (stated)

A `## Discovery` H2 (or equivalent) names how the human finds the entry-points on first encounter — `--help` text, dispatch table in `{slug}.md`, hotkey, banner copy, web nav. Don't assume discovery is obvious.

**Check pattern:** assert `## Discovery` exists OR an inline `discovery::` line in the spine table; body names the surfacing channel.

**Why:** a surface without discovery is invisible; UX Design is incomplete without naming how the user finds the surface in the first place.

### RULE R-ux-07 — Design decisions captured as `D-UX<n>` rows (sampled)

Load-bearing UX choices (a chosen affordance over an obvious alternative, a chosen output shape over a sibling, a chosen naming convention) appear as `D-UX<n>` rows under `## Design decisions` with: choice, alternatives considered, rationale (one or two sentences).

**Check pattern:** sample design decisions in CAE UX Design and SKL UX Design; assert each row has Choice + Alternatives + Rationale columns.

**Why:** UX choices look obvious after the fact but were contingent at the time. Capturing them as auditable rows lets the next reviewer reverse-engineer intent without re-litigating the decision.

### RULE R-ux-08 — Distinct from API Design, CLI doc, Architecture (stated)

UX Design owns the *intent* of the human-facing surface. It is NOT:

- The programmatic surface — that's [[DAS API Design]].
- The exhaustive flag/option reference — that's [[DAS CLI]] (for CLI anchors).
- The internal organization — that's [[DAS Architecture]].

When UX Design starts listing every flag, or describing function signatures, or explaining module structure, it is leaking the wrong content. Migrate the leak to the sibling facet.

**Check pattern:** sample UX Design docs; assert no flag-by-flag reference tables (CLI scope), no function signatures (API scope), no module dependency narrative (Architecture scope).

**Why:** facet leakage erodes the cut. The reader who wants the programmatic surface goes to API Design; if it lives in UX, they don't find it where they look.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). Paired peer to [[R-api]] — both fire when the anchor has a public user surface; the cut is human vs programmatic consumer.

## Adoption

**Not armed.** [[R-facet]] names it, and that umbrella is outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so no rule in this set has ever entered a plan (measured 2026-08-11, [[TINK Backlog#^T208|T208]]). Arming it means naming it in [[R-doc]] or [[R-anchor]] — and measuring the blast radius before doing so, per [[R-doc]]'s own record of what activating a dormant set costs.

## See also

- [[DAS UX Design]] — facet spec this ruleset enforces.
- [[R-api]] — paired peer ruleset for programmatic surface.
- [[R-facet]] — umbrella catalog.
- [[HBR UX Design]] — worked example.
- [[DAS Rulesets]] — top-level catalog.
