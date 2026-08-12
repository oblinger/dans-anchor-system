# RULESET R-api
include::
where:: `file:{anchor}/**/* API Design.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — the same exclusion [[R-prd]] carries, and load-bearing here because `DAS API Design.md` is itself a `* API Design.md` filename.
description:: facet spec this doc follows

> **Selector added 2026-08-11 ([[TINK Backlog#^T212|T212]]).** This set declared no `where::`, so it inherited `always` — every file in every anchor — while its rules describe one document kind. [[DAS API Design]] names that document unambiguously: `{slug} Design/{slug} API Design.md`, single-file, with an anchor-folder upgrade form. The selector globs the basename so both forms match, and carries [[R-prd]]'s `!**/DAS *.md` exclusion because `DAS API Design.md` would otherwise select itself as an instance of the facet it specifies. Measured before writing: **2 instance(s)** — the two live instances are both in this repo's own `examples/` gallery ([[FEX API Design]], `HBR API Design.md`) — the facet has no vault instance outside the gallery yet, which is worth knowing before anyone reads a clean sweep as coverage. Selector, not arming: [[R-facet]] is still inert ([[TINK Backlog#^T208|T208]]).

Embedded ruleset for the API Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. **Not armed.** [[R-facet]] names it, and that umbrella is outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so no rule in this set has ever entered a plan (measured 2026-08-11, [[TINK Backlog#^T208|T208]]). Arming it means naming it in [[R-doc]] or [[R-anchor]] — and measuring the blast radius before doing so, per [[R-doc]]'s own record of what activating a dormant set costs.

### RULE R-api-01 — Preface zone carries TLDR (figure recommended) (checked)

The doc opens with a dispatch table, then a TLDR (3–8 single-line bullets), then optionally a figure (schema diagram, sequence diagram, or a canonical code snippet) — before the first body H2.

**Check pattern:** read the doc; assert dispatch table + TLDR precede the first non-preface H2; figure presence is sampled but not enforced.

**Why:** programmatic consumers skim contracts for the shape they're going to integrate against; TLDR gives the integrator the at-a-glance pitch, figure (when present) gives the one example that beats prose.

### RULE R-api-02 — Consumer declared explicitly (stated)

The first body H2 is `## Consumer` and names who calls programmatically, in what language/runtime/transport, with what integration shape. One paragraph, not a vague "this exposes an API."

**Check pattern:** assert `## Consumer` exists as the first body H2; body names language (Rust crate / TS package / HTTP service / sub-skill called by another skill) + integration shape (sync call / event stream / batch).

**Why:** every contract decision (error envelope, async-ness, schema serialization) depends on the consumer. Leaving it implicit forces the integrator to reverse-engineer from signatures.

### RULE R-api-03 — Surface table is the spine (checked)

A `## Surface` H2 carries a canonical table listing every public callable / endpoint / sub-skill entry once: name, signature or schema sketch, one-line purpose, source story (`US-<slug>-<N>`) or feature doc link. No entry lives only in prose; every one is in the table.

**Check pattern:** parse the doc; gather all callable-like identifiers from H3s + prose; assert each appears in the spine table.

**Why:** the spine table IS the public surface contract. Prose-only entries silently leak from the spec into folklore.

### RULE R-api-04 — Contract semantics named per entry (stated)

A `## Contract semantics` H2 (or per-entry rows in the spine) names: idempotency, side-effects, ordering / concurrency guarantees, transactional posture, async-ness, deadlines / timeouts, retry behavior — the behavioral contract beyond the type signature.

**Check pattern:** for each entry in the spine table, assert at least one of (idempotency / side-effect / concurrency / deadline) is declared — either inline in the table or in a dedicated `## Contract semantics` section.

**Why:** type signatures lie about behavior — `fn submit(t: Task) -> Result<TaskId, _>` doesn't tell the caller whether two `submit` calls with the same Task are idempotent, whether the call blocks, whether failure is retryable. Behavioral contract is part of the API.

### RULE R-api-05 — Error model standardized to ONE form per anchor (checked)

