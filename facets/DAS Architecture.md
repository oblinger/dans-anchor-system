---
description: per-anchor architecture overview — anchor-folder form with subsystems; standard section order; mandatory visual diagram (Excalidraw, never ASCII); subsystem dispatch table with link convention; API detail lives in sub-docs, not the main page.
---

# DAS Architecture
Specification for the **Architecture** facet — the system-architecture story: a single `{slug} Design/{slug} Architecture.md` that upgrades to a folder-doc as subsystems grow.

| -[[DAS Architecture]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT]] → [DAS Architecture](hook://p/DAS%20Architecture)  |
| --- | --- |
| Related | [[DAS Module Doc]],  [[DAS Decisions]],  [[DAS Design Dispatch]],   |
| Examples | [[FEX Architecture\|minimal (Excalidraw, partial subsystem docs)]],  [[HBR Architecture\|fuller (D2/SVG, all subsystems linked)]],   |
| Rules | [[R-architecture]],  [[R-diagram]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Aspects]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

**Worked examples:** [[HBR Architecture]], [[FEX Architecture]]

*Conceptual source: [[PKM]] (under [[AOT]]) — the through-line the anchor system operationalizes.*

Facet spec defining the per-anchor system-architecture overview — its anchor-folder shape, standard section order, mandatory visual figure, subsystem dispatch table, and split between conceptual map (entry-point doc) and contract surface (API sub-doc).

**TLDR** — One `{slug} Architecture/` folder per anchor (cardinality: **one**). Entry-point doc has four required sections in order: Overview → Architecture diagram → Subsystems → supporting context. Diagram must be a real visual artifact (SVG/Excalidraw/D2); ASCII art is forbidden. Subsystem docs use kebab naming `{slug}-{Subsystem}.md`; `[[double-bracket]]` = real doc, `[single-bracket]` = placeholder. Public API detail lives in a sibling `{slug} API.md`, not the entry-point page.

**Location:** `{slug} Design/` — a single `{slug} Architecture.md` by default, upgraded to a `{slug} Architecture/` folder-doc (entry-point `{slug} Architecture/{slug} Architecture.md`, subsystem docs as siblings) once it grows subsystems. **Architecture is a child of Design** — the F094 / CAB-Log-2026-06-08 anchor-root placement was **reversed 2026-06-27** per user direction: architecture is a design artifact and lives with the rest of the design.

The Architecture facet is the **system-level overview** — how the codebase is structured, how its components interact, the thread model, the data flow. It's a synthesis-level doc (`/architect`-maintained with conservative-edit posture); lives in `{slug} Design/` alongside the PRD, UX/API Design, Decisions, and Roadmap (the `{slug} Track/`, `{slug} User Docs/`, `{slug} Dev Docs/` trees are siblings of Design at the anchor root). Maintained by `[[skills/architect/SKILL|/architect]]`.

**Scope clarification.** "Architecture" here means **the system-architecture story** specifically — components, modules, interfaces, data flow, thread model. It is NOT the umbrella for all design content; that's `{slug} Design/`. UX Design is a peer of Architecture, not a child.

**Architecture vs Public API doc.** Architecture is internal structure ("how is this codebase organized?"). Public API documentation — the surface a caller imports against — lives in a **separate sub-document** inside the Architecture folder (e.g., `{slug} API.md`), linked from the main Architecture doc. The main page shows the conceptual structure; the module doc shows the contract. See [[DAS Module Doc]] for the module doc rules.

## Folder shape

```
{slug} Architecture/
├── .anchor                                 ← folder-anchor marker
├── {slug} Architecture.md                  ← entry-point doc (this facet)
├── {slug} API.md                           ← (optional) public-API sub-doc
├── {slug}-<Subsystem-1>.md                 ← single-file subsystem (kebab form, e.g., CAE-Scheduler.md)
├── {slug}-<Subsystem-2>/                   ← multi-file subsystem (folder-doc form, kebab form)
│   ├── {slug}-<Subsystem-2>.md             ← subsystem dispatch + figure
│   └── {slug} <Subsystem-2> <Module-N>.md  ← per-module docs as needed
└── {slug}-<Subsystem-3>.excalidraw         ← diagram source files alongside (kebab form)
```

**Subsystem-as-folder upgrade** is reversible and case-by-case: single-file subsystems live as `.md` siblings; subsystems that decompose further upgrade to sub-folders.

**Module-to-subsystem invariant**: every module belongs to exactly one subsystem. Orphans + duplicates surface via `/audit architecture`.

**Bidirectional cross-linking**: every module doc carries an `Arch` row in its top-of-doc dispatch table (see [[DAS Module Doc]]) pointing at the most-specific architecture destination. `/architect` maintains both directions.

**Working example:** [[FEX Architecture]].

## Standard section order (entry-point doc)

The Architecture entry-point doc follows this order. Sections are required unless marked optional.

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc (per F060) | YAML frontmatter + `# {slug} Architecture` H1 + breadcrumb + dispatch-table placeholder. |
| 2 | `## Overview` | One paragraph (rarely two) — what this system *is*, the highest-level structural framing. Reader leaves knowing what kind of thing they're looking at. |
| 3 | `## Architecture diagram` | The system-level component figure. Visual artifact (Excalidraw + exported PNG/SVG embed), NEVER ASCII. Show boxes-and-arrows: who calls whom; who persists; where the I/O boundary is. **One paragraph max** under the diagram — the minimum text needed to read the figure. Long descriptions belong elsewhere. |
| 4 | `## Subsystems` | Dispatch table listing every subsystem with one-line descriptions. See § Subsystem dispatch below. Real docs use `[[double-bracket]]` wiki-links; placeholder/future subsystems use `[single-bracket]` plain text (no link). |
| 5 | `## Module grouping` (optional) | High-level prose grouping the modules into coherent areas ("Scheduling core" / "Infrastructure" / etc.). Module *summaries* OK; per-module class/function tables do NOT belong here. |
| 6 | `## Process model` (optional) | Single-process, daemon, multi-process — the runtime topology. One paragraph. |
| 7 | `## Thread layout` (when threads exist) | Visual diagram (Excalidraw) of the thread topology + brief description. |
| 8 | `## Design decisions` (optional) | Numbered table (D1, D2, …) of tactical decisions specific to this architecture. Project-wide *principles* live in `{slug} Decisions/` and are referenced here, not restated. |
| 9 | `## See also` (optional) | Links to peer design docs (PRD, Decisions, API). |

**No fixed-order requirement past the first four** — the spine is `Overview → Architecture diagram → Subsystems → [supporting context]`. The first four sections in that exact order are the load-bearing invariant.

**Common deviations seen in real instances (all flagged, all fixable):**
- **Inline-body spine** — older docs (CAE, MUX, OBU) put the Overview paragraph and the diagram embed directly under the H1 with no `## Overview` / `## Architecture diagram` headers. The content is present but unsectioned; the fix is to promote the inline prose into the two required H2s so the spine is machine-detectable.
- **ASCII diagram** — OBU shipped a fenced-code-block box-and-arrow drawing. Forbidden; replace with a real visual artifact (SVG/Excalidraw embed).
- **Missing figure** — HA shipped a subsystems roll-up with no diagram at all. The `## Architecture diagram` section with an `![[…]]` embed is required, even for a placeholder-heavy architecture.
- **Subsystems in the breadcrumb table** — MUX folded its subsystem inventory into the top-of-doc dispatch table rather than a dedicated `## Subsystems` H2 with the `SUBSYSTEMS | Description` table. The fix is a standalone `## Subsystems` section.
- **Non-kebab subsystem names** — HA/OBU used space-form (`HA Anchor Arch`, `OBU Client`) or `… Arch` suffixes. Normalize to kebab `{slug}-{Subsystem}` per § Subsystem dispatch.

## Subsystem dispatch table

Section 4's subsystems list takes this shape:

```markdown
## Subsystems

| SUBSYSTEMS         | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| [[FEX Scheduler]]  | priority queue + worker dispatch. Source: `src/execution/`.   |
| [CAE-Store]        | SQLite-backed task persistence (no doc yet)                   |
| [CAE-Retry]        | exponential backoff + dead-letter handling (no doc yet)       |
| [CAE-Clock]        | injectable Clock; production WallClock impl (no doc yet)      |

```

**Subsystem doc naming — kebab form (2026-06-08).** Every subsystem doc filename inside `{slug} Architecture/` uses the form `{slug}-{Subsystem}.md` — the anchor slug joined to the subsystem name with a hyphen, no spaces around it. Examples: `CAE-Scheduler.md`, `MUX-Data.md`, `MUX-Native-Bridge.md`. Multi-word subsystem names use internal hyphens (`MUX-Native-Bridge.md`, not `MUX-Native Bridge.md`).

Rationale:
- **Basename uniqueness** — `MUX-Data` doesn't collide with any module doc named `MUX Data` elsewhere in the anchor (e.g., in `MUX Dev Docs/`).
- **No markdown collision** — hyphens have no markdown formatting meaning, so wiki-link display (`[[MUX-Data]]`) and prose mentions render cleanly. (Underscores were ruled out because `_word_` is italic syntax.)
- **Compact** — kebab form adds only one character vs the bare anchor-prefixed name; no qualifier words ("Arch", "Subsystem") cluttering the filename.
- **Visual grouping** — all subsystem docs in a folder sort with the `{slug}-*` prefix together.

**Link convention:**

- `[[{slug}-Subsystem]]` — **double brackets**: a real wiki-link to an existing subsystem doc. Aliases (`[[MUX-Data|Data]]`) keep visible text clean in dispatch tables.
- `[{slug}-Subsystem]` — **single brackets**: placeholder for a subsystem whose doc is not yet authored. Plain text inside brackets; not a clickable link. Makes it visually obvious *where* a doc would live without polluting Obsidian's link graph with broken entries.

This lets the example anchor (CAE) demonstrate a partially-authored architecture honestly — the subsystem inventory is complete, but only the docs that genuinely exist resolve as links.

## Architecture diagram requirements

The figure in § 3 must:

1. **Be a real visual artifact.** Default authoring path: **hand-written SVG** (`/viz svg`) — the agent writes the XML directly with full control over color, font, layout, geometry. The `.svg` file IS the editable source. Alternatives, in order of preference: Excalidraw (`/viz excalidraw`) when a hand-drawn aesthetic is wanted; D2 (`/viz d2`) only when the user asks for D2 specifically. **ASCII art is forbidden** (per durable feedback memory) — it renders too small in Obsidian, doesn't scale, and signals casualness.
2. **Show arrows.** Boxes without arrows aren't an architecture — they're a list. Every relationship that matters in the system structure needs a labeled or directional connection.
3. **Match the subsystems table.** Every box in the diagram should be in the subsystem dispatch table; every subsystem in the table should appear in the diagram (or be a tangent acknowledged in the prose).
4. **Fill the reading pane — ABSOLUTE DEFAULT.** The embed MUST carry a large width hint so the figure fills the page: `![[<slug> Architecture.svg|2400]]`. Obsidian caps the hint to the pane, so over-specifying is safe and correct. A **bare embed `![[x.svg]]` is forbidden** — it renders as a tiny fit-to-column thumbnail. A smaller fixed width is permitted ONLY for a figure explicitly marked inline/thumbnail. (Same enforcement lives in the markdown discipline — see [[DAS markdown]] R-markdown diagram-sizing rule.)

Same rules for `## Thread layout` and any other in-architecture diagrams.

These are the mechanical floor. The judgment half — whether the figure should exist, what it should leave out, and the mistakes that keep recurring — is [[Drawing Wisdom]], the companion beside the the `viz` skill skill.

## What does NOT belong on the entry-point Architecture page

The main `{slug} Architecture.md` is a **conceptual map**. Detail belongs elsewhere:

| Content kind | Belongs in |
|---|---|
| Public API surface (modules, classes, functions, signatures) | `{slug} API.md` (sub-doc inside `{slug} Architecture/`); follows [[DAS Module Doc]] rules |
| Class/function/method tables for a specific subsystem | That subsystem's own doc (e.g., `{slug} Scheduler.md`) |
| Per-module schemas, error types, CLI surface | `{slug} API.md` or the relevant subsystem doc |
| Project-wide principles | `{slug} Decisions/{slug} Decisions.md` — reference by `[[…\|D<n>]]`, don't restate |
| File-tree / source layout | `{slug} Dev Docs/{slug} Files.md` |

If a class table starts showing up on the Architecture page, that's a smell that the doc is doing two jobs. Split it.

## Trait applicability

Available to any anchor with the `code` trait. Optional for non-code anchors — a `topic` anchor's "architecture" might be its content taxonomy, but that's usually expressed in the anchor page or PRD instead.

**Cardinality: one** — each anchor has exactly one `{slug} Architecture/` folder and one `{slug} Architecture.md` entry-point doc. Subsystem docs inside the folder are many, but the facet itself (the entry-point doc + folder) is singular per anchor.

## Audit

`/audit architecture` flags:
- **missing-architecture** — `code`-trait anchor without `{slug} Architecture/{slug} Architecture.md`.
- **missing-figure** — Architecture doc with no `![[…]]` image embed in `## Architecture diagram`.
- **ascii-diagram** — fenced-code-block ASCII art appearing in any architecture doc (per durable feedback).
- **orphan-subsystem** — a subsystem doc inside `{slug} Architecture/` not listed in the entry-point Subsystems table.
- **missing-subsystem-doc** — a `[[double-bracket]]` subsystem link in the table whose target doc doesn't exist (single-bracket placeholders skip this check).
- **api-content-on-arch-page** — class / function / method tables appearing in the entry-point Architecture doc (should be in API or subsystem doc).
- **section-order** — required first four sections (Overview → Architecture diagram → Subsystems → first supporting H2) out of order.

## See also

- [[DAS Module Doc]] — companion spec for the public-API sub-document.
- [[DAS Ruleset]] — ruleset format spec. Diagrams in architecture docs are audited against the anchor's active rulesets.
- [[R-diagram]] — the ruleset every architecture diagram is audited against (22 rules covering structural / aesthetic / semantic / accessibility / hygiene).
- [[DAS Decisions]] — anchor-level recorded choices; rules implement them (rule-side `implements D<N>` linkage).
- [[DAS Design Dispatch]] — Architecture sits alongside PRD / Decisions / Interface in `{slug} Design/`.
- [[FEX Architecture]] — worked example.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the embedded `# RULESET R-architecture` is its machine-readable form; the canonical worked instances are the audited examples listed at the top of the file.)*

