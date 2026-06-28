---
description: per-anchor architecture overview — anchor-folder form with subsystems; standard section order; mandatory visual diagram (Excalidraw, never ASCII); subsystem dispatch table with link convention; API detail lives in sub-docs, not the main page.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Design Docs]] → [FCT Architecture](hook://p/FCT%20Architecture)

# FCT Architecture
**Audited examples:** [[HBR Architecture]], [[CAE Architecture]], [[OBU Architecture]], [[MUX Architecture]], [[HA Architecture]]

Facet spec defining the per-anchor system-architecture overview — its anchor-folder shape, standard section order, mandatory visual figure, subsystem dispatch table, and split between conceptual map (entry-point doc) and contract surface (API sub-doc).

**Related:** [[FCT Module Doc]],  [[FCT Decisions]],  [[FCT Design Dispatch]],  [[R-diagram]]
**Examples:** [[CAE Architecture\|minimal (Excalidraw, partial subsystem docs)]],  [[HBR Architecture\|fuller (D2/SVG, all subsystems linked)]]

**TLDR** — One `{NAME} Architecture/` folder per anchor (cardinality: **one**). Entry-point doc has four required sections in order: Overview → Architecture diagram → Subsystems → supporting context. Diagram must be a real visual artifact (SVG/Excalidraw/D2); ASCII art is forbidden. Subsystem docs use kebab naming `{NAME}-{Subsystem}.md`; `[[double-bracket]]` = real doc, `[single-bracket]` = placeholder. Public API detail lives in a sibling `{NAME} API.md`, not the entry-point page.

**Location:** `{NAME} Design/` — a single `{NAME} Architecture.md` by default, upgraded to a `{NAME} Architecture/` folder-doc (entry-point `{NAME} Architecture/{NAME} Architecture.md`, subsystem docs as siblings) once it grows subsystems. **Architecture is a child of Design** — the F094 / CAB-Log-2026-06-08 anchor-root placement was **reversed 2026-06-27** per user direction: architecture is a design artifact and lives with the rest of the design.

The Architecture facet is the **system-level overview** — how the codebase is structured, how its components interact, the thread model, the data flow. It's a synthesis-level doc (`/architect`-maintained with conservative-edit posture); lives in `{NAME} Design/` alongside the PRD, UX/API Design, Decisions, and Roadmap (the `{NAME} Track/`, `{NAME} User Docs/`, `{NAME} Dev Docs/` trees are siblings of Design at the anchor root). Maintained by `[[skills/architect/SKILL|/architect]]`.

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

**Common deviations seen in real instances (all flagged, all fixable):**
- **Inline-body spine** — older docs (CAE, MUX, OBU) put the Overview paragraph and the diagram embed directly under the H1 with no `## Overview` / `## Architecture diagram` headers. The content is present but unsectioned; the fix is to promote the inline prose into the two required H2s so the spine is machine-detectable.
- **ASCII diagram** — OBU shipped a fenced-code-block box-and-arrow drawing. Forbidden; replace with a real visual artifact (SVG/Excalidraw embed).
- **Missing figure** — HA shipped a subsystems roll-up with no diagram at all. The `## Architecture diagram` section with an `![[…]]` embed is required, even for a placeholder-heavy architecture.
- **Subsystems in the breadcrumb table** — MUX folded its subsystem inventory into the top-of-doc dispatch table rather than a dedicated `## Subsystems` H2 with the `SUBSYSTEMS | Description` table. The fix is a standalone `## Subsystems` section.
- **Non-kebab subsystem names** — HA/OBU used space-form (`HA Anchor Arch`, `OBU Client`) or `… Arch` suffixes. Normalize to kebab `{NAME}-{Subsystem}` per § Subsystem dispatch.

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
4. **Fill the reading pane — ABSOLUTE DEFAULT.** The embed MUST carry a large width hint so the figure fills the page: `![[<NAME> Architecture.svg|2400]]`. Obsidian caps the hint to the pane, so over-specifying is safe and correct. A **bare embed `![[x.svg]]` is forbidden** — it renders as a tiny fit-to-column thumbnail. A smaller fixed width is permitted ONLY for a figure explicitly marked inline/thumbnail. (Same enforcement lives in the markdown discipline — see [[DSC markdown]] R-markdown diagram-sizing rule.)

Same rules for `## Thread layout` and any other in-architecture diagrams.

## What does NOT belong on the entry-point Architecture page

The main `{NAME} Architecture.md` is a **conceptual map**. Detail belongs elsewhere:

| Content kind | Belongs in |
|---|---|
| Public API surface (modules, classes, functions, signatures) | `{NAME} API.md` (sub-doc inside `{NAME} Architecture/`); follows [[FCT Module Doc]] rules |
| Class/function/method tables for a specific subsystem | That subsystem's own doc (e.g., `{NAME} Scheduler.md`) |
| Per-module schemas, error types, CLI surface | `{NAME} API.md` or the relevant subsystem doc |
| Project-wide principles | `{NAME} Decisions/{NAME} Decisions.md` — reference by `[[…\|D<n>]]`, don't restate |
| File-tree / source layout | `{NAME} Dev Docs/{NAME} Files.md` |

If a class table starts showing up on the Architecture page, that's a smell that the doc is doing two jobs. Split it.

## Trait applicability

Available to any anchor with the `Code` trait. Optional for non-code anchors — a `Topic` anchor's "architecture" might be its content taxonomy, but that's usually expressed in the anchor page or PRD instead.

**Cardinality: one** — each anchor has exactly one `{NAME} Architecture/` folder and one `{NAME} Architecture.md` entry-point doc. Subsystem docs inside the folder are many, but the facet itself (the entry-point doc + folder) is singular per anchor.

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

# RULESET R-architecture
include::
where:: file:{ANCHOR}/**/* Architecture.md
description:: spec for the `{NAME} Architecture.md` entry-point design facet — section spine, mandatory visual figure, subsystem dispatch + link convention, API content kept off the page

Embedded ruleset for the Architecture facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Adopted via the `R-facet` umbrella; an anchor that wants its `{NAME} Architecture.md` audited pulls `R-facet` from its `{NAME} Decisions.md`. The `where::` glob selects the entry-point doc only (`* Architecture.md`); subsystem docs (kebab `{NAME}-*.md`) follow [[FCT Module Doc]], not this ruleset.

### RULE R-architecture-01 — Entry-point doc is `{NAME} Architecture.md` (checked)
check:: architecture_filename_correct

The facet entry-point doc is named `{NAME} Architecture.md` and lives in `{NAME} Design/` — as a single file by default, or `{NAME} Design/{NAME} Architecture/{NAME} Architecture.md` in folder-doc form once it grows subsystems. (Anchor-root instances from the reversed F094 placement are tolerated but flagged for migration back into Design.)

**Check pattern:** a file matching `{NAME} Architecture.md` exists; its enclosing folder is `{NAME} Architecture/`.

**Why:** the basename is what `/architect` and `/audit architecture` key on; subsystem docs use the kebab `{NAME}-*` form so they never collide with this name.

### RULE R-architecture-02 — `# {NAME} Architecture` H1 present (checked)
check:: architecture_h1_present

The doc's first markdown heading is `# {NAME} Architecture` (single H1, matching the basename). No `[[wiki]] ·`-prefixed or otherwise decorated H1.

**Check pattern:** first `^# ` line equals `# {NAME} Architecture`.

**Why:** a clean H1 is the doc title every dispatch table and breadcrumb echoes; decorated H1s (`# [[HA]] · HA Architecture`) break title extraction.

### RULE R-architecture-03 — `## Overview` H2 present (checked)
check:: overview_section_present

The doc has a `## Overview` H2 carrying one paragraph (rarely two) that says what kind of system this is at the highest structural level.

**Check pattern:** grep for `^## Overview`; assert non-empty body before the next H2.

**Why:** the most common deviation is an inline Overview under the H1 with no header — present but unsectioned, so the spine isn't machine-detectable. The H2 makes the framing explicit and orderable.

### RULE R-architecture-04 — `## Architecture diagram` H2 present with a figure embed (checked)
check:: architecture_diagram_section_with_embed

The doc has a `## Architecture diagram` H2 containing at least one image embed (`![[…]]` or `![](…)`) pointing at a real visual artifact (`.svg` / `.png` / `.excalidraw`-derived).

**Check pattern:** grep for `^## Architecture diagram`; within its body assert ≥ 1 `!\[\[.+\]\]` or `!\[.*\]\(.+\)`.

**Why:** this is the `missing-figure` audit finding. A subsystems-only roll-up with no diagram (seen in HA) fails the core promise of the facet — the visual component map.

### RULE R-architecture-05 — No ASCII-art diagram (checked)
check:: no_ascii_diagram

No fenced code block in the doc contains box-drawing characters (`┌ ┐ └ ┘ │ ─ ▼ ▲ ◄ ►`) or an arrow-and-pipe layout used as a diagram.

**Check pattern:** scan fenced blocks for box-drawing / arrow glyphs forming a diagram; flag any match (`ascii-diagram` finding).

**Why:** ASCII art renders too small in Obsidian, doesn't scale, and signals casualness (durable feedback). OBU shipped one — the fix is a real SVG embed.

### RULE R-architecture-06 — `## Subsystems` H2 present with a dispatch table (checked)
check:: subsystems_section_present

The doc has a `## Subsystems` H2 containing a markdown table whose first column lists the subsystems and whose header reads `SUBSYSTEMS | Description` (or close kin).

**Check pattern:** grep for `^## Subsystems`; assert a markdown table follows with ≥ 1 data row.

**Why:** the subsystem inventory is the load-bearing structural index. MUX folded it into the breadcrumb dispatch table; the fix is a dedicated `## Subsystems` section so the inventory is unambiguous and audit-detectable.

### RULE R-architecture-07 — First four sections in spine order (checked)
check:: spine_order_correct

The first four H2 (or H1-then-H2) sections appear in the order `Overview → Architecture diagram → Subsystems → [first supporting H2]`. No supporting section (Process model, Design decisions, …) precedes Subsystems.

**Check pattern:** extract H2 sequence; assert the first three are `Overview`, `Architecture diagram`, `Subsystems` in that order.

**Why:** the spine is the load-bearing invariant (`section-order` finding). A reader should always meet what-it-is, then the picture, then the parts, before any supporting context.

### RULE R-architecture-08 — Subsystem docs use kebab `{NAME}-{Subsystem}` naming (checked)
check:: subsystem_kebab_naming

Every subsystem referenced in the Subsystems table uses kebab form `{NAME}-{Subsystem}` (anchor slug, hyphen, subsystem name; internal hyphens for multi-word). No space-form (`MUX Data`), no `… Arch` / `… Subsystem` suffix.

**Check pattern:** each subsystem link/placeholder target matches `^{NAME}-[A-Za-z0-9-]+$`.

**Why:** kebab form gives basename uniqueness against module docs, no markdown collision, and visual grouping (`{NAME}-*` sorts together). HA/OBU used space-form + `Arch` suffixes that collide and clutter.

### RULE R-architecture-09 — Link convention: `[[double]]` = real doc, `[single]` = placeholder (sampled)
check:: subsystem_link_convention

In the Subsystems table, `[[double-bracket]]` entries resolve to an existing subsystem doc; `[single-bracket]` entries are plain-text placeholders for unauthored docs (no broken wiki-link).

**Check pattern:** for each `[[…]]` subsystem link assert the target file exists (`missing-subsystem-doc`); single-bracket entries skip the existence check.

**Why:** lets a partially-authored architecture be honest — complete inventory, only real docs link. A `[[double-bracket]]` to a non-existent doc pollutes the link graph and lies about what's authored.

### RULE R-architecture-10 — No API / class-table content on the entry-point page (sampled)
check:: no_api_content_on_arch_page

The entry-point doc carries no per-module class / function / method / signature tables. That detail lives in `{NAME} API.md` or the relevant subsystem doc.

**Check pattern:** flag tables whose header rows name classes/methods/signatures, or fenced code blocks of API signatures, in the entry-point doc (`api-content-on-arch-page` finding).

**Why:** the entry-point page is a conceptual map; when a class table appears it's doing two jobs and both altitudes are lost. Split it out.

### RULE R-architecture-11 — Diagram has arrows, not just boxes (sampled)
check:: diagram_has_arrows

The architecture figure shows directional/labeled connections between components, not a bare collection of boxes.

**Check pattern:** sampled judgment over the embedded figure — assert at least one connecting arrow/edge between named boxes.

**Why:** boxes without arrows are a list, not an architecture. Every relationship that matters needs a connection. Audited against [[R-diagram]] for the full structural/aesthetic ruleset.

### RULE R-architecture-12 — Project-wide principles referenced, not restated (sampled)
check:: principles_referenced_not_restated

Anchor-wide principles/rulings are linked to `{NAME} Decisions` (e.g. `[[… |D<n>]]`), not copy-pasted into the Architecture doc. Tactical architecture-only decisions may live here in a numbered `## Design decisions` table.

**Check pattern:** sampled — flag long restated principle prose that duplicates `{NAME} Decisions` content verbatim.

**Why:** restating principles forks the source of truth; the Architecture doc drifts from Decisions. Reference keeps one canonical home (HBR/CAE both reference; this is the good pattern).

# BRIEF

- **This file is the authoritative facet spec for the Architecture anchor-folder** — `/architect`, `/audit architecture`, and every per-anchor `{NAME} Architecture/` doc derive their structure from here. Edits here change behavior across every Code-trait anchor.
- **NOT a tutorial, not a worked example, not API-doc rules.** Walk-throughs live at [[CAE Architecture]]; API-doc structure lives at [[FCT Module Doc]]; per-anchor decisions live in `{NAME} Decisions/`. Link to those — don't inline their content here.
- **Inclusion test for new content:** a rule belongs in this spec only if it applies to *every* Code-trait anchor's Architecture facet. Anchor-local quirks → `{NAME} Decisions.md`. Rules-set-wide diagram constraints → [[R-diagram]]. Markdown-rendering rules → [[R-markdown]].
- **Load-bearing invariants — do not weaken without a corresponding CAB Log entry:** (1) the first four sections in exact order (`Overview → Architecture diagram → Subsystems → first supporting H2`); (2) subsystem doc naming uses kebab form `{NAME}-{Subsystem}.md`; (3) `[[double-bracket]]` = real doc, `[single-bracket]` = placeholder — this convention drives `/audit architecture`'s `missing-subsystem-doc` check; (4) ASCII diagrams are forbidden (`ascii-diagram` audit finding).
- **The `## Audit` table is the contract with `/audit architecture`.** When a finding ID is added or renamed here, the audit script must change in lockstep. Don't introduce a finding name in the script without listing it here, and don't list one here without wiring it in the script.
- **The embedded `# RULESET R-architecture` block is the machine-readable form of this spec.** Twelve rules (`R-architecture-01..12`) mirror the `## Audit` findings + the section-spine / link-convention / kebab-naming invariants. Rule IDs are monotonic-forever — never renumber. Keep the rules and the prose above in AGREEMENT: a spec change that alters a section or convention must update the matching rule, and vice versa.
- **Audited examples (top of file) are the canonical worked instances** — HBR (clean maximal), CAE (inline-spine fix), OBU (ASCII→SVG fix), MUX (subsystems-out-of-breadcrumb fix), HA (missing-figure fix). They demonstrate the common deviations and their good fixes.
- **Keep the See also list curated, not exhaustive.** Peer specs that a reader genuinely needs to cross-reference (Module Doc, Rules, R-diagram, Decisions, Design Dispatch, worked example) — not every distantly-related CAB file. New peers added here should also link back.