The `## Error model` H2 declares a single error-envelope form for the whole surface: typed enum / discriminated union / exception class hierarchy / HTTP status taxonomy / error-code namespace. Mixing envelope forms within the same anchor's API is forbidden.

**Check pattern:** for each entry in the spine table, assert the return / failure type uses the declared envelope form. Mixed forms (some entries return `Result<T, MyError>`, others `Result<T, String>`) fail.

**Why:** consumers integrate against one mental model. Mixed envelopes force them to write per-call adapters and erode trust in the surface.

### RULE R-api-06 — Stability posture + version commitment declared (stated)

The `## Stability + compatibility` H2 declares: stability posture (stable / evolving / experimental / private), versioning scheme (semver / `0.x` rules / hand-rolled), and deprecation policy (how long deprecated surface is honored before removal).

**Check pattern:** assert `## Stability + compatibility` exists; body names posture + version scheme + deprecation policy in concrete terms (not "we will be careful with breaking changes").

**Why:** an unstable API used as if it were stable creates support burden + caller churn. Naming the posture upfront sets correct expectations.

### RULE R-api-07 — Compatibility commitments are concrete (stated)

Deprecation policy is concrete: "deprecated entries are removed no sooner than the next minor release after deprecation notice" or "deprecated entries live for 90 days minimum" — NOT "we'll try to be backward compatible." Stated commitments callers can verify.

**Check pattern:** for each deprecation-policy statement, assert it names a measurable horizon (release cadence, calendar duration, or version-step rule).

**Why:** vague commitments are unilaterally adjustable; callers can't plan against them. Concrete horizons are commitments.

### RULE R-api-08 — Design decisions captured as `D-API<n>` rows (sampled)

Load-bearing API choices (a chosen error envelope over an obvious alternative, a chosen async-ness model, a chosen schema-serialization format) appear as `D-API<n>` rows under `## Design decisions` with: choice, alternatives considered, rationale.

**Check pattern:** sample design decisions; assert each row has Choice + Alternatives + Rationale.

**Why:** API design choices look obvious in retrospect but were contingent — capturing them prevents the next consumer from re-litigating settled questions.

### RULE R-api-09 — Distinct from Module Doc, Architecture, UX Design (stated)

API Design owns the *intent* of the programmatic surface. It is NOT:

- The per-module reference of *what exists* — that's [[DAS Module Doc]].
- The internal organization of the system — that's [[DAS Architecture]].
- The human-facing surface — that's [[DAS UX Design]].

When API Design starts enumerating every function in every module, or narrating the dependency graph, or describing what the human sees on the screen, it is leaking the wrong content. Migrate the leak to the sibling facet.

**Check pattern:** sample API Design docs; assert no per-module function inventories (Module Doc scope), no internal dependency narratives (Architecture scope), no human screen / command lists (UX Design scope).

**Why:** facet leakage erodes the cut. The consumer who wants reference goes to Module Doc; if it lives in API Design, they don't find it where they look.

## Position in the catalog

Sits under [[R-facet]] (per-facet umbrella). Paired peer to [[R-ux]] — both fire when the anchor has a public user surface; the cut is programmatic vs human consumer. Distinct from R-module-doc (per-module reference rules; pending).

## Adoption

**Not armed.** [[R-facet]] names it, and that umbrella is outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so no rule in this set has ever entered a plan (measured 2026-08-11, [[TINK Backlog#^T208|T208]]). Arming it means naming it in [[R-doc]] or [[R-anchor]] — and measuring the blast radius before doing so, per [[R-doc]]'s own record of what activating a dormant set costs.

## See also

- [[DAS API Design]] — facet spec this ruleset enforces.
- [[R-ux]] — paired peer ruleset for human surface.
- [[R-facet]] — umbrella catalog.
- [[FEX API Design]] — worked example.
- [[DAS Module Doc]] — distinct facet covering per-module reference documentation (different altitude — intent vs reference).
- [[DAS Rulesets]] — top-level catalog.
