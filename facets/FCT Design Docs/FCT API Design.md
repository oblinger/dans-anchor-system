# FCT API Design

Facet spec defining the shape, required sections, and ruleset for an anchor's `{NAME} API Design.md` — the programmatic (code-to-code or sub-skill) user surface.

description:: facet spec this doc follows

API Design specifies the **programmatic user surface** of the anchor — what shape another piece of code (or another agent invoking this as a sub-skill) sees when integrating. It is sibling to [[FCT UX Design]] (the *human* user surface). The cut between them is **who the consumer is**: API = code calling; UX = human reading or invoking.

> [!info] Scope guard
> "API" here means the *intent* of the programmatic surface — how it's shaped, what it commits to. Distinct from [[FCT Module Doc]] (per-module reference; *what exists* in the source tree, often generated) and from [[FCT Architecture]] (internal organization; *how* the system is built). API Design is the *what* of the public contract.

The API Design doc is the **current spec** — the contract surface today. Rationale lives in [[FCT Decisions]] or in the document's own *D-API<n>* design-decision rows (see [[#RULESET R-api|R-api]]). If the anchor has no programmatic consumer (no library form, no sub-skill invocation surface, no integration story), this facet is N/A; mark it `none` in [[FCT Status]] and omit the file.

## When this facet applies

- The anchor ships a library, crate, package, or module that other code imports.
- The anchor is a skill whose sub-skills are invoked by other skills (e.g. `/design prd` called from `/design`).
- The anchor exposes a service or RPC surface (HTTP / gRPC / pub-sub / queue).
- The anchor's CLI is *also* used programmatically (consumers parsing its `--json` output) — API Design covers the structured-output contract; UX Design covers the human form.

When none of the above hold, omit the facet.

## Location

`{NAME} Docs/{NAME} Design/{NAME} API Design.md` — single-file form. Upgrade to anchor-folder form `{NAME} API Design/` only when distinct sub-surfaces (e.g., library API + service API + sub-skill API in the same anchor) warrant separate files.

Peer of [[FCT Architecture]] and [[FCT UX Design]] under [[FCT Design Dispatch|Design]].

## Preface zone

Per [[DSC progressive-disclosure]]:

- **TLDR** required — 3–8 short bullets: consumer, surface kind (library / sub-skill / service), error model, stability posture, compatibility horizon.
- **Figure** optional but recommended — schema diagram (struct/types relationship), sequence/interaction diagram (call → response shape), or a representative code snippet of one canonical call.

## Required section spine

| H2 | What it carries |
|---|---|
| `## Consumer` | One paragraph: who calls programmatically, what language/runtime/transport, what their integration shape is (synchronous call? streamed events? batch job?). Sets the frame. |
| `## Surface` | The spine table. Every public callable / endpoint / sub-skill entry listed once with: name, signature (or schema sketch), one-line purpose, source story (`US-<RID>-<N>`) or feature doc link. |
| `## Contract semantics` | Per-entry-point or per-surface-section: idempotency, side-effects, ordering / concurrency guarantees, transactional posture, async-ness, deadlines / timeouts, retries. The behavioral contract beyond the type signature. |
| `## Error model` | The standardized error envelope used across the surface: typed error variants (Rust `Result<T, E>`, TypeScript discriminated union, Python exception class hierarchy), HTTP status taxonomy, error-code namespace. Declare ONE form per anchor; consumers see one shape. |
| `## Stability + compatibility` | Stability posture (stable / evolving / experimental / private) + semver commitment (or equivalent — `0.x` rules, hand-rolled versioning) + deprecation policy (how long before a deprecated surface is removed; the smoke-signal callers should watch). |
| `## Design decisions` | `D-API<n>` rows: each load-bearing API choice with rationale. Bridge to [[FCT Decisions]] for decisions citing a ruleset. |

Other H2s (e.g., `## Concurrency`, `## Authentication`, `## Telemetry`, `## Migration`) join when applicable.

## Reference example

See [[CAE API Design]] — the CAE scheduler crate shows the canonical shape for a library-form API surface (Rust). For a sub-skill-form API surface example see [[ATL]] `/atlas add` / `/atlas update` (under the atlas anchor — pending).

## Relationship to other facets

| Facet | Owns | Boundary |
|---|---|---|
| **[[FCT UX Design]]** | Human user-facing surface (CLI commands, screens, organization, output shapes for the eye). | Different *consumer*. |
| **[[FCT Module Doc]]** | Per-module reference documentation (what exists in the source tree, often generated). | Different *altitude* — API Design is intent; API Doc is reference. |
| **[[FCT Architecture]]** | Internal organization (modules, dependency direction, layering). | Different *audience* — Architecture is for the system's builders; API Design is for consumers. |
| **[[FCT Interface]]** | Internal layer/component contracts (between subsystems within the anchor). | Different *visibility scope* — Interface is internal; API Design is the public surface. |
| **[[FCT CLI]]** | Exhaustive flag/exit-code reference for CLI binaries. | Different *form* — CLI doc is reference; API Design covers structured (`--json`) output contract when the CLI doubles as a programmatic surface. |

## See also

- [[FCT UX Design]] — sibling facet covering the human surface.
- [[FCT Module Doc]] — reference documentation for the implemented modules.
- [[FCT Architecture]] — internal organization that backs the API surface.
- [[FCT Decisions]] — bridge for D-API rows that cite rulesets.
- [[FCT Status]] — `{NAME} Status.md` carries the API-Design facet state.
- [[DSC progressive-disclosure]] — preface zone discipline.
- [[DSC markdown]] — markdown authoring discipline.


