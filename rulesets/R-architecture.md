# RULESET R-architecture
include::
where:: `file:{anchor}/**/* Architecture.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — added 2026-07-13, T014 follow-on.
description:: spec for the `{slug} Architecture.md` entry-point design facet — section spine, mandatory visual figure, subsystem dispatch + link convention, API content kept off the page

Embedded ruleset for the Architecture facet, co-located with the facet spec above per the [[F133 — Rulesets folder convention + facet embedding|F133]] embedding convention. Pulled in via the `R-facet` umbrella; active for an anchor through its traits ([[Warden Semantics]] § Rulesets). The `where::` glob selects the entry-point doc only (`* Architecture.md`); subsystem docs (kebab `{slug}-*.md`) follow [[DAS Module Doc]], not this ruleset.

### RULE R-architecture-01 — Entry-point doc is `{slug} Architecture.md` (checked)
check:: architecture_filename_correct

The facet entry-point doc is named `{slug} Architecture.md` and lives in `{slug} Design/` — as a single file by default, or `{slug} Design/{slug} Architecture/{slug} Architecture.md` in folder-doc form once it grows subsystems. (Anchor-root instances from the reversed F094 placement are tolerated but flagged for migration back into Design.)

**Check pattern:** a file matching `{slug} Architecture.md` exists; its enclosing folder is `{slug} Architecture/`.

**Why:** the basename is what `/architect` and `/audit architecture` key on; subsystem docs use the kebab `{slug}-*` form so they never collide with this name.

### RULE R-architecture-02 — `# {slug} Architecture` H1 present (checked)
check:: architecture_h1_present

The doc's first markdown heading is `# {slug} Architecture` (single H1, matching the basename). No `[[wiki]] ·`-prefixed or otherwise decorated H1.

**Check pattern:** first `^# ` line equals `# {slug} Architecture`.

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

### RULE R-architecture-08 — Design-resident subsystem docs use kebab `{slug}-{Subsystem}` naming (checked)
check:: subsystem_kebab_naming

A subsystem doc that lives in `{slug} Design/` uses kebab form `{slug}-{Subsystem}` (anchor slug, hyphen, subsystem name; internal hyphens for multi-word). No space-form (`MUX Data`), no `… Arch` / `… Subsystem` suffix. Two exemptions (amended 2026-07-13, T017 — the HBR exemplar forced the boundary): a table entry whose `[[link]]` resolves to a real component/group page in the **project tree** (outside any `* Design/` folder) references it by its true space-form name — that page is a real anchor-tree citizen governed by [[DAS Naming]], not an architecture artifact (worked example: [[HBR Architecture]] linking [[HBR Ingest]]); and `[single-bracket]` placeholders are exempt — their home, and so their naming, is decided when the doc is authored.

**Check pattern:** each `[[link]]` target matches `^{slug}-[A-Za-z0-9-]+$`, or resolves to an existing doc outside every `* Design/` folder.

**Why:** kebab form gives Design-resident subsystem docs basename uniqueness against module docs, no markdown collision, and visual grouping (`{slug}-*` sorts together). HA/OBU used space-form + `Arch` suffixes **inside Design** that collide and clutter — that is what this rule flags; real group anchors keep their real names.

### RULE R-architecture-09 — Link convention: `[[double]]` = real doc, `[single]` = placeholder (checked)
check:: subsystem_link_convention

In the Subsystems table, `[[double-bracket]]` entries resolve to an existing subsystem doc; `[single-bracket]` entries are plain-text placeholders for unauthored docs (no broken wiki-link).

**Check pattern:** for each `[[…]]` subsystem link assert the target file exists (`missing-subsystem-doc`); single-bracket entries skip the existence check.

**Why:** lets a partially-authored architecture be honest — complete inventory, only real docs link. A `[[double-bracket]]` to a non-existent doc pollutes the link graph and lies about what's authored.

### RULE R-architecture-10 — No API / class-table content on the entry-point page (sampled)

The entry-point doc carries no per-module class / function / method / signature tables. That detail lives in `{slug} API.md` or the relevant subsystem doc.

**Check pattern:** flag tables whose header rows name classes/methods/signatures, or fenced code blocks of API signatures, in the entry-point doc (`api-content-on-arch-page` finding).

**Why:** the entry-point page is a conceptual map; when a class table appears it's doing two jobs and both altitudes are lost. Split it out.

### RULE R-architecture-11 — Diagram has arrows, not just boxes (sampled)

The architecture figure shows directional/labeled connections between components, not a bare collection of boxes.

**Check pattern:** sampled judgment over the embedded figure — assert at least one connecting arrow/edge between named boxes.

**Why:** boxes without arrows are a list, not an architecture. Every relationship that matters needs a connection. Audited against [[R-diagram]] for the full structural/aesthetic ruleset.

### RULE R-architecture-12 — Project-wide principles referenced, not restated (sampled)

Anchor-wide principles/rulings are linked to `{slug} Decisions` (e.g. `[[… |D<n>]]`), not copy-pasted into the Architecture doc. Tactical architecture-only decisions may live here in a numbered `## Design decisions` table.

**Check pattern:** sampled — flag long restated principle prose that duplicates `{slug} Decisions` content verbatim.

**Why:** restating principles forks the source of truth; the Architecture doc drifts from Decisions. Reference keeps one canonical home (HBR/CAE both reference; this is the good pattern).
