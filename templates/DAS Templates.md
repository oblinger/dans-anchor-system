---
description: "the templates kind — one bare, flat whole-document skeleton per facet, cloned to start a new instance"
---

:>> [[DAS]] → [[Templates]] → [DAS Templates](hook://p/DAS%20Templates)
# DAS Templates

The `templates/` kind — one **whole-document skeleton per facet**, the markdown a new instance is cloned from. Bare + flat (`templates/<facet>.md`, lowercase-kebab), so the OpenSpec loader consumes them and there's no name-collision with the facet spec (`facets/DAS <X>.md`). Each template's *governing facet* is its spec; the facet is the fill instruction.

## Authoring pattern (seed — ratify before the fan-out)

A template is a **live document skeleton**, generated from its facet's `## File shape` / `# Reference Example` / required-section spine by re-variableizing a filled instance:

- **Live markdown, never fenced or described** — real H1 / frontmatter / sections, so a clone is immediately a working instance (wiki-links resolve, tables render). Not a `## How to use` write-up *about* the form. *(Same principle as `R-template-01`.)*
- **Anchor identity → `{slug}`** — the H1, filenames, and breadcrumb carry `{slug}`; cloning substitutes the anchor's slug. *(T003 vocabulary.)*
- **Fillable fields → `{{…}}`** — `{{UPPER_SNAKE}}` for a value reused within the doc or structural; `{{Mixed case hint}}` for a self-describing one-off. Bare (no backticks) so they stay find-and-replace targets. *([[DAS Template Variables]] `R-template-02/09`.)*
- **Repeating sections → one variableized entry-pattern + a level-marked `...`** — never a filled fake row. *(`R-template-03`.)*
- **Breadcrumbs are NOT author-computed** — a template carries the bare `:>>` marker on its own line at the top (below frontmatter, above the H1); HookAnchor computes and inserts the actual breadcrumb dynamically from the file's location once it's cloned into an anchor. A template never hand-writes the `→ [[kmr]] → …` chain. (In an anchor's own dispatch-table page the equivalent auto-marker is used in the masthead cell instead.) Facets whose own rule pins line 1 to the H1 (Roadmap `R-roadmap-02`) or are body-only (Status) carry no breadcrumb at all. *(Resolved 2026-07-10 by the user's HookAnchor auto-breadcrumb extension.)*
- **Folder-form facets → a template FOLDER mirroring the instance shape** — `templates/<facet>/` holds one skeleton file per member file, each named by its instance pattern (`templates/log/{slug} Log.md`, `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md`; `templates/track/{slug} Track.md`); a facet with both forms keeps the flat `<facet>.md` for its single-file form ([[templates/log.md|log.md]]). **Verified OpenSpec-safe against source** (v1.6.0, commit 0a99f41, checked 2026-07-12): the loader is dereference-only — `loadTemplate` joins the exact `template:` path from schema.yaml, nothing enumerates `templates/` — so unlisted folders are invisible; `schema validate` checks only that *referenced* templates exist (no orphan detection); `schema fork` copies the schema directory recursively, so extras survive; and subdirectory-valued `template:` paths (`log/page.md`) are legal — `schema init` even creates intermediate directories for them — so folder contents can be listed file-by-file when a schema binding is wanted. Constraint C5's no-nesting applies to *category* folders, not folder-shaped template artifacts (amended in [[SKA OpenSpec Compatibility]]).
- **Start-state honesty** — where a facet has a natural empty initial state (e.g. Status all-`none`, an empty Backlog), the skeleton shows it, plus one variableized filled pattern so the shape is legible.

**Deliberately NOT the `_{Name} Template` form.** These are per-facet, globally-standard, whole-document skeletons — the OpenSpec `templates/` model — not the folder-local `_{Name} Template.md` form the [[DAS Template]] facet governs. So: no leading `_`, no ` Template` suffix, **no `template notes` cut-line** (the fill-instruction lives in the facet spec, OpenSpec's schema-instruction model), and the `R-template` ruleset (`where:: **/_* Template.md`) does not fire on them.

**OPEN for ratification (before the ~60× fan-out):**
- **Cut-line: none (chosen) vs a lightweight one.** Chosen: none — pure clonable skeleton, instruction in the facet. Alternative: a trailing notes block for per-field no-data guidance inline.
- **Placeholder convention — RESOLVED (keep two-tier), 2026-07-10.** `{slug}` (single-brace, lowercase) = the *mechanical substitution* mirroring `.anchor`'s `slug:` key — auto-filled with the slug value, not an author prompt. `{{UPPER_SNAKE}}` (double-brace, uppercase) = the *author-fills-this-in* fields — the uppercase deliberately "yells" for visibility. Brace-count + case together encode "system substitutes" vs "you fill in"; don't lowercase the `{{VAR}}`s (erases the cue). *(User may still opt for uniform-lowercase — a one-pass sweep if so.)*
- **Naming** — kebab (`prd.md`, `module-doc.md`) vs the facet's exact lowercase (`prd.md` either way; multiword like `completed roadmap` → `completed-roadmap.md`).
- **~~Breadcrumb depth~~ — RESOLVED (2026-07-10):** bare `:>>` marker, HookAnchor computes. See the Breadcrumbs convention bullet above. (Templates updated: prd/decisions/testing now carry a bare `:>>`; roadmap/status stay breadcrumbless per their facets.)
- **`description` form — frontmatter vs inline (surfaced by the fan-out).** `status` uses inline `description::`; `prd`/`decisions`/`testing` use YAML `description:`. Several facets permit either. **Ratify one convention per file-tier** (e.g. Track docs body-only+inline; Design docs frontmatter) rather than per-facet drift.
- **Repeating table rows (surfaced by the fan-out).** The `...` repeat-marker was seeded only on list items + H3 headings; `testing` extended it to tables as a trailing `| ... | | |` row. Confirm that as the canonical table-repeat form.

**Facet-spec bugs found while authoring (fix in the facet, not the template):**
- **`DAS Roadmap` check-pattern regexes are stale** — `R-roadmap-03/09` still key on the legacy numeric `M1.2` heading form (`^## M\d+\.\d+`), not the current named `M-Name` convention (2026-07-05); the abstract Axis-1 text (H1 milestone / H2 point / H3 sub-point) also disagrees with the worked `FEX Roadmap` (H2 milestone / H3 sub-item). The `roadmap` template follows FEX. Worth reconciling the facet.

## Kind index

Authored: [[templates/agenda.md|agenda]] · [[templates/backlog.md|backlog]] · [[templates/completed-roadmap.md|completed-roadmap]] · [[templates/decisions.md|decisions]] · [[templates/icebox.md|icebox]] · [[templates/inbox.md|inbox]] · [[templates/log.md|log]] (single-file) · [[templates/log/{slug} Log.md|log/]] (folder form) · [[templates/messages.md|messages]] · [[templates/prd.md|prd]] · [[templates/query.md|query]] · [[templates/roadmap.md|roadmap]] · [[templates/status.md|status]] · [[templates/testing.md|testing]] · [[templates/track/{slug} Track.md|track/]] (folder form). Tracking-group templates completed 2026-07-17 per [[DAS Tracking Design]] (F243 MS-6 added inbox + icebox); the remaining per-facet templates are generated by the Sonnet fan-out (one per facet in `facets/`, from its `DAS <X>` spec) once this pattern is ratified.