# RULESET R-api
include::
description:: Rules for `{NAME} API Design.md` — programmatic user-facing surface intent.

Embedded ruleset for the API Design facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Adopted via [[R-facet]] umbrella.

### RULE R-api-01 — Preface zone carries TLDR (figure recommended) (checked)

The doc opens with a dispatch table, then a TLDR (3–8 single-line bullets), then optionally a figure (schema diagram, sequence diagram, or a canonical code snippet) — before the first body H2.

**Check pattern:** read the doc; assert dispatch table + TLDR precede the first non-preface H2; figure presence is sampled but not enforced.

**Why:** programmatic consumers skim contracts for the shape they're going to integrate against; TLDR gives the integrator the at-a-glance pitch, figure (when present) gives the one example that beats prose.

### RULE R-api-02 — Consumer declared explicitly (stated)

The first body H2 is `## Consumer` and names who calls programmatically, in what language/runtime/transport, with what integration shape. One paragraph, not a vague "this exposes an API."

**Check pattern:** assert `## Consumer` exists as the first body H2; body names language (Rust crate / TS package / HTTP service / sub-skill called by another skill) + integration shape (sync call / event stream / batch).

**Why:** every contract decision (error envelope, async-ness, schema serialization) depends on the consumer. Leaving it implicit forces the integrator to reverse-engineer from signatures.

### RULE R-api-03 — Surface table is the spine (checked)

A `## Surface` H2 carries a canonical table listing every public callable / endpoint / sub-skill entry once: name, signature or schema sketch, one-line purpose, source story (`US-<RID>-<N>`) or feature doc link. No entry lives only in prose; every one is in the table.

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

### RULE R-api-08 — Design decisions captured as D-API<n> rows (sampled)

Load-bearing API choices (a chosen error envelope over an obvious alternative, a chosen async-ness model, a chosen schema-serialization format) appear as `D-API<n>` rows under `## Design decisions` with: choice, alternatives considered, rationale.

**Check pattern:** sample design decisions; assert each row has Choice + Alternatives + Rationale.

**Why:** API design choices look obvious in retrospect but were contingent — capturing them prevents the next consumer from re-litigating settled questions.

### RULE R-api-09 — Distinct from API Doc, Architecture, UX Design (stated)

API Design owns the *intent* of the programmatic surface. It is NOT:

- The per-module reference of *what exists* — that's [[FCT Module Doc]].
- The internal organization of the system — that's [[FCT Architecture]].
- The human-facing surface — that's [[FCT UX Design]].

When API Design starts enumerating every function in every module, or narrating the dependency graph, or describing what the human sees on the screen, it is leaking the wrong content. Migrate the leak to the sibling facet.

**Check pattern:** sample API Design docs; assert no per-module function inventories (API Doc scope), no internal dependency narratives (Architecture scope), no human screen / command lists (UX Design scope).

**Why:** facet leakage erodes the cut. The consumer who wants reference goes to API Doc; if it lives in API Design, they don't find it where they look.

# BRIEF

- **This is the facet spec for `{NAME} API Design.md` — authority over shape, not over the contracts themselves.** Anchor-specific API contracts live in each anchor's own API Design doc; this file defines the spine (`## Consumer`, `## Surface`, `## Contract semantics`, `## Error model`, `## Stability + compatibility`, `## Design decisions`) and the embedded `R-api` ruleset those docs are audited against.
- **Embedded `# RULESET R-api` is co-located, not external.** Per F133 the ruleset lives inside this facet file under a top-level `# RULESET R-api` H1, adopted via the `R-facet` umbrella; do NOT split it into a sibling file, and do NOT add per-rule commentary to the facet body — rule rationale belongs in each rule's **Why** paragraph.
- **The cut against neighbors is load-bearing — don't blur it.** API Design = *intent* of the programmatic surface; [[FCT Module Doc]] = *what exists* in source (reference); [[FCT Architecture]] = *internal organization*; [[FCT UX Design]] = *human* surface. When tempted to add per-module inventories, dependency narratives, or screen flows here, redirect to the sibling facet — citing the redirect is fine, inlining the content is leakage.
- **Inclusion test for a new section / rule:** does it constrain what *every* anchor's API Design doc must contain or how it's shaped? If yes, it belongs here (as a section in the spine or as an `R-api-<n>` rule). If it's a contract decision specific to one anchor, it belongs in that anchor's API Design doc as a `D-API<n>` row, not here.
- **Rule numbering is append-only.** New rules get the next free `R-api-<n>`; never renumber existing rules (downstream `D-API<n>` rows in anchor docs cite by number). When a rule is retired, leave the number burned and add a tombstone line — don't reuse the slot.
- **`## Relationship to other facets` and `## See also` are the canonical cross-link surfaces.** When a new sibling facet ships or an existing one is renamed, update both tables here (and the corresponding `R-api-09` rule body which enumerates the cut) — stale cross-references silently teach the wrong boundary.
- **When the facet is N/A for an anchor** (no library form, no sub-skill invocation surface, no integration story), the anchor marks it `none` in [[FCT Status]] and omits the file entirely; this facet spec does NOT change shape based on that — anchors opt out, the spec stays whole.
