---
description: per-anchor architecture overview — anchor-folder form with subsystems; standard section order; mandatory visual diagram (Excalidraw, never ASCII); subsystem dispatch table with link convention; API detail lives in sub-docs, not the main page.
---
# FCT Architecture

Facet spec defining the per-anchor system-architecture overview — its anchor-folder shape, standard section order, mandatory visual figure, subsystem dispatch table, and split between conceptual map (entry-point doc) and contract surface (API sub-doc).

**Location:** `{NAME} Architecture/` (anchor-folder at the **anchor root**, per CAB Log 2026-06-08; previously `{NAME} Docs/{NAME} Design/{NAME} Architecture/`). The entry-point doc is `{NAME} Architecture/{NAME} Architecture.md`; subsystem docs are siblings inside that folder.

The Architecture facet is the **system-level overview** — how the codebase is structured, how its components interact, the thread model, the data flow. It's a synthesis-level doc (`/architect`-maintained with conservative-edit posture); lives at the anchor root alongside `{NAME} Design/`, `{NAME} Track/`, `{NAME} User Docs/`, `{NAME} Dev Docs/`. Maintained by `[[skills/architect/SKILL|/architect]]`.

**Scope clarification.** "Architecture" here means **the system-architecture story** specifically — components, modules, interfaces, data flow, thread model. It is NOT the umbrella for all design content; that's `{NAME} Design/`. UX Design is a peer of Architecture, not a child.

**Architecture vs Public API doc.** Architecture is internal structure ("how is this codebase organized?"). Public API documentation — the surface a caller imports against — lives in a **separate sub-document** inside the Architecture folder (e.g., `{NAME} API.md`), linked from the main Architecture doc. The main page shows the conceptual structure; the module doc shows the contract. See [[FCT Module Doc]] for the module doc rules.


## Folder shape

```
{NAME} Architecture/
├── .anchor                                 ← folder-anchor marker
├── {NAME} Architecture.md                  ← entry-point doc (this facet)
├── {NAME} API.md                           ← (optional) public-API sub-doc
├── {NAME}-<Subsystem-1>.md                 ← single-file subsystem (kebab form, e.g., CAE-Scheduler.md)
├── {NAME}-<Subsystem-2>/                   ← multi-file subsystem (folder-doc form, kebab form)
│   ├── {NAME}-<Subsystem-2>.md             ← subsystem dispatch + figure
│   └── {NAME} <Subsystem-2> <Module-N>.md  ← per-module docs as needed
└── {NAME}-<Subsystem-3>.excalidraw         ← diagram source files alongside (kebab form)
```

**Subsystem-as-folder upgrade** is reversible and case-by-case: single-file subsystems live as `.md` siblings; subsystems that decompose further upgrade to sub-folders.

**Module-to-subsystem invariant**: every module belongs to exactly one subsystem. Orphans + duplicates surface via `/audit architecture`.

**Bidirectional cross-linking**: every module doc carries an `Arch` row in its top-of-doc dispatch table (see [[FCT Module Doc]]) pointing at the most-specific architecture destination. `/architect` maintains both directions.

**Working example:** [[CAE Architecture]] (`~/ob/kmr/SYS/Bespoke/Skill Agent/CAE/CAE Architecture/`).


## Standard section order (entry-point doc)

The Architecture entry-point doc follows this order. Sections are required unless marked optional.

| # | Section | Purpose |
|---|---|---|
| 1 | Top of doc (per F060) | YAML frontmatter + `# {NAME} Architecture` H1 + breadcrumb + dispatch-table placeholder. |
| 2 | `## Overview` | One paragraph (rarely two) — what this system *is*, the highest-level structural framing. Reader leaves knowing what kind of thing they're looking at. |
| 3 | `## Architecture diagram` | The system-level component figure. Visual artifact (Excalidraw + exported PNG/SVG embed), NEVER ASCII. Show boxes-and-arrows: who calls whom; who persists; where the I/O boundary is. **One paragraph max** under the diagram — the minimum text needed to read the figure. Long descriptions belong elsewhere. |
| 4 | `## Subsystems` | Dispatch table listing every subsystem with one-line descriptions. See § Subsystem dispatch below. Real docs use `[[double-bracket]]` wiki-links; placeholder/future subsystems use `[single-bracket]` plain text (no link). |
| 5 | `## Module grouping` (optional) | High-level prose grouping the modules into coherent areas ("Scheduling core" / "Infrastructure" / etc.). Module *summaries* OK; per-module class/function tables do NOT belong here. |
| 6 | `## Process model` (optional) | Single-process, daemon, multi-process — the runtime topology. One paragraph. |
| 7 | `## Thread layout` (when threads exist) | Visual diagram (Excalidraw) of the thread topology + brief description. |
| 8 | `## Design decisions` (optional) | Numbered table (D1, D2, …) of tactical decisions specific to this architecture. Project-wide *principles* live in `{NAME} Decisions/` and are referenced here, not restated. |
| 9 | `## See also` (optional) | Links to peer design docs (PRD, Decisions, API). |