- **Tooling derives structure from here** — `/architect` and `/audit architecture` key on this spec, and every per-anchor `{slug} Architecture/` doc follows it; edits change behavior across every `code`-trait anchor.
- **Inclusion test:** a rule belongs here only if it applies to *every* Code-trait anchor's Architecture facet — anchor-local quirks → `{slug} Decisions.md`, ruleset-wide diagram constraints → [[R-diagram]], markdown-rendering rules → [[R-markdown]]. Don't inline tutorial / worked-example / API-doc content — link [[FEX Architecture]] / [[DAS Module Doc]] instead.
- **Don't weaken the load-bearing invariants without a corresponding CAB Log entry:** first-four-section order (R-architecture-07), kebab subsystem naming (R-architecture-08), `[[double-bracket]]` = real / `[single-bracket]` = placeholder (R-architecture-09, drives the `missing-subsystem-doc` check), ASCII-forbidden (R-architecture-05).
- **The `## Audit` table is the contract with `/audit architecture`** — a finding ID added or renamed here must change the audit script in lockstep; never introduce one without the other.
- **Keep the ruleset and the prose in AGREEMENT** — the twelve `R-architecture-01..12` rules mirror the `## Audit` findings and the spine / link-convention / kebab-naming invariants; rule IDs are monotonic-forever (never renumber), and a spec change that alters a section or convention must update the matching rule, and vice versa.
- **Keep the See also list curated, not exhaustive** — only peers a reader genuinely needs to cross-reference; new peers added here should also link back.
