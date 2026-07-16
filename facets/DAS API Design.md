---
description: "facet spec this doc follows"
---

# DAS API Design
Facet spec defining the shape, required sections, and ruleset for an anchor's `{slug} API Design.md` — the programmatic (code-to-code or sub-skill) user surface.

| -[[DAS API Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS API Design](hook://p/DAS%20API%20Design) |
| --- | --- |
| Related | [[DAS UX Design]],  [[DAS Architecture]],  [[DAS Module Doc]],  [[DAS Decisions]],   |
| Examples | [[FEX API Design\|minimal (library crate)]],  [[HBR API Design\|fuller (service + sub-skill)]],   |
| Rules | [[R-api]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Log]],  [[DAS Messages]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

API Design specifies the **programmatic user surface** of the anchor — what shape another piece of code (or another agent invoking this as a sub-skill) sees when integrating. It is sibling to [[DAS UX Design]] (the *human* user surface). The cut between them is **who the consumer is**: API = code calling; UX = human reading or invoking.

> [!info] Scope guard
> "API" here means the *intent* of the programmatic surface — how it's shaped, what it commits to. Distinct from [[DAS Module Doc]] (per-module reference; *what exists* in the source tree, often generated) and from [[DAS Architecture]] (internal organization; *how* the system is built). API Design is the *what* of the public contract.

The API Design doc is the **current spec** — the contract surface today. Rationale lives in [[DAS Decisions]] or in the document's own `D-API<n>` design-decision rows (see [[R-api]]). If the anchor has no programmatic consumer (no library form, no sub-skill invocation surface, no integration story), this facet is N/A; mark it `none` in [[DAS Status]] and omit the file.

## When this facet applies

- The anchor ships a library, crate, package, or module that other code imports.
- The anchor is a skill whose sub-skills are invoked by other skills (e.g. `/design prd` called from `/design`).
- The anchor exposes a service or RPC surface (HTTP / gRPC / pub-sub / queue).
- The anchor's CLI is *also* used programmatically (consumers parsing its `--json` output) — API Design covers the structured-output contract; UX Design covers the human form.

When none of the above hold, omit the facet.

## Location

`{slug} Docs/{slug} Design/{slug} API Design.md` — single-file form. Upgrade to anchor-folder form `{slug} API Design/` only when distinct sub-surfaces (e.g., library API + service API + sub-skill API in the same anchor) warrant separate files.

Peer of [[DAS Architecture]] and [[DAS UX Design]] under [[DAS Design Dispatch|Design]].

## Preface zone

Per [[DAS progressive-disclosure]]:

- **TLDR** required — 3–8 short bullets: consumer, surface kind (library / sub-skill / service), error model, stability posture, compatibility horizon.
- **Figure** optional but recommended — schema diagram (struct/types relationship), sequence/interaction diagram (call → response shape), or a representative code snippet of one canonical call.

## Required section spine

| H2 | What it carries |
|---|---|
| `## Consumer` | One paragraph: who calls programmatically, what language/runtime/transport, what their integration shape is (synchronous call? streamed events? batch job?). Sets the frame. |
| `## Surface` | The spine table. Every public callable / endpoint / sub-skill entry listed once with: name, signature (or schema sketch), one-line purpose, source story (`US-<slug>-<N>`) or feature doc link. |
| `## Contract semantics` | Per-entry-point or per-surface-section: idempotency, side-effects, ordering / concurrency guarantees, transactional posture, async-ness, deadlines / timeouts, retries. The behavioral contract beyond the type signature. |
| `## Error model` | The standardized error envelope used across the surface: typed error variants (Rust `Result<T, E>`, TypeScript discriminated union, Python exception class hierarchy), HTTP status taxonomy, error-code namespace. Declare ONE form per anchor; consumers see one shape. |
| `## Stability + compatibility` | Stability posture (stable / evolving / experimental / private) + semver commitment (or equivalent — `0.x` rules, hand-rolled versioning) + deprecation policy (how long before a deprecated surface is removed; the smoke-signal callers should watch). |
| `## Design decisions` | `D-API<n>` rows: each load-bearing API choice with rationale. Bridge to [[DAS Decisions]] for decisions citing a ruleset. |

Other H2s (e.g., `## Concurrency`, `## Authentication`, `## Telemetry`, `## Migration`) join when applicable.

## Reference example

See [[FEX API Design]] — the CAE scheduler crate shows the canonical shape for a library-form API surface (Rust). For a sub-skill-form API surface example see [[ATL]] `/atlas add` / `/atlas update` (under the atlas anchor — pending).

## Relationship to other facets

| Facet | Owns | Boundary |
|---|---|---|
| **[[DAS UX Design]]** | Human user-facing surface (CLI commands, screens, organization, output shapes for the eye). | Different *consumer*. |
| **[[DAS Module Doc]]** | Per-module reference documentation (what exists in the source tree, often generated). | Different *altitude* — API Design is intent; Module Doc is reference. |
| **[[DAS Architecture]]** | Internal organization (modules, dependency direction, layering). | Different *audience* — Architecture is for the system's builders; API Design is for consumers. |
| **[[DAS Interface]]** | Internal layer/component contracts (between subsystems within the anchor). | Different *visibility scope* — Interface is internal; API Design is the public surface. |
| **[[DAS CLI]]** | Exhaustive flag/exit-code reference for CLI binaries. | Different *form* — CLI doc is reference; API Design covers structured (`--json`) output contract when the CLI doubles as a programmatic surface. |

## See also

- [[DAS UX Design]] — sibling facet covering the human surface.
- [[DAS Module Doc]] — reference documentation for the implemented modules.
- [[DAS Architecture]] — internal organization that backs the API surface.
- [[DAS Decisions]] — the D-record form for API decisions (rules implement them; linkage on the rule side).
- [[DAS Status]] — `{slug} Status.md` carries the API-Design facet state.
- [[DAS progressive-disclosure]] — preface zone discipline.
- [[DAS markdown]] — markdown authoring discipline.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the embedded `# RULESET R-api` is its machine-readable form.)*

- **Inclusion test:** a new section or rule belongs here only if it constrains what *every* anchor's API Design doc must contain or how it's shaped; a contract decision specific to one anchor belongs in that anchor's doc as a `D-API<n>` row.
- **Rule numbering is append-only** — never renumber existing `R-api-<n>` rules (downstream `D-API<n>` rows cite by number); a retired rule leaves its number burned with a tombstone line.
- **Keep the ruleset embedded** — per F133 it stays inside this file under `# RULESET R-api`; don't split it into a sibling file, and rule rationale belongs in each rule's **Why** paragraph, not the facet body.
- **Cross-ref integrity** — when a sibling facet ships or is renamed, update `## Relationship to other facets`, `## See also`, and the `R-api-09` rule body together; stale cross-references silently teach the wrong boundary.