**No fixed-order requirement past the first four** — the spine is `Overview → Architecture diagram → Subsystems → [supporting context]`. The first four sections in that exact order are the load-bearing invariant.


## Subsystem dispatch table

Section 4's subsystems list takes this shape:

```markdown
## Subsystems

| SUBSYSTEMS         | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| [[CAE-Scheduler]]  | priority queue + worker dispatch. Source: `src/execution/`.   |
| [CAE-Store]        | SQLite-backed task persistence (no doc yet)                   |
| [CAE-Retry]        | exponential backoff + dead-letter handling (no doc yet)       |
| [CAE-Clock]        | injectable Clock; production WallClock impl (no doc yet)      |
```

**Subsystem doc naming — kebab form (2026-06-08).** Every subsystem doc filename inside `{NAME} Architecture/` uses the form `{NAME}-{Subsystem}.md` — the anchor slug joined to the subsystem name with a hyphen, no spaces around it. Examples: `CAE-Scheduler.md`, `MUX-Data.md`, `MUX-Native-Bridge.md`. Multi-word subsystem names use internal hyphens (`MUX-Native-Bridge.md`, not `MUX-Native Bridge.md`).

Rationale:
- **Basename uniqueness** — `MUX-Data` doesn't collide with any module doc named `MUX Data` elsewhere in the anchor (e.g., in `MUX Dev Docs/`).
- **No markdown collision** — hyphens have no markdown formatting meaning, so wiki-link display (`[[MUX-Data]]`) and prose mentions render cleanly. (Underscores were ruled out because `_word_` is italic syntax.)
- **Compact** — kebab form adds only one character vs the bare anchor-prefixed name; no qualifier words ("Arch", "Subsystem") cluttering the filename.
- **Visual grouping** — all subsystem docs in a folder sort with the `{NAME}-*` prefix together.

**Link convention:**

- `[[{NAME}-Subsystem]]` — **double brackets**: a real wiki-link to an existing subsystem doc. Aliases (`[[MUX-Data|Data]]`) keep visible text clean in dispatch tables.
- `[{NAME}-Subsystem]` — **single brackets**: placeholder for a subsystem whose doc is not yet authored. Plain text inside brackets; not a clickable link. Makes it visually obvious *where* a doc would live without polluting Obsidian's link graph with broken entries.

This lets the example anchor (CAE) demonstrate a partially-authored architecture honestly — the subsystem inventory is complete, but only the docs that genuinely exist resolve as links.


## Architecture diagram requirements

The figure in § 3 must:

1. **Be a real visual artifact.** Default authoring path: **hand-written SVG** (`/viz svg`) — the agent writes the XML directly with full control over color, font, layout, geometry. The `.svg` file IS the editable source. Alternatives, in order of preference: Excalidraw (`/viz excalidraw`) when a hand-drawn aesthetic is wanted; D2 (`/viz d2`) only when the user asks for D2 specifically. **ASCII art is forbidden** (per durable feedback memory) — it renders too small in Obsidian, doesn't scale, and signals casualness.
2. **Show arrows.** Boxes without arrows aren't an architecture — they're a list. Every relationship that matters in the system structure needs a labeled or directional connection.
3. **Match the subsystems table.** Every box in the diagram should be in the subsystem dispatch table; every subsystem in the table should appear in the diagram (or be a tangent acknowledged in the prose).

Same rules for `## Thread layout` and any other in-architecture diagrams.


## What does NOT belong on the entry-point Architecture page

The main `{NAME} Architecture.md` is a **conceptual map**. Detail belongs elsewhere:

| Content kind | Belongs in |
|---|---|
| Public API surface (modules, classes, functions, signatures) | `{NAME} API.md` (sub-doc inside `{NAME} Architecture/`); follows [[FCT Module Doc]] rules |
| Class/function/method tables for a specific subsystem | That subsystem's own doc (e.g., `{NAME} Scheduler.md`) |
| Per-module schemas, error types, CLI surface | `{NAME} API.md` or the relevant subsystem doc |
| Project-wide principles | `{NAME} Decisions/{NAME} Decisions.md` — reference by `[[…|D<n>]]`, don't restate |
| File-tree / source layout | `{NAME} Dev Docs/{NAME} Files.md` |

If a class table starts showing up on the Architecture page, that's a smell that the doc is doing two jobs. Split it.


## Trait applicability

Available to any anchor with the `Code` trait. Optional for non-code anchors — a `Topic` anchor's "architecture" might be its content taxonomy, but that's usually expressed in the anchor page or PRD instead.


## Audit

`/audit architecture` flags:
- **missing-architecture** — `Code`-trait anchor without `{NAME} Architecture/{NAME} Architecture.md`.
- **missing-figure** — Architecture doc with no `![[…]]` image embed in `## Architecture diagram`.
- **ascii-diagram** — fenced-code-block ASCII art appearing in any architecture doc (per durable feedback).
- **orphan-subsystem** — a subsystem doc inside `{NAME} Architecture/` not listed in the entry-point Subsystems table.
- **missing-subsystem-doc** — a `[[double-bracket]]` subsystem link in the table whose target doc doesn't exist (single-bracket placeholders skip this check).
- **api-content-on-arch-page** — class / function / method tables appearing in the entry-point Architecture doc (should be in API or subsystem doc).
- **section-order** — required first four sections (Overview → Architecture diagram → Subsystems → first supporting H2) out of order.


## See also

- [[FCT Module Doc]] — companion spec for the public-API sub-document.
- [[FCT Ruleset]] — ruleset format spec. Diagrams in architecture docs are audited against rulesets cited by the anchor's decisions.
- [[R-diagram]] — the ruleset every architecture diagram is audited against (22 rules covering structural / aesthetic / semantic / accessibility / hygiene).
- [[FCT Decisions]] — anchor-level applied choices that cite rules from rulesets.
- [[FCT Design Dispatch]] — Architecture sits alongside PRD / Decisions / Interface in `{NAME} Design/`.
- [[CAE Architecture]] — worked example.

# BRIEF

- **This file is the authoritative facet spec for the Architecture anchor-folder** — `/architect`, `/audit architecture`, and every per-anchor `{NAME} Architecture/` doc derive their structure from here. Edits here change behavior across every Code-trait anchor.
- **NOT a tutorial, not a worked example, not API-doc rules.** Walk-throughs live at [[CAE Architecture]]; API-doc structure lives at [[FCT Module Doc]]; per-anchor decisions live in `{NAME} Decisions/`. Link to those — don't inline their content here.
- **Inclusion test for new content:** a rule belongs in this spec only if it applies to *every* Code-trait anchor's Architecture facet. Anchor-local quirks → `{NAME} Decisions.md`. Rules-set-wide diagram constraints → [[R-diagram]]. Markdown-rendering rules → [[R-markdown]].
- **Load-bearing invariants — do not weaken without a corresponding CAB Log entry:** (1) the first four sections in exact order (`Overview → Architecture diagram → Subsystems → first supporting H2`); (2) subsystem doc naming uses kebab form `{NAME}-{Subsystem}.md`; (3) `[[double-bracket]]` = real doc, `[single-bracket]` = placeholder — this convention drives `/audit architecture`'s `missing-subsystem-doc` check; (4) ASCII diagrams are forbidden (`ascii-diagram` audit finding).
- **The `## Audit` table is the contract with `/audit architecture`.** When a finding ID is added or renamed here, the audit script must change in lockstep. Don't introduce a finding name in the script without listing it here, and don't list one here without wiring it in the script.
- **Keep the See also list curated, not exhaustive.** Peer specs that a reader genuinely needs to cross-reference (Module Doc, Rules, R-diagram, Decisions, Design Dispatch, worked example) — not every distantly-related CAB file. New peers added here should also link back.
