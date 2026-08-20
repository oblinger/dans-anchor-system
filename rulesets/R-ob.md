---
description: Umbrella folder-file for Ob's rulesets — applies to every project Dan owns regardless of trait. Children listed in the dispatch table below and rolled up via `include::`. Commit-discipline and em-dash rules pending capture as separate rulesets.
applies-when: every project Dan owns (cross-cutting, not trait-scoped).
set-id: OB
---

| -[[R-ob]]- | : Umbrella folder-file for Ob's rulesets — applies to every project Dan owns regardless of trait. Children listed in the dispatch table below and rolled up via `include::`. Commit-discipline and em-dash rules pending capture as separate rulesets.<br>→ [[DAS]] → [rulesets](hook://rulesets) → [R-ob](hook://p/R-ob)  |
| --- | --- |
| [[R-ob-cmd-proc]]  | Ob's opinionated take on the command-processor / event-driven architecture pattern — single dispatcher routes events from sensors through engines to effectors. Use this set for applications with a clear input→process→output flow that benefits from a central routing layer, unified event log, and clean concurrency story. Other architectures (direct calls, async tasks, actor model, CQRS) work fine for different problems; this set captures Dan's specific approach when the dispatcher pattern fits. |
| [[R-ob-observability]]  | Ob's opinionated take on observability — failures don't disappear silently, and every OS-bridge call is instrumented. Reflects a "log everything, gate by tier" philosophy; other schools prefer minimal logging and richer error context. This set captures Dan's specific approach. |
| [[R-ob-remote-ops]]  | Ob's remote-ops hygiene — remote machines are driven through the sanctioned control planes (`bridge` persistent tmux, `exp`), never one-shot SSH remote-control. First member: the F183 bridge-guard (`tool:pre:Bash` deny, rides `anchor-base`). |
| [[R-ob-state-mgt]]  | Ob's opinionated take on state management — centralize config and state behind a single data singleton, and refuse to hardcode values that could vary. Not universal (other architectures use repository pattern, CQRS, event sourcing, functional state passing); this set captures Dan's specific approach. |
| --- | |
| [[DAS Rulesets]]  | Curated, versioned bundles of rules. |
| [[Diagram]]  | Diagram authoring + validation rules: ASCII-forbidden, hand-written SVG default, source-alongside-output, style guidelines (palette / typography / spacing), 22-item audit checklist modeled on PCB-DRC discipline. Seeded 2026-06-08; ready to populate. |
| [[M-state-ownership]]  | mend messages for script-owned surfaces |
| [[R-agenda]]  | Structural rules for the {slug} Agenda.md facet doc; enforces location, the five required H2s and their order, the stated-interval Cadence, and the no-work-rows discipline. |
| [[R-all-files]]  | Rules every `{slug} Files.md` instance must satisfy — frontmatter, no-code-fence, tree structure, and link format. |
| [[R-anchor]]  | Everything checked when auditing a whole anchor — the entry page + naming + planning facets, plus the doc-level rulesets (via R-doc) for every document the anchor contains. |
| [[R-anchor-group]]  | the DAS Anchor family index — the anchor & structure facet group page |
| [[R-anchor-page]]  | the `{slug}.md` entry-page format |
| [[R-anchor-tree]]  | Rules governing the DAS Anchor Tree facet spec — the annotated master file tree of a DAS anchor. Covers content integrity, naming conventions, tree rendering, and cross-reference sync. |
| [[R-api]]  | facet spec this doc follows |
| [[R-arch]]  | Architecture rulesets — patterns for code organization, module structure, dependency direction. Adopt the umbrella to pull all architecture rulesets, or cherry-pick individual sets. |
| [[R-architecture]]  | spec for the `{slug} Architecture.md` entry-point design facet — section spine, mandatory visual figure, subsystem dispatch + link convention, API content kept off the page |
| [[R-backlog]]  | what /audit doc checks on a backlog file |
| [[R-brief]]  | agent-facing per-file editing-and-maintenance content paired with a source file |
| [[R-bringhurst-typography]]  | Bringhurst-style typographic discipline for diagrams. |
| [[R-c4]]  | C4-model semantic conventions; the "what does this diagram mean?" rules. |
| [[R-cards]]  | the `{slug} {topic}.md` study-card format (one cheat sheet + its summary & detail cards) |
| [[R-changes]]  | Rules for the OpenSpec-conformant `changes/` folder ([[DAS Changes]]) — C-numbered change folders created by `/change`, executed by `/mint`, closed by `/finalize`'s archive-merge. |
| [[R-chores]]  | the `{slug} Chores.md` sub-surface work file — flat list of items the user is neither aware of nor interested in |
| [[R-cli]]  | the `{slug} CLI.md` command-line specification format (a compressed SVG help figure over the full command reference) |
| [[R-code]]  | Code-flavored rulesets — language- or platform-specific coding conventions. Not armed: R-mac carries no `where::`, so it defaults to `always`. |
| [[R-code-mirror]]  | Two-Way Doc Mirror wrong-side-edit protection (F188, protection layer 3 of [[SKA Code-Docs Design]]) — deny the agent's Edit/Write on the repo-side copy of a mirrored doc route and redirect to the vault original. Routes come from the `mirror-routes.json` index that `code sync` regenerates from `.anchor` `mirror:` declarations. Rides the anchor base — fires vault-wide. |
| [[R-code-repository]]  | how an anchor declares & resolves its associated code repository |
| [[R-code-surface]]  | the code surface of an anchor — All Files tree + per-module docs, kept in correspondence |
| [[R-completed-roadmap]]  | completed-roadmap facet — migrated milestones in newest-on-top order, sibling of the forward-looking Roadmap |
| [[R-decisions]]  | spec for decisions — a `## Decisions` section (with `### D<N>` records) in any design doc, plus the optional central `{slug} Decisions.md` |
| [[R-design]]  | design facet — the `{slug} Design/` folder marks an anchor as following the designed-lifecycle convention; folder presence IS the signal (no trait field required) |
| [[R-design-dispatch]]  | Rules every `{slug} Design.md` dispatch page must satisfy — location, H1 form, dispatch-table structure, and required-document coverage for Code anchors. |
| [[R-design-docs-group]]  | the DAS Design Docs family index — the design-pipeline doc facet group page |
| [[R-design-gate]]  | Explicit user sign-off gates sit between design and dependent construction — contracts freeze before dependent code, design signs off before test construction, decisions are ratified before they are policy. |
| [[R-dev-dispatch]]  | the `{slug} Dev Docs.md` developer-docs dispatch page |
| [[R-diagram]]  | Diagram authoring + validation — **umbrella over 7 methodology sub-sets, 22 rules total**: |
| [[R-diagram-geometry]]  | Hard-fail geometric correctness for hand-authored diagrams — overlap, floating endpoints, tunneling, text overflow, label-association ambiguity, label-label collision. |
| [[R-discussion]]  | planning trade-offs |
| [[R-dispatch-group]]  | the DAS Dispatch family index — the per-section sub-folder dispatch-page facet group |
| [[R-dispatch-table]]  | The shape every dispatch table must take — masthead-placement law, member-zone mechanics, and pipe-escaped cell links. |
| [[R-doc]]  | Everything checked when auditing a document — markdown + file + dispatch-table conventions plus the doc-facet rulesets (Doc Structure, Ruleset, Brief, Discussion, Log, Messages, Query, Backlog) and the design-doc facet rulesets (PRD, Architecture, Testing, Decisions, Stories). |
| [[R-doc-facet]]  | what makes a content region a document facet (vs. a structural file/folder) |
| [[R-doc-structure]]  | the canonical document layering — progressive disclosure for a document. Scope: every authored document — any `.md` the system owns, identified by a leading `# ` H1 (the checkers skip H1-less files as out of scope). |
| [[R-documentation-site]]  | an anchor's published web presence — Jekyll project page or MkDocs full site |
| [[R-dot-anchor]]  | the `.anchor` file — anchor metadata declaration |
| [[R-examples]]  | Examples in a published anchor are wholly invented — no content drawn from the author's vault, and no real project, person, address, or drive name. |
| [[R-exception-discipline]]  | Accepted rule-violations are catalogued as numbered, graded exceptions with a stated justification — the audit engine reads that table, and a corpus's suppressions are counted on every run. |
| [[R-facet]]  | Umbrella ruleset aggregating the per-facet rulesets embedded in DAS facet spec files. |
| [[R-facet-spec]]  | The rules for authoring a facet — what every facet spec doc (a `DAS <Name>.md`) must contain and conform to. **Distinct from the umbrella [[R-facet]]**, which aggregates each materialized facet's *own* embedded rules (so an anchor's `{slug} Backlog.md`, `{slug} Testing.md`, … get audited); `R-facet-spec` instead governs the **facet-spec documents themselves**. **The target set is chosen by the spec's own `group:` declaration** — `file`, `folder` or `slot` — never by filename or folder, per [[DAS Facet]] § Facet groups (*"the group is declared in the spec, never encoded in which folder the spec lives in"*). A `group: discipline` spec selects nothing of its own and is out of scope here by construction. **This replaced a 48-clause hand-maintained negative** (a `DAS *.md` glob minus a 21-name brace expression plus 27 `!DAS <name>.md` clauses), every clause of which had been appended by an agent after a finding fired on a document the list had not yet heard of — [[TINK Backlog#^T361\|T361]], deleted 2026-08-11. |
| [[R-factory-pegboard]]  | Instances are created through factories registered on a per-subsystem pegboard, so the architecture's wiring is visible in one place. |
| [[R-fct-claude]]  | The rules every anchor-level `CLAUDE.md` instance must satisfy — location, shape, and agentic-project header discipline. |
| [[R-fct-features]]  | The rules every Features-facet instance must satisfy — covering the folder layout, filename pattern, the two-zone feature-doc structure, and the index page shape. Embedded per F133. Tier legend: **checked** (mechanically verifiable), **sampled** (spot-checked), **stated** (author-honored principle). |
| [[R-fct-folder]]  | The rules every anchor folder must satisfy — a named directory containing a marker file whose name matches the folder exactly. |
| [[R-fct-icebox]]  | Rules every `{slug} Icebox.md` instance must satisfy — location, cardinality, and entry format. |
| [[R-fct-inbox]]  | Rules every `{slug} Inbox.md` instance must satisfy — location, heading format, and status-tag vocabulary. |
| [[R-fct-interface]]  | The rules every `{slug} Interface.md` (and sub-Interface) must satisfy — layer-completeness, hiding discipline, required structural links, and lifecycle gates. |
| [[R-fct-move]]  | `/move` relocates an anchor folder to a new path and updates every path-dependent system that indexes it — HookAnchor, Claude Code session history, hardcoded paths inside the anchor's own configs, … |
| [[R-fct-outputs]]  | The rules every Outputs folder and its dispatch page must satisfy — location, naming, dispatch-page shape, and individual output-file format. |
| [[R-fct-system-design]]  | Rules every `{slug} System Design.md` instance must satisfy — location, top-of-doc shape, the Architecture boundary, and currency discipline. |
| [[R-fct-user-dispatch]]  | Rules every `{slug} User Docs.md` dispatch page must satisfy — the file must exist in the right location, open with the right dispatch-table header, and contain only user-task-shaped documentation (not system-spec docs). |
| [[R-feed]]  | Rules for the feed DAG — the `feeds:` key in `.anchor`, its consumer-only declaration, the acyclicity and resolvability invariants, and the no-silent-empty reporting duty of any pass that walks it. |
| [[R-file-association]]  | Rules for the general typed-association pattern — three placement methods, cardinality→placement, parent + plural-suffix naming, one-way migration, one-form-per-parent, parent linkage, sibling-folder shape, and the citing-facet method declaration. |
| [[R-files-architecture]]  | the file-tree / content-structure design doc kind |
| [[R-git]]  | Git discipline. Placeholder; future: `R-commit-discipline`, `R-pr-workflow`, `R-no-force-main`. |
| [[R-interfaces-folder]]  | All abstract contracts live in a single `Interfaces` package per system; business code depends on interfaces, never concretes. |
| [[R-ios]]  | iOS / Apple-platform development guardrails (F237, user-directed 2026-07-13) — ad-hoc code signing is forbidden (DENY at `tool:pre:Bash` and `tool:pre:Edit`; sign with the user's Apple Developer account), and GUI-affecting test runs are steered to a bridge agent on a remote machine. Rides the anchor base; every rule self-gates on Xcode tooling evidence (the command or file itself), so non-Apple work never pays for it. |
| [[R-layering]]  | Keeps the anchor-system layer cake real — one-directional coupling (Anchorage ← Warden ← TAS-core ← DAS content), per-skill dependency footprints, and generic-vs-personal provenance legibility. Ratified 2026-07-12; spec home: SKA System Design § System layers & coupling, SKA PRD § System Layers & the Adoption Ladder. |
| [[R-log]]  | Structural rules for the {slug} Log facet — folder shape, entry filename pattern, dispatch dispatch, content scope. |
| [[R-mac]]  | macOS app development — code signing, TCC permissions, sandboxing, and build conventions. Applies when an anchor builds a macOS `.app` bundle (Swift / Obj-C / Catalyst / Electron-on-macOS / any framework producing a macOS app). |
| [[R-markdown]]  | Mechanical + authoring rules for every markdown document; cited by every facet and skill that produces markdown. |
| [[R-masterguard]]  | The master archive is a write-once surface (ATT T178) — deny any Bash command that writes into `/Volumes/<X>/__MASTERS__/` unless a write session is explicitly open on that volume. Rides `anchor-base`; fires at `tool:pre:Bash`. |
| [[R-messages]]  | the Messages facet — agent's per-anchor background-process inbox, distinct from the user's Inbox |
| [[R-module-doc]]  | per-module source documentation — one doc per source module under `{slug} Dev/` |
| [[R-naming]]  | file-naming facet — `{slug} <X>.md` default + explicit exception allowlist |
| [[R-one-path]]  | For each operation there is exactly one current implementation path; superseded code is deleted, never parallel-maintained. |
| [[R-openspec]]  | OpenSpec mappability guards — the constraints that keep DAS structure mechanically projectable onto the OpenSpec layout (specs / changes / templates / schema.yaml), so the future TAS extraction stays a filter, not a rewrite. |
| [[R-output-group]]  | the DAS Output family index — the output / published-doc facet group page |
| [[R-ownership]]  | Every mutable resource has exactly one owner; invariants are made true by construction rather than defended at runtime. |
| [[R-paper]]  | Paper / writing-anchor rulesets — citation conventions, prose-style discipline, structural conventions for paper anchors. Adopt the umbrella to pull all paper rulesets. |
| [[R-pathguard]]  | Veto-path protection for state-managed file regions (F131) — deny the agent's Edit/Write on surfaces owned by a script (`state`, `/atlas`, the queries renderer) and redirect to the owning tool. Fires at `tool:pre:*` through the live dispatcher. Rides the anchor base — fires vault-wide (F264, 2026-07-18; formerly opt-in via the `pathguard` trait, which no anchor adopted, so the DENY never fired — only the softer [[R-state-region]] advisory rode the base). The two are twins on the same surfaces: this one blocks the edit, the advisory only reminds. |
| [[R-prd]]  | facet spec this doc follows |
| [[R-process]]  | Process rulesets — feature lifecycle, verification tiers, state transitions. Adopt the umbrella to pull all process rulesets. |
| [[R-progressive]]  | layout conventions of progressive disclosure — checked on every markdown doc |
| [[R-project-page]]  | Rules every Project Page instance must satisfy — presence of a `website/` folder, the Jekyll cayman front matter, and the deploy script. |
| [[R-query]]  | the `{slug} queries.md` format |
| [[R-roadmap]]  | facet spec for the project sequencing-design doc — milestones, shapes, and numbering |
| [[R-rocks]]  | Structural rules for the Rocks facet folder; enforces location, folder-note presence, the catch-all, short abbreviation-style rock names with their expansions, tier-line integrity, and the no-work-rows discipline. |
| [[R-ruleset]]  | Format every ruleset definition obeys — sentinels, header fields, per-rule structure, numbering, includes. |
| [[R-simple]]  | Simple-anchor rulesets — minimal-shape collections without full DAS structure. Adopt the umbrella to pull all simple-anchor rulesets. |
| [[R-single-source-of-truth]]  | Every canonical datum — a config value, a state field, a type definition, a compiled binary, a spec — lives in exactly one physical location; every other reference is a pointer, include, or explicitly-labeled derived mirror. |
| [[R-skill]]  | Per-skill rulesets — to embed in `~/.claude/skills/<skill>/SKILL.md` specs. First candidates: R-ask, R-feature, R-atlas. |
| [[R-skill-anchor]]  | Skill-anchor trait-scoped rulesets — apply to anchors that declare the `skill` trait in `.anchor`. Structural shape of skill folders, ask-format / verification / mode-style conventions specific to skill anchors. Sits under the [[R-trait]] umbrella. |
| [[R-skill-md]]  | the `SKILL.md` entry-point structure for a Claude Code skill |
| [[R-specs]]  | Rules for the OpenSpec-conformant `specs/` folder ([[DAS Specs]]) — the anchor's durable per-capability behavioral contract, written only by `/finalize`'s archive-merge. |
| [[R-spine]]  | the routing zone every document opens with — which of the two forms a document gets, and the fixed line order that follows |
| [[R-stable-ids]]  | Numbered identifiers are permanent handles — monotonic-forever, never recycled, gap-numbered where ordered, zero-padded where sorted. |
| [[R-state-region]]  | The F236 advisory on state-managed doc regions — an agent Edit/Write touching `## Open Questions` / `## Resolved` / `## Status` on an existing doc that carries labeled items (Q/V bullets, resolved `### Q<n>` H3s) gets the use-`state` reminder; the edit stands. Rides the anchor base (adopted 2026-07-13, F236 M3) — fires vault-wide. Doc creation is exempt; the backlog / queries surfaces and a feature doc's `## Open Questions` keep their harder [[R-pathguard]] DENY. A feature doc's `## Resolved` landed here in F291, on the rule *deny where desync is possible, detect where it is not* — an archived decision is not rendered, not counted, and gates nothing, so there is no live state left to protect. |
| [[R-status]]  | Structural rules for the {slug} Status.md facet doc; enforces the per-facet dataview-line shape and cell ladder. |
| [[R-stone]]  | Structural rules for a stone group — folder location and naming, the control file, the header-by-link-target rule, stone numbering, and the key block's position. |
| [[R-stories]]  | Structural rules for the {slug} Stories facet — folder shape, story file naming, dispatch table, bidirectional linking. |
| [[R-stream]]  | Rules ADDED by the dated specialization on top of [[R-file-association]] — newest-first ordering + prepend immutability, the parallel-entry-skeleton invariant, and ISO-date entry-file naming. |
| [[R-subs]]  | the `{slug} Subs/` subprojects zone — week-scale sub-efforts numbered from the anchor's F-mint |
| [[R-sugiyama]]  | Sugiyama-style graph-drawing aesthetics; quality rules below the hard-fail threshold. |
| [[R-svg-hygiene]]  | File-format hygiene for hand-authored SVG diagrams. |
| [[R-svg-jiggle]]  | Geometry-aware layout-repair ("jiggle") for hand-authored SVG diagrams — detect a named, explicit issue list, then resolve each issue with the cheapest resolution that closes it without opening a new one. |
| [[R-template]]  | the Template facet — a domain-specific, folder-local structure for the items in one folder/tree |
| [[R-test]]  | Testing posture. Placeholder; future: `R-integration-not-mock`, `R-deterministic`, `R-property-based`. |
| [[R-testing]]  | facet spec this doc instantiates |
| [[R-topic]]  | Topic-anchor rulesets — knowledge/reference anchors (folders of notes, surveys, glossaries). Adopt the umbrella to pull all topic rulesets. |
| [[R-track-dispatch]]  | Rules every `{slug} Track.md` dispatch page must satisfy — location, structure, top-left cell identity, and contents restricted to tracking metadata only. |
| [[R-track-group]]  | the DAS Track family index — the work-surface facet group page |
| [[R-trait]]  | Umbrella ruleset aggregating the per-trait rulesets — rulesets that activate when an anchor declares the matching Trait in its `.anchor`. Parallel to [[R-facet]] (per-facet) and [[R-skill]] (per-skill). |
| [[R-tufte-data-ink]]  | Tufte's data-ink discipline; every visual element carries information. |
| [[R-ux]]  | facet spec for the human user-facing surface doc |
| [[R-versions]]  | the versions/ release-artifact store — immutable, tag-gated published builds |
| [[R-wcag-contrast]]  | WCAG-2.1-AA accessibility for diagrams; contrast + colorblind-safe. |
| [[R-wp]]  | the `{slug} WP/` work-products zone — dated polished outputs |
| [[R-wrapper-cli]]  | All interaction with managed infrastructure flows through the sanctioned command surface; raw primitives are forbidden, missing capability is proposed rather than worked around, and destructive commands check status first. |
| [[rulesets/README]]  |  |
| [[Rulesets Brief]]  |  |

# RULESET R-ob
description:: Umbrella folder-file for Ob's rulesets — applies to every anchor Dan owns. Children rolled up via `include::` below. The markdown rule formerly here (D-OB01) moved out in 2026-06-09 since it's not Ob-specific; it now lives in [[R-markdown]] under [[R-doc]] (via the interim `R-md`, deleted 2026-08-11). Commit-discipline and em-dash rules pending capture as their own rulesets.
include:: [[R-ob-cmd-proc]], [[R-ob-observability]], [[R-ob-state-mgt]], [[R-ob-remote-ops]] 


# Notes

> **`R-ob-observability` and `R-ob-state-mgt` gained a selector 2026-08-11 ([[TINK Backlog#^T349|T349]]), and the obvious one would have been wrong.** Both declared no `where::`, so they inherited `always` — every file in every anchor. The reflex fix is to copy the sibling: [[R-ob-cmd-proc]] declares `file:{anchor}/**/*.rs`. **Reading the rules refuses it.** `R-ob-observability-01` writes out three Check patterns under three headings — *(Rust)*, *(TS/JS)* and *(Python)*, naming `except: pass` and `.catch(() => default)` explicitly — and `R-ob-state-mgt-01` names `env::var`, `process.env` and `os.environ` in a single line. These sets are deliberately multi-language, and the sibling's selector would have silently discarded two thirds of what they say.
>
> **The measurement is the argument.** Across the vault, `.rs` reaches **6** source files; `{rs,py,ts,js}` reaches **347** — so the reflex fix would have scoped a *"no silent fallbacks"* rule to under 2% of the code it was written about, and reported green over the rest. That is the same defect shape as [[R-wcag-contrast]]'s `file:*.svg` (69 of 127 diagrams, found the same day): a selector narrower than its rules, which cannot announce itself because a narrow scope is clean by construction. Both now carry `file:{anchor}/**/*.{rs,py,ts,js}`.
>
> **[[R-ob-cmd-proc]]'s own `.rs` scope is left as found and is not obviously wrong** — its rules turn on Rust-specific machinery (`-05` JSON-serializable events, `-11` trait-pluggable backends), so narrow may be right there. It is flagged only because a family whose three members disagree about their own language scope is worth one reader noticing.
>
> Selectors are a precondition, not arming: this umbrella is still inert ([[TINK Backlog#^T208|T208]]), and all five rules across the two sets read `(checked)` while resolving to no checker — the layer T212 takes up next.

A small canonical set of rules Dan applies to *every* project he owns. Not trait-scoped (a personal-Code-anchor and a personal-Skill-anchor both pull this in); not domain-scoped (applies to docs, code, configs alike). Naming "ob" mirrors the `ob-` prefix used elsewhere in Dan's tooling (`dans-anchor-system`, `ob-utils`, vault root `~/ob/`). Rename if a better umbrella name surfaces later.